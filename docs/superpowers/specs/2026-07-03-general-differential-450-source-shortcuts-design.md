# General Differential 450 Source Shortcuts Design

## Goal

Advance the clinician-only general differential workspace from 425 to 450 source-backed conditions and make the scan-first result page faster to use on mobile by exposing source-review shortcuts before detailed cards.

## Chosen Approach

Use another reviewed 25-condition slice focused on common cross-specialty gaps that are not just aliases of existing entries: gynecology/breast, hepatology, hematology/oncology, ENT/audiology, infection, dermatology/foot, vascular/rehab, pain/dental, pulmonary, urology, and ophthalmology. The static catalog gains a thirteenth generalist batch, the packaged reviewed JSON is regenerated through the existing import command, and tests advance the governance milestone from 425/503 to 450/528.

For the UI, keep the existing candidate scan table but make it denser and more useful: each scan row shows the linked-source count and a shortcut to open the detailed candidate cards where full source links live. This avoids adding new clinical logic while reducing the amount of scrolling needed before source review.

## Data Scope

The thirteenth generalist slice covers:

- Adenomyosis and mastitis.
- Alcohol-associated liver disease and anemia of chronic disease.
- Sickle cell disease, non-Hodgkin lymphoma, and Hodgkin lymphoma.
- Otosclerosis, vestibular schwannoma, and noise-induced hearing loss.
- Mumps, rubella, molluscum contagiosum, balanitis, hordeolum, and ingrown toenail.
- Lymphedema, varicose veins, pleural effusion, varicocele, hydrocele, plantar wart, chalazion, complex regional pain syndrome, and temporomandibular disorder.

Every new condition keeps clinician-facing bilingual wording, official source references, conservative next-step prompts, searchable English labels or aliases, and no patient data.

## UX Scope

- Render `data-candidate-scan-density="compact"` on the scan table.
- Render `data-candidate-source-count="true"` in scan rows.
- Render `data-candidate-source-shortcut="true"` before the primary detailed-card drawer.
- Keep existing result brief, action queue, patient workflow, candidate groups, collapsed primary cards, secondary drawer, and source links.

## Safety Rules

- Clinician-only reference support; not patient-facing diagnosis.
- No diagnosis certainty, medication orders, treatment plans, or prescribing instructions.
- No patient data in reviewed catalog payloads.
- No publishable milestone unless validation reports zero blockers and zero warnings.

## Acceptance Checks

- Catalog quality proves at least 450 conditions, at least 528 sources, zero blockers, and zero warnings.
- Search tests prove all 25 new slugs are findable.
- Posted differential results show compact scan density, source counts, and source shortcuts before detailed cards.
- Related catalog, next-action, import-workbench, UI, and dyspnea tests pass.
- Full Django test suite passes.
- Reviewed data validator and static catalog validator both report 450 conditions and 528 sources.
- Reviewed import preview accepts the packaged JSON.
- Public Render smoke confirms the deployed differential page, source shortcut UI, and a new query after push.
