from django.test import SimpleTestCase

from cds_core.general_differential import evaluate_general_differential


class GeneralDifferentialEngineTests(SimpleTestCase):
    def test_acute_coronary_syndrome_ranks_first_for_classic_chest_pain_pattern(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_coronary_syndrome")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("chest_pain", top["matched_findings"])
        self.assertIn("radiating_arm_jaw_pain", top["matched_findings"])
        self.assertGreaterEqual(top["score"], 12)
        self.assertTrue(top["sources"])
        self.assertIn("ECG", " ".join(top["ask_next"]))
        self.assertEqual(
            result["coverage"]["catalog_version"],
            "general-differential-starter-2026-06-28",
        )

    def test_sepsis_ranks_first_for_infectious_shock_pattern(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "fever",
                    "altered_mental_status",
                    "tachycardia",
                    "dyspnea",
                    "hemodynamic_instability",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "sepsis")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("altered_mental_status", top["matched_findings"])
        self.assertIn("CDC", [source["publisher"] for source in top["sources"]])

    def test_sparse_input_returns_stepwise_ask_next_prompts_and_limits(self):
        result = evaluate_general_differential({"query": "", "findings": []})

        self.assertEqual(result["results"], [])
        self.assertGreaterEqual(len(result["ask_next"]), 4)
        self.assertIn("starter catalog", result["coverage"]["limitation_en"])
        self.assertIn("不是完整疾病資料庫", result["coverage"]["limitation_zh"])

    def test_text_search_can_surface_named_condition_without_structured_findings(self):
        result = evaluate_general_differential({"query": "stroke", "findings": []})

        top = result["results"][0]
        self.assertEqual(top["slug"], "stroke_tia")
        self.assertTrue(top["matched_text_search"])
        self.assertEqual(top["urgency"], "emergent")

    def test_catalog_has_broad_cross_system_seed_conditions(self):
        result = evaluate_general_differential({"query": "", "findings": []})

        self.assertGreaterEqual(result["coverage"]["condition_count"], 50)
        expectations = [
            ("migraine", "migraine"),
            ("dvt", "deep_vein_thrombosis"),
            ("pancreatitis", "acute_pancreatitis"),
            ("thyroid storm", "thyroid_storm"),
            ("suicide risk", "suicide_self_harm_risk"),
            ("heat stroke", "heat_stroke"),
            ("febrile neutropenia", "febrile_neutropenia"),
            ("tumor lysis", "tumor_lysis_syndrome"),
            ("spinal cord compression", "metastatic_spinal_cord_compression"),
            ("hypercalcemia of malignancy", "hypercalcemia_of_malignancy"),
            ("acute leukemia", "acute_leukemia"),
            ("urinary retention", "acute_urinary_retention"),
            ("pelvic inflammatory disease", "pelvic_inflammatory_disease"),
            ("tubo ovarian abscess", "tubo_ovarian_abscess"),
            ("acute abnormal uterine bleeding", "acute_abnormal_uterine_bleeding"),
            ("first episode psychosis", "acute_psychosis"),
            ("mania", "mania_or_hypomania"),
            ("eating disorder", "eating_disorder_medical_risk"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_recent_cancer_treatment_fever_prioritizes_febrile_neutropenia(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "fever",
                    "recent_cancer_treatment",
                    "immunocompromised",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "febrile_neutropenia")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("recent_cancer_treatment", top["matched_findings"])

    def test_inability_to_void_prioritizes_acute_urinary_retention(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "inability_to_void",
                    "severe_pain",
                    "abdominal_pain",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_urinary_retention")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("inability_to_void", top["matched_findings"])

    def test_pelvic_pain_fever_discharge_prioritizes_pid_and_toa(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "pelvic_pain",
                    "fever",
                    "vaginal_discharge",
                    "cervical_motion_tenderness",
                ],
            }
        )

        self.assertEqual(result["results"][0]["slug"], "tubo_ovarian_abscess")
        slugs = [entry["slug"] for entry in result["results"][:5]]
        self.assertIn("tubo_ovarian_abscess", slugs)
        self.assertIn("pelvic_inflammatory_disease", slugs)
        self.assertIn("cervical_motion_tenderness", result["results"][0]["matched_findings"])

    def test_vaginal_bleeding_instability_prioritizes_acute_abnormal_uterine_bleeding(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "vaginal_bleeding",
                    "hemodynamic_instability",
                    "syncope",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_abnormal_uterine_bleeding")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("vaginal_bleeding", top["matched_findings"])

    def test_suicidal_ideation_and_self_harm_prioritizes_safety_risk(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "suicidal_ideation",
                    "self_harm_behavior",
                    "substance_use_concern",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "suicide_self_harm_risk")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("suicidal_ideation", top["matched_findings"])

    def test_hallucinations_agitation_prioritizes_acute_psychosis(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "hallucinations_delusions",
                    "severe_agitation",
                    "substance_use_concern",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_psychosis")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("hallucinations_delusions", top["matched_findings"])

    def test_decreased_sleep_and_risky_behavior_prioritizes_mania(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "decreased_need_for_sleep",
                    "risky_impulsive_behavior",
                    "severe_agitation",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "mania_or_hypomania")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("decreased_need_for_sleep", top["matched_findings"])
