from django.test import TestCase
from django.urls import reverse

from cds_core.models import CaseScenario, ChiefComplaint, ClinicalItem, Rule, Source
from cds_core.services import evaluate_case_scenario, evaluate_dyspnea_pathway


class DyspneaPathwayTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def test_seed_content_adds_source_linked_dyspnea_module(self):
        self.assertEqual(ChiefComplaint.objects.count(), 4)
        self.assertTrue(ChiefComplaint.objects.filter(slug="dyspnea").exists())
        self.assertTrue(
            Source.objects.filter(
                version_label="ACR acute respiratory illness immunocompetent"
            ).exists()
        )
        self.assertTrue(Source.objects.filter(version_label="NICE NG106").exists())
        self.assertTrue(
            Source.objects.filter(
                version_label="NHS adult breathlessness pathway"
            ).exists()
        )
        self.assertGreaterEqual(
            ClinicalItem.objects.filter(chief_complaint__slug="dyspnea").count(),
            8,
        )
        self.assertGreaterEqual(
            Rule.objects.filter(chief_complaint__slug="dyspnea").count(),
            8,
        )
        for item in ClinicalItem.objects.filter(
            chief_complaint__slug="dyspnea",
            status=ClinicalItem.Status.APPROVED,
        ):
            self.assertTrue(item.sources.exists(), item.title)

    def test_critical_dyspnea_matches_emergency_prompt(self):
        result = evaluate_dyspnea_pathway(
            {"severe_dyspnea": True, "hypoxemia": True}
        )
        titles = [entry["item"].title for entry in result["outputs"]]
        self.assertIn("Critical dyspnea emergency prompt", titles)

    def test_acute_respiratory_illness_matches_imaging_pathway(self):
        result = evaluate_dyspnea_pathway(
            {"acute_dyspnea": True, "cough": True, "fever": True}
        )
        titles = [entry["item"].title for entry in result["outputs"]]
        self.assertIn("Acute respiratory illness imaging pathway", titles)
        self.assertIn("Structured dyspnea reassessment", titles)

    def test_immunocompromised_dyspnea_matches_specific_prompt(self):
        result = evaluate_dyspnea_pathway(
            {
                "acute_dyspnea": True,
                "immunocompromised": True,
                "fever": True,
            }
        )
        titles = [entry["item"].title for entry in result["outputs"]]
        self.assertIn("Immunocompromised acute respiratory illness prompt", titles)

    def test_heart_failure_features_match_heart_failure_pathway(self):
        result = evaluate_dyspnea_pathway(
            {"orthopnea": True, "leg_edema": True}
        )
        titles = [entry["item"].title for entry in result["outputs"]]
        self.assertIn("Heart failure suspicion pathway", titles)

    def test_chronic_persistent_breathlessness_matches_diagnostic_pathway(self):
        result = evaluate_dyspnea_pathway(
            {"chronic_persistent_breathlessness": True, "dyspnea_duration_weeks": 10}
        )
        titles = [entry["item"].title for entry in result["outputs"]]
        self.assertIn("Chronic persistent breathlessness diagnostic pathway", titles)

    def test_dyspnea_view_renders_and_evaluates_reference_pathway(self):
        response = self.client.post(
            reverse("cds_core:dyspnea"),
            {"acute_dyspnea": "on", "cough": "on", "fever": "on"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "呼吸困難結構化問診")
        self.assertContains(response, "Dyspnea Intake")
        self.assertContains(response, "For qualified medical professionals")
        self.assertContains(response, "Acute respiratory illness imaging")
        self.assertContains(response, "ACR")

    def test_dyspnea_case_scenario_uses_chief_complaint_pathway(self):
        scenario = CaseScenario.objects.get(slug="acute-febrile-dyspnea")

        evaluation = evaluate_case_scenario(scenario)
        expected = {row["title"]: row["matched"] for row in evaluation["expected_outputs"]}

        self.assertTrue(expected["Acute respiratory illness imaging pathway"])
        self.assertTrue(expected["Structured dyspnea reassessment"])

    def test_next_action_plan_advances_to_coverage_depth_review(self):
        from cds_core.next_actions import build_next_action_plan

        plan = build_next_action_plan()

        self.assertEqual(plan["coverage"]["current_count"], 4)
        self.assertEqual(plan["coverage"]["gap_count"], 0)
        self.assertEqual(plan["coverage"]["next_target"]["slug"], "coverage-depth-review")
        self.assertEqual(
            plan["completion_status"],
            "general_catalog_import_ready",
        )
        self.assertEqual(
            plan["downstream_readiness"]["coverage_depth"]["complaints_with_gaps"],
            0,
        )
        self.assertEqual(
            plan["downstream_readiness"]["source_freshness"]["stale_source_count"],
            0,
        )
        self.assertEqual(
            plan["next_actions"][0]["action_id"],
            "expand_general_differential_catalog_via_import_workbench",
        )
        self.assertEqual(plan["general_catalog"]["condition_count"], 825)
