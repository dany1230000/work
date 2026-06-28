import json
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.source_freshness import build_source_freshness_report


class SourceFreshnessAuditTests(TestCase):
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
            "source-freshness-reviewer",
            password="test-pass",
            is_staff=True,
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_report_summarizes_source_freshness_from_governed_metadata(self):
        report = build_source_freshness_report()

        self.assertEqual(report["report_type"], "source_freshness_audit")
        self.assertEqual(report["summary"]["source_count"], 17)
        self.assertEqual(report["summary"]["current_source_count"], 17)
        self.assertEqual(report["summary"]["stale_source_count"], 0)
        self.assertEqual(report["summary"]["missing_publication_date_count"], 10)
        self.assertEqual(report["summary"]["stale_after_days"], 180)
        self.assertEqual(
            report["publication_date_gap_policy"]["policy_id"],
            "do_not_infer_missing_publication_dates",
        )
        self.assertTrue(
            report["publication_date_gap_policy"]["blank_dates_are_not_stale_blockers"]
        )
        self.assertEqual(
            report["publication_date_gap_policy"]["review_status"],
            "documented_pending_manual_verification",
        )
        self.assertEqual(
            report["next_actions"][0]["action_id"],
            "run_full_regression_and_smoke_checks",
        )
        self.assertEqual(report["next_actions"][0]["status"], "ready_to_run")
        self.assertEqual(len(report["sources"]), 17)
        missing_date_row = next(
            row
            for row in report["sources"]
            if row["publication_date_status"] == "not_listed_in_fixture"
        )
        self.assertEqual(
            missing_date_row["publication_date_review_status"],
            "manual_review_required",
        )
        self.assertFalse(missing_date_row["publication_date_gap_is_stale_blocker"])

    def test_unauthenticated_source_freshness_page_redirects_to_reviewer_login(self):
        path = reverse("cds_core:source_freshness")

        response = self.client.get(path)

        self.assertReviewerLoginRedirect(response, path)

    def test_staff_source_freshness_page_renders_summary_and_actions(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:source_freshness"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "來源新鮮度審查")
        self.assertContains(response, "Source Freshness Audit")
        self.assertContains(response, "Missing publication date")
        self.assertContains(response, "do_not_infer_missing_publication_dates")
        self.assertContains(response, "manual_review_required")
        self.assertContains(response, "ACR")
        self.assertContains(response, "NICE")

    def test_unauthenticated_source_freshness_json_redirects_to_reviewer_login(self):
        path = reverse("cds_core:export_source_freshness_json")

        response = self.client.get(path)

        self.assertReviewerLoginRedirect(response, path)

    def test_staff_source_freshness_json_contains_source_metadata_only(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_source_freshness_json"))
        body = response.content.decode("utf-8")
        payload = json.loads(body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["summary"]["source_count"], 17)
        self.assertEqual(payload["summary"]["stale_source_count"], 0)
        self.assertEqual(
            payload["publication_date_gap_policy"]["policy_id"],
            "do_not_infer_missing_publication_dates",
        )
        self.assertIn("https://", body)
        self.assertIn("manual_review_required", body)
        self.assertIn("source-freshness.json", response["Content-Disposition"])
        self.assertNotIn("document_publication_date_gaps", body)
        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("Possible acute coronary syndrome", body)

    def test_governance_source_library_and_coverage_depth_link_to_source_freshness(self):
        self.staff_login()

        dashboard_response = self.client.get(reverse("cds_core:review_dashboard"))
        source_response = self.client.get(reverse("cds_core:source_index"))
        coverage_response = self.client.get(reverse("cds_core:coverage_depth"))

        self.assertContains(dashboard_response, "Source Freshness Audit")
        self.assertContains(dashboard_response, reverse("cds_core:source_freshness"))
        self.assertContains(source_response, "Source Freshness Audit")
        self.assertContains(source_response, reverse("cds_core:source_freshness"))
        self.assertContains(coverage_response, "Source Freshness Audit")
        self.assertContains(coverage_response, reverse("cds_core:source_freshness"))
