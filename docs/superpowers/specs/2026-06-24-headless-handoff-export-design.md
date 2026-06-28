# Headless handoff export design

## Goal

Add a local command-line exporter that writes the staff handoff bundle directly from the local Django database and verifies it immediately. This lets a handoff owner produce the final ZIP without using a browser session.

## Scope

- Add `clinical_differential_support/scripts/export_handoff_bundle.py`.
- Reuse `cds_core.bundle.build_handoff_bundle_zip()` and `scripts.verify_handoff_bundle.verify_bundle()`.
- Support `--output`, `--overwrite`, and `--no-verify`.
- Document the command in README.
- Keep server routes and staff-only web access unchanged.

## Behavior

Default command:

```powershell
py -B clinical_differential_support\scripts\export_handoff_bundle.py --output handoff-bundle.zip --overwrite
```

The script:

- Boots Django using the local project settings.
- Writes `handoff-bundle.zip` to the requested path.
- Refuses to overwrite an existing file unless `--overwrite` is passed.
- Runs the P15 verifier unless `--no-verify` is passed.
- Returns exit code `0` only when export and verification pass.

## Acceptance checks

- `export_bundle(path, overwrite=True)` writes a valid ZIP that passes `verify_bundle(path)`.
- `export_bundle(path, overwrite=False)` refuses to replace an existing file.
- `main([...])` returns `0` for a verified export.
- README documents the headless export command.
