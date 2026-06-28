# Local Launch Entry Design

## Goal

Provide a local entry point that tells the user what to do next after the project has passed the final verification gate.

## User Need

The user needs a practical program, not only tests or documentation. The local entry must answer:

- How do I start it?
- What URL do I open?
- Do I need a staff reviewer account first?
- If the project is ready, where do I see the next action and final verification status?
- If evidence is missing or failed, what command do I run next?

## Design

- Add a pure Django selector `build_local_launch_status()` for launch readiness and next-step routing.
- Add a formatter `format_local_launch_status()` for Chinese-first CLI output with English secondary text.
- Add `scripts/local_launch_status.py` as a local CLI status program.
- Add `Start_Local_Server.cmd` as the Windows double-click/local terminal launcher.
- Keep the launcher local-only and do not create accounts, credentials, or external services automatically.

## Next-Step Rules

1. If no staff reviewer account exists, next step is `create_staff_reviewer`.
2. If a staff account exists but final verification evidence is not verified, next step is `run_final_verification_recorder`.
3. If final verification evidence is verified, next step is `open_final_verification_gate`.

## Safety Scope

- Local clinician-reference support only.
- Staff-only governance routes remain staff-only.
- No patient-identifying data.
- No diagnosis, treatment, medication, broker, trading, order API, Shioaji, or credential behavior.
- The launcher prints commands and URLs only; it does not store secrets or bypass authentication.
