# General Differential Import Workbench Design

## Goal

Build a staff-only governance workbench that tells reviewers which general differential catalog areas should be expanded next, how a reviewed batch must be prepared, and which validation commands must pass before catalog content can be treated as publishable.

## Scope

This phase does not add new medical conditions. It adds the workflow surface needed to expand the catalog safely after the current 300-condition milestone: gap visibility, import format guidance, validation commands, and JSON export evidence.

The workbench remains clinician-facing and source-backed. It must not collect patient data, issue diagnosis, treatment, medication, or clinical-order instructions, or present unreviewed content as publishable.

## Architecture

Create a small report builder that composes existing catalog quality, review seed, and batch-template helpers. The builder returns a deterministic dictionary for the HTML page and JSON export. Views and templates follow the existing staff governance pattern used by release readiness, coverage depth, and source freshness.

## User Flow

1. A staff reviewer opens the governance dashboard.
2. They choose "通用鑑別匯入工作台 / General Differential Import Workbench".
3. They see catalog totals, weakest specialty buckets, and a ranked next-batch recommendation.
4. They follow the command sequence to export the review seed, export the batch template, validate the seed, validate the batch payload, and validate the runtime catalog.
5. They can export the same report as JSON for handoff or deployment evidence.

## Data Contract

The report exposes:

- `summary`: condition count, source count, blocker count, warning count, format versions, and target state.
- `next_batch`: lowest-coverage specialty buckets sorted by current count, with recommended batch size and review rationale.
- `import_pipeline`: ordered command checklist using existing management-command surfaces.
- `safety_scope`: explicit no-patient-data and no-clinical-order boundaries.
- `exports`: JSON endpoint metadata.

## Testing

Use TDD with one focused test module. Tests must prove:

- unauthenticated users are redirected to the reviewer login;
- staff users can render the workbench page;
- the page contains next-batch, import-pipeline, safety, and export markers;
- the JSON export contains only governance metadata and no patient-identifying workflow;
- the governance dashboard and readiness page link to the new workbench.

## Acceptance Criteria

- Staff-only page at `/review/general-differential-import/`.
- Staff-only JSON export at `/review/exports/general-differential-import.json`.
- The page names the current 300-condition and 379-source catalog state.
- The page shows a concrete next-batch table and a command checklist.
- Existing full test suite and catalog validator pass.
- Local and public smoke checks prove the page and export render after deployment.
