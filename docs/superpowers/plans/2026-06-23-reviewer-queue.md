# Reviewer Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Chinese-first reviewer queue at `/review/queue/` for source gaps, due reviews, drafts, in-review items, and searchable/filterable item results.

**Architecture:** Extend the existing governance selector layer with `build_review_queue()`, add a read-only Django view and template, and link the route from the governance dashboard. The queue uses GET query parameters only and reuses existing `ClinicalItem`, `Source`, and item detail routes.

**Tech Stack:** Django 5.2, SQLite, Django TestCase, existing `cds_core` app.

---

### Task 1: Queue Selector Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_governance_dashboard.py`
- Modify: `clinical_differential_support/cds_core/governance.py`

- [ ] Write failing tests for `build_review_queue()` baseline counts, source-gap ordering, review-due ordering, and status/urgency/text filtering.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests.test_governance_dashboard -v 2` and confirm the new tests fail because `build_review_queue` does not exist.
- [ ] Implement `build_review_queue(filters=None, today=None)` using `ClinicalItem.objects.select_related("chief_complaint").prefetch_related("sources").annotate(source_count=Count("sources"))`.
- [ ] Run the same governance test command and confirm these selector tests pass.

### Task 2: Queue Route And Template

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_governance_dashboard.py`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Create: `clinical_differential_support/cds_core/templates/cds_core/review_queue.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html`

- [ ] Write failing tests for `/review/queue/`, dashboard link, and rendered Chinese-first/English-supported queue content.
- [ ] Run the governance test command and confirm the route/template tests fail because the route does not exist.
- [ ] Add `review_queue` view and URL pattern.
- [ ] Create `review_queue.html` with filter form, summary metrics, and result table.
- [ ] Add a dashboard link to `/review/queue/`.
- [ ] Run the governance test command and confirm route/template tests pass.

### Task 3: Documentation And Verification

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Add `/review/queue/` to README routes.
- [ ] Add P5 progress notes and verification evidence.
- [ ] Run `py -B clinical_differential_support\manage.py test`.
- [ ] Run `py -B clinical_differential_support\manage.py check`.
- [ ] Run the safety scan for forbidden execution and patient-data keywords.
- [ ] Restart the background Django dev server on `127.0.0.1:8000`.
- [ ] Live verify `/review/queue/` and filtered queue URLs.
