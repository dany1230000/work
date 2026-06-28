# Abdominal pain expansion design

Add abdominal pain as the third governed chief complaint so Clinical Differential Support can continue beyond headache and chest pain.

## Source basis

- ACR Appropriateness Criteria: Acute Nonlocalized Abdominal Pain.
- ACR Appropriateness Criteria: Right Lower Quadrant Pain, Suspected Appendicitis.
- ACR Appropriateness Criteria: Right Upper Quadrant Pain.
- NICE NG126: Ectopic pregnancy and miscarriage, diagnosis and initial management.
- WSES/JAMA Surgery 2025 appendicitis guideline metadata for appendicitis governance context.

## Scope

- Add a separate `abdominal_pain_mvp.json` fixture.
- Add abdominal pain sources, approved clinical items, source links, deterministic rules, and non-patient case scenarios.
- Add an abdominal pain clinician-reference route at `/abdominal-pain/`.
- Add `evaluate_abdominal_pain_pathway()` as a thin wrapper over the generic pathway evaluator.
- Keep the next-action workbench dynamic so completing abdominal pain advances the next target to dyspnea.

## Safety

- Clinician-reference support only.
- No autonomous diagnosis, treatment order, procedure order, medication order, dosing, patient-identifying persistence, credentials, trading behavior, broker behavior, or Shioaji behavior.
- The module surfaces prompts for structured assessment and source-backed governance review; it does not tell clinicians what treatment to perform.

## Acceptance checks

- Loading headache, chest pain, and abdominal pain fixtures creates three chief complaints.
- Every approved abdominal pain item has source links.
- Generalized abdominal pain with fever surfaces an acute nonlocalized abdominal pain workflow prompt.
- RLQ pain with fever/leukocytosis surfaces an appendicitis pathway prompt.
- RUQ pain with biliary features surfaces a biliary/RUQ pathway prompt.
- Early-pregnancy-compatible abdominal pain or bleeding surfaces an ectopic pregnancy safety prompt.
- `/abdominal-pain/` renders Chinese-first with English secondary labels and evaluates fixture inputs.
- The next-action workbench advances from abdominal pain to dyspnea after the fixture exists.
