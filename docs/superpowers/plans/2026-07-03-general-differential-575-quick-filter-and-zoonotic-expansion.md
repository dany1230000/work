# General Differential 575 Quick Filter And Zoonotic Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 550 to 575 conditions and make long candidate scans easier to act on with compact quick filters before the detailed cards.

**Architecture:** Add an eighteenth static catalog batch with source-backed infectious, neurologic, endocrine, toxicologic, and environmental conditions. Regenerate the reviewed JSON runtime artifact and advance governance counts to 575/653. Add presentation-only candidate scan filter metadata for urgency and system without changing ranking, then render compact filter controls above the scan table and secondary drawer.

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

- [x] Add a quality test for 575 conditions, 653 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_575`.
- [x] Add a searchability test for the 25 new condition slugs after de-dupe.
- [x] Add a UI test that candidate scan rows can be filtered by urgency/system before opening detailed cards.
- [x] Update exact reviewed catalog count assertions from 550/628 to 575/653.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Select 25 de-duplicated high-value conditions that improve broad front-door coverage without claiming all-disease completeness.
- [x] Use official or institutionally authoritative source rows, preferring CDC/WHO/NIH/Merck Professional where available.
- [x] Add the eighteenth 25-condition batch and extend `CONDITIONS`.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 575`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Candidate Scan Quick Filters

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Reuse existing urgency/system metadata to build candidate scan filter counts without changing ranking.
- [x] Render compact filter controls before the candidate scan table.
- [x] Add JavaScript that hides non-matching candidate scan rows, keeps the current panel in place, and shows an empty state.

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

Phase 575 is done only when the public site reports 575 conditions, 653 sources, returns exact top hits for the new condition queries, and the candidate scan quick filters work after POST without navigating away.
