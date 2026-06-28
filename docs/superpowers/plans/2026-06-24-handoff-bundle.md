# Handoff Bundle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single staff-only ZIP handoff bundle containing the existing human-readable, machine-readable, and CSV handoff artifacts.

**Architecture:** Add a focused bundle builder that composes existing evidence, handoff-report, and CSV export builders in memory. Expose it through a staff-only Django view and link it from the readiness page.

**Tech Stack:** Django 5.2, Python stdlib `zipfile`, `json`, `io`, existing reviewer staff guard.

---

### Task 1: Bundle Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_handoff_bundle.py`

- [ ] **Step 1: Write failing tests**

```python
import io
import json
import zipfile
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HandoffBundleTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "bundle-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_unauthenticated_handoff_bundle_redirects_to_reviewer_login(self):
        bundle_path = reverse("cds_core:export_handoff_bundle_zip")

        response = self.client.get(bundle_path)

        self.assertReviewerLoginRedirect(response, bundle_path)
```

- [ ] **Step 2: Verify RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle -v 2`

Expected: FAIL because `export_handoff_bundle_zip` does not exist.

### Task 2: CSV Text Helper And Bundle Builder

**Files:**
- Modify: `clinical_differential_support/cds_core/exports.py`
- Modify: `clinical_differential_support/cds_core/handoff.py`
- Create: `clinical_differential_support/cds_core/bundle.py`

- [ ] **Step 1: Add `build_csv_text(headers, rows)` and make `csv_response()` reuse it**

```python
def build_csv_text(headers, rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow({header: safe_csv_value(row.get(header, "")) for header in headers})
    return output.getvalue()
```

- [ ] **Step 2: Allow handoff report builder to receive an existing evidence package**

```python
def build_handoff_report_markdown(now=None, today=None, package=None):
    package = package or build_release_evidence_package(now=now, today=today)
```

- [ ] **Step 3: Build ZIP bytes in memory**

```python
def build_handoff_bundle_zip(now=None, today=None):
    package = build_release_evidence_package(now=now, today=today)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", manifest_json)
        archive.writestr("handoff-report.md", build_handoff_report_markdown(package=package))
        archive.writestr("release-evidence.json", evidence_json)
        archive.writestr("clinical-items.csv", clinical_csv)
        archive.writestr("sources.csv", sources_csv)
    return buffer.getvalue()
```

### Task 3: View, Route, Link, Docs

**Files:**
- Modify: `clinical_differential_support/cds_core/evidence.py`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/release_readiness.html`
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Add staff-only ZIP view**

```python
@staff_required
def export_handoff_bundle_zip(request):
    response = HttpResponse(
        build_handoff_bundle_zip(),
        content_type="application/zip",
    )
    response["Content-Disposition"] = 'attachment; filename="handoff-bundle.zip"'
    return response
```

- [ ] **Step 2: Add route and readiness link**

```python
path(
    "review/exports/handoff-bundle.zip",
    views.export_handoff_bundle_zip,
    name="export_handoff_bundle_zip",
)
```

- [ ] **Step 3: Verify GREEN**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_bundle -v 2`

Expected: bundle tests pass.

- [ ] **Step 4: Full verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Expected: tests pass, system check reports no issues, smoke check passes after server restart.
