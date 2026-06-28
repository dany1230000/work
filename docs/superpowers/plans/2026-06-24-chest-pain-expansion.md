# Chest pain expansion implementation plan

**Goal:** Make the product no longer headache-only by adding a governed chest pain module with source-backed content, route, tests, and scenario validation.

## RED

- Add `cds_core.tests.test_chest_pain_pathway`.
- Tests load both `headache_mvp.json` and `chest_pain_mvp.json`.
- Assert chest pain chief complaint, sources, approved items, rules, and cases exist.
- Assert `evaluate_chest_pain_pathway()` produces ACS, ECG/troponin, stable angina, and nonischemic high-risk prompts.
- Assert `/chest-pain/` renders and evaluates.
- Assert `evaluate_case_scenario()` respects a chest pain scenario.

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_chest_pain_pathway -v 2
```

Expected: fail before implementation because the fixture, form, route, and evaluator do not exist.

## GREEN

- Add `ChestPainIntakeForm`.
- Add generic pathway evaluator plus `evaluate_chest_pain_pathway()`.
- Add chest pain route, view, nav link, and template.
- Add `chest_pain_mvp.json`.
- Update next-action selector so once chest pain exists it points to the next expansion target.
- Update setup docs to load both fixtures.

## VERIFY

Run targeted tests, full Django tests, Django check, smoke check after server restart, and a local fixture load into the current dev database.
