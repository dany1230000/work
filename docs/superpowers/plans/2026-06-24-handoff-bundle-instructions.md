# Handoff Bundle Instructions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a self-contained instructions markdown file to the staff handoff ZIP and verifier.

**Architecture:** Add a focused builder function in `cds_core.bundle` for `handoff-instructions.md`, include it in the bundle payload map before manifest generation, and update verifier required files.

**Tech Stack:** Django 5.2 tests, Python stdlib ZIP/hash verification, Markdown text payload.

---

### Task 1: Bundle Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_handoff_bundle.py`

- [ ] **Step 1: Add failing assertions for `handoff-instructions.md`**

Update the expected ZIP filenames to include `handoff-instructions.md`; read it and assert it includes:

```text
# Handoff Instructions
交付包 / Handoff Bundle
verify_handoff_bundle.py
export_handoff_bundle.py
Not clinical deployment approval
```

- [ ] **Step 2: Include `handoff-instructions.md` in integrity assertions**

Assert manifest byte size and SHA-256 match the ZIP payload.

- [ ] **Step 3: Verify RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle -v 2`

Expected: FAIL because the ZIP does not include `handoff-instructions.md`.

### Task 2: Verifier Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_handoff_bundle_verifier.py`

- [ ] **Step 1: Add missing-instructions rejection assertion**

Use the existing `missing_file_bundle_bytes("handoff-instructions.md")` helper and assert:

```python
self.assertIn("handoff-instructions.md: missing from ZIP", result.errors)
```

### Task 3: Bundle And Verifier Implementation

**Files:**
- Modify: `clinical_differential_support/cds_core/bundle.py`
- Modify: `clinical_differential_support/scripts/verify_handoff_bundle.py`

- [ ] **Step 1: Add `build_handoff_instructions_markdown()`**

Return a Chinese-first, English-supported Markdown instructions text.

- [ ] **Step 2: Add manifest file entry**

Add a `handoff-instructions.md` file entry with content type `text/markdown; charset=utf-8`, summary, and `_payload_metadata(...)`.

- [ ] **Step 3: Add instructions payload**

Add:

```python
"handoff-instructions.md": build_handoff_instructions_markdown().encode("utf-8")
```

- [ ] **Step 4: Update verifier required files**

Add `handoff-instructions.md` to `REQUIRED_FILES`.

### Task 4: Verification

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Verify GREEN**

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle -v 2
py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle_verifier -v 2
```

Expected: both targeted suites pass.

- [ ] **Step 2: Full verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
git diff --check -- clinical_differential_support docs .planning
py -B clinical_differential_support\scripts\export_handoff_bundle.py --output <temp>\handoff-bundle.zip --overwrite
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Expected: all commands pass.
