# Next Step Windows Entry Design

## Goal

Add a Windows double-click entry point that runs the Local Setup Assistant and shows the user the next concrete action without requiring them to remember a Python command.

## Scope

- Add `clinical_differential_support\Next_Step.cmd`.
- Keep all behavior inside `clinical_differential_support`.
- Reuse `scripts\local_setup_assistant.py` instead of duplicating readiness logic in batch.
- Show the entry point on `/launch/`, README, and Quick Start.
- Do not create accounts, generate passwords, print passwords, store credentials, bypass login, store patient-identifying data, or add diagnosis/treatment/medication/trading execution behavior.

## Design

`Next_Step.cmd`:

- switches to UTF-8 console output;
- changes the working directory to the workspace root;
- runs `py -B .\clinical_differential_support\scripts\local_setup_assistant.py`;
- prints the assistant exit code and Launch Control URL;
- pauses by default for double-click usage;
- skips pause when `CDS_NEXT_STEP_NO_PAUSE=1` is set for automated verification.

`cds_core.local_launch.build_local_launch_status()` exposes the Windows entry command so `/launch/` can render it next to the shell command.

## Verification

- Red/green tests for the batch entry file and `/launch/` visibility.
- Direct `.cmd` check with `CDS_NEXT_STEP_NO_PAUSE=1`.
- Full Django regression, Django check, live smoke, direct `/launch/` HTML check, final evidence recorder, readable-content scan, and safety keyword scan.
