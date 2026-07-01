# Plan - General Differential Results Brief

1. Add evaluator tests for `results_brief`.
2. Add UI tests for the brief placement and data attributes.
3. Implement `_build_results_brief()` in `general_differential.py`.
4. Render the brief in `general_differential.html` above the action queue.
5. Run targeted tests, full regression, catalog validator, local smoke, public
   smoke, then commit and push.

## Verification Commands

```powershell
py -B manage.py test cds_core.tests.test_general_differential cds_core.tests.test_general_differential_ui -v 2
py -B manage.py test -v 2
py -B manage.py validate_general_differential_catalog
```
