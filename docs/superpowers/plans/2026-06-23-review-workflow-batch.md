# Review Workflow Batch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `/review/queue/` with changes-requested follow-up, recent reviewer notes, and automatic resubmission when approved content is edited.

**Architecture:** Reuse the existing `build_review_queue()` selector for read-only queue data, update `review_queue.html` to display the new sections, and add automatic state transition logic inside `review_item_edit()`. No database migration is required.

**Tech Stack:** Django 5.2, SQLite, Django TestCase, existing `cds_core` app.

---

### Task 1: Changes Requested Queue

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_governance_dashboard.py`
- Modify: `clinical_differential_support/cds_core/governance.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/review_queue.html`

- [ ] Write failing tests proving a `changes_requested` review decision appears in `build_review_queue()["changes_requested_items"]` and renders on `/review/queue/`.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests.test_governance_dashboard -v 2` and confirm failure.
- [ ] Add changes-requested queue data to `build_review_queue()`.
- [ ] Render a "Changes requested" priority section in `review_queue.html`.
- [ ] Run the governance tests and confirm they pass.

### Task 2: Reviewer Notes

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_governance_dashboard.py`
- Modify: `clinical_differential_support/cds_core/governance.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/review_queue.html`

- [ ] Write failing tests proving recent `ReviewRecord` notes are returned by the queue selector and shown on `/review/queue/`.
- [ ] Run the governance tests and confirm failure.
- [ ] Add recent review records to `build_review_queue()`.
- [ ] Render reviewer, decision, note text, timestamp, and item link in `review_queue.html`.
- [ ] Run the governance tests and confirm they pass.

### Task 3: Approved Edit Auto-Resubmission

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_governance_dashboard.py`
- Modify: `clinical_differential_support/cds_core/views.py`

- [ ] Write a failing test proving staff editing an approved item changes status to `in_review` and creates a `submitted` audit event.
- [ ] Run the governance tests and confirm failure.
- [ ] Update `review_item_edit()` so approved items are automatically marked `in_review` after staff edit.
- [ ] Create a `submitted` audit event with notes describing the automatic resubmission.
- [ ] Run the governance tests and confirm they pass.

### Task 4: Documentation And Verification

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Add P6 progress notes and verification evidence.
- [ ] Run `py -B clinical_differential_support\manage.py test`.
- [ ] Run `py -B clinical_differential_support\manage.py check`.
- [ ] Run the safety keyword scan.
- [ ] Restart the background Django dev server on `127.0.0.1:8000`.
- [ ] Live verify `/review/queue/` includes "Changes requested" and "Reviewer notes".
