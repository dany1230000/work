# General Differential 650 Guided Intake And Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 625 to 650 conditions and make the clinician workflow more complaint-directed so a new patient encounter clearly starts with the right minimum data, danger checks, and next action before long candidate review.

**Architecture:** Add a twenty-first static catalog batch with 25 de-duplicated, source-backed conditions that fill remaining ophthalmology, ENT, endocrine, hematology, rheumatology, dermatology, neurologic, infectious, toxicology, and urgent-care gaps. Regenerate the reviewed JSON runtime artifact and advance governance counts to 650/728. Add complaint-centered guided intake presets that map common patient presentations to minimum data prompts and structured finding shortcuts while preserving the current concise result summary and source provenance.

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

- [x] Add a quality test for 650 conditions, 728 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_650`.
- [x] Add a searchability test for 25 new non-duplicate condition slugs after checking current query behavior.
- [x] Add UI tests for complaint-centered guided intake presets appearing before long candidate and provenance sections.
- [x] Update exact reviewed catalog count assertions from 625/703 to 650/728.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] Select 25 non-duplicate high-yield conditions using query checks, not slug checks alone.
- [x] Use official or institutionally authoritative source rows, preferring CDC/WHO/NIH/Merck Professional/NICE/AAOS where available.
- [x] Add the twenty-first 25-condition batch and extend `CONDITIONS`.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 650`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Complaint-Guided Intake

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] Add a compact complaint-intake model for chest pain/dyspnea, abdominal pain, headache/neurologic deficit, fever/rash, eye/ENT, trauma/toxin, and nonspecific fatigue.
- [x] Surface each complaint preset as Chinese-first next-step cards with English helper text, minimum data prompts, and finding shortcuts.
- [x] Keep long candidate groups, source provenance, and secondary results behind the existing scan/drawer pattern.

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

Phase 650 is done only when the public site reports 650 conditions, 728 sources, new condition queries rank correctly, and the first screen can guide a clinician from common patient presentations to the next minimum data step before long details.
