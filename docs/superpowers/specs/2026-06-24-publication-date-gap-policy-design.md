# Publication Date Gap Policy Design

Date: 2026-06-24

## Objective

Make the Source Freshness Audit explicit about official sources that do not publish a clear publication date.

The product must not infer missing dates. It should document the policy, show per-source manual-review status, and avoid treating a blank publication date as a stale-source blocker when the access date is current.

## Scope

- Add a `publication_date_gap_policy` block to the source freshness report and JSON export.
- Add per-source publication-date review metadata for missing-date rows.
- Update next actions so missing publication dates are governed as a documented limitation, not as an automated date-fill task.
- Show the policy on the staff-only Source Freshness Audit page.

## Rules

- A blank `publication_date` remains blank unless an official source explicitly provides a date.
- Blank publication dates are not inferred from access dates, copyright years, URL paths, or page metadata.
- Blank publication dates are not stale blockers by themselves.
- Missing-date rows require manual review when the source is next refreshed or when the staff reviewer has an official date to record.
- If there are no stale sources, the next automated action is regression and smoke verification.

## Safety Scope

- Staff-only metadata governance.
- No clinical rule changes.
- No automatic scraping or external writes.
- No patient data, credentials, diagnosis orders, treatment orders, medication orders, broker behavior, trading behavior, or Shioaji behavior.

## Acceptance Checks

- Red tests fail before the policy block is implemented.
- Source freshness report includes the no-inference policy.
- Missing-date rows expose manual-review metadata.
- Staff page renders the policy and manual-review status.
- JSON export includes the policy and omits detailed clinical item text.
- Full regression, Django check, live smoke, and live DB verification pass.
