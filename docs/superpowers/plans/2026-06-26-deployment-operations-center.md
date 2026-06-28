# Deployment Operations Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local deployment operations center that tells the user the exact next deploy step and why the project is not publicly deployed yet.

**Architecture:** Add a pure report builder in `cds_core.deployment_status`, expose it through a CLI script, a Windows `.cmd` wrapper, and a public Django route/template. Integrate it into existing launch/completion/docs surfaces without changing clinical workflows.

**Tech Stack:** Django 5.2, Python stdlib subprocess/path checks, Windows `.cmd`, existing Django templates and tests.

---

### Task 1: Red Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_deployment_status.py`
- Modify: `clinical_differential_support/cds_core/tests/test_launch_guide.py`
- Modify: `clinical_differential_support/cds_core/tests/test_project_completion.py`
- Modify: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`

- [x] Write failing tests for a structured deployment status report.
- [x] Write failing tests for CLI JSON/text output and Windows entrypoint safety.
- [x] Write failing tests for `/deployment/`, Launch Control link, Final Gate link, docs links, and smoke route inclusion.
- [x] Run targeted tests and confirm expected failures.

### Task 2: Report Builder and CLI

**Files:**
- Create: `clinical_differential_support/cds_core/deployment_status.py`
- Create: `clinical_differential_support/scripts/deployment_status.py`
- Create: `clinical_differential_support/Deploy_Status.cmd`

- [x] Implement read-only local checks for deploy artifacts, Git remote, Render CLI, local completion, and safety flags.
- [x] Implement text formatter and JSON CLI output.
- [x] Implement Windows wrapper without credential handling.
- [x] Run targeted report/CLI tests.

### Task 3: Web Route and UI

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Create: `clinical_differential_support/cds_core/templates/cds_core/deployment_status.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/launch_guide.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/project_completion.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`

- [x] Add `/deployment/` public route.
- [x] Render checks, blockers, steps, next action, and copyable command.
- [x] Link deployment page from launch/final/nav.
- [x] Run targeted web tests.

### Task 4: Docs and Smoke

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `clinical_differential_support/QUICK_START.zh.md`
- Modify: `clinical_differential_support/DEPLOYMENT.md`
- Modify: `clinical_differential_support/scripts/smoke_check.py`

- [x] Document `Deploy_Status.cmd` and `/deployment/`.
- [x] Add deployment status route to smoke check.
- [x] Run smoke-related tests.

### Task 5: Verification

**Files:**
- Modify: `clinical_differential_support/cds_core/final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification.py`
- Modify: `.planning/2026-06-22-clinical-differential-support/task_plan.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [x] Update expected full-regression count after new tests.
- [x] Run targeted tests.
- [x] Run full regression.
- [x] Run `manage.py check`, live smoke, evidence recorder, Final_Check, whitespace check, CRLF check, and safety scans.
- [x] Mark Phase 9 complete only after fresh verification evidence.

## Results

- RED targeted tests first failed because deployment status module, CLI, Windows entrypoint, web route, docs links, and smoke route did not exist.
- GREEN targeted tests passed: 25 tests.
- Full regression passed: 187 tests.
- Django system check passed.
- Live smoke passed, including `deployment_status: ok`.
- Final verification evidence was rewritten and reports `187 tests pass`.
- `Final_Check.cmd` remains `final_complete`, exit 0.
- Deployment status reports `ready_for_remote_setup`, exit code 2, with next action `create_git_remote`.
- CRLF check passed for `Deploy_Status.cmd`.
- Whitespace check passed.
- Credential scan found no blocked markers.
- Trading/order scan found only explicit safety-prohibition text.
- Public deployment remains blocked by missing Git remote and missing Render CLI/auth.
