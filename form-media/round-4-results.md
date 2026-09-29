# Round 4 · Anatomical 3D comparison results

Five eight-second clips are ready in the [local workbench](http://127.0.0.1:8766/#ex_lateral_raise). These are **selected for comparison by production review, not selected or accepted by the user**. Their exact files have AI candidate reviews; all five user content statuses remain pending. The approved Graphic 3D baseline and earlier selections are preserved.

The treatment follows the inspected [reference post](https://x.com/averagetojacked/status/2098494293195305258): gray/silver anatomy, muscle contours, dark shorts, white background, gray apparatus and a fixed camera. Orange illustrates a primary-muscle category, never measured activation intensity. Lateral Raise uses bilateral dumbbells rather than the reference's cable variant. No third-party footage was copied or rehosted.

## Comparison files and sizes

Every MP4 is silent, fast-start H.264. Lateral Raise and Row are 1280 × 720 landscape; Press, Squat and Deadlift are 720 × 1280 portrait. Package bytes include one video and its WebP poster, excluding older alternatives and source masters. Manifest sizes match the actual files, and the five video hashes match their recorded delivery hashes.

| Exercise / video | Duration | Video bytes | Poster bytes | Package bytes |
| --- | ---: | ---: | ---: | ---: |
| [Lateral Raise · take 2](assets/delivery/round-4/r4-lateral-raise-anatomical-motion-66a6b920.mp4) | 8 s | 799,298 | [28,634](assets/delivery/round-4/r4-lateral-raise-anatomical-motion-66a6b920-poster.webp) | **827,932** |
| [Seated Dumbbell Press](assets/delivery/round-4/r4-seated-db-press-anatomical-motion-de3c3b17.mp4) | 8 s | 621,980 | [35,902](assets/delivery/round-4/r4-seated-db-press-anatomical-motion-de3c3b17-poster.webp) | **657,882** |
| [Seated Cable Row · take 2](assets/delivery/round-4/r4-cable-row-anatomical-motion-81725360.mp4) | 8 s | 442,874 | [21,896](assets/delivery/round-4/r4-cable-row-anatomical-motion-81725360-poster.webp) | **464,770** |
| [Barbell Squat · take 2](assets/delivery/round-4/r4-squat-anatomical-motion-c5d6dea2.mp4) | 8 s | 770,107 | [31,124](assets/delivery/round-4/r4-squat-anatomical-motion-c5d6dea2-poster.webp) | **801,231** |
| [Barbell Deadlift](assets/delivery/round-4/r4-deadlift-anatomical-motion-5bcc600b.mp4) | 8 s | 760,643 | [22,314](assets/delivery/round-4/r4-deadlift-anatomical-motion-5bcc600b-poster.webp) | **782,957** |
| **Total** | **40 s** | **3,394,902** | **139,870** | **3,534,772** |

The comparison package is **3.53 MB** in decimal units. Every exercise package is below 1 MB and the existing 5 MB ceiling. These are local delivery sizes, not a published app library.

## Teaching evidence and limitations

- **Lateral Raise:** approximately shoulder-height bilateral raise and full lowered return, with both weights visible and shoulder color attached in inspected phases. The head top is slightly cropped; feet are outside the deliberate upper-body view. The quiet finish is longer than prompted. No exact joint angle is established.
- **Seated Dumbbell Press:** supported press through nearly straight overhead arms and return, with distinct dumbbells and stable bench/foot support. Their inner ends **do not visibly meet**, although the catalog requests contact. Keep this mismatch explicit. Shorts are shorter than the shared appearance reference.
- **Seated Cable Row:** lower-rib pull and full forward return with coherent feet, hips and cable contact. A small trunk-angle change remains; inspected frames show no large assisting swing. The occluded upper-back surface is left gray, with muscle involvement in adjacent text. The pulley is simplified.
- **Barbell Squat:** standing start, meaningful hip/knee flexion, grounded feet and full standing return without rack interference. Thighs remain **somewhat above horizontal**, missing the requested prompt depth target. This is a comfortable-depth comparison, not a parallel-depth example, and does not automatically replace the accepted deeper option.
- **Barbell Deadlift:** grounded floor lift, standing hold and controlled floor return. Both plate rims contact the floor around 7.3 seconds and remain grounded through the inspected 7.95-second frame. Keep all eight seconds; a seven-second trim could omit the return. Exact midfoot distance, bracing and joint angles cannot be certified from the render.

Exact evidence remains in [starting-frame reviews](round-4-start-independent-reviews.json) and [delivery/editorial reviews](round-4-editorial-reviews.json), with current records synced to the [manifest](manifest.json). AI editorial inspection is separate from user acceptance and trainer review.

## Credits and prompt lessons

All **18 attempts settled**: **10 images at 0 credits** and **8 videos at 12 credits**, totaling **96 credits**. Cumulative pilot spend is **840 / 2,000**, with **1,160 remaining and zero reserved**. The observed account balance moved **9,336 → 9,240**. Provider balance and the local allowance are separate; [attempts.json](attempts.json) retains the exact settlements.

Five motions are current candidates; three earlier versions remain `needs-correction`: Lateral Raise stopped low and added a partial tail, Row generated a label/marker, and Squat was shallow with rack overlap. These are AI findings, not user rejection records. All source images and alternatives remain. No logical shot exceeded three generations; Squat used all three starting-image attempts.

Closer Lateral Raise framing established useful muscle detail after the first distant, smooth figure. Explicit endpoint wording improved the raise, although actual timing differed from the requested phases. Preserve the full weight path at a useful viewing scale.

Appearance references can transfer unwanted features: Row inherited orange deltoids. Removing color avoided inventing visible back anatomy. Keep application instructions outside generation prompts: mentioning the adjacent Form section caused rendered text and a marker. Removing that context produced an unannotated correction.

Review the whole motion volume. Squat's first animation exposed a rail entering the body despite an initially acceptable still. Removing the rack resolved interference but did not guarantee depth. Motion findings can supersede a starting-frame gate.

Deadlift's first still floated the plates. Reusing a reviewed grounded pose as the first reference and the new appearance as the second restored floor contact. Preserve reference roles and hashes; a style reference alone does not supply a valid pose.

## Working route and manual evidence

All generation used **gflow CLI**. Legacy pricing/credit APIs still returned 401. Explicit `--ui-quote-file` evidence supplied fresh, exact-setting quotes and same-account balances; the browser only read these observations. The runner froze evidence, reserved cost, submitted through gflow and held output until fresh post-balance reconciliation. [Production notes](round-4-production-notes.md#resume-procedure) describe resuming without cached prices or another unrecognized-login loop.

[Manual review evidence](round-4-manual-review.json) records all five dashboard HTML videos ending normally at eight seconds without media errors, readable Form/media at **390 × 844 CSS pixels** with no horizontal document overflow, and a **1600 × 900** wider view. Refresh retained history and prior selections; no user decision was submitted and the Round 3 snapshot hash is unchanged. An initial preview tab crashed; a fresh tab played successfully. No deliberate media failure was injected.

These are manual browser observations, not native app or trainer verification. Automated tests, builds, lint/type checks, native/device verification and theme sweeps remain deferred. Generated-binary hosting and app ingestion were not changed. The next action is user comparison of these five options and their limitations.
