# General Differential Patient Workflow Design

## Goal

把通用鑑別診斷頁從「候選清單」推進成「逐步病人流程」。臨床使用者輸入主訴、free-text 或 structured findings 後，頁面要先告訴下一步怎麼走，再顯示完整候選清單。

## Scope

- Keep the existing ranked reference evaluator intact.
- Add a `patient_workflow` wrapper around the result payload.
- Render a scan-first panel before the long candidate cards.
- Keep clinician-only, source-backed, conservative wording.
- Avoid diagnosis, treatment, medication, or order language.

## Workflow Steps

1. 先排除立即危險 / Rule out immediate danger.
2. 補齊缺少脈絡 / Complete missing context.
3. 比較前三個候選 / Compare leading candidates.
4. 交接或重跑 / Handoff or re-run.

## Acceptance Checks

- Evaluator returns stable `patient_workflow` data for ranked cases.
- UI renders `data-patient-workflow="true"` before long result cards.
- Handoff summary names leading reference candidates without patient identifiers.
- Existing guided follow-up, compact cards, source drawers, and catalog governance remain unchanged.
