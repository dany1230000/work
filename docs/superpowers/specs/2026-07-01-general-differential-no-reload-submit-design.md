# General Differential No-Reload Submit Design

## Goal

Make the public general differential workspace feel faster by submitting the case form without a full page reload, while preserving the existing Django POST path as the fallback.

## Chosen Approach

Keep the same server-rendered view and add progressive enhancement in the shared base script. The browser submits the existing form with `fetch`, parses the returned HTML, and replaces only the workflow stepper, selected findings summary, and results panel.

This avoids a second API contract and keeps CSRF, form validation, source rendering, and non-JavaScript behavior on the existing path.

## UX Behavior

- The page stays on `/differential/` during submit.
- The output panel updates inline after evaluation.
- A short inline status appears while the request is pending.
- If JavaScript, fetch, or the partial replacement fails, the form falls back to normal full-page POST.

## Safety Rules

- Do not change clinical ranking logic in this phase.
- Do not expose patient data through new JSON endpoints.
- Do not remove the clinician-only safety copy or source links.
- Keep the feature additive: no-JavaScript users must still get the same server-rendered result page.

## Acceptance Checks

- Django UI tests assert no-reload markers and replacement sections exist on GET and POST responses.
- Existing general differential UI tests still pass.
- Browser verification confirms submit keeps the same URL, preserves a JavaScript marker across submit, and updates the result panel with Pertussis and CDC source content.
- Full Django suite passes before commit.
