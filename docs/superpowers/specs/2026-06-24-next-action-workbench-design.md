# Next action workbench design

Build a staff-only next-action workbench for Clinical Differential Support so the product tells the owner what to do next instead of treating the headache MVP handoff as the final product.

## Scope

- Add a selector that reads the current governed content coverage from the database.
- Expose a staff-only page at `/review/next-actions/`.
- Expose a staff-only summary JSON export at `/review/exports/next-actions.json`.
- Link the workbench from the governance dashboard and release readiness report.
- Keep the output Chinese-first with English secondary labels.

## Required behavior

- If the database only contains the headache chief complaint, the workbench must explicitly mark the product as not final beyond headache.
- The first priority action must be adding the next chief complaint module, starting with chest pain as the next expansion target.
- The workbench must show coverage counts, existing chief complaints, expansion target, governance follow-ups, testing follow-ups, and handoff/export follow-ups.
- JSON must remain summary-only and must not include detailed clinical rule text, source titles, source URLs, patient data, diagnosis orders, treatment orders, credentials, or trading/order behavior.

## Acceptance checks

- Anonymous users are redirected to reviewer login for both page and JSON export.
- Staff users can open `/review/next-actions/` and see the coverage gap plus next actions.
- Staff users can download `/review/exports/next-actions.json`.
- The governance dashboard links to the workbench.
- The release readiness report links to the workbench.
- Existing headache workflow, governance tests, handoff tests, and smoke checks continue to pass.
