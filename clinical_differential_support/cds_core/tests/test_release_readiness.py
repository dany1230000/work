from datetime import date
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.models import ChiefComplaint, ClinicalItem


class ReleaseReadinessTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "readiness-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_readiness_selector_marks_fixture_ready_for_handoff(self):
        from cds_core.governance import build_release_readiness_report

        report = build_release_readiness_report(today=date(2026, 6, 24))

        self.assertTrue(report["ready_for_handoff"])
        self.assertEqual(report["total_items"], 13)
        self.assertEqual(report["approved_count"], 13)
        self.assertEqual(report["non_approved_count"], 0)
        self.assertEqual(report["source_gap_count"], 0)
        self.assertEqual(report["review_due_count"], 0)
        self.assertEqual(report["failed_case_count"], 0)

    def test_readiness_selector_flags_governance_blockers(self):
        from cds_core.governance import build_release_readiness_report

        complaint = ChiefComplaint.objects.get(slug="headache")
        blocker = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Readiness blocker",
            title_zh="交付阻擋項目",
            title_en="Readiness blocker",
            summary="Draft blocker for readiness report.",
            summary_zh="交付整備報告測試用草稿阻擋項目。",
            summary_en="Draft blocker for readiness report.",
            urgency=ClinicalItem.Urgency.URGENT,
            status=ClinicalItem.Status.DRAFT,
            review_due_at=date(2026, 6, 1),
        )

        report = build_release_readiness_report(today=date(2026, 6, 24))

        self.assertFalse(report["ready_for_handoff"])
        self.assertIn(blocker, report["non_approved_items"])
        self.assertIn(blocker, report["source_gap_items"])
        self.assertIn(blocker, report["review_due_items"])
        self.assertEqual(report["non_approved_count"], 1)
        self.assertEqual(report["source_gap_count"], 1)
        self.assertEqual(report["review_due_count"], 1)

    def test_unauthenticated_readiness_page_redirects_to_reviewer_login(self):
        readiness_path = reverse("cds_core:release_readiness")

        response = self.client.get(readiness_path)

        self.assertReviewerLoginRedirect(response, readiness_path)

    def test_staff_readiness_page_renders_status_exports_and_metrics(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Release Readiness Report")
        self.assertContains(response, "Ready for handoff")
        self.assertContains(response, "Clinical item CSV")
        self.assertContains(response, "Source CSV")
        self.assertContains(response, reverse("cds_core:export_clinical_items_csv"))
        self.assertContains(response, reverse("cds_core:export_sources_csv"))
        self.assertContains(response, "13")

    def test_staff_dashboard_links_to_release_readiness_report(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertContains(response, "Release Readiness Report")
        self.assertContains(response, reverse("cds_core:release_readiness"))
