# Git Publish Readiness Assistant Design

## Goal

Add a read-only Git publish readiness gate before Git remote setup so the deployment flow does not ask for `origin` and push while the clinical deployment package is still uncommitted or untracked.

## Context

Phase 10 added `Configure_Git_Remote.cmd`, but the current scoped deployment package still appears in Git as untracked:

```text
?? .planning/2026-06-22-clinical-differential-support/
?? clinical_differential_support/
?? docs/superpowers/
?? render.yaml
```

If the user sets a remote and pushes now, the remote may not contain the clinical app, docs, Render Blueprint, or planning evidence. The next-step program needs to catch that earlier and tell the user exactly what local Git packaging step comes first.

## Options Considered

1. Keep `ready_for_remote_setup` as the next action.
   - Too optimistic. It skips the fact that the deployable package is not committed.

2. Auto-stage and auto-commit the clinical package.
   - Too risky in a dirty shared repo. Commit scope and message need explicit human review.

3. Add a read-only publish readiness assistant before remote setup.
   - Recommended. It can inspect scoped Git status, explain what is uncommitted, provide exact scoped review/stage/commit commands, and avoid mutating Git state.

## Selected Design

Create `cds_core.git_publish_status` as a pure report builder with injected command execution. It will inspect only these deployment-package paths:

```text
clinical_differential_support
docs/superpowers
.planning/2026-06-22-clinical-differential-support
render.yaml
```

It will expose:

- `build_git_publish_status_report()`
- `format_git_publish_status_report()`
- constants for the scoped paths and Windows entrypoint

The default status will be:

- `publish_package_uncommitted`: scoped files have uncommitted or untracked changes
- `publish_package_ready`: scoped files are clean and ready for remote setup
- `git_unavailable`: Git cannot inspect the workspace

Add `clinical_differential_support/scripts/git_publish_status.py` and `clinical_differential_support/Publish_Status.cmd`. The wrapper is read-only and must not stage, commit, configure remotes, push, or handle credentials.

## Deployment Integration

Update `cds_core.deployment_status` to check publish readiness before Git remote. When the scoped package is not clean, Deployment Operations Center should return:

- status: `ready_for_publish_package`
- next action: `review_commit_publish_package`
- command: `clinical_differential_support\Publish_Status.cmd`

Only after the scoped package is clean should the flow advance to `ready_for_remote_setup` and `Configure_Git_Remote.cmd`.

## Safety Scope

- Read-only Git inspection only.
- No automatic `git add`, `git commit`, `git remote`, or `git push`.
- No credential, token, password, cloud account, Render auth, or Git host account handling.
- No clinical decision changes.
- No patient data, diagnosis orders, treatment orders, medication orders, broker APIs, trading flags, or live orders.

## Verification

Use TDD:

1. Add failing tests for publish-status parsing, CLI output, Windows wrapper safety, deployment-status integration, docs links, and final-verification expected count.
2. Verify RED fails before implementation.
3. Implement the assistant and deployment integration.
4. Verify targeted tests pass.
5. Run full Django regression, system check, live smoke, evidence recorder, Final_Check, CRLF, whitespace, credential, trading, and git-state scans.
