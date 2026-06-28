# Handoff smoke coverage design

## Goal

Expand the local smoke check so final handoff endpoints are covered by the same operational readiness command as the core app routes.

## Scope

- Add smoke checks for unauthenticated access to:
  - `/review/exports/handoff-report.md`
  - `/review/exports/handoff-bundle.zip`
- Verify both return HTTP 302 to reviewer login with the expected `next` parameter.
- Keep smoke check stdlib-only and non-authenticated.

## Behavior

`py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000` should include:

- `protected_handoff_report: ok`
- `protected_handoff_bundle: ok`

## Acceptance checks

- `build_check_plan()` contains the two handoff protected checks.
- Existing health/home/login/queue/source-create checks remain.
- Live smoke check passes with the expanded route list.
