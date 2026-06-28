# Final Project Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a final-version gate that tells the user whether the project is final-complete or exactly what remains.

**Architecture:** Build `cds_core.project_completion` as a thin selector over existing local setup, local launch, final verification, and next-action state. Keep the page server-rendered and local-only, and keep the Windows wrapper as a batch-only launcher with no business logic.

**Tech Stack:** Django views/templates, Python selector/CLI, Windows batch, existing smoke and final evidence recorder scripts.

---

### Task 1: Red Tests

**Files:**
- Add: `clinical_differential_support/cds_core/tests/test_project_completion.py`
- Modify: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`
- Modify: `clinical_differential_support/cds_core/tests/test_launch_guide.py`

- [x] Assert the selector reports `manual_setup_required`, exit code `2`, and next action `create_staff_reviewer` when no staff reviewer exists.
- [x] Assert the selector reports `final_complete`, exit code `0`, and no manual blockers when staff reviewer and evidence are ready.
- [x] Assert the formatter includes `最終版完成判斷 / Final Project Gate`, status, exit code, command, and completion URL.
- [x] Assert `Final_Check.cmd` exists, wraps `project_completion_status.py`, supports `CDS_FINAL_CHECK_NO_PAUSE`, uses CRLF, and embeds no credentials.
- [x] Assert `/completion/`, smoke checks, and `/launch/` expose the final gate.
- [x] Verify the initial red failure.

### Task 2: Selector, CLI, And Wrapper

**Files:**
- Add: `clinical_differential_support/cds_core/project_completion.py`
- Add: `clinical_differential_support/scripts/project_completion_status.py`
- Add: `clinical_differential_support/Final_Check.cmd`

- [x] Build completion checks from existing launch/setup state.
- [x] Return `final_complete` with exit code `0` only when all checks pass.
- [x] Return `manual_setup_required` with exit code `2` while staff setup is missing.
- [x] Print Chinese-first text and support `--json`, `--base-url`, and `--evidence-path`.
- [x] Add a UTF-8 CRLF `.cmd` wrapper with no-pause automation support.

### Task 3: Web Integration

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Add: `clinical_differential_support/cds_core/templates/cds_core/project_completion.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/launch_guide.html`
- Modify: `clinical_differential_support/scripts/smoke_check.py`

- [x] Add public `/completion/` page.
- [x] Link the page in shared navigation.
- [x] Show `Final_Check.cmd` and `/completion/` on Launch Control.
- [x] Add `completion_gate` to live smoke checks.

### Task 4: Docs And Final Evidence

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `clinical_differential_support/QUICK_START.zh.md`
- Modify: `clinical_differential_support/cds_core/final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification_evidence_recorder.py`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [x] Document `Final_Check.cmd` and `/completion/`.
- [x] Update expected full-regression count after adding tests.
- [x] Run targeted tests, direct CLI/cmd, full regression, Django check, live smoke, final evidence recorder, direct HTML checks, CRLF check, readable-content scan, and safety keyword scan.
- [x] Append final progress evidence.
