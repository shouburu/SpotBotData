#!/usr/bin/env python3
"""Local exercise-media dashboard and conservative pilot generation ledger.

This program never invokes a generator. Reserve before a paid submission, record
the remote IDs immediately, and settle only with an evidenced actual cost.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
from urllib.parse import unquote, urlsplit
import uuid

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "form-media"
MANIFEST = MEDIA / "manifest.json"
LEDGER = MEDIA / "attempts.json"
ROUND_ONE_SNAPSHOT = MEDIA / "reviews" / "round-1-before-round-2.json"
THREAD_LOCK = threading.RLock()
REVIEWS = {"pending", "accepted", "rejected", "needs-review"}
STATUSES = {"reserved", "submitted", "completed", "failed", "uncertain", "cancelled"}
DELIVERY_LIMIT_BYTES = 5_000_000
PILOT_VIDEO_MODELS = {"omni-flash": "omni_flash", "veo-fast": "veo_3_1_fast",
                      "veo-quality": "veo_3_1_quality"}
PILOT_MODEL_LABELS = {"nano-pro": "Nano Banana Pro", "omni-flash": "Omni 1.1 Flash",
                      "veo-fast": "Veo 3.1 - Fast", "veo-quality": "Veo 3.1 - Quality"}
RESOLUTION_LABEL_PATTERN = r"\b(?:\d{3,4}p|[248]k|resolution)\b"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def media_metadata(path: Path, kind: str):
    """Measure a downloaded/exported image or video; no generator or browser."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise ValueError("ffprobe is required to record actual media dimensions and duration.")
    result = subprocess.run([ffprobe, "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,width,height,duration:format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError("ffprobe could not read the media file.")
    data = json.loads(result.stdout)
    streams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    if len(streams) != 1 or any(type(streams[0].get(key)) is not int or streams[0][key] <= 0
                              for key in ("width", "height")):
        raise ValueError("Media must contain exactly one readable visual stream.")
    stream = streams[0]
    duration = None
    if kind == "video":
        duration = float(data.get("format", {}).get("duration") or stream.get("duration") or 0)
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("Video must have a finite, positive measured duration.")
    return {"path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size,
            "width": stream["width"], "height": stream["height"], "durationSeconds": duration,
            "codec": stream.get("codec_name")}


def read_json(path: Path, default=None):
    if not path.exists() and default is not None:
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    data = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


@contextmanager
def locked():
    # One lock covers both CLI processes and concurrent dashboard requests.
    MEDIA.mkdir(parents=True, exist_ok=True)
    with THREAD_LOCK, (MEDIA / ".form-media.lock").open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def ledger():
    return read_json(LEDGER, {"schemaVersion": 1, "attempts": []})


def budget(manifest, records):
    attempts = records["attempts"]
    periods = manifest.get("budgetPeriods", [])
    period_id = manifest.get("currentBudgetPeriodId")
    period = None
    current_attempts = attempts
    limit = manifest["pilotCreditLimit"]
    if periods or period_id:
        period_ids = [p["id"] for p in periods]
        if (not periods or len(set(period_ids)) != len(period_ids)
                or period_id != period_ids[-1]):
            raise ValueError("Budget periods must be unique and the latest period must be current.")
        period = periods[-1]
        limit = period["creditLimit"]
        if type(limit) is not int or limit <= 0:
            raise ValueError("The current budget period needs a positive integer credit limit.")
        prior_ids = period["priorAttemptIds"]
        attempt_ids = [a["id"] for a in attempts]
        if (len(set(prior_ids)) != len(prior_ids) or len(set(attempt_ids)) != len(attempt_ids)
                or not set(prior_ids).issubset(attempt_ids)):
            raise ValueError("The budget period's historical attempt snapshot is incomplete or duplicated.")
        prior_ids = set(prior_ids)
        for attempt in attempts:
            assigned = attempt.get("budgetPeriodId")
            if assigned is not None and assigned not in period_ids:
                raise ValueError("An attempt references an unknown budget period.")
            if ((attempt["id"] in prior_ids and assigned == period_id)
                    or (attempt["id"] not in prior_ids and assigned != period_id)):
                raise ValueError("Attempt budget assignment conflicts with the period boundary.")
        current_attempts = [a for a in attempts if a["id"] not in prior_ids]
    elif any(a.get("budgetPeriodId") is not None for a in attempts):
        raise ValueError("Attempt budget periods exist but the manifest period history is missing.")
    spent = sum(a["actualCredits"] for a in current_attempts if a.get("actualCredits") is not None)
    lifetime_spent = sum(a["actualCredits"] for a in attempts if a.get("actualCredits") is not None)
    # Holds never expire at a period boundary. Even an old attempt that becomes
    # uncertain again blocks new submissions and remains visible in this total.
    reserved = sum(a["quoteCredits"] for a in attempts if a.get("actualCredits") is None)
    return {"limit": limit, "reserved": reserved, "spent": spent,
            "remaining": limit - spent - reserved, "lifetimeSpent": lifetime_spent,
            "historicalSpent": lifetime_spent - spent,
            "periodId": period_id, "periodStartedAt": period["startedAt"] if period else None,
            "unresolvedAttemptCount": sum(unresolved(a) for a in attempts)}


def unresolved(attempt):
    # A status label alone never releases a hold, including failed/cancelled or
    # completed without an evidenced settlement. No expiry or automatic retry.
    return attempt.get("actualCredits") is None or attempt["status"] in {"reserved", "submitted", "uncertain"}


def start_budget_period(manifest, records, *, period_id, credit_limit, authorization):
    """Prepare an explicitly authorized reset; caller holds locked() and saves manifest.

    The boundary records exact prior IDs instead of editing settled attempts or
    inferring a provider renewal date. It never changes provider billing.
    """
    if manifest.get("activeGenerationGroup") or any(unresolved(a) for a in records["attempts"]):
        raise ValueError("Reconcile every pending attempt and active group before starting a budget period.")
    if not isinstance(period_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", period_id):
        raise ValueError("Use a stable, nonempty budget period ID of at most 80 characters.")
    if type(credit_limit) is not int or credit_limit <= 0:
        raise ValueError("A budget period needs a positive integer credit limit.")
    if not isinstance(authorization, str) or not authorization.strip():
        raise ValueError("Record the user's explicit budget-period authorization.")
    previous = budget(manifest, records)
    periods = list(manifest.get("budgetPeriods", []))
    if any(p["id"] == period_id for p in periods):
        raise ValueError("This budget period already exists; do not reset it again.")
    prior_ids = [a["id"] for a in records["attempts"]]
    if len(set(prior_ids)) != len(prior_ids):
        raise ValueError("Duplicate attempt IDs prevent a reliable budget boundary.")
    period = {"id": period_id, "startedAt": now(), "creditLimit": credit_limit,
              "authorization": authorization.strip(), "previousPeriodId": previous["periodId"],
              "priorAttemptIds": prior_ids, "lifetimeSpentBefore": previous["lifetimeSpent"]}
    periods.append(period)
    manifest.update(budgetPeriods=periods, currentBudgetPeriodId=period_id,
                    pilotCreditLimit=credit_limit)
    return period


def submission_window(manifest, records, group_id=None, profile=None, exercise=None, shot=None):
    """Allow overlap only among explicitly planned, separately profiled workers."""
    group = manifest.get("activeGenerationGroup")
    pending = [a for a in records["attempts"] if unresolved(a)]
    if not group_id:
        if group or pending:
            raise ValueError("Reconcile the active generation group or pending attempt first.")
        return
    if not group or group.get("id") != group_id or group.get("status") != "open":
        raise ValueError("The explicitly planned generation group is not open.")
    if group.get("budgetPeriodId") != manifest.get("currentBudgetPeriodId"):
        raise ValueError("Generation group and current budget period differ; reconcile before submitting.")
    members = group.get("members", [])
    matching = [j for j in members if (j["exerciseId"], j["shot"], j["profile"]) == (exercise, shot, profile)]
    if len(matching) != 1 or len({j["profile"] for j in members}) != len(members):
        raise ValueError("Each planned generation must have its own isolated worker profile.")
    if any(a.get("generationGroupId") != group_id or a["status"] == "uncertain" for a in pending):
        raise ValueError("Unrelated or uncertain submissions must be reconciled first.")
    if any(a.get("generationGroupId") == group_id and a["shot"] == shot for a in records["attempts"]):
        raise ValueError("This group member already has an attempt; never submit it twice.")


def counts_toward_shot_limit(attempt):
    # A reconciled CLI rejection before provider submission is retained in the
    # ledger, but is not a generated output or corrective regeneration.
    evidence = attempt.get("notSubmittedEvidence", {})
    if (attempt.get("submissionOutcome") != "confirmed-not-submitted"
            or attempt.get("status") != "failed" or type(attempt.get("actualCredits")) is not int
            or attempt["actualCredits"] != 0 or attempt.get("reservedCredits") != 0
            or type(attempt.get("balanceBefore")) is not int or attempt["balanceBefore"] < 0
            or type(attempt.get("balanceAfter")) is not int
            or attempt.get("balanceBefore") != attempt.get("balanceAfter")
            or attempt.get("jobId") or attempt.get("mediaId") or not isinstance(evidence, dict)):
        return True
    try:
        path = repo_path(evidence["path"])
        proof = read_json(path)
        return (sha256(path) != evidence["sha256"] or not isinstance(proof, dict)
                or proof.get("providerSubmissionReached") is not False
                or any(proof.get(key) != attempt.get(field) for key, field in
                       (("attemptId", "id"), ("exerciseId", "exerciseId"), ("shot", "shot"))))
    except (KeyError, OSError, ValueError):
        return True


def shot_attempt_limit(manifest, round_id=None, shot=None):
    """Keep the original limit unless this round records an authorized override."""
    identity = round_id or active_round(manifest)
    rounds = [r for r in manifest.get("productionRounds", []) if r["id"] == identity]
    if len(rounds) > 1:
        raise ValueError("Duplicate round definitions prevent a reliable attempt limit.")
    if not rounds or "maxAttemptsPerShot" not in rounds[0]:
        return 3
    limit = rounds[0]["maxAttemptsPerShot"]
    authorization = rounds[0].get("attemptLimitAuthorization")
    if type(limit) is not int or limit <= 0 or not isinstance(authorization, str) or not authorization.strip():
        raise ValueError("A round attempt-limit override needs a positive integer and explicit authorization.")
    exception = rounds[0].get("shotAttemptLimitExceptions", {}).get(shot) if shot else None
    if exception is not None:
        exception_limit = exception.get("maxAttempts")
        reason = exception.get("authorization")
        if (type(exception_limit) is not int or exception_limit <= limit
                or not isinstance(reason, str) or not reason.strip()):
            raise ValueError("A shot exception needs a higher integer limit and explicit authorization.")
        return exception_limit
    return limit


def accepted_shot(manifest, records, exercise_id, shot):
    exercise = manifest["exercises"][exercise_id]
    selected = set(exercise.get("selectedAssetIds", []))
    attempts = {item["id"]: item for item in records["attempts"]}
    for asset in manifest.get("assets", []):
        if asset["id"] not in selected or asset.get("exerciseId") != exercise_id:
            continue
        if asset.get("reviewStatus") != "accepted" and exercise.get("reviewStatus") != "accepted":
            continue
        origin = attempts.get(asset.get("attemptId"), {})
        asset_shot = origin.get("shot") or asset.get("shot")
        if not asset_shot and isinstance(asset.get("promptFile"), str):
            asset_shot = Path(asset["promptFile"]).stem
        if asset_shot == shot:
            return True
    return False


def selected_delivery_bytes(assets, selected):
    paths = set()
    for asset in assets:
        if asset["id"] not in selected:
            continue
        for key in ("url", "posterUrl", "overlayUrl"):
            url = asset.get(key)
            if not url:
                continue
            if key == "url" and asset.get("kind") == "external":
                continue
            if not isinstance(url, str):
                raise ValueError("Selected media has an invalid local URL.")
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                raise ValueError("Pilot delivery media must be local; external references must use the external kind.")
            path = unquote(parts.path)
            if path.startswith("/assets/"):
                target = contained(MEDIA / "assets", path[len("/assets/"):])
            elif path.startswith("/diagrams/"):
                target = contained(MEDIA / "diagrams", path[len("/diagrams/"):])
            else:
                raise ValueError("Selected media must use /assets/ or /diagrams/ URLs.")
            if not target.is_file():
                raise ValueError("Selected delivery media is missing locally.")
            paths.add(target)
    return sum(path.stat().st_size for path in paths)


def contained(base: Path, relative: str) -> Path:
    candidate = (base / relative).resolve()
    if not candidate.is_relative_to(base.resolve()):
        raise ValueError("Path escapes its allowed directory.")
    return candidate


def repo_path(value: str) -> Path:
    path = Path(value)
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    if not resolved.is_relative_to(MEDIA.resolve()):
        raise ValueError("Media and prompt paths must be inside form-media/.")
    if not resolved.is_file():
        raise ValueError(f"File does not exist: {value}")
    return resolved


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def require_exercise(manifest, exercise_id):
    if exercise_id not in manifest["exercises"]:
        raise ValueError("Unknown exercise ID.")
    return manifest["exercises"][exercise_id]


def require_attempt(records, attempt_id):
    for attempt in records["attempts"]:
        if attempt["id"] == attempt_id:
            return attempt
    raise ValueError("Unknown attempt ID.")


def active_round(manifest):
    return manifest.get("activeRoundId") or "round-1"


def prompt_spec(manifest, exercise_id, shot, prompt_file=None, round_id=None):
    candidates = [spec for spec in manifest.get("prompts", [])
                  if spec.get("exerciseId") == exercise_id and spec.get("shot") == shot
                  and (spec.get("roundId") or "round-1") == (round_id or active_round(manifest))]
    return next((spec for spec in candidates if spec.get("path") == prompt_file),
                candidates[0] if len(candidates) == 1 else {})


def review_history(manifest):
    # The fixed snapshot is never rewritten. Project its original decisions into
    # the same read-only history view as subsequent, atomically saved decisions.
    snapshot = read_json(ROUND_ONE_SNAPSHOT, {"exercises": {}})
    history = []
    for exercise_id, record in snapshot.get("exercises", {}).items():
        if record.get("reviewStatus", "pending") == "pending" and not record.get("notes") and not record.get("selectedAssetIds"):
            continue
        history.append(dict(record, id=f"round-1-snapshot:{exercise_id}", exerciseId=exercise_id,
                            roundId="round-1", source="round-snapshot",
                            createdAt=record.get("reviewedAt") or snapshot.get("capturedAt")))
    return history + manifest.get("reviewHistory", [])


def state():
    with locked():
        manifest = read_json(MANIFEST)
        records = ledger()
        catalog = read_json(ROOT / "catalog.json")
        exercises = catalog["exercises"]
        if isinstance(exercises, dict):
            exercises = [dict(item, id=key) for key, item in exercises.items()]
        joined = [dict(item, **manifest["exercises"].get(item["id"], {})) for item in exercises]
        style = ""
        for filename in ("style.md", "STYLE.md", "style-guide.md"):
            path = MEDIA / filename
            if path.exists():
                style = path.read_text(encoding="utf-8")
                break
        prompts = []
        for spec in manifest.get("prompts", []):
            prompt_path = repo_path(spec["path"])
            if not prompt_path.is_relative_to((MEDIA / "prompts").resolve()):
                raise ValueError("Prompt specs must point inside form-media/prompts/.")
            prompts.append(dict(spec, text=prompt_path.read_text(encoding="utf-8")))
        assets = [dict(asset, roundId=asset.get("roundId") or "round-1")
                  for asset in manifest.get("assets", [])]
        rounds = list(manifest.get("productionRounds", []))
        known_rounds = {item["id"] for item in rounds}
        for round_id in dict.fromkeys(["round-1", active_round(manifest)] + [a["roundId"] for a in assets]):
            if round_id not in known_rounds:
                rounds.append({"id": round_id, "title": round_id.replace("-", " ").title()})
                known_rounds.add(round_id)
        return {"catalog": {"version": catalog["version"], "revision": catalog["revision"]},
                "exercises": joined, "assets": assets,
                "attempts": records["attempts"], "budget": budget(manifest, records),
                "style": style, "styleVersion": manifest["styleVersion"], "prompts": prompts,
                "activeRoundId": active_round(manifest), "rounds": rounds,
                "reviewHistory": review_history(manifest)}


def review(payload):
    if not isinstance(payload, dict) or set(payload) - {"exerciseId", "reviewStatus", "notes", "selectedAssetIds", "roundId", "reviewedAssetIds"}:
        raise ValueError("Invalid review fields.")
    exercise_id = payload.get("exerciseId")
    status = payload.get("reviewStatus")
    notes = payload.get("notes", "")
    selected = payload.get("selectedAssetIds", [])
    if not isinstance(exercise_id, str) or not isinstance(status, str) or status not in REVIEWS:
        raise ValueError("A valid exerciseId and reviewStatus are required.")
    if not isinstance(notes, str) or len(notes) > 10000:
        raise ValueError("Notes must be text of at most 10,000 characters.")
    if not isinstance(selected, list) or any(not isinstance(item, str) for item in selected):
        raise ValueError("selectedAssetIds must be a list of asset IDs.")
    if len(selected) != len(set(selected)):
        raise ValueError("Duplicate selected asset IDs.")
    with locked():
        manifest = read_json(MANIFEST)
        round_id = active_round(manifest)
        if payload.get("roundId", "round-1") != round_id:
            raise ValueError("The active review round has changed. Refresh the dashboard before saving this decision.")
        exercise = require_exercise(manifest, exercise_id)
        valid = {a["id"] for a in manifest.get("assets", []) if a["exerciseId"] == exercise_id}
        if not set(selected).issubset(valid):
            raise ValueError("Selected assets must belong to this exercise.")
        seen = payload.get("reviewedAssetIds", list(valid))
        if (not isinstance(seen, list) or any(not isinstance(item, str) for item in seen)
                or len(seen) != len(set(seen)) or not set(seen).issubset(valid)):
            raise ValueError("Reviewed assets must be unique IDs belonging to this exercise.")
        if status == "accepted" and exercise["teachingFormat"] != "text" and not selected:
            raise ValueError("Select at least one asset before accepting media guidance.")
        previous = {key: exercise[key] for key in
                    ("reviewStatus", "notes", "selectedAssetIds", "reviewedAt", "reviewRoundId", "reviewedAssetIds") if key in exercise}
        if status == "accepted":
            delivery_bytes = selected_delivery_bytes(manifest.get("assets", []), set(selected))
            if delivery_bytes > DELIVERY_LIMIT_BYTES:
                raise ValueError(f"Selected media totals {delivery_bytes:,} bytes; export smaller delivery copies to meet the 5 MB per-exercise limit.")
            exercise["deliveryBytes"] = delivery_bytes
        reviewed_at = now()
        exercise.update(reviewStatus=status, notes=notes, selectedAssetIds=selected,
                        reviewedAt=reviewed_at, reviewRoundId=round_id, reviewedAssetIds=seen)
        if exercise.get("pilot"):
            exercise["recommendationStatus"] = "pilot-reviewed"
        elif status == "accepted":
            exercise["recommendationStatus"] = "reviewed"
        asset_reviews = []
        changed_asset_ids = []
        for asset in manifest.get("assets", []):
            if asset["id"] in selected:
                asset_round = asset.get("roundId") or "round-1"
                asset_reviews.append({"assetId": asset["id"], "roundId": asset_round,
                                     "reviewStatusBefore": asset.get("reviewStatus", "pending"),
                                     "reviewStatusAfter": status if asset_round == round_id else asset.get("reviewStatus", "pending")})
            if asset["id"] in selected and (asset.get("roundId") or "round-1") == round_id:
                asset["reviewStatus"] = status
                changed_asset_ids.append(asset["id"])
        entry = {"id": "review_" + uuid.uuid4().hex[:16], "exerciseId": exercise_id,
                 "roundId": round_id, "reviewStatus": status, "notes": notes,
                 "selectedAssetIds": selected, "createdAt": reviewed_at,
                 "source": "dashboard", "previous": previous, "assetReviews": asset_reviews, "reviewedAssetIds": seen}
        manifest.setdefault("reviewHistory", []).append(entry)
        write_json(MANIFEST, manifest)
        return {"ok": True, "exerciseId": exercise_id, "reviewStatus": status,
                "roundId": round_id, "reviewedAt": reviewed_at, "reviewedAssetIds": seen, "historyEntry": entry,
                "changedAssetIds": changed_asset_ids,
                "recommendationStatus": exercise.get("recommendationStatus", "provisional")}


def pilot_media_kind(model):
    if model == "nano-pro":
        return "image"
    if model in PILOT_VIDEO_MODELS:
        return "video"
    raise ValueError("Unsupported pilot model.")


def pilot_model_key(model, duration=None, frame_mode="start-only", aspect=None):
    if model == "nano-pro" and frame_mode == "start-only":
        return "GEM_PIX_2"
    if model == "omni-flash" and duration in {4, 6, 8, 10}:
        if frame_mode == "text-only":
            return f"abra_t2v_{duration}s"
        if frame_mode == "start-only":
            return f"abra_i2v_{duration}s"
        if frame_mode == "start-and-end":
            return f"omni_flash_i2v_{duration}s_first_last"
    if (model in {"veo-fast", "veo-quality"} and duration in {6, 8}
            and aspect in {"9:16", "16:9"} and frame_mode in {"text-only", "start-only"}):
        # A local exact-settings identity, NOT an inferred provider backend key.
        # Veo is UI-quote-only: its wire keys vary with account tier and aspect.
        mode = "t2v" if frame_mode == "text-only" else "i2v"
        return f"flow-ui:{model}:{mode}:{duration}s:{aspect}:provider-default:x1"
    raise ValueError("Unsupported pilot model, duration or frame mode.")


def require_veo_default_resolution(quote, model, duration, aspect, video_mode):
    """Accept provider-default only when the exact live Veo pane has no resolution control."""
    expected = {"model": model, "family": PILOT_MODEL_LABELS[model], "videoMode": video_mode,
                "durationSeconds": duration, "aspect": aspect, "count": 1,
                "resolutionPolicy": "provider-default", "resolutions": [], "visibleResolutionLabels": []}
    visible = quote.get("settingsText")
    selected = quote.get("selectedSettings")
    if (model not in {"veo-fast", "veo-quality"}
            or any(quote.get(k) != v for k, v in expected.items())
            or quote.get("resolutionControlObserved") is not False
            or type(quote.get("durationSeconds")) is not int or type(quote.get("count")) is not int
            or not isinstance(visible, str) or PILOT_MODEL_LABELS[model] not in visible
            or re.search(RESOLUTION_LABEL_PATTERN, visible, re.IGNORECASE)
            or not isinstance(selected, list) or not all(isinstance(x, str) for x in selected)):
        raise ValueError("Veo provider-default requires exact live settings and evidence that no resolution control is visible.")
    selected = [x.strip() for x in selected]
    if (not any(x.startswith("videocam") for x in selected)
            or not any(x.endswith(aspect) for x in selected)
            or f"{duration}s" not in selected or "x1" not in selected
            or (video_mode == "i2v" and not any(x.startswith("crop_free") for x in selected))):
        raise ValueError("Veo selected controls do not establish the requested video mode, aspect, duration and count.")


def reserve(args):
    media_kind = pilot_media_kind(args.model)
    prompt_path = repo_path(args.prompt_file)
    prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt.strip() or len(prompt) > 100000:
        raise ValueError("Prompt must be nonempty and at most 100,000 characters.")
    references = []
    for filename in args.reference:
        path = repo_path(filename)
        references.append({"path": relative(path), "sha256": sha256(path)})
    end_reference = getattr(args, "end_reference", None)
    video_mode = getattr(args, "video_mode", "i2v")
    if video_mode == "t2v" and (media_kind != "video" or references or end_reference):
        raise ValueError("Text-to-video requires an allowed video model with no image references.")
    frame_mode = "text-only" if video_mode == "t2v" else ("start-and-end" if end_reference else "start-only")
    if args.model in {"veo-fast", "veo-quality"}:
        pilot_model_key(args.model, args.duration, frame_mode, args.aspect)
        if not args.quote_json or len(references) != (0 if video_mode == "t2v" else 1):
            raise ValueError("Veo requires frozen live UI evidence and references matching its mode.")
    if end_reference:
        if args.model != "omni-flash" or len(references) != 1 or not args.quote_json:
            raise ValueError("An end frame requires one Omni starting frame and a frozen live quote.")
        path = repo_path(end_reference)
        if not path.is_relative_to((MEDIA / "assets").resolve()) or not path.is_file():
            raise ValueError("The end reference must be an existing pilot asset.")
        references.append({"path": relative(path), "sha256": sha256(path), "role": "end"})
    if media_kind == "video" and references:
        references[0]["role"] = "start"
    frozen_quote = None
    if args.quote_json:
        quote = json.loads(args.quote_json)
        if not isinstance(quote, dict) or type(quote.get("credits")) is not int or type(quote.get("balance")) is not int or quote.get("credits") != args.quote or quote.get("balance") != args.balance_before:
            raise ValueError("Frozen price evidence does not match the reserved quote and balance.")
        model_key = pilot_model_key(args.model, args.duration, frame_mode, args.aspect)
        if quote.get("modelKey") != model_key:
            raise ValueError("Frozen price evidence does not match the requested pilot model.")
        if args.model in {"veo-fast", "veo-quality"}:
            expected = {"sourceType": "flow-ui-observation", "modelKeySource": "flow-ui-settings-identity",
                        "model": args.model, "family": PILOT_MODEL_LABELS[args.model], "kind": "video",
                        "videoMode": video_mode, "durationSeconds": args.duration, "aspect": args.aspect, "count": 1}
            if any(quote.get(k) != v for k, v in expected.items()):
                raise ValueError("Veo quote must match its exact observed UI model, mode, duration, aspect and count one.")
            require_veo_default_resolution(quote, args.model, args.duration, args.aspect, video_mode)
        if end_reference:
            requirements = {"VIDEO_REQUIREMENT_TEXT", "VIDEO_REQUIREMENT_START_IMAGE", "VIDEO_REQUIREMENT_END_IMAGE"}
            aspect = {"9:16": "PORTRAIT", "16:9": "LANDSCAPE"}.get(args.aspect)
            if (quote.get("kind") != "video" or quote.get("durationSeconds") != args.duration
                    or aspect is None or aspect not in quote.get("aspects", [])
                    or "VIDEO_RESOLUTION_720P" not in quote.get("resolutions", [])
                    or not any(isinstance(group, list) and requirements.issubset(group)
                               for group in quote.get("requirements", []))):
                raise ValueError("The live offer does not cover the requested first/last video settings.")
        observed = datetime.fromisoformat(quote["observedAt"].replace("Z", "+00:00"))
        if observed.tzinfo is None or not -5 <= (datetime.now(timezone.utc) - observed).total_seconds() <= 300:
            raise ValueError("Price observation must be from the last five minutes.")
        fields = {"kind", "family", "modelKey", "credits", "durationSeconds", "resolutions", "aspects",
                  "requirements", "observedAt", "balance", "source", "snapshotSha256",
                  "sourceType", "modelKeySource", "model", "videoMode", "aspect", "count",
                  "resolutionPolicy", "resolutionControlObserved", "visibleResolutionLabels",
                  "resolutionObservation", "settingsText", "selectedSettings"}
        frozen_quote = {key: value for key, value in quote.items() if key in fields}
    with locked():
        manifest = read_json(MANIFEST)
        exercise = require_exercise(manifest, args.exercise)
        records = ledger()
        if end_reference and manifest.get("generationCapabilities", {}).get("endFrameSupported") is False:
            raise ValueError("The reviewed account frontend does not support end-frame submission.")
        if accepted_shot(manifest, records, args.exercise, args.shot):
            raise ValueError("This shot already has accepted selected media; review it before reserving regeneration.")
        previous = [a for a in records["attempts"] if a["exerciseId"] == args.exercise and a["shot"] == args.shot]
        attempt_limit = shot_attempt_limit(manifest, shot=args.shot)
        if sum(counts_toward_shot_limit(a) for a in previous) >= attempt_limit:
            raise ValueError(f"The limit of {attempt_limit} attempts per exercise/shot has been reached.")
        submission_window(manifest, records, getattr(args, "generation_group", None),
                          getattr(args, "profile", None), args.exercise, args.shot)
        if getattr(args, "generation_group", None):
            member = next(x for x in manifest["activeGenerationGroup"]["members"] if x["shot"] == args.shot)
            if (member["quoteCredits"] != args.quote or member["balance"] != args.balance_before
                    or member.get("promptSha256") != sha256(prompt_path)
                    or member["quoteSha256"] != quote.get("snapshotSha256")
                    or [{"path":r["path"], "sha256":r["sha256"]} for r in references] != member["references"]):
                raise ValueError("Group prompt, quote or reference changed after its explicit plan.")
        available = budget(manifest, records)
        if args.quote > available["remaining"]:
            raise ValueError(f"Quote exceeds the remaining pilot budget ({available['remaining']} credits).")
        if args.quote > args.balance_before:
            raise ValueError("Quote exceeds the observed account balance.")
        spec = prompt_spec(manifest, args.exercise, args.shot, relative(prompt_path))
        if spec.get("endFrameSameAsStart") is True and (
                not end_reference or references[0]["path"] != references[1]["path"]
                or references[0]["sha256"] != references[1]["sha256"]):
            raise ValueError("This shot requires the same reviewed starting image in both frame slots.")
        prompt_version = spec.get("promptVersion", manifest["styleVersion"])
        attempt = {
            "id": "attempt_" + uuid.uuid4().hex[:16], "exerciseId": args.exercise,
            "projectId": manifest.get("projectId"), "promptVersion": prompt_version, "styleVersion": manifest["styleVersion"],
            "shot": args.shot, "model": args.model, "durationSeconds": args.duration,
            "aspect": args.aspect,
            "quoteCredits": args.quote, "quoteSource": args.quote_source,
            "promptFile": relative(prompt_path), "prompt": prompt,
            "promptSha256": sha256(prompt_path), "references": references,
            "balanceBefore": args.balance_before, "status": "reserved",
            "reservedCredits": args.quote, "actualCredits": None,
            "createdAt": now(), "updatedAt": now(), "assetIds": [],
            "roundId": spec.get("roundId") or active_round(manifest),
        }
        if available["periodId"] is not None:
            attempt["budgetPeriodId"] = available["periodId"]
        attempt.update({key: spec[key] for key in ("styleId", "styleLabel") if spec.get(key)})
        if getattr(args, "generation_group", None):
            attempt["generationGroupId"] = args.generation_group
            attempt["profile"] = args.profile
        if media_kind == "video":
            attempt["videoFrameMode"] = frame_mode
        if frozen_quote is not None:
            attempt["priceQuote"] = frozen_quote
        records["attempts"].append(attempt)
        write_json(LEDGER, records)
        return {"id": attempt["id"], "attempt": attempt, "budget": budget(manifest, records)}


def update_attempt(args):
    if args.actual_credits is not None and not args.settlement_evidence:
        raise ValueError("An actual credit cost requires --settlement-evidence; failure or timeout alone does not prove no charge.")
    with locked():
        manifest = read_json(MANIFEST)
        records = ledger()
        attempt = require_attempt(records, args.attempt)
        if args.status:
            attempt["status"] = args.status
            if args.status == "submitted":
                attempt.setdefault("submittedAt", now())
            elif args.status == "uncertain":
                attempt.setdefault("uncertainAt", now())
        fields = {"jobId": args.job_id, "mediaId": args.media_id, "notes": args.notes,
                  "balanceAfter": args.balance_after, "settlementEvidence": args.settlement_evidence}
        for key, value in fields.items():
            if value is not None:
                attempt[key] = value
        if args.actual_credits is not None:
            attempt["actualCredits"] = args.actual_credits
            attempt["reservedCredits"] = 0
            attempt["settledAt"] = now()
        attempt["updatedAt"] = now()
        write_json(LEDGER, records)
        return {"attempt": attempt, "budget": budget(manifest, records)}


def register(args):
    local = repo_path(args.file) if args.file else None
    measured = media_metadata(local, args.kind) if local and args.kind in {"image", "video"} else None
    if measured:
        if any(supplied is not None and supplied != measured[key] for key, supplied in
               (("width", args.width), ("height", args.height))):
            raise ValueError("Supplied dimensions differ from the measured media dimensions.")
        args.width, args.height = measured["width"], measured["height"]
        args.duration = measured["durationSeconds"]
    if local:
        subdir = "diagrams" if local.is_relative_to((MEDIA / "diagrams").resolve()) else "assets"
        if not local.is_relative_to((MEDIA / subdir).resolve()):
            raise ValueError("Registered local files must be inside form-media/assets/ or form-media/diagrams/.")
        url = "/" + subdir + "/" + local.relative_to(MEDIA / subdir).as_posix()
    else:
        url = args.url
        parsed = urlsplit(url or "")
        if args.kind != "external" or parsed.scheme != "https" or not parsed.netloc or parsed.username:
            raise ValueError("External assets require an HTTPS --url; local assets require --file.")
    with locked():
        manifest = read_json(MANIFEST)
        require_exercise(manifest, args.exercise)
        records = ledger()
        attempt = require_attempt(records, args.attempt) if args.attempt else None
        if attempt and attempt["exerciseId"] != args.exercise:
            raise ValueError("Attempt belongs to a different exercise.")
        content_hash = sha256(local) if local else None
        round_id = (attempt or {}).get("roundId") or active_round(manifest)
        shot = attempt.get("shot") if attempt else args.shot
        spec = prompt_spec(manifest, args.exercise, shot,
                           attempt.get("promptFile") if attempt else None, round_id)
        asset = {
            "id": args.id or "asset_" + uuid.uuid4().hex[:16], "exerciseId": args.exercise,
            "kind": args.kind, "url": url, "title": args.title, "alt": args.alt,
            "bytes": local.stat().st_size if local else 0,
            "width": args.width, "height": args.height, "durationSeconds": args.duration,
            "sha256": content_hash, "source": args.source, "license": args.license,
            "reviewStatus": "pending", "promptVersion": manifest["styleVersion"],
            "createdAt": now(), "styleVersion": attempt.get("styleVersion", manifest["styleVersion"]) if attempt else manifest["styleVersion"],
            "roundId": round_id,
        }
        if shot:
            asset["shot"] = shot
        for key in ("styleId", "styleLabel"):
            value = (attempt or {}).get(key) or spec.get(key)
            if value:
                asset[key] = value
        if args.poster:
            poster = repo_path(args.poster)
            if not poster.is_relative_to((MEDIA / "assets").resolve()):
                raise ValueError("Poster must be inside form-media/assets/.")
            asset["posterUrl"] = "/assets/" + poster.relative_to(MEDIA / "assets").as_posix()
            asset["posterSha256"] = sha256(poster)
            asset["posterBytes"] = poster.stat().st_size
        if attempt:
            asset.update(attemptId=attempt["id"], promptFile=attempt["promptFile"],
                         promptText=attempt["prompt"], promptVersion=attempt.get("promptVersion", manifest["styleVersion"]),
                         referenceIds=[r["path"] for r in attempt["references"]])
        assets = manifest.setdefault("assets", [])
        if any(a["id"] == asset["id"] for a in assets):
            raise ValueError("Asset ID already exists.")
        if any(a["exerciseId"] == args.exercise and a.get("url") == url for a in assets):
            raise ValueError("This file/URL is already registered for the exercise.")
        assets.append(asset)
        write_json(MANIFEST, manifest)
        if attempt:
            attempt.setdefault("assetIds", []).append(asset["id"])
            attempt.setdefault("localFiles", []).append({"path": relative(local) if local else url,
                "sha256": content_hash, "bytes": asset["bytes"], "width": args.width,
                "height": args.height, "durationSeconds": args.duration})
            attempt["updatedAt"] = now()
            write_json(LEDGER, records)
        return asset


class Handler(BaseHTTPRequestHandler):
    server_version = "SpotBotFormMedia/1"

    def allowed_host(self):
        port = self.server.server_address[1]
        return self.headers.get("Host") in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def response_headers(self, code, length, content_type, extra=()):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-src 'self' https://www.youtube-nocookie.com; frame-ancestors 'self'; base-uri 'none'; form-action 'none'")
        for key, value in extra:
            self.send_header(key, value)
        self.end_headers()

    def respond(self, code, body, content_type="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.response_headers(code, len(body), content_type)
        if self.command != "HEAD":
            self.wfile.write(body)

    def serve_file(self, target, content_type):
        # Browser video controls use byte ranges for seeking and progressive
        # playback. Stream bounded chunks instead of loading each MP4 in RAM.
        with target.open("rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            start, end, status = 0, size - 1, 200
            headers = [("Accept-Ranges", "bytes")]
            requested = self.headers.get("Range")
            if requested:
                match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested.strip())
                valid = bool(match and size and (match[1] or match[2]))
                if valid:
                    if not match[1]:
                        length = int(match[2])
                        valid = length > 0
                        start = max(0, size - length)
                    else:
                        start = int(match[1])
                        end = min(int(match[2]), size - 1) if match[2] else size - 1
                        valid = start < size and end >= start
                if not valid:
                    self.response_headers(416, 0, content_type,
                        [("Accept-Ranges", "bytes"), ("Content-Range", f"bytes */{size}")])
                    return
                status = 206
                headers.append(("Content-Range", f"bytes {start}-{end}/{size}"))
            length = max(0, end - start + 1)
            self.response_headers(status, length, content_type, headers)
            if self.command == "HEAD":
                return
            stream.seek(start)
            try:
                while length:
                    chunk = stream.read(min(length, 64 * 1024))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    length -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                return  # A user seeking or pausing can cancel the old range.

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self.allowed_host():
            self.respond(403, {"error": "Loopback Host required."})
            return
        path = unquote(urlsplit(self.path).path)
        try:
            if path == "/api/state":
                self.respond(200, state())
                return
            if path.startswith("/api/"):
                self.respond(404, {"error": "Unknown API route."})
                return
            if path.startswith("/assets/"):
                target = contained(MEDIA / "assets", path[len("/assets/"):])
            elif path.startswith("/diagrams/"):
                target = contained(MEDIA / "diagrams", path[len("/diagrams/"):])
            else:
                target = contained(MEDIA / "dashboard", path.lstrip("/") or "index.html")
            if not target.is_file() or target.name.startswith("."):
                self.respond(404, {"error": "File not found."})
                return
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self.serve_file(target, content_type)
        except ValueError as exc:
            self.respond(400, {"error": str(exc)})
        except (OSError, KeyError, json.JSONDecodeError):
            self.respond(503, {"error": "Media data is unavailable or invalid."})

    def do_POST(self):
        port = self.server.server_address[1]
        if not self.allowed_host() or self.headers.get("Origin") not in {
            f"http://127.0.0.1:{port}", f"http://localhost:{port}"}:
            self.respond(403, {"error": "Same-origin loopback requests only."})
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
            self.respond(415, {"error": "Content-Type must be application/json."})
            return
        if urlsplit(self.path).path != "/api/review":
            self.respond(404, {"error": "Unknown API route."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 128000:
                raise ValueError("Invalid request length.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            self.respond(200, review(payload))
        except (ValueError, UnicodeDecodeError) as exc:
            self.respond(400, {"error": str(exc)})
        except (OSError, KeyError):
            self.respond(503, {"error": "Media data is unavailable or invalid."})


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("Must be nonnegative.")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve", help="Serve the local review dashboard.")
    serve.add_argument("--port", type=int, default=8766)
    commands.add_parser("state", help="Print joined dashboard data.")
    commands.add_parser("budget", help="Print remaining pilot credit budget.")
    period_parser = commands.add_parser("start-budget-period", help="Start an explicitly authorized credit period without deleting historical spending.")
    period_parser.add_argument("--id", required=True)
    period_parser.add_argument("--limit", required=True, type=nonnegative)
    period_parser.add_argument("--authorization", required=True)
    reserve_parser = commands.add_parser("reserve", help="Reserve one quoted generation; does not submit it.")
    for flag in ("exercise", "shot", "model", "quote-source", "prompt-file"):
        reserve_parser.add_argument("--" + flag, required=True)
    reserve_parser.add_argument("--quote", required=True, type=nonnegative)
    reserve_parser.add_argument("--balance-before", required=True, type=nonnegative)
    reserve_parser.add_argument("--duration", type=nonnegative)
    reserve_parser.add_argument("--aspect", help="Requested generation aspect recorded with the attempt.")
    reserve_parser.add_argument("--reference", action="append", default=[])
    reserve_parser.add_argument("--end-reference", help="Optional video end frame; frozen separately from the starting frame.")
    reserve_parser.add_argument("--video-mode", choices=["i2v", "t2v"], default="i2v")
    reserve_parser.add_argument("--quote-json", help="Freeze the sanitized live offer in the tracked attempt.")
    reserve_parser.add_argument("--generation-group")
    reserve_parser.add_argument("--profile")
    for name in ("update", "complete"):
        item = commands.add_parser(name, help="Record status/remote IDs or settle an evidenced actual charge.")
        item.add_argument("--attempt", required=True)
        item.add_argument("--status", choices=sorted(STATUSES), default="completed" if name == "complete" else None)
        item.add_argument("--actual-credits", type=nonnegative)
        item.add_argument("--balance-after", type=nonnegative)
        for flag in ("job-id", "media-id", "notes", "settlement-evidence"):
            item.add_argument("--" + flag)
    item = commands.add_parser("register", help="Register an existing generated file or external link.")
    item.add_argument("--exercise", required=True)
    item.add_argument("--attempt")
    item.add_argument("--shot", help="Shot for an authored asset without a generation attempt.")
    item.add_argument("--id")
    item.add_argument("--kind", choices=("image", "video", "animation", "external"), required=True)
    location = item.add_mutually_exclusive_group(required=True)
    location.add_argument("--file")
    location.add_argument("--url")
    item.add_argument("--title", required=True)
    item.add_argument("--alt", required=True)
    item.add_argument("--width", type=nonnegative)
    item.add_argument("--height", type=nonnegative)
    item.add_argument("--duration", type=float)
    item.add_argument("--poster")
    item.add_argument("--source", default="Google Flow")
    item.add_argument("--license", default="Generated for SpotBot; provider terms apply")
    args = parser.parse_args()
    try:
        if args.command == "serve":
            if not 1024 <= args.port <= 65535:
                raise ValueError("Choose a port between 1024 and 65535.")
            server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
            server.daemon_threads = True
            print(f"Exercise media dashboard: http://127.0.0.1:{args.port}", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            return
        if args.command == "state":
            result = state()
        elif args.command == "budget":
            with locked():
                result = budget(read_json(MANIFEST), ledger())
        elif args.command == "start-budget-period":
            with locked():
                manifest, records = read_json(MANIFEST), ledger()
                period = start_budget_period(manifest, records, period_id=args.id,
                                            credit_limit=args.limit, authorization=args.authorization)
                result = {"period": period, "budget": budget(manifest, records)}
                write_json(MANIFEST, manifest)
        elif args.command == "reserve":
            result = reserve(args)
        elif args.command in ("update", "complete"):
            result = update_attempt(args)
        else:
            result = register(args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
