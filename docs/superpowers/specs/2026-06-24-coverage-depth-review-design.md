# Coverage Depth Review Design

Date: 2026-06-24

## Objective

Add a staff-only Coverage Depth Review workbench after the configured chief complaint expansion list is complete.

The workbench should tell staff what to do next: source freshness audit, case-depth expansion, rule-depth review, and governance blocker cleanup.

## Scope

- Add a selector that summarizes coverage by chief complaint.
- Add a staff-only HTML page at `/review/coverage-depth/`.
- Add a staff-only JSON export at `/review/exports/coverage-depth.json`.
- Link the page from governance, release readiness, and next-action workbench.
- Keep the export summary-only: counts, gap codes, action IDs, and complaint slugs/titles only.

## Gap Signals

- `source_gap`: at least one clinical item has no source link.
- `non_approved_gap`: at least one clinical item is not approved.
- `review_due_gap`: at least one clinical item is due for review.
- `case_validation_gap`: at least one scenario is missing an expected output.
- `case_depth_gap`: fewer than 4 active validation cases for a chief complaint.
- `rule_depth_gap`: fewer than 8 active rules for a chief complaint.

## Safety Scope

- No new clinical recommendations.
- No patient data persistence.
- No diagnosis, treatment, medication, procedure, or order behavior.
- No credentials, trading behavior, broker behavior, or Shioaji behavior.
- JSON export must not include source URLs or detailed clinical item text.

## Acceptance Checks

- Coverage depth tests fail before selector/routes exist.
- Coverage depth tests pass after implementation.
- Operational smoke plan covers protected page and JSON export.
- Full Django regression and live smoke pass.
