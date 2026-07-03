# General Differential 600 Performance And Emergency Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 575 to 600 conditions and reduce perceived waiting during repeated differential runs.

**Architecture:** Add a nineteenth static catalog batch with 25 de-duplicated emergency, toxicology, metabolic, vascular, hematologic, and exposure-related conditions. Regenerate the reviewed JSON runtime artifact and advance governance counts to 600/678. Improve the differential submit experience by keeping the current result panel visible, using a quieter inline updating state, and preserving the candidate scan position after AJAX refresh.

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

- [x] Add a quality test for 600 conditions, 678 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_600`.
- [x] Add a searchability test for 25 new non-duplicate condition slugs.
- [x] Add a UI/performance test that repeated AJAX submit keeps the results panel visible and uses inline status instead of a full navigation loading state.
- [x] Update exact reviewed catalog count assertions from 575/653 to 600/678.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Select 25 de-duplicated high-value conditions after checking current query behavior, not just slug uniqueness.
- [x] Use official or institutionally authoritative source rows, preferring CDC/WHO/NIH/Merck Professional where available.
- [x] Add the nineteenth 25-condition batch and extend `CONDITIONS`.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 600`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Repeated-Run Performance Polish

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Keep existing results visible while a differential POST is pending.
- [x] Replace the heavy loading feel with a compact inline updating state near the submit button and results panel.
- [x] Preserve focus/scroll near the candidate scan after AJAX refresh when the user is already reviewing results.

### Task 4: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] Run focused tests.
- [x] Run related tests.
- [x] Run full `cds_core.tests` suite and validators.
- [x] Run local CSRF smoke.
- [x] Commit, push, and public Render smoke.

### Stop Condition

Phase 600 is done only when the public site reports 600 conditions, 678 sources, returns exact top hits for the new condition queries, and repeated differential runs do not replace the workflow with a full loading screen.
