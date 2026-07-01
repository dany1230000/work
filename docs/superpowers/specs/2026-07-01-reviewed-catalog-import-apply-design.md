# Reviewed Catalog Import Apply Design

## Goal

把 general differential catalog 的擴充流程從「只能驗證 JSON」推進到「可安全預覽、可明確套用、可再驗證」的 reviewed-data import 管線。

## Chosen Approach

Use a command-first pipeline:

- `preview` validates a supplied reviewed catalog JSON and reports whether it can be applied.
- `apply` requires an explicit flag and an output path before writing data.
- Output is the same reviewed payload shape used by packaged runtime data.
- The workbench lists the new command as the next governance step.

This avoids a premature upload UI and keeps publication under explicit staff/CLI control.

## Safety Rules

- Never accept patient data.
- Never write unless validation passes.
- Never overwrite an existing file unless `--overwrite` is explicit.
- Keep the command staff/governance oriented and free of diagnosis, treatment, medication, or clinical order language.

## Acceptance Checks

- Preview reports `READY` without writing an output file.
- Apply writes normalized reviewed catalog JSON only when `--apply --output` is supplied.
- Invalid payloads and overwrite attempts fail with `CommandError`.
- Existing validators continue to accept the written output.
- The staff import workbench exposes the new command step.
