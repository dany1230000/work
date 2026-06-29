from copy import deepcopy
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase

from cds_core.differential_catalog import CONDITIONS
from cds_core.differential_catalog_quality import (
    build_general_differential_catalog_quality_report,
)


class GeneralDifferentialCatalogQualityTests(SimpleTestCase):
    def test_report_summarizes_catalog_governance_and_next_actions(self):
        report = build_general_differential_catalog_quality_report()

        self.assertEqual(report["report_type"], "general_differential_catalog_quality")
        self.assertGreaterEqual(report["summary"]["condition_count"], 50)
        self.assertGreaterEqual(report["summary"]["source_count"], 5)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])
        self.assertIn("Cardiovascular", report["system_buckets"])
        self.assertIn("Neurologic", report["system_buckets"])
        self.assertEqual(
            report["next_actions"][0]["action_id"],
            "convert_static_catalog_to_reviewed_data_import",
        )
        self.assertIn(
            str(report["summary"]["condition_count"]),
            report["next_actions"][0]["reason_zh"],
        )

    def test_pulmonary_bucket_counts_respiratory_catalog_entries(self):
        report = build_general_differential_catalog_quality_report()
        pulmonary = report["system_buckets"]["Pulmonary"]

        self.assertGreaterEqual(pulmonary["condition_count"], 6)
        self.assertEqual(pulmonary["gap_count"], 0)
        self.assertEqual(pulmonary["status"], "target_met")

    def test_hematology_oncology_bucket_reaches_starter_depth(self):
        report = build_general_differential_catalog_quality_report()
        hematology_oncology = report["system_buckets"]["Hematology/Oncology"]

        self.assertGreaterEqual(hematology_oncology["condition_count"], 6)
        self.assertEqual(hematology_oncology["gap_count"], 0)
        self.assertEqual(hematology_oncology["status"], "target_met")

    def test_renal_urologic_bucket_counts_urinary_catalog_entries(self):
        report = build_general_differential_catalog_quality_report()
        renal_urologic = report["system_buckets"]["Renal/Urologic"]

        self.assertGreaterEqual(renal_urologic["condition_count"], 6)
        self.assertEqual(renal_urologic["gap_count"], 0)
        self.assertEqual(renal_urologic["status"], "target_met")

    def test_gynecologic_bucket_reaches_starter_depth(self):
        report = build_general_differential_catalog_quality_report()
        gynecologic = report["system_buckets"]["Gynecologic"]

        self.assertGreaterEqual(gynecologic["condition_count"], 5)
        self.assertEqual(gynecologic["gap_count"], 0)
        self.assertEqual(gynecologic["status"], "target_met")

    def test_mental_health_bucket_reaches_starter_depth(self):
        report = build_general_differential_catalog_quality_report()
        mental_health = report["system_buckets"]["Mental health"]

        self.assertGreaterEqual(mental_health["condition_count"], 6)
        self.assertEqual(mental_health["gap_count"], 0)
        self.assertEqual(mental_health["status"], "target_met")

    def test_skin_soft_tissue_bucket_reaches_starter_depth(self):
        report = build_general_differential_catalog_quality_report()
        skin_soft_tissue = report["system_buckets"]["Skin/Soft tissue"]

        self.assertGreaterEqual(skin_soft_tissue["condition_count"], 5)
        self.assertEqual(skin_soft_tissue["gap_count"], 0)
        self.assertEqual(skin_soft_tissue["status"], "target_met")

    def test_cardiovascular_bucket_reaches_starter_depth(self):
        report = build_general_differential_catalog_quality_report()
        cardiovascular = report["system_buckets"]["Cardiovascular"]

        self.assertGreaterEqual(cardiovascular["condition_count"], 8)
        self.assertEqual(cardiovascular["gap_count"], 0)
        self.assertEqual(cardiovascular["status"], "target_met")

    def test_report_flags_duplicate_slugs_and_unknown_sources(self):
        baseline = deepcopy(CONDITIONS[0])
        duplicate = deepcopy(CONDITIONS[1])
        duplicate["slug"] = baseline["slug"]
        duplicate["source_ids"] = ["missing_source"]

        report = build_general_differential_catalog_quality_report(
            conditions=[baseline, duplicate],
            sources={},
        )
        issue_codes = {issue["code"] for issue in report["blocking_issues"]}

        self.assertIn("duplicate_condition_slug", issue_codes)
        self.assertIn("unknown_source_id", issue_codes)
        self.assertFalse(report["summary"]["ready_for_public_reference"])


class GeneralDifferentialCatalogQualityCommandTests(SimpleTestCase):
    def test_validate_command_reports_publishable_catalog(self):
        stdout = StringIO()

        call_command("validate_general_differential_catalog", stdout=stdout)

        output = stdout.getvalue()
        self.assertIn("READY", output)
        self.assertIn("conditions", output)
        self.assertIn("blocking issues: 0", output)
