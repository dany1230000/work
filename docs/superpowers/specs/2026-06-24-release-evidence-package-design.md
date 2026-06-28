# Release evidence package design

## Goal

Add a staff-only JSON evidence package for reviewer handoff. The package summarizes governance readiness, validation status, safety scope, and export routes without exposing detailed clinical text.

## Scope

- Add `GET /review/exports/release-evidence.json`.
- Summarize readiness counts from the existing release readiness selector.
- Include safety-scope assertions and export route references.
- Link the package from the release readiness report.
- Keep the package staff-only through reviewer access.

## Package content

The JSON package includes:

- `package_type`: `release_evidence`
- `service`: `clinical_differential_support`
- `generated_at`
- `staff_only`
- `readiness`
- `validation`
- `governance_record_counts`
- `exports`
- `safety_scope`

The package intentionally does not include clinical item titles, summaries, source URLs, patient-like case details, credentials, diagnosis orders, treatment orders, or trading/order fields.

## Acceptance checks

- Anonymous requests redirect to `/review/login/?next=/review/exports/release-evidence.json`.
- Staff requests return JSON with readiness counts and export route references.
- The JSON response does not include fixture clinical text such as `Thunderclap headache`.
- The release readiness page links to the evidence package.
