# SpotBot standard exercise catalog

`catalog.json` is the only editable exercise dataset. It contains each exercise once, the 27 cloud starter templates, source and license evidence, source decisions, and one editorial review per exercise. The application snapshots are generated outputs in the sibling SpotBot repository.

The launch catalog is `2026.09.4`, revision `2`: 991 exercises. It contains no retired exercise records, migration ID lists, or duplicate redirects. The transport field `redirects` is explicitly empty. Active canonical IDs stay stable, and useful names remain searchable aliases.

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

Every one of those 873 source IDs has a durable decision and original row digest: 703 imported, 155 mapped, and 15 excluded. The exclusions are 13 assisted contraction/relaxation protocols requiring separately timed phases, the ambiguous instruction-free `Iron_Cross` record, and one mixed cable-crunch/side-bend protocol prescribed to failure. Three other instruction-free identities were recovered with independently authored guidance: barbell push press, single-arm kettlebell swing, and side-lying bent-knee V-up. A uniform BOSU cable crunch is also available as a separately authored component; it does not silently replace the excluded multi-phase protocol. Each reconsidered source decision records its specific evidence and any related adaptation.

Each of the 991 exercises has an individual review of its instructions, anatomy, apparatus, tracking, laterality, difficulty, activities, goals and default dose. The recorded decisions are 793 repair, 155 retain and 43 add; the 15 source exclusions are recorded separately. Source mappings retain their concrete movement comparisons, and current similar-name pairs have explicit keep-distinct decisions. This was AI editorial work; it does not claim independent trainer or clinical validation. Edited instructions and default prescriptions are SpotBot's editorial layer, including when derived from the public-domain source. Defaults are editable starting targets, not prescriptions attributed to the upstream author.

Identity depends on the actual movement, position, apparatus and contraction. Names, tempo suggestions and load percentages alone do not create new exercises. Alternate names become aliases when unambiguous; conflicts are recorded under `provenance.aliasOmissions`. Support and attachment requirements are explicit, so ownership of a generic cable tower or Smith machine does not imply possession of every special attachment.

New coverage prioritizes useful beginner paths: chair yoga and Pilates, seated and standing low-impact cardio, supported walking balance, gentle joint movement, and assisted/eccentric pulling. Existing movements can serve more than one activity without being duplicated under a new fitness label. The 27 templates retain three entries per activity; their exercises carry concrete level-appropriate targets.

Activity memberships overlap and must not be summed as distinct exercise counts. The source decision ledger accounts for provider records; it does not add duplicate exercise records to the application catalog.

## Edit and export

Edit `catalog.json` directly. Keep the data model's measurement contract explicit:

- `reps`: a positive ordered integer repetition range; load may be none, optional or required.
- `duration`: a positive number of seconds, such as a plank hold.
- `distance`: a positive distance in metres, such as a carry or a measured jump attempt.
- `time_distance`: a positive duration and optional distance, such as a cycling session.
- `perSide`: the target applies separately to each side; instructions must define how alternating work is counted.

Preserve the canonical ID for editorial wording corrections. Keep only one exercise and review for each actual movement. If an authoring duplicate is removed, update source mappings and starter references to the selected exercise and retain only useful, unambiguous aliases. Do not manufacture aliases for a different movement. Any future change to released tracking semantics must follow the publisher's compatibility rules.

Add source evidence and an honest review decision with every record. Required apparatus must exist in SpotBot's shared equipment vocabulary. Do not add media or material obtained from the removed scraping pipeline. Increment `version` and `revision` for a new published release; the publisher rejects modifications to an existing cloud revision.

From this directory:

```sh
python3 Scripts/build_catalog.py --check
python3 Scripts/build_catalog.py
```

The first command audits content without changing outputs. The second performs the same audit before writing both deterministic snapshots:

- `../SpotBot/packages/shared/src/catalogData.ts`: exercise runtime fields, revision, and the empty transport redirect map.
- `../SpotBot/apps/backend/src/appwrite/starterCatalogData.ts`: the 27 server-only starter templates.

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

Starter marketplace publication remains a separate backend operation. Its generated templates are not bundled into the frontend. Exporting or validating this repository does not publish either exercises or starters.
