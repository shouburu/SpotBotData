# Round 2 exercise content

The ten new exercises in [round-2-exercise-briefs.json](round-2-exercise-briefs.json) join the original ten pilots for twenty total. All ten additions are distinct canonical compound exercises: five seated and five standing. The briefs use `catalog.json` release 2026.09.4, revision 2, and preserve the selected movement, apparatus, sequence and repetition contract. Their pending status means the brief is ready for production consideration; generated media still needs review.

| Position | New exercise | Canonical ID | Main visual question |
| --- | --- | --- | --- |
| Seated | Seated Dumbbell Press | `open_seated_dumbbell_press_b32f5163` | Both free weights travel overhead and return to shoulder height with back support. |
| Seated | Seated Cable Row | `ex_seated_cable_row` | The handle reaches the lower ribs while the torso stays steady. |
| Seated | Lat Pulldown | `ex_lat_pulldown` | The bar travels in front toward the upper chest with the thighs secured. |
| Seated | Leg Press | `ex_leg_press` | The knees bend while the feet and lower back retain support. |
| Seated | Machine Chest Press | `ex_machine_chest_press` | Chest-height handles move forward and return with the back supported. |
| Standing | Barbell Squat | `ex_squat` | Hips and knees bend together over grounded feet. |
| Standing | Barbell Deadlift | `ex_deadlift` | The bar stays close to the legs from floor start through standing and return. |
| Standing | Overhead Press | `ex_overhead_press` | The bar clears the head without leg drive or a backward lean. |
| Standing | Walking Lunge | `ex_lunge` | Forward travel and alternating lead legs remain visibly continuous. |
| Standing | Low Step-Up | `cat_cal_low_stepup` | Both feet reach the box before the trailing foot descends first. |

## Apply the user's review notes

The Bench feedback asks for more options and a closer view of the moving body parts. Use tight, fixed framing around the actual movement and its necessary support contacts. A full machine, rack or wide room is not a reason to shrink the body. A setup still can preserve context while the motion shot concentrates on the relevant joints. Camera and framing recommendations are specific to each brief.

The three planned styles are Porcelain Studio, Warm Ceramic and Graphic 3D. All use a volumetric figure. The rejected ankle/calf schematics are not a template for new content. Compare styles with consistent pose and camera where possible; otherwise a clearer camera can be mistaken for a preferred rendering style. The rejected Mountain guides also show why alignment markers must never be added without checking the actual body orientation. Keep new generated frames free of markers.

Outdoor Walking's text and Plank's image are accepted user choices to preserve. Treadmill Walking now needs a short posture-focused video. Dead Bug needs a reference-led motion revision; the user supplied a specific short demonstration, which the research workstream is reviewing. External references should show the exercise directly in short-form content, ideally under one minute. Rejected long references and incorrect generated movement remain useful rejection evidence, not selected instruction.

## Sequence and counting boundaries

- Walking Lunge: each completed forward lunge step is one repetition, and the entered number is the total across both legs. The proposed two-step alternating demonstration shows two repetitions. It advances across the frame; do not force a seamless reset by teleporting, walking backward or changing it into a stationary split squat.
- Low Step-Up: one ascent and descent is one repetition, and the target applies to each lead leg. Both feet must reach the top; the trailing foot steps down first. A single-lead clip does not demonstrate both sides.
- The other eight additions use one bilateral repetition per controlled cycle. Do not count the two hands or legs separately.
- Seated Dumbbell Press explicitly uses a supported bench and palms facing forward. Its catalog wording asks the dumbbells to meet at the top; preserve that gentle endpoint without fusing the weights or substituting an Arnold press. The thigh-assisted setup can stay in text while the clip starts at shoulder height.
- Leg Press and Machine Chest Press describe generic machine categories. Choose a coherent ordinary machine as the visual example, without turning its rail angle, linkage or grip into a universal requirement. Do not substitute the separate Smith vertical leg-press exercise.
- Rack setup, safeties, seat adjustment, unracking and reracking remain in the Form instructions when a short clip only demonstrates the repetition. Do not claim that a single repetition covers the complete setup procedure.

The briefs propose eight seconds for most cycles and ten for the travelling lunge and step-up sequences. These are production suggestions, not permission to spend credits or evidence that the provider delivered those durations. Prefer a complete, correct action over a truncated clip. Starting frames should resolve support, grip and framing before paid motion; motion then needs its own review for path, contact continuity and the complete return.

## Editorial evidence

[round-2-editorial-reviews.json](round-2-editorial-reviews.json) is an append-only log of independent AI reviews bound to an exact output path and SHA-256. `ready-to-animate` means the reviewed starting frame can be used for a motion attempt; it does not mean the user accepted the style, a trainer verified the form, or the resulting video is correct. Reviews must describe specific observed evidence and limitations. Keep the user's review state in the manifest separate.

Each exercise brief also records a SHA-256 of its complete canonical record, serialized as sorted-key compact UTF-8 JSON. That fingerprint helps identify source changes before a future production round. No catalog records, default prescriptions or published snapshots are changed by these briefs. This work is content authoring and focused editorial review; no automated tests, builds, lint or native verification were run.
