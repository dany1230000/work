# Next Action Downstream Integration Design

Date: 2026-06-24

## Objective

Upgrade the staff-only Next Action Workbench so it reflects completed downstream audit gates.

After configured chief-complaint expansion, case-depth review, source freshness review, and publication-date gap policy are clear, the workbench should show the next practical gate: full regression and live smoke verification.

## Scope

- Add downstream readiness summary to the Next Action plan.
- Pull summary-only signals from Coverage Depth Review.
- Pull summary-only signals from Source Freshness Audit.
- Update next actions when downstream gates are clear.
- Render downstream readiness on `/review/next-actions/`.

## Readiness Rules

- If expansion targets are incomplete, keep expansion actions first.
- If governance blockers exist, keep governance remediation first.
- If coverage-depth has complaint gaps, point to Coverage Depth Review.
- If source freshness has stale sources, point to Source Freshness Audit.
- If no stale source remains and publication-date gaps are documented by policy, move to regression/smoke gate.

## Safety Scope

- Staff-only summary planning.
- No source URLs or detailed clinical rule text in Next Action JSON.
- No clinical recommendation changes.
- No patient data, credentials, diagnosis orders, treatment orders, medication orders, broker behavior, trading behavior, or Shioaji behavior.

## Acceptance Checks

- Red tests fail before downstream readiness is integrated.
- All-fixture plan has completion status `ready_for_regression_gate`.
- All-fixture first next action is `run_full_regression_and_smoke_checks`.
- Page renders coverage-depth and source-freshness readiness summaries.
- Next Action JSON remains summary-only.
- Full regression, Django check, live smoke, and DB verification pass.
