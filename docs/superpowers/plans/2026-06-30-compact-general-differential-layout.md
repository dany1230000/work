# Compact General Differential Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the general differential workbench shorter and easier to use by showing the workflow step-by-step instead of rendering every finding and every candidate as first-class page content.

**Architecture:** Keep the existing Django view and evaluator unchanged. Improve only `general_differential.html` with progressive disclosure: full finding selection starts collapsed, top results stay visible, and lower-priority candidates move into a collapsed secondary drawer.

**Tech Stack:** Django templates, existing Django `TestCase` UI tests, existing public smoke script.

---

### Task 1: Add Layout Regression Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [ ] Add a GET-page test requiring `data-finding-library-drawer="true"` and a compact summary before the full finding list.
- [ ] Add a POST-result test requiring `data-primary-result-list="true"` before `data-secondary-result-drawer="true"`.
- [ ] Run the targeted tests and verify they fail before editing the template.

### Task 2: Compact The Template

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [ ] Add CSS for a finding library drawer and secondary result drawer.
- [ ] Move the full finding filter/checkbox library inside a collapsed `<details>`.
- [ ] Render only the top three result cards in the primary list.
- [ ] Render remaining result cards inside a collapsed "More candidates" drawer.

### Task 3: Verify And Publish

**Files to stage:**
- `docs/superpowers/plans/2026-06-30-compact-general-differential-layout.md`
- `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`
- `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [ ] Run targeted UI tests.
- [ ] Run full Django tests, Django check, and `git diff --cached --check`.
- [ ] Commit as `Compact general differential workbench layout`.
- [ ] Push to `master`.
- [ ] Public smoke `/differential/` for compact markers and 300/379 catalog metrics.

### Self-Review

- Scope is limited to layout and tests.
- No evaluator, catalog, database, auth, or deployment config changes.
- No placeholders remain.
