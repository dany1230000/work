# Handoff bundle design

## Goal

新增 staff-only ZIP 交付包，讓 reviewer 或接手工程師可以一次下載交付所需檔案。此階段不新增臨床推論、不新增外部套件，只重用已驗證的 Markdown、JSON、CSV builders。

## Scope

- Add `GET /review/exports/handoff-bundle.zip`.
- Include `manifest.json`, `handoff-report.md`, `release-evidence.json`, `clinical-items.csv`, and `sources.csv`.
- Link the ZIP from `/review/readiness/`.
- Add route references to the release evidence export map and README.
- Keep the bundle staff-only through the existing reviewer guard.

## Bundle content

The ZIP contains:

- `manifest.json`: machine-readable bundle metadata, file list, readiness summary, validation summary, and safety-scope assertions.
- `handoff-report.md`: summary-only human-readable handoff report.
- `release-evidence.json`: summary-only machine-readable evidence package.
- `clinical-items.csv`: staff-only clinical item governance export.
- `sources.csv`: staff-only source governance export.

The bundle is a staff handoff artifact. The CSV files may include governance details already exposed by the existing staff-only CSV export routes. The Markdown report and release evidence JSON remain summary-only.

## Acceptance checks

- Anonymous requests redirect to `/review/login/?next=/review/exports/handoff-bundle.zip`.
- Staff requests return `application/zip` with `handoff-bundle.zip` in `Content-Disposition`.
- The ZIP contains all expected filenames.
- `manifest.json` declares `package_type: handoff_bundle`, `staff_only: true`, route references, readiness counts, and safety-scope assertions.
- The readiness page links to the ZIP bundle.
