#!/usr/bin/env python3
"""Validate the curated source and deterministically export the app catalog.

This is the content import boundary, not an application test runner. It never
reads scraped/combined data, accesses the network, or writes an Appwrite database.
"""
from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ACTIVITIES = {
    "strength", "cardio", "calisthenics", "yoga", "mobility", "stretching",
    "pilates", "balance", "conditioning",
}
GOALS = {"strength", "hypertrophy", "endurance", "athleticism", "weight-loss", "mobility", "general"}
MINIMUMS = {"strength": 78, "cardio": 20, "calisthenics": 30, "yoga": 30,
            "mobility": 24, "stretching": 24, "pilates": 20, "balance": 16, "conditioning": 16}
LEVELS = {"beginner": 0, "intermediate": 1, "advanced": 2}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def valid_number(value: object, *, minimum: float, maximum: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and minimum <= value <= maximum


def string_length(value: str) -> int:
    """Match JavaScript/Zod string bounds, including supplementary characters."""
    return len(value.encode("utf-16-le")) // 2


def text_value(value: object, maximum: int, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()) and value == value.strip()
            and string_length(value) <= maximum, f"{label}: invalid or overlong text")


def strict_keys(value: dict, required: set[str], optional: set[str], label: str) -> None:
    require(isinstance(value, dict) and required <= set(value) <= required | optional, f"{label}: missing or unknown fields")


def normalized_identity(value: str) -> str:
    return "".join(character for character in unicodedata.normalize("NFKD", value).casefold() if character.isalnum())


def url_value(value: object, label: str) -> None:
    text_value(value, 2048, label)
    parsed = urlparse(value)
    require(parsed.scheme in {"http", "https"} and bool(parsed.netloc), f"{label}: expected an HTTP(S) reference URL")


def prescription(value: dict, mode: str, label: str, *, starter: bool = False) -> None:
    strict_keys(value, {"sets", "restSeconds"} | ({"exerciseId"} if starter else set()),
                {"repRange", "durationSeconds", "distanceMeters"} | ({"perSide"} if starter else set()), label)
    if "perSide" in value:
        require(type(value["perSide"]) is bool, f"{label}: perSide must be boolean")
    require(type(value.get("sets")) is int and 1 <= value["sets"] <= 20, f"{label}: invalid set count")
    require(type(value.get("restSeconds")) is int and 0 <= value["restSeconds"] <= 900, f"{label}: invalid rest")
    for field, maximum in [("durationSeconds", 86400), ("distanceMeters", 1000000)]:
        if field in value:
            require(valid_number(value[field], minimum=0.01, maximum=maximum), f"{label}: invalid {field}")
    if "repRange" in value:
        text_value(value["repRange"], 40, label + "/repRange")
        match = re.fullmatch(r"([1-9][0-9]*)(?:\s*[-–]\s*([1-9][0-9]*))?", value["repRange"])
        require(match is not None and float(match[1]) > 0 and (match[2] is None or float(match[2]) >= float(match[1])), label + ": invalid numeric repetition range")
    if mode == "reps":
        require(bool(value.get("repRange")), f"{label}: repetitions need a rep target")
        require("durationSeconds" not in value and "distanceMeters" not in value, f"{label}: repetitions cannot contain duration/distance")
    elif mode == "duration":
        require("durationSeconds" in value and "repRange" not in value and "distanceMeters" not in value, f"{label}: invalid duration target")
    elif mode == "distance":
        require("distanceMeters" in value and "repRange" not in value and "durationSeconds" not in value, f"{label}: invalid distance target")
    else:
        require("repRange" not in value and "durationSeconds" in value, f"{label}: time/distance movement requires a positive duration target")


def duplicate_candidates(snapshot: dict) -> dict:
    """Emit advisory pairs only. A similarity score never merges exercise IDs."""
    rows = snapshot["exercises"]
    candidates = []
    tokens = {row["id"]: set(re.findall(r"[a-z0-9]+", row["name"].lower())) for row in rows}
    for position, left in enumerate(rows):
        left_name = normalized_identity(left["name"])
        for right in rows[position + 1:]:
            shared = tokens[left["id"]] & tokens[right["id"]]
            if len(shared) < 2:
                continue
            right_name = normalized_identity(right["name"])
            score = SequenceMatcher(None, left_name, right_name, autojunk=False).ratio()
            token_union = tokens[left["id"]] | tokens[right["id"]]
            token_score = len(shared) / len(token_union)
            if score < 0.90 and token_score < 0.80:
                continue
            candidates.append({"leftId": left["id"], "leftName": left["name"], "rightId": right["id"],
                               "rightName": right["name"], "nameSimilarity": round(score, 4),
                               "tokenOverlap": round(token_score, 4)})
    candidates.sort(key=lambda pair: (-max(pair["nameSimilarity"], pair["tokenOverlap"]), pair["leftId"], pair["rightId"]))
    return {"version": snapshot["version"], "revision": snapshot["revision"],
            "method": "Advisory normalized-name and token similarity; explicit instruction/apparatus comparison is required before any merge.",
            "candidateCount": len(candidates), "candidates": candidates}


def build(check_only: bool, output: Path, starter_output: Path, app_root: Path | None = None) -> dict:
    output, starter_output = output.resolve(), starter_output.resolve()
    require(output != starter_output, "Exercise and starter outputs must be different files")
    for destination in (output, starter_output):
        require(destination != ROOT and ROOT not in destination.parents,
                "Generated snapshots must be outside SpotBotData; source and tooling cannot be overwritten")
    raw_source_bytes = (ROOT / "catalog.json").read_bytes()
    raw_source = raw_source_bytes.decode("utf-8")
    source_digest = hashlib.sha256(raw_source_bytes).hexdigest()
    snapshot = json.loads(raw_source)
    strict_keys(snapshot, {"schemaVersion", "version", "revision", "sources", "provenance", "exercises", "redirects", "sourceDecisions", "reviews", "starterWorkouts"}, set(), "catalog")
    require(snapshot["schemaVersion"] == 1 and type(snapshot["revision"]) is int and snapshot["revision"] >= 1, "Catalog schema/revision must be explicit positive integers")
    text_value(snapshot["version"], 100, "catalog version")
    sources = {source["name"]: source for source in snapshot["sources"]}
    require(set(sources) == {"free-exercise-db", "SpotBot original exercise guidance"}, "Only approved open or original sources are allowed")
    open_source = sources["free-exercise-db"]
    open_hash = open_source["dataSnapshotSha256"]
    require(re.fullmatch(r"[a-f0-9]{64}", open_hash) is not None, "Pinned data hash is missing")
    require(open_source["license"] == "Unlicense" and open_source["dataSnapshotRowCount"] == 873, "Open-source manifest is inconsistent")
    license_snapshot = open_source["licenseSnapshot"]
    require(hashlib.sha256(license_snapshot["text"].encode()).hexdigest() == license_snapshot["sha256"], "Embedded upstream license digest does not match")
    require(re.fullmatch(r"[a-f0-9]{40}", license_snapshot["revision"]) is not None and license_snapshot["revision"] in license_snapshot["url"], "License must retain its pinned primary-source URL")
    decisions = snapshot["sourceDecisions"]
    open_ids = {row["sourceId"] for row in decisions}
    require(len(decisions) == len(open_ids) == open_source["dataSnapshotRowCount"], "Every original source ID must have exactly one durable decision")
    require(isinstance(snapshot["exercises"], list) and bool(snapshot["exercises"]), "Catalog cannot be empty")
    exercises = snapshot["exercises"]
    by_id: dict[str, dict] = {}
    names: set[str] = set()
    activity_counts: Counter = Counter()
    equipment_counts: Counter = Counter()
    source_counts: Counter = Counter()
    all_identities: dict[str, str] = {}
    for exercise in exercises:
        strict_keys(exercise, {"id", "name", "muscle_group", "movementType", "instructions", "metadata"}, set(), "exercise")
        key = exercise["id"]
        require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,35}", key) is not None, f"Invalid canonical ID: {key}")
        require(key not in by_id, f"Duplicate ID: {key}")
        by_id[key] = exercise
        text_value(exercise["name"], 100, key + "/name")
        normalized = normalized_identity(exercise["name"])
        require(normalized not in names, f"Duplicate normalized name: {exercise['name']}")
        names.add(normalized)
        require(exercise["movementType"] in {"compound", "isolation", "other"}, f"{key}: invalid movement type")
        text_value(exercise["muscle_group"], 50, key + "/muscle_group")
        require(isinstance(exercise["instructions"], list) and bool(exercise["instructions"]), f"{key}: missing instruction steps")
        for step in exercise["instructions"]:
            text_value(step, 6000, key + "/instruction")
        rendered_instructions = "\n".join(f"{index + 1}. {step}" for index, step in enumerate(exercise["instructions"]))
        require(string_length(rendered_instructions) <= 6000, f"{key}: numbered instructions exceed remote storage")
        metadata = exercise["metadata"]
        strict_keys(metadata, {"schemaVersion", "activities", "goals", "primaryMuscles", "secondaryMuscles", "equipment",
                              "difficulty", "measurementType", "loadBehavior", "aliases", "defaultPrescription", "source", "review"},
                    {"perSide", "media"}, key + "/metadata")
        require(type(metadata["schemaVersion"]) is int and metadata["schemaVersion"] == 1, f"{key}: unsupported metadata version")
        require(string_length(json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))) <= 12000, f"{key}: metadata exceeds storage cap")
        if "perSide" in metadata:
            require(type(metadata["perSide"]) is bool, f"{key}: perSide must be boolean")
        for field, allowed in [("activities", ACTIVITIES), ("goals", GOALS)]:
            values = metadata[field]
            require(isinstance(values, list) and 1 <= len(values) <= len(allowed)
                    and len(set(values)) == len(values) and set(values) <= allowed, f"{key}: invalid {field}")
        for field in ["primaryMuscles", "secondaryMuscles", "equipment", "aliases"]:
            values = metadata[field]
            require(isinstance(values, list) and len(values) <= (30 if field == "aliases" else 20), f"{key}: invalid {field} count")
            for value in values:
                text_value(value, 160, key + "/" + field)
            require(len({normalized_identity(value) for value in values}) == len(values), f"{key}: duplicate {field} labels")
        # Local authoring accepts 100 characters; remote exchange permits 500.
        # Bundled content must fit both boundaries without truncation.
        require(string_length(", ".join(metadata["equipment"])) <= 100, f"{key}: equipment text exceeds local authoring limit")
        identities = [normalized] + [normalized_identity(alias) for alias in metadata["aliases"]]
        require(len(set(identities)) == len(identities), f"{key}: alias repeats canonical name or another alias")
        for identity in identities:
            require(identity not in all_identities, f"{key}: name/alias collides with {all_identities.get(identity)}")
            all_identities[identity] = key
        require(bool(metadata["primaryMuscles"]) and bool(metadata["equipment"]), f"{key}: missing primary muscle/equipment")
        require("media" not in metadata, f"{key}: media needs a separately approved ingestion policy")
        require(metadata["difficulty"] in LEVELS, f"{key}: invalid difficulty")
        require(metadata["measurementType"] in {"reps", "duration", "distance", "time_distance"}, f"{key}: invalid measurement")
        require(metadata["loadBehavior"] in {"none", "optional", "required"}, f"{key}: invalid load behavior")
        prescription(metadata["defaultPrescription"], metadata["measurementType"], key)
        provenance = metadata["source"]
        strict_keys(provenance, {"name", "revision", "license"}, {"id", "url"}, key + "/source")
        for field in ["name", "revision", "license"] + (["id"] if "id" in provenance else []):
            text_value(provenance[field], 160, key + "/source/" + field)
        if "url" in provenance:
            url_value(provenance["url"], key + "/source/url")
        if provenance["name"] == "free-exercise-db":
            require(provenance.get("id") in open_ids and provenance["revision"] == "sha256:" + open_hash and provenance["license"] == "Unlicense", f"{key}: unpinned/unlicensed source")
        else:
            require(provenance["name"] == "SpotBot original exercise guidance" and provenance["revision"] in sources["SpotBot original exercise guidance"]["revisions"], f"{key}: source is not approved")
        strict_keys(metadata["review"], {"method", "reviewedAt"}, set(), key + "/review")
        text_value(metadata["review"]["method"], 500, key + "/review/method")
        text_value(metadata["review"]["reviewedAt"], 40, key + "/review/reviewedAt")
        if "media" in metadata:
            strict_keys(metadata["media"], {"url", "source", "license"}, set(), key + "/media")
            url_value(metadata["media"]["url"], key + "/media/url")
            text_value(metadata["media"]["source"], 160, key + "/media/source")
            text_value(metadata["media"]["license"], 160, key + "/media/license")
        activity_counts.update(metadata["activities"])
        equipment_counts.update(metadata["equipment"])
        source_counts.update([provenance["name"]])
    redirects = snapshot["redirects"]
    require(isinstance(redirects, dict) and not redirects, "The launch catalog has no retired identities; redirects must be empty")
    reviews = snapshot["reviews"]
    require(set(reviews) == set(by_id), "Every current exercise requires exactly one editorial decision")
    for identity, review in reviews.items():
        require(review["decision"] in {"retain", "repair", "add"} and bool(review["evidence"]), identity + ": missing review evidence")
        text_value(review["method"], 1000, identity + "/review method")
        text_value(review["reviewedAt"], 40, identity + "/review date")
        require(bool(review.get("instructionReview", "").strip()), identity + ": missing actual instruction-review decision")
    pair_reviews = snapshot["provenance"].get("duplicateCandidateReviews", [])
    reviewed_pairs = set()
    for pair in pair_reviews:
        require(pair["leftId"] in by_id and pair["rightId"] in by_id and pair["decision"] == "keep-distinct" and bool(pair["reason"].strip()), "Invalid advisory duplicate comparison")
        reviewed_pairs.add(tuple(sorted([pair["leftId"], pair["rightId"]])))
    pairs = duplicate_candidates(snapshot)["candidates"]
    require(all(tuple(sorted([pair["leftId"], pair["rightId"]])) in reviewed_pairs for pair in pairs), "New similarity candidates require explicit instruction/apparatus comparison before publication")
    decision_counts = Counter()
    imported_ids = set()
    for decision in decisions:
        require(decision["status"] in {"imported", "mapped", "excluded"} and bool(decision["reason"].strip()), "Invalid source decision")
        require(re.fullmatch(r"[a-f0-9]{64}", decision["sourceRecordSha256"]) is not None, "Missing source row digest")
        decision_counts.update([decision["status"]])
        if decision["status"] == "excluded":
            require("canonicalId" not in decision, "Excluded protocols cannot silently map to included movements")
        else:
            require(decision["canonicalId"] in by_id, "Source resolution references missing canonical exercise")
            if decision["status"] == "imported":
                require(decision["canonicalId"] not in imported_ids, "Each imported source row must add one distinct canonical exercise")
                imported_ids.add(decision["canonicalId"])
                exercise = by_id[decision["canonicalId"]]
                require(exercise["metadata"]["source"]["id"] == decision["sourceId"], "Imported source identity mismatch")
                for field in ["equipment", "measurementType", "loadBehavior", "difficulty"]:
                    require(decision["normalization"][field] == exercise["metadata"][field], "Source normalization accounting is stale")
        if "relatedAdaptationId" in decision:
            require(decision["relatedAdaptationId"] in by_id, "Missing prior source adaptation")
    require(equipment_counts["bands"] >= 12, "At least 12 distinct exercises must explicitly support resistance bands")
    for activity, minimum in MINIMUMS.items():
        require(activity_counts[activity] >= minimum, f"{activity}: {activity_counts[activity]} is below coverage minimum {minimum}")
    routine_counts: Counter = Counter()
    routine_ids: set[str] = set()
    for routine in snapshot["starterWorkouts"]:
        strict_keys(routine, {"id", "name", "description", "activity", "difficulty", "exercises"}, set(), "starter")
        key = routine["id"]
        require(isinstance(key, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,35}", key) is not None, f"Invalid starter ID: {key}")
        text_value(routine["name"], 255, key + "/name")
        text_value(routine["description"], 1000, key + "/description")
        require(key not in routine_ids, f"Duplicate starter ID: {key}")
        routine_ids.add(key)
        require(routine["activity"] in ACTIVITIES and routine["difficulty"] in LEVELS, f"{key}: invalid activity/level")
        require(isinstance(routine["exercises"], list) and 1 <= len(routine["exercises"]) <= 100, f"{key}: invalid exercise count")
        ids = [entry["exerciseId"] for entry in routine["exercises"]]
        require(len(set(ids)) == len(ids), f"{key}: repeated exercise identities cannot be represented in the current app")
        for target in routine["exercises"]:
            require(target["exerciseId"] in by_id, f"{key}: missing exercise {target['exerciseId']}")
            exercise = by_id[target["exerciseId"]]
            metadata = exercise["metadata"]
            require(routine["activity"] in metadata["activities"], f"{key}: {exercise['id']} does not support {routine['activity']}")
            require(LEVELS[metadata["difficulty"]] <= LEVELS[routine["difficulty"]], f"{key}: exercise exceeds starter difficulty")
            prescription(target, metadata["measurementType"], key + "/" + exercise["id"], starter=True)
        routine_counts.update([routine["activity"]])
    require(len(snapshot["starterWorkouts"]) == 27 and all(routine_counts[activity] == 3 for activity in ACTIVITIES), "Require three starters per activity, 27 total")
    encoded = json.dumps({"version": snapshot["version"], "revision": snapshot["revision"], "exercises": exercises, "redirects": redirects}, ensure_ascii=False, indent=2)
    generated = ("// Generated by SpotBotData/Scripts/build_catalog.py. Do not edit by hand.\n"
                 "import type { CatalogSnapshot } from './catalog';\n\n"
                 "export const catalogSnapshot: CatalogSnapshot = "
                 + encoded + ";\n")
    starter_encoded = json.dumps({"version": snapshot["version"], "revision": snapshot["revision"], "starterWorkouts": snapshot["starterWorkouts"]}, ensure_ascii=False, indent=2)
    starter_generated = ("// Generated by SpotBotData/Scripts/build_catalog.py. Do not edit by hand.\n"
                         "import type { StarterWorkout } from '@spotbot/shared';\n\n"
                         "export const starterCatalogSnapshot: { version: string; revision: number; starterWorkouts: StarterWorkout[] } = "
                         + starter_encoded + ";\n")
    app_root = (app_root or ROOT.parent / "SpotBot").resolve()
    bridge = app_root / "scripts/appwrite/catalog-source-validate.ts"
    require(bridge.is_file(), "Shared runtime/source validation bridge is unavailable; export is refused")
    verified = subprocess.run(["node", "--import", "tsx", str(bridge), "--source", str(ROOT / "catalog.json"),
                               "--schema", str(ROOT / "catalog.schema.json")], cwd=app_root, capture_output=True, text=True)
    require(verified.returncode == 0, "Shared runtime/source validation refused export: " + (verified.stderr or verified.stdout).strip())
    bridge_result = json.loads(verified.stdout)
    require(bridge_result.get("sourceFileSha256") == source_digest,
            "catalog.json changed during validation; retry after editing is complete")
    if not check_only:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(generated)
        starter_output.parent.mkdir(parents=True, exist_ok=True)
        starter_output.write_text(starter_generated)
    return {"version": snapshot["version"], "revision": snapshot["revision"], "redirects": len(redirects), "reviews": len(reviews), "exercises": len(exercises), "starterWorkouts": len(snapshot["starterWorkouts"]),
            "activityCounts": dict(sorted(activity_counts.items())), "equipmentCounts": dict(sorted(equipment_counts.items())),
            "sourceCounts": dict(source_counts), "sharedValidation": bridge_result, "snapshotSha256": hashlib.sha256(encoded.encode()).hexdigest(),
            "sourceResolution": dict(decision_counts), "starterSnapshotSha256": hashlib.sha256(starter_encoded.encode()).hexdigest(),
            "mode": "check-only" if check_only else "exported", "output": str(output), "starterOutput": str(starter_output)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-root", type=Path, default=ROOT.parent / "SpotBot", help="SpotBot checkout supplying shared schema authority")
    parser.add_argument("--duplicates-report", type=Path, help="Write an advisory similarity report to this explicit path; never merges records")
    parser.add_argument("--check", action="store_true", help="Inspect content without writing the application snapshot")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--starter-output", type=Path)
    args = parser.parse_args()
    args.output = args.output or args.app_root / "packages/shared/src/catalogData.ts"
    args.starter_output = args.starter_output or args.app_root / "apps/backend/src/appwrite/starterCatalogData.ts"
    try:
        report = None
        if args.duplicates_report:
            report_path = args.duplicates_report.resolve()
            require(report_path not in {args.output.resolve(), args.starter_output.resolve()}, "Duplicate report cannot overwrite runtime output")
            require(ROOT not in report_path.parents or (ROOT / "reports").resolve() in report_path.parents,
                    "Reports inside SpotBotData must use the ignored reports directory; source and tooling cannot be overwritten")
            require(report_path != ROOT, "Duplicate report must be a file outside the source root")
            report = duplicate_candidates(json.loads((ROOT / "catalog.json").read_text()))
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        result = build(args.check, args.output, args.starter_output, args.app_root)
        if report is not None:
            result["duplicateCandidates"] = report["candidateCount"]
            result["duplicateReport"] = str(report_path)
        print(json.dumps(result, indent=2))
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.exit(1, f"Catalog export refused: {error}\n")
