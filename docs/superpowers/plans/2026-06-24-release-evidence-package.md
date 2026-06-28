# Release Evidence Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a staff-only JSON evidence package for release handoff.

**Architecture:** Create a focused `cds_core.evidence` module that builds a summary-only package from existing governance selectors and model counts. Expose it through a staff-only view and link it from the release readiness page.

**Tech Stack:** Django 5.2, Python dict/JSON, existing reviewer staff guard.

---

### Task 1: Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_release_evidence.py`

- [ ] Add tests for unauthenticated redirect.
- [ ] Add tests for staff JSON package content.
- [ ] Add tests proving fixture clinical text is omitted.
- [ ] Add tests for readiness page link.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests.test_release_evidence -v 2` and confirm failures are for missing route/helper/link.

### Task 2: Evidence Builder

**Files:**
- Create: `clinical_differential_support/cds_core/evidence.py`

- [ ] Implement `build_release_evidence_package(now=None, today=None)`.
- [ ] Reuse `build_release_readiness_report()`.
- [ ] Return only counts, booleans, route references, and safety assertions.

### Task 3: View, Route, Link, Docs

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/release_readiness.html`
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Add staff-only JSON view.
- [ ] Add route.
- [ ] Link from readiness page.
- [ ] Document route and verification.
- [ ] Run targeted tests, full tests, system check, safety scan, restart server, and live verify.
