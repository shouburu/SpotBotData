# SpotBotData

The canonical SpotBot exercise catalog and its media authoring tools. The active catalog is `2026.09.22.5`, revision `15`: **427 exercises**, 564 retired identities and 21 starter workouts. `catalog.json` is the source of truth; generated app snapshots live in the sibling SpotBot repository.

Round 11 human media review is complete. The app release contains **111 approved generated videos and six direct YouTube references**, with 222 video/poster files totaling 71,750,810 bytes. All 427 active exercises also have a separately curated YouTube recommendation. Generation remains available, but the completed queues are not authorization to spend more credits.

## Current files

| File | Purpose |
| --- | --- |
| `catalog.json` | Canonical content, source/license evidence, editorial reviews, retirements and starters |
| `catalog.schema.json` | Authoring schema; shared SpotBot schemas add runtime constraints |
| `Scripts/build_catalog.py` | Source audit and deterministic app snapshot export |
| `Scripts/publish_catalog.py` | Source audit and existing SpotBot publication workflow |
| `form-media/manifest.json` | Media selections, asset provenance, human decisions, production rounds and budget authorizations |
| `form-media/attempts.json` | Immutable submitted prompts, prices, outcomes, credit settlements and lifetime attempt counts |
| `form-media/app-release.json` | Last exported approved selections and exact delivery hashes |
| `form-media/app-reference-recommendations.json` | Catalog-wide YouTube selections and publisher evidence |
| `form-media/round-11-jobs.json`, `prompts/`, `round-11-*-reviews.json` | Current authoring briefs and exact-output editorial evidence |
| `form-media/reviews/` | Durable catalog retirement and consolidation decisions |
| `form-media/style.md` | Current visual and movement review standard |
| `form-media/assets/`, `reports/` | Ignored local media, source evidence and generated inspection artifacts |

## Catalog editing and export

Edit `catalog.json` directly. Preserve canonical IDs for editorial corrections. Keep one record per actual movement, useful unambiguous aliases and precise apparatus, laterality and counting semantics. Record explicit product removals in `provenance.retiredExercises`, remove active reviews, and update source decisions and starter references. Retired IDs cannot be reimported. Do not substitute a different movement or add media from the removed scraping pipeline.

Every active exercise needs source evidence and an honest editorial decision. The 873 approved upstream source IDs retain their imported, mapped or excluded decisions, original row hashes and pinned Unlicense snapshot. Catalog reviews are AI editorial assessments, not independent trainer or clinical approval. Lower Back–SMR remains flagged for a removal/qualified-review decision in its Form Guidance audit.

Use short ordered setup, movement/hold and controlled-return steps. Preserve safe loading/unloading, contact points, useful optional variations and per-side counting. Measurement contracts are `reps`, `duration` (seconds), `distance` (metres), and `time_distance`; defaults are editable starting targets. Required apparatus must exist in SpotBot's shared equipment vocabulary. Increment version and revision for a new published release.

When content export is authorized:

```sh
python3 Scripts/build_catalog.py --check
python3 Scripts/build_catalog.py
```

Both commands audit provenance, reviews, duplicate decisions, IDs, starters, laterality, defaults and storage limits. They also invoke the sibling SpotBot shared/runtime schema validator, so its Node dependencies are required. The second writes `../SpotBot/packages/shared/src/catalogData.ts` and `../SpotBot/apps/backend/src/appwrite/starterCatalogData.ts`. `--app-root` selects another checkout. Advisory duplicate reports belong under ignored `reports/`; use `--duplicates-report reports/duplicate-candidates.json` and resolve findings explicitly rather than automatically merging names.

## Publication

`python3 Scripts/publish_catalog.py --dry-run` audits the source and delegates to SpotBot's existing publisher. The default is offline. Cloud comparison needs explicit endpoint, project and API URL; `--apply` additionally requires the selected project confirmation, reviewed plan hash and report path. The wrapper does not choose a cloud target or store credentials.

The standard-catalog API and collections have not been deployed or published. Starter marketplace publication and generated-binary hosting are also separate operations. Prior cloud releases remain immutable history. Product retirements require catalog-capability-4 clients; saved plans, workout history and personal/detached exercises remain preserved. Prescription exchange remains v3.

## Media review and app delivery

Start the local dashboard with `python3 Scripts/form_media.py serve`, then open [localhost:8766](http://127.0.0.1:8766). It reads current catalog content, assets, exact human decisions and the full credit ledger. Older-round selections retain their original attribution. Historical prompt text comes from frozen attempt/asset records; only current authoring prompts are read from separate files. Opening the dashboard never spends credits.

After authorized selection or recommendation changes:

```sh
python3 Scripts/export_form_media.py
python3 Scripts/export_youtube_references.py
```

The first requires current accepted selections, exact latest human approval and unchanged source delivery hashes. It writes `exerciseFormMediaData.ts`, `form-media/app-release.json` and ignored `../SpotBot/apps/frontend/public/exercise-media/` copies. A later human decision can approve an older asset without rewriting its original flags; AI candidate status is not human approval. The YouTube exporter requires one direct video per active canonical ID with selection evidence and recorded public embed metadata, and writes `exerciseYouTubeRecommendations.ts`. Both accept `--app-root`.

Media is served on demand from `/exercise-media/<sha256>.mp4` and `.webp`, outside the JavaScript/native asset bundle. `EXPO_PUBLIC_EXERCISE_MEDIA_BASE_URL` selects a deployed HTTPS origin/path; native 3D playback needs that base. Local export does not provision hosting. The web compilation guard requires the delivery files unless a remote origin is configured. The release manifest records the last export; its source digest is historical until the next authorized export.

## Generation and editing

Follow [the media standard](form-media/style.md). The guarded single-shot runner is `Scripts/generate_form_media.py`; sequential explicitly named jobs use `run_form_media_queue.py`, and bounded parallel groups use `run_form_media_round.py` with `generate_form_media_group.py`. The active round is recorded in the manifest; its job file and prompt hashes govern submission. `observe_form_media_flow.py` records fresh exact-model UI prices and same-account balance. The legacy `flow_pricing.py` route remains available if its API path works again; stale observations never authorize a generation.

Generation uses existing authenticated gflow profiles and the recorded Flow project. The macOS cookie and prompt readback patches have version/hash guards (`patch_gflow_macos.py`, `patch_gflow_prompt.py`); the version-specific image-picker patch is `patch_gflow_image_picker.py`. Inspect their source/status before changing installed gflow. Do not restart login loops merely because legacy endpoints fail, or run two jobs in one profile. Each output has its own frozen prompt/reference/quote hashes and reservation.

The current authorized ceiling is **10,000 credits for `google-flow-2026-09-21`**. Read current spending, reservations and remaining balance from the ledger/dashboard. Preserve all historical attempts and `budgetPeriods[].priorAttemptIds`. A new period requires explicit user authorization through `form_media.py start-budget-period`; a date change never resets it. Unknown outcomes, missing outputs, unexplained charges and unresolved reservations stop submission. Group settlement requires exact outputs and a matching aggregate debit, retaining the allocation method. Attempt limits and explicitly authorized exceptions are recorded per round/shot. The retained seven `notSubmittedEvidence` proof files are read by the lifetime-attempt guard and must remain byte-identical.

Use `reconcile_form_media.py --attempt ATTEMPT_ID` for failed/uncertain submissions only after their producer stops; it retrieves matching existing output and settles only an evidenced charge, without generating or retrying. `prepare_form_media_asset.py --attempt ATTEMPT_ID --title TITLE --alt TEXT` encodes a settled frozen master. `derive_form_media_clip.py` creates an explicitly reviewed original-speed interval with a new asset ID and immutable source/edit provenance. Review derivatives independently. `sync_form_media_reviews.py` imports active-round exact-output AI evidence; `advance_form_media_editorial.py` applies explicitly authored corrections without changing human decisions.

## History and local cleanup

Completed prompts, quote observations, group configurations, round reports, duplicate snapshots and review workbooks were removed from the active tree. Their original bytes remain at [checkpoint `670df4dd4c1894d92a9cf3b9e34e6f730dafe2fe`](https://github.com/shouburu/SpotBotData/tree/670df4dd4c1894d92a9cf3b9e34e6f730dafe2fe). No Git history was rewritten. For example:

```sh
git show 670df4dd4c1894d92a9cf3b9e34e6f730dafe2fe:form-media/round-9-report.md
```

Historical paths and hashes inside immutable attempts, approvals, assets and retirement records still identify files at that checkpoint; they are not instructions to rerun old queues. Restore explicitly needed historical authoring inputs from that commit before revisiting an old round. The ten Round 1 decisions formerly projected from a full snapshot now live unchanged in `manifest.reviewHistory`. Current queue inputs and the exact seven safety proofs stay in the checkout. New quote/group evidence remains tracked while active; retire a completed batch only after settlement and a recoverable Git checkpoint.

`outputs/` and inspection dumps are ignored. Ignored does not mean disposable: keep approved deliveries from `app-release.json.files`, masters, references, exact settlement evidence and edit masks/filters. Preserve binary backups before removing rejected/older media; Git cannot recover ignored files. Reproducible contact sheets may be removed only when their exact source survives and no retained record references them.

## Handoff and validation scope

Current phase remains focused manual web/media feedback. Catalog content, generated app descriptors, selected media and credit history are preserved. The cleanup received source/diff inspection and a phone-sized dashboard review of the current catalog/budget, active prompt, historical prompt text and migrated Round 1 review history; no review was saved and no credits were spent. Earlier playback/content evidence remains historical. Detailed run results belong in the cleanup PR.

No generation, exporters, automated tests, builds, lint/type checks, theme sweeps or native checks ran for cleanup. Further media production needs a requested action; automated validation, native verification, catalog publication and binary hosting remain deferred until explicitly selected.
