#!/usr/bin/env python3
"""Import exact-output active-round AI evidence without changing user decisions."""
import argparse
from datetime import datetime
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit

import form_media as media


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Editorial reviews require reviewedAt timestamps.")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Editorial timestamps must include a timezone.")
    return result


def output_key(path, checksum):
    if not isinstance(path, str) or not isinstance(checksum, str) or len(checksum) != 64:
        raise ValueError("Reviewed outputs require a path and SHA-256.")
    if any(char not in "0123456789abcdef" for char in checksum.lower()):
        raise ValueError("Invalid reviewed output SHA-256.")
    candidate = media.contained(media.ROOT, path)
    if not candidate.is_relative_to((media.MEDIA / "assets").resolve()):
        raise ValueError("Reviewed outputs must be inside form-media/assets/.")
    return media.relative(candidate), checksum.lower()


def load_reviews(round_id):
    outputs = {}
    total = 0
    paths = sorted(media.MEDIA.glob(f'{round_id}-*reviews.json'))
    if not paths:
        raise ValueError('No editorial review collections exist for this round.')
    for path in paths:
        filename = path.name
        raw = path.read_bytes()
        source = json.loads(raw)
        if not isinstance(source, dict) or not isinstance(source.get("reviews"), list):
            raise ValueError(f"Invalid review collection: {filename}")
        file_hash = hashlib.sha256(raw).hexdigest()
        for record_index, record in enumerate(source["reviews"]):
            if not isinstance(record, dict) or record.get("reviewerType") != "ai":
                raise ValueError(f"Only explicit AI records may be imported: {filename}")
            if not isinstance(record.get("status"), str) or not record["status"].strip():
                raise ValueError(f"Review status is missing: {filename}")
            key = output_key(record.get("outputPath"), record.get("outputSha256"))
            reviewed_at = timestamp(record.get("reviewedAt"))
            record_hash = digest(record)
            location = {"path": media.relative(path), "fileSha256": file_hash,
                        "recordIndex": record_index, "recordSha256": record_hash}
            candidate = {"record": record, "timestamp": reviewed_at,
                         "recordSha256": record_hash, "sources": [location], "key": key}
            previous = outputs.get(key)
            if previous is None or reviewed_at > previous["timestamp"]:
                outputs[key] = candidate
            elif reviewed_at == previous["timestamp"]:
                if record_hash != previous["recordSha256"]:
                    raise ValueError(f"Conflicting tied reviews for {key[0]}; no evidence imported.")
                previous["sources"].append(location)
            total += 1
    return list(outputs.values()), total


def review_notes(record):
    sections = []
    for key, heading in (("evidence", "Observed evidence"), ("limitations", "Limitations")):
        values = record.get(key, [])
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise ValueError(f"Review {key} must be a list of text observations.")
        if values:
            sections.append(heading + ":\n" + "\n".join(values))
    if not sections and record.get("notes"):
        if not isinstance(record["notes"], str):
            raise ValueError("Review notes must be text.")
        sections.append(record["notes"])
    return "\n\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', dest='round_id', help='Defaults to the manifest active round.')
    args = parser.parse_args()
    with media.locked():
        manifest = media.read_json(media.MANIFEST)
        round_id = args.round_id or manifest.get('activeRoundId')
        if not isinstance(round_id, str) or not re.fullmatch(r'round-[1-9][0-9]*', round_id):
            raise ValueError('A valid production round is required.')
        if manifest.get("activeRoundId") != round_id:
            raise ValueError("Only the active round may import new editorial evidence.")
        reviews, record_count = load_reviews(round_id)
        attempts = {attempt["id"]: attempt for attempt in media.ledger()["attempts"]}
        assets = {asset["id"]: asset for asset in manifest["assets"] if asset.get("roundId") == round_id}
        attribution = {}

        def add(key, asset_id, role):
            attribution.setdefault(key, {}).setdefault(asset_id, set()).add(role)

        for asset in assets.values():
            parts = urlsplit(asset.get("url", ""))
            if not parts.scheme and not parts.netloc and parts.path.startswith("/assets/") and asset.get("sha256"):
                add(output_key("form-media" + unquote(parts.path), asset["sha256"]), asset["id"], "delivery")
            attempt = attempts.get(asset.get("attemptId"))
            if not attempt:
                continue
            if attempt.get("roundId") != round_id or attempt.get("exerciseId") != asset["exerciseId"]:
                raise ValueError(f"Asset/attempt attribution differs: {asset['id']}")
            for master in attempt.get("localFiles", []):
                if master.get("role") == "master" and master.get("path") == attempt.get("outputPath"):
                    add(output_key(master["path"], master["sha256"]), asset["id"], "master")

        matched = {}
        unmatched = 0
        for candidate in reviews:
            key = candidate["key"]
            targets = attribution.get(key, {})
            if not targets:
                unmatched += 1
                continue
            if len(targets) != 1:
                raise ValueError(f"Reviewed output maps to multiple assets: {key[0]}")
            asset_id, roles = next(iter(targets.items()))
            asset = assets[asset_id]
            record = candidate["record"]
            attempt = attempts.get(asset.get("attemptId"), {})
            if record.get("exerciseId") and record["exerciseId"] != asset["exerciseId"]:
                raise ValueError(f"Review exercise differs from the exact output: {key[0]}")
            if record.get("shot") and record["shot"] != (asset.get("shot") or attempt.get("shot")):
                raise ValueError(f"Review shot differs from the exact output: {key[0]}")
            path = media.repo_path(key[0])
            if media.sha256(path) != key[1]:
                raise ValueError(f"Reviewed output bytes changed: {key[0]}")
            candidate["role"] = "delivery" if "delivery" in roles else "master"
            previous = matched.get(asset_id)
            if previous is None or candidate["timestamp"] > previous["timestamp"]:
                matched[asset_id] = candidate
            elif candidate["timestamp"] == previous["timestamp"] and candidate["recordSha256"] != previous["recordSha256"]:
                raise ValueError(f"Conflicting tied evidence for asset {asset_id}.")

        changed = 0
        preserved = 0
        for asset_id, candidate in matched.items():
            asset = assets[asset_id]
            existing = asset.get("editorialReview")
            if existing:
                if existing.get("reviewerType") != "ai" or timestamp(existing.get("reviewedAt")) > candidate["timestamp"]:
                    preserved += 1
                    continue
                previous_hash = existing.get("sourceReview", {}).get("recordSha256")
                if timestamp(existing["reviewedAt"]) == candidate["timestamp"] and previous_hash and previous_hash != candidate["recordSha256"]:
                    raise ValueError(f"Saved evidence conflicts with a tied review: {asset_id}")
            record = candidate["record"]
            imported = {"status": record["status"], "reviewerType": "ai", "reviewer": "Codex",
                        "reviewedAt": record["reviewedAt"], "notes": review_notes(record),
                        "reviewedOutput": {"path": candidate["key"][0], "sha256": candidate["key"][1],
                                           "role": candidate["role"]},
                        "sourceReview": {"recordSha256": candidate["recordSha256"],
                                         "locations": candidate["sources"], "record": record}}
            if record.get("reviewKind"):
                imported["reviewKind"] = record["reviewKind"]
            if existing != imported:
                asset["editorialReview"] = imported
                changed += 1
        if changed:
            media.write_json(media.MANIFEST, manifest)
        print(json.dumps({"reviewRecords": record_count, "matchedAssets": len(matched),
                          "updatedAssets": changed, "preservedNewerOrHuman": preserved,
                          "unmatchedOutputs": unmatched}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(f"Editorial import stopped: {error}")
