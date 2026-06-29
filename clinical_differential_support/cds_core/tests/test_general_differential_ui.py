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
        self.assertContains(response, 'data-compact-differential-layout="true"')
        self.assertContains(response, 'data-step="safety"')
        self.assertContains(response, 'data-step="findings"')
        self.assertContains(response, 'data-step="results"')
        self.assertContains(response, 'data-step-command-bar="true"')
        self.assertContains(response, 'href="#case-input"')
        self.assertContains(response, 'href="#finding-selection"')
        self.assertContains(response, 'href="#reference-results"')
        self.assertContains(response, 'href="#catalog-governance"')
        self.assertContains(response, 'id="case-input"')
        self.assertContains(response, 'id="finding-selection"')
        self.assertContains(response, 'id="reference-results"')
        self.assertContains(response, 'id="catalog-governance"')
        self.assertContains(response, 'data-finding-group-default-open="true"')
        self.assertContains(response, "通用鑑別工作台 / General Differential Workbench")
        self.assertContains(response, "下一步 / Next step")
        self.assertContains(response, "不包含病人識別資料")
        self.assertContains(response, "starter catalog")
        self.assertContains(response, "Runtime source: packaged reviewed catalog data")
        self.assertContains(response, f"{len(CONDITIONS)} conditions")
        self.assertContains(response, f"{len(SOURCES)} sources")
        self.assertContains(response, 'class="finding-group"')
        self.assertContains(response, "<summary>")
        self.assertContains(response, 'data-finding-filter-form="true"')
        self.assertContains(response, 'data-finding-filter-input="true"')
        self.assertContains(response, 'data-selected-only-toggle="true"')
        self.assertContains(response, 'data-clear-finding-filter="true"')
        self.assertContains(response, 'data-finding-match-count="true"')
        self.assertContains(response, 'data-no-finding-matches="true"')
        self.assertContains(response, 'data-complaint-preset-bar="true"')
        self.assertContains(response, 'data-finding-preset="true"')
        self.assertContains(
            response,
            'data-finding-preset-query="cardiopulmonary"',
        )
        self.assertContains(response, 'data-finding-preset-mode="any"')
        self.assertContains(response, 'data-active-preset-label="true"')
        self.assertContains(response, "initializeFindingFilters")
        self.assertContains(response, "initializeFindingPresets")
        self.assertContains(response, "findingMatchesQuery")
        self.assertContains(response, "termMatchesSearchIndex")
        self.assertContains(response, "findingQueryMode")
        self.assertContains(response, ".finding-option[hidden]")
        self.assertContains(response, "先選主訴 / Start by complaint")
        self.assertContains(response, "胸痛/心悸 / Chest")
        self.assertContains(response, "神經/頭痛 / Neuro")
        self.assertContains(response, "腹部/泌尿 / Abdomen")
        self.assertContains(response, "眼耳鼻牙 / Eye ENT dental")
        self.assertContains(response, "快速篩選 findings / Filter findings")
        self.assertContains(response, "只看已選 / Selected only")
        self.assertContains(response, "清除 / Clear")
        self.assertContains(response, 'data-finding-search-index="chest pain')
        self.assertContains(response, "chest_pain acs mi heart attack")
        self.assertContains(response, "neurologic_deficit stroke tia cva")
        self.assertContains(response, 'class="compact-governance"')
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
        self.assertContains(response, "Acute hot swollen joint")
        self.assertContains(response, "Tense compartment or pain with passive stretch")
        self.assertContains(response, "Painful eye movement or proptosis")
        self.assertContains(response, "Preeclampsia warning features")
        self.assertContains(response, "Severe sore throat with drooling or stridor")
        self.assertContains(response, "Trismus, muffled voice, or uvular deviation")
        self.assertContains(response, "Neck stiffness/swelling with dysphagia")
        self.assertContains(response, "Seizure activity or postictal state")
        self.assertContains(response, "Palpitations")
        self.assertContains(response, "Barking cough or stridor")
        self.assertContains(response, "Eye trauma or contact lens use")
        self.assertContains(response, "Unilateral facial weakness")
        self.assertContains(response, "Dental pain or facial swelling")
        self.assertContains(response, "Urethral discharge")
        self.assertContains(response, "Early pregnancy bleeding")
        self.assertContains(response, "Severe hyperglycemia, dehydration, or confusion")
        self.assertContains(response, "Intermittent colicky abdominal pain or currant jelly stool")
        self.assertContains(response, "Persistent fever with mucocutaneous changes")
        self.assertContains(response, "Chest pain / 胸痛")
        self.assertContains(response, "Neurologic deficit / 神經學缺損")

    def test_posted_findings_put_results_before_catalog_governance(self):
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

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertLess(content.index('data-result-card="true"'), content.index("Catalog governance"))
        self.assertContains(response, 'class="next-step-panel"')
        self.assertContains(response, "下一步 / Ask next")
        self.assertContains(response, "已選 findings / Selected findings")
        self.assertContains(response, 'name="findings" value="chest_pain" checked')
        self.assertContains(response, 'data-selected-only-toggle="true"')
        self.assertContains(response, 'data-finding-selected="true"')

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

    def test_posted_musculoskeletal_emergency_findings_show_joint_and_compartment_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "acute_hot_swollen_joint",
                    "tense_compartment_or_pain_with_passive_stretch",
                    "recent_trauma",
                    "severe_pain",
                    "fever",
                    "neurologic_deficit",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Septic arthritis")
        self.assertContains(response, "Acute compartment syndrome")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")

    def test_posted_eye_and_obstetric_findings_show_orbital_and_preeclampsia_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "painful_eye_movement_or_proptosis",
                    "eye_pain_redness",
                    "fever",
                    "visual_disturbance",
                    "pregnancy_possible",
                    "preeclampsia_warning_features",
                    "ruq_pain",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Orbital cellulitis")
        self.assertContains(response, "Preeclampsia or eclampsia")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "ACOG")
        self.assertContains(response, "WHO")

    def test_posted_ent_airway_findings_show_deep_neck_and_airway_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "severe_sore_throat_drooling_or_stridor",
                    "trismus_muffled_voice_uvula_deviation",
                    "neck_stiffness_swelling_dysphagia",
                    "fever",
                    "respiratory_distress",
                    "severe_pain",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Epiglottitis")
        self.assertContains(response, "Peritonsillar abscess")
        self.assertContains(response, "Retropharyngeal abscess")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "MSD Manuals Professional")

    def test_posted_pediatric_metabolic_findings_show_hhs_intussusception_and_kawasaki(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "severe_hyperglycemia_dehydration_confusion",
                    "extreme_thirst_polyuria",
                    "altered_mental_status",
                    "intermittent_colicky_abdominal_pain_or_currant_jelly_stool",
                    "vomiting",
                    "persistent_fever_mucocutaneous_changes",
                    "fever",
                    "rash",
                    "eye_pain_redness",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hyperosmolar hyperglycemic state")
        self.assertContains(response, "Intussusception")
        self.assertContains(response, "Kawasaki disease")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "CDC")

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
