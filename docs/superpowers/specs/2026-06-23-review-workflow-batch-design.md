# Review Workflow Batch Design

## Goal

Extend the reviewer queue into a practical batch workflow for content governance follow-up.

## Scope

This phase adds queue visibility and automatic governance state transitions only. It does not add clinical diagnosis behavior, treatment orders, medication orders, patient data persistence, external execution, or trading behavior.

## User Experience

- Keep `/review/queue/` as the primary reviewer work surface.
- Add a "Changes requested" queue section so reviewers can quickly find items returned for revision.
- Add a "Reviewer notes" section that shows recent review records with reviewer, decision, notes, and linked clinical item.
- When staff edit an already approved clinical item through the existing edit form, automatically move the item back to `In review`.
- Write an audit event when an approved item is edited and resubmitted for review.
- Show the automatic resubmission in queue results and audit trail.

## Data Flow

`build_review_queue()` continues to own read-only queue selection. It will add:

- `changes_requested_items`
- `filtered_changes_requested_items`
- `recent_review_records`

The edit view owns the write workflow: if the item was approved before the edit, the saved item is set to `in_review`, and a `submitted` audit event is created.

## Safety

All behavior remains content governance only. No clinician-facing rule output changes are made by this phase.

## Verification

- Add tests for changes-requested queue selection and rendering.
- Add tests for recent reviewer notes rendering.
- Add tests that editing an approved item automatically changes it to `in_review` and creates a `submitted` audit event.
- Run full Django tests, Django check, safety scan, and live verification.
