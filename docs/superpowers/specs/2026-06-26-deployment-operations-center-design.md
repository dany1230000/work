# Deployment Operations Center Design

## Goal

Add a step-by-step deployment operations center so the user can always see the next concrete deployment action after local final-complete.

## Scope

- Add a deployment status report that checks local deploy readiness artifacts and external blockers.
- Add a CLI and Windows entrypoint that print text or JSON.
- Add a public local web page that shows the deployment checklist and next action.
- Link the new page from Launch Control, Final Project Gate, README, Quick Start, and Deployment docs.
- Keep actual public deployment out of scope until a Git remote and Render authentication exist.

## Non-Goals

- No automatic creation of GitHub/GitLab/Bitbucket repositories.
- No Render account login automation.
- No credential storage, password printing, or staff account automation.
- No clinical production approval.
- No patient data, diagnosis orders, treatment orders, medication orders, or trading behavior.

## Design

The deployment report will live in `cds_core.deployment_status`. It will inspect the repo using read-only local checks: `render.yaml`, `build.sh`, `DEPLOYMENT.md`, deployment dependencies, Git remote state, Render CLI availability, and final local completion state. It will produce a structured report with `status`, `exit_code`, `checks`, `blockers`, `steps`, and `next_action`.

The report will use conservative statuses:

- `ready_for_remote_setup`: app is deploy-ready locally but no Git remote exists.
- `ready_for_render_auth`: Git remote exists but Render CLI/auth is not ready.
- `ready_for_dashboard_deploy`: local artifacts, remote, and Render CLI are present.
- `deployed_verification_required`: future state for a user-provided deployed URL.

The first implementation will stop at external blockers because the current environment has no Git remote and no Render CLI.

## Verification

Use TDD:

- status report tests fail first
- CLI tests fail first
- Windows entrypoint/docs/page/smoke tests fail first
- implementation makes them pass
- full regression, Django check, live smoke, Final_Check, whitespace, CRLF, and safety scans close the phase
