# Deployment Readiness Implementation Plan

## Objective

Move `clinical_differential_support` from local-only operation to deploy-ready operation without performing an unauthorised public clinical launch.

## Phase 1: Planning and Red Tests

Status: complete

- Add this plan and the design note.
- Add failing deployment-readiness tests covering settings, dependencies, Render Blueprint, build script, and deployment docs.
- Run the targeted test file and confirm the expected failures.

## Phase 2: Production Runtime Configuration

Status: complete

- Update Django settings to support environment-driven secret, debug, hosts, CSRF origins, database URL, HTTPS proxy, secure cookies, and WhiteNoise static files.
- Update Python dependencies for Render runtime support.
- Keep local defaults unchanged for existing localhost workflows.

## Phase 3: Render Blueprint and Build Assets

Status: complete

- Add root `render.yaml` with Python web service, PostgreSQL database, build command, start command, health check, and generated secret.
- Add `clinical_differential_support/build.sh` for install, collectstatic, migrations, and fixture loading.
- Ignore generated static output.

## Phase 4: Deployment Documentation

Status: complete

- Add Chinese-first `DEPLOYMENT.md` with English labels.
- Link deployment docs from README and Quick Start.
- State the remaining external blockers truthfully: Git remote/cloud auth/secrets.

## Phase 5: Verification and Evidence

Status: complete

- Run targeted deployment tests.
- Run full Django tests.
- Run Django production check and collectstatic with production-style env vars.
- Run Final_Check and smoke check.
- Run whitespace, credential, and forbidden marker scans.
- Update planning/progress files with results.

## Results

- Targeted deployment tests: 6 passed.
- Full Django regression: 179 passed.
- Django local system check: no issues.
- Django production deploy check: no issues with production-style env.
- Production collectstatic: 127 files copied and 635 post-processed.
- Final evidence recorder: 4 commands passed and evidence was rewritten.
- Final_Check: `final_complete`, exit 0.
- Live smoke: all route checks passed.
- Deployment artifact scans: no blocked credential, trading, or order markers.
- Public deployment was not attempted because no Git remote is configured and Render CLI is not installed.

## Acceptance Criteria

- Deployment-readiness tests pass.
- Full regression passes.
- Production-mode static collection succeeds.
- `render.yaml` does not embed credentials and references Render-managed database/secret values.
- Deployment documentation gives the operator concrete next steps without claiming the app is already publicly deployed.
