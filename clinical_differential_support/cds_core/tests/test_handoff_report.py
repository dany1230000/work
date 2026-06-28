from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HandoffReportTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "handoff-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_unauthenticated_handoff_report_redirects_to_reviewer_login(self):
        handoff_path = reverse("cds_core:export_handoff_report_markdown")

        response = self.client.get(handoff_path)

        self.assertReviewerLoginRedirect(response, handoff_path)

    def test_staff_can_export_handoff_report_markdown(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_handoff_report_markdown"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown; charset=utf-8")
        self.assertIn("handoff-report.md", response["Content-Disposition"])
        self.assertIn("# Clinical Differential Support Handoff Report", body)
        self.assertIn("## 交付狀態 / Handoff Status", body)
        self.assertIn("Ready for handoff", body)
        self.assertIn("Clinical items: 13", body)
        self.assertIn("Approved items: 13", body)
        self.assertIn("Case validations passed: 8", body)
        self.assertIn("/review/exports/clinical-items.csv", body)
        self.assertIn("/review/exports/sources.csv", body)
        self.assertIn("/review/exports/release-evidence.json", body)

    def test_handoff_report_omits_detailed_clinical_fixture_text(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_handoff_report_markdown"))
        body = response.content.decode("utf-8")

        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("ACR Appropriateness Criteria", body)
        self.assertNotIn("雷擊樣頭痛", body)

    def test_release_readiness_page_links_to_handoff_report(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(response, "Handoff report Markdown")
        self.assertContains(
            response, reverse("cds_core:export_handoff_report_markdown")
        )
