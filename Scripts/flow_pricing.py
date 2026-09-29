#!/usr/bin/env python3
"""Read current account-specific Flow generation prices without generating media."""

import argparse
import asyncio
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


async def read_prices(project_id):
    import structlog
    from gflow_cli import profile_store
    from gflow_cli.config import get_settings
    from gflow_cli.api.client import FlowApiClient
    from gflow_cli.api.video_extend import _inner

    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(40))
    profile = profile_store.resolve_profile(None)
    profile_dir = get_settings().profile_subdir(profile)
    async with FlowApiClient(profile_dir, headless=True) as client:
        payload = _inner(await client.capability_listing(project_id))
        user = payload.get('userData', {})
        tier = user.get('serviceTier')
        if not tier or not isinstance(user.get('credits'), int):
            raise ValueError('Flow did not provide a recognized tier and credit balance.')
        offers = []
        for group, kind in [('imageModelFamilies', 'image'), ('videoModelFamilies', 'video')]:
            for family in payload.get('modelConfig', {}).get(group, []):
                for usage in family.get('usages', []):
                    cost = usage.get('creditMapping', {}).get(tier, {}).get('cost')
                    if type(cost) is not int or cost < 0:
                        continue
                    offers.append({
                        'kind': kind, 'family': family.get('displayName'),
                        'modelKey': usage.get('key'), 'credits': cost,
                        'durationSeconds': usage.get('videoLengthSeconds'),
                        'resolutions': usage.get('supportedResolutions', []),
                        'aspects': usage.get('supportedAspectRatios', []),
                        'requirements': usage.get('requirements', []),
                    })
        if not offers:
            raise ValueError('No account-specific Flow prices could be verified.')
        return {
            'observedAt': datetime.now(timezone.utc).isoformat(),
            'source': 'Flow projectInitialData modelConfig creditMapping for current account tier',
            'projectId': project_id, 'balance': user['credits'],
            'offers': offers,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project')
    parser.add_argument('--model-key', help='Return one exact orderable model price, e.g. abra_i2v_8s.')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if importlib.util.find_spec('gflow_cli') is None:
        executable = shutil.which('gflow')
        python = Path(executable).resolve().parent / 'python' if executable else None
        if args.worker or not python or not python.exists():
            parser.error('Cannot find gflow\'s Python runtime. Install gflow-cli first.')
        return subprocess.call([str(python), str(Path(__file__).resolve()), *sys.argv[1:], '--worker'])
    try:
        manifest = json.loads((ROOT / 'form-media/manifest.json').read_text())
        project_id = args.project or manifest.get('projectId')
        if not project_id:
            raise ValueError('Create the pilot Flow project and save its projectId first.')
        snapshot = asyncio.run(read_prices(project_id))
        target = ROOT / 'form-media/pricing.json'
        temporary = target.with_suffix('.tmp')
        temporary.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n')
        temporary.replace(target)
        if args.model_key:
            matches = [offer for offer in snapshot['offers'] if offer['modelKey'] == args.model_key]
            if len(matches) != 1:
                raise ValueError('Exact model price unavailable; do not submit a generation.')
            print(json.dumps({**matches[0], 'observedAt': snapshot['observedAt'], 'balance': snapshot['balance'], 'source': snapshot['source']}))
        else:
            print(json.dumps({'observedAt': snapshot['observedAt'], 'balance': snapshot['balance'], 'offers': len(snapshot['offers']), 'file': str(target)}))
        return 0
    except Exception as error:
        print(f'Flow pricing unavailable ({type(error).__name__}); do not submit a generation.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
