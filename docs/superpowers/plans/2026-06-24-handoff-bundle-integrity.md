# Handoff Bundle Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add SHA-256 and byte-size integrity metadata to the staff-only handoff ZIP manifest.

**Architecture:** Build all non-manifest ZIP payloads as UTF-8 bytes before generating the manifest. Pass those exact payload bytes into the manifest builder so the manifest records the same bytes that are written to the ZIP.

**Tech Stack:** Django 5.2, Python stdlib `hashlib`, `zipfile`, existing bundle builder tests.

---

### Task 1: Integrity Tests

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_handoff_bundle.py`

- [ ] **Step 1: Add a failing test for file integrity metadata**

```python
def test_handoff_bundle_manifest_records_file_integrity(self):
    self.staff_login()

    response = self.client.get(reverse("cds_core:export_handoff_bundle_zip"))

    with zipfile.ZipFile(io.BytesIO(response.content)) as bundle:
        manifest = json.loads(bundle.read("manifest.json").decode("utf-8"))
        entries = {entry["filename"]: entry for entry in manifest["files"]}
        for filename in (
            "handoff-report.md",
            "release-evidence.json",
            "clinical-items.csv",
            "sources.csv",
        ):
            payload = bundle.read(filename)
            self.assertEqual(entries[filename]["byte_size"], len(payload))
            self.assertEqual(entries[filename]["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(len(entries[filename]["sha256"]), 64)
        self.assertTrue(entries["manifest.json"]["integrity_excluded"])
```

- [ ] **Step 2: Verify RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle -v 2`

Expected: FAIL because manifest file entries do not yet include `byte_size`, `sha256`, or `integrity_excluded`.

### Task 2: Manifest Builder

**Files:**
- Modify: `clinical_differential_support/cds_core/bundle.py`

- [ ] **Step 1: Import `hashlib`**

```python
import hashlib
```

- [ ] **Step 2: Add file-entry helper**

```python
def _payload_metadata(payload):
    return {
        "byte_size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
```

- [ ] **Step 3: Change `build_handoff_bundle_manifest(package, payloads)`**

Each file entry for payload files should merge `_payload_metadata(payloads[filename])`. The `manifest.json` entry should set `integrity_excluded` and an integrity note.

### Task 3: Build Payloads Before Manifest

**Files:**
- Modify: `clinical_differential_support/cds_core/bundle.py`

- [ ] **Step 1: Encode payload files before manifest generation**

```python
payloads = {
    "handoff-report.md": build_handoff_report_markdown(package=package).encode("utf-8"),
    "release-evidence.json": _json_text(package).encode("utf-8"),
    "clinical-items.csv": clinical_csv.encode("utf-8"),
    "sources.csv": sources_csv.encode("utf-8"),
}
manifest = build_handoff_bundle_manifest(package, payloads)
```

- [ ] **Step 2: Write the same bytes to ZIP**

```python
archive.writestr("manifest.json", _json_text(manifest).encode("utf-8"))
for filename, payload in payloads.items():
    archive.writestr(filename, payload)
```

- [ ] **Step 3: Verify GREEN**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle -v 2`

Expected: 5 tests pass.

- [ ] **Step 4: Full verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Expected: full test suite passes, system check reports no issues, smoke check passes after server restart.
