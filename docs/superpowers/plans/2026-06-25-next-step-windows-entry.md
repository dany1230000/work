# Next Step Windows Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a double-click Windows entry that tells the user exactly what to do next.

**Architecture:** Keep readiness logic in `cds_core.local_setup`. The batch file only wraps the existing assistant and handles pause behavior for double-click usage.

**Tech Stack:** Windows batch, Django template, Python selector tests, existing smoke and final evidence recorder scripts.

---

### Task 1: Red Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_local_setup_assistant.py`
- Modify: `clinical_differential_support/cds_core/tests/test_launch_guide.py`

- [x] Assert `Next_Step.cmd` exists and wraps `local_setup_assistant.py`.
- [x] Assert the batch entry has automated no-pause support and does not embed credential creation or test passwords.
- [x] Assert `/launch/` displays `Next_Step.cmd`.
- [x] Verify the initial red failure.

### Task 2: Windows Entry And Launch UI

**Files:**
- Add: `clinical_differential_support/Next_Step.cmd`
- Modify: `clinical_differential_support/cds_core/local_launch.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/launch_guide.html`

- [x] Add a UTF-8 batch wrapper that runs Local Setup Assistant.
- [x] Print assistant exit code and Launch Control URL.
- [x] Pause by default for double-click usage.
- [x] Support `CDS_NEXT_STEP_NO_PAUSE=1` for automated verification.
- [x] Render the Windows entry command on `/launch/`.

### Task 3: Docs And Verification

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `clinical_differential_support/QUICK_START.zh.md`
- Modify: `clinical_differential_support/cds_core/final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification_evidence_recorder.py`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [x] Update Quick Start and README with `Next_Step.cmd`.
- [x] Update final verification expected result from `163 tests pass` to `164 tests pass`.
- [x] Run targeted tests, direct `.cmd` check, full regression, Django check, live smoke, final evidence recorder, readable-content scan, and safety keyword scan.
- [x] Append final progress evidence.
