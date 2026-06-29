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
            "general-differential-starter-2026-06-29",
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
            ("skin abscess", "skin_abscess"),
            ("shingles", "herpes_zoster"),
            ("stevens-johnson syndrome", "stevens_johnson_syndrome_ten"),
            ("pericarditis", "acute_pericarditis_myocarditis"),
            ("myocarditis", "acute_pericarditis_myocarditis"),
            ("acute limb ischemia", "acute_limb_ischemia"),
            ("mesenteric ischemia", "acute_mesenteric_ischemia"),
            ("carbon monoxide poisoning", "carbon_monoxide_poisoning"),
            ("septic arthritis", "septic_arthritis"),
            ("compartment syndrome", "acute_compartment_syndrome"),
            ("orbital cellulitis", "orbital_cellulitis"),
            ("preeclampsia", "preeclampsia_eclampsia"),
            ("epiglottitis", "epiglottitis"),
            ("peritonsillar abscess", "peritonsillar_abscess"),
            ("retropharyngeal abscess", "retropharyngeal_abscess"),
            ("hyperosmolar hyperglycemic state", "hyperosmolar_hyperglycemic_state"),
            ("intussusception", "intussusception"),
            ("kawasaki disease", "kawasaki_disease"),
            ("acute otitis media", "acute_otitis_media"),
            ("otitis externa", "acute_otitis_externa"),
            ("acute sinusitis", "acute_sinusitis"),
            ("strep throat", "streptococcal_pharyngitis"),
            ("infectious mononucleosis", "infectious_mononucleosis"),
            ("allergic rhinitis", "allergic_rhinitis"),
            ("benign paroxysmal positional vertigo", "benign_paroxysmal_positional_vertigo"),
            ("vestibular neuritis", "vestibular_neuritis_labyrinthitis"),
            ("acute gout flare", "acute_gout_flare"),
            ("cauda equina syndrome", "cauda_equina_syndrome"),
            ("dehydration", "dehydration_volume_depletion"),
            ("orthostatic syncope", "vasovagal_orthostatic_syncope"),
            ("lumbar radiculopathy", "low_back_pain_radiculopathy"),
            ("allergic conjunctivitis", "allergic_conjunctivitis"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_ear_pain_fever_prioritizes_acute_otitis_media(self):
        result = evaluate_general_differential(
            {"query": "", "findings": ["ear_pain", "fever"]}
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_otitis_media")
        self.assertIn("ear_pain", top["matched_findings"])

    def test_sore_throat_exudate_prioritizes_streptococcal_pharyngitis(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "sore_throat",
                    "fever",
                    "tonsillar_exudate_or_tender_nodes",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "streptococcal_pharyngitis")
        self.assertIn("tonsillar_exudate_or_tender_nodes", top["matched_findings"])

    def test_positional_vertigo_prioritizes_bppv(self):
        result = evaluate_general_differential(
            {"query": "", "findings": ["vertigo", "positional_vertigo"]}
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "benign_paroxysmal_positional_vertigo")
        self.assertIn("positional_vertigo", top["matched_findings"])

    def test_back_pain_bladder_features_prioritizes_cauda_equina(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "low_back_pain",
                    "bladder_bowel_dysfunction",
                    "saddle_anesthesia",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "cauda_equina_syndrome")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("saddle_anesthesia", top["matched_findings"])

    def test_orthostatic_lightheaded_syncope_surfaces_orthostatic_vasovagal(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "syncope",
                    "orthostatic_lightheadedness",
                    "poor_oral_intake_dehydration",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "vasovagal_orthostatic_syncope")
        self.assertIn("orthostatic_lightheadedness", top["matched_findings"])

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

    def test_mucosal_sloughing_rash_prioritizes_sjs_ten(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "rash",
                    "mucosal_lesions",
                    "skin_sloughing_or_blistering",
                    "new_medication_exposure",
                    "fever",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "stevens_johnson_syndrome_ten")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("mucosal_lesions", top["matched_findings"])

    def test_dermatomal_vesicles_and_pain_prioritizes_herpes_zoster(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "vesicular_dermatomal_rash",
                    "severe_pain",
                    "eye_pain_redness",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "herpes_zoster")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("vesicular_dermatomal_rash", top["matched_findings"])

    def test_positional_pleuritic_chest_pain_prioritizes_pericarditis_myocarditis(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "positional_pleuritic_chest_pain",
                    "pleuritic_pain",
                    "dyspnea",
                    "tachycardia",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_pericarditis_myocarditis")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("positional_pleuritic_chest_pain", top["matched_findings"])
        self.assertIn("Merck Manual Professional", [source["publisher"] for source in top["sources"]])

    def test_acute_limb_pain_pallor_pulselessness_prioritizes_limb_ischemia(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "acute_limb_pain_pallor_pulselessness",
                    "severe_pain",
                    "neurologic_deficit",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_limb_ischemia")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("acute_limb_pain_pallor_pulselessness", top["matched_findings"])

    def test_acute_hot_swollen_joint_prioritizes_septic_arthritis(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "acute_hot_swollen_joint",
                    "fever",
                    "severe_pain",
                    "immunocompromised",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "septic_arthritis")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("acute_hot_swollen_joint", top["matched_findings"])
        self.assertIn("Merck Manual Professional", [source["publisher"] for source in top["sources"]])

    def test_passive_stretch_pain_after_trauma_prioritizes_compartment_syndrome(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "tense_compartment_or_pain_with_passive_stretch",
                    "recent_trauma",
                    "severe_pain",
                    "neurologic_deficit",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_compartment_syndrome")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn(
            "tense_compartment_or_pain_with_passive_stretch",
            top["matched_findings"],
        )
        self.assertIn("Merck Manual Professional", [source["publisher"] for source in top["sources"]])

    def test_painful_eye_movement_proptosis_prioritizes_orbital_cellulitis(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "painful_eye_movement_or_proptosis",
                    "eye_pain_redness",
                    "fever",
                    "visual_disturbance",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "orbital_cellulitis")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("painful_eye_movement_or_proptosis", top["matched_findings"])
        publishers = [source["publisher"] for source in top["sources"]]
        self.assertIn("MSD Manuals Professional", publishers)
        self.assertIn("Royal Children's Hospital Melbourne", publishers)

    def test_pain_out_of_proportion_prioritizes_acute_mesenteric_ischemia(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "pain_out_of_proportion_to_exam",
                    "abdominal_pain",
                    "severe_pain",
                    "vomiting",
                    "bloody_diarrhea",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_mesenteric_ischemia")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("pain_out_of_proportion_to_exam", top["matched_findings"])
        self.assertIn("World Society of Emergency Surgery", [source["publisher"] for source in top["sources"]])

    def test_combustion_exposure_with_multiple_patients_prioritizes_carbon_monoxide(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "carbon_monoxide_or_combustion_exposure",
                    "multiple_people_same_symptoms",
                    "altered_mental_status",
                    "syncope",
                    "vomiting",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "carbon_monoxide_poisoning")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("carbon_monoxide_or_combustion_exposure", top["matched_findings"])
        self.assertIn("CDC", [source["publisher"] for source in top["sources"]])

    def test_pregnancy_headache_vision_ruq_prioritizes_preeclampsia_eclampsia(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "pregnancy_possible",
                    "preeclampsia_warning_features",
                    "visual_disturbance",
                    "ruq_pain",
                    "severe_pain",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "preeclampsia_eclampsia")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("preeclampsia_warning_features", top["matched_findings"])
        publishers = [source["publisher"] for source in top["sources"]]
        self.assertIn("ACOG", publishers)
        self.assertIn("WHO", publishers)

    def test_sore_throat_drooling_stridor_prioritizes_epiglottitis(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "severe_sore_throat_drooling_or_stridor",
                    "fever",
                    "respiratory_distress",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "epiglottitis")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("severe_sore_throat_drooling_or_stridor", top["matched_findings"])
        self.assertIn("Merck Manual Professional", [source["publisher"] for source in top["sources"]])

    def test_trismus_muffled_voice_prioritizes_peritonsillar_abscess(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "trismus_muffled_voice_uvula_deviation",
                    "fever",
                    "severe_pain",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "peritonsillar_abscess")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("trismus_muffled_voice_uvula_deviation", top["matched_findings"])
        self.assertIn("MSD Manuals Professional", [source["publisher"] for source in top["sources"]])

    def test_neck_stiffness_dysphagia_prioritizes_retropharyngeal_abscess(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "neck_stiffness_swelling_dysphagia",
                    "fever",
                    "respiratory_distress",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "retropharyngeal_abscess")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("neck_stiffness_swelling_dysphagia", top["matched_findings"])

    def test_severe_hyperglycemia_dehydration_confusion_prioritizes_hhs(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "severe_hyperglycemia_dehydration_confusion",
                    "extreme_thirst_polyuria",
                    "altered_mental_status",
                    "hemodynamic_instability",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "hyperosmolar_hyperglycemic_state")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("severe_hyperglycemia_dehydration_confusion", top["matched_findings"])

    def test_colicky_abdominal_pain_currant_jelly_stool_prioritizes_intussusception(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "intermittent_colicky_abdominal_pain_or_currant_jelly_stool",
                    "abdominal_pain",
                    "vomiting",
                    "altered_mental_status",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "intussusception")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn(
            "intermittent_colicky_abdominal_pain_or_currant_jelly_stool",
            top["matched_findings"],
        )

    def test_persistent_fever_mucocutaneous_changes_prioritizes_kawasaki(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "persistent_fever_mucocutaneous_changes",
                    "fever",
                    "rash",
                    "eye_pain_redness",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "kawasaki_disease")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("persistent_fever_mucocutaneous_changes", top["matched_findings"])
        self.assertIn("CDC", [source["publisher"] for source in top["sources"]])
