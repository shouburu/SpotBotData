#!/usr/bin/env python3
"""Apply saved AI verdicts and explicitly authored corrective prompts to the queue.

Does not inspect media, invent verdicts, submit generations, or change human
exercise decisions. Run sync_form_media_reviews.py before this command.
"""
import argparse
from pathlib import Path
import form_media as f


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', required=True)
    parser.add_argument('--corrections-dir', required=True)
    args = parser.parse_args()
    corrections = f.contained(f.ROOT, args.corrections_dir)
    if not corrections.is_relative_to((f.ROOT / 'reports').resolve()):
        raise ValueError('Use the explicitly authored local report directory.')
    result = {'candidates': [], 'referencesReady': [], 'correctionsStaged': [], 'held': []}
    with f.locked():
        manifest, records = f.read_json(f.MANIFEST), f.ledger()
        if manifest['activeRoundId'] != args.round:
            raise ValueError('Only the active round may advance.')
        path = f.MEDIA / f'{args.round}-jobs.json'
        plan = f.read_json(path)
        active = {item['shot'] for item in manifest.get('activeGenerationGroup', {}).get('members', [])}
        assets = [a for a in manifest['assets'] if a.get('roundId') == args.round]
        video_winners = {a['exerciseId'] for a in assets if a.get('kind') in {'video', 'animation'}
                         and (a.get('reviewStatus') == 'accepted'
                              or a.get('editorialReview', {}).get('status') == 'candidate')}
        video_holds = {j['exerciseId'] for j in plan['jobs'] if j['kind'] == 'video'
                       and j.get('productionDisposition') == 'quality-hold'}
        for asset in assets:
            review = asset.get('editorialReview', {})
            if review.get('reviewerType') != 'ai':
                continue
            if review.get('status') == 'needs-correction' and asset.get('reviewStatus') == 'pending':
                asset.update(reviewStatus='rejected', rejectionSource='ai-editorial', rejectedAt=f.now())
            elif review.get('status') == 'candidate':
                asset['title'] = asset.get('title', '').replace('AI review pending', 'AI screened')
        for job in plan['jobs']:
            if job['kind'] not in {'image', 'video'} or job['shot'] in active:
                continue
            exercise = manifest['exercises'].get(job['exerciseId'])
            if not exercise or exercise.get('reviewStatus') == 'accepted':
                continue
            preserve_video_status = job['kind'] == 'image' and job['exerciseId'] in (video_winners | video_holds)
            if job['kind'] == 'image':
                image_prior = [a for a in records['attempts'] if a['shot'] == job['shot']]
                if (not image_prior or image_prior[-1]['status'] != 'completed'
                        or image_prior[-1].get('actualCredits') is None):
                    continue
                # An explicitly changed source/camera brief may refine a valid
                # still after motion failed. Keep that one armed refinement.
                if (job.get('correctAfterAttemptId') == image_prior[-1]['id']
                        and job.get('promptSha256') != image_prior[-1].get('promptSha256')
                        and job.get('productionDisposition') == 'prompt-reviewed'):
                    continue
                references = [a for a in assets if a.get('attemptId') == image_prior[-1]['id']
                              and a.get('editorialReview', {}).get('reviewerType') == 'ai'
                              and a.get('editorialReview', {}).get('status') == 'ready-to-animate']
                if references:
                    job['productionDisposition'] = 'reference-reviewed'
                    if not preserve_video_status:
                        exercise.update(productionStatus='awaiting-motion-production',
                                        productionNote='Exact starting frame passed AI review; animation and independent video review are still required.')
                    result['referencesReady'].append(job['exerciseId'])
                    continue
            candidates = [a for a in assets if job['kind'] == 'video' and a.get('shot') == job['shot']
                          and a.get('editorialReview', {}).get('status') == 'candidate']
            if candidates:
                job['productionDisposition'] = 'candidate-delivered'
                exercise.update(productionStatus='ready-for-review',
                                productionNote='Exact-output AI-screened candidate delivered; human decision remains yours.')
                result['candidates'].append(job['exerciseId'])
                continue
            if job['kind'] == 'video' and job.get('productionDisposition') == 'quality-hold':
                exercise.update(productionStatus='quality-hold', productionNote=job.get('productionNote')
                                or 'Motion remains on an evidenced quality hold; a reviewed still does not supply a video candidate.')
                continue
            if job.get('productionDisposition') in {'awaiting-calibration', 'awaiting-new-reference'}:
                continue
            prior = [a for a in records['attempts'] if a['shot'] == job['shot']]
            if not prior or prior[-1]['status'] != 'completed' or prior[-1].get('actualCredits') is None:
                continue
            last = prior[-1]
            reviewed = [a for a in assets if a.get('attemptId') == last['id']
                        and a.get('editorialReview', {}).get('reviewerType') == 'ai'
                        and a.get('editorialReview', {}).get('status') == 'needs-correction']
            if not reviewed:
                continue
            if sum(f.counts_toward_shot_limit(a) for a in prior) >= f.shot_attempt_limit(manifest, args.round, job['shot']):
                job['productionDisposition'] = 'quality-hold'
                if job['exerciseId'] not in video_winners:
                    # A final failed source cannot leave a dependent video queued;
                    # a valid still cannot reopen an exhausted motion attempt.
                    video_holds.add(job['exerciseId'])
                    for dependent in plan['jobs']:
                        if dependent['kind'] == 'video' and dependent['exerciseId'] == job['exerciseId']:
                            dependent['productionDisposition'] = 'quality-hold'
                if not preserve_video_status:
                    exercise.update(productionStatus='quality-hold',
                                    productionNote='No candidate passed within the round shot-attempt limit; all evidence retained.')
                result['held'].append(job['exerciseId'])
                continue
            # An operator may already have selected a different model/reference
            # or a more specific correction. Do not overwrite that armed plan.
            if (job.get('correctAfterAttemptId') == last['id']
                    and job.get('promptSha256') != last.get('promptSha256')
                    and job.get('productionDisposition') in {'prompt-reviewed', 'ready-to-animate'}):
                continue
            correction = corrections / f"{job['shot']}-after-{last['id']}.txt"
            if not correction.is_file():
                job['productionDisposition'] = 'needs-correction'
                if not preserve_video_status:
                    exercise.update(productionStatus='needs-correction',
                                    productionNote=f"The new {job['kind']} failed AI form review; a specific correction is needed before regeneration.")
                continue
            prompt = correction.read_text()
            if not prompt.strip() or f.sha256(correction) == last.get('promptSha256'):
                raise ValueError('A correction must contain an explicitly changed prompt.')
            destination = f.repo_path(job['promptFile'])
            destination.write_text(prompt)
            version = f"9.correction-{len(prior) + 1}" if args.round == 'round-9' else f"{args.round}-correction-{len(prior) + 1}"
            job.update(promptSha256=f.sha256(destination), promptVersion=version,
                       correctAfterAttemptId=last['id'],
                       productionDisposition='ready-to-animate' if job['kind'] == 'video' and job.get('videoMode') == 'i2v' else 'prompt-reviewed',
                       correctionReviewOutput=reviewed[0]['editorialReview']['reviewedOutput'])
            spec = next((s for s in manifest['prompts'] if s.get('shot') == job['shot']), None)
            if spec is None:
                spec = {'exerciseId': job['exerciseId'], 'shot': job['shot'],
                        'roundId': args.round, 'styleId': job.get('styleId'),
                        'styleLabel': job.get('styleLabel'), 'path': job['promptFile']}
                manifest['prompts'].append(spec)
            spec.update(promptVersion=version, version=version)
            if not preserve_video_status:
                exercise.update(productionStatus='correction-queued',
                                productionNote='A specific correction was authored after exact-output AI review.')
            result['correctionsStaged'].append(job['exerciseId'])
        f.write_json(path, plan)
        f.write_json(f.MANIFEST, manifest)
    import json
    print(json.dumps(result))


if __name__ == '__main__':
    main()
