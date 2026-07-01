# Next Action General Catalog Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Route clear downstream governance state to the General Differential Import Workbench before final regression gates.

**Architecture:** Extend `cds_core.next_actions` to compose `build_general_differential_import_workbench()` into a summary-only `general_catalog` block. Update next-action, final-verification, and project-completion expectations so the project remains truthful about not being final for "any disease" coverage.

**Tech Stack:** Django service functions, Django templates, Django TestCase, existing staff-only views.

---

### Task 1: Failing Next-Action Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_project_completion.py`

- [ ] **Step 1: Update expectations**

Assert that downstream-clear state now returns:

```python
self.assertEqual(plan["completion_status"], "general_catalog_import_ready")
self.assertEqual(
    plan["next_actions"][0]["action_id"],
    "expand_general_differential_catalog_via_import_workbench",
)
self.assertEqual(plan["general_catalog"]["condition_count"], 300)
self.assertEqual(plan["general_catalog"]["source_count"], 379)
self.assertEqual(
    plan["general_catalog"]["import_workbench_path"],
    "/review/general-differential-import/",
)
```

- [ ] **Step 2: Run RED**

Run: `py -B manage.py test cds_core.tests.test_next_actions cds_core.tests.test_dyspnea_pathway cds_core.tests.test_final_verification cds_core.tests.test_project_completion -v 2`

Expected: tests fail because `general_catalog` and the new completion status do not exist.

### Task 2: Build Summary-Only General Catalog Gate

**Files:**
- Modify: `clinical_differential_support/cds_core/next_actions.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/next_actions.html`

- [ ] **Step 1: Import the workbench builder**

Use `build_general_differential_import_workbench()` and expose only summary fields and bucket counts.

- [ ] **Step 2: Add first action**

When downstream status is `ready_for_regression_gate`, return:

```python
[
    _general_catalog_import_action(1, general_catalog),
    _regression_action(2, "pending_general_catalog_import"),
]
```

- [ ] **Step 3: Render the summary**

Add a compact panel with the import workbench link, 300 conditions, 379 sources, and the lowest-coverage buckets.

### Task 3: Update Final Gates

**Files:**
- Modify: `clinical_differential_support/cds_core/final_verification.py`
- Modify: `clinical_differential_support/cds_core/project_completion.py`

- [ ] **Step 1: Keep final verification blocked**

The final verification gate remains blocked when `completion_status` is not `ready_for_regression_gate`.

- [ ] **Step 2: Update labels and expected next-action evidence**

Expose `general_catalog_import_ready` as the current blocker. Do not claim final completion.

### Task 4: Verification and Publish

- [ ] **Step 1: Run targeted tests**

Run: `py -B manage.py test cds_core.tests.test_next_actions cds_core.tests.test_dyspnea_pathway cds_core.tests.test_final_verification cds_core.tests.test_project_completion -v 2`

Expected: PASS.

- [ ] **Step 2: Run full tests and catalog validator**

Run: `py -B manage.py test -v 2`

Run: `py -B manage.py validate_general_differential_catalog`

Expected: all pass.

- [ ] **Step 3: Smoke Next Action locally and publicly**

Local staff-client smoke checks `/review/next-actions/` and `/review/exports/next-actions.json` for `general_catalog_import_ready` and the import workbench link.

Public smoke checks protected routes still redirect and public routes still pass.

- [ ] **Step 4: Commit and push**

Stage only the next-action integration files and these plan/spec docs. Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.
