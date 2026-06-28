# Chinese-First Bilingual Clinical Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the clinical differential support MVP to a Chinese-first bilingual interface and content model while preserving English support and clinical safety labels.

**Architecture:** Add explicit Chinese and English clinical content fields to source-backed records, keep deterministic rules unchanged, and render Chinese primary text with English secondary text in the clinician workflow. Keep bilingual copy testable through model, fixture, template, and live HTTP assertions.

**Tech Stack:** Python 3.14 runtime, Django 5.2, SQLite local MVP database, Django TestCase.

---

### Task 1: Bilingual Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_models.py`
- Modify: `clinical_differential_support/cds_core/tests/test_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_safety_labels.py`

- [ ] Add tests that require `ClinicalItem` to store `title_zh`, `title_en`, `summary_zh`, and `summary_en`.
- [ ] Add tests that require the headache page to show Chinese first and English second for thunderclap headache.
- [ ] Add tests that require bilingual professional-use safety copy.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests` and confirm failure.

### Task 2: Bilingual Data Model

**Files:**
- Modify: `clinical_differential_support/cds_core/models.py`
- Modify: `clinical_differential_support/cds_core/admin.py`

- [ ] Add bilingual fields while preserving existing `title` and `summary` compatibility.
- [ ] Add display helpers for Chinese-first and English-secondary rendering.
- [ ] Update admin search and list display for bilingual fields.

### Task 3: Bilingual Content and UI

**Files:**
- Modify: `clinical_differential_support/cds_core/fixtures/headache_mvp.json`
- Modify: `clinical_differential_support/cds_core/forms.py`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/headache.html`
- Modify: `clinical_differential_support/README.md`

- [ ] Update fixture clinical items with Chinese primary and English secondary titles/summaries.
- [ ] Update form labels to Chinese first with English in parentheses.
- [ ] Update page headings, buttons, safety banner, empty state, tags, and source labels to Chinese first.
- [ ] Update README to Chinese first with short English support.
- [ ] Run `py -B clinical_differential_support\manage.py test`.

### Task 4: Local Database and Live Verification

**Files:**
- Local generated file: `clinical_differential_support/db.sqlite3`

- [ ] Recreate the local MVP database because this app still uses syncdb tables rather than committed migrations.
- [ ] Run `py -B clinical_differential_support\manage.py migrate --run-syncdb`.
- [ ] Run `py -B clinical_differential_support\manage.py loaddata headache_mvp`.
- [ ] Verify live GET and CSRF-backed POST show Chinese and English content.
