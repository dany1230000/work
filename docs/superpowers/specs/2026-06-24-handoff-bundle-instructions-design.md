# Handoff bundle instructions design

## Goal

Make the staff handoff ZIP self-contained by including a human-readable instructions file inside the archive.

## Scope

- Add `handoff-instructions.md` to `handoff-bundle.zip`.
- Include the file in `manifest.json` with byte size and SHA-256 metadata.
- Update the local verifier so bundles missing `handoff-instructions.md` fail validation.
- Keep the instructions Chinese-first with English support.
- Keep the instructions summary/procedure-only: no detailed clinical item content, no patient data, no credentials.

## Instructions Content

`handoff-instructions.md` should explain:

- The bundle is staff-only and content-governance-only.
- How to verify the ZIP with `verify_handoff_bundle.py`.
- What each bundle file is for.
- How to regenerate the ZIP locally with `export_handoff_bundle.py`.
- The safety boundary: not clinical deployment approval, no diagnosis/treatment orders, no patient-identifying data, no credentials, no trading/order API.

## Acceptance checks

- Staff ZIP export contains `handoff-instructions.md`.
- `manifest.json` contains an entry for `handoff-instructions.md` with content type, byte size, and SHA-256.
- The instructions contain Chinese-first labels plus English support text.
- The verifier accepts valid bundles containing the instructions file.
- The verifier rejects bundles missing `handoff-instructions.md`.
