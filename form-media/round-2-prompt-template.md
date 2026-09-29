# Reusable prompt pattern · Round 2

Use the exact catalog movement and counting convention. Combine one style entry from `round-2-style-prompts.json` with an exercise brief. Freeze the expanded prompt and actual reference hashes in the attempt ledger before submission. Model wording and references improve consistency but do not guarantee it; inspect the output.

## Starting image

> Create one instructional starting-frame render of {canonical exercise name}. {style description}
>
> Use the supplied reference for {style identity only OR exact pose/equipment/camera with a material change}. Do not silently carry its old exercise or apparatus into this one.
>
> START: {exact supported position, equipment, grip, joint arrangement and floor contacts}. This is {specific point in the cycle}, not {the commonly confused variant, only when needed}.
>
> CAMERA: fixed {view and height}, {aspect}. Frame for the FULL MOVEMENT ENVELOPE: {furthest hand, foot, head and equipment endpoints}. In this compact starting pose, {explicit space that must remain free for the later phase}. Keep {the key teaching joints/contacts} clearly distinguishable. Omit unrelated machine structure and scenery.
>
> Keep ordinary adult anatomy, stable equipment and clear surfaces. No text, arrows, body markers, muscle maps, split panels or decorative objects.

The movement envelope is the maximum extent through the entire repetition. “Fill the frame” alone tends to make the generator fill it with a bent or compact starting pose. For Dead Bug, the portrait mat must include the projected extended fingertips and toes. For a floor-start Deadlift, the crouched starting frame must leave space for the full standing head height. For ankle pointing, the raised forefoot needs space in the direction it will rotate.

## Motion

> Create a clear instructional demonstration of {canonical exercise name} from the supplied starting frame. Preserve that exact {style} figure, body proportions, clothes, equipment, lighting and framing. Keep the camera fixed throughout.
>
> Show {complete movement sequence} in {supported duration} seconds, including {readable start hold, endpoint and complete return}. Preserve {specific contacts, grip, apparatus path and stationary body regions}. {Laterality and exact repetition convention when relevant.}
>
> Keep every relevant joint and the complete movement path visible. Maintain stable anatomy and rigid equipment. No cuts, zoom, camera movement, generated text, arrows, muscle coloring, speech or music. Do not reverse footage to create the return.

Use eight seconds for a simple complete repetition; ten seconds for two clearly separated diagonal or alternating actions when needed. Do not shorten a complex sequence until phases disappear. Strip generated audio from delivery files even when the prompt requested silence.

## Corrective style transfer

> Restyle the supplied {exercise} reference into {new style}. Preserve its exact pose, body proportions, supported contacts, equipment and camera. Keep {screen direction and crucial visible endpoint}. Change only {materials, clothing colors, contour/shading treatment}. Do not mirror or reframe the scene, add apparatus, or change the exercise.

Prefer the clearest existing view of the same exercise as the reference for a corrective style comparison. Using only a global style anchor can produce different shoes, camera positions or machine designs; those are complete treatment comparisons, not controlled palette comparisons. The actual supplied reference, rather than an assumed visual identity, is recorded per attempt.

## Review gates

A starting frame is ready to animate only after its exact bytes have been checked for pose, apparatus and full movement room. A pleasing image that begins at the wrong phase or implies a different machine route is not a suitable seed. Motion requires its own editorial review for phase order, stable contacts, complete return and visible endpoints. Passing the still review does not establish correct movement.

Preserve a rejected candidate and its reason. Revise the smallest relevant instruction, increment the prompt version, retain the same logical shot ID, and submit the corrective attempt explicitly. The three-attempt limit and cumulative credit ceiling remain in force. Never resubmit an uncertain job before reconciliation.

When restyling an equipment-free exercise, remove generic equipment language from the style fragment. Even a phrase such as “clean charcoal equipment” can add an unrelated machine. Preserve the exact valid pose when correcting framing; changing pose, camera orientation and materials together can lose correct suspended limb positions.
