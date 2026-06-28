# Handoff Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a staff-only Markdown handoff report for human-readable MVP transfer.

**Architecture:** Create a focused handoff-report builder that formats existing release evidence into Markdown. Expose it through a staff-only Django view and link it from the release readiness page.

**Tech Stack:** Django 5.2, Python string formatting, existing reviewer staff guard, Django TestCase.

---

### Task 1: Handoff Report Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_handoff_report.py`

- [ ] **Step 1: Write failing tests**

```python
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HandoffReportTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "handoff-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_unauthenticated_handoff_report_redirects_to_reviewer_login(self):
        handoff_path = reverse("cds_core:export_handoff_report_markdown")

        response = self.client.get(handoff_path)

        self.assertReviewerLoginRedirect(response, handoff_path)

    def test_staff_can_export_handoff_report_markdown(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_handoff_report_markdown"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown; charset=utf-8")
        self.assertIn("handoff-report.md", response["Content-Disposition"])
        self.assertIn("# Clinical Differential Support Handoff Report", body)
        self.assertIn("## 交付狀態 / Handoff Status", body)
        self.assertIn("Ready for handoff", body)
        self.assertIn("Clinical items: 13", body)
        self.assertIn("Approved items: 13", body)
        self.assertIn("Case validations passed: 8", body)
        self.assertIn("/review/exports/clinical-items.csv", body)
        self.assertIn("/review/exports/sources.csv", body)
        self.assertIn("/review/exports/release-evidence.json", body)

    def test_handoff_report_omits_detailed_clinical_fixture_text(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_handoff_report_markdown"))
        body = response.content.decode("utf-8")

        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("ACR Appropriateness Criteria", body)
        self.assertNotIn("雷擊樣頭痛", body)

    def test_release_readiness_page_links_to_handoff_report(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(response, "Handoff report Markdown")
        self.assertContains(
            response, reverse("cds_core:export_handoff_report_markdown")
        )
```

- [ ] **Step 2: Verify RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_report -v 2`

Expected: FAIL because the route `export_handoff_report_markdown` does not exist yet.

### Task 2: Markdown Builder

**Files:**
- Create: `clinical_differential_support/cds_core/handoff.py`
- Modify: `clinical_differential_support/cds_core/evidence.py`

- [ ] **Step 1: Add the release evidence export route to the summary package**

```python
"release_evidence_json": "/review/exports/release-evidence.json",
```

- [ ] **Step 2: Implement `build_handoff_report_markdown(now=None, today=None)`**

```python
from .evidence import build_release_evidence_package


def build_handoff_report_markdown(now=None, today=None):
    package = build_release_evidence_package(now=now, today=today)
    readiness = package["readiness"]
    validation = package["validation"]
    exports = package["exports"]
    status = (
        "Ready for handoff"
        if readiness["ready_for_handoff"]
        else "Needs governance work"
    )
    case_validations_passed = (
        validation["case_count"] - validation["failed_case_count"]
    )

    lines = [
        "# Clinical Differential Support Handoff Report",
        "",
        "## 交付狀態 / Handoff Status",
        f"- Status: {status}",
        f"- Generated at: {package['generated_at']}",
    ]
    return "\n".join(lines)
```

- [ ] **Step 3: Expand the report to include governance summary, export routes, safety scope, and notes**

Use only count fields, booleans, and route strings from the evidence package.

### Task 3: View, Route, Link, Docs

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/release_readiness.html`
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Add staff-only Markdown view**

```python
@staff_required
def export_handoff_report_markdown(request):
    response = HttpResponse(
        build_handoff_report_markdown(),
        content_type="text/markdown; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="handoff-report.md"'
    return response
```

- [ ] **Step 2: Add route**

```python
path(
    "review/exports/handoff-report.md",
    views.export_handoff_report_markdown,
    name="export_handoff_report_markdown",
),
```

- [ ] **Step 3: Link from release readiness page**

```django
<a href="{% url 'cds_core:export_handoff_report_markdown' %}">交付報告 Markdown / Handoff report Markdown</a>
```

- [ ] **Step 4: Verify GREEN**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_handoff_report -v 2`

Expected: 4 tests pass.

- [ ] **Step 5: Full verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Expected: tests pass, system check reports no issues, smoke check passes after server restart.
