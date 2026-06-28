# Local Setup Assistant Design

## Goal

Add a safe local setup assistant command that tells the operator the exact next step, exit code, command, and URL before using the clinician-support MVP.

## Scope

- Keep all behavior inside `clinical_differential_support`.
- Reuse `cds_core.local_launch.build_local_launch_status()` so CLI and `/launch/` agree.
- Report staff reviewer readiness, final verification evidence, governed content data, next-action gate status, launch URL, and the next runnable/manual command.
- Do not create accounts, generate passwords, print passwords, save credentials, bypass login, store patient-identifying data, or add diagnosis/treatment/medication/trading execution behavior.

## Design

`cds_core.local_setup.build_local_setup_assistant_report()` returns:

- `status`: `ready` when local launch prerequisites are satisfied, otherwise `setup_required`;
- `exit_code`: `0` for ready, `2` when setup is still required;
- `next_step`: the same structured step currently shown by Launch Control;
- `launch_control_url`: the local `/launch/` URL;
- environment checks, manual blockers, final verification summary, next-action state, and explicit safety flags.

`scripts/local_setup_assistant.py` prints Chinese-first text by default and JSON with `--json`. It exits with the report exit code so shell users can see whether setup still needs manual action.

`/launch/` renders the assistant command near the top so the user can copy it directly.

## Verification

- Red/green tests for assistant report, formatter, and `/launch/` command visibility.
- Full Django regression after updating the final verification expected test count.
- Django system check, live smoke, direct assistant command check, direct `/launch/` HTML check, final evidence recorder, readable-content scan, and safety keyword scan.
