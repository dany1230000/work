# Launch Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `/launch/` into a local control panel with environment checks, manual blockers, verification evidence, and copyable commands.

**Architecture:** Extend `cds_core.local_launch.build_local_launch_status()` so the template renders structured state instead of calculating readiness itself. Keep the UI server-rendered and local-only.

**Tech Stack:** Django templates, Python selector logic, Django `TestCase`, stdlib smoke checks.

---

### Task 1: Selector State

**Files:**
- Modify: `clinical_differential_support/cds_core/local_launch.py`
- Test: `clinical_differential_support/cds_core/tests/test_local_launch.py`

- [x] Add failing assertions for `operator_summary`, `environment_checks`, and `manual_blockers`.
- [x] Implement `_build_operator_summary()`, `_build_environment_checks()`, and `_build_manual_blockers()`.
- [x] Add `manual_required` and `command_kind` to each step definition.
- [x] Verify targeted local launch tests pass.

### Task 2: Launch Page UI

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/launch_guide.html`
- Test: `clinical_differential_support/cds_core/tests/test_launch_guide.py`

- [x] Add failing assertions for `Local Control Panel`, environment checks, manual blockers, copy command affordance, password manual warning, and verification evidence.
- [x] Render Local Control Panel cards.
- [x] Add responsive control-card styling and copy-command buttons.
- [x] Verify targeted launch guide tests pass.

### Task 3: Verification And Evidence

**Files:**
- Modify: `clinical_differential_support/scripts/smoke_check.py`
- Modify: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [x] Update smoke check expected text to `Local Control Panel`.
- [x] Run full regression, Django check, live smoke, direct HTML checks, and final evidence recorder.
- [x] Append verified progress notes.
