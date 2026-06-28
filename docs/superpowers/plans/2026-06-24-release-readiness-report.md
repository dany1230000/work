# Release Readiness Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a staff-only release readiness report that summarizes governance blockers and links to exports.

**Architecture:** Extend `cds_core.governance` with a focused readiness selector, expose a staff-only view in `cds_core.views`, and render the report in a new template. Tests cover selector status, access control, page content, and dashboard links.

**Tech Stack:** Django 5.2, existing governance selectors, existing reviewer staff guard.

---

### Task 1: Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_release_readiness.py`

- [ ] Add selector tests for ready fixture baseline and blocker detection.
- [ ] Add view tests for staff-only access and rendered report content.
- [ ] Add dashboard link tests.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests.test_release_readiness -v 2` and confirm failures are for missing selector/routes/template.

### Task 2: Selector

**Files:**
- Modify: `clinical_differential_support/cds_core/governance.py`

- [ ] Implement `build_release_readiness_report(today=None)`.
- [ ] Reuse `build_case_validation_rows()` for case validation status.
- [ ] Return counts, blocker lists, failed case rows, and `ready_for_handoff`.

### Task 3: View, URL, Template

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Create: `clinical_differential_support/cds_core/templates/cds_core/release_readiness.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html`

- [ ] Add a staff-only `release_readiness` view.
- [ ] Add `/review/readiness/`.
- [ ] Add readiness template with metrics, blockers, and export links.
- [ ] Add dashboard staff link.

### Task 4: Verification

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Document route.
- [ ] Run targeted tests, full tests, system check, safety scan, restart server, and live verify.
