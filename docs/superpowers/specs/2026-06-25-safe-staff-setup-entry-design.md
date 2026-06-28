# Safe Staff Setup Entry Design

## Goal

Add a Windows-friendly, Chinese-first staff setup entry for the local clinician-support MVP so the Final Project Gate can tell the user exactly what to run when the only blocker is a missing local staff reviewer account.

## Scope

- Create `clinical_differential_support\Create_Staff_Reviewer.cmd` as the visible entry point for local staff account creation.
- Keep credential entry fully interactive through Django `createsuperuser`.
- Show the wrapper command in Final Gate, Launch Control, Local Setup Assistant output, README, and Quick Start.
- Keep the raw Django command visible as a secondary shell fallback for advanced use.
- Do not create accounts automatically.
- Do not generate, print, read, save, or pass passwords through environment variables or command-line flags.

## Architecture

The selector layer remains authoritative. `cds_core.local_launch` will expose both:

- `entry_command`: the user-friendly Windows command, `clinical_differential_support\Create_Staff_Reviewer.cmd`
- `raw_command`: the direct Django fallback, `py -B .\clinical_differential_support\manage.py createsuperuser`

`cds_core.project_completion` will use the Windows entry as the primary next action when the staff reviewer account is missing, while retaining the raw command in the report. Templates and text formatters will render both commands without duplicating credential logic.

## User Flow

1. User runs `clinical_differential_support\Final_Check.cmd`.
2. If status is `manual_setup_required`, Final Gate shows `Create_Staff_Reviewer.cmd` as the next command.
3. User runs or double-clicks `Create_Staff_Reviewer.cmd`.
4. Django prompts interactively for username, email, and password.
5. After the command exits, the wrapper runs the completion status check again.
6. User reruns `Final_Check.cmd` if needed, or opens `/completion/`.

## Safety Requirements

- The wrapper must not include a password literal, `DJANGO_SUPERUSER_PASSWORD`, `--password`, or test credentials.
- The wrapper may pass user-supplied arguments to `createsuperuser`; this supports `--help` verification without prompting.
- The wrapper must support `CDS_CREATE_STAFF_NO_PAUSE=1` for automated non-interactive checks.
- `.cmd` line endings must remain CRLF.

## Tests

- Regression tests prove the `.cmd` file exists, uses CRLF, wraps `createsuperuser`, runs the completion status command, and avoids password automation markers.
- Selector tests prove manual blockers and final next action expose `Create_Staff_Reviewer.cmd`.
- Page tests prove `/launch/` and `/completion/` render the wrapper command.
- Documentation tests prove README and Quick Start name the wrapper in the staff setup instructions.
