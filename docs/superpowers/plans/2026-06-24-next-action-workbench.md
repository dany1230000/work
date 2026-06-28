# Next action workbench implementation plan

**Goal:** Add a staff-only next-action workbench that tells the owner what to do next and prevents the headache-only MVP from being mistaken for final multi-complaint coverage.

**Architecture:** Add one selector module, one template, two staff-only routes, and focused tests. The selector reads existing `ChiefComplaint`, `ClinicalItem`, and `CaseScenario` data and returns summary-only action metadata.

## RED

- Create `cds_core.tests.test_next_actions`.
- Assert the selector marks headache-only coverage as `not_final_beyond_headache`.
- Assert the first next action is adding the chest pain module.
- Assert `/review/next-actions/` and `/review/exports/next-actions.json` are staff-only.
- Assert the JSON export omits detailed fixture clinical text.
- Assert dashboard/readiness pages link to the workbench.

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_next_actions -v 2
```

Expected: fail before implementation because the selector and routes do not exist.

## GREEN

- Create `cds_core/next_actions.py` with `build_next_action_plan(today=None)`.
- Add `next_actions` and `export_next_actions_json` views.
- Add URL patterns.
- Add `next_actions.html`.
- Add links from `review_dashboard.html` and `release_readiness.html`.
- Add route to README.

## VERIFY

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_next_actions -v 2
py -B clinical_differential_support\manage.py test -v 2
py -B clinical_differential_support\manage.py check
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Restart the local server before live checks if routes or templates changed.
