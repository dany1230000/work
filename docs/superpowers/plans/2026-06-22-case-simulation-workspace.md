# Case Simulation Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Chinese-first bilingual case simulation workspace that lets clinicians/reviewers validate the headache rule base against stored non-patient scenarios.

**Architecture:** Store reviewed case fixtures in a `CaseScenario` model with bilingual titles/summaries, structured findings JSON, and expected clinical item titles. Reuse the existing deterministic pathway service, add case index/detail views, and render whether expected outputs matched.

**Tech Stack:** Django 5.2, SQLite local MVP database, Django TestCase, existing `headache_mvp` fixture.

---

### Task 1: Failing Scenario Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_case_scenarios.py`

- [ ] Test that the fixture contains at least 8 Chinese-first case scenarios.
- [ ] Test that the case index page renders Chinese-first and English-secondary labels.
- [ ] Test that running the thunderclap scenario shows the expected clinical output and match status.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests.test_case_scenarios -v 2` and confirm failure before implementation.

### Task 2: Scenario Model and Service

**Files:**
- Modify: `clinical_differential_support/cds_core/models.py`
- Modify: `clinical_differential_support/cds_core/services.py`
- Modify: `clinical_differential_support/cds_core/admin.py`

- [ ] Add `CaseScenario` with chief complaint, slug, bilingual title/summary, findings JSON, expected item titles JSON, display order, active flag, and display helpers.
- [ ] Add `evaluate_case_scenario(scenario)` that reuses `evaluate_headache_pathway` and marks expected outputs as matched/unmatched.
- [ ] Register scenarios in Django admin.

### Task 3: Scenario Routes and Templates

**Files:**
- Modify: `clinical_differential_support/cds_core/urls.py`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Create: `clinical_differential_support/cds_core/templates/cds_core/case_index.html`
- Create: `clinical_differential_support/cds_core/templates/cds_core/case_detail.html`

- [ ] Add `/cases/` case index route.
- [ ] Add `/cases/<slug>/` case detail route.
- [ ] Add navigation links for headache intake and case simulation.
- [ ] Render Chinese-first case titles and English secondary titles.
- [ ] Render findings, expected outputs, matched status, and actual pathway outputs.

### Task 4: Seed and Verify

**Files:**
- Modify: `clinical_differential_support/cds_core/fixtures/headache_mvp.json`
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Add 8 case scenarios to `headache_mvp`.
- [ ] Update README with case simulation route.
- [ ] Recreate local SQLite DB with `migrate --run-syncdb` and `loaddata headache_mvp`.
- [ ] Verify full test suite and live GET/POST paths.
