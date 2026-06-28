from django.test import TestCase
from django.urls import reverse

from cds_core.differential_catalog import CONDITIONS, SOURCES


class GeneralDifferentialUiTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def test_dashboard_links_to_general_differential_workbench(self):
        response = self.client.get(reverse("cds_core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "通用鑑別 / General differential")
        self.assertContains(response, reverse("cds_core:general_differential"))

    def test_general_differential_page_shows_stepwise_workflow_and_limits(self):
        response = self.client.get(reverse("cds_core:general_differential"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "通用鑑別工作台 / General Differential Workbench")
        self.assertContains(response, "步驟 1/4")
        self.assertContains(response, "步驟 4/4")
        self.assertContains(response, "不包含病人識別資料")
        self.assertContains(response, "starter catalog")
        self.assertContains(response, f"{len(CONDITIONS)} conditions")
        self.assertContains(response, f"{len(SOURCES)} sources")
        self.assertContains(response, "Catalog governance")
        self.assertContains(response, "0 blocking issues")
        self.assertContains(response, "Convert static catalog to reviewed data import")
        self.assertContains(response, "export_general_differential_review_seed")
        self.assertContains(response, "validate_general_differential_review_seed")
        self.assertContains(response, "export_general_differential_batch_template")
        self.assertContains(response, "Recent cancer treatment")
        self.assertContains(response, "Easy bruising or bleeding")
        self.assertContains(response, "Chest pain / 胸痛")
        self.assertContains(response, "Neurologic deficit / 神經學缺損")

    def test_posted_findings_show_ranked_conditions_ask_next_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "急性冠心症")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertContains(response, "emergent")
        self.assertContains(response, "下一步要問 / Ask next")
        self.assertContains(response, "American Heart Association")
        self.assertContains(response, "starter catalog")
        self.assertContains(response, f"{len(CONDITIONS)} conditions")
        self.assertContains(response, f"{len(SOURCES)} sources")
        self.assertContains(response, "不是 diagnosis order")
