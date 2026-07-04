# General Differential 725 Priority Lane And Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 700 to 725 conditions and make the output tell the clinician the priority lane before they open any long details.

**Architecture:** Add a twenty-fourth static catalog batch with 25 de-duplicated, source-backed conditions across neurologic, GI/hepatic, GU, dermatology, cardiovascular, sleep/respiratory, and endocrine/eye gaps. Regenerate the reviewed JSON runtime artifact and advance governance counts to 725/803. Add a compact `priority_lane` object to the command-center payload and render it directly under the command center so the first screen states whether the case is critical-first, urgent-workup, routine-follow-up, or needs-more-data.

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

- [x] Add a quality test for 725 conditions, 803 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_725`.
- [x] Add a searchability test for 25 new non-duplicate condition slugs after checking current query behavior.
- [x] Add engine and UI tests for a `priority_lane` shown before the progressive detail drawers.
- [x] Update exact reviewed catalog count assertions from 700/778 to 725/803.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Add the twenty-fourth 25-condition batch and extend `CONDITIONS`.
- [x] Use official or institutionally authoritative source rows verified during this phase.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 725`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Priority Lane

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Add `priority_lane` to `next_step_command_center` using top urgency and selected data volume.
- [x] Render the Chinese-first lane strip with `data-priority-lane="..."` directly after the command center.
- [x] Keep the command center and progressive drawers intact.

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

Phase 725 is done only when the public site reports 725 conditions, 803 sources, the 25 new condition queries rank correctly, and the first result screen shows a priority lane before long workflow/evidence drawers.
