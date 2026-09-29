#!/usr/bin/env python3
"""Recover one existing Flow result after a CLI timeout; never submit generation.

Run explicitly with --attempt ID. Exact attribution and an evidenced matching
credit debit are required. Missing/ambiguous results retain their reservation.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

import form_media

ROOT = Path(__file__).resolve().parent.parent


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("A required attempt or media timestamp is missing.")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("A timestamp has no timezone; attribution is ambiguous.")
    return parsed.astimezone(timezone.utc)


def checked_attempt(attempt_id):
    with form_media.locked():
        manifest = form_media.read_json(form_media.MANIFEST)
        records = form_media.ledger()
        attempt = dict(form_media.require_attempt(records, attempt_id))
        if attempt["status"] not in {"uncertain", "failed"}:
            raise ValueError("Reconcile only an uncertain/failed attempt after its generation process exits.")
        if any(a["id"] != attempt_id and a["status"] in {"reserved", "submitted"} for a in records["attempts"]):
            raise ValueError("Another pilot submission is active; finish it before opening Flow for reconciliation.")
    if not manifest.get("projectId"):
        raise ValueError("The pilot project ID is missing.")
    if attempt.get("projectId"):
        manifest = dict(manifest, projectId=attempt["projectId"])
    if not re.fullmatch(r"[A-Za-z0-9_-]+", attempt["shot"]):
        raise ValueError("Invalid shot path in the ledger.")
    actual_hash = hashlib.sha256(attempt["prompt"].encode("utf-8")).hexdigest()
    if actual_hash != attempt["promptSha256"]:
        raise ValueError("Stored prompt text no longer matches its reserved hash.")
    return manifest, attempt


def expected_model(attempt):
    if attempt["model"] == "nano-pro":
        return "image", "GEM_PIX_2"
    if attempt["model"] == "omni-flash" and attempt.get("durationSeconds") in {4, 6, 8, 10}:
        mode = attempt.get("videoFrameMode", "start-only")
        key = form_media.pilot_model_key(attempt["model"], attempt["durationSeconds"], mode)
        if mode == "start-and-end":
            refs = attempt.get("references", [])
            if (len(refs) != 2 or [ref.get("role") for ref in refs] != ["start", "end"]
                    or attempt.get("priceQuote", {}).get("modelKey") != key):
                raise ValueError("First/last attribution lacks frozen frame roles or its exact quoted key.")
        return "video", key
    raise ValueError("This reconciler supports the pilot Nano Pro images and Omni starting-frame videos only.")


def candidate_for(contents, manifest, attempt):
    kind, model = expected_model(attempt)
    window_start = timestamp(attempt["createdAt"]) - timedelta(seconds=2)
    window_end = timestamp(attempt.get("uncertainAt") or attempt["updatedAt"]) + timedelta(seconds=2)
    matches = []
    for media in contents.get("media", []):
        if not isinstance(media, dict) or media.get("projectId") != manifest["projectId"]:
            continue
        metadata = media.get("mediaMetadata", {})
        try:
            created = timestamp(metadata.get("createTime"))
        except (ValueError, TypeError):
            continue
        if not window_start <= created <= window_end:
            continue
        if kind == "image":
            generated = media.get("image", {}).get("generatedImage", {})
            prompt = generated.get("prompt")
            observed_model = generated.get("modelNameType")
        else:
            # Fail closed on a new/unobserved video attribution shape. In
            # particular, an echoed CLI alias does not prove the billed key.
            generated = media.get("video", {}).get("generatedVideo", {})
            request_data = metadata.get("requestData", {})
            video_request = request_data.get("videoGenerationRequestData", {})
            prompt = generated.get("prompt")
            if prompt is None:
                inputs = request_data.get("promptInputs", [])
                if len(inputs) == 1 and isinstance(inputs[0], dict):
                    prompt = inputs[0].get("textInput")
            observed_model = (generated.get("videoModelKey") or generated.get("modelNameType")
                              or video_request.get("videoModelKey"))
        if prompt != attempt["prompt"] or observed_model != model:
            continue
        media_id, workflow_id = media.get("name"), media.get("workflowId")
        if not all(isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F-]{36}", value)
                   for value in (media_id, workflow_id)):
            continue
        if attempt.get("mediaId") and attempt["mediaId"] != media_id:
            continue
        matches.append(media)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one attributed {kind}; found {len(matches)}. No download or retry submitted.")
    return matches[0], kind


def inspect_download(path, kind):
    with path.open("rb") as stream:
        magic = stream.read(16)
    if kind == "video":
        if magic[4:8] != b"ftyp":
            raise ValueError("The video download is not MP4; a poster image cannot complete this attempt.")
        extension = ".mp4"
    elif magic.startswith(b"\x89PNG\r\n\x1a\n"):
        extension = ".png"
    elif magic.startswith(b"\xff\xd8\xff"):
        extension = ".jpg"
    elif magic[:4] == b"RIFF" and magic[8:12] == b"WEBP":
        extension = ".webp"
    else:
        raise ValueError("Downloaded bytes are not a recognized image; HTML/errors cannot complete this attempt.")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise ValueError("ffprobe is required to inspect the recovered asset before settlement.")
    result = subprocess.run([ffprobe, "-v", "error", "-show_entries",
                             "stream=codec_type,codec_name,width,height,duration:format=duration",
                             "-of", "json", str(path)], capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError("ffprobe could not read the recovered media.")
    metadata = json.loads(result.stdout)
    streams = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
    if len(streams) != 1 or any(type(streams[0].get(k)) is not int or streams[0][k] <= 0 for k in ("width", "height")):
        raise ValueError("Recovered media has no single readable visual stream and dimensions.")
    stream = streams[0]
    duration = None
    if kind == "video":
        if stream.get("codec_name") not in {"h264", "hevc", "av1", "vp9", "mpeg4"}:
            raise ValueError("The MP4 does not expose a recognized video codec.")
        duration = float(metadata.get("format", {}).get("duration") or stream.get("duration") or 0)
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("Recovered video has no readable positive duration.")
    return extension, {"sha256": form_media.sha256(path), "bytes": path.stat().st_size,
                       "width": stream["width"], "height": stream["height"],
                       "durationSeconds": duration, "codec": stream.get("codec_name")}


async def recover(manifest, attempt):
    import structlog
    from gflow_cli import profile_store
    from gflow_cli.api.client import FlowApiClient
    from gflow_cli.api.video_extend import _inner
    from gflow_cli.config import get_settings

    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(40))
    profile = profile_store.resolve_profile(None)
    profile_dir = get_settings().profile_subdir(profile)
    async with FlowApiClient(profile_dir, headless=True) as client:
        payload = _inner(await client.fetch_project_listing(manifest["projectId"]))
        contents = payload.get("projectContents")
        if not isinstance(contents, dict):
            raise ValueError("Flow listing has no recognized project contents.")
        media, kind = candidate_for(contents, manifest, attempt)
        with form_media.locked():
            records = form_media.ledger()
            current = form_media.require_attempt(records, attempt["id"])
            if current["status"] not in {"uncertain", "failed"}:
                raise ValueError("Attempt changed during reconciliation; stopping without replacing its state.")
            current.update(mediaId=media["name"], jobId=media["workflowId"],
                           recoveredMediaCreatedAt=media["mediaMetadata"]["createTime"],
                           updatedAt=form_media.now())
            current.setdefault("uncertainAt", attempt["updatedAt"])
            form_media.write_json(form_media.LEDGER, records)
        reports = ROOT / "reports" / "form-media" / attempt["id"]
        reports.mkdir(parents=True, exist_ok=True)
        download = reports / "reconcile-download.bin"
        # This retrieves an existing media UUID. It does not invoke generation.
        await client.download(media["name"], download)
        extension, details = inspect_download(download, kind)
        if attempt.get("videoFrameMode") == "start-and-end":
            expected_size = {"9:16": (720, 1280), "16:9": (1280, 720)}.get(attempt.get("aspect"))
            if ((details["width"], details["height"]) != expected_size
                    or abs(details["durationSeconds"] - attempt["durationSeconds"]) > 0.1):
                raise ValueError("Recovered first/last video dimensions or duration differ from the reserved settings.")
        output_dir = form_media.contained(ROOT / "form-media" / "assets" / "masters", attempt["shot"])
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / (attempt["id"] + extension)
        if output.exists():
            if form_media.sha256(output) != details["sha256"]:
                raise ValueError("A different local master already exists; recovered bytes remain in ignored diagnostics.")
            download.unlink()
        else:
            download.replace(output)
        details["path"] = output.relative_to(ROOT).as_posix()
        with form_media.locked():
            records = form_media.ledger()
            current = form_media.require_attempt(records, attempt["id"])
            if current["status"] not in {"uncertain", "failed"}:
                raise ValueError("Attempt changed after recovery; downloaded file retained for manual review.")
            files = current.setdefault("localFiles", [])
            if not any(item.get("path") == details["path"] for item in files):
                files.append(details)
            current.update(recoveredAt=form_media.now(), updatedAt=form_media.now())
            form_media.write_json(form_media.LEDGER, records)
        credits = await client.get_credits()
        observed_cost = attempt["balanceBefore"] - credits.credits
        with form_media.locked():
            records = form_media.ledger()
            current = form_media.require_attempt(records, attempt["id"])
            if current["status"] not in {"uncertain", "failed"}:
                raise ValueError("Attempt changed before settlement; recovered file retained for manual review.")
            current.update(balanceAfter=credits.credits, updatedAt=form_media.now())
            if observed_cost != current["quoteCredits"]:
                current.update(status="uncertain", notes=f"Existing media recovered after CLI timeout; observed account debit {observed_cost} differs from quote {current['quoteCredits']}. Reservation retained; reconcile account activity.")
                form_media.write_json(form_media.LEDGER, records)
                raise ValueError("Asset recovered, but credit attribution differs from the quote; reservation retained.")
            current.update(status="completed", actualCredits=observed_cost, reservedCredits=0,
                           settledAt=form_media.now(), notes="Recovered existing media after CLI timeout. No regeneration submitted.",
                           settlementEvidence=f"Exactly one matching project/prompt/model/creation-window result; verified downloaded media; account balance {current['balanceBefore']} → {credits.credits}; quoted cost {current['quoteCredits']}.")
            form_media.write_json(form_media.LEDGER, records)
            budget = form_media.budget(form_media.read_json(form_media.MANIFEST), records)
        return {"attemptId": attempt["id"], "status": "completed", "recovered": True,
                "mediaId": media["name"], "jobId": media["workflowId"], "kind": kind,
                "output": str(output), "metadata": details, "actualCredits": observed_cost,
                "budget": budget}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        # Require the reviewed cookie reader before any profile/browser access.
        patch = subprocess.run([sys.executable, str(ROOT / "Scripts" / "patch_gflow_macos.py"), "status"],
                               capture_output=True, text=True)
        if patch.returncode or json.loads(patch.stdout).get("patched") is not True:
            raise ValueError("The reviewed gflow macOS cookie patch must be active.")
        manifest, attempt = checked_attempt(args.attempt)
        if importlib.util.find_spec("gflow_cli") is None:
            command = shutil.which("gflow")
            python = Path(command).resolve().parent / "python" if command else None
            if args.worker or not python or not python.exists():
                raise ValueError("Cannot find the installed gflow Python runtime.")
            return subprocess.call([str(python), str(Path(__file__).resolve()), "--attempt", args.attempt, "--worker"])
        result = asyncio.run(recover(manifest, attempt))
        print(json.dumps(result, indent=2))
        return 0
    except (Exception, KeyboardInterrupt) as error:
        # Provider exceptions may contain signed URLs: expose only their class.
        detail = str(error) if isinstance(error, ValueError) else type(error).__name__
        print(f"Reconciliation stopped: {detail}. No generation or automatic retry submitted.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
