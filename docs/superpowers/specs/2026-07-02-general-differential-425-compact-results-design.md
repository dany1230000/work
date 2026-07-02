# General Differential 425 Compact Results Design

## Goal

Advance the clinician-only general differential workspace from 400 to 425 source-backed conditions and make the result page more usable for broad patient presentations by adding quick catalog entry shortcuts plus a scan-first candidate table before detailed cards.

## Chosen Approach

Use another reviewed 25-condition slice focused on genetic, congenital, metabolic, hematologic, neurodevelopmental, and neuromuscular conditions. The static catalog gains a twelfth generalist batch, the packaged reviewed JSON is regenerated through the existing import command, and tests advance the governance milestone from 400/478 to 425/503.

The UI remains a clinical workbench instead of a long report. It adds system quick-entry shortcuts near the input flow and replaces the first long-card impression with a candidate scan table followed by collapsed detailed candidate cards.

## Data Scope

The twelfth generalist slice covers:

- Wilson disease, hereditary hemochromatosis, fragile X syndrome, Marfan syndrome, Turner syndrome, Klinefelter syndrome, and congenital adrenal hyperplasia.
- G6PD deficiency, hereditary spherocytosis, phenylketonuria, maple syrup urine disease, galactosemia, and achondroplasia.
- Neurofibromatosis, tuberous sclerosis complex, Ehlers-Danlos syndrome, Noonan syndrome, Prader-Willi syndrome, Angelman syndrome, Rett syndrome, and 22q11.2 deletion syndrome.
- Congenital hypothyroidism, Tay-Sachs disease, Gaucher disease, and Pompe disease.

Every new condition keeps clinician-facing bilingual wording, official source references, conservative next-step prompts, searchable English labels or aliases, and no patient data.

## UX Scope

- Add `catalog_quick_entries` to the differential page for high-yield systems.
- Render `data-catalog-quick-entry="true"` with shortcut buttons that fill the query box.
- Render `data-candidate-scan-table="true"` before detailed candidate cards.
- Move primary detailed cards into `data-primary-result-drawer="true"` so the page reads step by step instead of as a long wall of cards.
- Keep existing result brief, action queue, patient workflow, candidate groups, secondary candidates, and source links.

## Safety Rules

- Clinician-only reference support; not patient-facing diagnosis.
- No diagnosis certainty, medication orders, treatment plans, or prescribing instructions.
- No patient data in reviewed catalog payloads.
- No publishable milestone unless validation reports zero blockers and zero warnings.

## Acceptance Checks

- Catalog quality proves at least 425 conditions, at least 503 sources, zero blockers, and zero warnings.
- Search tests prove all 25 new slugs are findable.
- Differential page shows catalog quick-entry shortcuts.
- Posted differential results show the candidate scan table before collapsed detailed cards.
- Related catalog, next-action, import-workbench, UI, and dyspnea tests pass.
- Full Django test suite passes.
- Reviewed data validator and static catalog validator both report 425 conditions and 503 sources.
- Reviewed import preview accepts the packaged JSON.
- Public Render smoke confirms the deployed differential page, quick-entry UI, scan-first result workflow, and a new query after push.
