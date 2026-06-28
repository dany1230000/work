# Coverage Depth Review Plan

Date: 2026-06-24

## Steps

1. Add failing tests for selector output, staff route protection, JSON export, and links.
2. Implement `cds_core.coverage_depth.build_coverage_depth_report()`.
3. Add staff-only page and JSON export views/routes.
4. Add `coverage_depth.html` and links from governance, release readiness, and next-action workbench.
5. Extend smoke check and operational readiness tests.
6. Run targeted tests, full regression, Django check, live smoke, and DB state verification.

## Verification Commands

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_coverage_depth -v 2
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_operational_readiness -v 2
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
py -B .\clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```
