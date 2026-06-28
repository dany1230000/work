# Next Action Downstream Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Next Action Workbench reflect downstream audit completion and point to regression/smoke when coverage and source freshness are clear.

**Architecture:** Reuse existing selector functions from `coverage_depth` and `source_freshness`, but copy only summary-safe fields into `next-actions.json`. Keep views thin.

**Tech Stack:** Django, Django TestCase, existing staff-only route and JSON export.

---

### Task 1: Red Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`

- [ ] Add all-fixture selector assertions for downstream readiness.
- [ ] Update the dyspnea completion test to expect regression gate after downstream audits are clear.
- [ ] Add page and JSON assertions for downstream readiness.
- [ ] Run targeted next-action tests and confirm failure.

### Task 2: Selector And Template

**Files:**
- Modify: `clinical_differential_support/cds_core/next_actions.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/next_actions.html`

- [ ] Add summary-only downstream readiness to the plan.
- [ ] Integrate coverage-depth and source-freshness status into completion status.
- [ ] Update final-stage next actions.
- [ ] Render downstream readiness on the staff page.
- [ ] Re-run targeted tests and confirm pass.

### Task 3: Verification

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Run full regression.
- [ ] Run Django system check.
- [ ] Restart local server.
- [ ] Run live smoke.
- [ ] Verify live DB next-action status.
- [ ] Record progress and safety boundary.
