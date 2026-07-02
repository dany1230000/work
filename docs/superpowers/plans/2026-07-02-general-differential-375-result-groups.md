# General Differential 375 Result Groups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next reviewed 25-condition slice so the general differential catalog reaches 375 conditions, then group ranked candidates by urgency before the long card list.

**Architecture:** Extend the static catalog with one named batch, regenerate the reviewed runtime JSON through the existing reviewed import command, update milestone expectations, and add a pure evaluator helper that builds urgency groups for the template.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django templates, Django test runner, existing management commands.

---

### Task 1: Failing Catalog And UI Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [x] **Step 1: Add the 375 milestone quality test**

Add `test_tenth_generalist_batch_expands_catalog_to_375_without_warnings` asserting at least 375 conditions, zero blockers, zero warnings, and completed `expand_condition_catalog_to_375`.

- [x] **Step 2: Add the 25-condition searchability test**

Add `test_tenth_generalist_batch_adds_25_more_searchable_conditions` with exact query-to-slug expectations for every new condition in the tenth batch.

- [x] **Step 3: Add result grouping behavior tests**

Assert `evaluate_general_differential` returns `result_groups`, and the posted page renders `data-result-groups="true"` before `data-result-card="true"`.

- [x] **Step 4: Verify RED**

Run the focused tests and confirm they fail because the catalog target, new slugs, and result grouping are not implemented yet.

### Task 2: Catalog And Reviewed JSON

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] **Step 1: Add source rows**

Add official source rows for CDC, NHLBI, NIDDK, NCI, NIMH, MedlinePlus, NICHD, and NIAMS references used by the tenth batch.

- [x] **Step 2: Add the tenth generalist batch**

Append 25 condition entries using the established `_eighth_generalist_condition` helper and extend `CONDITIONS`.

- [x] **Step 3: Update the expansion target**

Set `EXPANSION_TARGET_CONDITIONS = 375`.

- [x] **Step 4: Regenerate reviewed runtime JSON**

```powershell
$tmp = Join-Path $env:TEMP 'general_differential_catalog_reviewed_375.json'
py -B manage.py export_general_differential_review_seed --pretty | Set-Content -LiteralPath $tmp -Encoding UTF8
py -B manage.py import_general_differential_reviewed_catalog --path $tmp --output cds_core/data/general_differential_catalog_reviewed.json --apply --overwrite
```

Expected: `APPLIED reviewed catalog import: 375 conditions, 453 sources`.

### Task 3: Candidate Grouping

**Files:**
- Modify: `clinical_differential_support/cds_core/general_differential.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] **Step 1: Add evaluator grouping helper**

Build `result_groups` from ranked results by urgency, with each group containing `urgency`, `label`, `count`, and up to three candidate summaries.

- [x] **Step 2: Render compact grouping panel**

Render urgency groups before the result cards and after the existing primary next-step/action checklist sections.

### Task 4: Governance Count Updates

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`

- [x] **Step 1: Update exact count assertions**

Update current reviewed catalog expectations from 350/429 to 375/453 after regeneration.

### Task 5: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] **Step 1: Run targeted tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality.GeneralDifferentialCatalogQualityTests.test_tenth_generalist_batch_expands_catalog_to_375_without_warnings cds_core.tests.test_general_differential.GeneralDifferentialEngineTests.test_tenth_generalist_batch_adds_25_more_searchable_conditions cds_core.tests.test_general_differential.GeneralDifferentialEngineTests.test_ranked_results_are_grouped_by_urgency cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_posted_findings_show_result_groups_before_long_candidate_cards
```

- [x] **Step 2: Run related tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality cds_core.tests.test_general_differential cds_core.tests.test_general_differential_ui cds_core.tests.test_general_differential_import_workbench cds_core.tests.test_next_actions cds_core.tests.test_dyspnea_pathway
```

- [x] **Step 3: Run full suite and validators**

```powershell
py -B manage.py test cds_core.tests
py -B manage.py validate_general_differential_catalog
py -B manage.py validate_general_differential_reviewed_catalog_data
py -B manage.py import_general_differential_reviewed_catalog --path cds_core/data/general_differential_catalog_reviewed.json
```

- [ ] **Step 4: Commit, push, and public smoke**

Commit the exact staged phase files, push `origin master`, then smoke `https://clinical-differential-support.onrender.com/differential/` with CSRF GET/POST and one new query such as `meningococcal disease`.

### Next Phase Candidate

After this phase is verified publicly, continue with a 400-condition slice plus navigation/performance profiling so route switches and result updates feel less like page reloads.
