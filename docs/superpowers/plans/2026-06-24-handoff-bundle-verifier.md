# Handoff Bundle Verifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local CLI verifier for downloaded staff-only handoff ZIP bundles.

**Architecture:** Implement a standalone stdlib script in `clinical_differential_support/scripts/` with a testable `verify_bundle(path)` function and a thin `main(argv=None)` CLI wrapper. Tests generate real bundle bytes from the existing builder and create tampered/missing-file variants in memory.

**Tech Stack:** Django TestCase for fixture-backed bundle generation, Python stdlib `zipfile`, `json`, `hashlib`, `argparse`, `dataclasses`.

---

### Task 1: Verifier Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_handoff_bundle_verifier.py`

- [ ] **Step 1: Add tests for valid, tampered, missing-file, and CLI behavior**

```python
import io
import tempfile
import zipfile
from pathlib import Path

from django.test import TestCase

from cds_core.bundle import build_handoff_bundle_zip
from scripts.verify_handoff_bundle import main, verify_bundle


class HandoffBundleVerifierTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def write_bundle(self, data):
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name) / "handoff-bundle.zip"
        path.write_bytes(data)
        return temp_dir, path
```

- [ ] **Step 2: Verify RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle_verifier -v 2`

Expected: FAIL because `scripts.verify_handoff_bundle` does not exist yet.

### Task 2: Standalone Verifier Script

**Files:**
- Create: `clinical_differential_support/scripts/verify_handoff_bundle.py`

- [ ] **Step 1: Add result type and helpers**

```python
@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    messages: list[str]
    errors: list[str]
```

- [ ] **Step 2: Implement `verify_bundle(path)`**

Validate ZIP readability, `manifest.json`, `package_type == "handoff_bundle"`, required files, `integrity_excluded` for `manifest.json`, and SHA-256/byte-size for each non-manifest payload.

- [ ] **Step 3: Implement `main(argv=None)`**

Parse one positional ZIP path, print messages/errors, and return `0` or `1`.

### Task 3: Docs And Verification

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Document verifier command**

```powershell
py -B clinical_differential_support\scripts\verify_handoff_bundle.py path\to\handoff-bundle.zip
```

- [ ] **Step 2: Verify GREEN**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle_verifier -v 2`

Expected: verifier tests pass.

- [ ] **Step 3: Full verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
git diff --check -- clinical_differential_support docs .planning
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Expected: all commands pass.
