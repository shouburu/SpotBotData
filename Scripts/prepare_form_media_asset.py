#!/usr/bin/env python3
"""Encode and register an existing settled generation; never submits a job."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import form_media as media


def run(command):
    subprocess.run(command, cwd=media.ROOT, check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--alt', required=True)
    args = parser.parse_args()
    with media.locked():
        manifest = media.read_json(media.MANIFEST)
        attempt = dict(media.require_attempt(media.ledger(), args.attempt))
        existing = next((a for a in manifest['assets'] if a.get('attemptId') == args.attempt), None)
    if existing:
        url = existing.get('url', '')
        if not url.startswith('/assets/'):
            raise ValueError('Registered delivery has an unexpected location.')
        delivery = media.contained(media.MEDIA / 'assets', url.removeprefix('/assets/'))
        if not delivery.is_file() or media.sha256(delivery) != existing.get('sha256'):
            raise ValueError('Registered delivery is missing or differs from its recorded hash.')
        if existing.get('posterUrl'):
            poster_path = media.contained(media.MEDIA / 'assets', existing['posterUrl'].removeprefix('/assets/'))
            if not poster_path.is_file():
                raise ValueError('Registered video poster is missing.')
            if existing.get('posterSha256') and media.sha256(poster_path) != existing['posterSha256']:
                raise ValueError('Registered poster differs from its recorded hash.')
        print(json.dumps({'alreadyRegistered': existing['id']}))
        return
    if attempt['status'] != 'completed' or attempt.get('actualCredits') is None:
        raise ValueError('Only a settled completed attempt may be delivered.')
    master = media.repo_path(attempt['outputPath'])
    master_records = [item for item in attempt.get('localFiles', [])
                      if item.get('role') == 'master' and item.get('path') == attempt['outputPath']]
    if len(master_records) != 1 or media.sha256(master) != master_records[0].get('sha256'):
        raise ValueError('The master is missing its frozen provenance or has changed since download.')
    kind = media.pilot_media_kind(attempt['model'])
    asset_id = attempt['shot'] + '-' + args.attempt.removeprefix('attempt_')[:8]
    folder = media.MEDIA / 'assets/delivery' / attempt.get('roundId', 'round-2')
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / (asset_id + ('.mp4' if kind == 'video' else '.webp'))
    poster = None
    if kind == 'image':
        run(['cwebp', '-quiet', '-q', '86', str(master), '-o', str(output)])
        if output.stat().st_size > 500_000:
            raise ValueError('Still exceeds the 500 KB delivery maximum; revise encoding before registration.')
    else:
        # Keep the provider master intact. Only the delivered copy is scaled,
        # and only downward when its measured short side exceeds 720 pixels.
        width, height = master_records[0]['width'], master_records[0]['height']
        scaling = []
        if min(width, height) > 720:
            scaling = ['-vf', 'scale=720:-2' if width <= height else 'scale=-2:720']
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(master),
             '-map', '0:v:0', '-an', *scaling, '-c:v', 'libx264', '-preset', 'slow', '-crf', '22',
             '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)])
        raw_poster = folder / (asset_id + '-poster.png')
        poster = folder / (asset_id + '-poster.webp')
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(output),
             '-frames:v', '1', str(raw_poster)])
        run(['cwebp', '-quiet', '-q', '84', str(raw_poster), '-o', str(poster)])
        raw_poster.unlink()
        if output.stat().st_size + poster.stat().st_size > media.DELIVERY_LIMIT_BYTES:
            raise ValueError('Video and poster exceed the per-exercise package ceiling.')
        frames = media.ROOT / 'reports/form-media' / args.attempt / 'keyframes.jpg'
        frames.parent.mkdir(parents=True, exist_ok=True)
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(output),
             '-vf', 'fps=1,scale=360:-1,tile=4x3:padding=5:margin=5:color=white',
             '-frames:v', '1', str(frames)])
        # Dense ordered samples expose short extra pulses and incomplete returns.
        # These are editorial inspection artifacts, not an automated form verdict.
        dense = frames.parent / 'review-3fps-%02d.jpg'
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(output),
             '-vf', 'fps=3,scale=300:-1,tile=4x3:nb_frames=12:padding=4:margin=4:color=white',
             str(dense)])
    if media.sha256(master) != master_records[0]['sha256']:
        raise ValueError('The master changed during encoding; do not attribute this derivative.')
    command = [sys.executable, str(media.ROOT / 'Scripts/form_media.py'), 'register',
               '--exercise', attempt['exerciseId'], '--attempt', args.attempt, '--id', asset_id,
               '--kind', kind, '--file', media.relative(output), '--title', args.title, '--alt', args.alt]
    if poster:
        command.extend(['--poster', media.relative(poster)])
    result = subprocess.run(command, cwd=media.ROOT, check=True, capture_output=True, text=True)
    asset = json.loads(result.stdout)
    print(json.dumps({'assetId': asset['id'], 'path': media.relative(output), 'bytes': asset['bytes'],
                      'width': asset['width'], 'height': asset['height'], 'durationSeconds': asset['durationSeconds'],
                      'keyframes': media.relative(frames) if kind == 'video' else None}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'Delivery stopped: {error}')
