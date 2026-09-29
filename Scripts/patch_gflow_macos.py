#!/usr/bin/env python3
"""Apply/restore the reviewed gflow 0.75.0 macOS cookie-reader workaround.

No login, Keychain access, or generation. Refuses unknown installed source.
Backups live with gflow's local application data, never in the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

VERSION = "0.75.0"
ORIGINAL_SHA = "25aed0e5e2f2ad95d186e85a0f2a276eb86c747faa7be923ffa05c153860b89a"
ANCHOR = "    try:\n        return _get_chrome_cookies3(profile_dir=profile_dir)\n"
REPLACEMENT = (
    "    # SpotBot macOS workaround: use the isolated profile reader directly.\n"
    "    # browser_cookie3 otherwise requests Chrome Safe Storage on every call.\n"
    "    if sys.platform == \"darwin\":\n"
    "        return await _get_chrome_cookies_playwright(profile_dir=profile_dir)\n"
    + ANCHOR
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    fd, name = tempfile.mkstemp(prefix=".gflow-patch-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("apply", "restore", "status"))
    parser.add_argument("--python", help="Python executable from gflow's uv environment")
    args = parser.parse_args()
    if sys.platform != "darwin":
        raise SystemExit("This workaround is macOS-only.")
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
    target = Path(info["module"]).parent / "auth" / "cookies.py"
    current = target.read_bytes()
    backup = Path(info["home"]) / "patch-backups" / f"cookies-{VERSION}-{ORIGINAL_SHA[:12]}.py"
    if digest(current) == ORIGINAL_SHA:
        original = current
    elif backup.exists() and digest(backup.read_bytes()) == ORIGINAL_SHA:
        original = backup.read_bytes()
    else:
        raise SystemExit("Unrecognized source and no verified original backup; nothing changed.")
    source = original.decode("utf-8")
    if source.count(ANCHOR) != 1:
        raise SystemExit("Source anchor mismatch; nothing changed.")
    patched = source.replace("import structlog\n", "import sys\n\nimport structlog\n", 1).replace(ANCHOR, REPLACEMENT).encode("utf-8")
    patched_sha = digest(patched)
    if digest(current) not in (ORIGINAL_SHA, patched_sha):
        raise SystemExit("Installed source differs from both reviewed versions; nothing changed.")
    was_patched = digest(current) == patched_sha
    if args.action == "apply" and not was_patched:
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists() and digest(backup.read_bytes()) != ORIGINAL_SHA:
            raise SystemExit("Existing backup is not the reviewed original; nothing changed.")
        if not backup.exists():
            atomic_write(backup, original, 0o600)
        atomic_write(target, patched, target.stat().st_mode & 0o777)
    elif args.action == "restore" and was_patched:
        atomic_write(target, original, target.stat().st_mode & 0o777)
    print(json.dumps({"action": args.action, "version": VERSION, "path": str(target),
                      "patched": digest(target.read_bytes()) == patched_sha,
                      "sha256": digest(target.read_bytes()), "backup": str(backup)}, indent=2))


if __name__ == "__main__":
    main()
