# Case Action Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the general differential result page tell clinicians the next practical action before showing long candidate details.

**Architecture:** Reuse existing `result.guided_follow_up` and `result.action_checklist` data. Add a compact action queue above the current guided follow-up section, with stable anchors into top candidates and catalog coverage.

**Tech Stack:** Django template, existing Django `TestCase` UI tests, vanilla HTML/CSS.

---

### Task 1: Lock Result Ordering

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [ ] **Step 1: Add a failing UI test**

Post a classic chest-pain finding set and assert:

```python
self.assertContains(response, 'data-case-action-queue="true"')
self.assertContains(response, 'data-action-queue-current="true"')
self.assertContains(response, 'data-action-queue-link="top-candidates"')
self.assertContains(response, 'data-action-queue-link="coverage"')
self.assertContains(response, 'id="top-candidates"')
self.assertLess(content.index('data-case-action-queue="true"'), content.index('data-guided-follow-up="true"'))
self.assertLess(content.index('data-case-action-queue="true"'), content.index('data-result-card="true"'))
```

- [ ] **Step 2: Verify RED**

Run:

```powershell
py -B manage.py test cds_core.tests.test_general_differential_ui -v 2
```

Expected: failure because no case action queue is rendered yet.

### Task 2: Add The Queue UI

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [ ] **Step 1: Add CSS**

Add styles for `.case-action-queue`, `.case-action-list`, `.case-action-item`, and `.case-action-links` using the existing neutral clinical palette and 6px radius.

- [ ] **Step 2: Add markup before guided follow-up**

Render the first three `result.guided_follow_up` steps as a compact queue above the existing guided follow-up section. Mark the first item with `data-action-queue-current="true"`.

- [ ] **Step 3: Add anchors**

Set `id="top-candidates"` on the primary result list and include queue links to `#top-candidates` and `#catalog-governance`.

- [ ] **Step 4: Verify GREEN**

Run:

```powershell
py -B manage.py test cds_core.tests.test_general_differential_ui -v 2
```

Expected: all UI tests pass.

### Task 3: Verify And Ship

**Files:**
- New plan doc and modified result template/test only.

- [ ] **Step 1: Run full tests**

```powershell
py -B manage.py test -v 2
```

- [ ] **Step 2: Run catalog validator**

```powershell
py -B manage.py validate_general_differential_catalog
```

- [ ] **Step 3: Smoke local and public result pages**

Confirm POST `/differential/` shows the queue before candidate cards and still keeps the lazy finding library behavior.

- [ ] **Step 4: Commit and push**

Stage only this plan, the UI test, and the general differential template. Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.
