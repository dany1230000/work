# Scoped Deployment Package Commit Design

## Objective

Move the clinical deployment flow from `ready_for_publish_package` to `ready_for_remote_setup` by creating local Git commit(s) for the reviewed deployment package and its completion record.

## Current State

`clinical_differential_support\Publish_Status.cmd` reports `publish_package_uncommitted` because the scoped deployment package is still untracked:

- `.planning/2026-06-22-clinical-differential-support/`
- `clinical_differential_support/`
- `docs/superpowers/`
- `render.yaml`

Deployment Status correctly stops at `ready_for_publish_package` before any remote setup or push.

## Options Considered

### Option A: Commit the whole scoped directory as-is

This is fast, but it would include local verification artifacts such as logs, JSON snapshots, and zip exports under `clinical_differential_support\verification_artifacts\`. Those files are local evidence outputs, not source or deployment configuration.

### Option B: Curated scoped commit with artifact ignore

Add `verification_artifacts/` to the clinical app `.gitignore`, then stage only the allowed product, documentation, planning, and deployment paths. This preserves the current local evidence files for Final_Check while keeping generated artifacts out of Git. This is the selected approach.

### Option C: Stop for manual review

This is safest when ownership is unclear, but the user explicitly requested autonomous continuation after the publish-readiness gate identified the exact next action.

## Selected Design

Use local Git commit(s) with this boundary:

- Allowed stage paths:
  - `clinical_differential_support`
  - `docs/superpowers`
  - `.planning/2026-06-22-clinical-differential-support`
  - `render.yaml`
- Explicitly ignored local artifacts:
  - `clinical_differential_support/verification_artifacts/`
- Forbidden operations:
  - no Git remote configuration
  - no push
  - no cloud account creation
  - no Render authentication
  - no credentials
  - no TWQuant or ShopReport staging

## Verification

Before commit:

- `clinical_differential_support\Publish_Status.cmd --json` reports the current dirty scoped package.
- Full Django regression still reports `203 tests pass`.
- `py -B .\clinical_differential_support\manage.py check` has no issues.
- Credential and trading/order scans pass or only show explicit prohibition text.
- `git diff --check -- clinical_differential_support docs .planning render.yaml` has no whitespace errors.

After commit:

- `clinical_differential_support\Publish_Status.cmd --json` reports `publish_package_ready`.
- Deployment Status advances to `ready_for_remote_setup`.
- `git status --short -- clinical_differential_support docs/superpowers .planning/2026-06-22-clinical-differential-support render.yaml` is clean.
- `git remote -v` remains unchanged.
- `clinical_differential_support\Final_Check.cmd` remains `final_complete`.

## Planning Evidence Commit

If post-commit verification requires updating `.planning` records, create a second local documentation/planning commit inside the same allowed scope. The final state must be a clean scoped package and Deployment Status must still report `ready_for_remote_setup`.

## Stop Condition

Stop after local commit(s) and post-commit verification if there is still no remote URL, no Render authentication, or no explicit cloud credential context. The next external step remains remote setup through `clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>`.
