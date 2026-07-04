# General Differential 700 Progressive Review And Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 675 to 700 conditions and reduce first-screen clutter by putting long workflow/evidence sections behind explicit progressive detail drawers while keeping the compact command center visible first.

**Architecture:** Add a twenty-third static catalog batch with 25 de-duplicated, source-backed pediatric, obstetric, metabolic, neurologic, musculoskeletal, infectious, and gynecologic conditions. Regenerate the reviewed JSON runtime artifact and advance governance counts to 700/778. Keep the command center first, then add default-collapsed detail drawers for full workflow and evidence so the user sees “what to do next” before the long reference material.

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

- [x] Add a quality test for 700 conditions, 778 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_700`.
- [x] Add a searchability test for 25 new non-duplicate condition slugs after checking current query behavior.
- [x] Add UI tests that command center remains first and long workflow/evidence sections are inside progressive detail drawers.
- [x] Update exact reviewed catalog count assertions from 675/753 to 700/778.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Add the twenty-third 25-condition batch and extend `CONDITIONS`.
- [x] Use official or institutionally authoritative source rows verified during this phase.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 700`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Progressive Review Layout

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Keep `data-next-step-command-center="true"` immediately after coverage.
- [x] Put the full patient workflow in a default-collapsed drawer with `data-progressive-detail-drawer="workflow"`.
- [x] Put scan/evidence-heavy sections in a default-collapsed drawer with `data-progressive-detail-drawer="evidence"`.

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

Phase 700 is done only when the public site reports 700 conditions, 778 sources, the 25 new condition queries rank correctly, and the first result screen keeps next steps visible while long workflow/evidence sections are collapsed into clear drawers.
