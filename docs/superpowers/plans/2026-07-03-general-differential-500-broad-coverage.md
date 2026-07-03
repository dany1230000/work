# General Differential 500 Broad Coverage Implementation Plan

**Goal:** Expand the reviewed general differential catalog from 475 to 500 conditions while preserving the faster scan-first result page.

**Architecture:** Add a fifteenth static catalog batch, regenerate reviewed JSON through the existing importer, advance exact governance counts to 500/578, and keep UI behavior unchanged except for the already shipped step rail.

### Task 1: Failing Tests

- [x] Add a quality test for 500 conditions, 578 sources, zero blockers, zero warnings, and completed `expand_condition_catalog_to_500`.
- [x] Add a searchability test for the 25 new condition slugs.
- [x] Update exact reviewed catalog count assertions from 475/553 to 500/578.
- [x] Run focused tests and confirm RED before implementation.

### Task 2: Catalog And Reviewed Data

- [x] Add 25 reviewed source rows from CDC and MedlinePlus, with existing Merck professional fallback.
- [x] Add the fifteenth 25-condition batch and extend `CONDITIONS`.
- [x] Set `EXPANSION_TARGET_CONDITIONS = 500`.
- [x] Regenerate `cds_core/data/general_differential_catalog_reviewed.json`.

### Task 3: Verification And Publish

- [x] Run focused tests.
- [x] Run related tests.
- [x] Run full `cds_core.tests` suite and validators.
- [x] Run local CSRF smoke.
- [x] Commit, push, and public Render smoke.

### Next Phase Candidate

After this phase is verified publicly, continue with the 525-condition slice and add a source/provenance filter surface for long candidate lists.
