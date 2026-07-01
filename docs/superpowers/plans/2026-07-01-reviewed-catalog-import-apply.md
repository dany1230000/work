# Reviewed Catalog Import Apply Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe reviewed-catalog import command that previews, validates, and explicitly writes reviewed catalog JSON for the general differential runtime data pipeline.

**Architecture:** Extend `cds_core.differential_catalog_import` with preview/apply helpers, add a Django management command, and expose the command in the existing staff import workbench. The command never writes by default and reuses the current payload validator.

**Tech Stack:** Django management commands, Python JSON, existing general differential catalog validator, Django test runner.

---

### Task 1: Import Preview And Apply Helper

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog_import.py`
- Modify: `clinical_differential_support/cds_core/tests/test_differential_import_validation.py`

- [x] **Step 1: Write failing helper tests**

Add tests asserting `preview_general_differential_review_import()` returns `ready_to_apply` for the current review seed and that `write_reviewed_catalog_payload()` writes UTF-8 JSON with the same condition/source counts.

- [x] **Step 2: Run helper tests and verify RED**

Run:

```powershell
py -B manage.py test cds_core.tests.test_differential_import_validation.GeneralDifferentialImportValidationTests.test_review_import_preview_marks_valid_payload_ready cds_core.tests.test_differential_import_validation.GeneralDifferentialImportValidationTests.test_write_reviewed_catalog_payload_outputs_valid_json -v 2
```

Expected: fail because the helper functions do not exist.

- [x] **Step 3: Implement helpers**

Add focused helpers that validate payloads, build a summary-only preview report, and write JSON only when called by the command.

- [x] **Step 4: Run helper tests and verify GREEN**

Run the same targeted command. Expected: 2 tests pass.

### Task 2: Management Command

**Files:**
- Create: `clinical_differential_support/cds_core/management/commands/import_general_differential_reviewed_catalog.py`
- Modify: `clinical_differential_support/cds_core/tests/test_differential_import_validation.py`

- [x] **Step 1: Write failing command tests**

Add tests for dry-run preview, explicit apply output, invalid payload rejection, and overwrite protection.

- [x] **Step 2: Run command tests and verify RED**

Run:

```powershell
py -B manage.py test cds_core.tests.test_differential_import_validation.GeneralDifferentialImportValidationCommandTests -v 2
```

Expected: fail because the command does not exist.

- [x] **Step 3: Implement command**

The command accepts `--path`, optional `--output`, `--apply`, and `--overwrite`. It prints `READY reviewed catalog import preview` for dry-run and `APPLIED reviewed catalog import` after writing.

- [x] **Step 4: Run command tests and verify GREEN**

Run the same command test class. Expected: all command tests pass.

### Task 3: Workbench Exposure

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog_workbench.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential_import.html`
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`

- [x] **Step 1: Write failing workbench test**

Assert the staff workbench and JSON export include the new apply command and an explicit no-auto-apply safety note.

- [x] **Step 2: Run workbench tests and verify RED**

Run:

```powershell
py -B manage.py test cds_core.tests.test_general_differential_import_workbench -v 2
```

Expected: fail because the workbench does not expose the command.

- [x] **Step 3: Add workbench command step**

Add `import_general_differential_reviewed_catalog --path reviewed.json --output cds_core/data/general_differential_catalog_reviewed.json --apply --overwrite` as a documented governance step, with dry-run first.

- [x] **Step 4: Run workbench tests and verify GREEN**

Run the same workbench test command. Expected: all pass.

### Task 4: Verification And Deployment

**Files:**
- No new production files expected.

- [x] **Step 1: Run targeted tests**

```powershell
py -B manage.py test cds_core.tests.test_differential_import_validation cds_core.tests.test_general_differential_import_workbench -v 2
```

- [x] **Step 2: Run full suite**

```powershell
py -B manage.py test -v 2
```

- [x] **Step 3: Run validators**

```powershell
py -B manage.py validate_general_differential_reviewed_catalog_data
py -B manage.py validate_general_differential_catalog
```

- [x] **Step 4: Run command smoke**

```powershell
py -B manage.py import_general_differential_reviewed_catalog --path cds_core/data/general_differential_catalog_reviewed.json
```

- [ ] **Step 5: Commit, push, and public smoke**

Commit only this stage's files, push to `master`, then public-smoke the staff-protected workbench redirect and public differential route.
