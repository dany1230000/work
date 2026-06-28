# Launch Control Design

## Goal

Upgrade `/launch/` from a step guide into a local control panel that tells the user what is ready, what is blocked, and what to do next.

## Scope

- Keep all behavior local to `clinical_differential_support`.
- Extend the existing `cds_core.local_launch` selector instead of adding template-only state.
- Show environment checks, manual blockers, verification evidence, next-action status, commands, and URLs.
- Do not create accounts, generate passwords, store credentials, bypass login, store patient-identifying data, or add clinical/trading execution behavior.

## Design

`build_local_launch_status()` will add three structures:

- `operator_summary`: a compact status such as `needs_manual_setup`, `needs_verification`, or `ready_for_local_operation`.
- `environment_checks`: staff reviewer account, final verification evidence, governed content data, and next-action gate checks.
- `manual_blockers`: user-owned blockers such as creating a staff reviewer account. The password step remains explicitly manual.

`launch_guide.html` will render:

- a Local Control Panel header;
- environment check cards;
- manual blocker cards;
- verification evidence cards;
- the existing six-step flow with copyable commands.

## Verification

- Red/green tests for the selector and `/launch/` page.
- Smoke check must verify `Local Control Panel`.
- Full Django test suite, Django check, live smoke, direct HTML check, final evidence recorder, and progress log update.
