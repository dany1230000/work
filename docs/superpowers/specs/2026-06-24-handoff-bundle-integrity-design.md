# Handoff bundle integrity design

## Goal

Upgrade the staff-only handoff ZIP manifest with integrity metadata so a reviewer or receiving engineer can verify the downloaded payload files after transfer.

## Scope

- Add SHA-256 and byte-size metadata for ZIP payload files.
- Cover `handoff-report.md`, `release-evidence.json`, `clinical-items.csv`, and `sources.csv`.
- Mark `manifest.json` as integrity-excluded to avoid a self-referential manifest hash.
- Keep the route, access control, CSV export content, clinical logic, and safety scope unchanged.

## Manifest design

`manifest.json` keeps the current top-level summary fields and file list. Each non-manifest file entry gains:

- `byte_size`: UTF-8 byte length written into the ZIP.
- `sha256`: lowercase hexadecimal SHA-256 of the exact bytes written into the ZIP.

The `manifest.json` file entry gains:

- `integrity_excluded: true`
- `integrity_note: "Manifest hashes exclude manifest.json to avoid a self-referential digest."`

## Acceptance checks

- Bundle tests verify every non-manifest file entry has a positive byte size and a 64-character SHA-256 digest.
- Bundle tests recompute each digest from ZIP contents and match it to the manifest.
- Bundle tests verify the recorded byte size equals the ZIP entry bytes.
- Existing staff-only redirect, ZIP content, safety-field omission, and readiness-page link tests remain green.
