# Git Publish Readiness Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only Git publish readiness assistant that blocks the deployment flow before remote setup when the scoped clinical deployment package is uncommitted or untracked.

**Architecture:** Add a pure `cds_core.git_publish_status` module with injected command execution, expose it through a CLI script and Windows wrapper, then integrate its result into `cds_core.deployment_status` before the Git remote check. Keep all behavior read-only.

**Tech Stack:** Python standard library, Django test runner, existing Windows `.cmd` wrapper pattern, existing Deployment Operations Center report/template/docs.

---

## File Structure

- Create: `clinical_differential_support/cds_core/git_publish_status.py`
  - Parses scoped `git status --short` output and returns publish readiness.
- Create: `clinical_differential_support/scripts/git_publish_status.py`
  - CLI wrapper with text and `--json` output.
- Create: `clinical_differential_support/Publish_Status.cmd`
  - Windows read-only entrypoint with `CDS_PUBLISH_STATUS_NO_PAUSE`.
- Create: `clinical_differential_support/cds_core/tests/test_git_publish_status.py`
  - Red-green tests for status parsing, CLI, wrapper, deployment integration, and docs.
- Modify: `clinical_differential_support/cds_core/deployment_status.py`
  - Check publish readiness before Git remote and add a new deployment status.
- Modify: `clinical_differential_support/cds_core/tests/test_deployment_status.py`
  - Update expectations to cover publish-package gating and the clean-path remote stage.
- Modify: `clinical_differential_support/README.md`, `clinical_differential_support/QUICK_START.zh.md`, `clinical_differential_support/DEPLOYMENT.md`
  - Document `Publish_Status.cmd` before `Configure_Git_Remote.cmd`.
- Modify: `clinical_differential_support/cds_core/final_verification.py`, `clinical_differential_support/cds_core/tests/test_final_verification.py`
  - Update expected full-regression count after adding tests.
- Modify: `.planning/2026-06-22-clinical-differential-support/task_plan.md` and `progress.md`
  - Track Phase 11 and evidence.

### Task 1: Write RED Tests

- [x] **Step 1: Add publish status tests**

Expect:

```python
report["status"] == "publish_package_uncommitted"
report["dirty_count"] == 4
report["next_action"]["command"] == "clinical_differential_support\\Publish_Status.cmd"
```

- [x] **Step 2: Add clean-path tests**

Expect a clean scoped package to return:

```python
report["status"] == "publish_package_ready"
report["next_action"]["action_id"] == "configure_git_remote"
```

- [x] **Step 3: Add deployment integration expectations**

When scoped files are dirty, Deployment Operations Center should return `ready_for_publish_package` before `ready_for_remote_setup`.

- [x] **Step 4: Verify RED**

Run:

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_git_publish_status cds_core.tests.test_deployment_status -v 2
```

Expected: FAIL because `cds_core.git_publish_status`, `scripts\git_publish_status.py`, `Publish_Status.cmd`, and deployment integration do not exist.

### Task 2: Implement Assistant

- [x] **Step 1: Add `cds_core.git_publish_status`**

Implement:

```python
build_git_publish_status_report(workspace_root=None, command_runner=default_command_runner)
format_git_publish_status_report(report)
```

It must run only:

```powershell
git status --short -- clinical_differential_support docs/superpowers .planning/2026-06-22-clinical-differential-support render.yaml
git branch --show-current
```

- [x] **Step 2: Add CLI script and Windows wrapper**

Add text/JSON CLI output and `Publish_Status.cmd` with CRLF line endings.

- [x] **Step 3: Verify targeted tests pass**

Run the RED command again and require all tests to pass.

### Task 3: Integrate Deployment Status and Docs

- [x] **Step 1: Update deployment status**

Add deployment status `ready_for_publish_package` before `ready_for_remote_setup`.

- [x] **Step 2: Update docs**

Document that the package must be reviewed/staged/committed before remote setup.

- [x] **Step 3: Update final verification expected count**

If this phase adds eight tests, change expected full regression from `195 tests pass` to `203 tests pass`.

### Task 4: Final Verification

- [x] **Step 1: Run targeted tests**

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_git_publish_status cds_core.tests.test_deployment_status cds_core.tests.test_final_verification -v 2
```

- [x] **Step 2: Run full regression and system check**

```powershell
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
```

- [x] **Step 3: Run publish and deployment status commands**

```powershell
$env:CDS_PUBLISH_STATUS_NO_PAUSE='1'
clinical_differential_support\Publish_Status.cmd --json
py -B .\clinical_differential_support\scripts\deployment_status.py --json
```

- [x] **Step 4: Run smoke, evidence, and final gate**

```powershell
py -B .\clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
py -B .\clinical_differential_support\scripts\record_final_verification_evidence.py --overwrite
$env:CDS_FINAL_CHECK_NO_PAUSE='1'
clinical_differential_support\Final_Check.cmd
```

- [x] **Step 5: Run quality scans**

```powershell
git diff --check -- clinical_differential_support docs .planning render.yaml
```

Check CRLF for `Publish_Status.cmd`, credential markers, trading/order markers, and confirm `git remote -v` is still unchanged.

## Completion Evidence

- RED targeted tests failed before implementation.
- GREEN targeted tests passed after implementation.
- Full regression passed with the updated test count.
- `Publish_Status.cmd --json` reports current scoped uncommitted files without mutating Git state.
- Deployment status reports `ready_for_publish_package` before remote setup when scoped files are uncommitted.
- No credential, Git mutation, patient-data, clinical-order, trading, broker, or live-order behavior was added.
- Final regression after the JSON wrapper fix: `203 tests pass`.
- `Publish_Status.cmd --json` now emits parseable JSON only and returns expected exit code `2` for the current uncommitted scoped package.
- `Final_Check.cmd` remains `final_complete` for local product completion while deployment status correctly stops at `ready_for_publish_package`.
