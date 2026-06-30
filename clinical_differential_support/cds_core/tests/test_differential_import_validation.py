from copy import deepcopy
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase

from cds_core.differential_catalog import CATALOG_VERSION, CONDITIONS, SOURCES
from cds_core.differential_catalog_import import (
    build_general_differential_batch_template,
    validate_general_differential_review_payload,
)
from cds_core.differential_catalog_data import (
    build_runtime_catalog_from_review_payload,
    get_general_differential_runtime_catalog,
    load_default_reviewed_catalog_payload,
)
from cds_core.differential_catalog_review_seed import (
    build_general_differential_review_seed,
)


class GeneralDifferentialImportValidationTests(SimpleTestCase):
    def test_validator_accepts_current_review_seed(self):
        payload = build_general_differential_review_seed()

        report = validate_general_differential_review_payload(payload)

        self.assertTrue(report["valid"])
        self.assertEqual(report["summary"]["condition_count"], len(CONDITIONS))
        self.assertEqual(report["summary"]["source_count"], len(SOURCES))
        self.assertEqual(report["summary"]["blocking_issue_count"], 0)

    def test_validator_rejects_patient_data_and_unknown_source(self):
        payload = deepcopy(build_general_differential_review_seed())
        payload["safety_scope"]["contains_patient_data"] = True
        payload["conditions"][0]["source_ids"] = ["missing_source"]

        report = validate_general_differential_review_payload(payload)
        issue_codes = {issue["code"] for issue in report["blocking_issues"]}

        self.assertFalse(report["valid"])
        self.assertIn("patient_data_not_allowed", issue_codes)
        self.assertIn("unknown_source_id", issue_codes)

    def test_batch_template_defines_next_expansion_shape(self):
        template = build_general_differential_batch_template()
        condition = template["conditions"][0]

        self.assertEqual(
            template["format_version"],
            "general-differential-review-batch-v1",
        )
        self.assertFalse(template["safety_scope"]["contains_patient_data"])
        self.assertEqual(condition["review_status"], "draft_needs_clinician_review")
        self.assertIn("source_ids", condition)
        self.assertIn("signals", condition)
        self.assertIn("ask_next", condition)

    def test_default_reviewed_catalog_data_file_is_valid(self):
        payload = load_default_reviewed_catalog_payload()

        report = validate_general_differential_review_payload(payload)

        self.assertTrue(report["valid"])
        self.assertEqual(report["summary"]["condition_count"], len(CONDITIONS))
        self.assertEqual(report["summary"]["source_count"], len(SOURCES))

    def test_review_payload_can_be_normalized_for_runtime_catalog(self):
        payload = build_general_differential_review_seed()

        runtime_catalog = build_runtime_catalog_from_review_payload(payload)

        self.assertEqual(runtime_catalog["catalog_version"], payload["catalog"]["catalog_version"])
        self.assertEqual(len(runtime_catalog["conditions"]), len(CONDITIONS))
        self.assertEqual(len(runtime_catalog["sources"]), len(SOURCES))
        self.assertNotIn("review_status", runtime_catalog["conditions"][0])
        self.assertIn(CONDITIONS[0]["source_ids"][0], runtime_catalog["sources"])

    def test_default_runtime_catalog_comes_from_packaged_reviewed_data(self):
        get_general_differential_runtime_catalog.cache_clear()

        runtime_catalog = get_general_differential_runtime_catalog()

        self.assertEqual(runtime_catalog["catalog_version"], CATALOG_VERSION)
        self.assertEqual(len(runtime_catalog["conditions"]), len(CONDITIONS))
        self.assertEqual(len(runtime_catalog["sources"]), len(SOURCES))
        self.assertNotIn("review_status", runtime_catalog["conditions"][0])


class GeneralDifferentialImportValidationCommandTests(SimpleTestCase):
    def test_validate_command_accepts_default_review_seed(self):
        stdout = StringIO()

        call_command("validate_general_differential_review_seed", stdout=stdout)

        output = stdout.getvalue()
        self.assertIn("READY", output)
        self.assertIn(f"{len(CONDITIONS)} conditions", output)
        self.assertIn("blocking issues: 0", output)

    def test_validate_data_command_accepts_packaged_reviewed_catalog(self):
        stdout = StringIO()

        call_command("validate_general_differential_reviewed_catalog_data", stdout=stdout)

        output = stdout.getvalue()
        self.assertIn("READY", output)
        self.assertIn(f"{len(CONDITIONS)} conditions", output)
        self.assertIn("blocking issues: 0", output)
