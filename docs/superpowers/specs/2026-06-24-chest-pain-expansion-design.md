# Chest pain expansion design

Add chest pain as the second governed chief complaint so Clinical Differential Support is no longer headache-only.

## Source basis

- NICE CG95: recent-onset chest pain of suspected cardiac origin.
- AHA/ACC 2021 chest pain guideline material.
- ACR Appropriateness Criteria: chest pain, possible acute coronary syndrome.

## Scope

- Add a separate chest pain fixture so the existing headache baseline remains stable.
- Add chest pain sources, clinical items, deterministic rules, and non-patient case scenarios.
- Add a chest pain clinician-reference workspace route at `/chest-pain/`.
- Extend case scenario evaluation so it uses each scenario's chief complaint instead of always using headache.
- Keep all content clinician-only, source-backed, and non-prescriptive.

## Safety

- No patient-identifying data persistence.
- No diagnosis order, treatment order, medication order, dosing, or live clinical deployment approval.
- No trading, broker, Shioaji, order API, or credential behavior.
- Chest pain output is reference support only and must remain under staff content governance.

## Acceptance checks

- Loading `headache_mvp` plus `chest_pain_mvp` creates at least two chief complaints.
- Every approved chest pain item has source links.
- Acute chest pain fixture inputs surface ACS and ECG/troponin workflow prompts.
- Stable exertional fixture inputs surface stable angina pathway prompts.
- Nonischemic high-risk fixture inputs surface life-threatening nonischemic concern.
- Chest pain page is reachable and Chinese-first with English secondary labels.
- Case scenario validation works for chest pain scenarios.
