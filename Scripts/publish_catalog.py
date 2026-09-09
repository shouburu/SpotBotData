#!/usr/bin/env python3
"""Audit the normalized source, then delegate to SpotBot's standard publisher.

The delegated publisher defaults to an offline dry run. Cloud comparison and
apply remain explicit modes; this wrapper never chooses a cloud target.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from build_catalog import ROOT, build


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--app-root', type=Path, default=ROOT.parent / 'SpotBot')
    parser.add_argument('--help', action='store_true')
    options, arguments = parser.parse_known_args()
    if options.help:
        print(__doc__)
        print('Usage: python3 Scripts/publish_catalog.py [--app-root ../SpotBot] [publisher options]')
        print('Publisher options: --dry-run; --compare-cloud --endpoint URL --project-id ID --api-url URL;')
        print('  --apply also requires --confirm-project ID --approved-plan HASH --report PATH.')
        print('The source is always this repository\'s catalog.json. No credentials are stored here.')
        return 0
    if any(value == '--source' or value.startswith('--source=') for value in arguments):
        parser.error('The only source is this repository\'s catalog.json; edit and review it before publishing.')
    if any(value == '--expected-source-hash' or value.startswith('--expected-source-hash=') for value in arguments):
        parser.error('The expected source hash is supplied by the completed source audit and cannot be overridden.')
    if '--report' in arguments:
        position = arguments.index('--report')
        if position + 1 < len(arguments):
            report = Path(arguments[position + 1]).resolve()
            if report == ROOT or (ROOT in report.parents and (ROOT / 'reports').resolve() not in report.parents):
                parser.error('Publication reports inside SpotBotData must use the ignored reports directory, preserving source and tooling.')
    app = options.app_root.resolve()
    if not (app / 'scripts/appwrite/standard-catalog-publish.ts').is_file():
        parser.error('The selected SpotBot checkout does not contain the standard catalog publisher.')
    # Validate legal/editorial source completeness without touching generated files.
    result = build(True, app / 'packages/shared/src/catalogData.ts', app / 'apps/backend/src/appwrite/starterCatalogData.ts', app)
    print(f"Source audit accepted revision {result['revision']}: {result['exercises']} exercises, {result['redirects']} redirects.", flush=True)
    return subprocess.call(['npm', '--prefix', str(app), 'run', 'appwrite:standard-catalog:publish', '--',
                            '--source', str(ROOT / 'catalog.json'),
                            '--expected-source-hash', result['sharedValidation']['sourceFileSha256'], *arguments])


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (KeyError, TypeError, ValueError, OSError) as error:
        print(f'Catalog publication refused: {error}', file=sys.stderr)
        raise SystemExit(1)
