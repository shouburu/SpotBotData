# Round 2 exercise-media review

Ready for user review, 2026-09-10. Open the [local dashboard](http://127.0.0.1:8766/). This round revisits all 10 original exercises and adds 10 compounds: five seated and five standing. The 20-exercise sample compares Porcelain studio, Warm ceramic, and Graphic 3D through anatomical figures, closer views, stills, short clips, and external demonstrations.

**Final accounting:** Round 2 spent **522 credits**; cumulative pilot spending is **588 / 1,000**, including Round 1's 66. No credits are reserved or uncertain; **412 remain**. Generation is stopped. The ledger contains 55 completed still generations and 41 completed video generations for this round, including rejected attempts. Twelve zero-credit video edits and seven verified external references bring the round to 115 review assets. No output is silently regenerated when the dashboard opens.

The 19 exercises that use media have at least one AI editorial candidate; Outdoor Walking retains text as its recommended treatment. Across the round there are 32 candidate assets, 26 starting poses ready for possible animation, 37 needs-review assets and 20 rejected assets. A starting-pose review does not establish motion correctness. All current assets have recorded editorial evidence; none is marked accepted by the user this round.

Measured delivery sizes are **14–81 KB for stills** and **254 KB–1.01 MB for videos** (median video 658 KB), with durations of 3.58–10 seconds. All review alternatives plus posters occupy **36.58 MB**; retained Round 2 masters occupy **80.66 MB**, before upload/reference copies. The largest single delivery plus poster is **1.04 MB**. These alternatives are a review collection, not one shipping package per exercise. The dashboard enforces a 5 MB combined selection limit. See [measured counts and sizes](round-2-metrics.json); the manifest retains per-file hashes, locations and dimensions.

“Candidate” means plausible AI editorial evidence for the exact file, not user acceptance, trainer approval, or complete setup coverage. Prior attempts remain available.

| Exercise | Useful option / current finding |
| --- | --- |
| Barbell Bench Press | Generated motions remain flagged for ambiguous endpoints. CrossFit’s 38.9-second reference is clearer; the final bottom-contact still and Studio overhead still are static supplements only. |
| Standing Calf Raise | Warm and Graphic videos show complete bilateral rise/return with stable forefoot contact. |
| Plank | Studio and Warm stills show supported alignment; animation adds little to a static hold. |
| Clean and Jerk | Verified 35.8-second portrait human reference covers the floor clean, split jerk, and standing recovery. |
| Turkish Get-up | Verified 24.8-second portrait reference covers rise and floor return; final bell lowering remains written guidance. |
| Seated Ankle Pump | Warm video and 4-second Graphic trim are candidates; the full Graphic version ends during another partial cycle. |
| Mountain Pose | Warm and Graphic stills are candidates; retain simple written posture guidance. |
| Treadmill Walking | Studio video is a candidate for steady walking. Clip attachment, speed selection, and stopping remain in Form text. |
| Outdoor Walking | Recommend text this round. Both rendered attempts remain flagged for unclear forward travel and overlapping steps. |
| Dead Bug | Graphic 4.5-second trim shows **one diagonal repetition only**. Adjacent Form must direct alternation; retain the human reference. |
| Seated Dumbbell Press — seated | Studio revised trim, Warm correction, and Graphic trim provide three useful style candidates. |
| Seated Cable Row — seated | Studio and Warm single-cycle trims are candidates. Warm background weight-stack travel is not verified. |
| Lat Pulldown — seated | Studio trim shows front upper-chest pull and complete overhead return, with thigh support. |
| Leg Press — seated | Warm 5-second trim isolates a supported sled lowering/return; full two-cycle original remains flagged. |
| Machine Chest Press — seated | The wider 3.71-second first-cycle edit is a candidate, with both grips and supported torso visible. Full generated originals remain flagged. |
| Barbell Squat — standing | Warm/Graphic videos and Studio single-cycle trim are candidates. Setup and rack checks remain written guidance. |
| Barbell Deadlift — standing | Starting images failed the setup gate. Use the reviewed short CrossFit reference; no incorrect still was advanced into motion. |
| Overhead Press — standing | Studio video is a candidate with front-shoulder start, overhead press, and controlled return. |
| Walking Lunge — standing | Both generated takes return backward. Rogue’s 29.281-second reference demonstrates real forward travel; its dumbbells are clearly identified as an optional loaded variation. |
| Low Step-Up — standing | A 5-second **ascent-only** edit shows both feet on top. Follow Form for trailing-foot-first descent; none of the generated full cycles verifies the required descent order. |

Prompts need the exact catalog variant, starting pose, timed phases, required return, and visible contacts. Preserve reviewed pose and style references separately. Generic equipment wording introduced a machine into an ankle image; even “shoe” must match a barefoot reference. A complete-looking cycle is insufficient when its decisive endpoint is hidden.

Reserve the full movement envelope before motion spending. Portrait suits standing and vertical pressing; landscape accommodates floor reaches and cable travel. Dead Bug portrait reframing destroyed tabletop. Authored canvas extensions preserved the pose, but flat padding produced a panel and later edge continuation still yielded finger streaks in Warm motion. Explicit opposite-limb prompts did not ensure alternation. The intact Graphic cycle is honestly labeled one diagonal, with manual playback and no automatic looping.

Avoid stick figures and speculative markers. Contours cannot rescue an ambiguous bar path. Add muscle colors or alignment guides only where placement is defensible in that exact view. Style preference remains separate from correctness.

Actual browser playback verified [TrainHeroic Clean and Jerk](https://www.youtube.com/shorts/ZsCEUbs1Kzk), [Rebecca Rouse Turkish Get-up](https://www.youtube.com/shorts/-Zsx2JTfGsU), and the user's [Dead Bug](https://www.youtube.com/shorts/5c-vucY3beU): 35.800, 24.801, and 19.521 seconds, all portrait. Dead Bug's longest reach is cropped. [CrossFit deadlift](https://www.youtube.com/watch?v=op9kVnSso6Q&t=28s) is a 57.081-second landscape fallback; the timestamp does not enforce an endpoint. These remain external links, without copied footage or assumed republishing rights. See [reference evidence](round-2-reference-research.md) and [deadlift evidence](round-2-deadlift-reference.md).

Zero-credit [deterministic edits](../Scripts/derive_form_media_clip.py) preserve original speed using only trim, timestamp reset, and optional still holds. Frozen master hashes and `edits.json` preserve attribution; duplicate destinations fail. Silent H.264 CRF 22 MP4s include fast-start metadata, WebP posters, measurements, and keyframes. Examples, excluding posters: Graphic ankle 281 KB/4 seconds; Graphic Dead Bug 323 KB/4.5 seconds; Studio squat 465 KB/6 seconds; Warm leg press 478 KB/5 seconds. Trimming cannot repair incorrect anatomy.

The four editorial JSON collections tie findings to exact output hashes. Eight additional authored-reference records intentionally have no delivery asset; they remain in the reference registry and review files. Contact sheets and selected full-size phase frames do not certify every intermediate frame. Recorded dashboard checks cover 390 × 844 and desktop layouts, 991-exercise search, hash navigation, comparison, persistence, and preserved review archives. Root played the Graphic Dead Bug trim to completion with no player error, autoplay or loop; the 389 × 844 viewport had no horizontal overflow. External cards show verified duration, orientation, and publisher; the TGU page was manually checked. No tests, builds, lint, type checks, native-device checks, or theme sweeps ran. This local workbench does not establish production detail-page integration or cloud delivery. User decisions and trainer records remain separate.

Start style selection with **Seated Dumbbell Press** and **Barbell Squat**, which have useful candidates in all three looks. The looks compare complete visual treatments; camera, shoes and small equipment details are not perfectly controlled across every render. Keep that limitation separate from color/material preference. Bench contact, alternating limbs and step-down foot identity demonstrate why prompt wording alone is insufficient for form approval.

Round 1’s ten exercise reviews and all 15 earlier assets remain preserved; current saves append to review history. A provisional Codex-only Warm Bench preview selection was explicitly superseded after the independent closer review, without replacing the user’s original feedback. The catalog remains version 2026.09.4, revision 2, with no content/export changes. Next: user style and asset selection, then a deliberately scoped production batch. This pilot does not authorize automatic production for the remaining 971 provisional recommendations.
