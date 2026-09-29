# Source checkpoint · 2026-09-29

The user requested merge requests for SpotBot and SpotBotData and saving both repositories to `master`. This checkpoint preserves the current catalog, form-media authoring tools, production history, review evidence, and app delivery manifests.

The current catalog is `2026.09.22.5`, revision 15, with 427 active exercises and 21 starter workouts. The approved release manifest selects 111 generated videos and six direct YouTube references. The separate recommendation manifest covers all 427 active exercises. Round 11 human review is complete; its production report and the live manifests retain the decisions and remaining correction history.

The authorized phase for this request is repository publication. Source/diff inspection and publication file inventory were performed for this checkpoint. No tests, build, lint, type check, exporter, browser review, native/device verification, or theme sweep was run for this request. Earlier manual web/media evidence is recorded in `form-media/round-11-report.md` and the review files; it is historical evidence, not a new verification result. Automated checks and further platform review remain deferred until explicitly selected.

Generated masters and delivery binaries remain in the existing ignored `form-media/assets/` directory (approximately 2.54 GB), and diagnostics remain in ignored `reports/` (approximately 719 MB). They are preserved locally and are not part of this Git checkpoint. The approved video/poster delivery set is 71,750,810 bytes; its hashes and source paths remain in `form-media/app-release.json`. Moving or restoring the full media workbench requires separately transferring the ignored assets. No cloud media hosting or catalog publication is part of this checkpoint.

Next action: complete the coordinated repository merges, then resume from the live manifests and the sibling SpotBot handoff. Do not restart generation, reset the credit period, rerun exports, or expand validation solely because the checkpoint has been merged.
