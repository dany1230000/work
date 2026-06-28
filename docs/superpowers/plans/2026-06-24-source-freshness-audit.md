# Source Freshness Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a staff-only source freshness audit workbench and JSON export for governed clinical source metadata.

**Architecture:** Add a focused selector module `cds_core.source_freshness` that computes source-level and summary freshness from existing `Source` rows. Views remain thin, routes are staff-only, and templates follow the existing governance pages.

**Tech Stack:** Django, Django TestCase, JSON responses, existing stdlib smoke script.

---

### Task 1: Source Freshness Selector And Routes

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_source_freshness.py`
- Create: `clinical_differential_support/cds_core/source_freshness.py`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`

- [ ] Write failing tests for report summary, staff page, JSON export, and route protection.
- [ ] Run `py -B .\clinical_differential_support\manage.py test cds_core.tests.test_source_freshness -v 2` and confirm missing module/route failure.
- [ ] Implement `build_source_freshness_report(today=None)`.
- [ ] Add staff-only `source_freshness` and `export_source_freshness_json` views.
- [ ] Add `/review/source-freshness/` and `/review/exports/source-freshness.json`.
- [ ] Re-run targeted tests and confirm pass.

### Task 2: Templates, Links, Smoke, And Docs

**Files:**
- Create: `clinical_differential_support/cds_core/templates/cds_core/source_freshness.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/source_index.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/coverage_depth.html`
- Modify: `clinical_differential_support/scripts/smoke_check.py`
- Modify: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`
- Modify: `clinical_differential_support/README.md`

- [ ] Add the staff-only source freshness template.
- [ ] Link it from governance, source library, and coverage depth.
- [ ] Add protected route smoke checks.
- [ ] Add README route entries.
- [ ] Run operational readiness tests.

### Task 3: Verification

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Run `py -B .\clinical_differential_support\manage.py test -v 2`.
- [ ] Run `py -B .\clinical_differential_support\manage.py check`.
- [ ] Restart local server.
- [ ] Run `py -B .\clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000`.
- [ ] Verify DB source freshness summary with Django shell.
- [ ] Record progress.
