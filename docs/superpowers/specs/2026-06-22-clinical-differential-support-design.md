# Professional Clinical Differential Support Design

Date: 2026-06-22

## Product Goal

Build a professional clinical decision-support reference tool for qualified health care professionals. The product helps clinicians move from a chief complaint to red flags, structured history prompts, differential diagnoses, workup considerations, management pathways, medication-safety reminders, and source-backed references.

The first MVP should focus on headache. This is narrow enough to validate the product model while still showing professional depth: urgent secondary causes, primary headache classification, imaging/referral criteria, medication-overuse risk, acute treatment considerations, and evidence traceability.

## Positioning

The product must be positioned as:

- A clinician reference and teaching support tool.
- A structured pathway and knowledge-base system.
- A way to surface questions, red flags, differential considerations, and source-backed next steps.

The product must not be positioned as:

- A patient symptom checker.
- An autonomous diagnostic system.
- An automatic prescription or order-entry system.
- A replacement for clinician judgment.
- A tool ready for real clinical deployment before regulatory, legal, clinical, privacy, and security review.

## Regulatory and Safety Baseline

The planning baseline is deliberately conservative:

- FDA CDS guidance says non-device CDS criteria include use by health care professionals, recommendations that the professional can independently review, and enough basis shown so the professional is not expected to rely primarily on the software.
- FDA guidance also distinguishes text/medical-information CDS from software that acquires, processes, or analyzes medical images, signals, or patterns. The MVP should not process imaging, ECG, lab instrument signals, continuous monitoring streams, or uploaded medical images.
- Taiwan TFDA has guidance for AI/ML medical-device software registration preparation. Because this product could become regulated depending on claims and implementation, production release requires Taiwan regulatory review.
- IMDRF SaMD clinical evaluation uses valid clinical association, analytical validation, and clinical validation as core concepts. The MVP should collect evidence and test artifacts in a way that can later support those questions.
- WHO AI-for-health guidance emphasizes ethics, accountability, transparency, and responsiveness to health workers and affected communities.

Primary sources reviewed:

- Taiwan TFDA AI/ML medical-device software guidance announcement: https://www.fda.gov.tw/tc/siteListContent.aspx?id=34961&sid=3787
- FDA Clinical Decision Support Software guidance, document issued 2026-01-29: https://www.fda.gov/media/109618/download
- FDA AI in Software as a Medical Device page: https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-software-medical-device
- IMDRF SaMD Clinical Evaluation: https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation
- WHO Ethics and Governance of AI for Health: https://www.who.int/publications/i/item/9789240029200

## Approach Options

### Option 1: Structured Knowledge Base and Rule Engine

This approach stores clinical content as structured, reviewed records: questions, red flags, diagnostic criteria, supporting findings, opposing findings, workup prompts, management notes, medication safety warnings, and source citations. A deterministic rule engine maps clinician-entered findings to ranked prompts and differential considerations.

Pros:

- Strongest fit for professional safety and auditability.
- Every output can show why it appeared and which source supports it.
- Easier to review by clinicians and update over time.
- Easier to test with fixed cases.

Cons:

- Slower content authoring.
- Less flexible than free-form AI.
- Needs careful knowledge-model design.

### Option 2: AI-First Clinical Assistant with Retrieval

This approach uses a language model as the primary interface. It retrieves guideline snippets and generates conversational clinical suggestions.

Pros:

- Fast prototype.
- Natural interaction.
- Can summarize long sources well.

Cons:

- Harder to guarantee deterministic behavior.
- Higher hallucination and traceability risk.
- Harder to validate as a professional clinical tool.
- More likely to drift into autonomous diagnosis wording.

### Option 3: Hybrid Reference System

This approach uses a structured knowledge base and rule engine for clinical outputs, with AI limited to non-authoritative support such as searching content, summarizing source passages for editors, drafting content for review, and translating reviewed content. The clinician-facing diagnostic pathway remains deterministic and source-linked.

Pros:

- Keeps the clinical output auditable.
- Allows professional workflow and faster editorial work.
- Can add AI features later without making AI the decision engine.

Cons:

- More architecture than a pure prototype.
- Requires explicit UI labeling so generated/editorial drafts never look approved.

## Recommended Approach

Use Option 3: hybrid reference system with a structured clinical core.

The MVP should not make AI the clinical decision engine. The professional value should come from content quality, review workflow, source traceability, and a fast clinician-facing interface. AI can be added later as an editor assistant or internal search/summarization aid, but the first shipped clinical recommendations should be deterministic and reviewable.

## MVP Scope

### Included

- Clinician-only web app.
- Headache chief-complaint workflow.
- Structured intake:
  - age band
  - pregnancy/postpartum status
  - immunocompromised status
  - malignancy history
  - onset timing
  - thunderclap pattern
  - fever/meningism
  - neurological deficit
  - altered mental status
  - trauma
  - exertional/cough/valsalva trigger
  - orthostatic pattern
  - visual symptoms
  - eye pain/redness
  - medication use frequency
  - prior headache history
- Red-flag panel with urgent referral/workup prompts.
- Differential panel:
  - migraine with and without aura
  - tension-type headache
  - cluster headache
  - medication-overuse headache
  - subarachnoid hemorrhage concern
  - meningitis/encephalitis concern
  - intracranial mass or raised intracranial pressure concern
  - giant cell arteritis concern
  - acute angle-closure glaucoma concern
  - post-traumatic headache concern
- Workup panel:
  - referral triggers
  - imaging appropriateness references
  - lab prompts where source-backed
- Management notes:
  - high-level acute treatment options
  - medication-overuse warning
  - contraindication prompts
  - no automatic prescriptions
- Source and version display on every clinical item.
- Admin/reviewer workflow:
  - draft content
  - clinical review
  - approval
  - published version
  - retire/deprecate
- Audit log for content changes.
- Test cases for canonical clinical scenarios.

### Excluded from MVP

- Patient-facing access.
- Uploading or analyzing images.
- EHR/FHIR integration.
- Real patient record storage.
- Automatic diagnosis labels such as "final diagnosis".
- Automatic medication ordering or dosing engine.
- Real-time monitoring or signal analysis.
- Production clinical deployment.

## Core User Workflows

### Clinician Pathway Use

1. Clinician selects chief complaint: headache.
2. System shows a structured intake form.
3. Clinician enters known findings.
4. System immediately displays triggered red flags.
5. System shows differential considerations grouped by urgency and source strength.
6. Clinician opens each item to see supporting findings, opposing findings, missing questions, source citations, and last reviewed date.
7. Clinician can export or copy a reference summary that clearly states it is not a diagnosis and must be interpreted by the clinician.

### Clinical Content Review

1. Editor creates or updates a clinical item.
2. Item remains draft and cannot appear in clinician workflow.
3. Clinical reviewer checks source, wording, risk level, and contraindication logic.
4. Reviewer approves a new version.
5. Published workflow only uses approved versions.
6. Audit log records who changed what and why.

### Source Refresh

1. Maintainer records source URL, publisher, publication/update date, access date, and affected clinical items.
2. System marks affected clinical items as "review due".
3. Reviewer updates or confirms content.
4. Old versions remain viewable for audit.

## Information Architecture

Primary clinician screens:

- Dashboard: chief complaints and content status warnings.
- Headache workspace: intake, red flags, differentials, workup, management, sources.
- Clinical item detail: why shown, source basis, review status, missing questions.
- Case simulation mode: predefined cases for training and validation.

Admin/reviewer screens:

- Content library.
- Source library.
- Review queue.
- Version diff.
- Audit log.
- Test-case library.

## Clinical Knowledge Model

The knowledge model should be structured around versioned clinical entities:

- `ChiefComplaint`
- `Question`
- `Finding`
- `RedFlag`
- `DiagnosisConsideration`
- `Rule`
- `WorkupRecommendation`
- `ManagementNote`
- `MedicationSafetyNote`
- `Source`
- `ClinicalItemVersion`
- `ReviewRecord`
- `CaseFixture`

Each clinician-facing item must carry:

- title
- plain-language clinician summary
- severity/urgency category
- supporting findings
- opposing findings
- missing questions
- trigger rules
- source IDs
- review status
- last reviewed date
- content owner/reviewer

## Rule Engine Design

The MVP rule engine should be deterministic and explainable:

- Inputs: structured findings from the clinician intake form.
- Outputs: triggered red flags, ranked differential considerations, missing-question prompts, workup prompts, and medication-safety notes.
- Explanation: each output shows matching rule clauses and source references.

Rule scoring should be conservative:

- Red flags override ranking and appear at top.
- Differential scores are "consideration strength", not probability.
- The UI should avoid implying a final diagnosis.
- Unsupported findings should produce "insufficient information" rather than hallucinated advice.

Example output labels:

- "Urgent red flag triggered"
- "Consider in differential"
- "Ask next"
- "Review source"
- "Safety check"

Avoid labels:

- "Diagnosis"
- "Treatment order"
- "Patient instruction"
- "AI conclusion"

## Content Source Strategy for Headache MVP

Initial source candidates:

- NICE CG150 for headache assessment, diagnosis, diary, medication-overuse risk, and treatment considerations.
- ACR Appropriateness Criteria Headache for imaging decision support references.
- ICHD-3 for headache classification and diagnostic criteria.
- Taiwan-local clinical guidelines or society references should be added before Taiwan production use.

Each clinical content item should list whether it is:

- `source_backed`
- `local_adapted`
- `expert_reviewed`
- `needs_local_review`
- `retired`

## Safety UX Requirements

Every clinician-facing screen should include concise safety framing:

- "For qualified medical professionals."
- "Reference support only; not a diagnosis or treatment order."
- "Review basis and sources before applying to a patient."

The product should block or redirect unsafe use:

- If a user enters patient-identifying data in free text, warn and discourage it during MVP.
- If a user asks for patient-facing instructions, show a professional-use boundary.
- If no rule/source supports an answer, show "not covered in this MVP".
- If a red flag is triggered, show urgent escalation prompts before routine differential content.

## Architecture

Recommended MVP architecture:

- Backend: Python 3.11+ with Django.
- Database: SQLite for local MVP; PostgreSQL for production.
- Frontend: Django templates with restrained, professional UI. Add HTMX only if needed later.
- Knowledge model: relational tables plus JSON rule clauses for flexibility.
- Rule engine: pure Python service module with test fixtures.
- Content seed data: YAML or JSON fixtures imported into the database.
- Audit: database audit records for content/version changes.
- Tests: Django unit tests for models/rules plus scenario tests for headache cases.

Why Django:

- Built-in admin accelerates reviewer/content workflows.
- Built-in auth supports clinician/admin separation.
- ORM and migrations are mature.
- Server-rendered UI avoids early npm/tooling complexity.
- Python is already natural in this workspace.

## Validation Strategy

The MVP should validate four things:

1. Usability: a clinician can complete a headache pathway quickly.
2. Safety: red flags are never hidden behind routine diagnosis suggestions.
3. Traceability: every clinical output shows source and review status.
4. Determinism: fixed case fixtures produce expected outputs.

Test case categories:

- Thunderclap headache.
- Headache with fever and meningism.
- Migraine with typical aura.
- Atypical aura with motor weakness.
- Medication-overuse pattern.
- New headache with malignancy history.
- Cluster-like unilateral orbital pain with autonomic features.
- Routine tension-type headache without red flags.

## Risks and Controls

| Risk | Control |
|------|---------|
| Users interpret rankings as final diagnoses | Use "consideration" labels, explanation panels, and no final diagnosis banner |
| AI hallucination enters clinical output | Keep AI out of published clinical pathway; require clinical review for any AI-drafted content |
| Outdated guideline content | Store source version, access date, review due date, and content status |
| Medication advice becomes unsafe | Use high-level safety notes only in MVP; no dosing/order engine |
| Product becomes regulated without preparation | Maintain SaMD/CDS traceability, validation artifacts, and require regulatory review before production use |
| Patient data exposure | No real patient data in MVP; no EHR integration; warn against identifiers |

## Success Criteria

The MVP planning target is met when:

- A clinician can run through a headache case and see red flags, differential considerations, workup prompts, management notes, and sources.
- Each output has a transparent basis and review status.
- At least 8 scenario tests pass.
- The product does not claim autonomous diagnosis, patient advice, or prescribing.
- The content workflow supports draft, review, approval, versioning, and audit.
