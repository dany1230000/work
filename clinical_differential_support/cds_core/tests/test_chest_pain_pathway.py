from django.test import TestCase
from django.urls import reverse

from cds_core.models import CaseScenario, ChiefComplaint, ClinicalItem, Rule, Source
from cds_core.services import evaluate_case_scenario, evaluate_chest_pain_pathway


class ChestPainPathwayTests(TestCase):
    fixtures = ["headache_mvp.json", "chest_pain_mvp.json"]

    def test_seed_content_adds_source_linked_chest_pain_module(self):
        self.assertEqual(ChiefComplaint.objects.count(), 2)
        self.assertTrue(ChiefComplaint.objects.filter(slug="chest-pain").exists())
        self.assertTrue(Source.objects.filter(version_label="CG95").exists())
        self.assertTrue(Source.objects.filter(version_label="2021 chest pain guideline").exists())
        self.assertGreaterEqual(
            ClinicalItem.objects.filter(chief_complaint__slug="chest-pain").count(),
            8,
        )
        self.assertGreaterEqual(
            Rule.objects.filter(chief_complaint__slug="chest-pain").count(),
            8,
        )

        for item in ClinicalItem.objects.filter(
            chief_complaint__slug="chest-pain",
            status=ClinicalItem.Status.APPROVED,
        ):
            self.assertTrue(item.sources.exists(), item.title)

    def test_next_action_plan_advances_after_chest_pain_exists(self):
        from cds_core.next_actions import build_next_action_plan

        plan = build_next_action_plan()

        self.assertEqual(plan["coverage"]["current_count"], 2)
        self.assertEqual(plan["coverage"]["next_target"]["slug"], "abdominal-pain")
        self.assertEqual(
            plan["next_actions"][0]["action_id"], "add_abdominal_pain_module"
        )

    def test_acute_chest_pain_matches_acs_and_ecg_troponin_workflow(self):
        result = evaluate_chest_pain_pathway(
            {"ongoing_chest_pain": True, "diaphoresis": True}
        )

        titles = [entry["item"].title for entry in result["outputs"]]

        self.assertIn("Possible acute coronary syndrome", titles)
        self.assertIn("ECG and high-sensitivity troponin workflow", titles)
        self.assertEqual(
            result["outputs"][0]["item"].item_type,
            ClinicalItem.ItemType.RED_FLAG,
        )

    def test_stable_exertional_pattern_matches_stable_angina_pathway(self):
        result = evaluate_chest_pain_pathway(
            {"stable_exertional_chest_pain": True, "relieved_by_rest": True}
        )

        titles = [entry["item"].title for entry in result["outputs"]]

        self.assertIn("Stable angina diagnostic pathway", titles)
        self.assertIn("Structured risk assessment pathway", titles)

    def test_nonischemic_high_risk_pattern_matches_emergent_prompt(self):
        result = evaluate_chest_pain_pathway({"tearing_radiating_back": True})

        titles = [entry["item"].title for entry in result["outputs"]]

        self.assertIn("Life-threatening nonischemic chest pain concern", titles)

    def test_chest_pain_view_renders_and_evaluates_reference_pathway(self):
        response = self.client.post(
            reverse("cds_core:chest_pain"),
            {"ongoing_chest_pain": "on", "diaphoresis": "on"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "胸痛結構化問診")
        self.assertContains(response, "Chest Pain Intake")
        self.assertContains(response, "For qualified medical professionals")
        self.assertContains(response, "Possible acute coronary syndrome")
        self.assertContains(response, "AHA/ACC")

    def test_chest_pain_case_scenario_uses_chief_complaint_pathway(self):
        scenario = CaseScenario.objects.get(slug="acute-acs-chest-pain")

        evaluation = evaluate_case_scenario(scenario)

        expected = {row["title"]: row["matched"] for row in evaluation["expected_outputs"]}
        self.assertTrue(expected["Possible acute coronary syndrome"])
        self.assertTrue(expected["ECG and high-sensitivity troponin workflow"])

    def test_low_intermediate_acs_case_validates_imaging_and_shared_decision_pathway(self):
        scenario = CaseScenario.objects.get(slug="low-intermediate-acs-chest-pain")

        evaluation = evaluate_case_scenario(scenario)

        expected = {row["title"]: row["matched"] for row in evaluation["expected_outputs"]}
        self.assertTrue(expected["Low-to-intermediate ACS imaging consideration"])
        self.assertTrue(expected["Structured risk assessment pathway"])
        self.assertTrue(expected["Shared decision-making for stable chest pain"])
