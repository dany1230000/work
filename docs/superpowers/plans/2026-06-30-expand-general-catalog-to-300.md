# Expand General Catalog To 300 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the clinician-facing general differential catalog from 250 to at least 300 reviewed conditions while keeping catalog validation at 0 blocking issues and 0 warnings.

**Architecture:** Keep the current static catalog pattern in `cds_core/differential_catalog.py`: source metadata in `SOURCES`, condition dictionaries in an appended batch, and quality enforcement in `cds_core/tests/test_differential_catalog_quality.py`. Each new condition must carry at least two verified source IDs before it is added to `CONDITIONS`; no later warning-cleanup pass should be needed.

**Tech Stack:** Django, Python unittest, existing catalog validators, static reviewed JSON export.

---

### Task 1: Add The Expansion Gate

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`

- [ ] **Step 1: Write the failing test**

Add a test requiring at least 300 conditions, at least 342 sources, zero blocking issues, and zero warnings. The source floor is 292 existing sources plus at least one net-new source per added condition.

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `py -B manage.py test cds_core.tests.test_differential_catalog_quality.GeneralDifferentialCatalogQualityTests.test_seventh_generalist_batch_expands_catalog_to_300_without_warnings`

Expected: FAIL because the current catalog has 250 conditions.

### Task 2: Add The Seventh Generalist Batch

**Files:**
- Modify: `clinical_differential_support/cds_core/differential_catalog.py`

- [ ] **Step 1: Add source metadata**

Add official or academic sources for the 50 new conditions. Reuse existing source IDs only when clinically appropriate, but every new condition must end with at least two source IDs.

- [ ] **Step 2: Add condition metadata**

Add a seventh batch helper or reuse the current sixth-batch helper style. Each condition needs Chinese and English names, system bucket, urgency level, presentation triggers, risk cues, recommended next questions, safety reminder text, and source IDs.

- [ ] **Step 3: Run the targeted test**

Run: `py -B manage.py test cds_core.tests.test_differential_catalog_quality.GeneralDifferentialCatalogQualityTests.test_seventh_generalist_batch_expands_catalog_to_300_without_warnings`

Expected: PASS.

### Task 3: Regenerate Reviewed Catalog Data

**Files:**
- Modify: `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [ ] **Step 1: Regenerate the reviewed static data file**

Run the existing reviewed catalog generation command or script used by previous phases.

- [ ] **Step 2: Run catalog validators**

Run:

```powershell
py -B manage.py validate_general_differential_catalog
py -B manage.py validate_general_differential_review_seed
py -B manage.py validate_general_differential_reviewed_catalog_data
```

Expected: READY, 300 conditions or more, 342 sources or more, 0 blocking issues, 0 warnings.

### Task 4: Full Verification And Publish

**Files:**
- Stage only:
  - `docs/superpowers/plans/2026-06-30-expand-general-catalog-to-300.md`
  - `clinical_differential_support/cds_core/tests/test_differential_catalog_quality.py`
  - `clinical_differential_support/cds_core/differential_catalog.py`
  - `clinical_differential_support/cds_core/data/general_differential_catalog_reviewed.json`

- [ ] **Step 1: Run full verification**

Run:

```powershell
py -B manage.py test
py -B manage.py check
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Commit and push**

Commit message: `Expand differential catalog to 300 entries`

- [ ] **Step 3: Public smoke test**

After deployment, verify the public site reports at least 300 conditions, at least 342 sources, 0 warnings, and still shows the guided follow-up workflow.

### Self-Review

- Spec coverage: covers catalog size, source depth, zero-warning governance, regenerated reviewed data, full tests, and public smoke testing.
- Placeholder scan: no TBD/TODO placeholders.
- Type consistency: uses existing Django unittest and catalog validator surfaces.
