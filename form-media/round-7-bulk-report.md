# Round 7 initial bulk pass

Generated 30 videos across 20 exercises, plus 52 reference images across 30 exercises. One additional video was derived by trimming a complete source repetition.

7 exercises have AI editorial candidates. Other outputs are retained with correction notes; none were automatically approved. The larger 413-exercise production queue remains incomplete.

This round spent 324 credits. Cumulative spend is 1548 / 10000, with zero reserved and 8452 remaining.

Five or six outputs reached download in about 62 seconds per measured group; excludes cleanup, encoding, reconciliation and editorial review. Not a verified 10x end-to-end improvement.

CLI still launches internal browser sessions per job. No browser-free endpoint or warm browser pool implemented.

Six workers were demonstrated; four remain active after two pre-submission editor-access failures. Both failures were reconciled at zero credits. No generation remains running.

## Exercise results

| Exercise | Status | Candidate asset |
|---|---|---|
| [ex_barbell_row](http://127.0.0.1:8766/#ex_barbell_row) | ready-for-review | r7-barbell-row-complete-cycle |
| [ex_shrugs](http://127.0.0.1:8766/#ex_shrugs) | needs-correction | See failed outputs and AI notes |
| [ex_close_grip_bench](http://127.0.0.1:8766/#ex_close_grip_bench) | ready-for-review | r6-ex-close-grip-bench-motion-da49156a |
| [ex_front_raise](http://127.0.0.1:8766/#ex_front_raise) | needs-correction | See failed outputs and AI notes |
| [ex_preacher_curl](http://127.0.0.1:8766/#ex_preacher_curl) | ready-for-review | r6-ex-preacher-curl-motion-60e82673 |
| [ex_reverse_pec_deck](http://127.0.0.1:8766/#ex_reverse_pec_deck) | needs-correction | See failed outputs and AI notes |
| [ex_calf_raise_seated](http://127.0.0.1:8766/#ex_calf_raise_seated) | needs-correction | See failed outputs and AI notes |
| [ex_straight_arm_pulldown](http://127.0.0.1:8766/#ex_straight_arm_pulldown) | needs-correction | See failed outputs and AI notes |
| [ex_dumbbell_fly](http://127.0.0.1:8766/#ex_dumbbell_fly) | needs-correction | See failed outputs and AI notes |
| [ex_pec_deck](http://127.0.0.1:8766/#ex_pec_deck) | needs-correction | See failed outputs and AI notes |
| [ex_cable_fly](http://127.0.0.1:8766/#ex_cable_fly) | needs-correction | See failed outputs and AI notes |
| [ex_dumbbell_curl](http://127.0.0.1:8766/#ex_dumbbell_curl) | ready-for-review | r6-ex-dumbbell-curl-motion-4bccd9b9 |
| [ex_arnold_press](http://127.0.0.1:8766/#ex_arnold_press) | needs-correction | See failed outputs and AI notes |
| [ex_cable_curl](http://127.0.0.1:8766/#ex_cable_curl) | ready-for-review | r6-ex-cable-curl-motion-9f87b5a6 |
| [ex_cable_crunch](http://127.0.0.1:8766/#ex_cable_crunch) | needs-correction | See failed outputs and AI notes |
| [ex_cable_lateral_raise](http://127.0.0.1:8766/#ex_cable_lateral_raise) | needs-correction | See failed outputs and AI notes |
| [ex_concentration_curl](http://127.0.0.1:8766/#ex_concentration_curl) | needs-correction | See failed outputs and AI notes |
| [ex_decline_bench_press](http://127.0.0.1:8766/#ex_decline_bench_press) | needs-correction | See failed outputs and AI notes |
| [ex_pullover](http://127.0.0.1:8766/#ex_pullover) | needs-correction | See failed outputs and AI notes |
| [ex_dumbbell_shoulder_press](http://127.0.0.1:8766/#ex_dumbbell_shoulder_press) | needs-correction | See failed outputs and AI notes |
| [ex_tricep_kickback](http://127.0.0.1:8766/#ex_tricep_kickback) | needs-correction | See failed outputs and AI notes |
| [ex_face_pull](http://127.0.0.1:8766/#ex_face_pull) | ready-for-review | r6-ex-face-pull-motion-cdc90c31 |
| [ex_front_squat](http://127.0.0.1:8766/#ex_front_squat) | needs-correction | See failed outputs and AI notes |
| [ex_overhead_tricep_extension](http://127.0.0.1:8766/#ex_overhead_tricep_extension) | needs-correction | See failed outputs and AI notes |
| [ex_reverse_wrist_curl](http://127.0.0.1:8766/#ex_reverse_wrist_curl) | needs-correction | See failed outputs and AI notes |
| [ex_romanian_deadlift](http://127.0.0.1:8766/#ex_romanian_deadlift) | needs-correction | See failed outputs and AI notes |
| [ex_skullcrusher](http://127.0.0.1:8766/#ex_skullcrusher) | needs-correction | See failed outputs and AI notes |
| [ex_t_bar_row](http://127.0.0.1:8766/#ex_t_bar_row) | needs-correction | See failed outputs and AI notes |
| [ex_tricep_extension](http://127.0.0.1:8766/#ex_tricep_extension) | ready-for-review | r6-ex-tricep-extension-motion-2de990ab |
| [ex_upright_row](http://127.0.0.1:8766/#ex_upright_row) | needs-correction | See failed outputs and AI notes |

## Next production work

Improve starting references and movement constraints for failed exercises; use a different reference approach at the three-attempt shot limit. Continue untouched exercises in the remaining production queue with fresh quotes, reviewed references and four isolated workers.

Common failures: grip rotation, wrong exercise substitution, extra partial cycles, disappearing highlights, short range and equipment morphing. Increasing duration alone did not resolve these.

Focused manual phone-sized and wide web inspection, local playback and media editorial inspection. Automated tests/builds/lint/type checks/native/theme sweeps deferred.
