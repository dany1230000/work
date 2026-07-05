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
        self.assertEqual(report["summary"]["condition_count"], 825)
        self.assertEqual(report["summary"]["source_count"], 903)
        self.assertEqual(
            report["summary"]["batch_template_format_version"],
            "general-differential-review-batch-v1",
        )
        self.assertEqual(
            report["summary"]["review_seed_format_version"],
            "general-differential-review-seed-v1",
        )
        lowest_buckets = report["next_batch"]["lowest_coverage_buckets"]
        self.assertGreaterEqual(len(lowest_buckets), 3)
        self.assertEqual(
            lowest_buckets,
            sorted(lowest_buckets, key=lambda row: (row["condition_count"], row["system"])),
        )
        self.assertIn(
            "py -B manage.py export_general_differential_batch_template --pretty",
            [step["command"] for step in report["import_pipeline"]],
        )
        self.assertIn(
            "py -B manage.py import_general_differential_reviewed_catalog --path reviewed-catalog.json",
            [step["command"] for step in report["import_pipeline"]],
        )
        self.assertTrue(report["apply_policy"]["dry_run_first"])
        self.assertFalse(report["apply_policy"]["automatic_apply_allowed"])
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
        self.assertContains(response, "825 conditions")
        self.assertContains(response, "903 sources")
        self.assertContains(response, 'data-next-batch-table="true"')
        self.assertContains(response, 'data-import-pipeline="true"')
        self.assertContains(response, "export_general_differential_batch_template")
        self.assertContains(response, "validate_general_differential_review_seed")
        self.assertContains(response, "import_general_differential_reviewed_catalog")
        self.assertContains(response, 'data-import-apply-policy="true"')
        self.assertContains(response, "Dry-run first")
        self.assertContains(response, "Automatic apply allowed: no")
        self.assertContains(response, "No patient data")
        self.assertContains(
            response, reverse("cds_core:export_general_differential_import_json")
        )

    def test_staff_json_export_contains_governance_metadata_only(self):
        self.staff_login()

        response = self.client.get(
            reverse("cds_core:export_general_differential_import_json")
        )
        body = response.content.decode("utf-8")
        payload = json.loads(body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["summary"]["condition_count"], 825)
        self.assertEqual(payload["summary"]["source_count"], 903)
        self.assertTrue(payload["safety_scope"]["staff_only"])
        self.assertFalse(payload["safety_scope"]["contains_patient_data"])
        self.assertTrue(payload["apply_policy"]["dry_run_first"])
        self.assertFalse(payload["apply_policy"]["automatic_apply_allowed"])
        self.assertIn("general-differential-import.json", response["Content-Disposition"])
        self.assertNotIn("patient_name", body)
        self.assertNotIn("medical_record_number", body)

    def test_dashboard_and_readiness_link_to_import_workbench(self):
        self.staff_login()

        dashboard_response = self.client.get(reverse("cds_core:review_dashboard"))
        readiness_response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(
            dashboard_response, "General Differential Import Workbench"
        )
        self.assertContains(
            dashboard_response,
            reverse("cds_core:general_differential_import"),
        )
        self.assertContains(
            readiness_response, "General Differential Import Workbench"
        )
        self.assertContains(
            readiness_response,
            reverse("cds_core:general_differential_import"),
        )
