# Next Action General Catalog Import Design

## Goal

Make the Next Action Workbench stop treating the current four chief-complaint workflow as the final project gate when the broader "any disease" general differential catalog still needs reviewed expansion.

## Scope

This phase integrates the new staff-only General Differential Import Workbench into the existing next-action state machine. It does not add new medical conditions, import user-provided data, or change ranking behavior.

## Design

When chief-complaint coverage, source freshness, case validation, and governance blockers are clear, the next-action selector should advance to `general_catalog_import_ready` instead of `ready_for_regression_gate`. The first action should link to `/review/general-differential-import/`, summarize the 300-condition and 379-source catalog state, and point reviewers to the lowest-coverage specialty buckets. The regression/smoke action remains visible as the following gate, but it is no longer the first action.

The final verification and project completion gates must remain blocked while the first next action is general catalog import. This keeps status truthful: the app may be deployable, but the "any disease" product goal is not final.

## Data Contract

`build_next_action_plan()` adds a summary-only `general_catalog` block:

- `condition_count`
- `source_count`
- `catalog_target_met`
- `import_workbench_path`
- `lowest_coverage_buckets`
- `first_action`

No source URLs, detailed clinical item text, or patient data are exposed.

## Acceptance Criteria

- Next Action Workbench shows `General Differential Import Workbench`.
- Next Action JSON includes `general_catalog` summary and no source URLs.
- When downstream audits are clear, `completion_status` is `general_catalog_import_ready`.
- First action is `expand_general_differential_catalog_via_import_workbench`.
- Final Verification Gate is blocked by next-action gate until this step is resolved.
- Project Completion Gate does not report `final_complete` while this broader catalog expansion step remains.
