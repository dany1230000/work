"""General differential evaluator for the broad clinician workbench."""

from __future__ import annotations

from typing import Any

from .differential_catalog import DEFAULT_ASK_NEXT, URGENCY_ORDER
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

    return {
        "results": ranked_results,
        "result_groups": _build_result_groups(ranked_results),
        "ask_next": _build_global_ask_next(results, selected_findings),
        "action_checklist": _build_action_checklist(results, selected_findings),
        "guided_follow_up": guided_follow_up,
        "results_brief": _build_results_brief(ranked_results, guided_follow_up),
        "patient_workflow": _build_patient_workflow(
            ranked_results,
            selected_findings,
            guided_follow_up,
        ),
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


def _score_condition(
    condition: dict[str, Any],
    selected_findings: set[str],
    query: str,
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    signals = condition["signals"]
    matched_findings = [
        finding for finding in selected_findings if finding in signals
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
        "matched_findings": matched_findings,
        "matched_text_search": matched_text_search,
        "ask_next": condition["ask_next"],
        "action_items": _build_result_action_items(condition, matched_findings),
        "sources": [sources[source_id] for source_id in condition["source_ids"]],
    }


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
