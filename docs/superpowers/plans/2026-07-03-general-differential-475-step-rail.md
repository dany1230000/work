# General Differential 475 Step Rail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the reviewed general differential catalog from 450 to 475 conditions and make the result page show a compact "what to do next" rail before longer workflow text.

**Architecture:** Add a fourteenth static catalog batch, regenerate reviewed JSON through the existing importer, advance exact governance counts to 475/553, and add a presentation-only step rail rendered from existing `patient_workflow.steps`.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django templates, inline CSS, Django test runner, existing management commands.

---

### Task 1: Failing Catalog And UI Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [x] **Step 1: Add the 475 milestone quality test**

Add `test_fourteenth_generalist_batch_expands_catalog_to_475_without_warnings` asserting at least 475 conditions, at least 553 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_475`.

- [x] **Step 2: Add the 25-condition searchability test**

Add `test_fourteenth_generalist_batch_adds_25_more_searchable_conditions` with exact query-to-slug expectations for every new condition.

- [x] **Step 3: Add compact step rail UI test**

Assert posted results render `data-stepwise-next-rail="true"` and `data-stepwise-next-rail-item="true"` before the long patient workflow and before candidate scan.

- [x] **Step 4: Verify RED**

Run focused tests and confirm they fail before implementation.

### Task 2: Catalog And Reviewed JSON

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] **Step 1: Add 25 source rows**

Add source rows for CDC, NIDCD, MedlinePlus, NIDDK/NKF, NICHD, WHO, NHS, Cleveland Clinic, and Merck-backed references used by the fourteenth batch.

- [x] **Step 2: Add the fourteenth generalist batch**

Append 25 condition entries using `_eighth_generalist_condition` and extend `CONDITIONS`.

- [x] **Step 3: Update the expansion target**

Set `EXPANSION_TARGET_CONDITIONS = 475`.

- [x] **Step 4: Regenerate reviewed runtime JSON**

```powershell
$tmp = Join-Path $env:TEMP 'general_differential_catalog_reviewed_475.json'
py -B manage.py export_general_differential_review_seed --pretty | Set-Content -LiteralPath $tmp -Encoding UTF8
py -B manage.py import_general_differential_reviewed_catalog --path $tmp --output cds_core/data/general_differential_catalog_reviewed.json --apply --overwrite
```

Expected: `APPLIED reviewed catalog import: 475 conditions, 553 sources`.

### Task 3: Compact Step Rail

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] **Step 1: Add step rail styles**

Add a compact horizontal/stacking rail style that does not create nested cards.

- [x] **Step 2: Render the rail before long workflow**

Render the first four `result.patient_workflow.steps` as short ordered items before the detailed patient workflow section.

- [x] **Step 3: Keep logic presentation-only**

Do not add new diagnostic, treatment, or prescribing logic; the rail mirrors existing steps.

### Task 4: Governance Count Updates

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`

- [x] **Step 1: Update exact count assertions**

Update current reviewed catalog expectations from 450/528 to 475/553 after regeneration.

### Task 5: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] **Step 1: Run targeted tests**

- [x] **Step 2: Run related tests**

- [x] **Step 3: Run full suite and validators**

- [x] **Step 4: Commit, push, and public smoke**

Commit the exact staged phase files, push `origin master`, then smoke the public `/differential/` page with counts 475/553 and a new query such as `histoplasmosis`.

### Next Phase Candidate

After this phase is verified publicly, continue with a 500-condition slice and tighten the source drawer into a filterable provenance review surface.
