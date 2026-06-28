import hashlib
import io
import json
import zipfile
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HandoffBundleTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "bundle-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_unauthenticated_handoff_bundle_redirects_to_reviewer_login(self):
        bundle_path = reverse("cds_core:export_handoff_bundle_zip")

        response = self.client.get(bundle_path)

        self.assertReviewerLoginRedirect(response, bundle_path)

    def test_staff_can_export_handoff_bundle_zip(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_handoff_bundle_zip"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn("handoff-bundle.zip", response["Content-Disposition"])
        with zipfile.ZipFile(io.BytesIO(response.content)) as bundle:
            names = set(bundle.namelist())
            self.assertEqual(
                names,
                {
                    "manifest.json",
                    "handoff-instructions.md",
                    "handoff-report.md",
                    "release-evidence.json",
                    "clinical-items.csv",
                    "sources.csv",
                },
            )
            manifest = json.loads(bundle.read("manifest.json").decode("utf-8"))
            instructions = bundle.read("handoff-instructions.md").decode("utf-8")
            report = bundle.read("handoff-report.md").decode("utf-8")
            evidence = json.loads(bundle.read("release-evidence.json").decode("utf-8"))
            clinical_csv = bundle.read("clinical-items.csv").decode("utf-8")
            sources_csv = bundle.read("sources.csv").decode("utf-8")

        self.assertEqual(manifest["package_type"], "handoff_bundle")
        self.assertEqual(manifest["service"], "clinical_differential_support")
        self.assertTrue(manifest["staff_only"])
        self.assertEqual(manifest["readiness"]["total_items"], 13)
        self.assertEqual(manifest["validation"]["failed_case_count"], 0)
        self.assertEqual(
            manifest["exports"]["handoff_bundle_zip"],
            "/review/exports/handoff-bundle.zip",
        )
        self.assertEqual(
            manifest["exports"]["handoff_report_markdown"],
            "/review/exports/handoff-report.md",
        )
        self.assertTrue(manifest["safety_scope"]["content_governance_only"])
        self.assertIn("# Handoff Instructions", instructions)
        self.assertIn("交付包 / Handoff Bundle", instructions)
        self.assertIn("verify_handoff_bundle.py", instructions)
        self.assertIn("export_handoff_bundle.py", instructions)
        self.assertIn("Not clinical deployment approval", instructions)
        self.assertIn("# Clinical Differential Support Handoff Report", report)
        self.assertEqual(evidence["package_type"], "release_evidence")
        self.assertEqual(evidence["readiness"]["approved_count"], 13)
        self.assertIn("title_en", clinical_csv)
        self.assertIn("Thunderclap headache", clinical_csv)
        self.assertIn("ACR Appropriateness Criteria", sources_csv)

    def test_handoff_bundle_manifest_omits_credentials_and_order_fields(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_handoff_bundle_zip"))

        with zipfile.ZipFile(io.BytesIO(response.content)) as bundle:
            manifest_text = bundle.read("manifest.json").decode("utf-8")

        self.assertNotIn("password", manifest_text.lower())
        self.assertNotIn("api_key", manifest_text.lower())
        self.assertNotIn("PAPER_TRADABLE", manifest_text)
        self.assertNotIn("LIVE_TRADABLE", manifest_text)

    def test_handoff_bundle_manifest_records_file_integrity(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_handoff_bundle_zip"))

        with zipfile.ZipFile(io.BytesIO(response.content)) as bundle:
            manifest = json.loads(bundle.read("manifest.json").decode("utf-8"))
            entries = {entry["filename"]: entry for entry in manifest["files"]}
            for filename in (
                "handoff-instructions.md",
                "handoff-report.md",
                "release-evidence.json",
                "clinical-items.csv",
                "sources.csv",
            ):
                payload = bundle.read(filename)
                self.assertEqual(entries[filename]["byte_size"], len(payload))
                self.assertEqual(
                    entries[filename]["sha256"],
                    hashlib.sha256(payload).hexdigest(),
                )
                self.assertEqual(len(entries[filename]["sha256"]), 64)
            self.assertTrue(entries["manifest.json"]["integrity_excluded"])

    def test_release_readiness_page_links_to_handoff_bundle(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(response, "Handoff bundle ZIP")
        self.assertContains(response, reverse("cds_core:export_handoff_bundle_zip"))
