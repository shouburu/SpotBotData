# Exercise form media comparison · 4.0

Round 4, 2026-09-15: **Anatomical 3D is pending user review.** Compare five exercises, starting with Lateral Raise. Retain the approved Graphic 3D baseline in [style.md](style.md), accepted exceptions, existing selections and all earlier attempts. A new style comparison does not revoke an approval or make an AI candidate user-accepted.

## Observed reference and scope

The parent production agent inspected the actual [Average to Jacked public post](https://x.com/averagetojacked/status/2098494293195305258). The original direct HLS access failure remains historical evidence; the public post subsequently supplied a viewable reference. The observed six-second cable raise uses a gray/silver anatomical figure with visible muscle contours, orange shoulder accents, dark-gray shorts, a plain white background, a soft ground shadow, gray equipment and a fixed front three-quarter camera. It shows a controlled starting position, raised position and return.

Borrow this visual treatment and clarity. Keep the external source attributed in reference metadata; do not copy its footage or frames into user deliveries, trace its labels, or imply permission to rehost it. Canonical equipment, laterality, Form instructions and repetition counting govern each SpotBot asset. In particular, `ex_lateral_raise` means **bilateral dumbbell lateral raise**, not the reference's cable exercise.

## Reusable visual identity

- Use one solid, realistically proportioned adult anatomical figure with gray/silver surfaces and legible muscle contours. Preserve its identity, proportions, shorts and material across the five examples. The figure should read as a coherent 3D body, not a stick figure, skeleton, segmented toy or reflective chrome statue.
- Use dark-gray shorts, neutral gray apparatus, a plain white background and a soft contact shadow. Keep equipment visually secondary but mechanically intelligible. Avoid a busy gym, decorative scenery, strong reflections or shadows that hide a joint.
- Apply restrained orange **surface color only to reviewed primary-muscle regions** relevant to that exercise. The shoulder treatment is the reference for Lateral Raise. Other exercises need their own catalog-based primary-region choice; do not carry orange shoulders into every movement. Omit a region that cannot be placed confidently on the visible anatomy rather than inventing an exposed deep muscle.
- Color names a teaching category, not measured activation, force or intensity. Keep the same bounded region and color throughout the repetition: no pulsing, heat gradients, moving glow, expanding patches or color sliding across joints. Supporting muscles remain neutral. Explain the illustrated category in adjacent text, never generated lettering inside the image.
- Use no loose markers, arrows, wireframes, numeric joint angles or generated text. Any later guide is a separate, explicitly reviewed design decision; this round's orange treatment belongs to the anatomical surface itself.

Prefer portrait 9:16 when the moving body parts remain large and every endpoint fits. Use landscape 16:9 for the bilateral raise if portrait would shrink the figure or clip either dumbbell. Landscape is also valid when needed for the row's reach or apparatus. A fixed front three-quarter view is the default; choose a clearer side angle when the critical endpoint would otherwise be hidden. Record that deliberate camera difference instead of forcing identical framing across unlike exercises.

## Prompt foundation

Use this shared block with an exercise-specific starting pose, apparatus and motion contract. Record the exact text and version actually submitted.

> Anatomical 3D exercise demonstration. One realistically proportioned adult figure with gray/silver anatomical surfaces and clear muscle contours, dark-gray shorts, neutral gray exercise equipment, plain white background and soft ground contact shadow. Restrained orange surface color only on [reviewed visible primary-muscle regions]; preserve those exact anatomical boundaries and unchanged color throughout. Keep all other body regions neutral gray. Preserve figure identity and equipment geometry. Fixed [reviewed camera angle], steady soft lighting, useful close framing with room for the complete movement path. No generated text, floating markers, arrows, wireframes, glow or activation-intensity effects.

For motion, append the actual sequence: **starting pose → named working endpoint → controlled return to that starting pose**, including the nonmoving body contacts and brief readable holds. Use one complete repetition. The source's six seconds is an observed reference, not a guaranteed provider duration. Choose a supported duration only after its live quote is verified; roughly six to eight seconds of useful delivery is appropriate when it explains the complete cycle. An original-speed trim can remove surplus holds or later partial motion under the existing edit-provenance rules. Never reverse footage or manufacture a return.

## Five comparison samples

| Exercise | Teaching contract and camera priority |
| --- | --- |
| Lateral Raise · `ex_lateral_raise` | Produce first. Begin standing tall with dumbbells beside the body and softly bent elbows; raise both arms out to about shoulder height and lower fully, without shrugging or swinging. Show both shoulder/elbow paths and dumbbells at useful scale. Landscape is permitted. |
| Seated Dumbbell Press · `open_seated_dumbbell_press_b32f5163` | Show the catalog's palms-forward shoulder-height start, press to the stated top position, then controlled return. Keep both grips, elbows, dumbbells, bench support and feet readable. Initial dumbbell setup remains in Form text when the clip starts ready to press. |
| Seated Cable Row · `ex_seated_cable_row` | Show braced feet, softly bent knees, pull toward the lower ribs and controlled forward reach without torso rounding or rocking. Keep handle contact, cable direction and both endpoints visible. |
| Barbell Squat · `ex_squat` | Prefer a standing start, secure upper-back bar position, controlled descent and full standing return. Make depth and whole-foot support readable. Follow comfortable-depth wording; do not turn a mannequin's demonstrated depth into a universal joint-angle requirement. Rack setup remains written guidance. |
| Barbell Deadlift · `ex_deadlift` | Begin with the bar over midfoot and a reviewed floor grip/brace; stand with the bar close to the legs and lower under control to the floor. Show hands, feet, bar/plate contact and both endpoints. Reject a floating start or unsupported equipment. |

Review the exact Lateral Raise still before animating it, then inspect its actual complete motion before extending the treatment to the other four. A successful style frame does not establish a valid movement. Each exercise needs its own inspected starting image and motion evidence.

## Lessons from the first generated comparisons

Prompt version 4.1 adds explicit fine muscle-fiber striations and differentiated superficial muscle grooves; the first smooth mannequin was too generic. Use the reviewed original Lateral Raise take2 still as the appearance anchor, then independently review each new exercise pose. A shared image improves identity and material consistency but can also transfer unwanted shoulder coloring: the side-view row therefore uses an explicit all-gray policy in 4.2. The deadlift also stays gray where shorts cover its catalog primary glutes.

Describe the desired visible endpoint directly (for example, upper arms approximately level with the shoulders or near-straight overhead arms), along with one complete return and no extra pulse. Generated timing can differ from the written windows, so inspect the actual movement. Preserve cosmetic differences such as head crop and shorts length in review notes; do not label a style candidate as user-accepted.

For equipment-dependent poses, use an already reviewed pose image as the first reference and the anatomical appearance image as the second. State explicitly that the first controls contact geometry and headroom, while the second controls materials and identity. The deadlift experiment needed this to resolve floating plates. Keep rack hardware outside the entire squat motion volume; a standing still can look plausible while its rails intersect the body during descent.

Keep production explanations out of generation prompts. Mentioning that a separate Form section identifies muscles caused one video to render a literal “Form” label and leader marker. Store those explanations in the manifest and review notes instead.

## Production and review gates

Use the installed **gflow CLI** through the existing guarded sequential workflow. The cumulative ceiling is **2,000 credits**, with **744 already spent before Round 4**: 1,256 remained at that starting checkpoint. These are historical checkpoint figures; the live ledger, including unresolved reservations, governs every next call. Obtain the exact live offer, reserve before submitting one output, retain provider identifiers, then settle only against observed evidence. Do not assume the reference duration, an earlier offer or a failed command's cost applies to a new call.

Allow at most **three actual generations per defined round/style/shot**. Corrective wording retains the same logical shot identity; do not rename a shot to evade that limit. Apply the existing documented reconciliation rule to a proven refusal before provider submission. Unknown submissions retain their reservation and stop retries. Do not use unsupported end-frame requests; follow the current capability gate.

Record exact prompts, source reference URLs, local reference hashes, attempt and shot IDs, actual costs, delivery measurements and separate AI/user/trainer reviews. Inspect stable anatomy, orange boundaries, meaningful movement, full return, support contacts, equipment continuity and full-frame endpoints. Wrong equipment or laterality, ambiguous endpoints and moving muscle patches are reasons to flag or reject a polished result. Preserve failed outputs and prior user decisions.

Keep the established delivery limits: WebP stills at most 500 KB; silent H.264 720p MP4 with fast-start, targeting 1–2 MB; selected media plus posters at most 5 MB per exercise. Preserve masters and make explicit playback the default. Review useful phone-scale clarity in the existing dashboard, with Form text alongside the media. Automated tests, builds, lint, type checks, native checks and theme sweeps remain deferred. This specification records no new production results or validation outcomes.
