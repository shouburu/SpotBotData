# Round 3: apply the selected Graphic 3D standard

The latest reviews choose Graphic 3D for generated motion. This bounded plan creates nine revised exercise examples: eighteen logical shots, comprising one starting still and one eight-second motion per exercise. It adds no exercise and spends nothing on Ankle Pump, rejected outdoor walking media, or another incomplete Dead Bug sequence.

At the last recorded rates, the first pass is approximately 108 credits (nine videos at 12 credits, nine reference stills at zero). With 588 cumulative credits already spent, that would bring the total to 696, leaving 304 for explicitly reviewed corrections. These are planning estimates, not current quotes. The existing live-quote, reservation, settlement and cumulative 1,000-credit controls remain authoritative. Each shot permits at most two corrective regenerations, only after inspecting the prior result.

| Exercise | Revision | Coverage |
| --- | --- | --- |
| Lat Pulldown | Preserve the approved Studio movement in Graphic 3D | One front pull and overhead return |
| Treadmill Walking | Preserve the approved Studio walking phase in Graphic 3D | Steady walking, with setup/stopping in text |
| Leg Press | Preserve the successful fixed-seat sled setup, change style | One controlled sled lowering and press |
| Low Step-Up | Convert the useful ascent detail to Graphic 3D | Ascent only; descent and counting remain explicit in Form |
| Machine Chest Press | Center the person and both hand paths | One upper-body press and return |
| Seated Cable Row | True side profile as requested | One row to lower ribs and forward return |
| Overhead Press | Graphic replacement plus the exact requested Studio 0–6-second edit | One press and return; quiet finish |
| Barbell Deadlift | New conventional setup with full-size grounded plates; preserve excellent real reference | One floor lift and controlled return if verified |
| Barbell Squat | Clear side view and a fuller controlled example depth | One squat and return; comfortable depth remains the instruction |

## Decisions that need no generation

- Restore `plank-v1` for Plank because the user explicitly selected Round 1 in their latest note. Preserve its old review, source and overlay provenance rather than silently recoloring it.
- Use text for Outdoor Walking exactly as requested; do not keep rejected generated motion as its default.
- Keep the accepted expert Dead Bug reference. The user rejected a generated demonstration that covers only half the alternation.
- Keep accepted Graphic 3D Seated Dumbbell Press, Standing Calf Raise and Mountain Pose.
- Preserve the accepted short references for Bench, Clean and Jerk, Turkish Get-Up, Walking Lunge and Deadlift. An additional Deadlift render is supplementary and needs its own review.
- Remove Ankle Pump and the user-selected range-of-motion drills and stretching entries, retaining yoga before new generation. Historical spending, outputs and reviews remain durable records.

## Reference and prompt ownership

`round-3-jobs.json` holds the exact canonical Form text, correction rationale, framing and motion review gates for each shot. Its still jobs use `referenceFiles` with pinned SHA-256 hashes and roles. Image 1 is the accepted Graphic 3D squat starting still and anchors the mannequin identity, navy kit, ivory body, shoes and rendering treatment. Where a successful setup can be preserved, image 2 supplies only that exercise's pose, equipment and composition. Old flawed deadlift stills are deliberately excluded.

Every motion references its own newly inspected Round 3 start via `referenceShot`. No motion should proceed without a `ready-to-animate` review matching that exact still's bytes. A timeline is a generation request, not proof that the output followed it. Review complete motion and endpoint frames, then isolate a genuine useful cycle with an original-speed edit when necessary. Record a missing phase honestly; never reverse footage or interpolate a fictitious return.

The approved Step-Up ascent has deliberately limited coverage. Its new prompt finishes standing with both feet on the box and does not request another failed descent. The visible title must say **Ascent detail only**, and adjacent Form retains the trailing-foot-first descent and full ascent-plus-descent repetition convention.

## Squat depth check

The user-approved Graphic video `r2-squat-illustrated-motion-4e311c44` is visually shallow. The existing contact sheet and the full-size four-second bottom frame show the near thigh still sloping upward substantially toward the hip. The camera is oblique and a rack safety arm overlaps the hip, so exact joint angles or a precise hip-crease depth cannot be measured reliably from it.

The catalog says “comfortable depth,” so the current clip does not establish a categorical form violation or a universal safety problem. It does make a weak generic depth example. [NSCA's exercise description](https://www.nsca.com/education/articles/kinetic-select/anaerobic-and-muscle-endurance-development/) uses thighs parallel as a demonstration, while [NSCA's discussion of individual biomechanics](https://www.nsca.com/education/articles/ptq/a-coach-and-trainers-challenge-individual-variables-in-health-fitness-and-nutrition/) explains why hip structure affects achievable squat depth. These sources support an approximately thigh-parallel **example** while retaining person-specific comfortable-depth guidance; they do not justify demanding an extreme deep crouch from every user.

A new true side view will expose the near hip and knee without a rack arm covering them. Its prompt requests approximately thigh-parallel depth for this mannequin with grounded shoes, a controlled trunk and natural torso inclination. The replacement must be rejected if it obtains apparent depth through heel lift, pelvic collapse, equipment intersection or unstable anatomy. Preserve the user's accepted original and note; the new option is an editorial improvement for the specific depth concern.

AI source/frame review is separate from trainer review. No automated tests, builds, lint/type checks, native verification or theme sweep were run for this planning work.

## Starting-frame corrections, version 3.1

The first Cable Row image achieved the true side camera but bent the knees close to a right angle. Its next prompt keeps the camera and moves the braced footplates forward to show gently unlocked legs with complete sole contacts.

The first Deadlift image copied a hanging bar and floating plates despite the floor-setup text. The corrective still deliberately uses **text-to-image without a pose/style reference**: it establishes full-diameter grounded plates first, then places the adult at the fixed floor shaft. The full Graphic 3D appearance remains explicit in the prompt. This bounded exception avoids anchoring the incorrect standing-bar geometry. Correct pose/contact takes priority; a later style-only correction is possible only if required.

The first Squat image repeated the old oblique camera. Its next prompt uses the already reviewed Round 3 Graphic Lat Pulldown only as an identity reference and explicitly permits natural far-side occlusion in a true side view. It keeps rack hardware out of the near hip/knee silhouette; this movement detail begins after unracking, and rack safety setup remains in adjacent Form. All original images, exact-hash reviews and frozen attempt prompts remain retained.
