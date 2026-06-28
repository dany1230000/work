# Local Launch Entry Implementation Plan

## Scope

Create a local launch/status entry for the clinical differential support MVP.

## Steps

1. Add failing tests for local launch status selection:
   - no staff account -> create staff reviewer
   - staff account but no verified evidence -> run final verification recorder
   - staff account and verified evidence -> open final verification gate
   - formatted CLI output contains Chinese-first and English next-step labels
2. Implement `cds_core.local_launch`.
3. Add `scripts/local_launch_status.py`.
4. Add `Start_Local_Server.cmd`.
5. Update README launch and verification sections.
6. Verify with targeted tests, full tests, Django check, launcher status CLI, server smoke, final gate evidence, and safety scans.

## Acceptance Criteria

- The local status program prints the next step in Chinese and English.
- The Windows launcher exists at the path already referenced by README.
- The launcher does not create credentials or bypass staff login.
- Final verification evidence remains summary-only and verified.
- Full regression and smoke checks pass.
