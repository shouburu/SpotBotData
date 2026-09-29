#!/usr/bin/env python3
"""Pinned prompt/model guards and outgoing containment audit; never submits itself."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from patch_gflow_macos import atomic_write, digest

VERSION = "0.75.0"
ORIGINAL_SHA = "a8753ba6162678c3f4a9e87d0a3919f88547c7c1dcb07b910473e2e669c1f9b6"
PREVIOUS_AUDIT_SHA = "32beede12474e570ae15dd546cab1311a31f9ed9e1982fa091bda483053c8b9b"
REVISION_3_SHA = "e3f71ec9d488b62c8de168029420daa3da29411d6b1e8154c09ca4c169fac141"
IMAGE_PICKER_BASE_SHA = "14265d189d5d2bf8a1820e16beacae8bc117a7a1a1624a3b6d8d833687a34169"
IMAGE_PICKER_SHA = "5cf39454c5c81f08ff92c31f10eba9618b942c2dc24e73da111c8c8c9dfa2d0c"
START = '    async def send_prompt(self, page: Page, prompt: str, *, append: bool = False) -> None:\n'
END = '    async def submit_and_observe(\n'
REPLACEMENT = r'''    async def send_prompt(self, page: Page, prompt: str, *, append: bool = False) -> None:
        """SpotBot guard: replace ordinary draft text and verify it before submit.

        Start-frame chips live outside the text editor. Mention-based requests keep
        their inline chips and may append only when no old ordinary text remains.
        """
        composer = page.locator(COMPOSER).first
        if not await composer.count():
            raise UiSelectorDriftError(detail="migrated host: prompt editor missing; refusing to submit")

        def normalized(value: str) -> str:
            return re.sub(r"\s+", " ", value.replace("\u200b", "").replace("\ufeff", "")).strip()

        async def ordinary_text() -> str:
            # Read actual editor text, excluding inline reference labels. Preserve
            # word boundaries from ProseMirror paragraphs and hard line breaks.
            return await composer.evaluate("""(el) => {
                const read = (n) => {
                    if (n.nodeType === Node.TEXT_NODE) return n.textContent || '';
                    if (n.nodeType !== Node.ELEMENT_NODE) return '';
                    if (n.matches('.mention-chip')) return '';
                    if (n.tagName === 'BR') return '\\n';
                    const text = [...n.childNodes].map(read).join('');
                    return text + (['P', 'DIV'].includes(n.tagName) ? '\\n' : '');
                };
                return read(el);
            }""")

        async def frame_state() -> list:
            # Retain sources only in memory; never log signed image URLs.
            return await page.locator(BOUND_CHIP).evaluate_all("""nodes => nodes.map(n => ({
                text: (n.textContent || '').trim(),
                images: [...n.querySelectorAll('img')].map(i => i.getAttribute('src'))
            }))""")

        before_frames = await frame_state()
        before_mentions = await self.read_chips(page)
        if append:
            if normalized(await ordinary_text()):
                raise UiSelectorDriftError(detail="migrated host: stale text remains beside reference chips; refusing to submit")
            # Keep the caret and the original mention chips from the verified attach path.
            await page.keyboard.insert_text(prompt)
        else:
            if before_mentions:
                raise UiSelectorDriftError(detail="migrated host: unexpected mention chips in a plain prompt; refusing to remove references or submit")
            await self._click(page, composer, named=COMPOSER, timeout=5000)
            # Locator.fill supports contenteditable, replaces its text, and dispatches
            # input without Enter. It never selects the surrounding Start image chip.
            await composer.fill(prompt, timeout=5000)
        await page.wait_for_timeout(200)
        actual = await ordinary_text()
        if normalized(actual) != normalized(prompt):
            raise UiSelectorDriftError(detail="migrated host: prompt readback differs from intended text; refusing to submit")
        if before_frames != await frame_state() or before_mentions != await self.read_chips(page):
            raise ReferenceNotFoundError(detail="migrated host: reference chips changed while replacing prompt text; refusing to submit")
        log.info("migrated.prompt_readback_verified", chars=len(prompt), append=append,
                 bound_frames=len(before_frames), mention_chips=len(before_mentions))

'''


WIRE_AUDIT = r'''        # SpotBot diagnostic: inspect only this submit RPC's decoded arguments.
        # A matching leaf proves containment, not an undocumented provider prompt slot.
        # Never persist raw bodies, arbitrary strings, headers, tokens or signed URLs.
        import hashlib
        import json
        from urllib.parse import parse_qs

        request_audits: dict[Any, dict[str, Any]] = {}

        def normalized_prompt(value: str) -> str:
            return re.sub(r"\s+", " ", value.replace("\u200b", "").replace("\ufeff", "")).strip()

        def audit_submit_request(request: Any, rpcid: str) -> None:
            audit_id = f"submit-{len(request_audits) + 1}"
            expected = normalized_prompt(expected_prompt or "")
            expected_ids = tuple(dict.fromkeys(
                value for value in (expect_media_id, *expect_reference_ids)
                if isinstance(value, str) and UUID_RE.fullmatch(value)
            ))
            summary: dict[str, Any] = {
                "request_audit_id": audit_id,
                "rpc": rpcid,
                "evidence_kind": "decoded-submit-argument-containment-not-provider-slot",
                "match_status": "not_observed",
                "structure_status": "unreadable",
                "parse_stage": "body",
                "expected_normalized_sha256": hashlib.sha256(expected.encode()).hexdigest(),
                "expected_normalized_chars": len(expected),
                "matching_leaf_count": 0,
                "model_key_candidates": [],
                "expected_reference_id_leaf_matches": {value: False for value in expected_ids},
            }
            request_audits[request] = summary
            try:
                raw = request.post_data
                if not isinstance(raw, str) or not raw or len(raw) > 2_000_000:
                    summary["structure_status"] = "body_unavailable_or_too_large"
                else:
                    # Decode form exactly once. _post_data() already unquotes, so do
                    # not reuse it here and accidentally decode prompt '+' or '%'.
                    summary["parse_stage"] = "form"
                    fields = parse_qs(raw, keep_blank_values=True, max_num_fields=64)
                    encoded = fields.get("f.req", [])
                    if len(encoded) != 1:
                        summary["structure_status"] = "freq_missing_or_ambiguous"
                    else:
                        summary["parse_stage"] = "envelope"
                        envelope = json.loads(encoded[0])
                        rpc_entries: list[tuple[list[int], Any]] = []
                        nodes = 0

                        def find_rpc(node: Any, path: list[int]) -> None:
                            nonlocal nodes
                            nodes += 1
                            if nodes > 10_000 or len(path) > 24:
                                raise ValueError("bounded_structure")
                            if not isinstance(node, list):
                                return
                            if len(node) >= 2 and node[0] == rpcid and isinstance(node[1], str):
                                rpc_entries.append((path, json.loads(node[1])))
                                return
                            for index, child in enumerate(node):
                                find_rpc(child, path + [index])

                        summary["parse_stage"] = "rpc_arguments"
                        find_rpc(envelope, [])
                        matches: list[dict[str, Any]] = []
                        models: list[dict[str, Any]] = []

                        def read_argument(node: Any, rpc_path: list[int], path: list[int]) -> None:
                            nonlocal nodes
                            nodes += 1
                            if nodes > 20_000 or len(path) > 32:
                                raise ValueError("bounded_structure")
                            if isinstance(node, list):
                                for index, child in enumerate(node):
                                    read_argument(child, rpc_path, path + [index])
                            elif isinstance(node, str):
                                value = normalized_prompt(node)
                                if expected and value == expected:
                                    matches.append({
                                        "rpc_entry_path": rpc_path,
                                        "argument_path": path,
                                        "normalized_sha256": hashlib.sha256(value.encode()).hexdigest(),
                                        "normalized_chars": len(value),
                                        "raw_chars": len(node),
                                        "raw_exact": node == expected_prompt,
                                    })
                                if len(node) <= 160 and MODEL_KEY.fullmatch(node):
                                    models.append({"key": node, "rpc_entry_path": rpc_path,
                                                   "argument_path": path})
                                if node in summary["expected_reference_id_leaf_matches"]:
                                    summary["expected_reference_id_leaf_matches"][node] = True
                            elif isinstance(node, dict):
                                # This protocol is positional. Do not guess paths or
                                # log arbitrary object keys if its schema changes.
                                raise ValueError("object_argument_not_supported")

                        summary["parse_stage"] = "argument_leaves"
                        for rpc_path, arguments in rpc_entries:
                            read_argument(arguments, rpc_path, [])
                        summary["parse_stage"] = "complete"
                        summary["structure_status"] = "decoded" if rpc_entries else "rpc_arguments_not_found"
                        summary["matching_leaf_count"] = len(matches)
                        summary["model_key_candidates"] = models[:8]
                        summary["model_key_candidate_count"] = len(models)
                        summary["match_status"] = ("exact_unique" if len(matches) == 1
                                                   else "multiple" if matches else "not_observed")
                        if len(matches) == 1:
                            summary["matching_leaf"] = matches[0]
            except Exception:
                # Observing a paid request must never abort it or manufacture a retry.
                # Exception text can contain payload values; retain only closed labels.
                summary["structure_status"] = "parse_or_shape_unrecognized"
                summary["match_status"] = "not_observed"
            log.info("migrated.outgoing_prompt_containment", **summary)

'''


def add_wire_audit(source: str) -> str:
    """Transform only reviewed 0.75.0 anchors; no browser or network operation."""
    substitutions = [
        ('        expect_media_id: str | None = None,\n',
         '        expected_prompt: str | None = None,\n        expect_media_id: str | None = None,\n'),
        ('        route_error: asyncio.Future[WireFormatError] = loop.create_future()\n\n'
         '        def on_request(request: Any) -> None:\n',
         '        route_error: asyncio.Future[WireFormatError] = loop.create_future()\n\n'
         + WIRE_AUDIT + '        def on_request(request: Any) -> None:\n'),
        ('            if expect_reference_ids:\n                problem = _r2v_body_problem',
         '            audit_submit_request(request, rpcid)\n            if expect_reference_ids:\n                problem = _r2v_body_problem'),
        ('                    workflow["id"] = rec.workflow_id\n',
         '                    workflow["id"] = rec.workflow_id\n'
         '                    audit = request_audits.get(response.request)\n'
         '                    log.info("migrated.outgoing_prompt_containment_result",\n'
         '                             request_audit_id=audit.get("request_audit_id") if audit else None,\n'
         '                             match_status=audit.get("match_status") if audit else "not_observed",\n'
         '                             rpc=rid, workflow_id=rec.workflow_id, media_id=rec.media_id)\n'),
        ('        if expect_media_id is not None or expect_reference_ids:\n            page.on("request", on_request)\n',
         '        page.on("request", on_request)\n'),
        ('            if expect_media_id is not None or expect_reference_ids:\n                page.remove_listener("request", on_request)\n',
         '            page.remove_listener("request", on_request)\n'),
        ('        expect_media_id=media_id,\n',
         '        expected_prompt=request.prompt,\n        expect_media_id=media_id,\n'),
    ]
    for before, after in substitutions:
        if source.count(before) != 1:
            raise SystemExit('Wire-audit source anchor mismatch; nothing changed.')
        source = source.replace(before, after, 1)
    return source


def add_model_readback(source: str) -> str:
    """Wait for the actual picker label, not the menu item that was clicked."""
    before = ('        await items.nth(hits[0]).click(timeout=4000)\n'
              '        log.info("migrated.model_selected", model=offered[hits[0]], requested=model.value)\n')
    after = '''        await items.nth(hits[0]).click(timeout=4000)
        # Flow updates this picker asynchronously. The old menu-item log could
        # precede the actual model/price change, including across billing tiers.
        loop = asyncio.get_running_loop()
        deadline = loop.time() + 5.0
        observed = current
        while loop.time() < deadline:
            remaining_ms = max(1, int((deadline - loop.time()) * 1000))
            observed = (await button.text_content(timeout=min(1000, remaining_ms)) or "").strip()
            if matcher.matches(observed):
                log.info("migrated.model_selected", model=observed,
                         requested=model.value, picker_readback=True)
                return
            await asyncio.sleep(min(0.1, max(0.0, deadline - loop.time())))
        raise UiSelectorDriftError(
            detail=(f"migrated host: model picker did not confirm '{model.value}' "
                    f"within 5 seconds after selection; observed {observed[:160]!r}; "
                    "refusing to continue (host=migrated)"),
        )
'''
    if source.count(before) != 1:
        raise SystemExit('Model-readback source anchor mismatch; nothing changed.')
    return source.replace(before, after, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['apply', 'restore', 'restore-previous', 'status'])
    parser.add_argument('--python')
    args = parser.parse_args()
    executable = args.python
    if not executable:
        command = shutil.which('gflow')
        if not command:
            raise SystemExit('gflow is missing; provide --python.')
        line = Path(command).resolve().read_text().splitlines()[0]
        if not line.startswith('#!/') or ' ' in line[2:]:
            raise SystemExit('Cannot safely resolve gflow Python.')
        executable = line[2:]
    probe = ("import importlib.util,json; from importlib.metadata import version; "
             "from gflow_cli.config import get_settings; "
             "print(json.dumps({'version':version('gflow-cli'),'module':importlib.util.find_spec('gflow_cli').origin,'home':str(get_settings().home)}))")
    info = json.loads(subprocess.check_output([executable, '-c', probe], text=True))
    if info['version'] != VERSION:
        raise SystemExit('Unknown gflow version; inspect before patching.')
    target = Path(info['module']).parent/'api/transports/migrated_composer.py'
    backup = Path(info['home'])/'patch-backups'/f'migrated-composer-{VERSION}-{ORIGINAL_SHA[:12]}.py'
    previous_backup = backup.parent/f'migrated-composer-{VERSION}-rev3-{REVISION_3_SHA[:12]}.py'
    current = target.read_bytes()
    if digest(current) == ORIGINAL_SHA:
        original = current
    elif backup.exists() and digest(backup.read_bytes()) == ORIGINAL_SHA:
        original = backup.read_bytes()
    else:
        raise SystemExit('Unknown source and no checksum-verified original; nothing changed.')
    source = original.decode()
    if source.count(START) != 1 or source.count(END) != 1:
        raise SystemExit('Method anchor mismatch; nothing changed.')
    begin, finish = source.index(START), source.index(END)
    if finish <= begin:
        raise SystemExit('Method boundaries differ; nothing changed.')
    legacy_patched = (source[:begin] + REPLACEMENT + source[finish:]).encode()
    revision_3 = add_wire_audit(legacy_patched.decode()).encode()
    if digest(revision_3) != REVISION_3_SHA:
        raise SystemExit('Reviewed revision 3 transform differs; nothing changed.')
    patched = add_model_readback(revision_3.decode()).encode()
    patched_sha = digest(patched)
    # Round10 adds a narrowly reviewed image-picker readback to the existing
    # video/prompt guards. Accept only that exact combined source and backup.
    image_backup = target.with_suffix(target.suffix + '.spotbot-round10-backup')
    image_picker_verified = (digest(current) == IMAGE_PICKER_SHA
        and image_backup.exists() and digest(image_backup.read_bytes()) == IMAGE_PICKER_BASE_SHA
        and IMAGE_PICKER_BASE_SHA == patched_sha)
    guarded_states = {digest(legacy_patched), PREVIOUS_AUDIT_SHA, REVISION_3_SHA, patched_sha}
    if image_picker_verified:
        guarded_states.add(IMAGE_PICKER_SHA)
    if digest(current) not in {ORIGINAL_SHA, *guarded_states}:
        raise SystemExit('Installed source differs from reviewed original/DOM/audit states; nothing changed.')
    if args.action == 'apply':
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists() and digest(backup.read_bytes()) != ORIGINAL_SHA:
            raise SystemExit('Existing original backup has changed; nothing changed.')
        if not backup.exists():
            atomic_write(backup, original, 0o600)
        if previous_backup.exists() and digest(previous_backup.read_bytes()) != REVISION_3_SHA:
            raise SystemExit('Existing revision 3 backup has changed; nothing changed.')
        if not previous_backup.exists():
            atomic_write(previous_backup, revision_3, 0o600)
        if digest(current) not in {patched_sha, *({IMAGE_PICKER_SHA} if image_picker_verified else set())}:
            atomic_write(target, patched, target.stat().st_mode & 0o777)
    elif args.action == 'restore' and digest(current) in guarded_states:
        atomic_write(target, original, target.stat().st_mode & 0o777)
    elif args.action == 'restore-previous':
        if not previous_backup.exists() or digest(previous_backup.read_bytes()) != REVISION_3_SHA:
            raise SystemExit('No verified revision 3 backup; nothing changed.')
        atomic_write(target, previous_backup.read_bytes(), target.stat().st_mode & 0o777)
    installed_sha = digest(target.read_bytes())
    print(json.dumps({'action':args.action,'version':VERSION,'path':str(target),
                      'patched':installed_sha == patched_sha or image_picker_verified,
                      'domGuard':installed_sha in guarded_states,
                      'outgoingContainmentAudit':installed_sha in {REVISION_3_SHA, patched_sha, *({IMAGE_PICKER_SHA} if image_picker_verified else set())},
                      'modelReadbackGuard':installed_sha == patched_sha or image_picker_verified,
                      'patchRevision':5 if image_picker_verified else 4,
                      'sha256':installed_sha,'backup':str(backup),
                      'previousRevisionBackup':str(previous_backup)},indent=2))

if __name__ == '__main__':
    main()
