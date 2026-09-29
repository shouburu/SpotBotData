# Round 9 review handoff

**September 22 catalog update:** Finger Curls, Wrist Roller, Barbell Wrist Curl, and Seated Palms-Down Barbell Wrist Curl were explicitly retired. The same review round now has **110 exercises**, with **93 that received AI-screened candidates and 17 production holds**. Human reviews continue in the live manifest. The production totals and findings below describe the original 113-exercise batch; retired media and spending remain archived. See the [retirement record](reviews/retired-forearm-exercises-2026-09-22.json). No new credits were spent.

**95 of 113 target exercises now have AI-screened Anatomical 3D video candidates. 18 remain on hold.** Coverage is partial: the held exercises do not have a video that meets the current requirements. The round is ready for human review; nothing was marked human-accepted.

Open [the local review dashboard](http://127.0.0.1:8766/) and choose **Show media needing review**. New videos show **New · Round 9 · Video ready** and **Needs review**. Use the Candidate round control to compare Round 9 with older versions. Pending means awaiting media or an initial decision; Needs review is derived from new reviewable media or a deferred human decision. Earlier human rejections remain in history even when a new candidate makes that exercise need review again.

## Allowance and production

- The requested new period began at zero on September 21, 2026. Cap: **10,000 credits**. Used: **5,340**. Available: **4,660**. Reserved/uncertain: **0**.
- Historical spending remains **4,572**, making lifetime recorded spending **9,912**. The current period is `google-flow-2026-09-21`; do not reset it on resume.
- All submissions are settled. The last observed Flow balance was 4,760, 100 above the local allowance after separately recorded provider/account adjustments. Those adjustments were not added to the authorized cap.
- Production used four isolated gflow workers in parallel, with one coordinating producer. Live prices were verified per settings group and bound to individual submissions. No producer remains running.
- **368 actual video submissions** produced 330 complete video masters and 38 evidenced zero-charge provider failures. **336 image generations** completed. These totals include all rejected attempts and corrective work, not just the delivered candidates.

## Review results and delivery

There are **100 AI-candidate clips across 95 exercises**. Five exercises have two review alternatives; these are not extra exercise coverage. A separate Preacher Curl 0–5-second excerpt requested in the user's earlier notes remains visible as an operator-requested edit, with AI status Needs review; it is not counted among the 100 screened candidates.

Every candidate has exact-output editorial evidence and a file hash. Screening considered the actual start, full endpoint, return, extra pulses, working joint motion, equipment contact, anatomical consistency and muscle cue. Candidate means it passed this AI editorial screen, not independent trainer review or human acceptance. Notes disclose remaining minor limitations.

- Candidate videos: **57.82MB total**, median **552KB**, range **231KB–1.08MB**.
- Posters add **3.36MB**. Videos plus posters total **61.18MB** for all alternatives.
- Duration: **3.08–10 seconds**, median **6 seconds**. All are silent H.264 MP4 with fast-start.
- **69 portrait / 31 landscape** clips. 63 are 720×1280; the others use landscape compositions or reviewed crops that retain the working movement. These are layout exceptions, not all portrait.
- Largest per-exercise candidate package including alternate options and posters: **1.29MB**. No package exceeds 5MB. Rejected attempts, masters and reference images are excluded from delivery package sizes and should not be bundled into the app.
- **48 authored derivatives / 52 original deliveries.** Edits preserve actual continuous motion at original speed, with endpoint holds where recorded. No reversed footage was used to fabricate a return.

The Standing Barbell Calf Raise candidate is explicitly a lower-body mechanics detail: both knees and feet are visible, but barbell setup and unracking are outside the frame. The source still and full instructions remain available. Select a single final option per exercise before future publication.

## Lessons to retain

1. Start with a reviewed physical pose, then describe the motion the image actually supports. Appearance references alone do not guarantee sound mechanics.
2. Describe one complete cycle through specific visible endpoints and stable contact points. Short six-second isolated movements often reduce repetition drift, but still require exact review.
3. Fix the physical reference when repeated attempts substitute the wrong movement. Transferring a successful related starting pose worked for straight-bar skull crushers and flat dumbbell flyes; it failed for barbell overhead triceps, so transfer is a hypothesis rather than inherited approval.
4. Keep a genuine full cycle if a longer video includes one, trimming extra repetitions or idle color fade only after a complete return. Do not crop away a form defect or invent missing motion.
5. Review glow throughout the working cycle. It represents muscle involvement, not measured activation intensity. Incorrect anatomy or misplaced cues remain grounds for correction.
6. More expensive models did not reliably repair the remaining mechanical failures. Preserve credits when no distinct corrective method remains; do not repeatedly spend 100credits on the same failure.

## Outstanding exercises

The 17 quality holds below still show incorrect motion or an unusable starting pose. Cable Rear Delt Fly is a separate provider hold: its latest reviewed source produced no video in three consecutive, zero-charge attempts. These are not all attempt-cap exhaustion; some stopped because repeated trials had no viable new corrective hypothesis. No missed usable output or unattempted latest ready source was found among these 18.

| Exercise | Hold reason |
|---|---|
| Bar Inverted Row | The body rocks upward while the elbows remain nearly long; the required chest-toward-bar row through elbow flexion is absent even though heel/bar contacts remain stable. |
| Barbell Overhead Triceps Extension | The final source changes the standing raised-upper-arm triceps pose into a seated behind-neck press setup with low outward elbows. The last video also drops the upper arms and presses upward rather than completing an elbow-isolated extension cycle. |
| Cable Crossover | The Quality trial changes torso/stance and drops the hands toward the waist instead of returning to the original forward closed endpoint, then adds a partial second cycle. No complete consistent cable-fly cycle can be trimmed. |
| Cable Rear Delt Fly | The latest usable source was submitted three times, but all three attempts terminated without a video and settled at zero credits. Earlier delivered clips were rejected; there is no overlooked current-source output to review. |
| Calf Press | Both knees bend and extend to move the plate while the heels remain against it. The outputs demonstrate leg-press motion rather than ankle-only plantarflexion; trimming cannot isolate a valid calf-press cycle. |
| Clean | The shorter trial improves pull continuity but still catches the bar with low elbows and vertical forearms instead of a clear front-shoulder rack; the turnover remains curl-like and a plate crops at the rack. |
| Clean and Press | The clean becomes a deadlift pause and curl into a hand-supported low-elbow chest catch. The later overhead press and floor return do not repair the missing shoulder-supported clean; framing also crops a plate. |
| Decline Dumbbell Flyes | Even the bounded Quality trial deeply folds the elbows during closure, substituting press-like mechanics for a long soft-elbow shoulder fly, and adds a late partial pulse. No valid full cycle can be trimmed. |
| Donkey Calf Raises | The heels move together with substantial knee/hip pumping under the pelvis pad. No complete steady-knee ankle-only repetition exists in the latest output. |
| Dumbbell Clean | The grounded floor setup is now usable, but the video separates a deadlift and thigh hold from a squat/curl catch instead of one continuous close-body clean; the muscle cue also migrates onto anterior thighs. |
| Dumbbell Lunges | The Quality trial adds a split-stance dip and advances the trailing foot to the lead foot. It does not return the leading foot to the original stationary stance, so it cannot be trimmed into the catalog repetition. |
| Dumbbell Shrug | The Quality trial turns the shrug into repeated bent-arm raises/curls to head height rather than a straight-arm shoulder elevation. Broader orange spread is secondary to the wrong movement identity. |
| Finger Curls | The hands repeatedly open and close while the bar floats across fully open palms; there is no loaded roll into supported finger hooks and back into the palms. No trim can repair the missing load-bearing contact. |
| Landmine 180's | The opposite endpoint stops near the upper waist with a nearly upright shaft and bent elbows, then reverses. The first traverse lacks full range, and the catalog counts one side-to-side traverse, not the out-and-back pair. |
| Power Snatch | The bar is received in a deep squat with bent arms and pressed overhead during recovery instead of a shallow extended-arm power catch. Hamstring coloring disappears through most working phases. |
| Prone Dumbbell Shoulder External Rotation | The latest source leaves furniture underneath the proximal forearm, blocking the required downward rotation arc. Earlier motion extends/flexes the elbow instead of rotating the shoulder with a fixed bent elbow. |
| Smith Machine Calf Raise | Knees bend and hips shift backward at the low-heel endpoint, then knees straighten during the rise. The entire heel excursion therefore includes knee-driven motion rather than an ankle-only cycle. |
| Standing Dumbbell Calf Raise | The Quality trial repeats a knee dip and extension before the heel raises. No full heel cycle retains steady knees; removing the knee motion would also remove part of the heel excursion. |

Each hold is saved in the canonical exercise production status and job disposition, with exact attempt/source IDs in [the evidence audit](../reports/round-9-preparation/final-unresolved-audit.json). The dashboard shows its reason when the exercise is opened. Failed attempts remain available for comparison; no hold is exposed as a cleared new candidate.

## Preservation and verification

All 46 previously human-accepted selected-video exercises were excluded, including 36 in the loaded-equipment scope. Their decisions, notes, selected IDs and timestamps remain unchanged; all 304 baseline history entries are preserved. The 457-exercise catalog was not modified in this round. Catalog SHA-256 remains `cd14b85275ae183d00e602c8d4a4bd3ee4489cd22adf922a889998a5917d05fa`.

Candidate file/poster hashes, bytes, dimensions, durations, settled source attempts, master/reference bindings and edit provenance were inspected: no mismatch or missing candidate file was found. Manual web checks covered the new-review queue, round labels, budget, preserved feedback and phone/wide layout. Native IAB video playback crashed earlier in production; local QuickTime playback was demonstrated for one clip, not all clips. Do not claim a complete browser-playback or native-device pass.

Current phase remains local media production and focused manual media/web review. Automated tests, builds, lint, type checks, native/device verification and theme sweeps were not run and remain deferred under the repository workflow. The small queue/status and guarded-generation code changes were inspected and exercised through production where applicable; that is not a test-suite pass. No production hosting, app ingestion or published media contract changed.

## Resume safely

1. Read this report, `manifest.json`, `attempts.json`, and [the current checkpoint](../reports/round-9-preparation/current-production-checkpoint.json). The round is `ready-for-review-with-holds`; no session is running and no job is automatically armed for another retry.
2. Let the user review the 95 candidates. Preserve existing human selections and all attempt history. Do not automatically regenerate accepted or screened assets.
3. Work on a held exercise only with a distinct, documented method or corrected reference. The user has already authorized corrective generation within the current cap; a new wording-only loop is not warranted. Record any exact-shot exception without resetting history.
4. Keep gflow 0.75.0 and the installed prompt/model guards pinned until separately investigated. Use one producer and its configured isolated workers. Fresh price verification and settlement remain mandatory; reconcile uncertain work before retrying.
5. Keep the 10000 cap and current period. The recorded 4660 remainder is a handoff snapshot; recompute from the live ledger before submitting. Old report scripts and initialization/reset commands are historical, not a resume command.

Detailed records: [delivery audit](../reports/round-9-preparation/final-candidate-delivery-audit.md), [unresolved exercise audit](../reports/round-9-preparation/final-unresolved-audit.md), [accepted-video preservation](../reports/round-9-preparation/human-accepted-video-exclusion-audit.md), [handoff transition and reversible backups](../reports/round-9-preparation/review-handoff-transition.json), [shared standard](style.md), and [chronological production notes](round-9-production-notes.md).
