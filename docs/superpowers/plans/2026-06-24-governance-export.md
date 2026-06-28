# Governance Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add staff-only CSV exports for clinical items and source metadata.

**Architecture:** Put CSV row construction and sanitization in a focused `cds_core.exports` module, expose two staff-only views in `cds_core.views`, and link them from the existing governance dashboard. Tests cover redirect behavior, CSV content, formula sanitization, and dashboard links.

**Tech Stack:** Django 5.2, Python stdlib `csv`, existing staff reviewer access guard.

---

### Task 1: Export Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_governance_exports.py`

- [ ] Write tests for unauthenticated redirect, staff clinical item export, staff source export, formula sanitization, and staff dashboard links.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests.test_governance_exports -v 2`.
- [ ] Confirm the tests fail because export routes are not implemented.

### Task 2: CSV Export Module

**Files:**
- Create: `clinical_differential_support/cds_core/exports.py`

- [ ] Implement `safe_csv_value()`.
- [ ] Implement `build_clinical_item_export_rows()`.
- [ ] Implement `build_source_export_rows()`.
- [ ] Implement `csv_response()`.

### Task 3: Views, Routes, Dashboard Links

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html`
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Add staff-only CSV export views.
- [ ] Add export routes.
- [ ] Add staff-only export links to the governance dashboard.
- [ ] Document routes and verification results.
- [ ] Run targeted tests, full tests, system check, safety scan, restart server, and live verify.
