> Historical checkpoint: the user completed Round2 review and selected Graphic3D. Current work is tracked in `round-3-production-notes.md`. The figures and pending decisions below describe the end of Round2 production.

# Round 2 handoff — ready for user review

Current phase: local user review of the completed, bounded 20-exercise media collection. All original ten exercises received alternatives; ten new compounds cover five seated and five standing movements. Compare Porcelain studio, Warm ceramic and Graphic 3D. The next action is user style/asset selection, followed by an explicitly scoped production round. Do not automatically fill the remaining budget or produce the other 971 provisional catalog recommendations.

## Accounting and durable records

- Cumulative ceiling: 1,000 credits. Round 1 spent 66; Round 2 spent 522. Total spent 588, reserved 0, remaining 412. All 96 Round 2 generation attempts settled: 55 stills and 41 videos. There are no uncertain submissions to reconcile.
- Round 2 has 115 review assets: 55 WebP images, 53 MP4s (41 generated originals plus 12 authored edits), and seven external references. Masters and derivatives remain outside Git. `round-2-metrics.json` and `round-2-report.md` record measured sizes and outcomes.
- `attempts.json` retains frozen prompts, exact reference/upload hashes, live quote evidence, job IDs and balance settlement. Rejected attempts remain charged and reviewable. One output at a time; no concurrent use of the gflow profile.
- gflow 0.72.0 continues to use the version-checked profile-first macOS cookie patch. No Keychain/password prompts were observed this round. The CLI internally depends on its isolated Chrome profile; manual Flow website operation was not used for production.
- First-round snapshot remains read-only at `reviews/round-1-before-round-2.json`, SHA-256 `971faaa3873fb53548cb3309bce2e9c9d8293f5b04e9f7a21787d6a4c5fd6473`. All 15 earlier assets and original review decisions are retained. Only two explicitly labeled Codex Pending review-history entries were added; the second supersedes the provisional Warm Bench preview selection after closer review. User acceptance remains pending for all new round choices.

## Outcomes and limits

Nineteen exercises have at least one AI editorial media candidate; Outdoor Walking recommends text after both optional generated walks failed to establish clear forward travel. All current assets have editorial evidence: 32 candidates, 26 starting-pose approvals, 37 needs-review and 20 rejected. These are AI findings, not user or trainer acceptance.

Seated Dumbbell Press and Barbell Squat have useful candidates in all three styles. Complete-cycle authored edits also improve ankle pump, rows, pulldown, leg press and machine chest press. Keep actual speed and retain masters; trims and real endpoint holds spend no generation credits. Never manufacture a return or splice mismatched anatomy.

Bench motions all remain flagged for unclear chest endpoints, including Warm after independent full-resolution review. The final Warm bottom-contact image is a **static-only** candidate (`presentationRole: static-detail`); it does not pass the full-motion envelope gate. No corrective video was generated from that final image. The CrossFit 38.901-second reference supplies a clearer movement demonstration, alongside optional static bottom/overhead views.

Dead Bug's 4.5-second Graphic edit shows **one opposite-limb repetition**, not alternation. Adjacent Form directs alternating sides; the user's 19.521-second human reference remains available. No autoplay or automatic looping. The other generated sequences remain flagged for limb pairing, repeated sides or hand artifacts.

Low Step-Up's final full clip still does not verify trailing-foot-first descent. Its 5-second authored **ascent detail** shows both feet on top and explicitly omits descent/complete-repetition claims. Walking Lunge's generated takes return backward; the 29.281-second Rogue reference is explicitly a loaded variation while catalog default equipment remains bodyweight. Deadlift uses the short CrossFit reference because no generated starting image passed its floor-setup gate. The original catalog variants and counting rules remain unchanged.

The four `round-2-*-reviews.json` collections own exact-output findings. `sync_form_media_reviews.py` imports them without changing user choices. Eight unmatched authored-reference records are intentional: those canvas files are production references rather than delivery assets. The final Bench still's latest static-candidate status also keeps the animation gate closed because it is not `ready-to-animate`.

## Dashboard and validation scope

Local dashboard: `http://127.0.0.1:8766/` (server started in shell session 33702). Run `python3 Scripts/form_media.py serve` if it is no longer running. Existing queue resume commands reuse settled output; explicit corrections retain their shot identity and three-attempt maximum. All Round 2 spending is stopped. Do not rerun ignored one-off correction drivers: their expected attempt histories deliberately fail after use.

Focused manual web review covered approximately 390 × 844 and 1360 × 900, round/style comparison, history, candidate archives, file details and review persistence. Native browser playback of representative Bench, calf, seated press and Graphic Dead Bug clips completed without player errors; Dead Bug was confirmed without autoplay or looping. Phone DOM measured 389 × 844 with no horizontal overflow. External cards display verified full-source duration, orientation and attribution. Text-first Outdoor Walking remains readable while generated alternatives are accessible. Starting frames/earlier attempts are collapsed; explicit selection is preserved, and unselected defaults favor reviewed useful media over flagged generations.

No automated tests, test changes, production/native builds, lint, type checks, theme sweeps, emulator/device checks, catalog publication or app integration were performed. The catalog remains 991 exercises at version 2026.09.4 / revision 2. These deferred checkpoints require a separate explicit scope; finishing this content round does not authorize them. Production hosting and exercise-title/detail-route changes remain a later app phase.

Final focused UI follow-up: external-format defaults now open a reviewed external reference, Outdoor Walking defaults to text while optional takes remain accessible, and the static Bench bottom detail appears in the primary candidate list. Bench history shows three entries (original snapshot plus two Codex Pending notes). A wider root viewport measured 1416 × 937 with no horizontal overflow; its temporary viewport override was then reset.
