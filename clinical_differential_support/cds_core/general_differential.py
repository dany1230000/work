"""General differential evaluator for the broad clinician workbench."""

from __future__ import annotations

from typing import Any

from .differential_catalog import DEFAULT_ASK_NEXT, URGENCY_ORDER
from .differential_catalog_data import get_general_differential_runtime_catalog


def get_general_differential_catalog_summary() -> dict[str, Any]:
    runtime_catalog = get_general_differential_runtime_catalog()
    return {
        "catalog_version": runtime_catalog["catalog_version"],
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
        "coverage": {
            "catalog_version": runtime_catalog["catalog_version"],
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
    for result in results[:3]:
        for prompt in result["ask_next"]:
            if prompt not in prompts:
                prompts.append(prompt)
    if not selected_findings:
        return prompts[:4]
    return prompts[:7]
