# Round 4 · completed production, pending user review

The five-exercise Anatomical 3D comparison package is complete as of 2026-09-15. [Results, exact asset links, sizes and limitations](round-4-results.md) identify the five clips selected **for comparison**, not by the user. All five are AI editorial candidates with user review still pending. Graphic 3D remains the approved baseline; accepted earlier assets, exceptions and review history are preserved.

The [public reference](https://x.com/averagetojacked/status/2098494293195305258) was actually inspected: fixed-camera gray anatomy, orange shoulders, gray apparatus, white background and a six-second controlled cable raise/return. SpotBot's Lateral Raise remains bilateral dumbbells. The completed comparison adds Seated Dumbbell Press, Seated Cable Row, Barbell Squat and Barbell Deadlift. [Style 4.0](style-v4.md), the plan, jobs, immutable attempt prompts and reference hashes retain the production intent. No third-party footage was copied into deliveries.

## Settled package and review state

All **18 Round 4 attempts are completed and settled**: ten images at verified zero cost and eight videos at twelve credits each. Round 4 spent **96 credits**, raising cumulative pilot spend from 744 to **840 / 2,000**. **1,160 remain, zero are reserved**, and the final observed account balance is **9,240**, down from 9,336. Account balance and the local pilot ceiling are separate quantities. The [ledger](attempts.json) remains authoritative after any later work.

| Exercise | Comparison video asset | AI finding and material limitation |
| --- | --- | --- |
| Lateral Raise | `r4-lateral-raise-anatomical-motion-66a6b920` | Bilateral shoulder-height raise and return; slight head-top crop and feet outside the deliberate upper-body view. |
| Seated Dumbbell Press | `r4-seated-db-press-anatomical-motion-de3c3b17` | Supported overhead press and return; inner dumbbell ends retain a visible gap instead of meeting as the catalog describes. |
| Seated Cable Row | `r4-cable-row-anatomical-motion-81725360` | Lower-rib pull and forward return; small trunk-angle change remains. Entirely gray because the side view cannot support a confident primary-back highlight. |
| Barbell Squat | `r4-squat-anatomical-motion-c5d6dea2` | Standing start, meaningful flexion and standing return with clear apparatus space; thighs remain somewhat above horizontal. It is not a parallel-depth example. |
| Barbell Deadlift | `r4-deadlift-anatomical-motion-5bcc600b` | Grounded floor lift, standing hold and controlled floor return. Keep the full eight seconds: plate contact is established around 7.3 seconds. |

Each video is eight seconds. The five videos and posters total **3,534,772 bytes**; the largest exercise package is 827,932 bytes. Exact delivery reviews are synced to the manifest; all five asset content statuses remain `pending`. Earlier Lateral Raise, Row and Squat motions remain `needs-correction`, alongside their source images and critique. These are AI findings, not user rejections. No shot exceeded three actual generations; the Squat starting-image shot used all three. Do not rename a shot to bypass that limit.

The [manual review evidence](round-4-manual-review.json) records all five dashboard HTML videos ending normally at eight seconds without media errors. The measured 390 × 844 CSS-pixel view had document width 390, with readable Form, preview and controls; a 1600 × 900 view was also inspected. Refresh retained prior selections, historical notes, new candidates and imported reviews. No user decision was submitted, and the completed Round 3 snapshot hash is unchanged. An initial in-app preview tab crashed; a fresh tab played the same delivery successfully. No deliberate media-failure case was injected. This is manual browser evidence, not native app verification or trainer approval.

## Established compatibility path

Installed gflow 0.72.0 still verifies the original `shouburu` profile's email while legacy pricing and credit routes return HTTP 401. The user completed Google sign-in in separate profile `shouburu-round4`, but the CLI detector did not recognize completion; the process was stopped. No marker was fabricated, the separate profile was retained and the original default stayed `shouburu`. Do not restart that login loop or imply the user has not signed in. The reviewed macOS cookie patch remains active; no additional installed-source patch supplied this solution. See [authentication diagnosis](round-4-auth-diagnosis.json).

The upstream migrated-host gap is documented in [PR 797](https://github.com/ffroliva/gflow-cli/pull/797) and the [PR 812 price/balance investigation](https://github.com/ffroliva/gflow-cli/pull/812). Our same-account Flow UI observations supplied the prices and balances those legacy routes could not return. This does not repair the failing APIs.

**All 18 media generations used the normal gflow CLI.** The in-app browser only read composer settings, quotes and account balances. The repository runner's explicit `--ui-quote-file` mode froze the evidence and its hash; gflow continued to submit and retrieve the actual media. Each output remained held for a separate fresh UI post-balance observation before ledger completion. Zero-priced stills required reconciliation too.

## Resume procedure

The next action is user comparison in the existing workbench, using [the results](round-4-results.md). Remaining credits do not trigger an automatic extra batch or replacement of accepted media. For any subsequently authorized shot:

1. Read the live manifest, jobs, attempts and latest exact-output reviews. Preserve user selections, verify the logical shot's attempt count, and resolve any open submission first. Motion requires an exact reviewed starting master; keep unsupported end-frame mode disabled.
2. In the same account and intended Flow project, observe the exact composer selection and live declared cost, then the account balance. Save the observation under `form-media/ui-quotes/`. Bind project, exercise, shot, model, kind, aspect and x1 output; video also binds duration and 720p. Never reuse the historical zero or twelve-credit price without observing the next offer.
3. Pass that file through `Scripts/generate_form_media.py --ui-quote-file …` with matching generation arguments. The runner checks a maximum five-minute age, freezes visible evidence and hash, reserves the quote, and rechecks freshness and unchanged evidence before submitting through gflow. Keep calls sequential and avoid unrelated account spending during settlement.
4. After output retrieval and measured metadata, observe and save a fresh same-account balance. Complete the exact attempt through `form_media.py complete` only when the identified output and observed debit reconcile to its quote, retaining settlement evidence. An uncertain result, balance mismatch or expired quote stops further submission. Do not infer a free failure or fabricate evidence.
5. Encode/register the settled master using the existing asset workflow, preserve its hash, and review the actual delivery separately. AI candidate status, user acceptance and trainer review stay distinct. Retain corrections and old alternatives.

Current phase is a completed local content-production package awaiting user review. Generated-binary hosting and app ingestion were not changed. Machine Chest Press's two-position images and Leg Press's knee-flexion correction remain separate backlog. Automated tests, builds, lint/type checks, native/device verification and theme sweeps remain deferred; none are claimed to have run or passed here.
