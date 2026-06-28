# Final Project Gate Design

## Goal

Add a local final-version gate that answers one question: is the project final-complete, or is there still a concrete next step?

## Scope

- Keep all behavior inside `clinical_differential_support`.
- Add a public local `/completion/` page, CLI script, and Windows double-click wrapper.
- Reuse existing launch/setup/final-verification selectors; do not duplicate clinical or governance logic.
- Output Chinese-first status with English secondary labels.
- Do not create accounts, generate passwords, print passwords, store credentials, bypass login, store patient-identifying data, or add diagnosis/treatment/medication/trading execution behavior.

## Completion Rules

The gate reports `final_complete` only when all completion checks pass:

- staff reviewer account exists;
- final verification gate is `ready_for_final_verification`;
- latest final evidence is `verified`;
- final evidence failed command count is `0`;
- governed content data is loaded;
- next-action gate is `ready_for_regression_gate`.

If staff setup is still missing, the gate reports `manual_setup_required` with exit code `2` and points to the existing `createsuperuser` manual step.

## Components

- `cds_core.project_completion`: builds and formats the final project gate report.
- `scripts/project_completion_status.py`: prints the report as text or JSON and exits with the report exit code.
- `Final_Check.cmd`: double-click Windows wrapper for the CLI. It pauses by default and skips pause when `CDS_FINAL_CHECK_NO_PAUSE=1`.
- `/completion/`: public local page that renders the same report.
- `/launch/`: links to the final project gate and the `Final_Check.cmd` command.

## Verification

- Red/green selector, formatter, route, smoke, and Windows-wrapper tests.
- Direct CLI and `.cmd` checks.
- Full Django regression, Django check, live smoke, final evidence recorder, direct HTML checks, readable-content scan, CRLF check, safety keyword scan, and progress log update.
