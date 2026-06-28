# Reviewer Queue Design

## Goal

Build a Chinese-first, English-supported reviewer queue for the clinical differential support MVP so reviewers can quickly find content that needs governance attention.

## Scope

The queue is reviewer-facing and read-only. It does not change clinical rule behavior, diagnosis output, treatment guidance, medication behavior, patient data handling, or any trading-related behavior.

## User Experience

- Add a reviewer queue at `/review/queue/`.
- Link to it from the clinical governance dashboard.
- Show a compact summary for:
  - source gaps
  - review due
  - draft items
  - in-review items
  - currently visible results
- Provide filters using query string parameters:
  - `status`
  - `urgency`
  - `q`
- Results show the item title, secondary English title, status, urgency, source count, last reviewed date, review due date, and flags.
- Each row links to the existing clinical item review detail page.

## Data Flow

`cds_core.governance.build_review_queue()` receives optional filters and returns a plain dictionary for the template. The view reads query parameters, passes them to the selector, and renders `review_queue.html`.

## Safety

This phase remains content governance only. It adds no patient-identifying data persistence, no diagnosis order, no treatment order, no medication order, and no live execution behavior.

## Verification

- Add tests for selector baseline queue counts.
- Add tests for route rendering and governance-dashboard linking.
- Add tests for status, urgency, and text search filters.
- Run the full Django test suite, Django system check, safety keyword scan, and live HTTP verification after implementation.
