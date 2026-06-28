import contextlib
import io
import tempfile
import zipfile
from pathlib import Path

from django.test import TestCase

from scripts.export_handoff_bundle import export_bundle, main
from scripts.verify_handoff_bundle import verify_bundle


class HandoffBundleExporterTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def temp_path(self, filename="handoff-bundle.zip"):
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name) / filename
        self.addCleanup(temp_dir.cleanup)
        return path

    def test_export_bundle_writes_verified_zip(self):
        output_path = self.temp_path()

        result = export_bundle(output_path, overwrite=True)

        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.output_path, output_path)
        self.assertGreater(result.bytes_written, 0)
        self.assertTrue(output_path.exists())
        with zipfile.ZipFile(output_path) as archive:
            self.assertIn("manifest.json", archive.namelist())
        self.assertTrue(verify_bundle(output_path).ok)

    def test_export_bundle_refuses_to_overwrite_existing_file_by_default(self):
        output_path = self.temp_path()
        output_path.write_text("existing", encoding="utf-8")

        result = export_bundle(output_path)

        self.assertFalse(result.ok)
        self.assertIn(f"{output_path}: already exists", result.errors)
        self.assertEqual(output_path.read_text(encoding="utf-8"), "existing")

    def test_export_bundle_cli_returns_zero_for_verified_export(self):
        output_path = self.temp_path()
        stdout = io.StringIO()
        stderr = io.StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(["--output", str(output_path), "--overwrite"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("exported:", stdout.getvalue())
        self.assertIn("verified: ok", stdout.getvalue())
        self.assertTrue(verify_bundle(output_path).ok)
