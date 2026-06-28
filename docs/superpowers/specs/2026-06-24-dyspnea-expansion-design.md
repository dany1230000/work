# Dyspnea Expansion Design

Date: 2026-06-24

## Objective

Add dyspnea as the fourth source-backed chief complaint in the Clinical Differential Support MVP.

The module must remain a clinician-only reference workflow. It should help qualified medical professionals see structured next-step prompts and source links, not create diagnoses, treatment orders, medication orders, or patient-specific instructions.

## Source Basis

- ACR Acute Respiratory Illness in Immunocompetent Patients, revised 2024.
- ACR Acute Respiratory Illness in Immunocompromised Patients.
- NICE NG106 Chronic heart failure in adults: diagnosis and management, last updated 2025-09-03.
- NHS England Adult breathlessness pathway, pre-diagnosis support tool for chronic persistent breathlessness.

## Functional Scope

- Add `dyspnea` chief complaint fixture content with approved source-linked clinical items.
- Add deterministic rules for critical dyspnea, acute respiratory illness, immunocompromised respiratory illness, heart-failure suspicion, chronic persistent breathlessness, airflow-obstruction pattern, time-sensitive cardiopulmonary red flags, and structured reassessment.
- Add non-patient fixture cases with expected outputs.
- Add `/dyspnea/` Chinese-first bilingual intake page.
- Extend smoke check and README.
- After dyspnea exists, the Next Action Workbench should move to `coverage-depth-review`, not another complaint module.

## Safety Scope

- No patient-identifying data persistence.
- No diagnosis order, treatment order, procedure order, medication order, dosing, or prescription behavior.
- No trading, broker, Shioaji, real-order, or credential behavior.
- Source-linked prompts must remain conservative and governance-visible.

## Acceptance Checks

- Red test fails before implementation because `evaluate_dyspnea_pathway` or fixture content is missing.
- Dyspnea tests pass after implementation.
- Full Django regression and `manage.py check` pass.
- Local SQLite loads `dyspnea_mvp`.
- Live smoke check passes with `/dyspnea/`.
- Database next action becomes `coverage-depth-review` with first action `run_coverage_depth_review`.
