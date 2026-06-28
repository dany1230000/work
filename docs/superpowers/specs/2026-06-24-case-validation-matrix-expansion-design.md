# Case Validation Matrix Expansion Design

Date: 2026-06-24

## Objective

Resolve the current `case_depth_gap` reported by Coverage Depth Review by raising every configured chief complaint to at least 4 active validation cases.

## Scope

- Add one additional chest-pain non-patient case scenario.
- Do not change clinical rules, item content, source metadata, or clinician-facing recommendations.
- Update tests so Coverage Depth Review expects zero gap codes after fixture expansion.

## Safety Scope

- Fixture scenarios remain non-patient validation data.
- No patient data persistence.
- No diagnosis, treatment, medication, procedure, or order behavior.
- No credentials, trading behavior, broker behavior, or Shioaji behavior.

## Acceptance Checks

- Chest pain fixture has at least 4 active validation cases.
- Coverage Depth Review reports zero complaints with gaps.
- First depth action moves to `audit_source_freshness`.
- Full tests, Django check, live smoke, and coverage-depth DB verification pass.
