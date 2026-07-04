# General Differential 750 First Screen Brief And Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 725 to 750 conditions and make the first result screen even more actionable with a compact brief that says what to do now, what to ask next, and what to compare.

**Architecture:** Add a twenty-fifth static catalog batch with 25 de-duplicated, source-backed conditions across vascular, renal/metabolic, GI/hepatic, ENT, obstetric/gynecologic, pediatrics/dermatology, and musculoskeletal gaps. Regenerate the reviewed JSON runtime artifact and advance governance counts to 750/828. Add a compact `first_screen_brief` object to the command-center payload and render it directly under the priority lane, before long workflow/evidence drawers.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django templates, inline CSS, Django test runner, existing management commands.

---

### Task 1: Failing Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`

- [x] Add a quality test for 750 conditions, 828 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_750`.
- [x] Add a searchability test for 25 new non-duplicate condition slugs after checking current query behavior.
- [x] Add engine and UI tests for a `first_screen_brief` shown after the priority lane and before progressive detail drawers.
- [x] Update exact reviewed catalog count assertions from 725/803 to 750/828.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Add the twenty-fifth 25-condition batch and extend `CONDITIONS`.
- [x] Use official or institutionally authoritative source rows verified during this phase.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 750`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: First Screen Brief

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Add `first_screen_brief` to `next_step_command_center` with three terse actions: do now, ask next, compare.
- [x] Render the Chinese-first brief with `data-first-screen-brief="true"` after priority lane and before progressive drawers.
- [x] Keep command center, priority lane, and progressive drawers intact.

### Task 4: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] Run focused tests.
- [x] Run related tests.
- [x] Run full `cds_core.tests` suite and validators.
- [x] Run local CSRF smoke.
- [ ] Commit, push, and public Render smoke.

### Stop Condition

Phase 750 is done only when the public site reports 750 conditions, 828 sources, the 25 new condition queries rank correctly, and the first result screen shows a priority lane plus a concise first-screen brief before long workflow/evidence drawers.
