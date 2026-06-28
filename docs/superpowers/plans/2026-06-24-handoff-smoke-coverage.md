# Handoff Smoke Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add handoff report and handoff bundle protected-route coverage to the local smoke checker.

**Architecture:** Extend the existing `build_check_plan()` list with two redirect checks. Update the operational readiness test to assert the new check names and expected login redirects.

**Tech Stack:** Python stdlib smoke script, Django TestCase.

---

### Task 1: Smoke Plan Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`

- [ ] **Step 1: Add failing assertions for handoff route checks**

Assert that the smoke check plan contains:

```python
"protected_handoff_report": (
    "http://127.0.0.1:8000/review/exports/handoff-report.md",
    "/review/login/?next=/review/exports/handoff-report.md",
)
"protected_handoff_bundle": (
    "http://127.0.0.1:8000/review/exports/handoff-bundle.zip",
    "/review/login/?next=/review/exports/handoff-bundle.zip",
)
```

- [ ] **Step 2: Verify RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_operational_readiness -v 2`

Expected: FAIL because the new smoke checks do not exist yet.

### Task 2: Smoke Script Update

**Files:**
- Modify: `clinical_differential_support/scripts/smoke_check.py`

- [ ] **Step 1: Add protected handoff report check**

```python
Check(
    name="protected_handoff_report",
    url=f"{base}/review/exports/handoff-report.md",
    expected_status=302,
    expected_location="/review/login/?next=/review/exports/handoff-report.md",
)
```

- [ ] **Step 2: Add protected handoff bundle check**

```python
Check(
    name="protected_handoff_bundle",
    url=f"{base}/review/exports/handoff-bundle.zip",
    expected_status=302,
    expected_location="/review/login/?next=/review/exports/handoff-bundle.zip",
)
```

### Task 3: Verification

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Verify GREEN**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_operational_readiness -v 2`

Expected: operational readiness tests pass.

- [ ] **Step 2: Full verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
git diff --check -- clinical_differential_support docs .planning
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Expected: all commands pass and smoke output includes both handoff protected checks.
