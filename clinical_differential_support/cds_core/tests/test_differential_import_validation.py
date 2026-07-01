from copy import deepcopy
from io import StringIO
import json
from tempfile import TemporaryDirectory
from pathlib import Path

from django.core.management import call_command, CommandError
from django.test import SimpleTestCase

from cds_core.differential_catalog import CATALOG_VERSION, CONDITIONS, SOURCES
from cds_core.differential_catalog_import import (
    build_general_differential_batch_template,
    preview_general_differential_review_import,
    validate_general_differential_review_payload,
    write_reviewed_catalog_payload,
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

    def test_review_import_preview_marks_valid_payload_ready(self):
        payload = build_general_differential_review_seed()

        preview = preview_general_differential_review_import(payload)

        self.assertTrue(preview["ready_to_apply"])
        self.assertEqual(preview["status"], "ready")
        self.assertEqual(preview["summary"]["condition_count"], len(CONDITIONS))
        self.assertEqual(preview["summary"]["source_count"], len(SOURCES))
        self.assertFalse(preview["safety_scope"]["contains_patient_data"])
        self.assertIn(
            "validate_general_differential_catalog",
            preview["required_post_apply_checks"],
        )

    def test_write_reviewed_catalog_payload_outputs_valid_json(self):
        payload = build_general_differential_review_seed()

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "reviewed-catalog.json"
            written = write_reviewed_catalog_payload(payload, output_path)

            saved = json.loads(output_path.read_text(encoding="utf-8"))
            report = validate_general_differential_review_payload(saved)

        self.assertEqual(written["path"], str(output_path))
        self.assertEqual(written["condition_count"], len(CONDITIONS))
        self.assertEqual(written["source_count"], len(SOURCES))
        self.assertTrue(report["valid"])


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

    def test_import_command_previews_review_payload_without_writing_output(self):
        payload = build_general_differential_review_seed()

        with TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "review-seed.json"
            output_path = Path(temp_dir) / "reviewed-catalog.json"
            input_path.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            stdout = StringIO()

            call_command(
                "import_general_differential_reviewed_catalog",
                "--path",
                str(input_path),
                "--output",
                str(output_path),
                stdout=stdout,
            )

            self.assertFalse(output_path.exists())

        output = stdout.getvalue()
        self.assertIn("READY reviewed catalog import preview", output)
        self.assertIn(f"{len(CONDITIONS)} conditions", output)
        self.assertIn("apply required to write output", output)

    def test_import_command_applies_review_payload_to_output_path(self):
        payload = build_general_differential_review_seed()

        with TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "review-seed.json"
            output_path = Path(temp_dir) / "reviewed-catalog.json"
            input_path.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            stdout = StringIO()

            call_command(
                "import_general_differential_reviewed_catalog",
                "--path",
                str(input_path),
                "--output",
                str(output_path),
                "--apply",
                stdout=stdout,
            )

            saved = json.loads(output_path.read_text(encoding="utf-8"))
            report = validate_general_differential_review_payload(saved)

        self.assertTrue(report["valid"])
        self.assertIn("APPLIED reviewed catalog import", stdout.getvalue())
        self.assertIn(f"{len(CONDITIONS)} conditions", stdout.getvalue())

    def test_import_command_rejects_invalid_payload(self):
        payload = build_general_differential_review_seed()
        payload["safety_scope"]["contains_patient_data"] = True

        with TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "invalid.json"
            output_path = Path(temp_dir) / "reviewed-catalog.json"
            input_path.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )

            with self.assertRaises(CommandError):
                call_command(
                    "import_general_differential_reviewed_catalog",
                    "--path",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--apply",
                    stdout=StringIO(),
                )

            self.assertFalse(output_path.exists())

    def test_import_command_requires_overwrite_for_existing_output(self):
        payload = build_general_differential_review_seed()

        with TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "review-seed.json"
            output_path = Path(temp_dir) / "reviewed-catalog.json"
            input_path.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            output_path.write_text("existing", encoding="utf-8")

            with self.assertRaises(CommandError):
                call_command(
                    "import_general_differential_reviewed_catalog",
                    "--path",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--apply",
                    stdout=StringIO(),
                )

            self.assertEqual(output_path.read_text(encoding="utf-8"), "existing")
