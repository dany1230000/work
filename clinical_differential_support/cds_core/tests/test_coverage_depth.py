import json
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.coverage_depth import build_coverage_depth_report


class CoverageDepthReviewTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "coverage-depth-reviewer",
            password="test-pass",
            is_staff=True,
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_report_summarizes_multi_complaint_coverage_and_gaps(self):
        report = build_coverage_depth_report()
        rows_by_slug = {row["slug"]: row for row in report["complaints"]}

        self.assertEqual(report["summary"]["chief_complaint_count"], 4)
        self.assertEqual(report["summary"]["clinical_item_count"], 37)
        self.assertEqual(report["summary"]["rule_count"], 37)
        self.assertEqual(report["summary"]["case_count"], 20)
        self.assertEqual(report["summary"]["source_count"], 17)
        self.assertEqual(report["summary"]["source_gap_count"], 0)
        self.assertEqual(report["summary"]["failed_case_count"], 0)
        self.assertEqual(report["summary"]["complaints_with_gaps"], 0)
        self.assertNotIn("case_depth_gap", rows_by_slug["chest-pain"]["gap_codes"])
        self.assertNotIn("case_depth_gap", rows_by_slug["dyspnea"]["gap_codes"])
        self.assertEqual(
            report["next_actions"][0]["action_id"],
            "audit_source_freshness",
        )

    def test_unauthenticated_coverage_depth_page_redirects_to_reviewer_login(self):
        path = reverse("cds_core:coverage_depth")

        response = self.client.get(path)

        self.assertReviewerLoginRedirect(response, path)

    def test_staff_coverage_depth_page_renders_summary_and_gap_actions(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:coverage_depth"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "覆蓋深度審查")
        self.assertContains(response, "Coverage Depth Review")
        self.assertContains(response, "Chest pain")
        self.assertNotContains(response, "case_depth_gap")
        self.assertContains(response, "Audit source freshness")

    def test_unauthenticated_coverage_depth_json_redirects_to_reviewer_login(self):
        path = reverse("cds_core:export_coverage_depth_json")

        response = self.client.get(path)

        self.assertReviewerLoginRedirect(response, path)

    def test_staff_coverage_depth_json_is_summary_only(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_coverage_depth_json"))
        body = response.content.decode("utf-8")
        payload = json.loads(body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["report_type"], "coverage_depth_review")
        self.assertEqual(payload["summary"]["chief_complaint_count"], 4)
        self.assertEqual(payload["summary"]["complaints_with_gaps"], 0)
        self.assertIn("audit_source_freshness", body)
        self.assertNotIn("https://", body)
        self.assertNotIn("Thunderclap headache", body)
        self.assertIn("coverage-depth.json", response["Content-Disposition"])

    def test_governance_and_readiness_pages_link_to_coverage_depth_review(self):
        self.staff_login()

        dashboard_response = self.client.get(reverse("cds_core:review_dashboard"))
        readiness_response = self.client.get(reverse("cds_core:release_readiness"))
        next_actions_response = self.client.get(reverse("cds_core:next_actions"))

        self.assertContains(dashboard_response, "Coverage Depth Review")
        self.assertContains(dashboard_response, reverse("cds_core:coverage_depth"))
        self.assertContains(readiness_response, "Coverage Depth Review")
        self.assertContains(readiness_response, reverse("cds_core:coverage_depth"))
        self.assertContains(next_actions_response, "Coverage Depth Review")
        self.assertContains(next_actions_response, reverse("cds_core:coverage_depth"))
