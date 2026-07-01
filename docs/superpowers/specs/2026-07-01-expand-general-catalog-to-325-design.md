# Expand General Differential Catalog To 325 Design

## Goal

Expand the clinician-only general differential catalog from 300 to 325 source-backed conditions while preserving the stepwise workflow, reviewed runtime JSON pipeline, and zero-warning publication gate.

## Chosen Approach

Use a small reviewed-data slice instead of a broad unreviewed import. The static catalog gains a named eighth generalist batch, the reviewed JSON is regenerated through the import apply command, and the workbench and next-action reports advance their milestone counts from 300/379 to 325/404.

This keeps the system moving toward broad primary-care coverage without pretending the whole medical universe is complete.

## Data Scope

The batch adds 25 high-yield cross-system conditions across cardiology, infection, GI, pregnancy, urology, oncology, dermatology, ophthalmology, pediatrics, and thyroid evaluation.

Every new condition must have at least two linked sources, bilingual clinician-facing phrasing, non-ordering next-step prompts, and searchable English labels or aliases.

## Safety Rules

- Clinician-only reference support; not patient-facing diagnosis.
- No diagnosis certainty, medication orders, treatment plans, or prescribing instructions.
- No patient data in reviewed catalog payloads.
- No publishable milestone unless validation reports zero blockers and zero warnings.

## Acceptance Checks

- Targeted tests prove the 325 milestone and named-condition search behavior.
- Related catalog, next-action, import-workbench, import-validation, and dyspnea tests pass.
- Full Django suite passes.
- Reviewed data validator reports 325 conditions, 404 sources, zero blockers, and zero warnings.
- Catalog validator reports 325 conditions, 404 sources, zero blockers, and zero warnings.
- Reviewed import dry-run accepts the packaged JSON.
- Public Render smoke confirms the deployed differential page still loads and the stepwise sparse-input workflow still renders.
