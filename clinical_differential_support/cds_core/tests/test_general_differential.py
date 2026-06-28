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
