# General Differential Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Chinese-first general differential workbench with structured findings, ranked candidate conditions, ask-next prompts, source links, and explicit starter-catalog limits.

**Architecture:** Keep the first version as a versioned Python catalog and evaluator, then expose it through a Django form/view/template. This avoids migration risk while creating the workflow needed for later governed database expansion.

**Tech Stack:** Django forms/views/templates, existing `cds_core` app, Django `TestCase`, static catalog data.

---

### Task 1: Engine Contract

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Create: `clinical_differential_support/cds_core/general_differential.py`
- Create: `clinical_differential_support/cds_core/differential_catalog.py`

- [ ] **Step 1: Write failing tests** for acute coronary syndrome, sepsis, sparse input, and text search.
- [ ] **Step 2: Run** `py -B manage.py test cds_core.tests.test_general_differential --verbosity 2` and verify failure due to missing module.
- [ ] **Step 3: Add catalog and evaluator** with `evaluate_general_differential(raw_findings)`.
- [ ] **Step 4: Re-run** the focused test and verify it passes.

### Task 2: Workspace UI

**Files:**
- Modify: `clinical_differential_support/cds_core/forms.py`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Create: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/home.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Create: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [ ] **Step 1: Write failing UI tests** for the route, dashboard link, 4-step workflow, POST result, source links, and safety copy.
- [ ] **Step 2: Run** `py -B manage.py test cds_core.tests.test_general_differential_ui --verbosity 2` and verify route/template failures.
- [ ] **Step 3: Add form, view, URL, template, and navigation links.**
- [ ] **Step 4: Re-run** focused UI tests and verify they pass.

### Task 3: Verification and Publish

**Files:**
- Modify only files changed by Tasks 1-2 plus docs in this plan/spec.

- [ ] **Step 1: Run focused tests**
  `py -B manage.py test cds_core.tests.test_general_differential cds_core.tests.test_general_differential_ui --verbosity 2`
- [ ] **Step 2: Run full regression**
  `py -B manage.py test --verbosity 1`
- [ ] **Step 3: Copy the scoped files into the clean publish clone, commit, push, wait for Render, and verify `/differential/` publicly.**
