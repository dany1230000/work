# General Differential Workbench Design

## Goal

Build a Chinese-first, English-supported general differential workbench that helps clinicians decide the next question and must-not-miss conditions across body systems. This is a starter catalog and workflow, not a claim that every disease is fully covered.

## Scope

- Add `/differential/` as the first general entry point from the dashboard.
- Let clinicians select structured findings and optionally type a disease or complaint search term.
- Rank candidate conditions by urgency, matched findings, and text search.
- Show matched findings, ask-next prompts, coverage status, and source links.
- Keep safety boundaries: clinician-only reference support, no patient identifiers, no diagnosis/treatment/orders.

## Architecture

- `cds_core/differential_catalog.py` owns the starter finding groups, source references, and condition catalog.
- `cds_core/general_differential.py` evaluates selected findings against the catalog and returns display-ready results.
- `GeneralDifferentialForm` collects a free-text query, structured findings, and non-identifying notes.
- `general_differential_workspace` renders a 4-step workflow and results.

## Data Boundary

This stage uses a versioned Python catalog so the workflow can ship quickly without database migration risk. The next stage should promote this catalog into governed database tables with staff review, source freshness checks, and CSV export.

## Success Criteria

- Clinicians can open a general differential page from the dashboard.
- Selecting chest pain, dyspnea, diaphoresis, and arm/jaw radiation returns acute coronary syndrome near the top with emergency urgency and source links.
- Selecting fever, confusion, tachycardia, and dyspnea returns sepsis near the top with emergency urgency and source links.
- Unknown or sparse presentations show explicit starter-catalog coverage limits and ask-next prompts.
- Full regression passes before publishing.
