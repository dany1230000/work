from django.test import TestCase
from django.urls import reverse


class OperationalReadinessTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def test_health_check_returns_minimal_json_without_clinical_content(self):
        response = self.client.get(reverse("cds_core:health_check"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "clinical_differential_support")
        self.assertEqual(payload["checks"]["database"], "ok")
        self.assertNotIn("Thunderclap headache", response.content.decode())

    def test_smoke_check_normalizes_base_url_and_builds_route_plan(self):
        from scripts.smoke_check import build_check_plan, normalize_base_url

        self.assertEqual(normalize_base_url("http://127.0.0.1:8000/"), "http://127.0.0.1:8000")

        plan = build_check_plan("http://127.0.0.1:8000/")
        checks_by_name = {check.name: check for check in plan}

        self.assertEqual(plan[0].name, "health")
        self.assertEqual(plan[0].url, "http://127.0.0.1:8000/health/")
        self.assertEqual(plan[0].expected_status, 200)
        self.assertEqual(
            checks_by_name["launch_guide"].url,
            "http://127.0.0.1:8000/launch/",
        )
        self.assertEqual(checks_by_name["launch_guide"].expected_status, 200)
        self.assertEqual(
            checks_by_name["launch_guide"].expected_text,
            "Local Control Panel",
        )
        self.assertEqual(
            checks_by_name["completion_gate"].url,
            "http://127.0.0.1:8000/completion/",
        )
        self.assertEqual(checks_by_name["completion_gate"].expected_status, 200)
        self.assertEqual(
            checks_by_name["completion_gate"].expected_text,
            "Final Project Gate",
        )
        self.assertEqual(
            checks_by_name["deployment_status"].url,
            "http://127.0.0.1:8000/deployment/",
        )
        self.assertEqual(checks_by_name["deployment_status"].expected_status, 200)
        self.assertEqual(
            checks_by_name["deployment_status"].expected_text,
            "Deployment Operations Center",
        )
        self.assertEqual(
            checks_by_name["chest_pain"].url,
            "http://127.0.0.1:8000/chest-pain/",
        )
        self.assertEqual(checks_by_name["chest_pain"].expected_status, 200)
        self.assertEqual(checks_by_name["chest_pain"].expected_text, "Chest Pain Intake")
        self.assertEqual(
            checks_by_name["abdominal_pain"].url,
            "http://127.0.0.1:8000/abdominal-pain/",
        )
        self.assertEqual(checks_by_name["abdominal_pain"].expected_status, 200)
        self.assertEqual(
            checks_by_name["abdominal_pain"].expected_text,
            "Abdominal Pain Intake",
        )
        self.assertEqual(
            checks_by_name["dyspnea"].url,
            "http://127.0.0.1:8000/dyspnea/",
        )
        self.assertEqual(checks_by_name["dyspnea"].expected_status, 200)
        self.assertEqual(checks_by_name["dyspnea"].expected_text, "Dyspnea Intake")
        self.assertEqual(
            checks_by_name["protected_source_create"].expected_status,
            302,
        )
        self.assertEqual(
            checks_by_name["protected_source_create"].expected_location,
            "/review/login/?next=/review/sources/new/",
        )
        self.assertEqual(
            checks_by_name["protected_handoff_report"].url,
            "http://127.0.0.1:8000/review/exports/handoff-report.md",
        )
        self.assertEqual(
            checks_by_name["protected_handoff_report"].expected_status,
            302,
        )
        self.assertEqual(
            checks_by_name["protected_handoff_report"].expected_location,
            "/review/login/?next=/review/exports/handoff-report.md",
        )
        self.assertEqual(
            checks_by_name["protected_handoff_bundle"].url,
            "http://127.0.0.1:8000/review/exports/handoff-bundle.zip",
        )
        self.assertEqual(
            checks_by_name["protected_handoff_bundle"].expected_status,
            302,
        )
        self.assertEqual(
            checks_by_name["protected_handoff_bundle"].expected_location,
            "/review/login/?next=/review/exports/handoff-bundle.zip",
        )
        self.assertEqual(
            checks_by_name["protected_next_actions"].url,
            "http://127.0.0.1:8000/review/next-actions/",
        )
        self.assertEqual(
            checks_by_name["protected_next_actions"].expected_location,
            "/review/login/?next=/review/next-actions/",
        )
        self.assertEqual(
            checks_by_name["protected_next_actions_json"].url,
            "http://127.0.0.1:8000/review/exports/next-actions.json",
        )
        self.assertEqual(
            checks_by_name["protected_next_actions_json"].expected_location,
            "/review/login/?next=/review/exports/next-actions.json",
        )
        self.assertEqual(
            checks_by_name["protected_coverage_depth"].url,
            "http://127.0.0.1:8000/review/coverage-depth/",
        )
        self.assertEqual(
            checks_by_name["protected_coverage_depth"].expected_location,
            "/review/login/?next=/review/coverage-depth/",
        )
        self.assertEqual(
            checks_by_name["protected_coverage_depth_json"].url,
            "http://127.0.0.1:8000/review/exports/coverage-depth.json",
        )
        self.assertEqual(
            checks_by_name["protected_coverage_depth_json"].expected_location,
            "/review/login/?next=/review/exports/coverage-depth.json",
        )
        self.assertEqual(
            checks_by_name["protected_source_freshness"].url,
            "http://127.0.0.1:8000/review/source-freshness/",
        )
        self.assertEqual(
            checks_by_name["protected_source_freshness"].expected_location,
            "/review/login/?next=/review/source-freshness/",
        )
        self.assertEqual(
            checks_by_name["protected_source_freshness_json"].url,
            "http://127.0.0.1:8000/review/exports/source-freshness.json",
        )
        self.assertEqual(
            checks_by_name["protected_source_freshness_json"].expected_location,
            "/review/login/?next=/review/exports/source-freshness.json",
        )
        self.assertEqual(
            checks_by_name["protected_final_verification"].url,
            "http://127.0.0.1:8000/review/final-verification/",
        )
        self.assertEqual(
            checks_by_name["protected_final_verification"].expected_location,
            "/review/login/?next=/review/final-verification/",
        )
        self.assertEqual(
            checks_by_name["protected_final_verification_json"].url,
            "http://127.0.0.1:8000/review/exports/final-verification.json",
        )
        self.assertEqual(
            checks_by_name["protected_final_verification_json"].expected_location,
            "/review/login/?next=/review/exports/final-verification.json",
        )
