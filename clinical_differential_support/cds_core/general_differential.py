"""General differential evaluator for the broad clinician workbench."""

from __future__ import annotations

import re
from typing import Any

from .differential_catalog import DEFAULT_ASK_NEXT, FINDING_GROUPS, URGENCY_ORDER
from .differential_catalog_data import get_general_differential_runtime_catalog

FOCUSED_ASK_NEXT_CONTEXTS = [
    (
        {
            "chest_pain",
            "dyspnea",
            "pleuritic_pain",
            "orthopnea_edema",
            "palpitations",
            "syncope",
            "tachycardia",
        },
        "心肺脈絡：確認血氧、血壓、心電圖風險、運動耐受、胸痛特徵與是否有休克或低氧。 / Cardiopulmonary context: confirm oxygenation, BP, ECG risk, exertional tolerance, chest-pain features, and shock or hypoxemia.",
    ),
    (
        {
            "abdominal_pain",
            "ruq_pain",
            "rlq_pain",
            "llq_pain",
            "vomiting",
            "gi_bleeding",
            "bloody_diarrhea",
            "constipation_obstipation",
            "dysuria",
            "flank_pain",
            "decreased_urine_output",
        },
        "腹部/泌尿脈絡：確認疼痛位置、腹膜刺激、排便排尿、嘔吐/血便、懷孕可能、脫水與是否需影像或尿檢。 / Abdominal or urinary context: confirm pain location, peritoneal signs, bowel/urinary symptoms, vomiting or bleeding, pregnancy possibility, dehydration, and imaging or urinalysis need.",
    ),
    (
        {
            "neurologic_deficit",
            "unilateral_weakness",
            "speech_vision_changes",
            "thunderclap_headache",
            "neck_stiffness",
            "seizure_activity_or_postictal_state",
            "vertigo",
        },
        "神經脈絡：確認最後正常時間、局灶神經缺損、雷擊樣頭痛、癲癇後狀態、頸僵硬與是否需急症神經評估。 / Neurologic context: confirm last-known-well, focal deficits, thunderclap headache, postictal state, neck stiffness, and urgent neurologic review need.",
    ),
    (
        {
            "fever",
            "rash",
            "immunocompromised",
            "rapidly_spreading_skin_infection",
            "mucosal_lesions",
            "purulent_skin_lesion",
        },
        "感染/皮膚脈絡：確認發燒時程、暴露接觸、免疫狀態、皮疹型態、感染管制與敗血症警訊。 / Infectious or skin context: confirm fever timeline, exposure/contact, immune status, rash morphology, infection-control needs, and sepsis red flags.",
    ),
    (
        {
            "pelvic_pain",
            "vaginal_bleeding",
            "early_pregnancy_bleeding",
            "vaginal_discharge",
            "cervical_motion_tenderness",
            "pregnancy_possible",
        },
        "婦產脈絡：確認妊娠狀態、出血量、骨盆痛位置、分泌物、發燒、性健康風險與是否需急症婦科評估。 / Gynecologic context: confirm pregnancy status, bleeding amount, pelvic pain location, discharge, fever, sexual health risk, and urgent gynecology review need.",
    ),
    (
        {
            "suicidal_ideation",
            "self_harm_behavior",
            "hallucinations_delusions",
            "severe_agitation",
            "substance_use_concern",
        },
        "精神/毒物脈絡：先確認自傷/他傷、譫妄、物質或藥物暴露、生命徵象與是否需立即安全處置。 / Mental health or toxicology context: first check self/other-harm risk, delirium, substance or medication exposure, vitals, and immediate safety action need.",
    ),
]

COMPLAINT_GUIDED_INTAKE_PRESETS = [
    {
        "complaint_id": "cardiopulmonary",
        "display_order": 10,
        "title_zh": "胸痛或呼吸困難",
        "title_en": "Chest pain or dyspnea",
        "trigger_findings": {
            "chest_pain",
            "dyspnea",
            "pleuritic_pain",
            "positional_pleuritic_chest_pain",
            "palpitations",
            "syncope",
            "orthopnea_edema",
            "hemoptysis",
        },
        "query_keywords": ("chest pain", "dyspnea", "shortness of breath", "breathless"),
        "minimum_data_prompts": [
            "先補生命徵象、血氧、血壓、心電圖風險與休克或低氧線索。 / Add vitals, oxygenation, BP, ECG risk, and shock or hypoxemia clues first.",
            "釐清開始時間、誘發因子、運動相關、胸膜性/姿勢性、手臂或下顎放射痛。 / Clarify onset, triggers, exertional pattern, pleuritic or positional features, and arm or jaw radiation.",
            "補 PE/DVT、感染、心衰、氣胸、創傷、藥物或物質使用等會改變急迫性的風險。 / Add PE/DVT, infection, heart failure, pneumothorax, trauma, medication, or substance risks that change urgency.",
        ],
        "finding_shortcuts": [
            "chest_pain",
            "dyspnea",
            "diaphoresis",
            "radiating_arm_jaw_pain",
            "syncope",
            "palpitations",
        ],
    },
    {
        "complaint_id": "abdominal_urinary",
        "display_order": 20,
        "title_zh": "腹痛、嘔吐或泌尿症狀",
        "title_en": "Abdominal, vomiting, or urinary symptoms",
        "trigger_findings": {
            "abdominal_pain",
            "ruq_pain",
            "rlq_pain",
            "llq_pain",
            "vomiting",
            "gi_bleeding",
            "bloody_diarrhea",
            "constipation_obstipation",
            "dysuria",
            "flank_pain",
        },
        "query_keywords": ("abdominal pain", "vomiting", "dysuria", "flank pain", "bloody diarrhea"),
        "minimum_data_prompts": [
            "先定位疼痛、病程、腹膜刺激徵象、嘔吐/排便/排氣與脫水或血流不穩。 / First localize pain, tempo, peritoneal signs, vomiting, stool/flatus, dehydration, and instability.",
            "補懷孕可能、泌尿症狀、血便/黑便、近期抗生素、手術史與疝氣風險。 / Add pregnancy possibility, urinary symptoms, bleeding, antibiotics, surgery history, and hernia risk.",
            "確認是否需要影像、尿液、血液檢查或外科/婦產/泌尿急評估。 / Decide whether imaging, urine, labs, or surgical/gynecology/urology review is needed.",
        ],
        "finding_shortcuts": [
            "abdominal_pain",
            "vomiting",
            "constipation_obstipation",
            "gi_bleeding",
            "dysuria",
            "pregnancy_possible",
        ],
    },
    {
        "complaint_id": "neuro_headache",
        "display_order": 30,
        "title_zh": "頭痛、眩暈或神經症狀",
        "title_en": "Headache, vertigo, or neurologic symptoms",
        "trigger_findings": {
            "headache",
            "neurologic_deficit",
            "unilateral_weakness",
            "speech_vision_changes",
            "thunderclap_headache",
            "seizure_activity_or_postictal_state",
            "vertigo",
        },
        "query_keywords": ("headache", "weakness", "speech", "vision", "seizure", "vertigo"),
        "minimum_data_prompts": [
            "先補 last-known-well、神經缺損、意識、血糖、血壓與突發最痛時間。 / Add last-known-well, focal deficits, mental status, glucose, BP, and thunderclap timing.",
            "釐清外傷、抗凝、發燒頸僵、免疫低下、癌症、妊娠/產後與 50 歲後新發。 / Check trauma, anticoagulation, fever/neck stiffness, immune risk, cancer, pregnancy/postpartum, and new onset after 50.",
            "確認是否需要中風、癲癇、感染或出血急症路徑。 / Decide if stroke, seizure, infection, or hemorrhage emergency pathways apply.",
        ],
        "finding_shortcuts": [
            "headache",
            "thunderclap_headache",
            "neurologic_deficit",
            "speech_vision_changes",
            "seizure_activity_or_postictal_state",
            "vertigo",
        ],
    },
    {
        "complaint_id": "fever_rash",
        "display_order": 40,
        "title_zh": "發燒、皮疹或感染",
        "title_en": "Fever, rash, or infection",
        "trigger_findings": {
            "fever",
            "rash",
            "mucosal_lesions",
            "rapidly_spreading_skin_infection",
            "purulent_skin_lesion",
            "immunocompromised",
        },
        "query_keywords": ("fever", "rash", "infection", "cellulitis", "mucosal lesion"),
        "minimum_data_prompts": [
            "先補敗血症警訊、免疫狀態、暴露史、旅遊、接觸者與感染管制需求。 / Add sepsis red flags, immune status, exposure, travel, contacts, and infection-control needs.",
            "描述皮疹形態、分布、黏膜、水泡/脫皮、紫斑、疼痛程度與新藥。 / Describe morphology, distribution, mucosa, blisters/sloughing, purpura, pain, and new medications.",
            "確認是否需要隔離、培養、影像、抗菌路徑或皮膚科/感染科急評估。 / Decide on isolation, cultures, imaging, antimicrobial pathway, or dermatology/infectious review.",
        ],
        "finding_shortcuts": [
            "fever",
            "rash",
            "mucosal_lesions",
            "skin_sloughing_or_blistering",
            "new_medication_exposure",
            "immunocompromised",
        ],
    },
    {
        "complaint_id": "eye_ent",
        "display_order": 50,
        "title_zh": "眼、耳鼻喉或口腔症狀",
        "title_en": "Eye, ENT, or oral symptoms",
        "trigger_findings": {
            "eye_pain_redness",
            "visual_disturbance",
            "ear_pain",
            "hearing_loss_tinnitus",
            "severe_sore_throat_drooling_or_stridor",
            "neck_stiffness_swelling_dysphagia",
        },
        "query_keywords": ("eye pain", "red eye", "vision loss", "ear pain", "hearing loss", "sore throat"),
        "minimum_data_prompts": [
            "先補視力、眼球轉動痛/突出、外傷、隱形眼鏡、聽力、吞嚥與呼吸道警訊。 / Add vision, painful eye movement/proptosis, trauma, contact lens, hearing, swallowing, and airway red flags.",
            "釐清發燒、分泌物、臉/牙源感染、鼻竇症狀、耳水泡或神經症狀。 / Clarify fever, discharge, facial/dental source, sinus symptoms, ear vesicles, or neurologic signs.",
            "確認是否需要眼科、ENT、牙科或急診 airway 路徑。 / Decide if ophthalmology, ENT, dental, or emergency airway pathway is needed.",
        ],
        "finding_shortcuts": [
            "eye_pain_redness",
            "visual_disturbance",
            "ear_pain",
            "hearing_loss_tinnitus",
            "dental_pain_or_facial_swelling",
            "severe_sore_throat_drooling_or_stridor",
        ],
    },
    {
        "complaint_id": "trauma_toxin",
        "display_order": 60,
        "title_zh": "外傷、暴露或中毒",
        "title_en": "Trauma, exposure, or toxicology",
        "trigger_findings": {
            "recent_trauma",
            "substance_use_concern",
            "carbon_monoxide_or_combustion_exposure",
            "hypothermia",
            "pain_out_of_proportion_to_exam",
            "hemodynamic_instability",
        },
        "query_keywords": ("trauma", "overdose", "poisoning", "carbon monoxide", "hypothermia"),
        "minimum_data_prompts": [
            "先補 ABC、出血、神經狀態、暴露時間、同場他人症狀與安全隔離。 / Add ABCs, bleeding, neurologic status, exposure time, co-exposed people, and scene safety.",
            "釐清藥物/物質、燃燒密閉空間、低溫/高溫、疼痛與理學檢查不成比例。 / Clarify substances, combustion in enclosed spaces, temperature exposure, and pain out of proportion.",
            "確認是否需要毒物中心、創傷、CO、高壓氧或外科急症路徑。 / Decide on poison center, trauma, CO, hyperbaric, or surgical emergency pathways.",
        ],
        "finding_shortcuts": [
            "recent_trauma",
            "substance_use_concern",
            "altered_mental_status",
            "carbon_monoxide_or_combustion_exposure",
            "hemodynamic_instability",
            "pain_out_of_proportion_to_exam",
        ],
    },
    {
        "complaint_id": "fatigue_systemic",
        "display_order": 70,
        "title_zh": "疲倦、體重變化或全身症狀",
        "title_en": "Fatigue, weight change, or systemic symptoms",
        "trigger_findings": {
            "fatigue",
            "weight_loss",
            "jaundice",
            "easy_bruising_bleeding",
            "extreme_thirst_polyuria",
            "hypoglycemia_risk",
        },
        "query_keywords": ("fatigue", "weight loss", "jaundice", "bruising", "polyuria"),
        "minimum_data_prompts": [
            "先補病程、體重、食慾、發燒夜汗、出血、黃疸、口渴多尿與低血糖風險。 / Add tempo, weight, appetite, fever/night sweats, bleeding, jaundice, thirst/polyuria, and hypoglycemia risk.",
            "釐清藥物、妊娠、內分泌、肝腎、血液腫瘤、感染與自體免疫線索。 / Clarify medication, pregnancy, endocrine, liver/kidney, hematology/oncology, infection, and autoimmune clues.",
            "確認需要的基礎檢查與需要立即升級的貧血、肝衰、代謝或敗血症警訊。 / Decide baseline tests and escalation for anemia, liver failure, metabolic, or sepsis red flags.",
        ],
        "finding_shortcuts": [
            "fatigue",
            "weight_loss",
            "jaundice",
            "easy_bruising_bleeding",
            "extreme_thirst_polyuria",
            "hypoglycemia_risk",
        ],
    },
]


def get_general_differential_catalog_summary() -> dict[str, Any]:
    runtime_catalog = get_general_differential_runtime_catalog()
    return {
        "catalog_version": runtime_catalog["catalog_version"],
        "runtime_source": runtime_catalog.get("runtime_source", "reviewed runtime catalog"),
        "condition_count": len(runtime_catalog["conditions"]),
        "source_count": len(runtime_catalog["sources"]),
    }


def evaluate_general_differential(raw_findings: dict[str, Any]) -> dict[str, Any]:
    selected_findings = {
        str(finding)
        for finding in raw_findings.get("findings", [])
        if str(finding).strip()
    }
    query = str(raw_findings.get("query", "")).strip().lower()
    runtime_catalog = get_general_differential_runtime_catalog()
    conditions = runtime_catalog["conditions"]
    sources = runtime_catalog["sources"]
    results = []

    for condition in conditions:
        scored = _score_condition(condition, selected_findings, query, sources)
        if scored["score"] <= 0:
            continue
        results.append(scored)

    results.sort(
        key=lambda item: (
            -item["score"],
            URGENCY_ORDER.get(item["urgency"], 99),
            item["name_en"],
        )
    )

    ranked_results = results[:12]
    guided_follow_up = _build_guided_follow_up(
        ranked_results,
        selected_findings,
    )
    complaint_guided_intake = _build_complaint_guided_intake(
        selected_findings,
        query,
    )
    source_provenance = _build_source_provenance(ranked_results)
    patient_workflow = _build_patient_workflow(
        ranked_results,
        selected_findings,
        guided_follow_up,
    )
    candidate_comparison = _build_candidate_comparison(
        ranked_results,
        selected_findings,
    )
    intake_gap_tracker = _build_intake_gap_tracker(
        ranked_results,
        selected_findings,
    )
    current_action_plan = _build_current_action_plan(
        ranked_results,
        guided_follow_up,
        intake_gap_tracker,
        source_provenance,
        patient_workflow,
    )

    return {
        "results": ranked_results,
        "result_groups": _build_result_groups(ranked_results),
        "ask_next": _build_global_ask_next(results, selected_findings),
        "action_checklist": _build_action_checklist(results, selected_findings),
        "guided_follow_up": guided_follow_up,
        "results_brief": _build_results_brief(ranked_results, guided_follow_up),
        "candidate_comparison": candidate_comparison,
        "intake_gap_tracker": intake_gap_tracker,
        "current_action_plan": current_action_plan,
        "concise_result_summary": _build_concise_result_summary(
            ranked_results,
            guided_follow_up,
            selected_findings,
        ),
        "next_step_command_center": _build_next_step_command_center(
            ranked_results,
            guided_follow_up,
            complaint_guided_intake,
            source_provenance,
            patient_workflow,
        ),
        "complaint_guided_intake": complaint_guided_intake,
        "source_provenance": source_provenance,
        "candidate_scan_filters": _build_candidate_scan_filters(ranked_results),
        "secondary_candidate_filters": _build_secondary_candidate_filters(ranked_results),
        "patient_workflow": patient_workflow,
        "coverage": {
            "catalog_version": runtime_catalog["catalog_version"],
            "runtime_source": runtime_catalog.get(
                "runtime_source",
                "reviewed runtime catalog",
            ),
            "condition_count": len(conditions),
            "source_count": len(sources),
            "limitation_zh": "這是 starter catalog，不是完整疾病資料庫；未命中不代表排除疾病。",
            "limitation_en": "This is a starter catalog, not a complete disease database; no match does not rule out disease.",
        },
}


def _build_next_step_command_center(
    results: list[dict[str, Any]],
    guided_follow_up: list[dict[str, Any]],
    complaint_guided_intake: dict[str, Any],
    source_provenance: dict[str, Any],
    patient_workflow: dict[str, Any],
) -> dict[str, Any]:
    top_result = results[0] if results else None
    complaint_cards = list(complaint_guided_intake.get("cards", []))
    first_complaint = complaint_cards[0] if complaint_cards else {}
    source_count = int(source_provenance.get("unique_source_count", 0))
    safety_step = _workflow_source_step(guided_follow_up, "safety")

    return {
        "status": str(patient_workflow.get("status", "needs_structured_findings")),
        "priority_lane": _build_priority_lane(results, patient_workflow),
        "first_screen_brief": _build_first_screen_brief(
            results,
            guided_follow_up,
            complaint_guided_intake,
        ),
        "cards": [
            {
                "command_id": "safety_gate",
                "title_zh": "先排危險",
                "title_en": "Safety gate",
                "instruction_zh": "先確認 ABC、生命徵象、血氧、意識與立即紅旗，再看排序。",
                "instruction_en": str(
                    safety_step.get(
                        "instruction_en",
                        "Re-check ABCs, vitals, oxygenation, mental status, and red flags before using the ranking.",
                    )
                ),
                "anchor": "#case-input",
                "primary_candidate_slug": "",
                "primary_candidate_name_en": "",
            },
            {
                "command_id": "complaint_minimum_data",
                "title_zh": "補主訴最少資料",
                "title_en": "Minimum data",
                "instruction_zh": "把主訴、起始時間、嚴重度、相關陽性與陰性 findings 補齊後再重跑。",
                "instruction_en": (
                    "Complete complaint-specific minimum data before relying on the candidate list."
                ),
                "anchor": "#finding-selection",
                "primary_candidate_slug": "",
                "primary_candidate_name_en": str(first_complaint.get("title_en", "")),
                "complaint_id": str(first_complaint.get("complaint_id", "")),
            },
            {
                "command_id": "leading_candidate_review",
                "title_zh": "核對最高候選",
                "title_en": "Leading candidate check",
                "instruction_zh": "先核對最高候選的 matched findings、缺漏資料與不支持的線索。",
                "instruction_en": (
                    "Compare the leading candidate against matched findings, missing context, and disconfirming clues."
                ),
                "anchor": "#top-candidates",
                "primary_candidate_slug": str(top_result["slug"]) if top_result else "",
                "primary_candidate_name_en": str(top_result["name_en"]) if top_result else "",
                "primary_candidate_urgency": str(top_result["urgency"]) if top_result else "",
            },
            {
                "command_id": "source_review",
                "title_zh": "開來源再下結論",
                "title_en": "Source review",
                "instruction_zh": "至少打開最高候選的來源，確認適用範圍後再整理交班或重跑。",
                "instruction_en": (
                    "Open linked sources for the top candidates before using this reference in clinical reasoning."
                ),
                "anchor": "#source-provenance",
                "primary_candidate_slug": str(top_result["slug"]) if top_result else "",
                "primary_candidate_name_en": str(top_result["name_en"]) if top_result else "",
                "source_count": source_count,
            },
        ],
    }


def _build_first_screen_brief(
    results: list[dict[str, Any]],
    guided_follow_up: list[dict[str, Any]],
    complaint_guided_intake: dict[str, Any],
) -> dict[str, Any]:
    top_result = results[0] if results else None
    context_step = _workflow_source_step(guided_follow_up, "context")
    complaint_cards = list(complaint_guided_intake.get("cards", []))
    first_complaint = complaint_cards[0] if complaint_cards else {}
    first_context_prompt = next(
        iter(context_step.get("prompts", []) or []),
        "Add the highest-yield positive and negative findings for the chief complaint.",
    )

    return {
        "title_zh": "第一屏下一步",
        "title_en": "First-screen next steps",
        "items": [
            {
                "brief_id": "do_now",
                "title_zh": "現在先做",
                "title_en": "Do now",
                "instruction_zh": "先確認 ABC、生命徵象、血氧、意識與紅旗。",
                "instruction_en": "Re-check ABCs, vitals, oxygenation, mental status, and red flags.",
                "anchor": "#reference-results",
                "primary_candidate_slug": "",
                "primary_candidate_name_en": "",
            },
            {
                "brief_id": "ask_next",
                "title_zh": "接著補問",
                "title_en": "Ask next",
                "instruction_zh": "補上最會改變排序的陽性與陰性資料。",
                "instruction_en": str(first_context_prompt),
                "anchor": "#finding-selection",
                "primary_candidate_slug": "",
                "primary_candidate_name_en": str(first_complaint.get("title_en", "")),
            },
            {
                "brief_id": "compare",
                "title_zh": "再核對",
                "title_en": "Compare",
                "instruction_zh": "用已符合 findings、缺少資料與來源連結核對第一候選。",
                "instruction_en": "Compare the leading candidate against matched findings, missing context, and linked sources.",
                "anchor": "#top-candidates",
                "primary_candidate_slug": str(top_result["slug"]) if top_result else "",
                "primary_candidate_name_en": str(top_result["name_en"]) if top_result else "",
            },
        ],
    }


def _build_priority_lane(
    results: list[dict[str, Any]],
    patient_workflow: dict[str, Any],
) -> dict[str, Any]:
    selected_finding_count = int(patient_workflow.get("selected_finding_count", 0))
    top_urgencies = [str(result.get("urgency", "")) for result in results[:3]]
    top_urgency = next(
        (
            urgency
            for urgency in ("emergent", "urgent", "soon", "routine")
            if urgency in top_urgencies
        ),
        "none",
    )

    if not results or selected_finding_count < 2:
        return {
            "lane_id": "needs_more_data",
            "title_zh": "先補資料",
            "title_en": "Needs more data",
            "instruction_zh": "先補主訴、時間軸、生命徵象與紅旗，再重新產生排序。",
            "instruction_en": "Complete chief complaint, timeline, vitals, and red flags before relying on ranking.",
            "selected_finding_count": selected_finding_count,
            "top_urgency": top_urgency,
        }

    if top_urgency == "emergent":
        return {
            "lane_id": "critical_first",
            "title_zh": "危急先排",
            "title_en": "Critical first",
            "instruction_zh": "先確認立即危險、生命徵象與急症處置需求，再補鑑別資料。",
            "instruction_en": "Rule out immediate danger and emergency escalation needs before expanding the reference list.",
            "selected_finding_count": selected_finding_count,
            "top_urgency": top_urgency,
        }

    if top_urgency == "urgent":
        return {
            "lane_id": "urgent_workup",
            "title_zh": "急性評估",
            "title_en": "Urgent workup",
            "instruction_zh": "先完成會改變急迫性的資料與來源核對，再安排下一步評估。",
            "instruction_en": "Complete urgency-changing context and source checks before planning the next evaluation step.",
            "selected_finding_count": selected_finding_count,
            "top_urgency": top_urgency,
        }

    return {
        "lane_id": "routine_followup",
        "title_zh": "例行追蹤",
        "title_en": "Routine follow-up",
        "instruction_zh": "目前沒有前排急症訊號；補齊陰性資料、核對來源，並規劃追蹤或轉介。",
        "instruction_en": "No urgent leader is in the front rank; add negative findings, check sources, and plan follow-up or referral.",
        "selected_finding_count": selected_finding_count,
        "top_urgency": top_urgency,
    }


def _score_condition(
    condition: dict[str, Any],
    selected_findings: set[str],
    query: str,
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    signals = condition["signals"]
    signal_findings = _rank_signal_findings(signals)
    matched_findings = [
        finding for finding in signal_findings if finding in selected_findings
    ]
    score = sum(signals[finding] for finding in matched_findings)
    query_match_score = _query_match_score(condition, query)
    matched_text_search = query_match_score > 0
    score += query_match_score

    return {
        "slug": condition["slug"],
        "name_zh": condition["name_zh"],
        "name_en": condition["name_en"],
        "system": condition["system"],
        "urgency": condition["urgency"],
        "summary_zh": condition["summary_zh"],
        "summary_en": condition["summary_en"],
        "score": score,
        "urgency_filter_value": condition["urgency"],
        "system_filter_value": _source_filter_slug(condition["system"]),
        "matched_findings": matched_findings,
        "signal_findings": signal_findings,
        "matched_text_search": matched_text_search,
        "ask_next": condition["ask_next"],
        "action_items": _build_result_action_items(condition, matched_findings),
        "sources": [sources[source_id] for source_id in condition["source_ids"]],
    }


def _rank_signal_findings(signals: dict[str, int]) -> list[str]:
    return [
        str(finding)
        for finding, _weight in sorted(
            signals.items(),
            key=lambda item: (-int(item[1]), str(item[0])),
        )
    ]


def _query_match_score(condition: dict[str, Any], query: str) -> int:
    if not query:
        return 0
    normalized_query = query.strip().lower()
    synonyms = [synonym.lower() for synonym in condition.get("synonyms", [])]
    names = [
        condition["name_en"].lower(),
        condition["name_zh"].lower(),
    ]
    slug_text = condition["slug"].replace("_", " ")

    if normalized_query in synonyms:
        return 12
    if normalized_query in names or normalized_query == slug_text:
        return 11

    tokenized_terms = [slug_text, *names, *synonyms]
    for term in tokenized_terms:
        if normalized_query in term.split():
            return 9
    if any(
        normalized_query in term
        or (len(term) >= 4 and term in normalized_query)
        for term in tokenized_terms
    ):
        return 7
    return 0


def _build_complaint_guided_intake(
    selected_findings: set[str],
    query: str,
) -> dict[str, Any]:
    matched_cards: list[dict[str, Any]] = []
    fallback_cards: list[dict[str, Any]] = []
    normalized_query = query.strip().lower()

    for preset in COMPLAINT_GUIDED_INTAKE_PRESETS:
        trigger_findings = set(preset["trigger_findings"])
        matched_findings = sorted(selected_findings.intersection(trigger_findings))
        matched_query = bool(
            normalized_query
            and any(
                str(keyword).lower() in normalized_query
                for keyword in preset.get("query_keywords", ())
            )
        )
        card = _complaint_guided_intake_card(
            preset,
            matched_findings,
            matched_query,
        )
        if matched_findings or matched_query:
            matched_cards.append(card)
        else:
            fallback_cards.append(card)

    matched_cards.sort(
        key=lambda card: (
            -len(card["matched_findings"]),
            int(card["display_order"]),
        )
    )
    fallback_cards.sort(key=lambda card: int(card["display_order"]))

    if matched_cards:
        return {
            "status": "matched",
            "cards": matched_cards[:3],
        }

    return {
        "status": "needs_complaint_selection",
        "cards": fallback_cards[:3],
    }


def _complaint_guided_intake_card(
    preset: dict[str, Any],
    matched_findings: list[str],
    matched_query: bool,
) -> dict[str, Any]:
    return {
        "complaint_id": str(preset["complaint_id"]),
        "display_order": int(preset["display_order"]),
        "title_zh": str(preset["title_zh"]),
        "title_en": str(preset["title_en"]),
        "matched_findings": matched_findings,
        "matched_query": matched_query,
        "minimum_data_prompts": list(preset["minimum_data_prompts"]),
        "finding_shortcuts": list(preset["finding_shortcuts"]),
    }


def _build_source_provenance(results: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    seen_rows: set[tuple[str, str]] = set()
    unique_urls: set[str] = set()
    publisher_counts: dict[str, dict[str, Any]] = {}

    for result in results:
        for source in result.get("sources", []):
            url = str(source.get("url", ""))
            publisher = str(source.get("publisher", "Unknown source"))
            row_key = (str(result["slug"]), url)
            if row_key in seen_rows:
                continue
            seen_rows.add(row_key)
            unique_urls.add(url)
            publisher_slug = _source_filter_slug(publisher)
            publisher_counts.setdefault(
                publisher_slug,
                {"publisher": publisher, "publisher_slug": publisher_slug, "count": 0},
            )
            publisher_counts[publisher_slug]["count"] += 1
            rows.append(
                {
                    "candidate_slug": result["slug"],
                    "candidate_name_en": result["name_en"],
                    "urgency": result["urgency"],
                    "publisher": publisher,
                    "publisher_slug": publisher_slug,
                    "title": source.get("title", "Untitled source"),
                    "url": url,
                }
            )

    publisher_filters = sorted(
        publisher_counts.values(),
        key=lambda item: (-int(item["count"]), str(item["publisher"])),
    )

    return {
        "unique_source_count": len(unique_urls),
        "row_count": len(rows),
        "publisher_filters": publisher_filters,
        "rows": rows,
    }


def _source_filter_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown-source"


def _build_secondary_candidate_filters(results: list[dict[str, Any]]) -> dict[str, Any]:
    secondary_results = results[3:]
    urgency_counts: dict[str, dict[str, Any]] = {}
    system_counts: dict[str, dict[str, Any]] = {}

    for result in secondary_results:
        urgency_value = str(result["urgency_filter_value"])
        urgency_counts.setdefault(
            urgency_value,
            {
                "filter_type": "urgency",
                "filter_value": urgency_value,
                "label": str(result["urgency"]).title(),
                "count": 0,
            },
        )
        urgency_counts[urgency_value]["count"] += 1

        system_value = str(result["system_filter_value"])
        system_counts.setdefault(
            system_value,
            {
                "filter_type": "system",
                "filter_value": system_value,
                "label": str(result["system"]),
                "count": 0,
            },
        )
        system_counts[system_value]["count"] += 1

    return {
        "secondary_count": len(secondary_results),
        "urgency_filters": sorted(
            urgency_counts.values(),
            key=lambda item: (URGENCY_ORDER.get(str(item["filter_value"]), 99), str(item["label"])),
        ),
        "system_filters": sorted(
            system_counts.values(),
            key=lambda item: (-int(item["count"]), str(item["label"])),
        ),
    }


def _build_candidate_scan_filters(results: list[dict[str, Any]]) -> dict[str, Any]:
    scan_results = results[:5]
    urgency_counts: dict[str, dict[str, Any]] = {}
    system_counts: dict[str, dict[str, Any]] = {}

    for result in scan_results:
        urgency_value = str(result["urgency_filter_value"])
        urgency_counts.setdefault(
            urgency_value,
            {
                "filter_type": "urgency",
                "filter_value": urgency_value,
                "label": str(result["urgency"]).title(),
                "count": 0,
            },
        )
        urgency_counts[urgency_value]["count"] += 1

        system_value = str(result["system_filter_value"])
        system_counts.setdefault(
            system_value,
            {
                "filter_type": "system",
                "filter_value": system_value,
                "label": str(result["system"]),
                "count": 0,
            },
        )
        system_counts[system_value]["count"] += 1

    return {
        "scan_count": len(scan_results),
        "urgency_filters": sorted(
            urgency_counts.values(),
            key=lambda item: (URGENCY_ORDER.get(str(item["filter_value"]), 99), str(item["label"])),
        ),
        "system_filters": sorted(
            system_counts.values(),
            key=lambda item: (-int(item["count"]), str(item["label"])),
        ),
    }


def _build_result_groups(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        grouped.setdefault(result["urgency"], []).append(result)

    result_groups: list[dict[str, Any]] = []
    for urgency in sorted(grouped, key=lambda key: URGENCY_ORDER.get(key, 99)):
        candidates = grouped[urgency]
        result_groups.append(
            {
                "urgency": urgency,
                "label": urgency.title(),
                "count": len(candidates),
                "candidates": [
                    {
                        "slug": candidate["slug"],
                        "name_zh": candidate["name_zh"],
                        "name_en": candidate["name_en"],
                        "score": candidate["score"],
                        "system": candidate["system"],
                    }
                    for candidate in candidates[:3]
                ],
            }
        )
    return result_groups


def _build_global_ask_next(
    results: list[dict[str, Any]], selected_findings: set[str]
) -> list[str]:
    prompts = list(DEFAULT_ASK_NEXT)
    for prompt in _build_focused_context_prompts(selected_findings):
        if prompt not in prompts:
            prompts.append(prompt)
    for result in results[:3]:
        for prompt in result["ask_next"]:
            if prompt not in prompts:
                prompts.append(prompt)
    if not selected_findings:
        return prompts[:4]
    return prompts[:7]


def _build_guided_follow_up(
    results: list[dict[str, Any]],
    selected_findings: set[str],
) -> list[dict[str, Any]]:
    context_prompts = _build_focused_context_prompts(selected_findings)
    if not context_prompts:
        context_prompts = [DEFAULT_ASK_NEXT[3]]

    top_results = results[:3]
    top_prompts: list[str] = []
    for result in top_results:
        for prompt in result["ask_next"][:1]:
            if prompt not in top_prompts:
                top_prompts.append(prompt)
    if not top_prompts:
        top_prompts = [DEFAULT_ASK_NEXT[1]]

    return [
        {
            "step_id": "safety",
            "title_zh": "先確認安全",
            "title_en": "Safety first",
            "instruction_zh": "先回到 ABC、生命徵象、血氧、意識狀態與紅旗，再使用排序結果。",
            "instruction_en": "Re-check ABCs, vitals, oxygenation, mental status, and red flags before using the ranking.",
            "prompts": [DEFAULT_ASK_NEXT[0]],
            "related_condition_slugs": [],
            "related_condition_names": [],
        },
        {
            "step_id": "context",
            "title_zh": "補最高價值脈絡",
            "title_en": "Fill the highest-yield context",
            "instruction_zh": "先補最能改變排序的陽性與陰性資訊，再看候選疾病。",
            "instruction_en": "Add the focused positive and negative context most likely to change the ranking before relying on the candidate list.",
            "prompts": context_prompts,
            "related_condition_slugs": [],
            "related_condition_names": [],
        },
        {
            "step_id": "top_differential",
            "title_zh": "核對前三個候選",
            "title_en": "Check the leading differentials",
            "instruction_zh": "核對前三個候選的符合點、缺資料處與來源連結，作為臨床推理參考。",
            "instruction_en": "Compare the leading candidates against matched findings, missing context, and source links before applying clinical reasoning.",
            "prompts": top_prompts,
            "related_condition_slugs": [
                result["slug"] for result in top_results
            ],
            "related_condition_names": [
                result["name_en"] for result in top_results
            ],
        },
        {
            "step_id": "rerun",
            "title_zh": "補資料後重跑",
            "title_en": "Re-run after updates",
            "instruction_zh": "把已確認的 findings 加回左側，移除不確定項目，再重新排序。",
            "instruction_en": "Add confirmed findings, remove uncertain items, and re-run the ranking.",
            "prompts": [
                "Re-run the ranking after adding confirmed data and removing uncertain findings."
            ],
            "related_condition_slugs": [],
            "related_condition_names": [],
        },
    ]


def _build_focused_context_prompts(selected_findings: set[str]) -> list[str]:
    prompts: list[str] = []
    for findings, prompt in FOCUSED_ASK_NEXT_CONTEXTS:
        if selected_findings.intersection(findings):
            prompts.append(prompt)
    return prompts[:2]


def _build_action_checklist(
    results: list[dict[str, Any]],
    selected_findings: set[str],
) -> list[dict[str, str]]:
    if not results:
        return [
            {
                "category_zh": "安全再確認",
                "category_en": "Safety check",
                "instruction_zh": "先重新確認 ABC、生命徵象、血氧、意識與紅旗，再補 structured findings。",
                "instruction_en": "Re-check ABCs, vitals, oxygenation, mental status, and red flags before adding structured findings.",
            },
            {
                "category_zh": "補資料",
                "category_en": "Data to add",
                "instruction_zh": "從主訴與系統分類補勾已確認 findings；不要輸入病人識別資料。",
                "instruction_en": "Add confirmed findings from the complaint and system groups; do not enter patient identifiers.",
            },
            {
                "category_zh": "重跑",
                "category_en": "Re-run",
                "instruction_zh": "補完資料後重新產生排序，再看來源與 ask-next。",
                "instruction_en": "Re-run the ranking after adding findings, then review sources and ask-next prompts.",
            },
        ]

    top_results = results[:3]
    top_names = ", ".join(result["name_en"] for result in top_results)
    data_instruction_zh = "先處理前 3 名的 ask-next，補勾確定存在或確定不存在的 findings。"
    data_instruction_en = "Use the top 3 ask-next prompts, then add confirmed positive or negative finding context."
    if not selected_findings:
        data_instruction_zh = "目前 structured findings 不足，先回到左側補勾已確認 findings。"
        data_instruction_en = "Structured findings are sparse; return to the left panel and add confirmed findings first."

    return [
        {
            "category_zh": "安全再確認",
            "category_en": "Safety check",
            "instruction_zh": "先重新確認 ABC、生命徵象、血氧、意識與紅旗；排序不可取代臨床判斷。",
            "instruction_en": "Re-check ABCs, vitals, oxygenation, mental status, and red flags; ranking does not replace clinical judgment.",
        },
        {
            "category_zh": "補資料",
            "category_en": "Data to add",
            "instruction_zh": data_instruction_zh,
            "instruction_en": data_instruction_en,
        },
        {
            "category_zh": "看來源",
            "category_en": "Source review",
            "instruction_zh": f"先打開前 3 名來源並核對適用範圍：{top_names}。",
            "instruction_en": f"Open the source links for the top 3 items and check applicability: {top_names}.",
        },
        {
            "category_zh": "重跑",
            "category_en": "Re-run",
            "instruction_zh": "補完資料、移除不確定 findings 後重新產生排序。",
            "instruction_en": "Re-run the ranking after adding confirmed data and removing uncertain findings.",
        },
    ]


def _build_results_brief(
    results: list[dict[str, Any]],
    guided_follow_up: list[dict[str, Any]],
) -> dict[str, Any]:
    top = results[0] if results else None
    next_step = guided_follow_up[0] if guided_follow_up else {}
    primary_result_count = min(len(results), 3)
    secondary_result_count = max(len(results) - primary_result_count, 0)

    return {
        "top_candidate_name_zh": str(top["name_zh"]) if top else "",
        "top_candidate_name_en": str(top["name_en"]) if top else "",
        "top_urgency": str(top["urgency"]) if top else "",
        "top_score": int(top["score"]) if top else 0,
        "primary_result_count": primary_result_count,
        "secondary_result_count": secondary_result_count,
        "has_more_candidates": secondary_result_count > 0,
        "next_step_title_zh": str(next_step.get("title_zh", "")),
        "next_step_title_en": str(next_step.get("title_en", "")),
        "next_step_instruction_zh": str(next_step.get("instruction_zh", "")),
        "next_step_instruction_en": str(next_step.get("instruction_en", "")),
    }


def _finding_label_map() -> dict[str, dict[str, str]]:
    labels: dict[str, dict[str, str]] = {}
    for group in FINDING_GROUPS:
        for finding_id, label_en, label_zh in group["findings"]:
            labels[str(finding_id)] = {
                "label_zh": str(label_zh),
                "label_en": str(label_en),
                "group_zh": str(group["group_zh"]),
                "group_en": str(group["group_en"]),
            }
    return labels


def _format_finding_label(
    finding_id: str,
    labels: dict[str, dict[str, str]],
) -> dict[str, str]:
    label = labels.get(finding_id)
    if label:
        return {
            "finding_id": finding_id,
            "label_zh": label["label_zh"],
            "label_en": label["label_en"],
        }
    fallback = finding_id.replace("_", " ")
    return {
        "finding_id": finding_id,
        "label_zh": fallback,
        "label_en": fallback,
    }


def _build_candidate_comparison(
    results: list[dict[str, Any]],
    selected_findings: set[str],
) -> dict[str, Any]:
    labels = _finding_label_map()
    rows: list[dict[str, Any]] = []
    for result in results[:3]:
        matched_findings = [
            str(finding)
            for finding in result.get("matched_findings", [])
        ]
        support_points = [
            {
                "kind": "matched_finding",
                **_format_finding_label(finding, labels),
            }
            for finding in matched_findings[:4]
        ]
        if result.get("matched_text_search"):
            support_points.append(
                {
                    "kind": "text_match",
                    "finding_id": "text_match",
                    "label_zh": "主訴文字命中此候選",
                    "label_en": "Query text matched this candidate",
                }
            )
        if result.get("sources"):
            support_points.append(
                {
                    "kind": "source_count",
                    "finding_id": "source_count",
                    "label_zh": f"{len(result['sources'])} 個已連結來源",
                    "label_en": f"{len(result['sources'])} linked sources",
                }
            )
        if not support_points:
            support_points.append(
                {
                    "kind": "limited_support",
                    "finding_id": "limited_support",
                    "label_zh": "目前結構化支持點不足，需先補資料",
                    "label_en": "Limited structured support; add more data first",
                }
            )

        if matched_findings:
            against_points = [
                {
                    "kind": "missing_negative_data",
                    "label_zh": "尚未輸入陰性資料；不要把未勾選當作排除",
                    "label_en": "No negative findings entered; absence of a checkbox is not exclusion",
                }
            ]
        elif selected_findings:
            against_points = [
                {
                    "kind": "no_direct_structured_match",
                    "label_zh": "已選 findings 目前未直接支持此候選",
                    "label_en": "Selected findings do not directly support this candidate yet",
                }
            ]
        else:
            against_points = [
                {
                    "kind": "needs_structured_findings",
                    "label_zh": "尚未輸入結構化 findings，不能比較反對點",
                    "label_en": "No structured findings entered, so opposing evidence cannot be compared",
                }
            ]

        rows.append(
            {
                "slug": result["slug"],
                "name_zh": result["name_zh"],
                "name_en": result["name_en"],
                "urgency": result["urgency"],
                "score": result["score"],
                "system": result["system"],
                "source_count": len(result.get("sources", [])),
                "support_points": support_points[:5],
                "against_points": against_points,
                "next_questions": list(result.get("ask_next", []))[:2],
            }
        )

    return {
        "rows": rows,
        "selected_finding_count": len(selected_findings),
        "title_zh": "前三名比較",
        "title_en": "Top-three comparison",
        "caution_zh": "反對點只代表目前資料缺口；未輸入陰性資料不能排除疾病。",
        "caution_en": "Opposing evidence here means current data gaps; absent negative findings do not rule out disease.",
    }


def _build_intake_gap_tracker(
    results: list[dict[str, Any]],
    selected_findings: set[str],
) -> dict[str, Any]:
    labels = _finding_label_map()
    priority_map: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []

    for result_rank, result in enumerate(results[:3]):
        signal_findings = [
            str(finding)
            for finding in result.get("signal_findings", [])
        ]
        matched_findings = [
            str(finding)
            for finding in result.get("matched_findings", [])
        ]
        missing_findings = [
            finding
            for finding in signal_findings
            if finding not in selected_findings
        ]
        signal_count = len(signal_findings)
        completion_percent = (
            round((len(matched_findings) / signal_count) * 100)
            if signal_count
            else 0
        )

        for missing_rank, finding in enumerate(missing_findings[:4]):
            entry = priority_map.setdefault(
                finding,
                {
                    **_format_finding_label(finding, labels),
                    "candidate_names_en": [],
                    "candidate_names_zh": [],
                    "first_seen_rank": result_rank,
                    "first_missing_rank": missing_rank,
                },
            )
            entry["candidate_names_en"].append(str(result["name_en"]))
            entry["candidate_names_zh"].append(str(result["name_zh"]))

        if missing_findings:
            next_label = _format_finding_label(missing_findings[0], labels)
            next_step_zh = f"先確認：{next_label['label_zh']}"
            next_step_en = f"Ask next: {next_label['label_en']}"
        else:
            next_step_zh = "核心 findings 已初步輸入，接著看來源與下一問。"
            next_step_en = "Core findings are entered; review sources and the next question."

        rows.append(
            {
                "slug": result["slug"],
                "name_zh": result["name_zh"],
                "name_en": result["name_en"],
                "urgency": result["urgency"],
                "matched_count": len(matched_findings),
                "signal_count": signal_count,
                "completion_percent": completion_percent,
                "completion_label": f"{len(matched_findings)}/{signal_count}",
                "known_findings": [
                    _format_finding_label(finding, labels)
                    for finding in matched_findings[:3]
                ],
                "missing_findings": [
                    _format_finding_label(finding, labels)
                    for finding in missing_findings[:4]
                ],
                "next_step_zh": next_step_zh,
                "next_step_en": next_step_en,
            }
        )

    priority_next = sorted(
        priority_map.values(),
        key=lambda item: (
            item["first_seen_rank"],
            item["first_missing_rank"],
            -len(item["candidate_names_en"]),
            item["label_en"],
        ),
    )
    for item in priority_next:
        candidate_count = len(item["candidate_names_en"])
        item["candidate_count"] = candidate_count
        item["candidate_names_en"] = item["candidate_names_en"][:2]
        item["candidate_names_zh"] = item["candidate_names_zh"][:2]
        item["reason_zh"] = f"可同時釐清 {candidate_count} 個前排候選"
        item["reason_en"] = f"Clarifies {candidate_count} leading candidates"

    return {
        "rows": rows,
        "priority_next": priority_next[:5],
        "selected_finding_count": len(selected_findings),
        "title_zh": "資料缺口追蹤",
        "title_en": "Intake gap tracker",
        "priority_title_zh": "下一步先補",
        "priority_title_en": "Ask these next",
        "caution_zh": "還缺代表尚未詢問或尚未輸入，不是陰性，也不是排除。",
        "caution_en": "Missing means not asked or not entered; it is not a negative finding or exclusion.",
    }


def _build_current_action_plan(
    results: list[dict[str, Any]],
    guided_follow_up: list[dict[str, Any]],
    intake_gap_tracker: dict[str, Any],
    source_provenance: dict[str, Any],
    patient_workflow: dict[str, Any],
) -> dict[str, Any]:
    selected_count = int(patient_workflow.get("selected_finding_count", 0))
    top_result = results[0] if results else {}
    priority_next = list(intake_gap_tracker.get("priority_next", []))
    top_priority = priority_next[0] if priority_next else {}
    safety_step = _workflow_source_step(guided_follow_up, "safety")
    source_count = int(source_provenance.get("unique_source_count", 0))

    if not results:
        current_step_id = "case_input"
        title_zh = "先完成主訴與結構化 findings"
        title_en = "Complete case input first"
        command_zh = "輸入主訴、時間軸、生命徵象與至少一個關鍵 finding。"
        command_en = "Enter the chief complaint, timeline, vitals, and at least one key finding."
        reason_zh = "目前沒有足夠資料產生可用的候選比較。"
        reason_en = "There is not enough information to produce a useful candidate comparison."
        anchor = "#case-input"
    elif selected_count < 2:
        current_step_id = "minimum_data"
        title_zh = "先補最低限度資料"
        title_en = "Add minimum data first"
        command_zh = "至少再補一個與主訴相關的 positive 或 negative finding。"
        command_en = "Add at least one more chief-complaint-specific positive or negative finding."
        reason_zh = "少於兩個 findings 時，排序只能當作粗略搜尋入口。"
        reason_en = "With fewer than two findings, the ranking is only a coarse search entry."
        anchor = "#finding-selection"
    elif top_priority:
        current_step_id = "ask_missing_finding"
        title_zh = "現在先問這個缺口"
        title_en = "Ask this gap now"
        command_zh = f"先確認：{top_priority['label_zh']}"
        command_en = f"Ask next: {top_priority['label_en']}"
        reason_zh = str(top_priority.get("reason_zh", "可釐清前排候選。"))
        reason_en = str(top_priority.get("reason_en", "Clarifies leading candidates."))
        anchor = "#finding-selection"
    else:
        current_step_id = "compare_and_source_check"
        title_zh = "比較前三名並看來源"
        title_en = "Compare top candidates and sources"
        command_zh = "確認支持點、資料缺口與來源後，再決定下一個臨床問題。"
        command_en = "Review supports, data gaps, and sources before choosing the next clinical question."
        reason_zh = "核心 findings 已初步輸入，下一步是確認推理依據。"
        reason_en = "Core findings are entered; the next step is to check reasoning support."
        anchor = "#top-candidates"

    step_statuses = {
        "safety_gate": "required",
        "minimum_data": "next",
        "candidate_compare": "after",
        "source_review": "after",
    }
    if current_step_id in ("case_input", "minimum_data", "ask_missing_finding"):
        step_statuses["minimum_data"] = "current"
    elif current_step_id == "compare_and_source_check":
        step_statuses["minimum_data"] = "done"
        step_statuses["candidate_compare"] = "current"
        step_statuses["source_review"] = "next"

    steps = [
        {
            "step_id": "safety_gate",
            "title_zh": "安全先行",
            "title_en": "Safety first",
            "status": step_statuses["safety_gate"],
            "instruction_zh": "先確認生命徵象、意識、ABC 與紅旗。",
            "instruction_en": str(
                safety_step.get(
                    "instruction_en",
                    "Check vitals, mental status, ABCs, and red flags first.",
                )
            ),
            "anchor": "#case-input",
        },
        {
            "step_id": "minimum_data",
            "title_zh": "補資料缺口",
            "title_en": "Fill data gap",
            "status": step_statuses["minimum_data"],
            "instruction_zh": command_zh
            if current_step_id in ("minimum_data", "ask_missing_finding")
            else "確認主訴相關的 positive 與 negative findings。",
            "instruction_en": command_en
            if current_step_id in ("minimum_data", "ask_missing_finding")
            else "Confirm chief-complaint-specific positive and negative findings.",
            "anchor": "#finding-selection",
        },
        {
            "step_id": "candidate_compare",
            "title_zh": "比較候選",
            "title_en": "Compare candidates",
            "status": step_statuses["candidate_compare"],
            "instruction_zh": "看前三名的支持點、反對或缺口、下一問。",
            "instruction_en": "Review top-three supports, gaps, and next questions.",
            "anchor": "#top-candidates",
        },
        {
            "step_id": "source_review",
            "title_zh": "來源稽核",
            "title_en": "Source review",
            "status": step_statuses["source_review"],
            "instruction_zh": f"查看前排候選連結的 {source_count} 個 unique sources。",
            "instruction_en": f"Review {source_count} unique linked sources for leading candidates.",
            "anchor": "#source-provenance",
        },
    ]

    return {
        "current_step_id": current_step_id,
        "title_zh": title_zh,
        "title_en": title_en,
        "command_zh": command_zh,
        "command_en": command_en,
        "reason_zh": reason_zh,
        "reason_en": reason_en,
        "anchor": anchor,
        "top_candidate_slug": str(top_result.get("slug", "")),
        "top_candidate_name_en": str(top_result.get("name_en", "")),
        "top_candidate_name_zh": str(top_result.get("name_zh", "")),
        "top_candidate_urgency": str(top_result.get("urgency", "")),
        "source_count": source_count,
        "steps": steps,
        "safety_note_zh": "這是臨床人員參考步驟，不是診斷或治療指令。",
        "safety_note_en": "This is a clinician reference step, not a diagnosis or treatment order.",
    }


def _build_concise_result_summary(
    results: list[dict[str, Any]],
    guided_follow_up: list[dict[str, Any]],
    selected_findings: set[str],
) -> dict[str, Any]:
    primary_step = guided_follow_up[0] if guided_follow_up else {}
    primary_next_action = {
        "title_zh": str(primary_step.get("title_zh", "先排除立即危險")),
        "title_en": str(primary_step.get("title_en", "Safety first")),
        "instruction_zh": str(
            primary_step.get(
                "instruction_zh",
                "先確認 ABC、生命徵象、血氧、意識與紅旗，再使用排名。",
            )
        ),
        "instruction_en": str(
            primary_step.get(
                "instruction_en",
                "Re-check ABCs, vitals, oxygenation, mental status, and red flags before using the ranking.",
            )
        ),
    }

    danger_checks: list[str] = []
    for prompt in [DEFAULT_ASK_NEXT[0], *_build_focused_context_prompts(selected_findings)]:
        if prompt not in danger_checks:
            danger_checks.append(prompt)
    for step in guided_follow_up[:3]:
        for prompt in step.get("prompts", [])[:1]:
            if prompt not in danger_checks:
                danger_checks.append(str(prompt))
    if not danger_checks:
        danger_checks.append(DEFAULT_ASK_NEXT[0])

    return {
        "primary_next_action": primary_next_action,
        "danger_checks": danger_checks[:3],
        "top_candidates": [
            {
                "slug": result["slug"],
                "name_zh": result["name_zh"],
                "name_en": result["name_en"],
                "urgency": result["urgency"],
                "score": result["score"],
                "system": result["system"],
                "source_count": len(result.get("sources", [])),
            }
            for result in results[:3]
        ],
        "has_structured_findings": bool(selected_findings),
    }


def _build_patient_workflow(
    results: list[dict[str, Any]],
    selected_findings: set[str],
    guided_follow_up: list[dict[str, Any]],
) -> dict[str, Any]:
    top_results = results[:3]
    top_names_zh = [str(result["name_zh"]) for result in top_results]
    top_names_en = [str(result["name_en"]) for result in top_results]
    top_source_count = len(
        {
            str(source["url"])
            for result in top_results
            for source in result.get("sources", [])
            if source.get("url")
        }
    )
    context_step = _workflow_source_step(guided_follow_up, "context")
    top_differential_step = _workflow_source_step(
        guided_follow_up,
        "top_differential",
    )
    context_prompts = list(context_step.get("prompts") or [DEFAULT_ASK_NEXT[1]])
    compare_prompts = list(
        top_differential_step.get("prompts") or context_prompts[:1]
    )
    status = "ready_for_stepwise_review" if top_results else "needs_structured_findings"
    risk_gate = _build_workflow_risk_gate(top_results)
    needs_minimum_data = not top_results or len(selected_findings) < 2
    candidate_summary_zh = "、".join(top_names_zh) if top_names_zh else "尚未有可排序候選"
    candidate_summary_en = ", ".join(top_names_en) if top_names_en else "none ranked yet"

    if top_results:
        handoff_summary_zh = (
            f"已選 {len(selected_findings)} 個結構化 findings；"
            f"先比較：{candidate_summary_zh}。"
            "交接時保留未解紅旗、已查來源與需要補問的資料。"
        )
        handoff_summary_en = (
            f"Structured findings: {len(selected_findings)}. "
            f"Leading reference candidates to review: {candidate_summary_en}. "
            "Immediate workflow: rule out danger, complete missing context, "
            "compare the leading candidates, then hand off or re-run with updated findings."
        )
    else:
        handoff_summary_zh = (
            "目前資料不足以排序；先確認生命徵象、紅旗與主訴相關 findings，"
            "再重新產生參考排序。"
        )
        handoff_summary_en = (
            "Not enough structured data to rank yet. Confirm vitals, red flags, "
            "and complaint-specific findings, then re-run the reference ranking."
        )

    return {
        "status": status,
        "risk_gate": risk_gate,
        "needs_minimum_data": needs_minimum_data,
        "minimum_data_items": (
            _build_minimum_data_items() if needs_minimum_data else []
        ),
        "selected_finding_count": len(selected_findings),
        "top_candidate_count": len(top_results),
        "top_source_count": top_source_count,
        "candidate_summary_zh": candidate_summary_zh,
        "candidate_summary_en": candidate_summary_en,
        "handoff_summary_zh": handoff_summary_zh,
        "handoff_summary_en": handoff_summary_en,
        "steps": [
            {
                "step_id": "rule_out_immediate_danger",
                "title_zh": "先排除立即危險",
                "title_en": "Rule out immediate danger",
                "instruction_zh": "先確認 ABC、生命徵象、血氧、意識狀態與紅旗，再看參考排序。",
                "instruction_en": "Re-check ABCs, vitals, oxygenation, mental status, and red flags before using the reference ranking.",
                "prompts": [DEFAULT_ASK_NEXT[0]],
                "candidate_names_zh": [],
                "candidate_names_en": [],
                "anchor": "#reference-results",
            },
            {
                "step_id": "complete_missing_context",
                "title_zh": "補齊缺少脈絡",
                "title_en": "Complete missing context",
                "instruction_zh": "用最可能改變排序的追問，補上陽性與陰性資料。",
                "instruction_en": "Use the focused prompts to add positive and negative context that can change the ranking.",
                "prompts": context_prompts,
                "candidate_names_zh": [],
                "candidate_names_en": [],
                "anchor": "#finding-selection",
            },
            {
                "step_id": "compare_leading_candidates",
                "title_zh": "比較前三個候選",
                "title_en": "Compare leading candidates",
                "instruction_zh": "把前三個候選和已符合 findings、缺少資料、來源連結逐項對照。",
                "instruction_en": "Compare the leading candidates against matched findings, missing context, and linked sources.",
                "prompts": compare_prompts,
                "candidate_names_zh": top_names_zh,
                "candidate_names_en": top_names_en,
                "anchor": "#top-candidates",
            },
            {
                "step_id": "handoff_or_rerun",
                "title_zh": "交接或重跑",
                "title_en": "Handoff or re-run",
                "instruction_zh": "記錄候選、未解問題、已查來源；新資料回來後更新 findings 並重跑。",
                "instruction_en": "Document leading candidates, unresolved safety questions, and checked sources; re-run after new data arrives.",
                "prompts": [
                    "Re-run the ranking after adding confirmed data and removing uncertain findings."
                ],
                "candidate_names_zh": top_names_zh,
                "candidate_names_en": top_names_en,
                "anchor": "#case-input",
            },
        ],
    }


def _build_minimum_data_items() -> list[dict[str, str]]:
    return [
        {
            "item_id": "chief_complaint_onset",
            "label_zh": "主訴與開始時間",
            "label_en": "Chief complaint and onset",
            "instruction_zh": "先寫清楚主要問題、開始時間、進展速度、最嚴重位置或症狀。",
            "instruction_en": "Clarify the main problem, onset, tempo, worst location, and most concerning symptom.",
        },
        {
            "item_id": "vitals_stability",
            "label_zh": "生命徵象與穩定度",
            "label_en": "Vitals and stability",
            "instruction_zh": "確認血壓、心跳、呼吸、血氧、體溫、意識狀態與是否不穩定。",
            "instruction_en": "Check blood pressure, pulse, respirations, oxygenation, temperature, mental status, and instability.",
        },
        {
            "item_id": "red_flags",
            "label_zh": "紅旗",
            "label_en": "Red flags",
            "instruction_zh": "依主訴補問會改變急迫性的紅旗，例如休克、低氧、神經缺損、劇痛、出血或懷孕風險。",
            "instruction_en": "Ask complaint-specific red flags that change urgency, such as shock, hypoxemia, focal deficit, severe pain, bleeding, or pregnancy risk.",
        },
        {
            "item_id": "pertinent_context",
            "label_zh": "關鍵陽性與陰性資料",
            "label_en": "Pertinent positives and negatives",
            "instruction_zh": "把確定有與確定沒有的 findings 都加入，避免只用單一症狀排序。",
            "instruction_en": "Add confirmed positive and negative findings so the ranking is not based on one symptom alone.",
        },
        {
            "item_id": "rerun_with_findings",
            "label_zh": "更新 findings 後重跑",
            "label_en": "Update findings and re-run",
            "instruction_zh": "資料補齊後更新 structured findings，再重新產生參考排序與下一步。",
            "instruction_en": "After collecting minimum data, update structured findings and re-run the reference ranking and next steps.",
        },
    ]


def _workflow_source_step(
    guided_follow_up: list[dict[str, Any]],
    step_id: str,
) -> dict[str, Any]:
    for step in guided_follow_up:
        if step.get("step_id") == step_id:
            return step
    return {}


def _build_workflow_risk_gate(results: list[dict[str, Any]]) -> str:
    if not results:
        return "insufficient_input"
    top_urgencies = {str(result.get("urgency", "")) for result in results[:3]}
    if "emergent" in top_urgencies:
        return "emergent_leader_present"
    if "urgent" in top_urgencies:
        return "urgent_leader_present"
    return "no_emergent_leader_in_top_three"


def _build_result_action_items(
    condition: dict[str, Any],
    matched_findings: list[str],
) -> list[dict[str, str]]:
    matched_summary = ", ".join(matched_findings) if matched_findings else "text search only"
    first_prompt = condition["ask_next"][0] if condition["ask_next"] else DEFAULT_ASK_NEXT[0]
    return [
        {
            "label_zh": "核對符合點",
            "label_en": "Check match",
            "instruction": f"Matched findings: {matched_summary}.",
        },
        {
            "label_zh": "補問",
            "label_en": "Ask next",
            "instruction": first_prompt,
        },
        {
            "label_zh": "查來源",
            "label_en": "Review source",
            "instruction": "Open linked sources before using this reference in clinical reasoning.",
        },
    ]
