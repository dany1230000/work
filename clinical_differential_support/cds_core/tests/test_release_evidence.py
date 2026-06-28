from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ReleaseEvidencePackageTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "evidence-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_unauthenticated_release_evidence_redirects_to_reviewer_login(self):
        evidence_path = reverse("cds_core:export_release_evidence_json")

        response = self.client.get(evidence_path)

        self.assertReviewerLoginRedirect(response, evidence_path)

    def test_staff_can_export_release_evidence_json(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_release_evidence_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("release-evidence.json", response["Content-Disposition"])
        payload = response.json()
        self.assertEqual(payload["package_type"], "release_evidence")
        self.assertEqual(payload["service"], "clinical_differential_support")
        self.assertTrue(payload["staff_only"])
        self.assertIn("generated_at", payload)
        self.assertTrue(payload["readiness"]["ready_for_handoff"])
        self.assertEqual(payload["readiness"]["total_items"], 13)
        self.assertEqual(payload["readiness"]["source_gap_count"], 0)
        self.assertEqual(payload["validation"]["failed_case_count"], 0)
        self.assertEqual(
            payload["exports"]["clinical_items_csv"],
            "/review/exports/clinical-items.csv",
        )
        self.assertEqual(
            payload["exports"]["sources_csv"],
            "/review/exports/sources.csv",
        )
        self.assertTrue(payload["safety_scope"]["no_patient_identifying_data"])
        self.assertTrue(payload["safety_scope"]["no_diagnosis_or_treatment_orders"])
        self.assertTrue(payload["safety_scope"]["no_credentials"])

    def test_release_evidence_omits_detailed_clinical_fixture_text(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_release_evidence_json"))
        body = response.content.decode("utf-8")

        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("ACR Appropriateness Criteria", body)
        self.assertNotIn("雷擊樣頭痛", body)

    def test_release_readiness_page_links_to_evidence_package(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(response, "Release evidence JSON")
        self.assertContains(response, reverse("cds_core:export_release_evidence_json"))
