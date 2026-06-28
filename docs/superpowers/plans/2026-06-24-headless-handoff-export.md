# Headless Handoff Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local CLI that exports and verifies the staff handoff bundle without a browser.

**Architecture:** Implement a standalone script that bootstraps Django, calls the existing bundle builder, writes the ZIP to disk, and calls the verifier. Tests call the script functions inside Django TestCase using temporary directories.

**Tech Stack:** Django 5.2, Python stdlib `argparse`, `dataclasses`, `pathlib`, existing bundle builder and verifier.

---

### Task 1: Exporter Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_handoff_bundle_exporter.py`

- [ ] **Step 1: Add failing tests**

```python
import contextlib
import io
import tempfile
import zipfile
from pathlib import Path

from django.test import TestCase

from scripts.export_handoff_bundle import export_bundle, main
from scripts.verify_handoff_bundle import verify_bundle
```

- [ ] **Step 2: Verify RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle_exporter -v 2`

Expected: FAIL because `scripts.export_handoff_bundle` does not exist.

### Task 2: Exporter Script

**Files:**
- Create: `clinical_differential_support/scripts/export_handoff_bundle.py`

- [ ] **Step 1: Add `ExportResult`**

```python
@dataclass(frozen=True)
class ExportResult:
    ok: bool
    output_path: Path
    bytes_written: int
    messages: list[str]
    errors: list[str]
```

- [ ] **Step 2: Add Django bootstrap**

Insert the project directory in `sys.path`, set `DJANGO_SETTINGS_MODULE`, and call `django.setup()` only if apps are not ready.

- [ ] **Step 3: Add `export_bundle(output_path, overwrite=False, verify=True)`**

Refuse overwrite without `overwrite=True`, create parent directories, write bundle bytes, and verify unless disabled.

- [ ] **Step 4: Add CLI wrapper**

Parse `--output`, `--overwrite`, and `--no-verify`; print messages/errors and return `0`/`1`.

### Task 3: Docs And Verification

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Document export command**

```powershell
py -B clinical_differential_support\scripts\export_handoff_bundle.py --output handoff-bundle.zip --overwrite
```

- [ ] **Step 2: Verify GREEN**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle_exporter -v 2`

Expected: exporter tests pass.

- [ ] **Step 3: Full verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
git diff --check -- clinical_differential_support docs .planning
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
py -B clinical_differential_support\scripts\export_handoff_bundle.py --output <temp>\handoff-bundle.zip --overwrite
```

Expected: all commands pass.
