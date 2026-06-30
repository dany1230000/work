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

    return {
        "results": results[:12],
        "ask_next": _build_global_ask_next(results, selected_findings),
        "action_checklist": _build_action_checklist(results, selected_findings),
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
