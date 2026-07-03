# General Differential 550 Filtered Secondary Drawer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 525 to 550 conditions and reduce long-result clutter by making secondary candidates filterable by urgency and system.

**Architecture:** Add a seventeenth static catalog batch with official source rows, regenerate the reviewed JSON runtime artifact, advance governance counts to 550/628, and keep ranking unchanged. Add presentation-only result metadata for urgency/system filters and render secondary cards inside a compact drawer with deterministic `data-secondary-filter-*` markers.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django templates, inline CSS/JavaScript, Django test runner, existing management commands.

---

### Task 1: Failing Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`

- [x] Add a quality test for 550 conditions, 628 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_550`.
- [x] Add a searchability test for the 25 new condition slugs after de-dupe.
- [x] Add a UI test that secondary candidate cards render inside a filterable drawer after primary candidates.
- [x] Update exact reviewed catalog count assertions from 525/603 to 550/628.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Select 25 de-duplicated high-value conditions from vaccine-preventable, zoonotic, fungal, and opportunistic infection gaps.
- [x] Use official or institutionally authoritative source rows, preferring CDC/WHO/NIH/Merck Professional where available.
- [x] Add the seventeenth 25-condition batch and extend `CONDITIONS`.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 550`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Filtered Secondary Drawer

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Add presentation metadata for urgency and system filter counts without changing ranking.
- [x] Render secondary candidates behind urgency/system filter controls.
- [x] Add minimal JavaScript to filter rows with stable `data-secondary-filter-*` markers and an empty state.

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

Phase 550 is done only when the public site reports 550 conditions, 628 sources, returns an exact top hit for a new condition query, and the secondary candidate drawer filters work after AJAX POST.
