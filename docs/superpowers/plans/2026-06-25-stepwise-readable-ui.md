# Stepwise Readable UI Implementation Plan

## Steps

1. Add failing UI tests for the missing three-step workflows.
2. Add a shared symptom workflow include and responsive CSS.
3. Update headache, chest pain, abdominal pain, and dyspnea pages to render the workflow and use consistent Chinese-first titles.
4. Update reviewer login and reviewer queue with staff review workflows.
5. Clean mixed Chinese/English spacing in safety copy and success/error messages.
6. Update final verification expected regression count after the new tests.
7. Run full verification and record final evidence.

## Verification Commands

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_stepwise_ui -v 2
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
git diff --check -- clinical_differential_support docs .planning
py -B .\clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
py -B .\clinical_differential_support\scripts\record_final_verification_evidence.py --overwrite
```
