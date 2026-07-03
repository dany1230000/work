# General Differential 625 Concise Results And Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 600 to 625 conditions and make the result view shorter, more stepwise, and easier to use during repeated clinical review.

**Architecture:** Add a twentieth static catalog batch with 25 de-duplicated high-yield conditions that fill remaining ophthalmology, ENT, neurologic, endocrine, hematology, dermatology, and urgent-care gaps. Regenerate the reviewed JSON runtime artifact and advance governance counts to 625/703. Refactor the output panel so the first visible result area emphasizes the next action, danger checks, and top candidates while keeping long provenance and secondary detail collapsed or filtered.

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

- [ ] Add a quality test for 625 conditions, 703 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_625`.
- [ ] Add a searchability test for 25 new non-duplicate condition slugs.
- [ ] Add a UI test that the result panel starts with a concise next-action summary before long source/provenance sections.
- [ ] Update exact reviewed catalog count assertions from 600/678 to 625/703.
- [ ] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [ ] Select 25 non-duplicate conditions after checking current query behavior, not only slug uniqueness.
- [ ] Use official or institutionally authoritative source rows, preferring CDC/WHO/NIH/Merck Professional where available.
- [ ] Add the twentieth 25-condition batch and extend `CONDITIONS`.
- [ ] Set `EXPANSION_TARGET_CONDITIONS = 625`.
- [ ] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Concise Stepwise Results

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`

- [ ] Add a compact result summary model that surfaces primary next action, top danger checks, and top 3 candidates.
- [ ] Move long result groups, source provenance, and secondary candidates behind clear drawers or filters.
- [ ] Keep Chinese-first labels with English helper text and avoid adding explanatory marketing copy.

### Task 4: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [ ] Run focused tests.
- [ ] Run related tests.
- [ ] Run full `cds_core.tests` suite and validators.
- [ ] Run local CSRF smoke.
- [ ] Commit, push, and public Render smoke.

### Stop Condition

Phase 625 is done only when the public site reports 625 conditions, 703 sources, top hits work for the new condition queries, and the first result screen clearly tells the clinician what to do next before any long detail sections.
