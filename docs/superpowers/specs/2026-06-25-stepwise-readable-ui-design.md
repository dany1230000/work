# Stepwise Readable UI Design

## Goal

Make the smoke-covered user-facing pages tell the user what to do next on the page itself, not only in Markdown or CLI output.

## Scope

- Public symptom pages: headache, chest pain, abdominal pain, dyspnea.
- Public reviewer entry pages: reviewer login and reviewer queue.
- Final verification metadata affected by the new regression tests.

## Design

Each symptom page shows a three-step workflow before the intake form:

1. Enter structured findings.
2. Run the reference pathway.
3. Review ask-next prompts, why-shown text, and sources.

The reviewer login page shows a three-step staff access flow:

1. Enter staff credentials.
2. Open the reviewer queue.
3. Handle source gaps first.

The reviewer queue page shows a prioritized review flow:

1. Resolve source gaps first.
2. Review due items.
3. Open the item and record a decision.

The UI remains Chinese-first with English secondary labels. It does not add clinical recommendations, diagnosis orders, treatment orders, medication orders, patient data storage, credentials, or external integrations.

## Verification

Add a regression test that renders the smoke-covered pages and asserts:

- required workflow labels are present;
- legacy mixed Chinese/English wording in user-facing empty states is absent;
- common mojibake replacement markers are absent.

Then run targeted UI tests, full Django tests, Django check, live smoke, direct HTML checks, and final verification evidence recording.
