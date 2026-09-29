# Round 3 · Graphic 3D refinements

Seven revised Graphic 3D videos are ready for operator review in the [local workbench](http://127.0.0.1:8766/#ex_squat). Machine Chest Press and Overhead Press remain held for unclear arm endpoints. New AI candidates are **pending**, not user-approved. The ten carried choices retain the user's earlier decisions, including Round 1 Plank, Outdoor Walking text and the accepted expert references.

The active catalog and dashboard now contain **879 exercises**: 112 range-of-motion and non-yoga stretching entries were removed, and all 39 yoga identities were preserved. The pilot contains 19 retained exercises after Ankle Pump's removal. Catalog version is 2026.09.6, revision 4, with 21 starters. Exclusion IDs prevent retired source exercises from returning through older releases. Personal and historical records remain protected. Source-owned cloud cleanup removed six withdrawn starters and updated one Pilates starter; there were no global exercise rows to delete. Standard-catalog API deployment/publication remains separate.

## Revised review choices

Sizes include the local poster. All movement deliveries are silent H.264 MP4 at 720p with fast-start metadata.

| Exercise | Suggested media | Duration | Package |
|---|---|---:|---:|
| Treadmill Walking | Graphic 3D walking pattern; setup and stopping stay in Form | 8 s | 1.22 MB |
| Lat Pulldown | Starts lowered, releases overhead, then pulls toward the upper chest | 6.25 s | 558 KB |
| Leg Press | One supported sled cycle | 5.25 s | 539 KB |
| Seated Cable Row | True side view, pull to lower ribs and controlled return | 5.5 s | 453 KB |
| Low Step-Up | Explicit **ascent detail**, with descent and counting in Form | 8 s | 680 KB |
| Barbell Deadlift | Floor lift and controlled floor return, alongside the accepted CrossFit reference | 8 s | 675 KB |
| Barbell Squat | Starts at demonstrated depth, rises upright, then lowers again | 6.5 s | 532 KB |

The squat shows greater depth than the prior option. It does not establish a measured parallel target; canonical guidance remains comfortable individual depth. Lat, Leg Press, Row and Squat use separately reviewed original-speed edits to remove extra generated tail motion. Their actual return phases are preserved, with brief still holds. No footage was reversed to invent movement.

Overhead Press includes the requested **0–6-second Porcelain edit**, with no added holds, at 491 KB including its poster. It remains a comparison while the Graphic replacement is held. Both Graphic motion attempts leave the far elbow unclear. Three still attempts included an unchanged bent elbow and a frontal image with unwanted generated text. Machine Chest Press also failed to establish a readable extended endpoint after three still attempts; its earlier motion stays flagged. A trim would not resolve either missing endpoint, so no further generation is queued automatically.

All historical takes remain available under earlier attempts and round comparison. No new body markers, speculative muscle maps or stick-figure animations were introduced.

## Credits and retained assets

This round spent **156 credits**: 13 video generations at a verified 12 credits each, and 18 still generations with verified zero-credit quotes and unchanged balances. Five authored edits spent no generation credits. One additional CLI invocation was refused before provider submission and reconciled at zero. It remains in the ledger with hash-linked source and balance evidence.

The cumulative pilot total is **744 / 1,000 credits**, with **256 remaining and zero reserved**. All 36 new assets have exact-output AI editorial records. New masters occupy 27.08 MB; all new delivery alternatives and posters occupy 12.45 MB. The currently selected local packages across the 19 exercises total 6.22 MB; the largest is 1.22 MB, below the 5 MB per-exercise ceiling. These selected packages include provisional choices and are not a published library. YouTube-hosted bytes are excluded from local package totals. Exact figures and IDs are in [round-3-metrics.json](round-3-metrics.json).

## YouTube inside Form

The app now embeds the six approved YouTube references for Bench Press, Deadlift, Clean and Jerk, Turkish Get-Up, Dead Bug and Walking Lunge. Loading and playback are explicit; publisher controls, attribution and an external fallback remain available. Portrait sources keep their portrait layout. Bench and Deadlift retain the selected excerpt timestamps. Third-party videos are not downloaded or rehosted.

Manual web playback confirmed the Bench excerpt stops at its requested end, the portrait Clean and Jerk plays inside Form, and switching away from Form unloads playback. The local dashboard also loads official YouTube embeds, closes them cleanly and preserves saved feedback across refresh. The new Deadlift MP4 played to its eight-second end and the selected Squat edit played to its 6.5-second end, without media errors, autoplay or looping. Phone and wider layout checks found no horizontal overflow. Native implementation includes a fallback for older clients missing the new WebView module, but **native playback requires a rebuilt client and an explicitly selected device checkpoint**. Universal exercise-title links remain separate navigation work; existing workout Form actions already preserve active set drafts.

## Workflow lessons and resume point

Graphic 3D is now the [shared standard](style.md). Exact pose references, clear camera views and independent motion review matter more than repeated style wording. Anchoring the missing lowered/depth pose helped Lat and Squat. A matching-looking starting image does not establish the middle or return phases.

The installed gflow 0.72.0 help advertises end-frame support, but its driver for this account's migrated `flow.google.com` frontend explicitly refuses that option before upload or submission. The account offers a first/last model price, which does not prove CLI support. The [reconciled refusal evidence](round-3-lat-end-frame-refusal-evidence.json) records that distinction. Current jobs use supported single-start mode; a capability gate blocks end-frame attempts before pricing. No manual Flow website navigation or password prompt was needed for these CLI operations.

The queue preserves prompt versions, reference hashes, quote evidence, source masters, rejected attempts and user history. An explicit reference-attempt pin can reuse an earlier valid pose after later stills fail. A resume cannot relabel an older completed render with a newer prompt's phase description. Confirmed pre-submit refusals are excluded from the three-generation limit only with exact attempt-bound evidence and an unchanged numeric account balance; uncertain failures remain counted and reserved.

Next: review the seven Graphic replacements and the two held exercises in the workbench. Generated binary hosting and app ingestion remain unprovisioned. Automated tests, builds, lint/type checks, native/device verification and theme sweeps were not run and remain deferred under the repository workflow.
