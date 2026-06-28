from django.test import TestCase
from django.urls import reverse

from cds_core.models import CaseScenario
from cds_core.services import evaluate_case_scenario


class CaseScenarioTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def test_fixture_contains_chinese_first_case_scenarios(self):
        self.assertGreaterEqual(CaseScenario.objects.count(), 8)

        scenario = CaseScenario.objects.get(slug="thunderclap-headache")

        self.assertEqual(scenario.primary_title, "雷擊樣頭痛病例")
        self.assertEqual(scenario.secondary_title, "Thunderclap headache case")
        self.assertEqual(scenario.findings["onset_peak_minutes"], 1)
        self.assertIn("Thunderclap headache", scenario.expected_item_titles)

    def test_case_index_page_lists_bilingual_scenarios(self):
        response = self.client.get(reverse("cds_core:case_index"))

        self.assertContains(response, "病例模擬")
        self.assertContains(response, "Case Simulation")
        self.assertContains(response, "雷擊樣頭痛病例")
        self.assertContains(response, "Thunderclap headache case")
        self.assertContains(response, "/cases/thunderclap-headache/")

    def test_case_detail_runs_scenario_and_marks_expected_outputs(self):
        response = self.client.get(
            reverse("cds_core:case_detail", kwargs={"slug": "thunderclap-headache"})
        )

        self.assertContains(response, "雷擊樣頭痛病例")
        self.assertContains(response, "雷擊樣頭痛")
        self.assertContains(response, "Thunderclap headache")
        self.assertContains(response, "符合預期")
        self.assertContains(response, "Matched")

    def test_evaluate_case_scenario_reports_expected_matches(self):
        scenario = CaseScenario.objects.get(slug="thunderclap-headache")

        result = evaluate_case_scenario(scenario)

        expected = result["expected_outputs"]
        self.assertEqual(expected[0]["title"], "Thunderclap headache")
        self.assertTrue(expected[0]["matched"])
