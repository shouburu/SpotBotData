#!/usr/bin/env python3
"""Generate one explicitly selected pilot shot with live pricing and a durable reservation."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import form_media

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'Scripts'


def command_json(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'{Path(command[0]).name} failed; no further generation will be submitted.')
    return json.loads(result.stdout)


def ledger(*args):
    return command_json([sys.executable, str(SCRIPTS / 'form_media.py'), *map(str, args)])


def ui_quote(path, args, project_id, model_key):
    path = (ROOT / path).resolve()
    if not path.is_relative_to((ROOT / 'form-media/ui-quotes').resolve()) or not path.is_file():
        raise ValueError('UI quote evidence must be an existing file inside form-media/ui-quotes/.')
    raw = path.read_bytes()
    quote = json.loads(raw)
    if not isinstance(quote, dict):
        raise ValueError('UI quote evidence must be a JSON object.')
    expected = {'sourceType': 'flow-ui-observation', 'projectId': project_id,
                'exerciseId': args.exercise, 'shot': args.shot, 'modelKey': model_key,
                'kind': args.kind, 'aspect': args.aspect}
    model = getattr(args, 'model', None) or ('nano-pro' if args.kind == 'image' else 'omni-flash')
    if model in {'veo-fast', 'veo-quality'}:
        expected.update(model=model, family=form_media.PILOT_MODEL_LABELS[model],
                        modelKeySource='flow-ui-settings-identity')
    if any(quote.get(field) != value for field, value in expected.items()):
        raise ValueError('UI quote evidence does not match this project, exercise, shot or generation settings.')
    if type(quote.get('count')) is not int or quote['count'] != 1:
        raise ValueError('UI quote evidence must cover exactly one output.')
    for field in ('balance', 'credits'):
        if type(quote.get(field)) is not int or quote[field] < 0:
            raise ValueError('UI quote balance and credits must be nonnegative integers.')
    for field in ('source', 'observer', 'visiblePriceText', 'visibleBalanceText', 'observedAt'):
        if not isinstance(quote.get(field), str) or not quote[field].strip():
            raise ValueError(f'UI quote evidence requires nonempty {field}.')
    observed = datetime.fromisoformat(quote['observedAt'].replace('Z', '+00:00'))
    if observed.tzinfo is None or not -5 <= (datetime.now(timezone.utc) - observed).total_seconds() <= 300:
        raise ValueError('UI price and balance observation must be from the last five minutes.')
    if args.kind == 'video':
        video_mode = getattr(args, 'video_mode', 't2v' if model_key.startswith('abra_t2v_') else 'i2v')
        if quote.get('videoMode') != video_mode:
            raise ValueError('Video requires a live quote explicitly observed in the requested mode.')
        if type(quote.get('durationSeconds')) is not int or quote['durationSeconds'] != args.duration:
            raise ValueError('UI video quote must cover the exact requested duration.')
        if model in {'veo-fast', 'veo-quality'}:
            form_media.require_veo_default_resolution(quote, model, args.duration, args.aspect, video_mode)
        else:
            if quote.get('resolutions') not in (['720p'], ['VIDEO_RESOLUTION_720P']):
                raise ValueError('Omni video quote must explicitly select only 720p resolution.')
            quote['resolutions'] = ['VIDEO_RESOLUTION_720P']
    elif quote.get('durationSeconds') is not None:
        raise ValueError('UI image quote cannot specify a video duration.')
    # Match unambiguous displayed numbers, including comma-grouped balances.
    # Keep the original text for operator review when a label is more complex.
    number = r'(?<![\w.,])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?![\w.,])'
    for field, text_field in (('credits', 'visiblePriceText'), ('balance', 'visibleBalanceText')):
        label = quote[text_field]
        credit_numbers = re.findall(f'({number})\\s*(?:AI\\s+)?credits?\\b', label, re.IGNORECASE)
        numbers = credit_numbers if len(credit_numbers) == 1 else re.findall(number, label)
        if len(numbers) == 1 and int(numbers[0].replace(',', '')) != quote[field]:
            raise ValueError(f'UI {text_field} does not match its recorded {field}.')
    quote['snapshotSha256'] = hashlib.sha256(raw).hexdigest()
    return path, raw, quote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exercise', required=True)
    parser.add_argument('--shot', required=True, help='Prompt filename without .txt, and the durable shot identity.')
    parser.add_argument('--kind', choices=['image', 'video'], required=True)
    parser.add_argument('--model', choices=list(form_media.PILOT_MODEL_LABELS),
                        help='Explicit model; defaults to nano-pro for images and omni-flash for videos. Veo requires a live UI quote.')
    parser.add_argument('--aspect', choices=['16:9', '9:16', '4:3', '1:1'], required=True)
    parser.add_argument('--duration', type=int, choices=[6, 8, 10])
    parser.add_argument('--reference', action='append', default=[])
    parser.add_argument('--end-reference', help='Optional video end frame; requires its own first/last model quote.')
    parser.add_argument('--video-mode', choices=['i2v', 't2v'], default='i2v')
    parser.add_argument('--ui-quote-file', help='Fresh Flow UI settings and account-panel evidence in form-media/ui-quotes/. Holds settlement for a separately observed post-generation balance.')
    parser.add_argument('--generation-group', help='Explicit isolated-worker group; settlement remains aggregate and manual.')
    parser.add_argument('--profile', help='Isolated gflow worker profile, only valid with a planned generation group.')
    args = parser.parse_args()
    args.model = args.model or ('nano-pro' if args.kind == 'image' else 'omni-flash')
    attempt_id = None
    try:
        if form_media.pilot_media_kind(args.model) != args.kind:
            raise ValueError('The selected model does not match the requested media kind.')
        if args.model in {'veo-fast', 'veo-quality'} and not args.ui_quote_file:
            raise ValueError('Veo comparison requires fresh model-specific UI price evidence; API or historical prices are not used.')
        frame_mode = 'text-only' if args.video_mode == 't2v' else ('start-and-end' if args.end_reference else 'start-only')
        model = args.model
        key = form_media.pilot_model_key(model, args.duration, frame_mode, args.aspect)
        if bool(args.generation_group) != bool(args.profile) or (args.generation_group and not args.ui_quote_file):
            raise ValueError('An isolated worker requires a planned group, explicit profile and live UI quote.')
        if not args.shot.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Shot identity must contain only letters, numbers, underscores, and hyphens.')
        prompt_file = ROOT / 'form-media/prompts' / (args.shot + '.txt')
        prompt = prompt_file.read_text()
        manifest = json.loads((ROOT / 'form-media/manifest.json').read_text())
        if not manifest.get('projectId'):
            raise ValueError('Create and record the pilot Flow project first.')
        # Cheap preflight before opening Flow. reserve repeats these checks under
        # the same cross-process lock immediately before committing the quote.
        with form_media.locked():
            manifest = form_media.read_json(form_media.MANIFEST)
            exercise = form_media.require_exercise(manifest, args.exercise)
            if not exercise.get('pilot'):
                raise ValueError('Only explicitly selected pilot exercises can use this runner.')
            records = form_media.ledger()
            if args.end_reference and manifest.get('generationCapabilities', {}).get('endFrameSupported') is False:
                raise ValueError('End frames are unsupported by this account frontend and reviewed gflow version. Recheck capability before enabling them; no price reservation or generation submitted.')
            if form_media.accepted_shot(manifest, records, args.exercise, args.shot):
                raise ValueError('Accepted selected media already exists for this shot; review it before regeneration.')
            attempts = records['attempts']
            attempt_limit = form_media.shot_attempt_limit(manifest, shot=args.shot)
            if sum(form_media.counts_toward_shot_limit(a) for a in attempts
                   if a['exerciseId'] == args.exercise and a['shot'] == args.shot) >= attempt_limit:
                raise ValueError(f'This shot has reached its {attempt_limit}-attempt limit.')
            form_media.submission_window(manifest, records, args.generation_group,
                                         args.profile, args.exercise, args.shot)
        if not shutil.which('ffprobe'):
            raise ValueError('ffprobe is required to record downloaded media before any generation is submitted.')
        if args.kind == 'video' and (len(args.reference) != (0 if args.video_mode == 't2v' else 1) or not args.duration or args.aspect not in ['16:9', '9:16']):
            raise ValueError('Video requires references matching its explicit mode, duration, and supported aspect.')
        if args.video_mode == 't2v' and (args.kind != 'video' or args.end_reference):
            raise ValueError('Text-to-video cannot use image or end-frame mode.')
        if args.kind == 'image' and args.duration is not None:
            raise ValueError('Image generation does not accept a duration.')
        if args.end_reference and args.kind != 'video':
            raise ValueError('Only video accepts an end reference.')
        references = []
        for ref in [*args.reference, *([args.end_reference] if args.end_reference else [])]:
            path = (ROOT / ref).resolve()
            if not path.is_relative_to((ROOT / 'form-media/assets').resolve()) or not path.is_file():
                raise ValueError('References must be existing files inside form-media/assets/.')
            references.append(path)
        # Detect replaced/unknown gflow source before using the reviewed macOS session path.
        patch = command_json([sys.executable, str(SCRIPTS / 'patch_gflow_macos.py'), 'status'])
        if patch.get('patched') is not True:
            raise ValueError('The reviewed macOS cookie patch is not active; run patch_gflow_macos.py apply first.')
        prompt_patch = command_json([sys.executable, str(SCRIPTS / 'patch_gflow_prompt.py'), 'status'])
        if prompt_patch.get('patched') is not True:
            raise ValueError('The reviewed prompt replacement/readback guard is not active; run patch_gflow_prompt.py apply first.')
        print(f'Verifying current Flow price for {key}…',
              file=sys.stderr if args.ui_quote_file else sys.stdout, flush=True)
        if args.ui_quote_file:
            quote_file, quote_bytes, quote = ui_quote(args.ui_quote_file, args, manifest['projectId'], key)
        else:
            quote = command_json([sys.executable, str(SCRIPTS / 'flow_pricing.py'), '--model-key', key])
            quote_file = ROOT / 'form-media/pricing.json'
            quote_bytes = quote_file.read_bytes()
            snapshot = json.loads(quote_bytes)
            matching_offers = [item for item in snapshot.get('offers', []) if item.get('modelKey') == key]
            if snapshot.get('observedAt') != quote.get('observedAt') or snapshot.get('balance') != quote.get('balance') or snapshot.get('projectId') != manifest['projectId'] or len(matching_offers) != 1 or matching_offers[0].get('credits') != quote.get('credits'):
                raise ValueError('Live pricing snapshot changed before reservation; no generation submitted.')
            if args.end_reference and any(quote.get(field) != value for field, value in matching_offers[0].items()):
                raise ValueError('First/last quote settings differ from the retained live pricing snapshot.')
            quote['snapshotSha256'] = hashlib.sha256(quote_bytes).hexdigest()
        evidence = f"{quote['source']}; {key}; {quote['observedAt']}; snapshot sha256:{quote['snapshotSha256']}"
        reserve_args = ['reserve', '--exercise', args.exercise, '--shot', args.shot,
                        '--model', model, '--quote', quote['credits'], '--quote-source', evidence,
                        '--prompt-file', prompt_file.relative_to(ROOT), '--balance-before', quote['balance'],
                        '--quote-json', json.dumps(quote), '--aspect', args.aspect]
        if args.generation_group:
            reserve_args.extend(['--generation-group', args.generation_group, '--profile', args.profile])
        if args.duration:
            reserve_args.extend(['--duration', args.duration])
        if args.kind == 'video':
            reserve_args.extend(['--video-mode', args.video_mode])
        for ref in references[:len(args.reference)]:
            reserve_args.extend(['--reference', ref.relative_to(ROOT)])
        if args.end_reference:
            reserve_args.extend(['--end-reference', references[-1].relative_to(ROOT)])
        reservation = ledger(*reserve_args)
        attempt_id = reservation['id']
        # The ledger's frozen text is what must actually be sent, even if an
        # editor changed the prompt file while the live-price read was running.
        prompt = reservation['attempt']['prompt']
        folder = ROOT / 'form-media/assets/masters' / args.shot
        folder.mkdir(parents=True, exist_ok=True)
        output = folder / (attempt_id + ('.png' if args.kind == 'image' else '.mp4'))
        reports = ROOT / 'reports/form-media' / attempt_id
        reports.mkdir(parents=True, exist_ok=True)
        (reports / 'quote.json').write_text(json.dumps(quote, indent=2) + '\n')
        (reports / 'pricing-snapshot.json').write_bytes(quote_bytes)
        if args.ui_quote_file:
            frozen_ui_quote = reports / 'ui-quote-observation.json'
            frozen_ui_quote.write_bytes(quote_bytes)
            with form_media.locked():
                records = form_media.ledger()
                recorded = form_media.require_attempt(records, attempt_id)
                recorded['uiQuoteEvidence'] = {
                    'path': str(quote_file.relative_to(ROOT)), 'sha256': quote['snapshotSha256'],
                    'frozenPath': str(frozen_ui_quote.relative_to(ROOT)),
                    'observation': json.loads(quote_bytes),
                }
                form_media.write_json(form_media.LEDGER, records)
                if recorded['projectId'] != quote['projectId']:
                    raise ValueError('UI quote project changed after reservation; do not submit it.')
        # Flow's frame picker identifies uploads by filename. A unique name per
        # submission avoids selecting an older upload with the same basename.
        # Keep the original reference hashes and record these exact upload copies.
        upload_references = []
        upload_dir = ROOT / 'form-media/assets/references' / attempt_id
        for index, reference in enumerate(reservation['attempt']['references']):
            original = ROOT / reference['path']
            if form_media.sha256(original) != reference['sha256']:
                raise ValueError('A reference changed after reservation; do not submit it.')
            upload_dir.mkdir(parents=True, exist_ok=True)
            upload = upload_dir / f'{attempt_id}-ref-{index + 1}{original.suffix}'
            shutil.copyfile(original, upload)
            if form_media.sha256(upload) != reference['sha256']:
                raise ValueError('Upload copy differs from the recorded reference.')
            upload_references.append(upload)
        with form_media.locked():
            records = form_media.ledger()
            recorded = form_media.require_attempt(records, attempt_id)
            recorded['uploadReferences'] = [
                {'path': str(path.relative_to(ROOT)), 'sha256': form_media.sha256(path),
                 **({'role': reference['role']} if reference.get('role') else {})}
                for path, reference in zip(upload_references, reservation['attempt']['references'])
            ]
            form_media.write_json(form_media.LEDGER, records)
        if args.kind == 'image':
            command = ['gflow', 'image', 'i2i' if references else 't2i', prompt]
            for ref in upload_references:
                command.extend(['--ref', str(ref)])
        else:
            command = ['gflow', 'video', args.video_mode]
            if args.video_mode == 'i2v':
                command.append(str(upload_references[0]))
            command.extend([prompt, '--duration', str(args.duration)])
            if args.end_reference:
                command.extend(['--end-frame', str(upload_references[1])])
        command.extend(['--model', model, '--aspect', args.aspect, '--count', '1',
                        '--project', manifest['projectId'], '--output', str(output), '--json'])
        if args.profile:
            command.extend(['--profile', args.profile])
        for reference in reservation['attempt']['references']:
            if form_media.sha256(ROOT / reference['path']) != reference['sha256']:
                raise ValueError('A reference image changed after reservation; do not submit the stale request.')
        for upload, reference in zip(upload_references, reservation['attempt']['references']):
            if form_media.sha256(upload) != reference['sha256']:
                raise ValueError('An upload copy changed before submission; reconcile the reservation.')
        if args.ui_quote_file:
            _, current_bytes, _ = ui_quote(quote_file, args, manifest['projectId'], key)
            if current_bytes != quote_bytes or frozen_ui_quote.read_bytes() != quote_bytes:
                raise ValueError('UI quote evidence changed before submission; reconcile the reservation.')
        ledger('update', '--attempt', attempt_id, '--status', 'submitted', '--notes',
               f'One output requested; quoted model/settings {key}; aspect {args.aspect}; output {output.relative_to(ROOT)}; diagnostics {reports.relative_to(ROOT)}')
        print(f"Submitting {args.shot}: {quote['credits']} credits reserved; attempt {attempt_id}",
              file=sys.stderr if args.ui_quote_file else sys.stdout, flush=True)
        with (reports / 'stdout.json').open('w') as stdout, (reports / 'stderr.log').open('w') as stderr:
            result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        # Capture returned IDs even when the generator reports a paid failure.
        # Raw stdout stays in ignored diagnostics because it can contain signed URLs.
        try:
            response = json.loads((reports / 'stdout.json').read_text())
        except (ValueError, OSError):
            response = None
        if isinstance(response, dict):
            images = response.get('images')
            first_image = images[0] if isinstance(images, list) and images and isinstance(images[0], dict) else {}
            media_id = response.get('media_id') or first_image.get('media_name')
            job_id = response.get('flow_operation_id') or first_image.get('workflow_id')
            identity_args = ['update', '--attempt', attempt_id]
            if isinstance(media_id, str) and media_id:
                identity_args.extend(['--media-id', media_id])
            if isinstance(job_id, str) and job_id:
                identity_args.extend(['--job-id', job_id])
            if len(identity_args) > 3:
                ledger(*identity_args)
            # gflow can normalize a requested .png to the actual .jpg/.webp
            # format. Accept only the same reserved directory and basename.
            actual_path = first_image.get('local_path') if args.kind == 'image' else response.get('local_path')
            if isinstance(actual_path, str):
                candidate = Path(actual_path).resolve()
                extensions = {'.png', '.jpg', '.jpeg', '.webp'} if args.kind == 'image' else {'.mp4'}
                if candidate.parent != output.parent.resolve() or candidate.stem != output.stem or candidate.suffix.lower() not in extensions:
                    raise ValueError('Returned output path is outside this attempt\'s reserved file family; reconcile attribution.')
                output = candidate
        if result.returncode or not output.is_file():
            ledger('update', '--attempt', attempt_id, '--status', 'uncertain', '--notes',
                   f'gflow exited {result.returncode}; reconcile project and balance before retrying. Diagnostics {reports.relative_to(ROOT)}')
            print(json.dumps({'attemptId': attempt_id, 'status': 'uncertain', 'exitCode': result.returncode, 'diagnostics': str(reports)}))
            return 1
        if not isinstance(response, dict) or response.get('status') != 'ok':
            raise ValueError('The downloaded output has no recognized success response; reconcile its attribution.')
        if args.kind == 'image':
            images = response.get('images')
            if type(response.get('count')) is not int or response['count'] != 1 or not isinstance(images, list) or len(images) != 1:
                raise ValueError('Flow did not confirm exactly one generated image; reconcile the reservation.')
            output_item = images[0]
            if not isinstance(output_item, dict) or output_item.get('model_name_type') != key:
                raise ValueError('The generated image model differs from the quoted model; reconcile the reservation.')
            returned_path = output_item.get('local_path')
        else:
            # gflow exposes requested count, not an independent actual-output
            # count for video. Do not claim that this proves provider billing.
            request = response.get('request')
            if not isinstance(request, dict) or request.get('count') != 1 or request.get('model') != form_media.PILOT_VIDEO_MODELS[model]:
                raise ValueError('Video response request differs from the reserved single-output model.')
            if (args.end_reference or args.ui_quote_file) and (request.get('mode') != args.video_mode or request.get('duration') != args.duration
                    or request.get('aspect') != ('portrait' if args.aspect == '9:16' else 'landscape')):
                raise ValueError('Video response differs from the reserved mode, duration or aspect.')
            returned_path = response.get('local_path')
        if not isinstance(returned_path, str) or Path(returned_path).resolve() != output.resolve():
            raise ValueError('The returned output path differs from this attempt\'s file; reconcile attribution.')
        with output.open('rb') as stream:
            magic = stream.read(16)
        if args.kind == 'image':
            signatures = {
                '.png': magic.startswith(b'\x89PNG\r\n\x1a\n'),
                '.jpg': magic.startswith(b'\xff\xd8\xff'),
                '.jpeg': magic.startswith(b'\xff\xd8\xff'),
                '.webp': magic[:4] == b'RIFF' and magic[8:12] == b'WEBP',
            }
            if not signatures.get(output.suffix.lower(), False):
                raise ValueError('Downloaded image bytes do not match its PNG/JPEG/WebP filename.')
        elif magic[4:8] != b'ftyp':
            raise ValueError('Downloaded video is not MP4; a poster image cannot complete this attempt.')
        metadata = form_media.media_metadata(output, args.kind)
        if args.end_reference or (args.ui_quote_file and args.kind == 'video'):
            if abs(metadata['durationSeconds'] - args.duration) > 0.1:
                raise ValueError('Video output duration differs from the quoted settings.')
            if model in {'veo-fast', 'veo-quality'}:
                # Provider-default is an unknown pixel size, never an inferred 720p claim.
                # Allow at most two pixels of rounding in the requested aspect ratio.
                expected_ratio = 9 / 16 if args.aspect == '9:16' else 16 / 9
                if abs(metadata['width'] - metadata['height'] * expected_ratio) > 2:
                    raise ValueError('Veo provider-default output aspect differs from the quoted setting.')
                metadata['resolutionPolicy'] = 'provider-default'
            else:
                expected_size = (720, 1280) if args.aspect == '9:16' else (1280, 720)
                if (metadata['width'], metadata['height']) != expected_size:
                    raise ValueError('Video output dimensions differ from the quoted 720p setting.')
        metadata['role'] = 'master'
        with form_media.locked():
            records = form_media.ledger()
            recorded = form_media.require_attempt(records, attempt_id)
            recorded.setdefault('localFiles', []).append(metadata)
            recorded['outputPath'] = metadata['path']
            recorded['updatedAt'] = form_media.now()
            if args.ui_quote_file:
                recorded['notes'] = 'Output downloaded and metadata verified. Runner deferred settlement to a separately observed Flow UI post-generation balance through complete with settlement evidence.'
            form_media.write_json(form_media.LEDGER, records)
            if args.ui_quote_file:
                held_budget = form_media.budget(form_media.read_json(form_media.MANIFEST), records)
        if args.ui_quote_file:
            print(json.dumps({'attemptId': attempt_id, 'status': 'awaiting-credit-reconciliation',
                              'output': str(output), 'quotedCredits': quote['credits'],
                              'balanceBefore': quote['balance'], 'metadata': metadata,
                              'budget': held_budget, 'responseFile': str(reports / 'stdout.json'),
                              'uiQuoteEvidenceFile': str(frozen_ui_quote)}))
            return 0
        # Read the balance only after the completed output exists. Never assume a failed request was free.
        after = command_json(['gflow', 'credits', 'user', '--json'])
        actual = quote['balance'] - after['credits']
        if actual != quote['credits']:
            ledger('update', '--attempt', attempt_id, '--status', 'uncertain', '--balance-after', after['credits'])
            raise ValueError(f"Observed credit change {actual} differs from quote {quote['credits']}; retain the reservation and reconcile account activity.")
        settled = ledger('complete', '--attempt', attempt_id, '--status', 'completed',
                         '--actual-credits', actual, '--balance-after', after['credits'],
                         '--settlement-evidence', f"Output downloaded; balance {quote['balance']} → {after['credits']}; verified quote {quote['credits']}. No concurrent pilot generation.")
        print(json.dumps({'attemptId': attempt_id, 'status': 'completed', 'output': str(output),
                          'actualCredits': actual, 'metadata': metadata, 'budget': settled['budget'],
                          'responseFile': str(reports / 'stdout.json')}))
        return 0
    except (Exception, KeyboardInterrupt) as error:
        if attempt_id:
            try:
                ledger('update', '--attempt', attempt_id, '--status', 'uncertain',
                       '--notes', f'Runner stopped ({type(error).__name__}): {error}; reconcile before another generation.')
            except Exception:
                pass
        print(f'Generation stopped ({type(error).__name__}): {error}. No automatic retry. Attempt: {attempt_id or "not reserved"}.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
