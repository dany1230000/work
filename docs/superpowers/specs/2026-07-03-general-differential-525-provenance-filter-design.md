# General Differential 525 Provenance Filter Design

## Goal

Move the clinician-only general differential workspace from 500 to 525 reviewed conditions and make source review faster by adding a compact provenance filter before the long candidate cards.

## Data Scope

The sixteenth slice covers currently missing enteric, foodborne, pediatric viral, and parasitic infections:

- Cyclosporiasis, amebiasis, taeniasis, hookworm infection, toxocariasis, lymphatic filariasis, onchocerciasis, cysticercosis, echinococcosis, paragonimiasis, clonorchiasis, fascioliasis, and trichinellosis.
- Campylobacter infection, salmonella infection, shigellosis, listeriosis, cholera, yersiniosis, vibriosis, rotavirus infection, adenovirus infection, fifth disease, scarlet fever, and roseola.

## UX Scope

- Add a `source_provenance` summary to the evaluated result payload.
- Render a source provenance panel between candidate scan and detailed candidate cards.
- Provide publisher filter buttons with stable markers so the clinician can scan linked sources without opening every candidate card.
- Keep the filter presentation-only; it must not change ranking, diagnosis, treatment, or prescribing logic.

## Safety Rules

- Clinician-only reference support.
- Source-backed catalog entries only.
- No diagnosis certainty, treatment orders, medication orders, or patient-facing claims.
- No publish milestone unless validators report zero blockers and zero warnings.

## Acceptance Checks

- Catalog quality reports at least 525 conditions, at least 603 sources, zero blockers, and zero warnings.
- Search tests prove all 25 new slugs are findable.
- Engine tests prove `source_provenance` includes rows, publisher filters, and unique source counts.
- Posted UI shows `data-source-provenance-panel`, filter buttons, source rows, and count before detailed candidate cards.
- Full Django test suite passes.
- Reviewed data validator and static catalog validator both report 525 conditions and 603 sources.
- Public Render smoke confirms 525/603, source provenance markers, and a new query such as `cyclosporiasis`.
