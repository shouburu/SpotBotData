#!/usr/bin/env python3
"""Reversible gflow 0.75.0 image-model picker readback fix.

The migrated Flow menu can close before the selected image model appears in
the settings button. Without a readback, the first generation may use the old
model even though gflow logs the clicked menu item as selected.
"""
import importlib.metadata
from pathlib import Path

VERSION = '0.75.0'
if importlib.metadata.version('gflow-cli') != VERSION:
    raise SystemExit(f'This patch is only for gflow-cli {VERSION}.')

import gflow_cli.api.transports.migrated_composer as module

path = Path(module.__file__)
before = '''        await items.nth(hits[0]).click(timeout=4000)
        log.info("migrated.image_model_selected", model=offered[hits[0]], requested=model.value)
'''
after = '''        await items.nth(hits[0]).click(timeout=4000)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + 5.0
        observed = current
        while loop.time() < deadline:
            remaining_ms = max(1, int((deadline - loop.time()) * 1000))
            observed = (await button.text_content(timeout=min(1000, remaining_ms)) or "").strip()
            if matcher.matches(observed):
                log.info("migrated.image_model_selected", model=observed,
                         requested=model.value, picker_readback=True)
                return
            await asyncio.sleep(min(0.1, max(0.0, deadline - loop.time())))
        raise UiSelectorDriftError(
            detail=(f"migrated host: image model picker did not confirm '{model.value}' "
                    f"within 5 seconds after selection; observed {observed[:160]!r}; "
                    "refusing to continue (host=migrated)"),
        )
'''
text = path.read_text()
if text.count(after) == 1:
    print(f'Already applied: {path}')
elif text.count(before) == 1:
    backup = path.with_suffix(path.suffix + '.spotbot-round10-backup')
    if backup.exists():
        raise SystemExit(f'Backup already exists; inspect {backup}')
    backup.write_text(text)
    path.write_text(text.replace(before, after, 1))
    print(f'Applied to {path}; reversible backup {backup}')
else:
    raise SystemExit('Expected 0.75.0 method body differs; patch refused.')
