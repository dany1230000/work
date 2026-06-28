# Scoped Deployment Package Commit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create local Git commit(s) for the verified clinical deployment package and completion record so Deployment Status advances from `ready_for_publish_package` to `ready_for_remote_setup`.

**Architecture:** Keep this as an operations phase, not an application feature. Use `.gitignore` to exclude local verification artifacts, then run fresh verification before and after a scoped Git commit.

**Tech Stack:** Git, PowerShell, existing Django test runner, existing clinical deployment status commands.

---

## File Structure

- Modify: `clinical_differential_support/.gitignore`
  - Ignore generated local verification artifacts.
- Modify: `.planning/2026-06-22-clinical-differential-support/task_plan.md`
  - Add Phase 12 and decision/error tracking.
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`
  - Record Phase 12 actions and verification evidence.
- Create: `docs/superpowers/specs/2026-06-27-scoped-deployment-package-commit-design.md`
  - Design note for scoped commit boundary.
- Create: `docs/superpowers/plans/2026-06-27-scoped-deployment-package-commit.md`
  - This implementation plan.

### Task 1: Prepare the Commit Boundary

- [x] **Step 1: Inspect file-level status**

Run:

```powershell
git status --short -uall -- clinical_differential_support docs/superpowers .planning/2026-06-22-clinical-differential-support render.yaml
```

Expected: source/docs/planning files are untracked and `verification_artifacts` appears as generated local evidence.

- [x] **Step 2: Ignore local verification artifacts**

Add to `clinical_differential_support/.gitignore`:

```gitignore
verification_artifacts/
```

- [x] **Step 3: Confirm generated artifacts no longer appear**

Run:

```powershell
git status --short -uall -- clinical_differential_support/verification_artifacts
```

Expected: no output.

### Task 2: Pre-Commit Verification

- [x] **Step 1: Verify publish status before commit**

Run:

```powershell
$env:CDS_PUBLISH_STATUS_NO_PAUSE='1'
clinical_differential_support\Publish_Status.cmd --json
```

Expected: `publish_package_uncommitted`, exit code `2`, scoped dirty files only.

- [x] **Step 2: Run regression and check**

Run:

```powershell
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
```

Expected: `203 tests pass` and no system-check issues.

- [x] **Step 3: Run safety and whitespace scans**

Run:

```powershell
git diff --check -- clinical_differential_support docs .planning render.yaml
```

Expected: exit code `0`. Credential scan must be clear; trading/order scan may only show explicit prohibition text.

### Task 3: Create the Scoped Package Commit

- [x] **Step 1: Stage only the allowed package paths**

Run:

```powershell
git add -- clinical_differential_support docs/superpowers .planning/2026-06-22-clinical-differential-support render.yaml
```

- [x] **Step 2: Confirm staged scope excludes unrelated work**

Run:

```powershell
git diff --cached --name-only
```

Expected: no `tw_quant_v2`, `shop_report_lite`, Windows repair logs, or unrelated workspace paths.

- [x] **Step 3: Commit**

Run:

```powershell
git commit -m "feat: prepare clinical deployment package"
```

If Git identity is missing, use per-command Git author/committer environment variables without writing credentials or mutating global Git config.

### Task 4: Post-Commit Verification

- [x] **Step 1: Verify publish readiness advanced**

Run:

```powershell
$env:CDS_PUBLISH_STATUS_NO_PAUSE='1'
clinical_differential_support\Publish_Status.cmd --json
```

Expected: `publish_package_ready`, exit code `0`.

- [x] **Step 2: Verify deployment status advanced**

Run:

```powershell
py -B .\clinical_differential_support\scripts\deployment_status.py --json
```

Expected: `ready_for_remote_setup`, exit code `2`, next action `create_git_remote`.

- [x] **Step 3: Verify local final gate still passes**

Run:

```powershell
$env:CDS_FINAL_CHECK_NO_PAUSE='1'
clinical_differential_support\Final_Check.cmd
```

Expected: `final_complete`, exit code `0`.

- [x] **Step 4: Verify no external mutation**

Run:

```powershell
git remote -v
git status --short -- clinical_differential_support docs/superpowers .planning/2026-06-22-clinical-differential-support render.yaml
```

Expected: remote remains unchanged and scoped package status is clean.

- [x] **Step 5: Commit final planning evidence if needed**

If post-commit verification updates `.planning` records, run:

```powershell
git add -- .planning/2026-06-22-clinical-differential-support docs/superpowers
git commit -m "docs: record clinical deployment package verification"
```

Expected: only planning/spec/plan files are staged.

## Completion Evidence

- Local scoped commit set exists.
- `Publish_Status.cmd --json` reports `publish_package_ready`.
- Deployment Status reports `ready_for_remote_setup`.
- Final_Check remains `final_complete`.
- No unrelated paths were staged or committed.
- No remote, push, cloud login, or credential handling occurred.
- Package commit: `7085253 feat: prepare clinical deployment package`.
- Post-commit publish status: `publish_package_ready`, dirty count `0`.
- Post-commit deployment status: `ready_for_remote_setup`, next command `clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>`.
