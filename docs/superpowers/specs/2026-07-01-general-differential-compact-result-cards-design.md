# General Differential Compact Result Cards Design - 2026-07-01

## Goal

Reduce visual length inside the top result cards. Each condition card should
show one primary action first, then keep the full action list available inside a
drawer.

## Scope

- Keep the same ranking and action item data.
- Update only the result card partial and focused UI tests.
- Preserve ask-next and source drawers.

## Success Criteria

- Each result card exposes `data-result-action-compact="true"`.
- The card shows `Primary action`.
- The complete action list is still available in `data-result-actions-detail`.
- Existing ask-next and source detail drawers still render.
