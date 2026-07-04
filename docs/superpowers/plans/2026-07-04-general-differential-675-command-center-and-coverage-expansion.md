# General Differential 675 Command Center And Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 650 to 675 conditions and make the first results screen more usable by turning the scattered next-step sections into a compact command center: safety gate, minimum data, leading candidate check, and source review in one predictable order.

**Architecture:** Add a twenty-second static catalog batch with 25 de-duplicated, source-backed conditions across cardiology, pulmonary, GI/hepatic, renal/metabolic, hematology, neurology, toxicology/nutrition, and rheumatology gaps. Regenerate the reviewed JSON runtime artifact and advance governance counts to 675/753. Add a compact next-step command center built from existing concise summary, complaint-guided intake, patient workflow, and source provenance outputs without removing detailed drawers.

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

- [x] Add a quality test for 675 conditions, 753 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_675`.
- [x] Add a searchability test for 25 new non-duplicate condition slugs after checking current query behavior.
- [x] Add UI tests for the command center appearing before long workflow, scan, provenance, and result cards.
- [x] Update exact reviewed catalog count assertions from 650/728 to 675/753.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Select 25 non-duplicate high-yield conditions using query checks, not slug checks alone.
- [x] Use official or institutionally authoritative source rows, preferring CDC/WHO/NIH/Merck Professional/NICE/NIDDK/NCBI where available.
- [x] Add the twenty-second 25-condition batch and extend `CONDITIONS`.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 675`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Next-Step Command Center

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Build a compact `next_step_command_center` payload from safety, complaint intake, leading candidates, and source review.
- [x] Surface a Chinese-first command center before the long patient workflow, candidate scan, provenance, and detailed drawers.
- [x] Keep detailed content available but make the first screen answer "what do I do next?" in four compact blocks.

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

Phase 675 is done only when the public site reports 675 conditions, 753 sources, the 25 new condition queries rank correctly, and the first results screen gives a compact command center before long clinical details.
