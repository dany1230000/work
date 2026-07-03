# General Differential 475 Step Rail Design

## Goal

Move the clinician-only general differential workspace from 450 to 475 reviewed conditions and make posted results easier to use by showing the immediate step order before the long explanatory workflow.

## Chosen Approach

Use a 25-condition slice focused on still-missing cross-specialty gaps: fungal and parasitic infections, voice/laryngeal disorders, oral and skin disease, endocrine and hematology/systemic disease, rheumatic sequelae, renal/urologic obstruction, and neonatal gastrointestinal disorders. The reviewed JSON remains the runtime source.

For usability, add a compact step rail above the detailed patient workflow. It mirrors existing workflow steps and uses short labels only, so it clarifies what to do next without adding new clinical logic or making the page longer.

## Data Scope

The fourteenth generalist slice covers:

- Histoplasmosis, coccidioidomycosis, toxoplasmosis, giardiasis, pinworm infection, schistosomiasis, strongyloidiasis, ascariasis, Rocky Mountain spotted fever, and Chagas disease.
- Laryngitis, vocal cord paralysis, oral candidiasis, pityriasis rosea, lichen planus, and pressure injury.
- Primary hyperaldosteronism, amyloidosis, acute rheumatic fever, rheumatic heart disease, and IgA vasculitis.
- Hydronephrosis, pyloric stenosis, necrotizing enterocolitis, and Hirschsprung disease.

## UX Scope

- Render `data-stepwise-next-rail="true"` before the detailed patient workflow.
- Render one `data-stepwise-next-rail-item="true"` for each mirrored workflow step.
- Keep the detailed workflow, summary strip, action queue, candidate scan, collapsed primary cards, secondary drawer, and source links unchanged.

## Safety Rules

- Clinician-only reference support; not patient-facing diagnosis.
- No diagnosis certainty, medication orders, treatment plans, or prescribing instructions.
- No patient data in reviewed catalog payloads.
- No publishable milestone unless validation reports zero blockers and zero warnings.

## Acceptance Checks

- Catalog quality proves at least 475 conditions, at least 553 sources, zero blockers, and zero warnings.
- Search tests prove all 25 new slugs are findable.
- Posted differential results show the compact step rail before the detailed workflow and before candidate scan.
- Related catalog, next-action, import-workbench, UI, and dyspnea tests pass.
- Full Django test suite passes.
- Reviewed data validator and static catalog validator both report 475 conditions and 553 sources.
- Reviewed import preview accepts the packaged JSON.
- Public Render smoke confirms the deployed differential page, step rail UI, source shortcut UI, and a new query after push.
