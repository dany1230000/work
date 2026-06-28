# Final Verification Evidence Recorder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local evidence recorder that runs final verification commands and writes summary-only evidence consumed by the Final Verification Gate.

**Architecture:** Keep command execution in a standalone script under `clinical_differential_support/scripts/`. Keep web requests read-only by having `cds_core.final_verification` only load an existing JSON evidence file. Tests use an injected command runner.

**Tech Stack:** Django, unittest, stdlib subprocess/json/pathlib/tempfile.

---

### Task 1: Recorder Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_final_verification_evidence_recorder.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification.py`

- [ ] Add failing tests for evidence writing with an injected runner.
- [ ] Add failing tests for missing and verified evidence states in `build_final_verification_gate()`.
- [ ] Run `py -B .\clinical_differential_support\manage.py test cds_core.tests.test_final_verification_evidence_recorder cds_core.tests.test_final_verification -v 2`.

### Task 2: Recorder Implementation

**Files:**
- Create: `clinical_differential_support/scripts/record_final_verification_evidence.py`
- Modify: `clinical_differential_support/cds_core/final_verification.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/final_verification.html`

- [ ] Implement `record_final_verification_evidence()` with injectable runner.
- [ ] Implement command-output summarization without full stdout/stderr persistence.
- [ ] Add `load_latest_evidence()` and wire it into the final gate report.
- [ ] Render latest evidence status and recorder command on the staff page.
- [ ] Re-run targeted tests and confirm pass.

### Task 3: Verification

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Run full regression.
- [ ] Run Django system check.
- [ ] Restart local server.
- [ ] Run live smoke.
- [ ] Run the real evidence recorder.
- [ ] Verify live final gate reads the recorded evidence.
- [ ] Verify handoff bundle export and independent verifier.
- [ ] Record progress and run safety scan.
