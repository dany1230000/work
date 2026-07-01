# General Differential 350 Compact Workbench Implementation Plan

> **For agentic workers:** continue task-by-task, update checkboxes as work lands, and do not stage unrelated existing changes such as `clinical_differential_support/cds_core/templates/cds_core/home.html`.

**Goal:** Add the next reviewed 25-condition slice so the general differential catalog reaches 350 conditions and 429 sources, then shorten the posted result workflow into a step-by-step workbench.

**Architecture:** Extend the static catalog with one named batch, regenerate the reviewed runtime JSON through the reviewed import command, update governance count expectations, and add a compact result summary strip in the existing Django template.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django templates, Django test runner, existing management commands.

---

### Task 1: Failing Coverage And UI Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [x] **Step 1: Add milestone quality test**

Assert the catalog reaches at least 350 conditions, at least 429 sources, zero blockers, zero warnings, and a completed 350-condition next action.

- [x] **Step 2: Add searchability test**

Assert text search can surface all 25 new slugs from the ninth generalist batch.

- [x] **Step 3: Add compact results test**

Assert posted findings render a next-step summary strip before the longer brief, guided follow-up, and result card sections.

### Task 2: Catalog And Reviewed JSON

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] **Step 1: Add source rows and condition batch**

Add the ninth generalist batch with source-backed entries and update the expansion target to 350.

- [x] **Step 2: Regenerate reviewed runtime JSON**

```powershell
$tmp = Join-Path $env:TEMP 'general_differential_catalog_reviewed_350.json'
py -B manage.py export_general_differential_review_seed --pretty | Set-Content -LiteralPath $tmp -Encoding UTF8
py -B manage.py import_general_differential_reviewed_catalog --path $tmp --output cds_core/data/general_differential_catalog_reviewed.json --apply --overwrite
```

Expected: `APPLIED reviewed catalog import: 350 conditions, 429 sources`.

### Task 3: Result Workbench Compression

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] **Step 1: Add next-step summary strip**

Place immediate action, top candidate, next question, and source count before the longer evidence sections.

- [x] **Step 2: Collapse guided follow-up**

Convert guided follow-up into a disclosure block so the result page starts with action and triage, not a long text section.

### Task 4: Governance Count Updates

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`

- [x] **Step 1: Update count assertions**

Update exact milestone expectations from 325/404 to 350/429 where tests assert the current reviewed catalog summary.

### Task 5: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] **Step 1: Run targeted tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality.GeneralDifferentialCatalogQualityTests.test_ninth_generalist_batch_expands_catalog_to_350_without_warnings cds_core.tests.test_general_differential.GeneralDifferentialEngineTests.test_ninth_generalist_batch_adds_25_more_searchable_conditions cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_posted_findings_show_next_step_summary_strip_before_long_sections cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_posted_findings_show_guided_follow_up_before_result_cards
```

- [x] **Step 2: Run related tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality cds_core.tests.test_general_differential cds_core.tests.test_general_differential_ui cds_core.tests.test_general_differential_import_workbench cds_core.tests.test_next_actions cds_core.tests.test_dyspnea_pathway
```

- [x] **Step 3: Run full suite**

```powershell
py -B manage.py test cds_core.tests
```

- [x] **Step 4: Run validators and import preview**

```powershell
py -B manage.py validate_general_differential_catalog
py -B manage.py validate_general_differential_reviewed_catalog_data
py -B manage.py import_general_differential_reviewed_catalog --path cds_core/data/general_differential_catalog_reviewed.json
```

- [ ] **Step 5: Commit and push**

```powershell
git add docs/superpowers/specs/2026-07-02-general-differential-350-compact-workbench-design.md docs/superpowers/plans/2026-07-02-general-differential-350-compact-workbench.md clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json clinical_differential_support/cds_core/differential_catalog.py clinical_differential_support/cds_core/differential_catalog_quality.py clinical_differential_support/cds_core/templates/cds_core/general_differential.html clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py clinical_differential_support/cds_core/tests/test_general_differential.py clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py clinical_differential_support/cds_core/tests/test_general_differential_ui.py clinical_differential_support/cds_core/tests/test_next_actions.py
git commit -m "Expand general differential catalog to 350 conditions"
git push origin master
```

- [ ] **Step 6: Public smoke**

Smoke the public differential route after Render deploys the pushed commit. Confirm the page loads, the packaged catalog count is no lower than 350, and a sparse clinical query still renders the posted results workflow.

### Next Phase Candidate

After this phase is verified publicly, continue with a 375-condition slice and a dedicated differential result grouping pass so the app can scale toward broad disease coverage without making each result page longer.
