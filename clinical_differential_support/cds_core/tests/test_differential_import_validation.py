from copy import deepcopy
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase

from cds_core.differential_catalog import CONDITIONS, SOURCES
from cds_core.differential_catalog_import import (
    build_general_differential_batch_template,
    validate_general_differential_review_payload,
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


class GeneralDifferentialImportValidationCommandTests(SimpleTestCase):
    def test_validate_command_accepts_default_review_seed(self):
        stdout = StringIO()

        call_command("validate_general_differential_review_seed", stdout=stdout)

        output = stdout.getvalue()
        self.assertIn("READY", output)
        self.assertIn(f"{len(CONDITIONS)} conditions", output)
        self.assertIn("blocking issues: 0", output)
