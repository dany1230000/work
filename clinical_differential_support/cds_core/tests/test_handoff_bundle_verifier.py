import contextlib
import io
import tempfile
import zipfile
from pathlib import Path

from django.test import TestCase

from cds_core.bundle import build_handoff_bundle_zip
from scripts.verify_handoff_bundle import main, verify_bundle


class HandoffBundleVerifierTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def write_bundle(self, data):
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name) / "handoff-bundle.zip"
        path.write_bytes(data)
        return temp_dir, path

    def tampered_bundle_bytes(self, filename, replacement):
        original = build_handoff_bundle_zip()
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(original)) as source:
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
                for info in source.infolist():
                    data = replacement if info.filename == filename else source.read(info.filename)
                    target.writestr(info.filename, data)
        return output.getvalue()

    def missing_file_bundle_bytes(self, omitted_filename):
        original = build_handoff_bundle_zip()
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(original)) as source:
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
                for info in source.infolist():
                    if info.filename != omitted_filename:
                        target.writestr(info.filename, source.read(info.filename))
        return output.getvalue()

    def test_verify_bundle_accepts_valid_handoff_bundle(self):
        temp_dir, bundle_path = self.write_bundle(build_handoff_bundle_zip())
        self.addCleanup(temp_dir.cleanup)

        result = verify_bundle(bundle_path)

        self.assertTrue(result.ok, result.errors)
        self.assertIn("handoff-bundle.zip: ok", result.messages)

    def test_verify_bundle_rejects_tampered_payload(self):
        temp_dir, bundle_path = self.write_bundle(
            self.tampered_bundle_bytes("clinical-items.csv", b"tampered\n")
        )
        self.addCleanup(temp_dir.cleanup)

        result = verify_bundle(bundle_path)

        self.assertFalse(result.ok)
        self.assertIn(
            "clinical-items.csv: sha256 mismatch",
            result.errors,
        )

    def test_verify_bundle_rejects_missing_payload_file(self):
        temp_dir, bundle_path = self.write_bundle(
            self.missing_file_bundle_bytes("sources.csv")
        )
        self.addCleanup(temp_dir.cleanup)

        result = verify_bundle(bundle_path)

        self.assertFalse(result.ok)
        self.assertIn("sources.csv: missing from ZIP", result.errors)

    def test_verify_bundle_rejects_missing_instructions_file(self):
        temp_dir, bundle_path = self.write_bundle(
            self.missing_file_bundle_bytes("handoff-instructions.md")
        )
        self.addCleanup(temp_dir.cleanup)

        result = verify_bundle(bundle_path)

        self.assertFalse(result.ok)
        self.assertIn("handoff-instructions.md: missing from ZIP", result.errors)

    def test_verify_bundle_cli_returns_exit_code(self):
        valid_temp_dir, valid_bundle_path = self.write_bundle(build_handoff_bundle_zip())
        invalid_temp_dir, invalid_bundle_path = self.write_bundle(
            self.tampered_bundle_bytes("sources.csv", b"tampered\n")
        )
        self.addCleanup(valid_temp_dir.cleanup)
        self.addCleanup(invalid_temp_dir.cleanup)

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(main([str(valid_bundle_path)]), 0)
            self.assertEqual(main([str(invalid_bundle_path)]), 1)
        self.assertIn("handoff-bundle.zip: ok", stdout.getvalue())
        self.assertIn("sources.csv: sha256 mismatch", stderr.getvalue())
