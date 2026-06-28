# Source Freshness Audit Design

Date: 2026-06-24

## Objective

Add a staff-only Source Freshness Audit workbench after Coverage Depth Review reports no coverage gaps.

The audit should show whether governed source metadata is current enough for local handoff review, which sources are stale by access date, which sources lack publication dates, and what staff should do next.

## Scope

- Add a selector that summarizes source freshness from the governed database.
- Add a staff-only HTML page at `/review/source-freshness/`.
- Add a staff-only JSON export at `/review/exports/source-freshness.json`.
- Link the page from Coverage Depth Review, Source Library, and Clinical Governance.
- Keep this as metadata governance: no clinical rule changes, no automatic source scraping, and no inferred publication dates.

## Freshness Rules

- A source is `current` when `access_date` is within 180 days of the audit date.
- A source is `stale` when `access_date` is older than 180 days.
- A source has publication status `recorded` when `publication_date` is present.
- A source has publication status `not_listed_in_fixture` when `publication_date` is blank; this is not automatically treated as stale because some official pages do not publish a clear date.
- JSON export may include source metadata and URLs because it is staff-only and source-governance-specific.

## Safety Scope

- No patient data.
- No diagnosis, treatment, medication, procedure, or order behavior.
- No credentials, trading behavior, broker behavior, or Shioaji behavior.
- No automatic external writes or source edits.

## Acceptance Checks

- Red tests fail before `cds_core.source_freshness` and routes exist.
- Report summarizes 17 governed sources with 0 stale sources and 10 missing publication dates on 2026-06-24.
- Staff page and JSON export are protected.
- Governance, Source Library, and Coverage Depth Review link to the page.
- Full regression, Django check, live smoke, and DB verification pass.
