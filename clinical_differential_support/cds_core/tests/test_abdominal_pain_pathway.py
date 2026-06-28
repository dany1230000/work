from django.test import TestCase
from django.urls import reverse

from cds_core.models import CaseScenario, ChiefComplaint, ClinicalItem, Rule, Source
from cds_core.services import evaluate_abdominal_pain_pathway, evaluate_case_scenario


class AbdominalPainPathwayTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
    ]

    def test_seed_content_adds_source_linked_abdominal_pain_module(self):
        self.assertEqual(ChiefComplaint.objects.count(), 3)
        self.assertTrue(ChiefComplaint.objects.filter(slug="abdominal-pain").exists())
        self.assertTrue(
            Source.objects.filter(
                version_label="ACR acute nonlocalized abdominal pain"
            ).exists()
        )
        self.assertTrue(
            Source.objects.filter(version_label="NICE NG126").exists()
        )
        self.assertGreaterEqual(
            ClinicalItem.objects.filter(
                chief_complaint__slug="abdominal-pain"
            ).count(),
            8,
        )
        self.assertGreaterEqual(
            Rule.objects.filter(chief_complaint__slug="abdominal-pain").count(),
            8,
        )

        for item in ClinicalItem.objects.filter(
            chief_complaint__slug="abdominal-pain",
            status=ClinicalItem.Status.APPROVED,
        ):
            self.assertTrue(item.sources.exists(), item.title)

    def test_generalized_abdominal_pain_with_fever_matches_nonlocalized_pathway(self):
        result = evaluate_abdominal_pain_pathway(
            {"generalized_abdominal_pain": True, "fever": True}
        )

        titles = [entry["item"].title for entry in result["outputs"]]

        self.assertIn("Acute nonlocalized abdominal pain with fever pathway", titles)
        self.assertIn("Structured abdominal pain reassessment", titles)

    def test_rlq_pain_with_inflammatory_features_matches_appendicitis_pathway(self):
        result = evaluate_abdominal_pain_pathway(
            {
                "right_lower_quadrant_pain": True,
                "fever": True,
                "leukocytosis": True,
            }
        )

        titles = [entry["item"].title for entry in result["outputs"]]

        self.assertIn("Right lower quadrant appendicitis pathway", titles)
        self.assertIn("Structured abdominal pain reassessment", titles)

    def test_ruq_pain_with_biliary_features_matches_biliary_pathway(self):
        result = evaluate_abdominal_pain_pathway(
            {"right_upper_quadrant_pain": True, "postprandial_ruq_pain": True}
        )

        titles = [entry["item"].title for entry in result["outputs"]]

        self.assertIn("Right upper quadrant biliary pathway", titles)

    def test_possible_early_pregnancy_pain_matches_ectopic_safety_prompt(self):
        result = evaluate_abdominal_pain_pathway(
            {
                "pregnancy_possible": True,
                "positive_pregnancy_test": True,
                "vaginal_bleeding": True,
            }
        )

        titles = [entry["item"].title for entry in result["outputs"]]

        self.assertIn("Early pregnancy and ectopic pregnancy safety prompt", titles)

    def test_abdominal_pain_view_renders_and_evaluates_reference_pathway(self):
        response = self.client.post(
            reverse("cds_core:abdominal_pain"),
            {"generalized_abdominal_pain": "on", "fever": "on"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "腹痛結構化問診")
        self.assertContains(response, "Abdominal Pain Intake")
        self.assertContains(response, "For qualified medical professionals")
        self.assertContains(response, "Acute nonlocalized abdominal pain with fever")
        self.assertContains(response, "ACR")

    def test_abdominal_pain_case_scenario_uses_chief_complaint_pathway(self):
        scenario = CaseScenario.objects.get(slug="nonlocalized-fever-abdominal-pain")

        evaluation = evaluate_case_scenario(scenario)

        expected = {
            row["title"]: row["matched"] for row in evaluation["expected_outputs"]
        }
        self.assertTrue(expected["Acute nonlocalized abdominal pain with fever pathway"])
        self.assertTrue(expected["Structured abdominal pain reassessment"])

    def test_next_action_plan_advances_after_abdominal_pain_exists(self):
        from cds_core.next_actions import build_next_action_plan

        plan = build_next_action_plan()

        self.assertEqual(plan["coverage"]["current_count"], 3)
        self.assertEqual(plan["coverage"]["next_target"]["slug"], "dyspnea")
        self.assertEqual(plan["next_actions"][0]["action_id"], "add_dyspnea_module")
