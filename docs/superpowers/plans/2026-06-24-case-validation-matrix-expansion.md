# Case Validation Matrix Expansion Plan

Date: 2026-06-24

## Steps

1. Update tests to expect no `case_depth_gap` after case matrix expansion.
2. Add one source-backed, non-patient chest-pain validation scenario for low-to-intermediate ACS imaging/shared decision workflow.
3. Run targeted chest-pain and coverage-depth tests.
4. Run full regression, Django check, live smoke, and coverage-depth report verification.

## Verification Commands

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_chest_pain_pathway cds_core.tests.test_coverage_depth -v 2
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
py -B .\clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```
