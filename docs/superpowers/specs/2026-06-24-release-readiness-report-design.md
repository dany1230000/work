# Release readiness report design

## Goal

Add a staff-only release readiness report for the Clinical Differential Support MVP so reviewers can see whether the governed knowledge base is ready for handoff.

## Scope

- Add a readiness selector that summarizes governance blockers.
- Add a staff-only `/review/readiness/` page.
- Link the readiness page from the clinical governance dashboard for staff users.
- Include CSV export links from the readiness page.
- Keep the feature governance-only: no patient data, diagnosis orders, treatment orders, credentials, trading, or order APIs.

## Readiness criteria

The MVP is marked `ready` only when all are true:

- Every clinical item is approved.
- No clinical item is missing a linked source.
- No clinical item is due for review.
- Every active case simulation passes expected-output validation.

## Report sections

- Status banner: `Ready for handoff` or `Needs governance work`.
- Metrics: total items, approved items, non-approved items, source gaps, review due, case validation failures.
- Blockers: grouped links to source gaps, due reviews, non-approved items, and failed cases.
- Export links: clinical item CSV and source CSV.

## Safety

The page is staff-only and content-governance-only. It does not export or collect patient-identifying data and does not create diagnosis or treatment orders.
