from copy import deepcopy
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase

from cds_core.differential_catalog import CONDITIONS, SOURCES
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

    def test_cross_system_emergency_batch_expands_catalog_depth(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 80)
        self.assertGreaterEqual(report["summary"]["source_count"], 52)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_pediatric_ent_metabolic_batch_expands_catalog_depth(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 86)
        self.assertGreaterEqual(report["summary"]["source_count"], 59)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_common_ambulatory_batch_expands_catalog_depth(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 100)
        self.assertGreaterEqual(report["summary"]["source_count"], 72)
        self.assertGreaterEqual(len(CONDITIONS), 100)
        self.assertGreaterEqual(len(SOURCES), 72)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_broad_primary_care_batch_expands_catalog_depth(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 125)
        self.assertGreaterEqual(report["summary"]["source_count"], 95)
        self.assertGreaterEqual(len(CONDITIONS), 125)
        self.assertGreaterEqual(len(SOURCES), 95)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_next_generalist_batch_expands_catalog_to_150_conditions_and_130_sources(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 150)
        self.assertGreaterEqual(report["summary"]["source_count"], 130)
        self.assertGreaterEqual(len(CONDITIONS), 150)
        self.assertGreaterEqual(len(SOURCES), 130)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_specialty_generalist_batch_expands_catalog_to_175_conditions_and_155_sources(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 175)
        self.assertGreaterEqual(report["summary"]["source_count"], 155)
        self.assertGreaterEqual(len(CONDITIONS), 175)
        self.assertGreaterEqual(len(SOURCES), 155)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_final_generalist_batch_expands_catalog_to_200_conditions_and_190_sources(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 200)
        self.assertGreaterEqual(report["summary"]["source_count"], 190)
        self.assertGreaterEqual(len(CONDITIONS), 200)
        self.assertGreaterEqual(len(SOURCES), 190)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_sixth_generalist_batch_expands_catalog_to_250_conditions(self):
        report = build_general_differential_catalog_quality_report()

        self.assertGreaterEqual(report["summary"]["condition_count"], 250)
        self.assertGreaterEqual(report["summary"]["source_count"], 195)
        self.assertGreaterEqual(len(CONDITIONS), 250)
        self.assertGreaterEqual(len(SOURCES), 195)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_sixth_generalist_batch_has_second_source_depth(self):
        report = build_general_differential_catalog_quality_report()
        sixth_batch_slugs = {condition["slug"] for condition in CONDITIONS[-50:]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["source_count"], 240)
        self.assertLessEqual(report["summary"]["warning_count"], 51)
        self.assertFalse(sixth_batch_slugs.intersection(single_source_slugs))

    def test_catalog_has_no_single_source_conditions(self):
        report = build_general_differential_catalog_quality_report()
        single_source_slugs = [
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        ]

        self.assertEqual(single_source_slugs, [])
        self.assertEqual(report["summary"]["warning_count"], 0)

    def test_seventh_generalist_batch_expands_catalog_to_300_without_warnings(self):
        report = build_general_differential_catalog_quality_report()
        seventh_batch_slugs = {condition["slug"] for condition in CONDITIONS[-50:]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["condition_count"], 300)
        self.assertGreaterEqual(report["summary"]["source_count"], 342)
        self.assertGreaterEqual(len(CONDITIONS), 300)
        self.assertGreaterEqual(len(SOURCES), 342)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)
        self.assertFalse(seventh_batch_slugs.intersection(single_source_slugs))
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_eighth_generalist_batch_expands_catalog_to_325_without_warnings(self):
        report = build_general_differential_catalog_quality_report()
        eighth_batch_slugs = {condition["slug"] for condition in CONDITIONS[-25:]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["condition_count"], 325)
        self.assertGreaterEqual(report["summary"]["source_count"], 404)
        self.assertGreaterEqual(len(CONDITIONS), 325)
        self.assertGreaterEqual(len(SOURCES), 404)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)
        self.assertFalse(eighth_batch_slugs.intersection(single_source_slugs))
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_ninth_generalist_batch_expands_catalog_to_350_without_warnings(self):
        report = build_general_differential_catalog_quality_report()
        ninth_batch_slugs = {condition["slug"] for condition in CONDITIONS[-25:]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["condition_count"], 350)
        self.assertGreaterEqual(report["summary"]["source_count"], 429)
        self.assertGreaterEqual(len(CONDITIONS), 350)
        self.assertGreaterEqual(len(SOURCES), 429)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)
        self.assertFalse(ninth_batch_slugs.intersection(single_source_slugs))
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_tenth_generalist_batch_expands_catalog_to_375_without_warnings(self):
        report = build_general_differential_catalog_quality_report()
        tenth_batch_slugs = {condition["slug"] for condition in CONDITIONS[-25:]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["condition_count"], 375)
        self.assertGreaterEqual(report["summary"]["source_count"], 453)
        self.assertGreaterEqual(len(CONDITIONS), 375)
        self.assertGreaterEqual(len(SOURCES), 453)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)
        self.assertFalse(tenth_batch_slugs.intersection(single_source_slugs))
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_eleventh_generalist_batch_expands_catalog_to_400_without_warnings(self):
        report = build_general_differential_catalog_quality_report()
        eleventh_batch_slugs = {condition["slug"] for condition in CONDITIONS[-50:-25]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["condition_count"], 400)
        self.assertGreaterEqual(report["summary"]["source_count"], 478)
        self.assertGreaterEqual(len(CONDITIONS), 400)
        self.assertGreaterEqual(len(SOURCES), 478)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)
        self.assertFalse(eleventh_batch_slugs.intersection(single_source_slugs))
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_twelfth_generalist_batch_expands_catalog_to_425_without_warnings(self):
        report = build_general_differential_catalog_quality_report()
        twelfth_batch_slugs = {condition["slug"] for condition in CONDITIONS[-50:-25]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["condition_count"], 425)
        self.assertGreaterEqual(report["summary"]["source_count"], 503)
        self.assertGreaterEqual(len(CONDITIONS), 425)
        self.assertGreaterEqual(len(SOURCES), 503)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)
        self.assertFalse(twelfth_batch_slugs.intersection(single_source_slugs))
        self.assertTrue(report["summary"]["ready_for_public_reference"])

    def test_thirteenth_generalist_batch_expands_catalog_to_450_without_warnings(self):
        report = build_general_differential_catalog_quality_report()
        thirteenth_batch_slugs = {condition["slug"] for condition in CONDITIONS[-25:]}
        single_source_slugs = {
            warning["subject"]
            for warning in report["warnings"]
            if warning["code"] == "single_source_condition"
        }

        self.assertGreaterEqual(report["summary"]["condition_count"], 450)
        self.assertGreaterEqual(report["summary"]["source_count"], 528)
        self.assertGreaterEqual(len(CONDITIONS), 450)
        self.assertGreaterEqual(len(SOURCES), 528)
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)
        self.assertFalse(thirteenth_batch_slugs.intersection(single_source_slugs))
        self.assertTrue(report["summary"]["ready_for_public_reference"])
        self.assertEqual(report["summary"]["expansion_target_condition_count"], 450)
        expansion_action = next(
            action
            for action in report["next_actions"]
            if action["action_id"] == "expand_condition_catalog_to_450"
        )
        self.assertEqual(expansion_action["status"], "done")

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

    def test_gastrointestinal_hepatic_bucket_reaches_starter_depth(self):
        report = build_general_differential_catalog_quality_report()
        gastrointestinal_hepatic = report["system_buckets"]["Gastrointestinal/Hepatic"]

        self.assertGreaterEqual(gastrointestinal_hepatic["condition_count"], 10)
        self.assertEqual(gastrointestinal_hepatic["gap_count"], 0)
        self.assertEqual(gastrointestinal_hepatic["status"], "target_met")

    def test_toxicology_environmental_bucket_reaches_starter_depth(self):
        report = build_general_differential_catalog_quality_report()
        toxicology_environmental = report["system_buckets"]["Toxicology/Environmental"]

        self.assertGreaterEqual(toxicology_environmental["condition_count"], 6)
        self.assertEqual(toxicology_environmental["gap_count"], 0)
        self.assertEqual(toxicology_environmental["status"], "target_met")

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
