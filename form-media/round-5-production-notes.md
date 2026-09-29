# Round 5 · production handoff

Current phase: operator review, with three held motion studies. Production and focused manual web/media inspection are complete for this batch. The user requested 15 NEW exercises, mostly compound, with Anatomical 3D as the only future generated-video style, visible muscle glow, and exactly one complete repetition with a full return. No automated test/build/lint/type/native/theme checkpoint is authorized.

Round 4 raw final reviews are preserved in `reviews/round-4-completed.json`. Press was explicitly accepted as Anatomical in the user's prose while its checkboxes still named the old Graphic clip; the manifest reconciles this with the old selected IDs and source note retained. Squat is accepted. Lateral Raise's pulse/partial return, Row's missing back highlighting and Deadlift's missing highlighting are recorded as correction backlog, separate from the 15 new exercises. Do not repeat the previous AI claim that Lateral's movement was a clean single cycle.

The 15 new exercises are in `round-5-jobs.json`: ten compound and five isolation. Canonical instructions and muscles are copied into shot briefs, while the catalog remains unchanged. Prompts and exact hashes are registered. `style-v5.md` supersedes Graphic and Round 4 all-gray exceptions. Every exact still needs an AI ready-to-animate record before paid motion. Do not use the first tightly cropped incline-press still; its rejection is recorded. Prompt 5.1 reserves the whole movement envelope and removes unneeded hip-cutaway wording from upper-body exercises.

Budget at entry: cumulative limit 2,000, spent 840, remaining 1,160. `attempts.json` is authoritative, including uncertain submitted jobs. Live Flow UI still works in the original project/profile; legacy API quotes return 401. gflow remains 0.72.0. Use the guarded runner with fresh exact UI quote evidence, then fresh account balance after each output before settlement. Submit one output at a time, including references. Never infer a zero charge just because an image quote is zero. Never upgrade or restart login merely because the old API endpoints fail.

Working local helpers currently reside in `/tmp/spotbot-r5-plan.py` (one-time materialization; do not rerun), `/tmp/spotbot-r5-run.py` (explicit job index, actually observed balance and price; records quote and invokes guarded runner), `/tmp/spotbot-r5-review.py` (actual inspection evidence), and `/tmp/spotbot-r4-settle.py` (exact observed balance reconciliation). Before relying on a helper, inspect it. Jobs, prompts, ledger and review evidence in this repository remain durable if temporary helpers disappear. The production CLI commands are `Scripts/generate_form_media.py`, `Scripts/prepare_form_media_asset.py`, and `Scripts/sync_form_media_reviews.py --round round-5`.

Next action: review Round 5 in the dashboard. Do not regenerate existing candidates automatically. Pull-up and Bulgarian Split Squat require new references in a separately tracked later round; Chest Dip exhausted all three motion attempts. Keep held studies visible and do not present them as correct demonstrations.

## Reference production findings

All 15 active movements now have inspected starting references. Front Squat was held after three unsuccessful pose/color references and replaced with Single-Arm Dumbbell Row; its history remains visible. Bulgarian Split Squat uses a lowered technical reference: the generated motion must first rise, then perform one full top-to-bottom-to-top cycle, and its delivery must trim that initial setup rise at original speed. Do not label the technical reference as the normal start.

Reference pose beats repeated style wording: conflicting source grips needed text-only pose corrections for barbell curl and pushdown. No muscle cutaways are used in this batch. Preserve opaque shorts and never paint a glute target onto anterior thigh or shorts fabric. Permanent orange/blue material with restrained emissive glow is more reliable than phase-dependent activation wording.

Use dense 4-fps editorial sheets plus full-size key frames for ambiguous depth/contact. The first push-up had one cycle but shallow lowering and was rejected. Incline press has a contiguous original-speed 6.75-second full-cycle edit with blank top margin cropped; exact edit provenance is in edits.json. AI candidate status is distinct from operator acceptance.

A zero-quoted step-up image timed out. It was reconciled against an unchanged fresh balance, retained as failed delivery with provider acceptance uncertainty noted, and checked again for late output before a deliberate retry succeeded. Do not erase the failed attempt or infer that a timeout proves no provider request.

The submission helper now takes four arguments: job index, observed account balance, observed price, and the exact UI observation timestamp. Fresh UI quote evidence must precede each generation.

## Closeout · 2026-09-15

All 15 requested new exercises have generated motion studies (10 compound, 5 isolation). Twelve have AI editorial candidates; three remain flagged: Pull-up (repeated partial pulls, unusable third reference), Bulgarian Split Squat (head clipped at standing and fading glow), and Chest Dip (three shallow pulsing motion attempts despite a clearer second reference). Front Squat is additional failed reference work, replaced in the 15 by Single-Arm Dumbbell Row. No held output is cleared for app publication.

The authoritative measured result is `round-5-summary.json`. Candidate deliveries total 6.43 MB, individually 273,261–824,771 bytes. Several exact contiguous original-speed edits remove extra reps, initial settling, or a faulty post-movement tail; eight edits are recorded with source hashes, source time ranges, and optional still holds in `edits.json`. No footage was reversed or a return phase invented. Generated masters remain outside Git.

Round spending: 312 credits, including rejected videos; cumulative 1,152 / 2,000, zero reserved, 848 remaining. Latest independently observed Flow balance: 8,928. All submissions are settled. Images were quoted and reconciled at zero. No background generation or automated retry remains.

Manual evidence: inspected every generated motion and each candidate edit using dense 4fps sheets and full-size frames where depth/contact was ambiguous. Dashboard wide view and 390×844 CSS viewport had readable guidance and no horizontal document overflow. Native HTML video playback completed for the edited incline press (6.75s) and barbell curl (5.17s), readyState 4, no reported media error. Orange/blue legend matches current standard. Candidate count distinguishes drafts from AI-reviewed videos; held exercises show a clear production note. User review selections/history were preserved; no fake operator review was submitted.

Automated tests, builds, lint, type checks, native/device verification and theme sweeps remain deferred by repository workflow. This is a review batch, not production approval. The next task should start with the user's Round 5 reviews and the durable summary, not a fresh generation run.
