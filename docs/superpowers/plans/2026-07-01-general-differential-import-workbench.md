# General Differential Import Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a staff-only workbench that turns catalog expansion into a stepwise reviewed-import workflow.

**Architecture:** Add a focused report-builder module that composes existing catalog quality, batch-template, and review-seed helpers. Add staff-only HTML and JSON views using the current governance page pattern, then link the page from existing reviewer surfaces.

**Tech Stack:** Django views/templates/tests, existing Python catalog helper modules, Django test client, existing management commands.

---

### Task 1: Failing Governance Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`

- [ ] **Step 1: Write the failing tests**

```python
import json
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.differential_catalog_workbench import (
    build_general_differential_import_workbench,
)


class GeneralDifferentialImportWorkbenchTests(TestCase):
    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "general-import-reviewer",
            password="test-pass",
            is_staff=True,
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_report_builds_next_batch_and_import_pipeline(self):
        report = build_general_differential_import_workbench()

        self.assertEqual(report["report_type"], "general_differential_import_workbench")
        self.assertEqual(report["summary"]["condition_count"], 300)
        self.assertEqual(report["summary"]["source_count"], 379)
        self.assertEqual(
            report["summary"]["batch_template_format_version"],
            "general-differential-review-batch-v1",
        )
        self.assertEqual(
            report["summary"]["review_seed_format_version"],
            "general-differential-review-seed-v1",
        )
        self.assertGreaterEqual(len(report["next_batch"]["lowest_coverage_buckets"]), 3)
        self.assertEqual(
            report["next_batch"]["lowest_coverage_buckets"],
            sorted(
                report["next_batch"]["lowest_coverage_buckets"],
                key=lambda row: (row["condition_count"], row["system"]),
            ),
        )
        self.assertIn(
            "py -B manage.py export_general_differential_batch_template --pretty",
            [step["command"] for step in report["import_pipeline"]],
        )
        self.assertFalse(report["safety_scope"]["contains_patient_data"])
        self.assertTrue(report["safety_scope"]["review_required_before_publication"])

    def test_unauthenticated_page_redirects_to_reviewer_login(self):
        path = reverse("cds_core:general_differential_import")

        response = self.client.get(path)

        self.assertReviewerLoginRedirect(response, path)

    def test_staff_page_renders_next_batch_pipeline_and_export(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:general_differential_import"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "通用鑑別匯入工作台")
        self.assertContains(response, "General Differential Import Workbench")
        self.assertContains(response, "300 conditions")
        self.assertContains(response, "379 sources")
        self.assertContains(response, 'data-next-batch-table="true"')
        self.assertContains(response, 'data-import-pipeline="true"')
        self.assertContains(response, "export_general_differential_batch_template")
        self.assertContains(response, "validate_general_differential_review_seed")
        self.assertContains(response, "No patient data")
        self.assertContains(response, reverse("cds_core:export_general_differential_import_json"))

    def test_staff_json_export_contains_governance_metadata_only(self):
        self.staff_login()

        response = self.client.get(
            reverse("cds_core:export_general_differential_import_json")
        )
        payload = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["summary"]["condition_count"], 300)
        self.assertEqual(payload["summary"]["source_count"], 379)
        self.assertTrue(payload["safety_scope"]["staff_only"])
        self.assertFalse(payload["safety_scope"]["contains_patient_data"])
        self.assertIn("general-differential-import.json", response["Content-Disposition"])
        self.assertNotIn("patient_name", response.content.decode("utf-8"))

    def test_dashboard_and_readiness_link_to_import_workbench(self):
        self.staff_login()

        dashboard_response = self.client.get(reverse("cds_core:review_dashboard"))
        readiness_response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(dashboard_response, "General Differential Import Workbench")
        self.assertContains(
            dashboard_response,
            reverse("cds_core:general_differential_import"),
        )
        self.assertContains(readiness_response, "General Differential Import Workbench")
        self.assertContains(
            readiness_response,
            reverse("cds_core:general_differential_import"),
        )
```

- [ ] **Step 2: Run the targeted test to verify RED**

Run: `py -B manage.py test cds_core.tests.test_general_differential_import_workbench -v 2`

Expected: FAIL because `cds_core.differential_catalog_workbench` does not exist yet.

### Task 2: Report Builder

**Files:**
- Create: `clinical_differential_support/cds_core/differential_catalog_workbench.py`
- Test: `clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py`

- [ ] **Step 1: Implement the minimal builder**

```python
from .differential_catalog_import import BATCH_TEMPLATE_FORMAT_VERSION
from .differential_catalog_quality import (
    build_general_differential_catalog_quality_report,
)
from .differential_catalog_review_seed import (
    REVIEW_SEED_EXPORT_COMMAND,
    REVIEW_SEED_FORMAT_VERSION,
)


def build_general_differential_import_workbench():
    quality = build_general_differential_catalog_quality_report()
    summary = quality["summary"]
    lowest_buckets = sorted(
        quality["system_buckets"],
        key=lambda row: (row["condition_count"], row["system"]),
    )[:6]

    return {
        "report_type": "general_differential_import_workbench",
        "summary": {
            **summary,
            "batch_template_format_version": BATCH_TEMPLATE_FORMAT_VERSION,
            "review_seed_format_version": REVIEW_SEED_FORMAT_VERSION,
            "catalog_target_met": (
                summary["condition_count"]
                >= summary["expansion_target_condition_count"]
            ),
        },
        "next_batch": {
            "strategy": "expand_lowest_coverage_buckets_first",
            "recommended_batch_size": 12,
            "lowest_coverage_buckets": [
                {
                    **row,
                    "recommended_batch_size": 12,
                    "review_focus": "add reviewed, source-backed conditions before changing public ranking logic",
                }
                for row in lowest_buckets
            ],
        },
        "import_pipeline": [
            {
                "step_id": "export_review_seed",
                "label_zh": "匯出目前審核基準",
                "label_en": "Export current review seed",
                "command": REVIEW_SEED_EXPORT_COMMAND,
            },
            {
                "step_id": "export_batch_template",
                "label_zh": "匯出匯入批次模板",
                "label_en": "Export reviewed batch template",
                "command": "py -B manage.py export_general_differential_batch_template --pretty",
            },
            {
                "step_id": "validate_review_seed",
                "label_zh": "驗證審核基準",
                "label_en": "Validate review seed",
                "command": "py -B manage.py validate_general_differential_review_seed",
            },
            {
                "step_id": "validate_catalog",
                "label_zh": "驗證通用鑑別 catalog",
                "label_en": "Validate general differential catalog",
                "command": "py -B manage.py validate_general_differential_catalog",
            },
        ],
        "safety_scope": {
            **quality["safety_scope"],
            "staff_only": True,
            "contains_patient_data": False,
            "review_required_before_publication": True,
        },
        "exports": {
            "json_filename": "general-differential-import.json",
        },
    }
```

- [ ] **Step 2: Run targeted test**

Run: `py -B manage.py test cds_core.tests.test_general_differential_import_workbench -v 2`

Expected: URL/view tests still fail because routes and templates do not exist yet.

### Task 3: Staff Views, URLs, and Template

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Create: `clinical_differential_support/cds_core/templates/cds_core/general_differential_import.html`

- [ ] **Step 1: Wire views and URLs**

Add staff-only page and JSON export using `build_general_differential_import_workbench()`.

- [ ] **Step 2: Render the workbench**

Template must include:
- `data-next-batch-table="true"`
- `data-import-pipeline="true"`
- "300 conditions"
- "379 sources"
- command checklist rows
- "No patient data"

- [ ] **Step 3: Run targeted test**

Run: `py -B manage.py test cds_core.tests.test_general_differential_import_workbench -v 2`

Expected: dashboard/readiness link test still fails until navigation is added.

### Task 4: Governance Navigation Links

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/release_readiness.html`

- [ ] **Step 1: Add staff navigation links**

Add a link labeled `通用鑑別匯入工作台 / General Differential Import Workbench` to the reviewer dashboard and release readiness page.

- [ ] **Step 2: Run targeted test**

Run: `py -B manage.py test cds_core.tests.test_general_differential_import_workbench -v 2`

Expected: PASS.

### Task 5: Verification, Commit, Push, Deploy Smoke

**Files:**
- Use changed files from Tasks 1-4.

- [ ] **Step 1: Run focused tests**

Run: `py -B manage.py test cds_core.tests.test_general_differential_import_workbench -v 2`

Expected: `OK`.

- [ ] **Step 2: Run full tests**

Run: `py -B manage.py test -v 2`

Expected: all tests pass.

- [ ] **Step 3: Run catalog validator**

Run: `py -B manage.py validate_general_differential_catalog`

Expected: `READY`, `Blocking issues: 0`, `Warnings: 0`.

- [ ] **Step 4: Run local staff smoke**

Use Django test client to log in a staff user and GET `/review/general-differential-import/` plus `/review/exports/general-differential-import.json`.

Expected: both return 200 and include import-pipeline and 300-condition markers.

- [ ] **Step 5: Commit and push**

Run: `git add docs/superpowers/specs/2026-07-01-general-differential-import-workbench-design.md docs/superpowers/plans/2026-07-01-general-differential-import-workbench.md clinical_differential_support/cds_core/differential_catalog_workbench.py clinical_differential_support/cds_core/tests/test_general_differential_import_workbench.py clinical_differential_support/cds_core/views.py clinical_differential_support/cds_core/urls.py clinical_differential_support/cds_core/templates/cds_core/general_differential_import.html clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html clinical_differential_support/cds_core/templates/cds_core/release_readiness.html`

Run: `git commit -m "Add general differential import workbench"`

Run: `git push origin master`

- [ ] **Step 6: Run public smoke after Render deploy**

GET the deployed workbench and export with reviewer authentication if available; otherwise smoke public deployment markers that do not require credentials and note the staff page remains protected.
