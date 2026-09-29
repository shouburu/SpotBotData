# Exercise form media standard · 1.0

This is the shared visual and editorial contract for the exercise-media pilot. It belongs to content operators and asset reviewers. The catalog remains the source of movement identity, apparatus, instructions, laterality and primary/secondary muscles. Media demonstrates that exact exercise; it does not silently substitute an easier variation or override its instructions.

## Choose the simplest sufficient medium

Use text for familiar actions that need only brief setup and pacing cues. Use a still for a held posture, support arrangement or alignment relationship. Use a small authored animation for a clearly bounded movement that a geometric schematic can explain accurately. Use generated video when coordination, several moving joints or equipment contact materially improves understanding. Use an external expert reference when a short generated demonstration omits necessary phases or repeatedly fails review.

Every exercise retains readable Form instructions. A video is not required merely because the exercise has no video yet. The all-catalog recommendations are provisional production candidates, not a batch generation queue. The ten pilot choices test the boundaries between media types.

## Generated mannequin identity

- One gender-neutral adult mannequin with ordinary athletic proportions, a smooth featureless face, matte medium cool-gray surface, charcoal fitted sleeveless top and shorts. Keep the same build, proportions, clothes and material across shots. No idealized extreme musculature.
- Pale warm-gray seamless studio and flat floor, with soft directional studio lighting and restrained contact shadows. Equipment is simple, physically plausible and easy to distinguish from the body. No decorated gym, props, dramatic strain or advertising composition.
- A locked camera with little perspective distortion. Show the entire movement and all relevant contacts at phone size; keep about ten percent framing margin around the needed motion. Choose the view that makes the specific form question visible, rather than using one universal camera angle.
- Landscape 16:9 for Bench Press and Dead Bug; landscape 4:3 for Plank; portrait 9:16 for Mountain Pose. These are generation aspects supported by gflow 0.72.0 on the migrated Flow frontend; its CLI advertises 3:4 but that path is not ported. Do not stretch an output to fit a different aspect.
- No baked text, numbers, arrows, guide lines, skeletons, muscle colors, logos, watermarks added by the prompt, music or speech. Keep overlays separately editable. Do not remove provider provenance or watermarks that appear in delivered outputs.

Start from one accepted identity reference when the provider supports it. Passing the same text prompt helps but does not guarantee identity consistency. Save the actual reference asset IDs with each attempt; reuse an accepted starting frame for motion whenever possible. Reject anatomy or equipment defects before spending credits to animate that frame.

## Motion and framing

Each generated clip explains a complete, controlled action, with a short starting hold and a matching final hold. Preserve stable contacts, body proportions, apparatus, grip and camera throughout. Movements should be slow enough to inspect and should not imply maximal effort or a mandatory joint angle.

The Bench Press brief asks for one eight-second lower-and-press cycle, with a separate overhead still for arm position. The Dead Bug pilot attempted a ten-second two-sided sequence, including both returns, and then a simpler eight-second single-diagonal shot. All motion attempts failed form review; the current selected fallback is a setup still with catalog text. In that exercise, each diagonal extension-and-return counts as one repetition; a valid two-sided clip would show two repetitions. Do not accept repeated same-side motion as an alternating demonstration. A generator's actual supported duration takes precedence over a requested number in prompt text: record the real duration, revise the brief explicitly when needed, and never accept a truncated return just to meet a size target.

Bench side video demonstrates the repetition after unracking. The text retains rack setup, safeties and reracking instructions. Do not claim the short clip covers those omitted actions. Advanced multi-phase movements in the pilot use linked expert references instead of compression into an incomplete loop.

## Separate guides and muscle involvement

Use primary orange `#F58A38` and supporting blue `#61A7ED`, always with text labels. Alignment lines are white with dark joint markers. When the catalog lists only full body (Mountain Pose), use an alignment guide and the full-body text rather than inventing a localized muscle map.

Use deterministic overlays or adjacent diagrams for the information that must remain correct: alignment guides, path arrows, named muscles and primary/secondary muscle colors. A primary/secondary legend communicates the catalog's muscle categories; it does not represent measured activation percentages or fatigue. Do not reuse the app's fatigue scale for this meaning.

Overlays must be aligned to the accepted asset and reviewed after any crop or asset change. Keep labels readable on a phone, use words as well as color, and show no more than the one or two guides needed for the shot's teaching purpose. For Bench Press, an overhead still can explain arm position while the side clip explains bar travel. Avoid numeric angles without exercise-specific supporting evidence.

The ankle-pump and calf-raise pilots are deliberately different: crisp SVG geometry, muted green motion emphasis, visible ground contact, and plain phase labels. They are motion schematics, not generated anatomical figures. Their range and proportions are illustrative. Both start paused, provide Play/Pause, Restart and scrubbing, and stop when hidden or scrolled out of view. Reduced-motion users keep a useful static starting pose and can choose to inspect motion themselves.

## Review and credit discipline

An asset starts `pending`. `accepted` records an operator's content review, not independent professional validation. `rejected` means the asset should not be selected; `needs-review` records unresolved questions. `recommendationStatus: pilot-reviewed` only means the proposed medium was considered for this pilot; it never approves the resulting instruction or image.

Review each candidate against the canonical instructions and the following criteria before selecting it:

1. Exact movement, equipment, supported position, side/counting rule and visible phases match the exercise.
2. Anatomy remains plausible. Hands, feet and apparatus have stable contact. No extra limbs, changed grips, clipping, floating supports or impossible joint transitions.
3. The key form question is visibly answered. Cropping, perspective, clothing or an overlay does not hide it.
4. The style reference remains consistent; the image is clear at phone display size and the clip has no abrupt cut or missing return.
5. Text, alternative text and a static fallback remain sufficient when motion is paused or media is unavailable. Source and usage rights are recorded accurately.

Record a specific rejection reason before another attempt. Change the smallest relevant prompt clause or starting frame instead of rewriting the whole style. Keep every attempt, including unsuccessful and uncertain ones, in the durable credit ledger. The pilot ceiling is 1,000 credits; it is a ceiling, not a spending target. Use the verified quote for the actual model and options. Never silently retry a possibly submitted job. Do not regenerate an accepted selected asset as a side effect of opening the dashboard.

The pilot settles the look and teaching value before mass production or app integration. Original generation, review and later publication are separate states. Nothing in this standard authorizes publishing draft assets or adding them to the standard catalog.
