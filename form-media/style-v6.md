# Anatomical 3D — standard 6.0

Continue the visual standard in style-v5.md: silver anatomical mannequin, white background, gray equipment, fixed camera, orange primary and blue supporting illustrative muscle involvement, no generated text or audio. All future generated videos use this style.

Round 5 operator feedback overrides earlier AI candidate judgments. Accepted: barbell curl, barbell step-up, Bulgarian split squat, incline dumbbell press, incline push-up, lying leg curl, single-arm dumbbell row. Keep those selections and their original editorial limitations. Leg Extension has no submitted decision yet.

## Required corrections and review gates

- A repetition must reach BOTH the exercise-specific outer endpoint and the complete starting endpoint. Dip and pull-up were rejected for two shallow bobs. Count excursions and inspect actual range; "one cycle" alone is insufficient.
- Inspect the grip at the start, middle, turnaround and return at full resolution. Hammer Curl must maintain palms inward with no forearm supination. Straight-Bar Triceps Pushdown must keep a closed pronated grip with neutral wrist alignment throughout; reject impossible rotations.
- The prior hammer-curl clip may be repurposed only if it matches a canonical dumbbell-curl variant. The catalog's alternating curl is unilateral, while its simultaneous curl begins supinated: do not silently relabel a bilateral rotating curl to either contract.
- Push-up: create the operator-requested 0–5s excerpt and review that exact derivative. Preserve the rejected full source and provenance.
- Pike Push-up: replace generated instruction with an attributed YouTube reference for review.
- Reverse Lunge rejected overall; do not carry its AI candidate status into the new round.
- Preserve visible anatomically anchored muscle glow for the whole rep. For covered primary muscles, establish a valid anatomical treatment before paying for motion; opaque shorts with glow painted onto them do not qualify.

## Round 6 production and budget

Cumulative authorized ceiling: 10,000 credits. Opening spend: 1,152; opening available allowance: 8,848. Preserve all prior charges and uncertain reservations. Live quotes remain authoritative. Unknown prices or uncertain submissions stop paid generation.

Scope: catalog compound/isolation exercises with dumbbells, barbell/specialty bars, resistance machines, cable stations or Smith machine. 432 eligible catalog entries, 11 accepted entries preserved, 421 remaining entries tracked individually. Similar names do not imply interchangeable grips, apparatus or repetition conventions. Prior pending media remains available; a queue entry is not a generated or approved asset.

All 842 starting-image/motion prompts begin as drafts. Review exact pose, physical endpoint, camera, equipment and grip before submitting each; inspect and hash the exact starting frame before paid motion. At most three attempts per logical shot. Keep production state distinct from human decisions.

User permits concurrent generation and multiple outputs. Installed gflow 0.72.0 uses a shared generation lock/context request handler; its own source warns concurrent use can strip another job's references. Existing video result handling returns only one media object. Use the new explicit group runner with separate gflow worker profiles for two or three concurrent jobs. Never overlap jobs inside one profile/context. Each job requests one output, freezes its own quote and exact prompt/reference hashes, and reserves credits before submission. Settle only when every output succeeds and the fresh aggregate balance change equals all frozen quotes; record per-job costs as aggregate quote allocations. Unknown or mismatched charges halt the group. Initial zero-credit references and the first three-video group completed with matching aggregate settlement.

Phase remains rapid implementation and focused manual web/media review. No automated tests, builds, lint, type checks, native/device checks or theme sweeps authorized or run.
