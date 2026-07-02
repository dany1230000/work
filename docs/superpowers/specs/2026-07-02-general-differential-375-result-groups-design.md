# General Differential 375 Result Groups Design

## Goal

Advance the clinician-only general differential workspace from 350 to 375 source-backed conditions and make the result page easier to scan by grouping candidates before the long card list.

## Chosen Approach

Use another reviewed 25-condition slice instead of a broad unreviewed import. The static catalog gains a tenth generalist batch, the packaged reviewed JSON is regenerated through the existing import command, and tests advance the governance milestone from 350/429 to 375/453.

For the UI, add a compact candidate grouping panel before result cards. It summarizes emergent, urgent, soon, and routine candidates, then names the leading candidates in each group. This preserves the deterministic evaluator while making the page feel like a step-by-step clinical workbench.

## Data Scope

The tenth generalist slice covers infectious/travel risks, hematology emergencies, chronic liver/GI disease, oncology, mental health, gynecologic/reproductive presentations, dermatology, foot pain, and spine deformity:

- Meningococcal disease, tetanus, rabies, Zika, chikungunya, West Nile virus.
- Aplastic anemia, disseminated intravascular coagulation, TTP, HUS, polycythemia vera, CML.
- Primary biliary cholangitis, primary sclerosing cholangitis, Barrett esophagus, anal cancer.
- Anorexia nervosa, bulimia nervosa, borderline personality disorder.
- Premenstrual syndrome, pelvic organ prolapse, infertility.
- Pemphigus, plantar fasciitis, scoliosis.

Every new condition keeps clinician-facing bilingual wording, source-backed references, non-ordering next-step prompts, searchable English labels or aliases, and no patient data.

## UX Scope

- Add `result.result_groups` from the evaluator so grouping is testable outside the template.
- Render `data-result-groups="true"` before the first result card.
- Show urgency buckets with counts and the leading candidates.
- Keep existing next-step summary strip, patient workflow, guided follow-up, and source links.

## Safety Rules

- Clinician-only reference support; not patient-facing diagnosis.
- No diagnosis certainty, medication orders, treatment plans, or prescribing instructions.
- No patient data in reviewed catalog payloads.
- No publishable milestone unless validation reports zero blockers and zero warnings.

## Acceptance Checks

- Catalog quality proves at least 375 conditions, zero blockers, and zero warnings.
- Search tests prove all 25 new slugs are findable.
- Runtime evaluation exposes grouped candidate buckets ordered by urgency.
- Posted differential results show the result grouping panel before long result cards.
- Related catalog, next-action, import-workbench, UI, and dyspnea tests pass.
- Full Django test suite passes.
- Reviewed data validator and static catalog validator both report 375 conditions and 453 sources.
- Reviewed import preview accepts the packaged JSON.
- Public Render smoke confirms the deployed differential page, grouped result workflow, and one new query after push.
