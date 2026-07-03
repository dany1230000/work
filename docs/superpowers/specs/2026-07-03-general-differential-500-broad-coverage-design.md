# General Differential 500 Broad Coverage Design

## Goal

Move the clinician-only general differential workspace from 475 to 500 reviewed conditions without adding diagnosis, treatment, medication, or patient-facing logic.

## Data Scope

The fifteenth slice covers missing high-yield gaps across fungal, opportunistic, zoonotic, tickborne, waterborne, and electrolyte disease:

- Blastomycosis, cryptococcosis, aspergillosis, invasive candidiasis, pneumocystis pneumonia, nontuberculous mycobacterial lung disease, hypokalemia, and botulism.
- Plague, anthrax, brucellosis, leptospirosis, hantavirus pulmonary syndrome, ehrlichiosis, anaplasmosis, babesiosis, tularemia, Q fever, psittacosis, Legionnaires' disease, nocardiosis, mucormycosis, leprosy, cytomegalovirus infection, and cryptosporidiosis.

## Safety Rules

- Clinician-only reference support.
- Source-backed catalog entries only.
- No diagnosis certainty or treatment/prescribing instructions.
- No publish milestone unless validators report zero blockers and zero warnings.

## Acceptance Checks

- Catalog quality reports at least 500 conditions, at least 578 sources, zero blockers, and zero warnings.
- Search tests prove all 25 new slugs are findable.
- Full Django test suite passes.
- Reviewed data validator and static catalog validator both report 500 conditions and 578 sources.
- Public Render smoke confirms 500/578 and a new query such as `blastomycosis`.
