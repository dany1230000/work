import json
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase

from cds_core.differential_catalog_review_seed import (
    build_general_differential_review_seed,
)


class GeneralDifferentialReviewSeedTests(SimpleTestCase):
    def test_review_seed_exports_catalog_in_reviewable_import_shape(self):
        seed = build_general_differential_review_seed()

        self.assertEqual(
            seed["format_version"],
            "general-differential-review-seed-v1",
        )
        self.assertEqual(seed["catalog"]["condition_count"], 57)
        self.assertEqual(seed["catalog"]["source_count"], 8)
        self.assertTrue(seed["safety_scope"]["clinician_only"])
        self.assertTrue(seed["safety_scope"]["review_required_before_publication"])
        self.assertFalse(seed["safety_scope"]["contains_patient_data"])
        self.assertEqual(len(seed["conditions"]), 57)
        self.assertEqual(len(seed["sources"]), 8)

        first = seed["conditions"][0]
        self.assertIn("slug", first)
        self.assertIn("review_status", first)
        self.assertIn("source_ids", first)
        self.assertIn("signals", first)
        self.assertEqual(first["review_status"], "seed_needs_clinician_review")

    def test_review_seed_source_references_are_declared(self):
        seed = build_general_differential_review_seed()
        source_ids = {source["source_id"] for source in seed["sources"]}

        for condition in seed["conditions"]:
            with self.subTest(slug=condition["slug"]):
                self.assertTrue(set(condition["source_ids"]).issubset(source_ids))


class GeneralDifferentialReviewSeedCommandTests(SimpleTestCase):
    def test_export_command_outputs_parseable_json(self):
        stdout = StringIO()

        call_command("export_general_differential_review_seed", stdout=stdout)

        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            payload["format_version"],
            "general-differential-review-seed-v1",
        )
        self.assertEqual(payload["catalog"]["condition_count"], 57)
        self.assertEqual(payload["catalog"]["quality"]["blocking_issue_count"], 0)
