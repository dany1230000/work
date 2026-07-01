# General Differential 350 Compact Workbench Design

## Goal

Advance the clinician-only general differential workspace from 325 to 350 source-backed conditions and make posted results immediately tell the clinician what to do next before long evidence sections.

## Chosen Approach

Add one reviewed 25-condition slice to the static catalog, regenerate the packaged reviewed JSON, and keep the publication gate at zero blockers and zero warnings. In the UI, place a compact next-step summary strip before the brief, guided follow-up, and detailed result cards so the page reads step-by-step instead of long-form.

This phase keeps the product moving toward broad primary-care differential support without presenting it as complete coverage for every possible disease.

## Data Scope

The ninth generalist slice adds conditions across bone health, ENT, dermatology, infectious disease, hematology, psychiatry, oncology, ophthalmology, audiology, rheumatology, dermatology, urology, and bladder pain evaluation.

Every new condition must keep clinician-facing bilingual wording, source-backed references, non-ordering next-step prompts, searchable English labels or aliases, and no patient data.

## UX Scope

- Show a four-card next-step summary immediately after submitted findings.
- Surface immediate action, top candidate, next question, and source count at a glance.
- Keep the detailed guided follow-up available but collapsed behind a native disclosure control.
- Preserve the no-reload and lazy findings behavior from earlier phases.

## Safety Rules

- Clinician-only reference support; not patient-facing diagnosis.
- No diagnosis certainty, medication orders, treatment plans, or prescribing instructions.
- No patient data in reviewed catalog payloads.
- No publishable milestone unless validation reports zero blockers and zero warnings.

## Acceptance Checks

- Catalog quality proves at least 350 conditions, at least 429 sources, zero blockers, and zero warnings.
- Search tests prove all 25 new slugs are findable.
- Posted differential results show the next-step strip before long sections.
- Guided follow-up stays available but no longer dominates the first result viewport.
- Related catalog, next-action, import-workbench, UI, and dyspnea tests pass.
- Full Django test suite passes.
- Reviewed data validator and static catalog validator both report 350 conditions and 429 sources.
- Reviewed import preview accepts the packaged JSON.
- Public Render smoke confirms the deployed differential page and sparse-input workflow still load after push.
