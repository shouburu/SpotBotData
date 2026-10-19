#!/usr/bin/env python3
"""Apply/restore the reviewed gflow 0.75.0 migrated record compatibility fix.

Flow changed the video record marker from CAE to null after accepting and
billing submissions. This ports upstream #948's record recognition and exact
workflow selection from project-wide status replies, preserving prompt guards.
No login, browser, generation, or network calls. Unknown source is refused.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

from patch_gflow_macos import atomic_write, digest

VERSION = "0.75.0"
ORIGINAL_SHA = "c6018f48894d70c5a4eeba88ff37334dbdc16a3e360b40660d58df34bcd415ac"
UPSTREAM_COMMIT = "52b1c822f8c6f9b42be15e0d20f7302640bb0e4c"
MARKER_ONLY_SHA = "235ee432fd01bdaabcf44cd5738fb7389e3e7b431cff20bef3d60abf46f170a9"
COMPOSER_ORIGINAL_SHA = "5cf39454c5c81f08ff92c31f10eba9618b942c2dc24e73da111c8c8c9dfa2d0c"
COMPOSER_PATCHED_SHA = "c3a2689226e02a6f32130b95595ff07f3d828817121d3dfac55806394adc3212"
ANCHOR = '    if len(node) < 6 or node[3] != "CAE":\n'
REPLACEMENT = (
    "    # Upstream #948: Flow sends null in slot 3 since October 2026.\n"
    "    # Three UUIDs and a DETAILS list identify a record; ignore the marker.\n"
    "    if len(node) < 6 or not isinstance(node[5], list):\n"
)
FIND_ANCHOR = '''def _find_record(node: object) -> list[Any] | None:
    items = _as_list(node)
    if items is None:
        return None
    if _is_record(items):
        return items
    for child in items:
        found = _find_record(child)
        if found is not None:
            return found
    return None
'''
FIND_REPLACEMENT = '''def _find_record(node: object, want: tuple[int, str] | None = None) -> list[Any] | None:
    items = _as_list(node)
    if items is None:
        return None
    if _is_record(items) and (want is None or items[want[0]] == want[1]):
        return items
    for child in items:
        found = _find_record(child, want)
        if found is not None:
            return found
    return None
'''
RECORD_ANCHOR = "def generation_record(rpcid: str, payload: Any) -> GenerationRecord:\n"
RECORD_REPLACEMENT = '''def generation_record(
    rpcid: str,
    payload: Any,
    *,
    workflow_id: str | None = None,
    media_id: str | None = None,
) -> GenerationRecord:
'''
SEARCH_ANCHOR = "    rec = _find_record(payload)\n"
SEARCH_REPLACEMENT = '''    want: tuple[int, str] | None = None
    if workflow_id is not None:
        want = (0, workflow_id)
    elif media_id is not None:
        want = (2, media_id)
    rec = _find_record(payload, want)
'''
COMPOSER_ANCHOR = '''                elif rid in STATUS_RPCS and workflow:
                    try:
                        rec = generation_record(rid, payload)
                    except WireFormatError:
                        continue
                    if rec.workflow_id != workflow["id"]:
                        continue
'''
COMPOSER_REPLACEMENT = '''                elif rid in STATUS_RPCS and workflow:
                    try:
                        rec = generation_record(rid, payload, workflow_id=workflow["id"])
                    except WireFormatError:
                        continue
'''


def reviewed_replace(source: str, before: str, after: str) -> str:
    if source.count(before) != 1:
        raise SystemExit("Source anchor mismatch; nothing changed.")
    return source.replace(before, after, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("apply", "restore", "status"))
    parser.add_argument("--python", help="Python executable from gflow's uv environment")
    args = parser.parse_args()
    executable = args.python
    if not executable:
        command = shutil.which("gflow")
        if not command:
            raise SystemExit("gflow is not on PATH; supply --python.")
        first_line = Path(command).resolve().read_text().splitlines()[0]
        if not first_line.startswith("#!/") or " " in first_line[2:]:
            raise SystemExit("Cannot resolve gflow Python safely; supply --python.")
        executable = first_line[2:]
    probe = (
        "import importlib.util,json; from importlib.metadata import version; "
        "from gflow_cli.config import get_settings; "
        "print(json.dumps({'version':version('gflow-cli'),"
        "'module':importlib.util.find_spec('gflow_cli').origin,"
        "'home':str(get_settings().home)}))"
    )
    info = json.loads(subprocess.check_output([executable, "-c", probe], text=True))
    if info["version"] != VERSION:
        raise SystemExit(f"Expected gflow {VERSION}; found {info['version']}. Reinspect before patching.")
    target = Path(info["module"]).parent / "api" / "transports" / "batchexecute.py"
    current = target.read_bytes()
    backup = Path(info["home"]) / "patch-backups" / f"batchexecute-{VERSION}-{ORIGINAL_SHA[:12]}.py"
    if digest(current) == ORIGINAL_SHA:
        original = current
    elif backup.exists() and digest(backup.read_bytes()) == ORIGINAL_SHA:
        original = backup.read_bytes()
    else:
        raise SystemExit("Unrecognized source and no verified original backup; nothing changed.")
    source = original.decode("utf-8")
    for before, after in ((ANCHOR, REPLACEMENT), (FIND_ANCHOR, FIND_REPLACEMENT),
                          (RECORD_ANCHOR, RECORD_REPLACEMENT), (SEARCH_ANCHOR, SEARCH_REPLACEMENT)):
        source = reviewed_replace(source, before, after)
    patched = source.encode("utf-8")
    patched_sha = digest(patched)
    if digest(current) not in (ORIGINAL_SHA, MARKER_ONLY_SHA, patched_sha):
        raise SystemExit("Installed parser differs from reviewed versions; nothing changed.")
    composer = target.with_name("migrated_composer.py")
    composer_current = composer.read_bytes()
    composer_backup = backup.parent / f"migrated-composer-wire-{VERSION}-{COMPOSER_ORIGINAL_SHA[:12]}.py"
    if digest(composer_current) == COMPOSER_ORIGINAL_SHA:
        composer_original = composer_current
    elif composer_backup.exists() and digest(composer_backup.read_bytes()) == COMPOSER_ORIGINAL_SHA:
        composer_original = composer_backup.read_bytes()
    else:
        raise SystemExit("Unknown composer and no verified wire backup; nothing changed.")
    composer_patched = reviewed_replace(composer_original.decode("utf-8"),
                                        COMPOSER_ANCHOR, COMPOSER_REPLACEMENT).encode("utf-8")
    if (digest(composer_patched) != COMPOSER_PATCHED_SHA
            or digest(composer_current) not in (COMPOSER_ORIGINAL_SHA, COMPOSER_PATCHED_SHA)):
        raise SystemExit("Composer differs from reviewed workflow-filter states; nothing changed.")
    was_patched = digest(current) == patched_sha
    # Inspect both files and both backups before any mutation.
    for path, expected in ((backup, ORIGINAL_SHA), (composer_backup, COMPOSER_ORIGINAL_SHA)):
        if path.exists() and digest(path.read_bytes()) != expected:
            raise SystemExit("Existing backup is not the reviewed original; nothing changed.")
    if args.action == "apply":
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            atomic_write(backup, original, 0o600)
        if not composer_backup.exists():
            atomic_write(composer_backup, composer_original, 0o600)
        if not was_patched:
            atomic_write(target, patched, target.stat().st_mode & 0o777)
        if digest(composer_current) != COMPOSER_PATCHED_SHA:
            atomic_write(composer, composer_patched, composer.stat().st_mode & 0o777)
    elif args.action == "restore":
        if digest(composer_current) == COMPOSER_PATCHED_SHA:
            atomic_write(composer, composer_original, composer.stat().st_mode & 0o777)
        atomic_write(target, original, target.stat().st_mode & 0o777)
    parser_installed_sha = digest(target.read_bytes())
    composer_installed_sha = digest(composer.read_bytes())
    print(json.dumps({"action": args.action, "version": VERSION, "path": str(target),
                      "patched": parser_installed_sha == patched_sha and composer_installed_sha == COMPOSER_PATCHED_SHA,
                      "sha256": parser_installed_sha, "patchedSha256": patched_sha,
                      "backup": str(backup), "upstreamCommit": UPSTREAM_COMMIT,
                      "composerPath": str(composer), "composerSha256": composer_installed_sha,
                      "composerPatchedSha256": COMPOSER_PATCHED_SHA,
                      "composerBackup": str(composer_backup), "workflowFilter": composer_installed_sha == COMPOSER_PATCHED_SHA}, indent=2))


if __name__ == "__main__":
    main()
