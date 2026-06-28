# Git Remote Setup Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a safe local Git remote setup assistant that turns Deployment Operations Center's `create_git_remote` action into an executable, validated, Chinese-first step without storing credentials or pushing unless explicitly requested.

**Architecture:** Add a pure `cds_core.git_remote_setup` module with injected command execution, expose it through a CLI script and Windows wrapper, then wire Deployment Operations Center and docs to point to that wrapper. Keep all behavior outside clinical decision logic.

**Tech Stack:** Python standard library, Django test runner, existing Windows `.cmd` entrypoint pattern, existing deployment status report/template/docs.

---

## File Structure

- Create: `clinical_differential_support/cds_core/git_remote_setup.py`
  - Validates remote URLs, inspects origin, runs safe Git commands through an injected runner, and formats reports.
- Create: `clinical_differential_support/scripts/configure_git_remote.py`
  - CLI wrapper with `--remote-url`, `--push`, and `--json`.
- Create: `clinical_differential_support/Configure_Git_Remote.cmd`
  - Windows entrypoint with no credential handling and `CDS_GIT_REMOTE_NO_PAUSE` support.
- Create: `clinical_differential_support/cds_core/tests/test_git_remote_setup.py`
  - Red-green tests for behavior, CLI, wrapper, deployment integration, and docs.
- Modify: `clinical_differential_support/cds_core/deployment_status.py`
  - Change `ready_for_remote_setup` next action to the assistant command.
- Modify: `clinical_differential_support/cds_core/tests/test_deployment_status.py`
  - Update expectations from raw Git commands to `Configure_Git_Remote.cmd`.
- Modify: `clinical_differential_support/README.md`, `clinical_differential_support/QUICK_START.zh.md`, `clinical_differential_support/DEPLOYMENT.md`
  - Document the next step and push boundary.
- Modify: `clinical_differential_support/cds_core/final_verification.py`, `clinical_differential_support/cds_core/tests/test_final_verification.py`
  - Update expected full-regression count after adding tests.
- Modify: `.planning/2026-06-22-clinical-differential-support/task_plan.md` and `progress.md`
  - Track Phase 10 and evidence.

### Task 1: Write RED Tests

- [x] **Step 1: Add `test_git_remote_setup.py`**

Add tests that expect:

```python
report["status"] == "remote_url_required"
report["next_action"]["command"].startswith("clinical_differential_support\\Configure_Git_Remote.cmd")
report["status"] == "invalid_remote_url"
report["status"] == "remote_configured"
report["status"] == "remote_conflict"
report["status"] == "remote_pushed"
```

- [x] **Step 2: Update existing deployment status tests**

Expect `Configure_Git_Remote.cmd --remote-url <your-repo-url>` instead of raw `git remote add origin`.

- [x] **Step 3: Verify RED**

Run:

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_git_remote_setup cds_core.tests.test_deployment_status -v 2
```

Expected: FAIL because `cds_core.git_remote_setup`, `Configure_Git_Remote.cmd`, and the updated deployment action do not exist yet.

### Task 2: Implement Assistant

- [x] **Step 1: Add `cds_core.git_remote_setup`**

Implement:

```python
build_git_remote_setup_report(remote_url="", push=False, workspace_root=None, command_runner=default_command_runner)
format_git_remote_setup_report(report)
```

The module must reject unsupported hosts and HTTPS URLs with embedded credentials, refuse remote conflicts, add `origin` only when safe, and push only with `push=True`.

- [x] **Step 2: Add CLI script**

Implement `configure_git_remote.py` with:

```powershell
--remote-url <url>
--push
--json
```

- [x] **Step 3: Add Windows wrapper**

Create `Configure_Git_Remote.cmd` using CRLF line endings and the existing pause/no-pause pattern.

- [x] **Step 4: Verify GREEN targeted tests**

Run the same targeted command and require all targeted tests to pass.

### Task 3: Integrate Deployment Surfaces

- [x] **Step 1: Update `deployment_status.py`**

For `ready_for_remote_setup`, set command to:

```powershell
clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>
```

Mention `--push` only as an explicit optional follow-up.

- [x] **Step 2: Update docs**

Add the assistant to README, Quick Start, and DEPLOYMENT. Include no credentials or tokens.

- [x] **Step 3: Update expected regression count**

If this phase adds eight tests, change expected full regression from `187 tests pass` to `195 tests pass`.

### Task 4: Final Verification

- [x] **Step 1: Run targeted tests**

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_git_remote_setup cds_core.tests.test_deployment_status cds_core.tests.test_final_verification -v 2
```

- [x] **Step 2: Run full regression and system check**

```powershell
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
```

- [x] **Step 3: Run assistant without URL**

```powershell
$env:CDS_GIT_REMOTE_NO_PAUSE='1'
clinical_differential_support\Configure_Git_Remote.cmd --json
```

Expected: exit code `2`, status `remote_url_required`, no credential output.

- [x] **Step 4: Run deployment and final checks**

```powershell
py -B .\clinical_differential_support\scripts\deployment_status.py --json
py -B .\clinical_differential_support\scripts\record_final_verification_evidence.py --overwrite
$env:CDS_FINAL_CHECK_NO_PAUSE='1'
clinical_differential_support\Final_Check.cmd
```

- [x] **Step 5: Run quality scans**

```powershell
git diff --check -- clinical_differential_support docs .planning render.yaml
```

Scan edited files for credential markers and trading/order markers. Treat explicit prohibition text as allowed and any executable broker/order behavior as a blocker.

## Completion Evidence

- RED targeted tests failed for the missing assistant.
- GREEN targeted tests passed after implementation.
- Full regression passed with the updated test count.
- `Configure_Git_Remote.cmd --json` returns `remote_url_required` when no URL is provided.
- Deployment status points to `Configure_Git_Remote.cmd`.
- `Final_Check.cmd` remains `final_complete`.
- No credential, patient-data, diagnosis-order, treatment-order, medication-order, trading, broker, or live-order behavior was added.

## Completion Notes

- RED command failed as expected before implementation: `py -B .\clinical_differential_support\manage.py test cds_core.tests.test_git_remote_setup cds_core.tests.test_deployment_status -v 2`.
- GREEN targeted command passed: 16 tests.
- Final targeted command passed: 24 tests.
- Full regression passed: 195 tests.
- `Configure_Git_Remote.cmd --json` returned `remote_url_required`, exit code `2`, and only inspected `git remote -v`.
- Deployment status now reports `ready_for_remote_setup` with command `clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>`.
- Final verification evidence was rewritten and reports `195 tests pass`.
- `Final_Check.cmd` remains `final_complete`, exit code `0`.
- `git remote -v` still has no output, so no remote was configured without a user-provided URL.
