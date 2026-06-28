# Final Verification Evidence Recorder Design

Date: 2026-06-24

## Objective

Add a local evidence recorder for the Final Verification Gate.

The existing Final Verification Gate lists the required commands, but it does not persist evidence that the commands were actually run. The next step is to add a local script that runs the required verification commands, records summary-only results, and writes a JSON artifact that the staff-only gate can read.

## Scope

- Add `clinical_differential_support/scripts/record_final_verification_evidence.py`.
- Write summary-only evidence to `clinical_differential_support/verification_artifacts/final-verification-evidence.json` by default.
- Add a latest-evidence reader to the Final Verification Gate selector.
- Show latest evidence status on `/review/final-verification/`.
- Keep the JSON summary-only: no full command output, no source URLs, no detailed clinical item text.
- Record command ids, command strings, exit codes, pass/fail status, and short output summaries.

## Rules

- The app still does not execute external commands during web requests.
- The recorder script is the only component that runs final verification commands.
- Tests use an injected runner so unit tests do not run the full suite recursively.
- A recorded evidence file is `verified` only when every command exits `0` and the gate status at recording time is `ready_for_final_verification`.
- Missing evidence is not a blocker for displaying the gate; it appears as `not_recorded`.

## Safety Scope

- Local staff verification only.
- No patient data.
- No credentials.
- No clinical recommendation changes.
- No diagnosis, treatment, medication, broker, trading, order API, or Shioaji behavior.

## Acceptance Checks

- Red tests fail before the recorder exists.
- Recorder writes summary-only JSON with no detailed clinical fixture text.
- Final Verification Gate reads missing and verified evidence states.
- Targeted tests, full regression, Django check, live smoke, real recorder run, and handoff verify pass.
