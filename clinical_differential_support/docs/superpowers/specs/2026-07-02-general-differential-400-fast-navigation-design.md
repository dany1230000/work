# General Differential 400 + Fast Navigation Design

## Goal

Make the clinician-only differential workbench more useful for broad first-pass review by expanding the reviewed catalog from 375 to 400 conditions and by reducing perceived wait during common page switches.

## Scope

- Add 25 source-backed conditions across genetic, endocrine, neurologic, gynecologic, musculoskeletal, hematology, and congenital/pediatric domains.
- Keep every new condition at two sources: one specific public medical source plus the existing Merck Professional umbrella reference.
- Preserve the conservative reference posture: no patient-facing diagnosis, prescribing, or treatment orders.
- Add low-risk fast navigation enhancements: idle prefetch remains, plus hover/focus intent prefetch and a small live status indicator.

## Acceptance

- Static and reviewed runtime catalogs report at least 400 conditions and 478 sources.
- Catalog quality has 0 blocking issues and 0 warnings.
- Every new condition can be surfaced by direct text search.
- Primary navigation still works without JavaScript; enhanced navigation is progressive.
- Fast navigation exposes status and request headers that can be smoke-tested in rendered HTML.
