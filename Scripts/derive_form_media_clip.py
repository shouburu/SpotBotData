#!/usr/bin/env python3
"""Trim a frozen, settled video master without generating or replacing media."""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile

import form_media as media


EDITS = media.MEDIA / 'edits.json'
SAFE_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}')


def run(command):
    result = subprocess.run(command, cwd=media.ROOT, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f'{command[0]} failed: {result.stderr.strip()[-2000:]}')


def source_snapshot(attempt_id, manifest):
    attempt = copy.deepcopy(media.require_attempt(media.ledger(), attempt_id))
    if attempt.get('status') != 'completed' or attempt.get('actualCredits') is None:
        raise ValueError('Source must be a settled, completed attempt.')
    originals = [asset for asset in manifest.get('assets', [])
                 if asset.get('attemptId') == attempt_id and asset.get('kind') == 'video'
                 and not asset.get('edit')]
    if len(originals) != 1:
        raise ValueError('Source attempt must have exactly one registered original video asset.')
    asset = copy.deepcopy(originals[0])
    if asset.get('exerciseId') != attempt.get('exerciseId'):
        raise ValueError('Source asset and attempt exercise IDs differ.')
    media.require_exercise(manifest, attempt['exerciseId'])
    master = media.repo_path(attempt['outputPath'])
    if not master.is_relative_to((media.MEDIA / 'assets/masters').resolve()):
        raise ValueError('Source must be a frozen master inside form-media/assets/masters/.')
    masters = [item for item in attempt.get('localFiles', [])
               if item.get('role') == 'master' and item.get('path') == attempt['outputPath']]
    if len(masters) != 1 or media.sha256(master) != masters[0].get('sha256'):
        raise ValueError('Source master lacks frozen provenance or its SHA-256 has changed.')
    prompt = attempt.get('prompt')
    if not isinstance(prompt, str) or hashlib.sha256(prompt.encode()).hexdigest() != attempt.get('promptSha256'):
        raise ValueError('Source attempt lacks valid frozen prompt text and SHA-256.')
    frozen = {key: copy.deepcopy(attempt[key]) for key in (
        'id', 'exerciseId', 'outputPath', 'shot', 'roundId', 'styleId', 'styleLabel',
        'styleVersion', 'promptVersion', 'promptFile', 'prompt', 'promptSha256', 'references'
    ) if key in attempt}
    frozen.update(sourceAssetId=asset['id'], sourceAssetSha256=asset.get('sha256'),
                  sourceSha256=masters[0]['sha256'])
    return attempt, asset, master, frozen


def require_unused(manifest, edits, asset_id, output, poster, report):
    if any(item.get('id') == asset_id for item in manifest.get('assets', [])):
        raise ValueError('Asset ID already exists; choose a new explicit ID.')
    if any(item.get('id') == asset_id for item in edits.get('edits', [])):
        raise ValueError('Edit ID already exists; choose a new explicit ID.')
    url = '/assets/' + output.relative_to(media.MEDIA / 'assets').as_posix()
    if any(item.get('url') == url for item in manifest.get('assets', [])):
        raise ValueError('Delivery URL is already registered.')
    if any(os.path.lexists(path) for path in (output, poster, report)):
        raise ValueError('A destination file or report directory already exists; nothing will be overwritten.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', required=True, help='Explicit settled original video attempt ID')
    parser.add_argument('--id', required=True, help='New unique authored asset/edit ID')
    parser.add_argument('--start', required=True, type=float, help='Source trim start, in seconds')
    parser.add_argument('--end', required=True, type=float, help='Source trim end, in seconds')
    parser.add_argument('--hold', required=True, type=float, help='Cloned still hold at each endpoint, in seconds')
    parser.add_argument('--title', required=True)
    parser.add_argument('--alt', help='Accessible description; defaults to a factual edit description')
    parser.add_argument('--round-id', help='Attribute this new edit to the active production round; source attribution is retained')
    parser.add_argument('--crop', nargs=4, type=int, metavar=('X', 'Y', 'WIDTH', 'HEIGHT'),
                        help='Optional fixed, even-pixel crop of the source; inspect the full movement envelope first')
    args = parser.parse_args()
    if not SAFE_ID.fullmatch(args.id):
        raise ValueError('ID must contain only letters, digits, underscores or hyphens and start with a letter or digit.')
    if not args.title.strip():
        raise ValueError('Title must not be empty.')
    if (not all(math.isfinite(value) for value in (args.start, args.end, args.hold))
            or not 0 <= args.start < args.end or args.hold < 0):
        raise ValueError('Require finite bounds: 0 <= start < end and hold >= 0.')

    with media.locked():
        manifest = media.read_json(media.MANIFEST)
        attempt, source_asset, master, frozen = source_snapshot(args.attempt, manifest)
        source_round_id = attempt.get('roundId') or source_asset.get('roundId')
        if not isinstance(source_round_id, str) or not SAFE_ID.fullmatch(source_round_id):
            raise ValueError('Source lacks a valid frozen round ID.')
        round_id = args.round_id or source_round_id
        if not SAFE_ID.fullmatch(round_id):
            raise ValueError('Target round ID is invalid.')
        if args.round_id and manifest.get('activeRoundId') != round_id:
            raise ValueError('An explicitly selected target must be the active production round.')
        folder = media.contained(media.MEDIA / 'assets/delivery', round_id)
        output = folder / (args.id + '.mp4')
        poster = folder / (args.id + '-poster.webp')
        report = media.contained(media.ROOT / 'reports/form-media', args.id)
        require_unused(manifest, media.read_json(EDITS, {'schemaVersion': 1, 'edits': []}),
                       args.id, output, poster, report)

    measured_source = media.media_metadata(master, 'video')
    if args.end > measured_source['durationSeconds']:
        raise ValueError('Trim end exceeds the measured source duration.')
    if measured_source['sha256'] != frozen['sourceSha256']:
        raise ValueError('Source master changed before encoding.')
    trim_filter = f'trim=start={args.start}:end={args.end},setpts=PTS-STARTPTS'
    expected_size = (measured_source['width'], measured_source['height'])
    if args.crop:
        x, y, width, height = args.crop
        if (min(x, y) < 0 or min(width, height) <= 0 or any(v % 2 for v in args.crop)
                or x + width > expected_size[0] or y + height > expected_size[1]):
            raise ValueError('Crop must use even integers and remain within the source frame.')
        trim_filter += f',crop={width}:{height}:{x}:{y}'
        expected_size = (width, height)
    if args.hold:
        trim_filter += (f',tpad=start_mode=clone:start_duration={args.hold}'
                        f':stop_mode=clone:stop_duration={args.hold}')

    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.' + args.id + '-', dir=folder) as temp:
        staging = Path(temp)
        staged_video = staging / output.name
        staged_poster = staging / poster.name
        raw_poster = staging / 'poster.png'
        staged_frames = staging / 'keyframes.jpg'
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(master),
             '-map', '0:v:0', '-an', '-vf', trim_filter, '-fps_mode', 'passthrough',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p',
             '-movflags', '+faststart', str(staged_video)])
        measured = media.media_metadata(staged_video, 'video')
        if measured['codec'] != 'h264' or (measured['width'], measured['height']) != expected_size:
            raise ValueError('Encoded video must match the requested frame dimensions and use H.264.')
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(staged_video),
             '-frames:v', '1', str(raw_poster)])
        run(['cwebp', '-quiet', '-q', '84', str(raw_poster), '-o', str(staged_poster)])
        poster_bytes = staged_poster.stat().st_size
        poster_sha = media.sha256(staged_poster)
        if measured['bytes'] + poster_bytes > media.DELIVERY_LIMIT_BYTES:
            raise ValueError('Video and poster exceed the per-exercise package ceiling.')
        rows = max(1, math.ceil(measured['durationSeconds'] * 2 / 4))
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(staged_video),
             '-vf', f'fps=2,scale=360:-1,tile=4x{rows}:padding=5:margin=5:color=white',
             '-frames:v', '1', '-pix_fmt', 'yuvj420p', str(staged_frames)])
        if media.sha256(master) != frozen['sourceSha256']:
            raise ValueError('Source master changed during encoding; derivative will not be registered.')

        with media.locked():
            manifest = media.read_json(media.MANIFEST)
            if args.round_id and manifest.get('activeRoundId') != round_id:
                raise ValueError('The target production round changed during encoding.')
            current_attempt, current_asset, _, current_frozen = source_snapshot(args.attempt, manifest)
            if current_frozen != frozen:
                raise ValueError('Frozen source attribution changed during encoding.')
            edits = media.read_json(EDITS, {'schemaVersion': 1, 'edits': []})
            require_unused(manifest, edits, args.id, output, poster, report)
            created = media.now()
            measured['path'] = media.relative(output)
            edit = dict(id=args.id, roundId=round_id, sourceRoundId=source_round_id,
                        sourceAssetId=source_asset['id'],
                        sourceAttemptId=args.attempt, sourcePath=media.relative(master),
                        sourceSha256=frozen['sourceSha256'], trimStartSeconds=args.start,
                        trimEndSeconds=args.end, leadHoldSeconds=args.hold, tailHoldSeconds=args.hold,
                        playbackRate=1, filter=trim_filter, generationCredits=0, createdAt=created,
                        **measured)
            if args.crop:
                edit['crop'] = dict(zip(('x', 'y', 'width', 'height'), args.crop))
            asset = {key: copy.deepcopy(current_attempt.get(key, current_asset.get(key)))
                     for key in ('shot', 'roundId', 'styleId', 'styleLabel', 'styleVersion', 'promptVersion')
                     if current_attempt.get(key, current_asset.get(key)) is not None}
            hold_description = ' with brief still endpoint holds' if args.hold else ''
            asset.update(id=args.id, exerciseId=attempt['exerciseId'], kind='video',
                         roundId=round_id, sourceRoundId=source_round_id,
                         url='/assets/' + output.relative_to(media.MEDIA / 'assets').as_posix(),
                         title=args.title, alt=args.alt if args.alt is not None else
                         f'A trimmed movement excerpt at original speed{hold_description}; the full source video is retained.',
                         bytes=measured['bytes'], width=measured['width'], height=measured['height'],
                         durationSeconds=measured['durationSeconds'], sha256=measured['sha256'],
                         source='Authored edit of Google Flow render', license=source_asset.get('license'),
                         reviewStatus='pending', createdAt=created,
                         posterUrl='/assets/' + poster.relative_to(media.MEDIA / 'assets').as_posix(),
                         posterSha256=poster_sha, posterBytes=poster_bytes,
                         edit=edit, sourceAttemptId=args.attempt, sourceAssetId=source_asset['id'],
                         promptText=attempt['prompt'], promptFile=attempt.get('promptFile'),
                         promptSha256=attempt['promptSha256'],
                         referenceIds=[ref['path'] for ref in attempt.get('references', [])],
                         references=copy.deepcopy(attempt.get('references', [])))
            # Publish only complete files. Hard links refuse an existing destination,
            # including a concurrent non-cooperating writer; no original is replaced.
            report.mkdir(parents=True, exist_ok=False)
            os.link(staged_video, output)
            os.link(staged_poster, poster)
            os.link(staged_frames, report / 'keyframes.jpg')
            edits.setdefault('edits', []).append(edit)
            manifest.setdefault('assets', []).append(asset)
            # Both atomic JSON writes happen under the shared lock. Each asset also
            # embeds its complete provenance; the generation ledger is untouched.
            media.write_json(EDITS, edits)
            media.write_json(media.MANIFEST, manifest)
        print(json.dumps({'assetId': args.id, **measured, 'posterBytes': poster_bytes,
                          'poster': media.relative(poster), 'keyframes': media.relative(report / 'keyframes.jpg'),
                          'sourceAttemptId': args.attempt, 'sourceAssetId': source_asset['id'],
                          'generationCredits': 0}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(f'Clip derivation stopped: {error}')
