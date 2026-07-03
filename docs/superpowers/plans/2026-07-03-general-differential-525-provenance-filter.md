# General Differential 525 Provenance Filter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 500 to 525 conditions and add a compact source provenance filter before long candidate cards.

**Architecture:** Add a sixteenth static catalog batch, regenerate reviewed JSON through the existing importer, advance exact governance counts to 525/603, and build a presentation-only provenance summary from already ranked results. The template renders publisher filters and source rows without changing ranking or clinical logic.

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

- [x] Add a quality test for 525 conditions, 603 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_525`.
- [x] Add a searchability test for all 25 new condition slugs.
- [x] Add an engine test for `source_provenance` rows, publisher filters, unique source count, and source URLs.
- [x] Add a UI test that posted results show the source provenance panel before detailed candidate cards.
- [x] Update exact reviewed catalog count assertions from 500/578 to 525/603.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Add 25 reviewed source rows from CDC and MedlinePlus, with existing Merck professional fallback.
- [x] Add the sixteenth 25-condition batch and extend `CONDITIONS`.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 525`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Source Provenance Filter

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Add `_build_source_provenance` to derive source rows and publisher filters from ranked results.
- [x] Render the source provenance panel after candidate scan and before detailed candidate cards.
- [x] Add minimal JavaScript to filter rows by publisher with stable `data-source-provenance-*` markers.

### Task 4: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] Run focused tests.
- [x] Run related tests.
- [x] Run full `cds_core.tests` suite and validators.
- [x] Run local CSRF smoke.
- [x] Commit, push, and public Render smoke.

### Next Phase Candidate

Continue with the 550-condition slice and collapse secondary candidate cards into a filterable drawer by urgency and system.
