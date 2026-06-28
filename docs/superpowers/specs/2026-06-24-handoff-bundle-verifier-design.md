# Handoff bundle verifier design

## Goal

Add a local verifier for downloaded staff-only handoff bundles so the receiving reviewer or engineer can prove the ZIP contents match `manifest.json` after transfer.

## Scope

- Add `clinical_differential_support/scripts/verify_handoff_bundle.py`.
- Verify `handoff-bundle.zip` using only Python standard library modules.
- Validate `manifest.json`, expected package type, required file entries, byte sizes, SHA-256 digests, and manifest self-hash exclusion.
- Provide a CLI exit code suitable for handoff checklists.
- Document the verifier in the README verification section.

## Behavior

`verify_bundle(path)` returns a structured result with:

- `ok`: boolean pass/fail.
- `messages`: human-readable verification details.
- `errors`: human-readable failure details.

The CLI:

```powershell
py -B clinical_differential_support\scripts\verify_handoff_bundle.py path\to\handoff-bundle.zip
```

returns exit code `0` for a valid bundle and `1` for invalid, missing, unreadable, tampered, or incomplete bundles.

## Acceptance checks

- A bundle produced by `build_handoff_bundle_zip()` verifies successfully.
- Tampering with a payload file while keeping the original manifest fails SHA-256 validation.
- Removing a payload file fails missing-file validation.
- `main([path])` returns `0` for a valid bundle and `1` for an invalid bundle.
- The README documents the verifier command.
