# Final Verification Gate Design

Date: 2026-06-24

## Objective

Add a staff-only Final Verification Gate after Next Action Workbench reaches the regression/smoke gate.

The gate should tell staff exactly what must be run before handoff/export, which handoff artifacts to export after successful verification, and what status the governed database currently supports.

## Scope

- Add a summary-only selector for final verification.
- Add a staff-only HTML page at `/review/final-verification/`.
- Add a staff-only JSON export at `/review/exports/final-verification.json`.
- Link it from Next Action Workbench and Release Readiness Report.
- Extend local smoke checks for the protected page and JSON export.

## Rules

- The app must not pretend external commands were run unless evidence is recorded by a future evidence recorder.
- The gate status is `ready_for_final_verification` when release readiness is clear and next-action status is `ready_for_regression_gate`.
- Required commands are listed as command strings and expected evidence summaries, not full command output.
- Handoff exports remain staff-only and are suggested only after required commands pass.

## Safety Scope

- Staff-only summary planning.
- No detailed clinical item text.
- No source URLs in final verification JSON.
- No patient data, credentials, diagnosis orders, treatment orders, medication orders, broker behavior, trading behavior, or Shioaji behavior.

## Acceptance Checks

- Red tests fail before selector/routes/templates exist.
- Final verification report exposes gate status, required commands, and handoff export routes.
- Page and JSON export are staff-only.
- Next Action and Release Readiness link to the gate.
- Smoke script includes protected final-verification checks.
- Full regression, Django check, live smoke, and live DB verification pass.
