# General Differential Results Brief Design - 2026-07-01

## Goal

Make the broad differential result page easier to scan after catalog expansion.
The user should see the next clinical workflow step, the leading candidate, and
how much of the result set is hidden before reading individual condition cards.

## Scope

- Add a compact `results_brief` object to the general differential evaluator.
- Render a short results brief above the action queue and result cards.
- Keep the existing top 3 cards and secondary drawer behavior.
- Keep the page clinician-only in wording: reference support, not diagnosis,
  treatment, medication, or disposition order.

## Non-goals

- No new clinical scoring model.
- No new disease catalog entries in this phase.
- No patient-facing language.
- No JavaScript-heavy interaction or new dependency.

## Success Criteria

- Posted results include `data-results-brief="true"` before the action queue.
- Brief displays top candidate, urgency, top-card count, hidden candidate count,
  and next safest action.
- Existing result cards, action checklist, guided follow-up, and secondary drawer
  still pass regression tests.
