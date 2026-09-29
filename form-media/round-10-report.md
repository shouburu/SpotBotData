# Round 10 · review handoff · 2026-09-22

**Closed after user review.** The [Round 11 handoff](round-11-report.md) is current. Two user-requested 0–4 second clips were accepted, Donkey Calf Raises was retired, and the remaining Round 10 decisions and quality holds were preserved. The paragraphs below document the original review-ready production checkpoint.

Round 10 is open for human review. It targets the 39 surviving Round 9 exercises that were rejected or still pending after the user's decisions. **Fourteen new Anatomical 3D videos passed an exact-delivery AI editorial screen and are in Needs Review.** The other 25 are on documented quality hold, not silently presented as reviewable clips. AI screening is not user acceptance or trainer approval.

The user explicitly requested removal of 16 Round 9 exercises. Their active records and current queue entries were retired before generation, leaving catalog version `2026.09.22.1`, revision 11, with 437 active exercises and 554 retired identities. The [decision archive](reviews/round-9-user-catalog-decisions-2026-09-22.json) retains exact names, prior reviews, selected assets and source mappings. The closed Round 9 review set has 94 entries: 55 accepted, 31 rejected, eight pending. No accepted exercise was automatically regenerated.

## Delivered for your review

Machine Triceps Extension; Thigh Abductor; Hack Squat; Leg Press; Smith Machine Squat; Decline Dumbbell Bench Press; Dip Machine; Arnold Press; Dumbbell Lunges; Cable Crunch; Donkey Calf Raises; Seated Calf Raise; Decline Smith Press; and Thigh Adductor. The selected delivered files are 720 × 1280, silent H.264 MP4. Their measured sizes range from 457 KB to 789 KB, averaging 586 KB. Leg Press and Seated Calf Raise use documented original-speed full-cycle trims with still endpoint holds; their untrimmed masters remain preserved. The exact selected asset IDs and SHA-256 evidence are in [round-10-outcome.json](round-10-outcome.json), the manifest and the per-wave reviews.

The dashboard at [http://127.0.0.1:8766](http://127.0.0.1:8766) has a Round 10 pilot scope. Use **Show media needing review**, then **Generated in → Round 10**. The round now requires an editorial pass, so AI-held videos and flawed source stills do not inflate Needs Review. A human review saves the exact loaded asset IDs and preserves the prior Round 9 decision in history.

## Production and spending

- 62 generated source frames and 24 generated videos; 14 exercises have screened candidate deliveries and 25 target exercises remain on quality hold. Two candidate delivery trims are additional assets, not new paid generations. Twelve original video deliveries are flagged for correction, including the two untrimmed masters whose complete-cycle trims became candidates.
- The source frames were zero-credit Nano Banana Pro edits after a live quote; each paid Omni Flash video had its own live price observation. Round 10 spent **247 credits** in the existing `google-flow-2026-09-21` period. Current period spending is **5,587 / 10,000**, with **4,413 remaining**, zero reserved and zero unresolved attempts. Lifetime spending is 10,159. Do not reset this period on resume.
- The version-checked [gflow image-picker patch](../Scripts/patch_gflow_image_picker.py) corrects an observed Nano Banana Pro picker race in installed gflow 0.75.0. It has a local backup. gflow generation still uses its CLI and isolated Chrome profile internally; no manual browsing of Flow is part of the normal producer path.
- One producer group at a time was used, with up to four isolated workers in a group. Before each group the runner confirmed the live model/duration price and reserved the full amount. Interrupted or uncertain submissions must be reconciled before any retry. All this round's attempts settled.

## Quality holds and next approach

Every held output has an exact path, hash and observed failure in [round-10-outcome.json](round-10-outcome.json); corresponding source and delivery reviews are in `round-10-*reviews.json`. Preserve those assets and human feedback. The next attempt requires a genuinely different physical reference or medium, not simply stronger negative wording.

| Failure pattern | Held exercises | Next useful method |
| --- | --- | --- |
| Press or curl substituted for the required fixed-joint movement | Machine Chest Press, Dumbbell Fly, Dumbbell Shrug, Cable Crossover, Bent-Arm Barbell Pullover, Cable Shrugs, Decline Dumbbell Flyes, Incline Dumbbell Fly | Prepare correct start **and** full endpoint reference poses with physical object continuity, or author a short mechanical animation. Current Flow/gflow cannot use an end frame in its available account mode. |
| Correct broad motion but cue or loaded joint fails | Straight-Arm Pulldown, Calf Press, Clean and Press | Rework the endpoint and muscle-cue method; do not use a generated clip with absent orange glow, knee-driven calf motion or an incorrect front rack. |
| Cable or machine topology remains implausible in the source | Cable Rear Delt Fly, One-Legged Cable Kickback, Pull Through, Smith Machine Calf Raise, Standing Dumbbell Calf Raise | Build a verified equipment/foot-contact reference, potentially from an authored diagram plus a trusted real apparatus view, and inspect the exact generated start before any motion charge. |
| Start pose or implements contradict the named lift | Clean, Dumbbell Clean, Power Snatch, Bar Inverted Row, Landmine 180's, Smith Machine Stiff-Legged Deadlift, Stiff-Legged Dumbbell Deadlift, Prone Dumbbell Shoulder External Rotation, Barbell Overhead Triceps Extension | Use a real pose/equipment anchor or an expert reference video; require the correct bar-on-floor, heel support, hinge, grip or fixed elbow before video generation. |

The last six-source correction pass yielded one acceptable wide-open Cable Crossover still, but its video folded the elbows into a press at the close endpoint, so it remains held. Other corrections still had wrong cable routes, foot placement or knee angles. This is a useful limit on the current generative path: source accuracy and exact motion are separate gates.

## Validation scope and resumption

Manual review covered the exact delivered files at four frames per second plus selected full-resolution phase frames. The dashboard was inspected at approximately 390 × 844 and 1100 × 800 CSS-pixel viewports; its Round 10 count showed 14 screened video candidates after the editorial gate was enabled. The catalog exporter ran after the 16 authorized removals. Automated tests, builds, lint/type checks, native/device verification, theme sweeps, app binary publication and trainer review were not authorized or run.

For current work, resume from [Round 11](round-11-report.md) and its [plan](round-11-plan.json). The Round 10 plan, jobs, outcome, manifest history and ledger preserve this checkpoint and its exact failed attempts. A future candidate is exposed to human review only after its exact delivered file passes the same form, muscle-cue, one-repetition and equipment checks.
