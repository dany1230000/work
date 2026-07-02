# General Differential 425 Compact Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next reviewed 25-condition slice so the general differential catalog reaches 425 conditions, then make the workbench tell the clinician what to do next through quick system entry and scan-first results.

**Architecture:** Extend the static catalog with one named batch, regenerate the reviewed runtime JSON through the existing reviewed import command, update milestone expectations, and add template-only scan and drawer structure around existing ranked results.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django templates, vanilla JavaScript, Django test runner, existing management commands.

---

### Task 1: Failing Catalog And UI Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [x] **Step 1: Add the 425 milestone quality test**

Add `test_twelfth_generalist_batch_expands_catalog_to_425_without_warnings` asserting at least 425 conditions, at least 503 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_425`.

- [x] **Step 2: Add the 25-condition searchability test**

Add `test_twelfth_generalist_batch_adds_25_more_searchable_conditions` with exact query-to-slug expectations for every new condition in the twelfth batch.

- [x] **Step 3: Add quick-entry and scan-first UI tests**

Assert the empty page renders catalog quick-entry shortcuts and posted results render a candidate scan table before collapsed detailed cards.

- [x] **Step 4: Verify RED**

Run focused tests and confirm they fail because the catalog target, new slugs, and UI markers are not implemented yet.

### Task 2: Catalog And Reviewed JSON

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] **Step 1: Add source rows**

Add official source rows for NIDDK, CDC, NHLBI, NICHD, MedlinePlus, and NINDS references used by the twelfth batch.

- [x] **Step 2: Add the twelfth generalist batch**

Append 25 condition entries using the established `_eighth_generalist_condition` helper and extend `CONDITIONS`.

- [x] **Step 3: Update the expansion target**

Set `EXPANSION_TARGET_CONDITIONS = 425`.

- [x] **Step 4: Regenerate reviewed runtime JSON**

```powershell
$tmp = Join-Path $env:TEMP 'general_differential_catalog_reviewed_425.json'
py -B manage.py export_general_differential_review_seed --pretty | Set-Content -LiteralPath $tmp -Encoding UTF8
py -B manage.py import_general_differential_reviewed_catalog --path $tmp --output cds_core/data/general_differential_catalog_reviewed.json --apply --overwrite
```

Expected: `APPLIED reviewed catalog import: 425 conditions, 503 sources`.

### Task 3: Compact Workbench Results

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] **Step 1: Add catalog quick entries**

Build system-level quick entries in the view and render buttons that place useful queries into the existing query input.

- [x] **Step 2: Add scan-first results**

Render the top five candidates as a compact scan table before detailed result cards.

- [x] **Step 3: Collapse primary detailed cards**

Move the primary result cards into a details drawer so long condition cards no longer dominate the result page.

### Task 4: Governance Count Updates

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`

- [x] **Step 1: Update exact count assertions**

Update current reviewed catalog expectations from 400/478 to 425/503 after regeneration.

### Task 5: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] **Step 1: Run targeted tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality.GeneralDifferentialCatalogQualityTests.test_twelfth_generalist_batch_expands_catalog_to_425_without_warnings cds_core.tests.test_general_differential.GeneralDifferentialEngineTests.test_twelfth_generalist_batch_adds_25_more_searchable_conditions cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_general_differential_page_shows_catalog_quick_entry_shortcuts cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_posted_findings_show_candidate_scan_table_before_collapsed_cards
```

- [x] **Step 2: Run related tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality cds_core.tests.test_general_differential cds_core.tests.test_general_differential_ui cds_core.tests.test_general_differential_import_workbench cds_core.tests.test_next_actions cds_core.tests.test_dyspnea_pathway cds_core.tests.test_stepwise_ui
```

- [x] **Step 3: Run full suite and validators**

```powershell
py -B manage.py test cds_core.tests
py -B manage.py validate_general_differential_catalog
py -B manage.py validate_general_differential_reviewed_catalog_data
py -B manage.py import_general_differential_reviewed_catalog --path cds_core/data/general_differential_catalog_reviewed.json
```

- [ ] **Step 4: Commit, push, and public smoke**

Commit the exact staged phase files, push `origin master`, then smoke `https://clinical-differential-support.onrender.com/differential/` with CSRF GET/POST and a new query such as `wilson disease`.

### Next Phase Candidate

After this phase is verified publicly, continue with a 450-condition slice plus mobile result density and source-review shortcuts.
