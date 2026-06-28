# Safe Staff Setup Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe interactive Windows staff setup entry and wire it into Final Gate, Launch Control, CLI output, and docs without automating credentials.

**Architecture:** `cds_core.local_launch` remains the shared readiness selector and will expose the Windows entry plus the raw Django fallback. `cds_core.project_completion` uses the Windows entry as the primary next action. Templates, docs, and tests read those selector fields instead of hard-coding account setup behavior.

**Tech Stack:** Django, Python standard library, Windows batch scripts, Django `TestCase`.

---

### Task 1: Lock The Missing Entry With Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_staff_setup_entry.py`
- Modify: `clinical_differential_support/cds_core/tests/test_project_completion.py`
- Modify: `clinical_differential_support/cds_core/tests/test_launch_guide.py`

- [ ] **Step 1: Write failing tests**

Add tests asserting:

```python
self.assertIn("Create_Staff_Reviewer.cmd", report["next_action"]["command"])
self.assertIn("createsuperuser", report["next_action"]["raw_command"])
self.assertIn("Create_Staff_Reviewer.cmd", body)
self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", script_body)
self.assertNotIn("--password", script_body)
```

- [ ] **Step 2: Run the focused tests**

Run:

```powershell
py -B .\clinical_differential_support\manage.py test cds_core.tests.test_staff_setup_entry cds_core.tests.test_project_completion cds_core.tests.test_launch_guide -v 2
```

Expected: fail because `Create_Staff_Reviewer.cmd`, selector fields, and page output do not exist yet.

### Task 2: Implement Selector And Formatter Fields

**Files:**
- Modify: `clinical_differential_support/cds_core/local_launch.py`
- Modify: `clinical_differential_support/cds_core/local_setup.py`
- Modify: `clinical_differential_support/cds_core/project_completion.py`

- [ ] **Step 1: Add constants and report fields**

Expose:

```python
CREATE_STAFF_REVIEWER_ENTRY_COMMAND = r"clinical_differential_support\Create_Staff_Reviewer.cmd"
CREATE_STAFF_COMMAND = r"py -B .\clinical_differential_support\manage.py createsuperuser"
```

Manual blocker and staff setup step should include `entry_command`, `command`, and `raw_command`.

- [ ] **Step 2: Make Final Gate primary command user-friendly**

For `create_staff_reviewer`, Final Gate should set:

```python
"command": CREATE_STAFF_REVIEWER_ENTRY_COMMAND
"raw_command": CREATE_STAFF_COMMAND
```

- [ ] **Step 3: Update text formatters**

Print the primary command first and the raw Django command second.

### Task 3: Add Windows Entry Script

**Files:**
- Create: `clinical_differential_support/Create_Staff_Reviewer.cmd`

- [ ] **Step 1: Add CRLF batch script**

The script must:

```batch
@echo off
chcp 65001 > nul
cd /d "%~dp0\.."
echo Create local staff reviewer
echo You will enter username, email, and password locally.
py -B .\clinical_differential_support\manage.py createsuperuser %*
set CREATE_STAFF_EXIT=%ERRORLEVEL%
echo Django createsuperuser exit code: %CREATE_STAFF_EXIT%
py -B .\clinical_differential_support\scripts\project_completion_status.py
set FINAL_GATE_EXIT=%ERRORLEVEL%
if not "%CDS_CREATE_STAFF_NO_PAUSE%"=="1" pause
exit /b %FINAL_GATE_EXIT%
```

### Task 4: Render The New Entry In UI And Docs

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/launch_guide.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/project_completion.html`
- Modify: `clinical_differential_support/README.md`
- Modify: `clinical_differential_support/QUICK_START.zh.md`

- [ ] **Step 1: Show the wrapper in manual blocker cards and completion next action**

Render `entry_command` where available and label `raw_command` as direct shell fallback.

- [ ] **Step 2: Update Quick Start**

Step 1 should tell the user to run:

```powershell
clinical_differential_support\Create_Staff_Reviewer.cmd
```

Then explain that Django prompts locally for username, email, and password.

### Task 5: Verify And Refresh Evidence

**Files:**
- Modify: `clinical_differential_support/cds_core/final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_final_verification_evidence_recorder.py`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Update expected regression count after adding tests**

Replace `169 tests pass` with the fresh full regression count.

- [ ] **Step 2: Run verification**

Run focused tests, full tests, `manage.py check`, `.cmd --help` safe verification, smoke check, evidence recorder, CRLF checks, diff check, readability scan, and safety scan.
