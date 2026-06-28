# Professional Clinical Differential Support MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local professional clinical decision-support reference MVP for headache, using structured reviewed content and deterministic rules rather than autonomous diagnosis.

**Architecture:** Create a new Django app under `clinical_differential_support/`. Use Django auth/admin for reviewer workflows, SQLite for MVP storage, fixture-based clinical content, and a pure Python rule engine with scenario tests.

**Tech Stack:** Python 3.11+, Django, SQLite, Django templates, Python unittest/Django TestCase, JSON/YAML seed fixtures.

---

## File Structure

Create a new isolated product directory:

- `clinical_differential_support/README.md`: product setup and safety scope.
- `clinical_differential_support/requirements.txt`: Django dependency pin.
- `clinical_differential_support/manage.py`: Django entrypoint.
- `clinical_differential_support/clinical_differential_support/settings.py`: project settings.
- `clinical_differential_support/clinical_differential_support/urls.py`: root URL routing.
- `clinical_differential_support/cds_core/models.py`: knowledge, source, review, and audit models.
- `clinical_differential_support/cds_core/rules.py`: deterministic rule engine.
- `clinical_differential_support/cds_core/services.py`: pathway orchestration service.
- `clinical_differential_support/cds_core/admin.py`: content-review admin.
- `clinical_differential_support/cds_core/views.py`: clinician workflow views.
- `clinical_differential_support/cds_core/urls.py`: app routes.
- `clinical_differential_support/cds_core/forms.py`: structured headache intake form.
- `clinical_differential_support/cds_core/templates/cds_core/base.html`: base layout.
- `clinical_differential_support/cds_core/templates/cds_core/headache.html`: headache workflow UI.
- `clinical_differential_support/cds_core/templates/cds_core/result.html`: result panels.
- `clinical_differential_support/cds_core/fixtures/headache_mvp.json`: seed clinical content.
- `clinical_differential_support/cds_core/tests/test_rules.py`: unit tests for rule output.
- `clinical_differential_support/cds_core/tests/test_pathway.py`: scenario tests.
- `clinical_differential_support/cds_core/tests/test_safety_labels.py`: regression tests for unsafe labels.

## Milestones

### Task 1: Scaffold Django MVP

**Files:**
- Create all project/app boilerplate files listed above.

- [ ] Create a new isolated app directory at `clinical_differential_support/`.
- [ ] Add `requirements.txt` with a reviewed Django version.
- [ ] Create Django project and `cds_core` app.
- [ ] Configure SQLite, templates, static files, timezone, and app registration.
- [ ] Add a README with the exact safety scope:
  - professional use only
  - not a diagnosis
  - not prescribing
  - no real patient data in MVP
- [ ] Run: `py -B -m django --version`
- [ ] Run: `py -B clinical_differential_support/manage.py check`

Expected result: Django project boots and system checks pass.

### Task 2: Define Knowledge Models

**Files:**
- Modify `clinical_differential_support/cds_core/models.py`
- Modify `clinical_differential_support/cds_core/admin.py`
- Test `clinical_differential_support/cds_core/tests/test_models.py`

- [ ] Add `Source` with publisher, title, URL, publication date, access date, version label.
- [ ] Add `ChiefComplaint`.
- [ ] Add `ClinicalItem` with item type, title, summary, urgency, status, and review fields.
- [ ] Add `ClinicalItemSource` for many-to-many source linkage.
- [ ] Add `Rule` with structured JSON conditions and output item.
- [ ] Add `ReviewRecord` with reviewer, decision, notes, and timestamp.
- [ ] Add `AuditEvent` for content changes.
- [ ] Register models in Django admin with filters for status, item type, urgency, and review due date.
- [ ] Write tests confirming draft items are not publishable until approved.
- [ ] Run: `py -B clinical_differential_support/manage.py test cds_core.tests.test_models`

Expected result: data model supports reviewed, source-backed clinical content.

### Task 3: Build Deterministic Rule Engine

**Files:**
- Modify `clinical_differential_support/cds_core/rules.py`
- Test `clinical_differential_support/cds_core/tests/test_rules.py`

- [ ] Implement a `FindingSet` value object from structured intake data.
- [ ] Implement rule condition operators:
  - `equals`
  - `in`
  - `present`
  - `absent`
  - `gte`
  - `lte`
  - `any`
  - `all`
- [ ] Implement `evaluate_rules(finding_set, rules)` returning matched outputs with explanations.
- [ ] Ensure explanations include matched clauses and source IDs.
- [ ] Write tests for thunderclap, fever/meningism, medication-overuse, migraine features, and no-match.
- [ ] Run: `py -B clinical_differential_support/manage.py test cds_core.tests.test_rules`

Expected result: fixed input findings produce deterministic, explainable outputs.

### Task 4: Seed Headache MVP Content

**Files:**
- Create `clinical_differential_support/cds_core/fixtures/headache_mvp.json`
- Test `clinical_differential_support/cds_core/tests/test_seed_content.py`

- [ ] Add sources for NICE CG150, ACR Headache Appropriateness Criteria, ICHD-3, FDA CDS guidance, and IMDRF SaMD clinical evaluation.
- [ ] Add headache chief complaint.
- [ ] Add red-flag items:
  - sudden onset reaching maximum intensity quickly
  - fever/meningism
  - new neurologic deficit
  - altered mental status
  - recent trauma
  - immunocompromised status
  - malignancy history
  - symptoms suggestive of giant cell arteritis
  - symptoms/signs suggestive of acute narrow-angle glaucoma
- [ ] Add differential considerations:
  - migraine
  - migraine with aura
  - tension-type headache
  - cluster headache
  - medication-overuse headache
  - SAH concern
  - meningitis/encephalitis concern
  - raised intracranial pressure/mass concern
- [ ] Add management notes with source-backed caution wording, not dosing/order language.
- [ ] Add fixture load command to README.
- [ ] Run: `py -B clinical_differential_support/manage.py loaddata headache_mvp`

Expected result: seed content loads and all published clinician-facing items are source-linked.

### Task 5: Build Clinician Headache Workflow

**Files:**
- Modify `clinical_differential_support/cds_core/forms.py`
- Modify `clinical_differential_support/cds_core/views.py`
- Modify templates under `clinical_differential_support/cds_core/templates/cds_core/`
- Test `clinical_differential_support/cds_core/tests/test_pathway.py`

- [ ] Build structured headache intake form.
- [ ] Avoid free-text patient identifiers in MVP; if free-text notes exist, show a warning.
- [ ] Show red flags first.
- [ ] Show differential considerations as "consider in differential", not "diagnosis".
- [ ] Show missing questions.
- [ ] Show source links, review status, and last reviewed date for each item.
- [ ] Show safety banner on every page.
- [ ] Add scenario tests for at least 8 headache cases.
- [ ] Run: `py -B clinical_differential_support/manage.py test cds_core.tests.test_pathway`

Expected result: clinician can complete a headache case and see source-backed, safety-labeled outputs.

### Task 6: Add Review and Audit Workflow

**Files:**
- Modify `clinical_differential_support/cds_core/admin.py`
- Modify `clinical_differential_support/cds_core/models.py`
- Test `clinical_differential_support/cds_core/tests/test_review_workflow.py`

- [ ] Add admin actions for submit for review, approve, request changes, retire.
- [ ] Prevent unapproved items from appearing in clinician workflow.
- [ ] Record review decisions.
- [ ] Record audit events for content status changes.
- [ ] Add tests for draft exclusion and retired exclusion.
- [ ] Run: `py -B clinical_differential_support/manage.py test cds_core.tests.test_review_workflow`

Expected result: only reviewed approved content can reach clinician workflow.

### Task 7: Safety and Label Regression Tests

**Files:**
- Create `clinical_differential_support/cds_core/tests/test_safety_labels.py`

- [ ] Assert clinician-facing pages include professional-use-only language.
- [ ] Assert pages do not include unsafe labels:
  - final diagnosis
  - prescribe
  - order medication
  - patient instruction
  - AI diagnosis
- [ ] Assert red flags sort before routine differential content.
- [ ] Assert unsupported cases show "not covered in this MVP" rather than invented recommendations.
- [ ] Run: `py -B clinical_differential_support/manage.py test cds_core.tests.test_safety_labels`

Expected result: unsafe positioning is guarded by tests.

### Task 8: End-to-End Verification

**Files:**
- Modify `clinical_differential_support/README.md`

- [ ] Run full tests: `py -B clinical_differential_support/manage.py test`
- [ ] Run Django check: `py -B clinical_differential_support/manage.py check --deploy`
- [ ] Prepare local database: `py -B clinical_differential_support/manage.py migrate --run-syncdb`
- [ ] Load seed content: `py -B clinical_differential_support/manage.py loaddata headache_mvp`
- [ ] Manually run local server: `py -B clinical_differential_support/manage.py runserver 127.0.0.1:8000`
- [ ] Verify headache workflow in browser.
- [ ] Document known limitations:
  - MVP is not production clinical software.
  - Requires clinician review and regulatory/legal/privacy review before real use.
  - Taiwan-local sources must be added before Taiwan production claims.

Expected result: MVP is locally runnable, tested, and clearly bounded.

## Acceptance Criteria

- The app is isolated under `clinical_differential_support/`.
- No `tw_quant_v2` or `shop_report_lite` files are modified.
- Headache MVP has structured intake, red flags, differential considerations, workup prompts, management notes, and source display.
- Every clinician-facing item has source and review metadata.
- At least 8 scenario tests pass.
- The UI never presents outputs as final diagnosis, automatic prescribing, or patient advice.
- README explains the safety and regulatory boundary.
