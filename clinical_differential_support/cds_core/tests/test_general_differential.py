from unittest.mock import patch

from django.test import SimpleTestCase

from cds_core.differential_catalog import CATALOG_VERSION
from cds_core.general_differential import (
    evaluate_general_differential,
    get_general_differential_catalog_summary,
)


class GeneralDifferentialEngineTests(SimpleTestCase):
    def test_engine_uses_reviewed_runtime_catalog_loader(self):
        reviewed_runtime_catalog = {
            "catalog_version": "reviewed-runtime-test",
            "sources": {
                "reviewed_source": {
                    "publisher": "Reviewed Source",
                    "title": "Reviewed Runtime Test",
                    "url": "https://example.test/reviewed-runtime",
                }
            },
            "conditions": [
                {
                    "slug": "reviewed_runtime_only_condition",
                    "name_zh": "審核資料測試疾病",
                    "name_en": "Reviewed runtime only condition",
                    "system": "Test",
                    "urgency": "soon",
                    "summary_zh": "僅存在於 reviewed runtime catalog。",
                    "summary_en": "Exists only in the reviewed runtime catalog.",
                    "signals": {"reviewed_runtime_finding": 5},
                    "synonyms": ["reviewed runtime condition"],
                    "ask_next": ["確認 reviewed runtime loader。 / Confirm reviewed runtime loader."],
                    "source_ids": ["reviewed_source"],
                }
            ],
        }

        with patch(
            "cds_core.general_differential.get_general_differential_runtime_catalog",
            return_value=reviewed_runtime_catalog,
        ):
            summary = get_general_differential_catalog_summary()
            result = evaluate_general_differential(
                {
                    "query": "reviewed runtime condition",
                    "findings": ["reviewed_runtime_finding"],
                }
            )

        self.assertEqual(summary["catalog_version"], "reviewed-runtime-test")
        self.assertEqual(summary["runtime_source"], "reviewed runtime catalog")
        self.assertEqual(summary["condition_count"], 1)
        self.assertEqual(summary["source_count"], 1)
        self.assertEqual(result["coverage"]["catalog_version"], "reviewed-runtime-test")
        self.assertEqual(result["coverage"]["runtime_source"], "reviewed runtime catalog")
        self.assertEqual(result["results"][0]["slug"], "reviewed_runtime_only_condition")
        self.assertEqual(result["results"][0]["sources"][0]["publisher"], "Reviewed Source")

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
            CATALOG_VERSION,
        )

    def test_results_include_concise_next_action_summary(self):
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

        summary = result["concise_result_summary"]

        self.assertEqual(summary["primary_next_action"]["title_en"], "Safety first")
        self.assertEqual(summary["top_candidates"][0]["slug"], "acute_coronary_syndrome")
        self.assertEqual(len(summary["top_candidates"]), 3)
        self.assertGreaterEqual(len(summary["danger_checks"]), 1)
        self.assertTrue(summary["has_structured_findings"])

    def test_results_include_complaint_guided_intake_cards(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                ],
            }
        )

        intake = result["complaint_guided_intake"]

        self.assertEqual(intake["status"], "matched")
        self.assertEqual(intake["cards"][0]["complaint_id"], "cardiopulmonary")
        self.assertIn("Chest pain or dyspnea", intake["cards"][0]["title_en"])
        self.assertGreaterEqual(len(intake["cards"][0]["minimum_data_prompts"]), 3)
        self.assertIn("chest_pain", intake["cards"][0]["finding_shortcuts"])
        self.assertIn("dyspnea", intake["cards"][0]["finding_shortcuts"])

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
            ("first seizure", "first_seizure"),
            ("bell palsy", "bell_palsy"),
            ("atrial fibrillation", "atrial_fibrillation_or_arrhythmia"),
            ("infective endocarditis", "infective_endocarditis"),
            ("croup", "croup"),
            ("corneal ulcer contact lens", "corneal_abrasion_keratitis"),
            ("dental abscess", "dental_abscess"),
            ("diverticulitis", "diverticulitis"),
            ("hyponatremia", "hyponatremia"),
            ("genital herpes", "genital_herpes"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_next_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("acute cholecystitis", "acute_cholecystitis"),
            ("acute cholangitis", "acute_cholangitis"),
            ("c difficile colitis", "clostridioides_difficile_colitis"),
            ("inflammatory bowel disease flare", "inflammatory_bowel_disease_flare"),
            ("ischemic colitis", "ischemic_colitis"),
            ("retinal detachment", "retinal_detachment"),
            ("optic neuritis", "optic_neuritis"),
            ("uveitis", "uveitis"),
            ("mastoiditis", "mastoiditis"),
            ("lyme disease", "lyme_disease"),
            ("mpox", "mpox"),
            ("measles", "measles"),
            ("rsv infection", "rsv_infection"),
            ("alcohol withdrawal", "alcohol_withdrawal"),
            ("opioid overdose", "opioid_overdose"),
            ("stimulant toxicity", "stimulant_toxicity"),
            ("salicylate toxicity", "salicylate_toxicity"),
            ("sickle cell acute chest syndrome", "sickle_cell_acute_chest_syndrome"),
            ("sickle cell pain crisis", "sickle_cell_vaso_occlusive_crisis"),
            ("immune thrombocytopenia", "immune_thrombocytopenia"),
            ("multiple myeloma", "multiple_myeloma"),
            ("rheumatoid arthritis", "rheumatoid_arthritis"),
            ("polymyalgia rheumatica", "polymyalgia_rheumatica"),
            ("osteomyelitis", "osteomyelitis"),
            ("guillain barre syndrome", "guillain_barre_syndrome"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_specialty_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("cardiac tamponade", "cardiac_tamponade"),
            ("acute respiratory distress syndrome", "acute_respiratory_distress_syndrome"),
            ("pulmonary hypertension", "pulmonary_hypertension"),
            ("sarcoidosis", "sarcoidosis"),
            ("obstructive sleep apnea", "obstructive_sleep_apnea"),
            ("pulmonary fibrosis", "pulmonary_fibrosis"),
            ("glomerulonephritis", "glomerulonephritis"),
            ("nephrotic syndrome", "nephrotic_syndrome"),
            ("acute prostatitis", "acute_prostatitis"),
            ("benign prostatic hyperplasia", "benign_prostatic_hyperplasia"),
            ("endometriosis", "endometriosis"),
            ("polycystic ovary syndrome", "polycystic_ovary_syndrome"),
            ("primary dysmenorrhea", "primary_dysmenorrhea"),
            ("bacterial vaginosis", "bacterial_vaginosis"),
            ("vulvovaginal candidiasis", "vulvovaginal_candidiasis"),
            ("systemic lupus erythematosus", "systemic_lupus_erythematosus"),
            ("antiphospholipid syndrome", "antiphospholipid_syndrome"),
            ("ankylosing spondylitis", "ankylosing_spondylitis"),
            ("reactive arthritis", "reactive_arthritis"),
            ("fibromyalgia", "fibromyalgia"),
            ("osteoarthritis", "osteoarthritis"),
            ("cluster headache", "cluster_headache"),
            ("meniere disease", "meniere_disease"),
            ("cirrhosis", "cirrhosis"),
            ("functional constipation", "functional_constipation"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_abdominal_findings_add_focused_ask_next_before_condition_prompts(self):
        result = evaluate_general_differential(
            {"query": "", "findings": ["abdominal_pain", "fever", "vomiting"]}
        )

        focused_prompts = result["ask_next"][4:6]
        self.assertTrue(
            any("Abdominal or urinary context" in prompt for prompt in focused_prompts),
            focused_prompts,
        )
        self.assertLess(
            result["ask_next"].index(next(prompt for prompt in result["ask_next"] if "Abdominal or urinary context" in prompt)),
            result["ask_next"].index(result["results"][0]["ask_next"][0]),
        )

    def test_guided_follow_up_breaks_next_steps_into_ordered_actions(self):
        result = evaluate_general_differential(
            {"query": "", "findings": ["abdominal_pain", "fever", "vomiting"]}
        )

        guided = result["guided_follow_up"]

        self.assertEqual(
            [step["step_id"] for step in guided],
            ["safety", "context", "top_differential", "rerun"],
        )
        self.assertEqual(guided[0]["title_en"], "Safety first")
        self.assertEqual(guided[1]["title_en"], "Fill the highest-yield context")
        self.assertTrue(
            any("Abdominal or urinary context" in prompt for prompt in guided[1]["prompts"]),
            guided[1]["prompts"],
        )
        self.assertIn(result["results"][0]["slug"], guided[2]["related_condition_slugs"])
        self.assertGreaterEqual(len(guided[2]["prompts"]), 1)
        combined = " ".join(
            [step["instruction_en"] for step in guided]
            + [prompt for step in guided for prompt in step["prompts"]]
        ).lower()
        self.assertNotIn("diagnosis order", combined)
        self.assertNotIn("treatment order", combined)
        self.assertNotIn("medication order", combined)

    def test_final_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("multiple sclerosis", "multiple_sclerosis"),
            ("parkinson disease", "parkinson_disease"),
            ("dementia", "dementia_major_neurocognitive_disorder"),
            ("peripheral neuropathy", "peripheral_neuropathy"),
            ("carpal tunnel syndrome", "carpal_tunnel_syndrome"),
            ("myasthenia gravis", "myasthenia_gravis"),
            ("cerebral venous sinus thrombosis", "cerebral_venous_sinus_thrombosis"),
            ("intracerebral hemorrhage", "intracerebral_hemorrhage"),
            ("vertebral compression fracture", "vertebral_compression_fracture"),
            ("diabetic foot infection", "diabetic_foot_infection"),
            ("chronic kidney disease", "chronic_kidney_disease"),
            ("diabetes mellitus", "diabetes_mellitus"),
            ("hyperthyroidism", "hyperthyroidism"),
            ("vitamin b12 deficiency", "vitamin_b12_deficiency"),
            ("iron deficiency anemia", "iron_deficiency_anemia"),
            ("celiac disease", "celiac_disease"),
            ("irritable bowel syndrome", "irritable_bowel_syndrome"),
            ("inguinal hernia", "inguinal_hernia"),
            ("urinary incontinence", "urinary_incontinence"),
            ("uterine fibroids", "uterine_fibroids"),
            ("menopause transition", "menopause_transition"),
            ("urticaria", "urticaria"),
            ("allergic contact dermatitis", "allergic_contact_dermatitis"),
            ("adverse drug reaction", "adverse_drug_reaction"),
            ("chronic venous insufficiency", "chronic_venous_insufficiency"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_sixth_generalist_batch_adds_50_more_searchable_conditions(self):
        expectations = [
            ("cushing syndrome", "cushing_syndrome"),
            ("pituitary apoplexy", "pituitary_apoplexy"),
            ("pheochromocytoma", "pheochromocytoma"),
            ("diabetes insipidus", "diabetes_insipidus"),
            ("primary hyperparathyroidism", "primary_hyperparathyroidism"),
            ("hypoparathyroidism", "hypoparathyroidism"),
            ("renal artery stenosis", "renal_artery_stenosis"),
            ("polycystic kidney disease", "polycystic_kidney_disease"),
            ("interstitial nephritis", "interstitial_nephritis"),
            ("bladder cancer", "bladder_cancer"),
            ("renal cell carcinoma", "renal_cell_carcinoma"),
            ("achalasia", "achalasia"),
            ("gastroparesis", "gastroparesis"),
            ("small intestinal bacterial overgrowth", "small_intestinal_bacterial_overgrowth"),
            ("bronchiectasis", "bronchiectasis"),
            ("aspiration pneumonia", "aspiration_pneumonia"),
            ("lung abscess", "lung_abscess"),
            ("mitral regurgitation", "mitral_regurgitation"),
            ("mitral stenosis", "mitral_stenosis"),
            ("hypertrophic cardiomyopathy", "hypertrophic_cardiomyopathy"),
            ("supraventricular tachycardia", "supraventricular_tachycardia"),
            ("ventricular tachycardia", "ventricular_tachycardia"),
            ("normal pressure hydrocephalus", "normal_pressure_hydrocephalus"),
            ("amyotrophic lateral sclerosis", "amyotrophic_lateral_sclerosis"),
            ("huntington disease", "huntington_disease"),
            ("restless legs syndrome", "restless_legs_syndrome"),
            ("essential tremor", "essential_tremor"),
            ("somatic symptom disorder", "somatic_symptom_disorder"),
            ("adjustment disorder", "adjustment_disorder"),
            ("autism spectrum disorder", "autism_spectrum_disorder"),
            ("adhd", "attention_deficit_hyperactivity_disorder"),
            ("insomnia disorder", "insomnia_disorder"),
            ("dermatomyositis", "dermatomyositis"),
            ("polymyositis", "polymyositis"),
            ("mixed connective tissue disease", "mixed_connective_tissue_disease"),
            ("behcet disease", "behcet_disease"),
            ("dengue", "dengue"),
            ("malaria", "malaria"),
            ("typhoid fever", "typhoid_fever"),
            ("syphilis", "syphilis"),
            ("gonorrhea", "gonorrhea"),
            ("chlamydia", "chlamydia"),
            ("varicella", "varicella"),
            ("rosacea", "rosacea"),
            ("tinea corporis", "tinea_corporis"),
            ("impetigo", "impetigo"),
            ("hidradenitis suppurativa", "hidradenitis_suppurativa"),
            ("melanoma", "melanoma"),
            ("placenta previa", "placenta_previa"),
            ("postpartum hemorrhage", "postpartum_hemorrhage"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_eighth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("aortic stenosis", "aortic_stenosis"),
            ("dilated cardiomyopathy", "dilated_cardiomyopathy"),
            ("pertussis", "pertussis"),
            ("norovirus", "norovirus_gastroenteritis"),
            ("gastritis", "gastritis"),
            ("h pylori infection", "helicobacter_pylori_infection"),
            ("gestational diabetes", "gestational_diabetes"),
            ("hyperemesis gravidarum", "hyperemesis_gravidarum"),
            ("trichomoniasis", "trichomoniasis"),
            ("overactive bladder", "overactive_bladder"),
            ("pancreatic cancer", "pancreatic_cancer"),
            ("liver cancer", "liver_cancer"),
            ("stomach cancer", "stomach_cancer"),
            ("esophageal cancer", "esophageal_cancer"),
            ("endometrial cancer", "endometrial_cancer"),
            ("thyroid cancer", "thyroid_cancer"),
            ("squamous cell carcinoma", "squamous_cell_carcinoma_skin"),
            ("alopecia areata", "alopecia_areata"),
            ("vitiligo", "vitiligo"),
            ("dry eye", "dry_eye_disease"),
            ("cataract", "cataract"),
            ("macular degeneration", "age_related_macular_degeneration"),
            ("diabetic retinopathy", "diabetic_retinopathy"),
            ("hand foot mouth disease", "hand_foot_mouth_disease"),
            ("pertinent thyroid nodule", "thyroid_nodule"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_ninth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("osteoporosis", "osteoporosis"),
            ("blepharitis", "blepharitis"),
            ("chronic sinusitis", "chronic_sinusitis"),
            ("nosebleed", "epistaxis"),
            ("nasal polyps", "nasal_polyps"),
            ("otitis media with effusion", "otitis_media_with_effusion"),
            ("eustachian tube dysfunction", "eustachian_tube_dysfunction"),
            ("onychomycosis", "onychomycosis"),
            ("head lice", "pediculosis"),
            ("common warts", "warts"),
            ("athlete foot", "tinea_pedis"),
            ("folate deficiency", "folate_deficiency"),
            ("bipolar disorder", "bipolar_disorder"),
            ("testicular cancer", "testicular_cancer"),
            ("oral cancer", "oral_cancer"),
            ("erectile dysfunction", "erectile_dysfunction"),
            ("open angle glaucoma", "open_angle_glaucoma"),
            ("age related hearing loss", "age_related_hearing_loss"),
            ("tinnitus", "tinnitus"),
            ("chronic fatigue syndrome", "chronic_fatigue_syndrome"),
            ("sjogren disease", "sjogren_disease"),
            ("scleroderma", "scleroderma"),
            ("psoriatic arthritis", "psoriatic_arthritis"),
            ("atopic dermatitis", "atopic_dermatitis"),
            ("interstitial cystitis", "interstitial_cystitis_bladder_pain_syndrome"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_tenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("meningococcal disease", "meningococcal_disease"),
            ("tetanus", "tetanus"),
            ("rabies", "rabies"),
            ("zika virus disease", "zika_virus_disease"),
            ("chikungunya", "chikungunya"),
            ("west nile virus disease", "west_nile_virus_disease"),
            ("aplastic anemia", "aplastic_anemia"),
            ("disseminated intravascular coagulation", "disseminated_intravascular_coagulation"),
            ("thrombotic thrombocytopenic purpura", "thrombotic_thrombocytopenic_purpura"),
            ("hemolytic uremic syndrome", "hemolytic_uremic_syndrome"),
            ("polycythemia vera", "polycythemia_vera"),
            ("chronic myeloid leukemia", "chronic_myeloid_leukemia"),
            ("primary biliary cholangitis", "primary_biliary_cholangitis"),
            ("primary sclerosing cholangitis", "primary_sclerosing_cholangitis"),
            ("barrett esophagus", "barrett_esophagus"),
            ("anal cancer", "anal_cancer"),
            ("anorexia nervosa", "anorexia_nervosa"),
            ("bulimia nervosa", "bulimia_nervosa"),
            ("borderline personality disorder", "borderline_personality_disorder"),
            ("premenstrual syndrome", "premenstrual_syndrome"),
            ("pelvic organ prolapse", "pelvic_organ_prolapse"),
            ("infertility", "infertility"),
            ("pemphigus", "pemphigus"),
            ("plantar fasciitis", "plantar_fasciitis"),
            ("scoliosis", "scoliosis"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_eleventh_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("cystic fibrosis", "cystic_fibrosis"),
            ("alpha 1 antitrypsin deficiency", "alpha_1_antitrypsin_deficiency"),
            ("cerebral palsy", "cerebral_palsy"),
            ("spina bifida", "spina_bifida"),
            ("down syndrome", "down_syndrome"),
            ("fetal alcohol spectrum disorders", "fetal_alcohol_spectrum_disorders"),
            ("tourette syndrome", "tourette_syndrome"),
            ("narcolepsy", "narcolepsy"),
            ("graves disease", "graves_disease"),
            ("hashimoto disease", "hashimoto_disease"),
            ("adrenal insufficiency", "adrenal_insufficiency"),
            ("acromegaly", "acromegaly"),
            ("prolactinoma", "prolactinoma"),
            ("vulvodynia", "vulvodynia"),
            ("primary ovarian insufficiency", "primary_ovarian_insufficiency"),
            ("rotator cuff injury", "rotator_cuff_injury"),
            ("spinal stenosis", "spinal_stenosis"),
            ("bursitis", "bursitis"),
            ("tendinitis", "tendinitis"),
            ("paget disease of bone", "paget_disease_of_bone"),
            ("osteonecrosis", "osteonecrosis"),
            ("myelodysplastic syndromes", "myelodysplastic_syndromes"),
            ("essential thrombocythemia", "essential_thrombocythemia"),
            ("primary myelofibrosis", "primary_myelofibrosis"),
            ("muscular dystrophy", "muscular_dystrophy"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_twelfth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("wilson disease", "wilson_disease"),
            ("hemochromatosis", "hereditary_hemochromatosis"),
            ("fragile x syndrome", "fragile_x_syndrome"),
            ("marfan syndrome", "marfan_syndrome"),
            ("turner syndrome", "turner_syndrome"),
            ("klinefelter syndrome", "klinefelter_syndrome"),
            ("congenital adrenal hyperplasia", "congenital_adrenal_hyperplasia"),
            ("g6pd deficiency", "g6pd_deficiency"),
            ("hereditary spherocytosis", "hereditary_spherocytosis"),
            ("phenylketonuria", "phenylketonuria"),
            ("maple syrup urine disease", "maple_syrup_urine_disease"),
            ("galactosemia", "galactosemia"),
            ("achondroplasia", "achondroplasia"),
            ("neurofibromatosis", "neurofibromatosis"),
            ("tuberous sclerosis complex", "tuberous_sclerosis_complex"),
            ("ehlers danlos syndrome", "ehlers_danlos_syndrome"),
            ("noonan syndrome", "noonan_syndrome"),
            ("prader willi syndrome", "prader_willi_syndrome"),
            ("angelman syndrome", "angelman_syndrome"),
            ("rett syndrome", "rett_syndrome"),
            ("22q11.2 deletion syndrome", "twenty_two_q11_2_deletion_syndrome"),
            ("congenital hypothyroidism", "congenital_hypothyroidism"),
            ("tay sachs disease", "tay_sachs_disease"),
            ("gaucher disease", "gaucher_disease"),
            ("pompe disease", "pompe_disease"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_thirteenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("adenomyosis", "adenomyosis"),
            ("alcohol associated liver disease", "alcohol_associated_liver_disease"),
            ("sickle cell disease", "sickle_cell_disease"),
            ("otosclerosis", "otosclerosis"),
            ("mumps", "mumps"),
            ("rubella", "rubella"),
            ("molluscum contagiosum", "molluscum_contagiosum"),
            ("lymphedema", "lymphedema"),
            ("varicose veins", "varicose_veins"),
            ("anemia of chronic disease", "anemia_of_chronic_disease"),
            ("vestibular schwannoma", "vestibular_schwannoma"),
            ("complex regional pain syndrome", "complex_regional_pain_syndrome"),
            ("temporomandibular disorder", "temporomandibular_disorder"),
            ("plantar wart", "plantar_wart"),
            ("ingrown toenail", "ingrown_toenail"),
            ("pleural effusion", "pleural_effusion"),
            ("varicocele", "varicocele"),
            ("hydrocele", "hydrocele"),
            ("non hodgkin lymphoma", "non_hodgkin_lymphoma"),
            ("hodgkin lymphoma", "hodgkin_lymphoma"),
            ("noise induced hearing loss", "noise_induced_hearing_loss"),
            ("mastitis", "mastitis"),
            ("balanitis", "balanitis"),
            ("chalazion", "chalazion"),
            ("hordeolum", "hordeolum"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_fourteenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("histoplasmosis", "histoplasmosis"),
            ("coccidioidomycosis", "coccidioidomycosis"),
            ("toxoplasmosis", "toxoplasmosis"),
            ("giardiasis", "giardiasis"),
            ("pinworm infection", "pinworm_infection"),
            ("schistosomiasis", "schistosomiasis"),
            ("strongyloidiasis", "strongyloidiasis"),
            ("ascariasis", "ascariasis"),
            ("rocky mountain spotted fever", "rocky_mountain_spotted_fever"),
            ("chagas disease", "chagas_disease"),
            ("laryngitis", "laryngitis"),
            ("vocal cord paralysis", "vocal_cord_paralysis"),
            ("oral candidiasis", "oral_candidiasis"),
            ("pityriasis rosea", "pityriasis_rosea"),
            ("lichen planus", "lichen_planus"),
            ("pressure injury", "pressure_injury"),
            ("primary hyperaldosteronism", "primary_hyperaldosteronism"),
            ("amyloidosis", "amyloidosis"),
            ("acute rheumatic fever", "acute_rheumatic_fever"),
            ("rheumatic heart disease", "rheumatic_heart_disease"),
            ("iga vasculitis", "iga_vasculitis"),
            ("hydronephrosis", "hydronephrosis"),
            ("pyloric stenosis", "pyloric_stenosis"),
            ("necrotizing enterocolitis", "necrotizing_enterocolitis"),
            ("hirschsprung disease", "hirschsprung_disease"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_fifteenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("blastomycosis", "blastomycosis"),
            ("cryptococcosis", "cryptococcosis"),
            ("aspergillosis", "aspergillosis"),
            ("invasive candidiasis", "invasive_candidiasis"),
            ("pneumocystis pneumonia", "pneumocystis_pneumonia"),
            ("nontuberculous mycobacterial lung disease", "nontuberculous_mycobacterial_lung_disease"),
            ("hypokalemia", "hypokalemia"),
            ("botulism", "botulism"),
            ("plague", "plague"),
            ("anthrax", "anthrax"),
            ("brucellosis", "brucellosis"),
            ("leptospirosis", "leptospirosis"),
            ("hantavirus pulmonary syndrome", "hantavirus_pulmonary_syndrome"),
            ("ehrlichiosis", "ehrlichiosis"),
            ("anaplasmosis", "anaplasmosis"),
            ("babesiosis", "babesiosis"),
            ("tularemia", "tularemia"),
            ("q fever", "q_fever"),
            ("psittacosis", "psittacosis"),
            ("legionnaires disease", "legionnaires_disease"),
            ("nocardiosis", "nocardiosis"),
            ("mucormycosis", "mucormycosis"),
            ("leprosy", "leprosy"),
            ("cytomegalovirus infection", "cytomegalovirus_infection"),
            ("cryptosporidiosis", "cryptosporidiosis"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_sixteenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("cyclosporiasis", "cyclosporiasis"),
            ("amebiasis", "amebiasis"),
            ("taeniasis", "taeniasis"),
            ("hookworm infection", "hookworm_infection"),
            ("toxocariasis", "toxocariasis"),
            ("lymphatic filariasis", "lymphatic_filariasis"),
            ("onchocerciasis", "onchocerciasis"),
            ("cysticercosis", "cysticercosis"),
            ("echinococcosis", "echinococcosis"),
            ("paragonimiasis", "paragonimiasis"),
            ("clonorchiasis", "clonorchiasis"),
            ("fascioliasis", "fascioliasis"),
            ("trichinellosis", "trichinellosis"),
            ("campylobacter infection", "campylobacter_infection"),
            ("salmonella infection", "salmonella_infection"),
            ("shigellosis", "shigellosis"),
            ("listeriosis", "listeriosis"),
            ("cholera", "cholera"),
            ("yersiniosis", "yersiniosis"),
            ("vibriosis", "vibriosis"),
            ("rotavirus infection", "rotavirus_infection"),
            ("adenovirus infection", "adenovirus_infection"),
            ("fifth disease", "fifth_disease"),
            ("scarlet fever", "scarlet_fever"),
            ("roseola", "roseola"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_seventeenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("diphtheria", "diphtheria"),
            ("poliomyelitis", "poliomyelitis"),
            ("smallpox", "smallpox"),
            ("yellow fever", "yellow_fever"),
            ("japanese encephalitis", "japanese_encephalitis"),
            ("la crosse encephalitis", "la_crosse_encephalitis"),
            ("eastern equine encephalitis", "eastern_equine_encephalitis"),
            ("powassan virus disease", "powassan_virus_disease"),
            ("st louis encephalitis", "st_louis_encephalitis"),
            ("colorado tick fever", "colorado_tick_fever"),
            ("lymphocytic choriomeningitis", "lymphocytic_choriomeningitis"),
            ("ebola disease", "ebola_disease"),
            ("marburg virus disease", "marburg_virus_disease"),
            ("lassa fever", "lassa_fever"),
            ("crimean congo hemorrhagic fever", "crimean_congo_hemorrhagic_fever"),
            ("rift valley fever", "rift_valley_fever"),
            ("trichuriasis", "trichuriasis"),
            ("sporotrichosis", "sporotrichosis"),
            ("enterovirus d68", "enterovirus_d68"),
            ("hand foot and mouth disease", "hand_foot_and_mouth_disease"),
            ("melioidosis", "melioidosis"),
            ("tickborne relapsing fever", "tickborne_relapsing_fever"),
            ("epidemic typhus", "epidemic_typhus"),
            ("scrub typhus", "scrub_typhus"),
            ("middle east respiratory syndrome", "middle_east_respiratory_syndrome"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_eighteenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("glanders", "glanders"),
            ("rat bite fever", "rat_bite_fever"),
            ("cat scratch disease", "cat_scratch_disease"),
            ("actinomycosis", "actinomycosis"),
            ("whipple disease", "whipple_disease"),
            ("rickettsialpox", "rickettsialpox"),
            ("murine typhus", "murine_typhus"),
            ("borrelia miyamotoi disease", "borrelia_miyamotoi_disease"),
            ("oropouche virus disease", "oropouche_virus_disease"),
            ("mayaro virus disease", "mayaro_virus_disease"),
            ("toxoplasmic encephalitis", "toxoplasmic_encephalitis"),
            ("non tuberculous mycobacterial disease", "non_tuberculous_mycobacterial_disease"),
            ("haemophilus influenzae type b", "haemophilus_influenzae_type_b"),
            ("pneumococcal disease", "pneumococcal_disease"),
            ("talaromycosis", "talaromycosis"),
            ("paracoccidioidomycosis", "paracoccidioidomycosis"),
            ("chromoblastomycosis", "chromoblastomycosis"),
            ("mycetoma", "mycetoma"),
            ("buruli ulcer", "buruli_ulcer"),
            ("yaws", "yaws"),
            ("toxic shock syndrome", "toxic_shock_syndrome"),
            ("gas gangrene", "gas_gangrene"),
            ("methemoglobinemia", "methemoglobinemia"),
            ("decompression sickness", "decompression_sickness"),
            ("high altitude illness", "high_altitude_illness"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_nineteenth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("frostbite", "frostbite"),
            ("electrical injury", "electrical_injury"),
            ("acute radiation syndrome", "acute_radiation_syndrome"),
            ("smoke inhalation injury", "smoke_inhalation_injury"),
            ("major burn injury", "major_burn_injury"),
            ("drowning", "drowning"),
            ("caustic ingestion", "caustic_ingestion"),
            ("lead poisoning", "lead_poisoning"),
            ("acetaminophen poisoning", "acetaminophen_poisoning"),
            ("organophosphate poisoning", "organophosphate_carbamate_poisoning"),
            ("anticholinergic toxidrome", "anticholinergic_toxidrome"),
            ("cyanide poisoning", "cyanide_poisoning"),
            ("sedative hypnotic toxicity", "sedative_hypnotic_toxicity"),
            ("digoxin toxicity", "digoxin_toxicity"),
            ("lithium toxicity", "lithium_toxicity"),
            ("neuroleptic malignant syndrome", "neuroleptic_malignant_syndrome"),
            ("malignant hyperthermia", "malignant_hyperthermia"),
            ("acute porphyria", "acute_porphyria"),
            ("rhabdomyolysis", "rhabdomyolysis"),
            ("heparin induced thrombocytopenia", "heparin_induced_thrombocytopenia"),
            ("acute transfusion reaction", "acute_transfusion_reaction"),
            ("fat embolism syndrome", "fat_embolism_syndrome"),
            ("arterial gas embolism", "arterial_gas_embolism"),
            ("snakebite envenoming", "snakebite_envenoming"),
            ("acute arsenic poisoning", "acute_arsenic_poisoning"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_twentieth_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("hyphema", "hyphema"),
            ("central retinal artery occlusion", "central_retinal_artery_occlusion"),
            ("retinal vein occlusion", "retinal_vein_occlusion"),
            ("subconjunctival hemorrhage", "subconjunctival_hemorrhage"),
            ("ludwig angina", "ludwig_angina"),
            ("bacterial tracheitis", "bacterial_tracheitis"),
            ("cholesteatoma", "cholesteatoma"),
            ("idiopathic intracranial hypertension", "idiopathic_intracranial_hypertension"),
            ("insulinoma", "insulinoma"),
            ("erythema multiforme", "erythema_multiforme"),
            ("erythema nodosum", "erythema_nodosum"),
            ("dacryocystitis", "dacryocystitis"),
            ("scleritis", "scleritis"),
            ("cerumen impaction", "cerumen_impaction"),
            ("adhesive capsulitis", "adhesive_capsulitis"),
            ("lateral epicondylitis", "lateral_epicondylitis"),
            ("de quervain tenosynovitis", "de_quervain_tenosynovitis"),
            ("melasma", "melasma"),
            ("drug eruption", "drug_eruption"),
            ("hypogonadism", "hypogonadism"),
            ("paroxysmal nocturnal hemoglobinuria", "paroxysmal_nocturnal_hemoglobinuria"),
            ("autoimmune hemolytic anemia", "autoimmune_hemolytic_anemia"),
            ("superficial thrombophlebitis", "superficial_thrombophlebitis"),
            ("raynaud phenomenon", "raynaud_phenomenon"),
            ("granulomatosis with polyangiitis", "granulomatosis_with_polyangiitis"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_twenty_first_generalist_batch_adds_25_more_searchable_conditions(self):
        expectations = [
            ("vitreous hemorrhage", "vitreous_hemorrhage"),
            ("endophthalmitis", "endophthalmitis"),
            ("carcinoid syndrome", "carcinoid_syndrome"),
            ("hyperprolactinemia", "hyperprolactinemia"),
            ("ramsay hunt syndrome", "ramsay_hunt_syndrome"),
            ("sialolithiasis", "sialolithiasis"),
            ("acute parotitis", "acute_parotitis"),
            ("bullous pemphigoid", "bullous_pemphigoid"),
            ("lichen sclerosus", "lichen_sclerosus"),
            ("acanthosis nigricans", "acanthosis_nigricans"),
            ("takayasu arteritis", "takayasu_arteritis"),
            ("polyarteritis nodosa", "polyarteritis_nodosa"),
            ("microscopic polyangiitis", "microscopic_polyangiitis"),
            ("eosinophilic granulomatosis with polyangiitis", "eosinophilic_granulomatosis_with_polyangiitis"),
            ("hereditary angioedema", "hereditary_angioedema"),
            ("septic bursitis", "septic_bursitis"),
            ("preseptal cellulitis", "preseptal_cellulitis"),
            ("corneal foreign body", "corneal_foreign_body"),
            ("sudden sensorineural hearing loss", "sudden_sensorineural_hearing_loss"),
            ("aphthous stomatitis", "aphthous_stomatitis"),
            ("subacute thyroiditis", "subacute_thyroiditis"),
            ("autoimmune hepatitis", "autoimmune_hepatitis"),
            ("perianal abscess", "perianal_abscess"),
            ("pilonidal disease", "pilonidal_disease"),
            ("small bowel obstruction", "small_bowel_obstruction"),
        ]
        for query, slug in expectations:
            with self.subTest(query=query):
                match = evaluate_general_differential({"query": query, "findings": []})
                self.assertEqual(match["results"][0]["slug"], slug)

    def test_ranked_results_are_grouped_by_urgency(self):
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

        self.assertIn("result_groups", result)
        self.assertGreaterEqual(len(result["result_groups"]), 2)
        self.assertEqual(result["result_groups"][0]["urgency"], "emergent")
        self.assertGreaterEqual(result["result_groups"][0]["count"], 1)
        self.assertEqual(
            result["result_groups"][0]["candidates"][0]["slug"],
            "acute_coronary_syndrome",
        )
        self.assertLessEqual(len(result["result_groups"][0]["candidates"]), 3)

    def test_ruq_fever_pattern_prioritizes_acute_cholecystitis(self):
        result = evaluate_general_differential(
            {"query": "", "findings": ["ruq_pain", "fever", "vomiting"]}
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "acute_cholecystitis")
        self.assertIn("ruq_pain", top["matched_findings"])

    def test_substance_respiratory_depression_prioritizes_opioid_overdose(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "substance_use_concern",
                    "respiratory_distress",
                    "altered_mental_status",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "opioid_overdose")
        self.assertEqual(top["urgency"], "emergent")

    def test_results_include_action_checklist_for_next_steps(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": ["chest_pain", "dyspnea", "diaphoresis"],
            }
        )

        self.assertGreaterEqual(len(result["action_checklist"]), 4)
        self.assertIn("category_zh", result["action_checklist"][0])
        self.assertIn("instruction_en", result["action_checklist"][0])
        self.assertIn("action_items", result["results"][0])
        self.assertGreaterEqual(len(result["results"][0]["action_items"]), 3)
        combined = " ".join(
            item["instruction_en"] for item in result["action_checklist"]
        )
        self.assertIn("Re-run", combined)

    def test_results_include_filterable_source_provenance_summary(self):
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

        provenance = result["source_provenance"]

        self.assertGreaterEqual(provenance["unique_source_count"], 2)
        self.assertGreaterEqual(provenance["row_count"], 2)
        self.assertGreaterEqual(len(provenance["publisher_filters"]), 1)
        self.assertGreaterEqual(len(provenance["rows"]), 2)
        first_row = provenance["rows"][0]
        self.assertIn("candidate_slug", first_row)
        self.assertIn("publisher_slug", first_row)
        self.assertIn("url", first_row)
        self.assertTrue(first_row["url"].startswith("http"))
        publishers = {row["publisher"] for row in provenance["rows"]}
        self.assertIn(provenance["publisher_filters"][0]["publisher"], publishers)

    def test_results_include_secondary_candidate_filter_metadata(self):
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

        filters = result["secondary_candidate_filters"]

        self.assertGreaterEqual(filters["secondary_count"], 1)
        self.assertGreaterEqual(len(filters["urgency_filters"]), 1)
        self.assertGreaterEqual(len(filters["system_filters"]), 1)
        self.assertEqual(filters["urgency_filters"][0]["filter_type"], "urgency")
        self.assertEqual(filters["system_filters"][0]["filter_type"], "system")
        self.assertIn("filter_value", filters["urgency_filters"][0])
        self.assertIn("filter_value", filters["system_filters"][0])

    def test_results_include_candidate_scan_filter_metadata(self):
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

        filters = result["candidate_scan_filters"]

        self.assertGreaterEqual(filters["scan_count"], 1)
        self.assertGreaterEqual(len(filters["urgency_filters"]), 1)
        self.assertGreaterEqual(len(filters["system_filters"]), 1)
        self.assertEqual(filters["urgency_filters"][0]["filter_type"], "urgency")
        self.assertEqual(filters["system_filters"][0]["filter_type"], "system")
        self.assertIn("filter_value", filters["urgency_filters"][0])
        self.assertIn("filter_value", filters["system_filters"][0])

    def test_results_include_compact_brief_for_scan_first_layout(self):
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

        brief = result["results_brief"]

        self.assertEqual(brief["top_candidate_name_en"], "Acute coronary syndrome")
        self.assertEqual(brief["top_urgency"], "emergent")
        self.assertEqual(brief["primary_result_count"], 3)
        self.assertEqual(brief["secondary_result_count"], len(result["results"]) - 3)
        self.assertEqual(brief["next_step_title_en"], "Safety first")
        self.assertIn("Re-check ABCs", brief["next_step_instruction_en"])
        self.assertTrue(brief["has_more_candidates"])

    def test_results_include_patient_workflow_for_step_by_step_case_review(self):
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

        workflow = result["patient_workflow"]

        self.assertEqual(workflow["status"], "ready_for_stepwise_review")
        self.assertEqual(workflow["risk_gate"], "emergent_leader_present")
        self.assertEqual(workflow["selected_finding_count"], 4)
        self.assertEqual(
            [step["step_id"] for step in workflow["steps"]],
            [
                "rule_out_immediate_danger",
                "complete_missing_context",
                "compare_leading_candidates",
                "handoff_or_rerun",
            ],
        )
        self.assertEqual(workflow["steps"][0]["title_en"], "Rule out immediate danger")
        self.assertIn(
            "Acute coronary syndrome",
            workflow["steps"][2]["candidate_names_en"],
        )
        self.assertIn("Acute coronary syndrome", workflow["handoff_summary_en"])
        combined = " ".join(
            [workflow["handoff_summary_en"]]
            + [step["instruction_en"] for step in workflow["steps"]]
        ).lower()
        self.assertNotIn("diagnosis order", combined)
        self.assertNotIn("treatment order", combined)
        self.assertNotIn("medication order", combined)

    def test_sparse_input_workflow_tells_user_minimum_data_to_collect(self):
        result = evaluate_general_differential({"query": "", "findings": []})

        workflow = result["patient_workflow"]

        self.assertEqual(workflow["status"], "needs_structured_findings")
        self.assertEqual(workflow["risk_gate"], "insufficient_input")
        self.assertTrue(workflow["needs_minimum_data"])
        self.assertEqual(workflow["top_candidate_count"], 0)
        self.assertGreaterEqual(len(workflow["minimum_data_items"]), 5)
        minimum_labels = [item["label_en"] for item in workflow["minimum_data_items"]]
        self.assertIn("Chief complaint and onset", minimum_labels)
        self.assertIn("Vitals and stability", minimum_labels)
        self.assertIn("Red flags", minimum_labels)
        self.assertIn("Pertinent positives and negatives", minimum_labels)
        self.assertIn("Update findings and re-run", minimum_labels)
        self.assertIn("Not enough structured data", workflow["handoff_summary_en"])

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

    def test_seizure_activity_prioritizes_first_seizure_safety_review(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "seizure_activity_or_postictal_state",
                    "altered_mental_status",
                    "recent_trauma",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "first_seizure")
        self.assertEqual(top["urgency"], "emergent")
        self.assertIn("seizure_activity_or_postictal_state", top["matched_findings"])

    def test_palpitations_with_syncope_prioritizes_arrhythmia_review(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": ["palpitations", "syncope", "dyspnea"],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "atrial_fibrillation_or_arrhythmia")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("palpitations", top["matched_findings"])

    def test_barking_cough_stridor_prioritizes_croup(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "barking_cough_or_stridor",
                    "respiratory_distress",
                    "fever",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "croup")
        self.assertIn("barking_cough_or_stridor", top["matched_findings"])

    def test_eye_pain_contact_lens_prioritizes_corneal_keratitis_review(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": [
                    "eye_pain_redness",
                    "eye_trauma_or_contact_lens",
                    "visual_disturbance",
                ],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "corneal_abrasion_keratitis")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("eye_trauma_or_contact_lens", top["matched_findings"])

    def test_unilateral_facial_weakness_surfaces_bell_palsy_after_stroke_check(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": ["unilateral_facial_weakness"],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "bell_palsy")
        self.assertIn("unilateral_facial_weakness", top["matched_findings"])

    def test_dental_pain_swelling_prioritizes_dental_abscess_review(self):
        result = evaluate_general_differential(
            {
                "query": "",
                "findings": ["dental_pain_or_facial_swelling", "fever", "severe_pain"],
            }
        )

        top = result["results"][0]
        self.assertEqual(top["slug"], "dental_abscess")
        self.assertEqual(top["urgency"], "urgent")
        self.assertIn("dental_pain_or_facial_swelling", top["matched_findings"])

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
