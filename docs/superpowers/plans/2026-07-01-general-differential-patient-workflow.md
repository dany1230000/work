# General Differential Patient Workflow Plan

## Objective

讓通用鑑別診斷結果變成可一步一步執行的臨床參考流程，避免使用者直接面對過長候選清單。

## Implementation

- Add evaluator tests for `patient_workflow`.
- Build workflow metadata from the existing ranked results and guided follow-up.
- Render a compact workflow panel before results cards.
- Include a bilingual handoff summary for the current case.
- Preserve source-backed conservative reference wording.

## Verification

- Targeted workflow evaluator and UI tests.
- General differential evaluator and UI suites.
- Full Django test suite.
- General catalog validator.
- Local POST smoke for workflow markers.
- Public POST smoke after push/deploy.
