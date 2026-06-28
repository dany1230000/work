# Dyspnea Expansion Plan

Date: 2026-06-24

## Steps

1. Add failing tests for dyspnea fixture content, pathway evaluation, page rendering, case scenarios, and next-action advancement.
2. Add `evaluate_dyspnea_pathway()`.
3. Add `DyspneaIntakeForm`, `/dyspnea/`, navigation, and `dyspnea.html`.
4. Add `dyspnea_mvp.json` with source metadata, clinical items, source links, rules, and non-patient cases.
5. Improve coverage-depth next-action handling after all configured expansion targets exist.
6. Extend smoke coverage and README setup/routes.
7. Run targeted dyspnea tests, next-action tests, operational readiness tests, full regression, Django check, fixture load, server restart, live smoke, and database next-action verification.

## Verification Commands

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_dyspnea_pathway -v 2
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_next_actions -v 2
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_operational_readiness -v 2
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
py -B .\clinical_differential_support\manage.py loaddata dyspnea_mvp
py -B .\clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```
