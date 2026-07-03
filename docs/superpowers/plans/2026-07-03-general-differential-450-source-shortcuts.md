# General Differential 450 Source Shortcuts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next reviewed 25-condition slice so the general differential catalog reaches 450 conditions, then make scan-first results expose source review shortcuts before detailed cards.

**Architecture:** Extend the static catalog with one named batch, regenerate the reviewed runtime JSON through the existing reviewed import command, update milestone expectations, and add presentation-only scan table source counts/shortcuts around existing ranked results.

**Tech Stack:** Django, Python catalog modules, reviewed JSON runtime data, Django templates, vanilla CSS, Django test runner, existing management commands.

---

### Task 1: Failing Catalog And UI Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential.py`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [x] **Step 1: Add the 450 milestone quality test**

Add `test_thirteenth_generalist_batch_expands_catalog_to_450_without_warnings` asserting at least 450 conditions, at least 528 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_450`.

- [x] **Step 2: Add the 25-condition searchability test**

Add `test_thirteenth_generalist_batch_adds_25_more_searchable_conditions` with exact query-to-slug expectations for every new condition in the thirteenth batch.

- [x] **Step 3: Add source shortcut UI test**

Assert posted results render `data-candidate-scan-density="compact"`, `data-candidate-source-count="true"`, and `data-candidate-source-shortcut="true"` before detailed result cards.

- [x] **Step 4: Verify RED**

Run focused tests and confirm they fail because the catalog target, new slugs, and UI markers are not implemented yet.

### Task 2: Catalog And Reviewed JSON

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`
- Modify: `clinical_differential_support/cds_core/differential_catalog_quality.py`
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [x] **Step 1: Add source rows**

Add official and high-trust source rows for CDC, NIDDK, NCI, NIDCD, NINDS, NIDCR, NHLBI, AASLD, MedlinePlus, and Merck references used by the thirteenth batch.

- [x] **Step 2: Add the thirteenth generalist batch**

Append 25 condition entries using the established `_eighth_generalist_condition` helper and extend `CONDITIONS`.

- [x] **Step 3: Update the expansion target**

Set `EXPANSION_TARGET_CONDITIONS = 450`.

- [x] **Step 4: Regenerate reviewed runtime JSON**

```powershell
$tmp = Join-Path $env:TEMP 'general_differential_catalog_reviewed_450.json'
py -B manage.py export_general_differential_review_seed --pretty | Set-Content -LiteralPath $tmp -Encoding UTF8
py -B manage.py import_general_differential_reviewed_catalog --path $tmp --output cds_core/data/general_differential_catalog_reviewed.json --apply --overwrite
```

Expected: `APPLIED reviewed catalog import: 450 conditions, 528 sources`.

### Task 3: Compact Source Shortcuts

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [x] **Step 1: Add compact scan density marker**

Add `data-candidate-scan-density="compact"` to the candidate scan section.

- [x] **Step 2: Add source count tags**

Render each scan row with a `data-candidate-source-count="true"` marker and source count from `entry.sources|length`.

- [x] **Step 3: Add source shortcut link**

Render a `data-candidate-source-shortcut="true"` link to `#top-candidates` with the text `Review sources` before the primary detailed-card drawer.

### Task 4: Governance Count Updates

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`
- Modify: `clinical_differential_support/cds_core/tests/test_dyspnea_pathway.py`
- Modify: `clinical_differential_support/cds_core/tests/test_next_actions.py`

- [x] **Step 1: Update exact count assertions**

Update current reviewed catalog expectations from 425/503 to 450/528 after regeneration.

### Task 5: Verification And Publish

**Files:**
- Stage only this phase's code, data, test, and doc files.
- Do not stage `clinical_differential_support/cds_core/templates/cds_core/home.html`.

- [x] **Step 1: Run targeted tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_catalog_quality.GeneralDifferentialCatalogQualityTests.test_thirteenth_generalist_batch_expands_catalog_to_450_without_warnings cds_core.tests.test_general_differential.GeneralDifferentialEngineTests.test_thirteenth_generalist_batch_adds_25_more_searchable_conditions cds_core.tests.test_general_differential_ui.GeneralDifferentialUiTests.test_candidate_scan_table_shows_source_shortcuts_and_mobile_density_markers
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

Commit the exact staged phase files, push `origin master`, then smoke `https://clinical-differential-support.onrender.com/differential/` with CSRF GET/POST and a new query such as `sickle cell disease`.

### Next Phase Candidate

After this phase is verified publicly, continue with a 475-condition slice plus clearer source provenance filtering and printable handoff density.
