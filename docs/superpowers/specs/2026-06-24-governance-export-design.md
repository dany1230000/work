# Governance export design

## Goal

Add staff-only CSV exports for the governed MVP knowledge base so reviewers can hand off clinical content and source metadata for external review.

## Scope

- Export clinical item inventory as CSV.
- Export source library as CSV.
- Link exports from the clinical governance dashboard for staff users.
- Keep exports staff-only through the existing reviewer login flow.
- Sanitize exported cells that could be interpreted as spreadsheet formulas.

## Clinical item export

Route: `GET /review/exports/clinical-items.csv`

Columns:

- `id`
- `chief_complaint`
- `item_type`
- `urgency`
- `status`
- `title_zh`
- `title_en`
- `summary_zh`
- `summary_en`
- `version_label`
- `last_reviewed_at`
- `review_due_at`
- `source_count`
- `source_publishers`
- `source_titles`

## Source export

Route: `GET /review/exports/sources.csv`

Columns:

- `id`
- `publisher`
- `title`
- `url`
- `publication_date`
- `access_date`
- `version_label`
- `linked_item_count`
- `linked_item_titles`

## Safety

- No patient-identifying data is exported.
- No diagnosis or treatment orders are generated.
- No credentials are exported.
- No trading/order behavior is added.
- Cells starting with spreadsheet formula prefixes are prefixed with a single quote.

## Acceptance checks

- Unauthenticated export requests redirect to `/review/login/?next=...`.
- Staff export requests return `text/csv`.
- Clinical item export includes bilingual item text and source coverage.
- Source export includes source metadata and linked item counts.
- Dashboard exposes export links only to staff users.
