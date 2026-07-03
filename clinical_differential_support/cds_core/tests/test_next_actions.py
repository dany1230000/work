import json
from datetime import date
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class NextActionWorkbenchTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "next-action-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_selector_marks_headache_only_scope_as_not_final(self):
        from cds_core.next_actions import build_next_action_plan

        plan = build_next_action_plan(today=date(2026, 6, 24))

        self.assertEqual(plan["completion_status"], "not_final_beyond_headache")
        self.assertEqual(plan["coverage"]["current_count"], 1)
        self.assertEqual(
            plan["coverage"]["current_chief_complaints"][0]["slug"], "headache"
        )
        self.assertEqual(plan["coverage"]["next_target"]["slug"], "chest-pain")
        self.assertEqual(
            plan["next_actions"][0]["action_id"], "add_chest_pain_module"
        )
        self.assertIn("新增", plan["next_actions"][0]["title_zh"])
        self.assertIn("Add chest pain module", plan["next_actions"][0]["title_en"])

    def test_unauthenticated_next_action_page_redirects_to_reviewer_login(self):
        next_action_path = reverse("cds_core:next_actions")

        response = self.client.get(next_action_path)

        self.assertReviewerLoginRedirect(response, next_action_path)

    def test_staff_next_action_page_renders_gap_and_prioritized_steps(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:next_actions"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "下一步工作台")
        self.assertContains(response, "Next Action Workbench")
        self.assertContains(response, "Current coverage has 1 chief complaint only")
        self.assertContains(response, "Headache")
        self.assertContains(response, "Chest pain")
        self.assertContains(response, "not the final multi-complaint version")
        self.assertContains(response, "Add chest pain module")

    def test_unauthenticated_next_action_json_redirects_to_reviewer_login(self):
        export_path = reverse("cds_core:export_next_actions_json")

        response = self.client.get(export_path)

        self.assertReviewerLoginRedirect(response, export_path)

    def test_staff_next_action_json_is_summary_only(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_next_actions_json"))
        payload = json.loads(response.content.decode("utf-8"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("next-actions.json", response["Content-Disposition"])
        self.assertEqual(payload["coverage"]["current_count"], 1)
        self.assertEqual(
            payload["next_actions"][0]["action_id"], "add_chest_pain_module"
        )
        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("ACR Appropriateness Criteria", body)
        self.assertNotIn("https://", body)

    def test_governance_dashboard_links_to_next_action_workbench(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertContains(response, "Next Action Workbench")
        self.assertContains(response, reverse("cds_core:next_actions"))

    def test_release_readiness_links_to_next_action_workbench(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(response, "Next Action Workbench")
        self.assertContains(response, reverse("cds_core:next_actions"))


class NextActionDownstreamReadinessTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "downstream-next-action-reviewer",
            password="test-pass",
            is_staff=True,
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_selector_advances_to_general_catalog_import_when_downstream_audits_are_clear(self):
        from cds_core.next_actions import build_next_action_plan

        plan = build_next_action_plan(today=date(2026, 6, 24))

        self.assertEqual(plan["completion_status"], "general_catalog_import_ready")
        self.assertEqual(
            plan["downstream_readiness"]["coverage_depth"]["complaints_with_gaps"],
            0,
        )
        self.assertEqual(
            plan["downstream_readiness"]["source_freshness"]["stale_source_count"],
            0,
        )
        self.assertEqual(
            plan["downstream_readiness"]["source_freshness"][
                "publication_date_gap_policy"
            ],
            "do_not_infer_missing_publication_dates",
        )
        self.assertEqual(
            plan["next_actions"][0]["action_id"],
            "expand_general_differential_catalog_via_import_workbench",
        )
        self.assertEqual(plan["next_actions"][0]["status"], "ready_to_start")
        self.assertEqual(plan["general_catalog"]["condition_count"], 500)
        self.assertEqual(plan["general_catalog"]["source_count"], 578)
        self.assertEqual(
            plan["general_catalog"]["import_workbench_path"],
            "/review/general-differential-import/",
        )
        self.assertEqual(
            plan["next_actions"][0]["url"],
            "/review/general-differential-import/",
        )

    def test_staff_next_action_page_renders_downstream_readiness(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:next_actions"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Downstream readiness")
        self.assertContains(response, "Coverage depth")
        self.assertContains(response, "Source freshness")
        self.assertContains(response, "general_catalog_import_ready")
        self.assertContains(response, "General Differential Import Workbench")
        self.assertContains(response, "500 conditions")
        self.assertContains(response, "578 sources")
        self.assertContains(response, reverse("cds_core:general_differential_import"))

    def test_staff_next_action_json_includes_summary_only_downstream_readiness(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_next_actions_json"))
        payload = json.loads(response.content.decode("utf-8"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["completion_status"], "general_catalog_import_ready")
        self.assertEqual(
            payload["downstream_readiness"]["source_freshness"]["first_action"],
            "run_full_regression_and_smoke_checks",
        )
        self.assertEqual(payload["general_catalog"]["condition_count"], 500)
        self.assertEqual(payload["general_catalog"]["source_count"], 578)
        self.assertEqual(
            payload["general_catalog"]["first_action"],
            "expand_general_differential_catalog_via_import_workbench",
        )
        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("Possible acute coronary syndrome", body)
        self.assertNotIn("https://", body)
