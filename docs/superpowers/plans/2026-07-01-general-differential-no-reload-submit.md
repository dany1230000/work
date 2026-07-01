# General Differential No-Reload Submit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Submit the general differential form without a full browser page reload and keep normal server-rendered POST as fallback.

**Architecture:** Add replaceable section markers to the general differential template and add a progressive-enhancement submit handler to the existing shared base script. The handler posts the current form, parses the full HTML response, and swaps only the stepper, selected findings summary, and results panel.

**Tech Stack:** Django templates, existing Django view, vanilla JavaScript fetch/FormData/DOMParser, Django tests, Playwright browser smoke.

---

### Task 1: Failing UI Contract Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [x] **Step 1: Add GET marker assertions**

Assert the general differential page exposes `data-differential-workbench`, `data-differential-form`, `data-differential-submit-button`, `data-differential-submit-status`, `data-differential-selected-summary`, and `data-differential-results-panel`.

- [x] **Step 2: Add POST replacement assertions**

Assert an XMLHttpRequest-style POST for `pertussis` still returns replaceable sections and source-backed result content.

- [x] **Step 3: Verify RED**

Run:

```powershell
py -B manage.py test cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_general_differential_page_shows_stepwise_workflow_and_limits cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_posted_general_differential_page_keeps_replaceable_fetch_sections -v 2
```

Expected: fail because the markers and submit JavaScript do not exist.

### Task 2: Template And JavaScript Implementation

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`

- [x] **Step 1: Add replaceable markers**

Mark the workbench, form, selected summary, inline submit status, and results panel with stable `data-*` selectors.

- [x] **Step 2: Add progressive submit handler**

Add `initializeGeneralDifferentialFetchSubmit()` and `replaceDifferentialWorkspaceSections()` to the shared script, call the initializer on initial load and after fast navigation, and fall back to native `form.submit()` if fetch replacement fails.

- [x] **Step 3: Verify GREEN**

Run the targeted command from Task 1 again.

Expected: 2 tests pass.

### Task 3: Browser Behavior Check

**Files:**
- No production file changes.

- [x] **Step 1: Start local server**

```powershell
py -B manage.py runserver 127.0.0.1:8055
```

- [x] **Step 2: Run real browser smoke**

Open `http://127.0.0.1:8055/differential/`, fill `pertussis`, submit, and confirm URL remains unchanged, a JavaScript marker survives, and the results panel contains Pertussis plus the CDC source.

Expected evidence: marker `alive`, same URL, `hasPertussis=true`, `hasCdc=true`, active step `differential`.

### Task 4: Final Verification And Publish

**Files:**
- Stage only this phase's template, UI test, and docs files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] **Step 1: Run full suite**

```powershell
py -B manage.py test -v 2
```

- [ ] **Step 2: Commit and push**

```powershell
git add clinical_differential_support/cds_core/templates/cds_core/base.html clinical_differential_support/cds_core/templates/cds_core/general_differential.html clinical_differential_support/cds_core/tests/test_general_differential_ui.py docs/superpowers/specs/2026-07-01-general-differential-no-reload-submit-design.md docs/superpowers/plans/2026-07-01-general-differential-no-reload-submit.md
git commit -m "Add no-reload general differential submit"
git push origin master
```

- [ ] **Step 3: Public smoke**

After Render deploys, smoke `/differential/` for the no-reload markers and POST workflow.
