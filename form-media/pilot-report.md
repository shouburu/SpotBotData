# Exercise form media pilot — review collection

Completed production pass: 9 September 2026. The local dashboard contains ten representative studies and a durable, provisional queue for all 991 canonical exercises. This is a style-selection collection, not a published library or trainer-approved instruction.

## Spending and delivery

**66 credits spent; 0 reserved; 934 of the 1,000-credit ceiling remain.** All 14 attempts, including failed setup, recovered output and rejected media, are retained in `attempts.json`. Current account-specific Nano Pro quotes were 0 credits; eight-second Omni clips cost 12 and ten-second clips 15. Future runs must obtain a new live quote.

Selected-package sizes include posters and overlays, exclude rejected candidates and full-quality masters, and use decimal KB. Text/external references add no hosted media binary.

| Exercise | Pilot format | Selected package | Editorial outcome |
|---|---|---:|---|
| Barbell Bench Press | video | 547.99 KB | Bench endpoint needs human review |
| Standing Calf Raise | animation | 7.48 KB | Ready for style/content selection |
| Plank | image | 17.38 KB | Ready for style/content selection |
| Clean and Jerk | external | 0.00 KB | Ready for style/content selection |
| Turkish Get-up | external | 0.00 KB | Ready for style/content selection |
| Seated Ankle Pump | animation | 6.86 KB | Ready for style/content selection |
| Yoga — Mountain Pose | image | 21.76 KB | Ready for style/content selection |
| Treadmill Walking | text | 0.00 KB | Ready for style/content selection |
| Outdoor Walking | text | 0.00 KB | Ready for style/content selection |
| Dead Bug | video | 17.71 KB | Still + text fallback; all motion rejected |

The largest selected package is 0.548MB, below the 5 MB limit. All preserved masters, derivatives and reference copies currently total 12.87MB locally. They are outside Git and need separate backup.

## What the pilot established

- The shared matte-gray mannequin, charcoal clothing, soft studio and separate editable guides work well for static alignment. Orange means primary muscle involvement; blue means supporting involvement. These are schematic regions, not measured activation. Mountain's catalog category is full body, so its overlay adds alignment without inventing regional muscle claims.
- Authored SVG motion is appropriate for bounded ankle movement and calf rise. The two schematic files are about 7 KB each, start paused, and offer play/pause, restart and scrubbing. They intentionally use simplified geometry rather than pretending to be a human rig.
- Bench v1 was rejected for incomplete lowering. The fuller v2 remains a review candidate: fixed support and equipment are consistent, but the foreground arm/camera obscure the exact chest-level endpoint. The overhead still teaches arm alignment separately.
- Dead Bug is the failure boundary. Three starting frames produced a usable elevated setup still. All three generated motion candidates failed arm trajectory, stationary-limb or alternation constraints, including a simpler one-diagonal attempt. No motion clip is selected. The setup still and catalog Form text remain available; use authored precise motion or an expert demonstration before publishing movement guidance. Do not salvage a wrong arm path by cropping or reverse footage to manufacture a return.
- The two complex sequence examples link to Catalyst Athletics and StrongFirst with attribution; no third-party video was copied or rehosted.

## gflow operation and recovery

Generation ran through gflow 0.72.0, which internally uses an isolated Chrome profile. The version/hash-checked macOS cookie-reader patch used that existing profile directly. Credit reads and successful submissions completed without password input. The local gflow media database was initialized through its normal data command.

The first bench still existed in Flow although CLI collection timed out; it was recovered without regeneration. A Mountain 3:4 request failed before submission because that aspect is not ported to gflow's migrated frontend; 9:16 worked. A Bench retry stopped in a duplicate reference picker before submission; after reconciliation, a uniquely named copy of the same reference avoided that picker ambiguity. Both failures were settled at 0 based on diagnostic evidence, matching project checks and unchanged credit balance. Original outcomes remain recorded.

The runner reserves a live quote, freezes prompt/reference/model evidence, records the submission before waiting, and leaves uncertain reservations in place. It enforces one outstanding attempt, the credit ceiling, three attempts per shot, and no regeneration of an accepted selected shot. It is a workflow guard, not a provider billing cap. Generated masters retain hashes, locations and measured dimensions/duration. Delivery uses WebP or silent H.264 MP4 with fast-start; no return phase is reversed.

## Manual review and remaining phase

Authorized validation was source inspection and focused manual web feedback. The dashboard was inspected at 390 × 844 CSS pixels and a wider 1400 × 1000 CSS viewport, in the existing theme. Search across all 991 exercises, hash-based exercise navigation, candidate comparison, overlay loading, schematic play/pause/scrubbing, video playback through its full eight-second duration, saved selections/notes after reload, and text fallback when the Plank image was temporarily unavailable were exercised. The image was restored and confirmed loaded. No automated tests, test maintenance, builds, lint, type checks, native/device checks or theme sweep were run.

All ten content decisions remain `needs-review` for operator selection. AI editorial evidence is distinct from content decisions, and trainer review is explicitly not recorded. The next step is to select the still/schematic style, review Bench's endpoint, and replace Dead Bug motion with a precise or expert source. Further catalog recommendations remain provisional and are not an authorized bulk generation batch.

The app's exercise-title navigation, Form media integration, schema/export changes and Appwrite uploads remain in the subsequent app phase. No published exercise contract or production hosting changed.
