# Expand General Differential Catalog To 325 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next reviewed 25-condition slice so the general differential catalog reaches 325 conditions and 404 sources.

**Architecture:** Extend the static catalog with one named batch, regenerate the reviewed runtime JSON through the reviewed import command, and update governance surfaces that expose catalog counts. Keep UI behavior unchanged in this slice.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django test runner, existing management commands.

---

### Task 1: Failing Coverage Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`

- [x] **Step 1: Add milestone quality test**

Assert the catalog reaches at least 325 conditions, at least 404 sources, zero blockers, zero warnings, and a completed `expand_condition_catalog_to_325` next action.

- [x] **Step 2: Add searchability test**

Assert text search can surface all 25 new slugs: aortic stenosis, dilated cardiomyopathy, pertussis, norovirus gastroenteritis, gastritis, Helicobacter pylori infection, gestational diabetes, hyperemesis gravidarum, trichomoniasis, overactive bladder, pancreatic cancer, liver cancer, stomach cancer, esophageal cancer, endometrial cancer, thyroid cancer, squamous cell carcinoma skin, alopecia areata, vitiligo, dry eye disease, cataract, age-related macular degeneration, diabetic retinopathy, hand foot mouth disease, and thyroid nodule.

- [x] **Step 3: Verify RED**

Run:

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality.GeneralDifferentialCatalogQualityTests.test_eighth_generalist_batch_expands_catalog_to_325_without_warnings cds_core.tests.test_general_differential.GeneralDifferentialEngineTests.test_eighth_generalist_batch_adds_25_more_searchable_conditions -v 2
```

Expected: fail because the static catalog is still at 300 conditions.

### Task 2: Catalog And Reviewed JSON

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] **Step 1: Add source rows and condition batch**

Add the eighth generalist batch with two or more sources per condition and update the expansion target to 325.

- [x] **Step 2: Regenerate reviewed runtime JSON**

Run:

```powershell
$tmp = Join-Path $env:TEMP 'general_differential_catalog_reviewed_325.json'
py -B manage.py export_general_differential_review_seed --pretty | Set-Content -LiteralPath $tmp -Encoding UTF8
py -B manage.py import_general_differential_reviewed_catalog --path $tmp --output cds_core/data/general_differential_catalog_reviewed.json --apply --overwrite
```

Expected: `APPLIED reviewed catalog import: 325 conditions, 404 sources`.

- [x] **Step 3: Verify GREEN**

Run the targeted command from Task 1 again.

Expected: 2 tests pass.

### Task 3: Governance Count Updates

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`

- [x] **Step 1: Update count assertions**

Update exact milestone expectations from 300/379 to 325/404 where the tests assert the current reviewed catalog summary.

- [x] **Step 2: Verify related tests**

Run:

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality cds_core.tests.test_general_differential cds_core.tests.test_next_actions cds_core.tests.test_general_differential_import_workbench cds_core.tests.test_differential_import_validation cds_core.tests.test_dyspnea_pathway -v 2
```

Expected: all related tests pass.

### Task 4: Final Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] **Step 1: Run full suite**

```powershell
py -B manage.py test -v 2
```

- [x] **Step 2: Run validators and import preview**

```powershell
py -B manage.py validate_general_differential_reviewed_catalog_data
py -B manage.py validate_general_differential_catalog
py -B manage.py import_general_differential_reviewed_catalog --path cds_core/data/general_differential_catalog_reviewed.json
```

- [ ] **Step 3: Commit and push**

```powershell
git add clinical_differential_support/cds_core/differential_catalog.py clinical_differential_support/cds_core/differential_catalog_quality.py clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py clinical_differential_support/cds_core/tests/test_general_differential.py clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py clinical_differential_support/cds_core/tests/test_next_actions.py docs/superpowers/specs/2026-07-01-expand-general-catalog-to-325-design.md docs/superpowers/plans/2026-07-01-expand-general-catalog-to-325.md
git commit -m "Expand general differential catalog to 325 conditions"
git push origin master
```

- [ ] **Step 4: Public smoke**

Smoke the protected import workbench redirect, public differential route, sparse-input POST workflow, and one new query such as `pertussis` after Render deploys the pushed commit.
