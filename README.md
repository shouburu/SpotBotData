# SpotBot standard exercise catalog

`catalog.json` is the only editable exercise dataset. It contains each exercise once, the 21 cloud starter templates, source and license evidence, source decisions, and one editorial review per exercise. The application snapshots are generated outputs in the sibling SpotBot repository.

The active local catalog is `2026.09.22.5`, revision `15`: 427 exercises. Nineteen grip-only duplicates were consolidated into existing base movements; their names remain aliases, and their retired IDs cannot be reimported. The 16 retained entries now use grip-neutral display names. Bench Press - Powerlifting is consolidated into Barbell Bench Press. See the [naming changes and further variant candidates](form-media/exercise-variant-audit-2026-09-17.md). See the [consolidation mapping](form-media/grip-consolidation-2026-09-17.md). 112 range-of-motion drills and non-yoga stretches, including Seated Ankle Pump, have been removed from active content. Their IDs, names and product reasons remain in `provenance.retiredExercises` to prevent reimport; no executable retired exercise records remain in the catalog. The transport field `redirects` stays empty because these removals do not map to different movements. Active canonical IDs stay stable, and useful names remain searchable aliases.

All 40 entries from the [weirdness ranking](docs/exercise-weirdness-ranking.md) were explicitly retired on September 17, 2026. On September 21 the user also approved all 176 [ranked form-variation consolidations](docs/exercise-form-variation-review-2026-09-21.md), merging them into 98 standard exercises. Removed names remain searchable aliases and useful setup/counting choices are optional guidance. That step removed 78 form variants from Round 8, leaving 156 entries before the second simplification. Production credit totals and archived reviews remain intact.

All 186 recommendations from the second [simplification review](docs/exercise-simplification-review-2-2026-09-21.md) are now approved and applied: 102 entries consolidated into 66 standards and 84 product-scope removals without replacements. That simplification left 457 exercises and 534 retired identities. Useful optional setup/counting guidance and 138 search aliases were retained; eight survivor names were generalized. The same Round 8 now has 100 members after removing its 56 affected entries. Surviving media decisions, historical workouts and production/spending records are preserved in place; original retired content and mappings are in the [application archive](form-media/reviews/simplification-consolidation-2-2026-09-21.json).

On September 22, the user explicitly removed Finger Curls, Wrist Roller, Barbell Wrist Curl, and Seated Palms-Down Barbell Wrist Curl without replacements. The catalog now contains 453 active exercises and 538 retired identities; three affected entries were removed from the existing Round 9, leaving 110. Original records, reviews and selected media are preserved in the [retirement archive](form-media/reviews/retired-forearm-exercises-2026-09-22.json). Media files and credit history remain intact.

After completing Round 9, the user requested 16 more named removals before Round 10. The surviving Round 9 review set has 94 entries. Round 10 review retired Donkey Calf Raises. Round 11 review retired Farmer's Walk, Suitcase Carry, and seven further explicitly marked exercises, leaving 427 active exercises and 564 retired identities. The [Round 9](form-media/reviews/round-9-user-catalog-decisions-2026-09-22.json), [Round 10](form-media/reviews/round-10-user-decisions-2026-09-23.json), [carry-removal](form-media/reviews/round-11-carry-removals-2026-09-23.json), and [Round 11 explicit-removal](form-media/reviews/round-11-explicit-removals-2026-09-23.json) archives retain the exact removal decisions and prior media/review provenance.

## Files

| File | Purpose |
| --- | --- |
| `catalog.json` | Canonical content, provenance, reviews, and starter references |
| `catalog.schema.json` | Draft-07 authoring schema; runtime constraints also come from SpotBot shared code |
| `Scripts/build_catalog.py` | Intrinsic source audit and deterministic snapshot export |
| `Scripts/publish_catalog.py` | Source audit followed by the existing SpotBot publisher |

There is no second raw, CSV, scraped, combined, or versioned copy of the exercise dataset in this checkout. The old importer and scraping credentials have been removed from the working tree. Previously committed files may still exist in Git history; this change does not rewrite repository history.

## Content and review

The consolidated source retains an exact snapshot of the upstream Unlicense text and its SHA-256, primary-source URL and commit. The approved 873-row free-exercise-db input is identified by SHA-256 `d68a817484964095e6af0be2cdcbcc2c2504168d1d190c7d5c725ce52f3ae1f4`. Its license snapshot is pinned to upstream commit `a859101d633a01c4a1a920d6a8ce41dabba0705f` at [LICENSE.md](https://github.com/yuhonas/free-exercise-db/blob/a859101d633a01c4a1a920d6a8ce41dabba0705f/LICENSE.md).

Every one of those 873 source IDs has a durable decision and original row digest: 207 imported, 405 mapped, and 261 excluded. The exclusions include 13 assisted contraction/relaxation protocols requiring separately timed phases, the ambiguous instruction-free `Iron_Cross` record, one mixed cable-crunch/side-bend protocol prescribed to failure, and 76 source records for the removed range-of-motion drills and stretches. Three other instruction-free identities were recovered with independently authored guidance: barbell push press, single-arm kettlebell swing, and side-lying bent-knee V-up. The separately authored uniform BOSU cable-crunch component is now optional setup guidance under Cable Crunch; it does not silently replace the excluded multi-phase protocol. Each reconsidered source decision records its specific evidence and any related adaptation.

Each of the 427 active exercises has an individual review of its instructions, anatomy, apparatus, tracking, laterality, difficulty, activities, goals and default dose. The current recorded decisions are 373 repair, 26 retain and 28 add; 261 source exclusions are recorded separately. Source mappings retain their concrete movement comparisons, and current similar-name pairs have explicit keep-distinct decisions. This was AI editorial work; it does not claim independent trainer or clinical validation. Edited instructions and default prescriptions are SpotBot's editorial layer, including when derived from the public-domain source. Defaults are editable starting targets, not prescriptions attributed to the upstream author.

The September 22 Form Guidance audit covered all 427 active entries. It revised 279 instruction sets and retained 148, reducing total text from 36,274 to 24,630 words; entries over 100 words fell from 126 to 18. Correctness assessments distinguish 52 corrections, 168 clarifications, 206 consistent entries and one unresolved entry. Per-exercise findings, retained details, source evidence and before/after counts live in `reviews[exerciseId].evidence.formGuidanceAudit`; these are AI editorial assessments, not trainer approval. Lower Back–SMR remains flagged pending the user’s removal/qualified-review decision because its floor-roller setup loads the lumbar spine; its instructions were not silently substituted with a different movement.

Write Form guidance as short, ordered setup → movement/hold → controlled return/finish steps. Preserve necessary contact points, machine adjustments, range limits, safe loading/unloading and repetition or per-side counting. Keep useful consolidated variations clearly optional. Remove redundant muscle-benefit prose and repeated generic cues; do not impose a word cap that drops essential technique. Complex sequences and movements carrying several approved setup options may remain longer.

Identity depends on the actual movement, position, apparatus and contraction. Names, tempo suggestions and load percentages alone do not create new exercises. Alternate names become aliases when unambiguous; conflicts are recorded under `provenance.aliasOmissions`. Support and attachment requirements are explicit, so ownership of a generic cable tower or Smith machine does not imply possession of every special attachment.

New coverage prioritizes useful beginner paths: chair yoga and Pilates, seated and standing low-impact cardio, supported walking balance and assisted/eccentric pulling. Existing movements can serve more than one activity without being duplicated under a new fitness label. All 39 yoga identities remain available, including nine poses with overlapping stretching tags. Foam-rolling recovery and substantive bodyweight/loaded strength movements are retained. Six dedicated mobility/stretching programmes are removed; the 21 remaining starter templates provide three per retained programme activity with concrete level-appropriate targets. Their retired IDs remain in `provenance.retiredStarterWorkouts` for exact source-owned cloud cleanup.

Activity memberships overlap and must not be summed as distinct exercise counts. The source decision ledger accounts for provider records; it does not add duplicate exercise records to the application catalog.

## Edit and export

Edit `catalog.json` directly. Keep the data model's measurement contract explicit:

- `reps`: a positive ordered integer repetition range; load may be none, optional or required.
- `duration`: a positive number of seconds, such as a plank hold.
- `distance`: a positive distance in metres, such as a carry or a measured jump attempt.
- `time_distance`: a positive duration and optional distance, such as a cycling session.
- `perSide`: the target applies separately to each side; instructions must define how alternating work is counted.

Preserve the canonical ID for editorial wording corrections. Keep only one exercise and review for each actual movement. If an authoring duplicate is removed, update source mappings and starter references to the selected exercise and retain only useful, unambiguous aliases. Do not manufacture aliases for a different movement. Explicit product removals need a durable `provenance.retiredExercises` decision; remove their active reviews, update source decisions and starter references, then export. The exporter refuses to reinstate retired IDs. Any future change to released tracking semantics must follow the publisher's compatibility rules.

Add source evidence and an honest review decision with every record. Required apparatus must exist in SpotBot's shared equipment vocabulary. Do not add media or material obtained from the removed scraping pipeline. Increment `version` and `revision` for a new published release; the publisher rejects modifications to an existing cloud revision.

From this directory:

```sh
python3 Scripts/build_catalog.py --check
python3 Scripts/build_catalog.py
```

The first command audits content without changing outputs. The second performs the same audit before writing both deterministic snapshots:

- `../SpotBot/packages/shared/src/catalogData.ts`: exercise runtime fields, revision, empty transport redirect map, and a separate list of excluded canonical IDs.
- `../SpotBot/apps/backend/src/appwrite/starterCatalogData.ts`: the 21 server-only starter templates and separate withdrawn starter IDs.

The audit enforces source/license accounting, one review per current exercise, explicit review evidence, name/alias collisions, starter references and coverage, laterality, mode-specific defaults, and storage limits. It also invokes `../SpotBot/scripts/appwrite/catalog-source-validate.ts`, which applies the full JSON schema and the actual shared runtime and publishing schemas before either output is written. The sibling SpotBot checkout and its installed Node dependencies are required. This is a content boundary, not an application test/build command.

To inspect advisory similarity candidates while editing:

```sh
python3 Scripts/build_catalog.py --check --duplicates-report reports/duplicate-candidates.json
```

The explicit report is written before the audit, including when new candidates prevent export. It compares normalized names and token overlap, and never merges records automatically. Compare the actual instructions and apparatus, then record a keep-distinct decision in `provenance.duplicateCandidateReviews` or remove the duplicate and update its references. Export requires a recorded decision for every current candidate. Reports are ignored generated files. `--app-root` selects the checkout supplying both shared validation and default output paths; snapshots must remain outside this source repository. Source hashes must agree between the Python and shared-schema passes, so an edit during validation requires a retry.

## Publication

```sh
python3 Scripts/publish_catalog.py --dry-run
```

This first audits the source, then delegates its explicit absolute path to SpotBot's existing `appwrite:standard-catalog:publish` command. The default is offline. `--compare-cloud` requires an explicit endpoint, project ID and API URL. `--apply` additionally requires the selected project confirmation, the reviewed cloud plan hash and a report path. The wrapper never chooses a cloud target or stores credentials. `--app-root` selects a different SpotBot checkout.

Product retirements are included in the reviewed publication plan and require catalog capability 4 clients; prescription exchange remains v3. Only explicitly recorded removals can disappear from the next release. Prior cloud releases remain immutable history, so publishing a new active release is not physical deletion of all old cloud rows. Updated apps omit retired IDs from old downloaded releases, prune only untouched unreferenced catalog-owned local rows, and retain referenced rows solely to preserve saved plans and workout history. Personal or detached rows remain intact.

The requested source-owned production cleanup is complete: the cloud had no global exercise rows; six withdrawn mobility/stretching starter documents were deleted, and Mermaid was removed from the remaining Pilates Side-Line starter. All seven writes were read back successfully, with a private local backup. Personal documents and workout history were untouched. The new standard-catalog collections and API are not deployed or published; that rollout remains separate.

Starter marketplace publication remains a separate backend operation. Its generated templates are not bundled into the frontend. Exporting or validating this repository does not publish either exercises or starters.

## Form media pilot and operator workflow

**Approved app media:** Round 11 user review is complete. The app now receives **111 selected generated videos and six direct YouTube references** from the [approved release manifest](form-media/app-release.json). The generated videos and posters total **71,750,810 bytes** (about 71.8 MB); these files are requested on demand and are not imported into the JavaScript or native asset bundle. The descriptor release keeps canonical exercise IDs, exact approved asset IDs, hashes and human approval provenance. It excludes retired exercises, superseded generated versions, unapproved candidates and search-result pages from embedded players. Older approved styles remain selected where the user never replaced them.

After changing media reviews, refresh the app delivery files with:

```sh
python3 Scripts/export_form_media.py
```

This content exporter checks the source delivery hashes before writing `../SpotBot/apps/frontend/src/features/exercises/exerciseFormMediaData.ts`, the ignored `../SpotBot/apps/frontend/public/exercise-media/` copies, and `form-media/app-release.json`. `--app-root` selects another SpotBot checkout. The web app and compiled web preview serve `/exercise-media/<sha256>.mp4` and `.webp` from the same origin. A deployed media origin can be set with `EXPO_PUBLIC_EXERCISE_MEDIA_BASE_URL`; the base may include a path prefix, followed by `/exercise-media/`. Native apps expose 3D media only when that base is configured. No cloud bucket or hosting was provisioned by this export. The versioned exercise catalog and database schema remain unchanged.

Approval is taken from the latest exact-asset human decision, including recorded user-conditional edits whose conditions were fulfilled. This matters because selecting an older-round asset in the dashboard leaves its original asset status untouched. Three accepted older selections still have pending flags, and Clean has an older AI rejection followed by explicit user acceptance; these four overrides are recorded in the release without modifying review history. Accepted direct expert references remain available alongside a selected generated video; search-only references use the app's exercise-name form search action.

**Catalog-wide YouTube recommendations:** All **427 active exercises** have a direct recommended video in the [reference manifest](form-media/app-reference-recommendations.json). It preserves the six human-approved references and the two short replacements requested for Dumbbell Lunges and Stiff-Legged Dumbbell Deadlift. Other selections are explicitly AI-curated, with publisher evidence and review limitations. Every selected URL returned public YouTube oEmbed video metadata; ambiguous movements received targeted browser checks, and source-verified excerpts keep selected longer tutorials focused. These checks do not represent exhaustive playback or trainer review. The rejected Bench Press reference remains excluded; the new recommendation is a different NASM video.

After editing recommendations or changing the active catalog, run:

```sh
python3 Scripts/export_youtube_references.py
```

This separate exporter requires exactly one reference per active canonical exercise and recorded public embed metadata. It writes only small descriptors to `../SpotBot/apps/frontend/src/features/exercises/exerciseYouTubeRecommendations.ts`; videos stay on YouTube. It never changes exercise contracts or generated-media approvals. In the app, human-selected references retain priority, followed by catalog recommendations; saved direct YouTube references remain personal overrides. Form always offers YouTube and Search for standard exercises, with 3D first and selected by default when its approved clip can be served. Custom exercises without canonical IDs rely on their own reference and Search.

Web export includes a compilation guard that requires every mapped local generated-media delivery file and hash, unless an explicit remote HTTPS media origin is configured.

**Round 6 in production (2026-09-15):** User feedback from Round 5 is preserved in `form-media/reviews/round-5-completed.json` (14 decisions; Leg Extension pending). Anatomical 3D remains the only new-video style. The cumulative cap is now **10,000 credits**, including the 1,152 spent before Round 6. The new queue tracks **421 remaining dumbbell, barbell/specialty-bar and machine/cable exercises**, plus two explicit Round 5 follow-ups. Draft prompts are not generated media and require exercise-specific review before submission. See `form-media/style-v6.md`, `form-media/round-6-jobs.json`, and `form-media/round-6-production-notes.md`. Existing accepted selections remain intact.

**Round 5 awaiting review (2026-09-15):** Generated motion studies for **15 new exercises: ten compound and five isolation**, using Anatomical 3D. **12 have AI editorial video candidates; Pull-up, Bulgarian Split Squat and Chest Dip remain flagged** for incomplete motion or reference framing. Candidate videos range from 273–825 KB. This round spent 312 credits; cumulative spending is 1,152 / 2,000 with no unresolved reservations. See the [measured summary](form-media/round-5-summary.json), [current standard](form-media/style-v5.md), and [handoff](form-media/round-5-production-notes.md). User acceptance and trainer review remain separate. Round 4 raw reviews remain in the [snapshot](form-media/reviews/round-4-completed.json).

The [Round 11 equipment-coverage report](form-media/round-11-report.md), [23-exercise queue](form-media/round-11-plan.json), live manifest and attempt ledger preserve the completed production/review record. The user ended the review phase and requested approved-media app integration; further generation is not the next action. Farmer's Walk and Suitcase Carry were retired without replacement; their prior starter and source mappings are archived in [the carry-removal record](form-media/reviews/round-11-carry-removals-2026-09-23.json). Earlier reviews, external selections, assets and credit charges remain historical. Do not reset the current budget period.

The [media standard](form-media/style.md) selects **Anatomical 3D** for future generation. The [Round 3 production report](form-media/round-3-report.md) records the earlier 19-exercise production checkpoint, before the completed user decisions above. Its candidate/held statuses are historical; use the current checkpoint and live manifest when resuming. The [prompt plan](form-media/round-3-prompt-plan.md) preserves the original nine revision briefs. [Round 1](form-media/pilot-report.md) and [Round 2](form-media/round-2-report.md) remain historical reports. Catalog removal is covered above; the catalog ingestion gate still excludes media. Approved media uses the separate app descriptor export described above.

[`form-media/manifest.json`](form-media/manifest.json) joins the catalog by canonical exercise ID without copying exercise names or instructions. It contains a proposed teaching medium and rationale for all 427 current exercises, priority, review state, selected asset IDs and operator notes. Round 11 has 23 members after removals. Earlier production cohorts remain historical. `recommendationStatus: pilot-reviewed` approves a pilot format choice only. Every generated or authored asset begins with pending content review. All other recommendations are provisional rules based on activity, difficulty, held versus moving positions, isolation versus compound movement and sequence complexity. Review those suggestions before production; they are not an instruction to generate hundreds of videos.

The original pilot compared text, stills, simple diagrams, generated motion and expert references. Current decisions keep Outdoor Walking as text, restore the user's Round 1 Plank, retain approved Graphic 3D assets, and preserve the short expert references. Ankle Pump and the other retired range-of-motion/stretching entries are absent from the active queue; their old costs, media and reviews remain in the historical record.

Start the local operator dashboard from this directory:

```sh
python3 Scripts/form_media.py serve
```

Open [the local dashboard](http://127.0.0.1:8766). It reads current catalog content and the durable manifest/attempt ledger. Review changes persist to disk; restarting the server keeps reviews, selected assets and reservations. Use the dashboard to compare drafts, inspect prompts and costs, record review notes, and choose assets. Carried selections remain visible in the current round with their original round labels. YouTube references load only after an explicit click, retain publisher controls and have an external fallback. Earlier SVG schematics remain historical alternatives.

Generation uses the user's existing authenticated `gflow` profile and a dedicated Flow project ID recorded in the manifest. These are CLI operations: `gflow` uses its isolated Chrome profile internally for Flow authentication and requests. Generation is submitted through the CLI. Live price and balance observations are required; do not restart sign-in loops merely because legacy endpoints fail. An expired session or Google authentication challenge can still require completing sign-in in that profile. The current allowance is **10,000 credits for period `google-flow-2026-09-21`**, reset once at the user's request on September 21. Read the current spent, reserved and remaining values from the live attempt ledger and dashboard; Round 10 is actively spending within that same period. Historical spending remains recorded separately. This is a local submission guard, not a Google billing limit; direct gflow commands outside the runner do not inherit it. Preserve the current period on resume. The following legacy read-only quote command is retained for a future repaired API path; fresh Flow UI observations are the working path:

```sh
python3 Scripts/flow_pricing.py --model-key GEM_PIX_2
```

To request one explicitly selected shot using its saved prompt, verified current quote and durable credit reservation:

```sh
python3 Scripts/generate_form_media.py --exercise ex_bench_press --shot bench-overhead-image --kind image --aspect 16:9
```

The runner in [`Scripts/generate_form_media.py`](Scripts/generate_form_media.py) owns the supported flags and one-shot submission flow. It reads `form-media/prompts/<shot>.txt`, requires the reviewed macOS patch, checks the pilot/attempt guards, obtains the current account quote for its explicitly selected model, records a reservation, and submits one requested output. Images use `nano-pro`; starting-frame videos use `omni-flash`. The model selections are explicit in the runner, and the price must be verified for that exact selection before submission.

Add `--reference form-media/assets/masters/<shot>/<asset>.png` to reuse a reviewed style or starting-frame image, using the file's actual PNG, JPEG or WebP path. For a video, replace the example reference below with the existing side-view starting frame; the overhead Bench image is a different camera and is not the correct starting frame for this shot:

```sh
python3 Scripts/generate_form_media.py --exercise ex_bench_press --shot bench-side-motion-video --kind video --aspect 16:9 --duration 8 --reference form-media/assets/masters/bench-side-start-image/START_FRAME.jpg
```

Video requires exactly one starting-frame reference, `16:9` or `9:16`, and a supported duration matching the brief. Run one generation at a time and avoid unrelated Flow spending during settlement. The API path completes an attempt only after a recognized success response, an attributed output file with matching media format, and an account debit equal to the verified quote. UI-quote mode deliberately leaves a downloaded output submitted and awaiting reconciliation until a fresh same-account UI balance settles it through the normal ledger command. A local file alone does not prove a successful, correctly charged submission.

The runner has an optional `--end-reference` path, but it is currently disabled for this account: gflow 0.72.0 has not ported end frames to the migrated flow.google.com frontend. Round 4 uses one reviewed starting image per video. A future supported loop request would declare `endFrameSameAsStart: true` and require the same exact image in both slots. The runner quotes the distinct first/last model (`omni_flash_i2v_8s_first_last` for eight seconds), freezes both roles and hashes, and checks returned settings. The delivery caption identifies whether the cycle starts lowered, overhead or at squat depth. Matching endpoints still require editorial inspection of the actual middle phase. Never assume first-only and first/last requests have the same price.

Exact briefs live in [`form-media/prompts/`](form-media/prompts/). Review a still for anatomy, equipment and framing before animating it. Save references and record the actual output duration; a prompt's requested duration does not establish what the provider delivered. Record a specific issue before retrying. The ledger enforces the active budget-period ceiling and the round-specific attempt limit. The historical default is three attempts per exercise/shot; Round 9 allows seven under the explicit request for corrective retries, always with exact-output evidence and a changed prompt or reference. A proven pre-submission CLI refusal remains recorded but can be excluded only after explicit zero-cost reconciliation with hash-linked source and balance evidence; unknown failures are never exempt. The guard blocks regeneration of a shot that already has accepted selected media; other distinct shots remain available. Any unsettled attempt also blocks a new generation, including a stale reservation on a terminal status. A failed or uncertain submission keeps its quoted reservation until the account/job outcome is reconciled; reopening the dashboard never retries a job.

If the CLI times out or reports an uncertain result, first wait for that generation process to exit. Preserve the reservation. The following recovery command depends on legacy project/credit endpoints and is currently subject to the same 401 limitation; use the Round 4 handoff for explicit UI reconciliation instead of regenerating an uncertain result:

```sh
python3 Scripts/reconcile_form_media.py --attempt attempt_REPLACE_WITH_LEDGER_ID
```

[`Scripts/reconcile_form_media.py`](Scripts/reconcile_form_media.py) only accepts a failed or uncertain attempt after submission has stopped. It reads the existing Flow project and requires exactly one result matching the stored prompt/hash, model and creation window, plus a stored media ID when available. It downloads that existing media, verifies the file signature and readable dimensions with `ffprobe`, and checks that a video has duration rather than being a poster image. It settles the reservation only when the account debit matches the quote. It never submits generation or automatically retries. Missing, ambiguous or differently billed results retain their reservation for manual reconciliation. A successfully recovered master remains a review candidate; use the asset-registration/review workflow before selecting it.

[`Scripts/form_media.py`](Scripts/form_media.py) owns ledger reservation, reconciliation and asset registration commands. `form-media/attempts.json` records the exact prompt, prompt version/hash, reference paths/hashes, quote evidence, provider outcome and settled or reserved credit use. Keep this ledger and the manifest for future sessions. Prompt and policy changes are versioned separately from immutable past attempt evidence. Never put passwords, cookies or session tokens in either file.

Credit renewals require an explicit user-authorized `start-budget-period --id PERIOD_ID --limit CREDITS --authorization TEXT` command in `Scripts/form_media.py`. It refuses any unresolved attempt or active generation group and records the exact prior attempt IDs in the manifest's `budgetPeriods`; it never clears or rewrites historical spending. New reservations and groups retain `budgetPeriodId`. Budget output reports the current period's `spent` and `remaining` alongside `lifetimeSpent`; all unsettled holds remain global. A date change alone never resets the cap, and live Flow prices and account balance still constrain each submission. The command changes the local submission budget, not Google billing.

The historical attempt limit remains three per logical shot. A specifically authorized round can record `maxAttemptsPerShot` with `attemptLimitAuthorization` in its production-round record. That raises only the ceiling: accepted media, unsettled attempts, unchanged correction prompts, live quotes, and remaining credit budget still enforce their existing gates. An increased ceiling never schedules automatic retries.

Generated masters and delivery copies live under ignored `form-media/assets/`; diagnostics live under ignored `reports/`. The manifest references these files, but Git does not carry the binary media. Back up or explicitly transfer that asset directory when moving to another machine, and retain hashes so missing or changed files are detectable. The authored HTML/SVG diagrams, prompt text and editorial manifest stay in source control. External videos remain hosted by their publishers and can play through the official YouTube embed; they are not copied or rehosted.

The installed-gflow macOS compatibility patch is managed separately by [`Scripts/patch_gflow_macos.py`](Scripts/patch_gflow_macos.py). It routes the known cookie reader through the isolated Chrome profile to avoid repeatedly requesting Chrome Safe Storage from Keychain. The script verifies the supported installed version and original/patched source hashes, and refuses unknown or upgraded source until it is reviewed. Its verified backup stays in gflow's application-data `patch-backups` directory outside this repository.

```sh
python3 Scripts/patch_gflow_macos.py status
python3 Scripts/patch_gflow_macos.py restore
```

`status` is read-only. `restore` undoes this specific cookie-reader patch; the guarded generation and recovery scripts then stop until the reviewed patch is applied again. Use `python3 Scripts/patch_gflow_macos.py apply` only for the recognized installed source. The patch does not manage the Google account, persist a password or eliminate normal authentication challenges. If a challenge appears, complete it in the existing profile and retain uncertain reservations until the generation outcome is known.

The September 21 [AI triage pass](form-media/reviews/ai-triage-2026-09-21.md), explicitly authorized to reject clear failures, reviewed 188 pending video versions and marked 140 exercise entries Rejected. That triage checkpoint left **46 exercises Needs Review** across the catalog. After subsequent user reviews and the approved 176-variant consolidation, that historical checkpoint showed **22 Needs Review**. Prior user decisions and all media remain intact; the [exact-output audit](form-media/reviews/ai-triage-2026-09-21.json) records every reason and original value. This is sampled-frame AI screening, not automatic acceptance. No new generation or credits.

Current phase is **Round 11 human review and correction backlog**. The [Round 11 report](form-media/round-11-report.md), [plan](form-media/round-11-plan.json), populated [job queue](form-media/round-11-jobs.json), live manifest and attempt ledger are the resumption source of truth. Six entries have new media in Needs Review: five AI-screened generated clips and one external Power Clean reference. Fourteen generated-video briefs failed exact-output AI review and need a new approach or reference before more credits are spent. The active Google Flow period is 5,851 / 10,000 credits spent, 4,149 available, zero reserved and zero unresolved; Round 11 used 264 credits. AI editorial flags are distinct from user approval. Automated tests, builds, lint/type checks, native/device verification and theme sweeps remain deferred.

In the dashboard, **Pending** means awaiting media or an initial decision; **Needs review** means newly delivered relevant media or a deferred decision. Use **Show media needing review**, then **Generated in → Round 11**, to find new deliveries. Round 11 clips enter that queue after an exact-output AI candidate review; clearly failed drafts remain recorded for correction. Explicitly requested edits remain available as operator options. New eligible media carries a round badge and opens in the preview. Earlier decisions and selected assets remain recorded. Saving a review records the exact loaded asset IDs so an unseen later delivery remains new. Refresh reloads incoming media; it spends no credits.

Delivery copies are encoded before hosting. Stills use WebP (`cwebp`, quality 86); videos use FFmpeg/libx264, CRF 22, `yuv420p`, no audio track and `+faststart`, while original masters remain intact. `ffprobe` records real dimensions, duration and bytes. The local server supports byte-range playback/seek, and accepting selected assets enforces a combined 5 MB limit including posters and overlays. Do not reverse footage to manufacture a return phase.

The future app phase should keep descriptors in local data and fetch approved binaries on demand from [Appwrite Storage](https://appwrite.io/docs/products/storage/upload-download). Encode before upload; this proposal uses progressive MP4 files, not a newly provisioned adaptive streaming service. Bundling 427 videos at 2 MB each would add about 854 MB before posters. YouTube Form placement is implemented; generated binary publication still needs approved assets and coordinated ingestion/hosting changes.

### Production queue and historical comparison

The completed Round 2 contained the original ten exercises plus ten new compounds (five seated, five standing). It compared **Porcelain studio**, **Warm ceramic**, and **Graphic 3D**. It replaces the rejected stick-figure approach with anatomical renders, removes unverified body markers, and uses short portrait references for the complex lifts. The saved Round 1 decisions remain in `form-media/reviews/round-1-before-round-2.json`; subsequent saves append to `manifest.reviewHistory` without rewriting earlier-round asset decisions.

`form-media/round-11-plan.json` is the current coverage plan; its job file contains the 19 generated-video briefs attempted this round. Earlier rounds remain historical. Round 10 used four CLI workers through `Scripts/run_form_media_round.py`, with live mode-specific quotes and exact group credit reconciliation. Direct text-to-video drafts require no image reference; image-to-video jobs still require exact starting-frame review. Resume only after inspecting unresolved attempts and the existing producer, never by launching a duplicate runner. `round-2-exercise-briefs.json` records the ten new movements' exact catalog constraints. Exact-output still and motion reviews live in the four `round-2-*-reviews.json` files; AI review is distinct from user approval. The historical `python3 Scripts/sync_form_media_reviews.py --round round-3` command copies matching Round 3 evidence into the dashboard without changing user decisions; use the actual active round for new work. Authored starting-reference reviews intentionally remain in their source files because those references are not delivery assets. No paid motion should use a starting frame whose exact master hash has not passed its framing/pose review.

To resume named jobs, one at a time:

```sh
python3 Scripts/run_form_media_queue.py --round round-3 --shots r3-lat-pulldown-illustrated-motion
```

The queue uses an existing completed output instead of regenerating it. It stops on unresolved submissions, previous unsuccessful attempts, missing references, or an unreviewed starting frame. Corrective generation is an explicit action with the same shot identity and a revised prompt; it never resets the active budget period or round-specific attempt ceiling. Each upload gets a unique filename while retaining the original reference hash, avoiding ambiguity in Flow's frame picker.

`Scripts/prepare_form_media_asset.py` encodes and registers a settled existing attempt without generation. It checks the frozen master hash, preserves that master, exports a WebP or silent fast-start MP4, records measured dimensions/duration/bytes, and produces video keyframes for editorial inspection. Existing registrations are checked before being reused. The selected package still has a 5 MB limit; unselected style alternatives are review material and would not be shipped together by default.

Current validation scope remains focused manual web and media review. Normal content export, app YouTube implementation and the precisely scoped source-owned cloud cleanup are complete. Automated tests, builds, lint/type checks, theme sweeps, native verification, new catalog API publication and generated-binary hosting remain deferred. The next production action is always determined from the durable queue, attempts and editorial findings, rather than rerunning a successful generation.

A complete repetition can also be delivered as an authored trim of a settled master. Use an explicitly reviewed interval and a new asset ID; the original remains available:

```sh
python3 Scripts/derive_form_media_clip.py --attempt attempt_REPLACE_WITH_LEDGER_ID --id NEW_UNIQUE_EDIT_ID --start 0 --end 5.5 --hold 0.25 --title "One complete cycle"
```

For a new-round edit of an earlier master, add `--round-id round-3`; it records the original source round separately and requires the target round to be active. This operation spends no generation credits. It preserves the actual speed and anatomy, records source hashes and endpoint holds in `form-media/edits.json`, and refuses to overwrite an existing edit. Review the new delivery separately. Never trim away a necessary phase or label a partial/incorrect sequence as a complete repetition.

Round 2 results and per-exercise limitations are in [the final report](form-media/round-2-report.md), with measured totals in [round-2-metrics.json](form-media/round-2-metrics.json). Compare Seated Dumbbell Press and Barbell Squat for three useful style options. Generated masters, rejected versions and exact-output editorial evidence remain available. The Bench bottom-contact still is explicitly static-only; Dead Bug's Graphic edit shows one diagonal repetition, and the Step-Up edit shows ascent only. Opening or refreshing the workbench never spends credits.
