# Local Setup Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local setup assistant command and surface it in Launch Control so the user always knows the next concrete action.

**Architecture:** Build a thin assistant selector on top of `cds_core.local_launch.build_local_launch_status()`. Keep readiness logic centralized and keep the CLI output summary-only and local-only.

**Tech Stack:** Django selector logic, stdlib CLI script, Django `TestCase`, existing smoke and final evidence recorder scripts.

---

### Task 1: Red Tests

**Files:**
- Add: `clinical_differential_support/cds_core/tests/test_local_setup_assistant.py`
- Modify: `clinical_differential_support/cds_core/tests/test_launch_guide.py`

- [x] Assert the assistant reports `setup_required`, exit code `2`, a `createsuperuser` next step, launch URL, and credential safety flags when no staff reviewer exists.
- [x] Assert the assistant reports `ready`, exit code `0`, and `Start_Local_Server.cmd` when staff reviewer and evidence are ready.
- [x] Assert `/launch/` renders `Local Setup Assistant` and `local_setup_assistant.py`.
- [x] Verify the initial red failure.

### Task 2: Assistant Selector And CLI

**Files:**
- Add: `clinical_differential_support/cds_core/local_setup.py`
- Add: `clinical_differential_support/scripts/local_setup_assistant.py`

- [x] Build the assistant report from local launch status.
- [x] Format Chinese-first next-step output with command, URL, environment checks, blockers, evidence, safety scope, and exit code.
- [x] Add `--json`, `--base-url`, and `--evidence-path` CLI options.
- [x] Return exit code `0` when ready and `2` when setup still requires action.

### Task 3: Launch Control Integration

**Files:**
- Modify: `clinical_differential_support/cds_core/local_launch.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/launch_guide.html`

- [x] Add structured `setup_assistant` state to the launch report.
- [x] Render the assistant command, status, exit code, and safety copy on `/launch/`.
- [x] Verify targeted launch and assistant tests pass.

### Task 4: Verification And Evidence

**Files:**
- Modify: `clinical_differential_support/cds_core/final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification_evidence_recorder.py`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [x] Update the full regression expected result from `160 tests pass` to `163 tests pass`.
- [x] Run full regression, Django check, live smoke, direct assistant command checks, direct `/launch/` HTML checks, final evidence recorder, readable-content scan, and safety keyword scan.
- [x] Append final progress evidence.
