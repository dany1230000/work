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
        self.assertContains(response, "Inability to void")
        self.assertContains(response, "Vaginal discharge")
        self.assertContains(response, "Cervical motion tenderness")
        self.assertContains(response, "Suicidal ideation")
        self.assertContains(response, "Hallucinations or delusions")
        self.assertContains(response, "Decreased need for sleep")
        self.assertContains(response, "Purulent skin lesion")
        self.assertContains(response, "Vesicular dermatomal rash")
        self.assertContains(response, "Mucosal lesions")
        self.assertContains(response, "Positional or pleuritic chest pain")
        self.assertContains(response, "Acute limb pain, pallor, or pulselessness")
        self.assertContains(response, "Pain out of proportion to exam")
        self.assertContains(response, "Bloody diarrhea")
        self.assertContains(response, "Carbon monoxide or combustion exposure")
        self.assertContains(response, "Multiple people with similar symptoms")
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

    def test_posted_gynecologic_findings_show_pid_toa_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "pelvic_pain",
                    "fever",
                    "vaginal_discharge",
                    "cervical_motion_tenderness",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "骨盆腔發炎性疾病")
        self.assertContains(response, "Pelvic inflammatory disease")
        self.assertContains(response, "輸卵管卵巢膿瘍")
        self.assertContains(response, "Tubo-ovarian abscess")
        self.assertContains(response, "下一步要問 / Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "CDC")

    def test_posted_mental_health_findings_show_safety_and_psychosis_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "suicidal_ideation",
                    "self_harm_behavior",
                    "hallucinations_delusions",
                    "severe_agitation",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "自殺或自傷風險")
        self.assertContains(response, "Suicide or self-harm risk")
        self.assertContains(response, "急性精神病性症狀")
        self.assertContains(response, "Acute psychosis")
        self.assertContains(response, "下一步要問 / Ask next")
        self.assertContains(response, "NIMH")
        self.assertContains(response, "NICE")

    def test_posted_skin_findings_show_sjs_ten_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "rash",
                    "mucosal_lesions",
                    "skin_sloughing_or_blistering",
                    "new_medication_exposure",
                    "fever",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "史蒂文斯-強森症候群")
        self.assertContains(response, "Stevens-Johnson syndrome")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "DermNet")

    def test_posted_cardiovascular_findings_show_pericarditis_limb_ischemia_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "positional_pleuritic_chest_pain",
                    "acute_limb_pain_pallor_pulselessness",
                    "severe_pain",
                    "neurologic_deficit",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acute pericarditis or myocarditis")
        self.assertContains(response, "Acute limb ischemia")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "Society for Vascular Surgery")

    def test_posted_gastrointestinal_findings_show_mesenteric_ischemia_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "pain_out_of_proportion_to_exam",
                    "abdominal_pain",
                    "severe_pain",
                    "vomiting",
                    "bloody_diarrhea",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acute mesenteric ischemia")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "World Society of Emergency Surgery")

    def test_posted_toxicology_findings_show_carbon_monoxide_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "carbon_monoxide_or_combustion_exposure",
                    "multiple_people_same_symptoms",
                    "altered_mental_status",
                    "syncope",
                    "vomiting",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carbon monoxide poisoning")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "CDC")
        self.assertContains(response, "Merck Manual Professional")
