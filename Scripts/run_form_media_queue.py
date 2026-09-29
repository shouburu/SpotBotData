#!/usr/bin/env python3
"""Run explicitly named active-round shots sequentially, resuming existing outputs."""
import argparse
import json
import re
import subprocess
import sys

import form_media as media


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shots', nargs='+', required=True)
    parser.add_argument('--round', dest='round_id', help='Defaults to the manifest active round.')
    args = parser.parse_args()
    round_id = args.round_id or media.read_json(media.MANIFEST).get('activeRoundId')
    if not isinstance(round_id, str) or not re.fullmatch(r'round-[1-9][0-9]*', round_id):
        raise ValueError('A valid production round is required.')
    jobs = {j['shot']: j for j in media.read_json(media.MEDIA / f'{round_id}-jobs.json')['jobs']}
    if len(args.shots) != len(set(args.shots)) or any(s not in jobs for s in args.shots):
        raise ValueError('Name each known queue shot exactly once.')
    for shot in args.shots:
        job = jobs[shot]
        if not isinstance(job.get('endFrameSameAsStart', False), bool):
            raise ValueError('endFrameSameAsStart must be an explicit boolean.')
        if job.get('endFrameSameAsStart') and (job['kind'] != 'video' or not job.get('referenceShot')):
            raise ValueError('Matching end frames require a video with a separately reviewed starting frame.')
        with media.locked():
            records = media.ledger()
            manifest = media.read_json(media.MANIFEST)
        if manifest.get('activeRoundId') != job['roundId'] or job['roundId'] != round_id:
            raise ValueError('This production round is no longer active.')
        media.require_exercise(manifest, job['exerciseId'])
        if job.get('model') and job['model'] != ('nano-pro' if job['kind'] == 'image' else 'omni-flash'):
            raise ValueError('The requested model differs from the reviewed runner model.')
        if job.get('promptSha256'):
            prompt_path = media.ROOT / 'form-media/prompts' / f'{shot}.txt'
            if media.relative(prompt_path) != job.get('promptFile') or media.sha256(prompt_path) != job['promptSha256']:
                raise ValueError('The planned prompt changed; record its reviewed version before submission.')
        if job.get('productionDisposition') in {'not-submitted-reference-fallback', 'blocked-review-gate'}:
            print(f'Held: {shot}. {job.get("holdReason", "Use the recorded external reference.")}', flush=True)
            continue
        prior = [a for a in records['attempts'] if a['shot'] == shot and a['exerciseId'] == job['exerciseId']
                 and a.get('roundId') == job['roundId']]
        completed = [a for a in prior if a['status'] == 'completed' and a.get('actualCredits') is not None]
        if any(media.unresolved(a) for a in records['attempts']):
            raise ValueError('Reconcile the unresolved submission before continuing the queue.')
        if completed:
            attempt = completed[-1]
            if (job.get('promptSha256') and attempt.get('promptSha256') != job['promptSha256']):
                raise ValueError(f'{shot} has an older completed prompt version. Review the held revision and submit it explicitly; the queue will not relabel an older output with new phase instructions.')
            print(f'Using existing output for {shot}: {attempt["id"]}', flush=True)
        else:
            if prior:
                raise ValueError(f'{shot} has a previous unsuccessful attempt. Review it and retry explicitly; the queue will not regenerate it automatically.')
            command = [sys.executable, str(media.ROOT / 'Scripts/generate_form_media.py'),
                       '--exercise', job['exerciseId'], '--shot', shot, '--kind', job['kind'], '--aspect', job['aspect']]
            if job.get('duration'):
                command.extend(['--duration', str(job['duration'])])
            for reference_file in job.get('referenceFiles', []):
                if job['kind'] != 'image':
                    raise ValueError('Motion must use its separately reviewed starting frame.')
                path = media.repo_path(reference_file['path'])
                if not path.is_relative_to((media.MEDIA / 'assets').resolve()) or media.sha256(path) != reference_file['sha256']:
                    raise ValueError('The pinned style/setup reference is missing or changed.')
                command.extend(['--reference', media.relative(path)])
            reference_shot = job.get('referenceShot')
            if reference_shot:
                reference_job = jobs[reference_shot]
                references = [a for a in records['attempts'] if a['shot'] == reference_shot
                              and a['exerciseId'] == reference_job['exerciseId']
                              and a.get('roundId') == reference_job['roundId']
                              and a['status'] == 'completed' and a.get('actualCredits') is not None]
                if not references:
                    raise ValueError(f'Missing completed reference: {reference_shot}')
                if job.get('referenceAttemptId'):
                    pinned = [a for a in references if a['id'] == job['referenceAttemptId']]
                    if len(pinned) != 1:
                        raise ValueError('The pinned starting attempt is not a settled output of this reference shot.')
                    reference = pinned[0]
                else:
                    reference = references[-1]
                path = media.repo_path(reference['outputPath'])
                if job.get('referenceDerivativeId'):
                    derivatives = media.read_json(media.MEDIA / 'reference-derivatives.json')['derivatives']
                    matches = [d for d in derivatives if d['id'] == job['referenceDerivativeId']]
                    if len(matches) != 1:
                        raise ValueError('The authored reference must have one provenance record.')
                    derivative = matches[0]
                    source = next((a for a in records['attempts'] if a['id'] == derivative['sourceAttemptId']), None)
                    if (not source or source['status'] != 'completed' or source.get('actualCredits') is None
                            or (job.get('referenceAttemptId') and source['id'] != reference['id'])
                            or source['exerciseId'] != job['exerciseId'] or source['shot'] != reference_shot
                            or source.get('roundId') != job['roundId']
                            or derivative['sourcePath'] != source['outputPath']
                            or media.sha256(media.repo_path(source['outputPath'])) != derivative['sourceSha256']):
                        raise ValueError('The authored reference source is not the recorded settled pose.')
                    path = media.repo_path(derivative['path'])
                    if not path.is_relative_to((media.MEDIA / 'assets').resolve()) or media.sha256(path) != derivative['sha256']:
                        raise ValueError('The authored reference is missing or changed.')
                if job['kind'] == 'video':
                    reviews = []
                    for review_path in sorted(media.MEDIA.glob(f'{round_id}-*reviews.json')):
                        reviews.extend(media.read_json(review_path, {'reviews': []})['reviews'])
                    matching = [r for r in reviews if r.get('reviewerType') == 'ai'
                                and r.get('shot') == reference_shot
                                and r.get('outputPath') == media.relative(path)
                                and r.get('outputSha256') == media.sha256(path)]
                    matching.sort(key=lambda r: r.get('reviewedAt', ''))
                    latest = matching[-1] if matching else None
                    conflicting = latest and any(r.get('reviewedAt') == latest.get('reviewedAt')
                                                  and r['status'] != latest['status'] for r in matching)
                    if not latest or conflicting or latest['status'] != 'ready-to-animate':
                        raise ValueError(f'Inspect the exact starting frame before paid motion: {reference_shot}')
                command.extend(['--reference', media.relative(path)])
                if job.get('endFrameSameAsStart'):
                    command.extend(['--end-reference', media.relative(path)])
            subprocess.run(command, cwd=media.ROOT, check=True)
            with media.locked():
                attempt = [a for a in media.ledger()['attempts'] if a['shot'] == shot
                           and a['exerciseId'] == job['exerciseId'] and a.get('roundId') == round_id][-1]
        subprocess.run([sys.executable, str(media.ROOT / 'Scripts/prepare_form_media_asset.py'),
                        '--attempt', attempt['id'], '--title', job['title'], '--alt', job['alt']],
                       cwd=media.ROOT, check=True)
        with media.locked():
            manifest = media.read_json(media.MANIFEST)
            exercise = manifest['exercises'][job['exerciseId']]
            exercise['productionStatus'] = 'drafts-in-progress'
            media.write_json(media.MANIFEST, manifest)
        print(f'Ready for review: {shot}', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'Queue stopped: {error}')
