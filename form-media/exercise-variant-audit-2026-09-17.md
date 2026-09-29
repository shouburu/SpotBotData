# Exercise naming cleanup and variant audit — 2026-09-17

## Implemented

Renamed all 16 remaining Grip-named exercises, preserving canonical IDs and old names as search aliases. The naming change retains meaningful apparatus and movement distinctions. Former grip-width cues were generalized where practical; secure equipment contact remains explicit. Incline dumbbell fly no longer mandates wrist rotation. Historical media prompts and outputs remain unchanged.

Merged Bench Press - Powerlifting into Barbell Bench Press; Bench Press and the powerlifting name are searchable aliases. Previous media/reviews remain archived without approval transfer. Catalog 2026.09.8 revision 6 contains 859 exercises and no display names containing Grip.

| Previous name | Current name |
| --- | --- |
| Barbell Incline Bench Press - Medium Grip | Barbell Incline Bench Press |
| Bent-Over Neutral-Grip Dumbbell Row | Bent-Over Dumbbell Row |
| Cross-Bench Single-Dumbbell Close-Grip Press | Cross-Bench Single-Dumbbell Press |
| Close-Grip EZ-Bar Curl with Band | EZ-Bar Curl with Band |
| Close-Grip EZ-Bar Press | EZ-Bar Bench Press |
| Close-Grip Push-Up off of a Dumbbell | Push-Up off of a Dumbbell |
| Decline Close-Grip Bench To Skull Crusher | Decline Bench Press to Skullcrusher |
| Incline Dumbbell Fly with Rotating Grip | Incline Dumbbell Fly |
| Incline Push-Up Reverse Grip | Rack-Bar Incline Push-Up |
| Lying Close-Grip Bar Curl On High Pulley | Lying High-Pulley Bar Curl |
| Lying Close-Grip Barbell Triceps Extension Behind The Head | Lying Barbell Triceps Extension Behind the Head |
| Lying Close-Grip Barbell Triceps Press To Chin | Lying Barbell Triceps Press to Chin |
| Seated Close-Grip Concentration Barbell Curl | Seated Concentration Barbell Curl |
| Wide-Grip Decline Barbell Pullover | Decline Barbell Pullover |
| Wide-Grip Pulldown Behind The Neck | Behind-the-Neck Pulldown |
| Wide-Grip Rear Pull-Up | Behind-the-Neck Pull-Up |

## Additional candidates found — not yet merged

These 19 examples come from comparing catalog instructions and equipment, not name matching alone. They are consolidation candidates under the user preference, not claims that all grips or techniques have identical training effects.

| Variant | Existing standard exercise | Differentiator |
| --- | --- | --- |
| Reverse Triceps Bench Press | Barbell Bench Press | Reverse hand orientation on the same flat barbell press. |
| Push-Up Wide | Push-up | Hand spacing. |
| Incline Push-Up Wide | Incline Push-Up | Hand spacing on the same raised bench setup. |
| Reverse Barbell Curl | Barbell Bicep Curl | Palms-down rather than palms-up grip. |
| Reverse Cable Curl | Cable Bicep Curl | Hand orientation on a low-cable bar curl. |
| Reverse EZ-Bar Preacher Curl | EZ-Bar Preacher Curl | Hand orientation; same EZ bar and preacher support. |
| Standing Dumbbell Reverse Curl | Dumbbell Bicep Curl | Hand orientation; both arms curl together. |
| Underhand Cable Pulldowns | Lat Pulldown | Hand orientation and width at the same pulldown station. |
| Standing Palms-In Dumbbell Press | Dumbbell Shoulder Press | Neutral hand orientation on a standing overhead dumbbell press. |
| Cross-Arm Front Squat | Front Squat | Front-rack hand support style. |
| Hammer Curl | Dumbbell Bicep Curl | Neutral rather than supinated grip; both arms together. |
| Incline Hammer Curls | Incline Dumbbell Curl | Neutral grip on the same supported incline curl. |
| Alternate Hammer Curl | Alternating Dumbbell Curl | Neutral grip on the same alternating movement; preserve per-side counting if merged. |
| Narrow Stance Squats | Barbell Squat | Stance width. |
| Wide Stance Barbell Squat | Barbell Squat | Stance width. |
| Narrow Stance Leg Press | Leg Press | Foot spacing on the machine. |
| Narrow Stance Hack Squats | Hack Squat | Foot spacing on the same machine. |
| Olympic Squat | Barbell Squat | High-bar/upright squat style and depth cues; inspect technique guidance before merging. |
| Barbell Full Squat | Barbell Squat | Explicit deep range; decide whether depth is guidance or a distinct tracking variant. |

Keep genuine differences explicit: incline versus flat pressing, dumbbells versus barbells, standing versus supported/seated work, single-arm versus bilateral counting, behind-the-neck paths, combined press-plus-extension repetitions, and added bands/supports are not merely names. Palms-up wrist curls and palms-down reverse wrist curls involve different wrist actions; do not collapse them solely because the title mentions hand orientation.

Validation phase: intrinsic catalog/schema export completed successfully, regenerating shared app and backend starter snapshots. Manual local dashboard check completed: revision 6 shows 859 tracked exercises; the incline result is Barbell Incline Bench Press, and searching Bench Press - Powerlifting returns the accepted Barbell Bench Press entry. No review decision was changed. No automated tests, lint/type checks, app builds, native/device work, theme sweep or cloud publication. Future action: select additional variant consolidations from this report before editing those identities.
