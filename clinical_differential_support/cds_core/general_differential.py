"""General differential evaluator for the broad clinician workbench."""

from __future__ import annotations

from typing import Any

from .differential_catalog import (
    CATALOG_VERSION,
    CONDITIONS,
    DEFAULT_ASK_NEXT,
    SOURCES,
    URGENCY_ORDER,
)


def evaluate_general_differential(raw_findings: dict[str, Any]) -> dict[str, Any]:
    selected_findings = {
        str(finding)
        for finding in raw_findings.get("findings", [])
        if str(finding).strip()
    }
    query = str(raw_findings.get("query", "")).strip().lower()
    results = []

    for condition in CONDITIONS:
        scored = _score_condition(condition, selected_findings, query)
        if scored["score"] <= 0:
            continue
        results.append(scored)

    results.sort(
        key=lambda item: (
            URGENCY_ORDER.get(item["urgency"], 99),
            -item["score"],
            item["name_en"],
        )
    )

    return {
        "results": results[:12],
        "ask_next": _build_global_ask_next(results, selected_findings),
        "coverage": {
            "catalog_version": CATALOG_VERSION,
            "condition_count": len(CONDITIONS),
            "source_count": len(SOURCES),
            "limitation_zh": "這是 starter catalog，不是完整疾病資料庫；未命中不代表排除疾病。",
            "limitation_en": "This is a starter catalog, not a complete disease database; no match does not rule out disease.",
        },
    }


def _score_condition(
    condition: dict[str, Any], selected_findings: set[str], query: str
) -> dict[str, Any]:
    signals = condition["signals"]
    matched_findings = [
        finding for finding in selected_findings if finding in signals
    ]
    score = sum(signals[finding] for finding in matched_findings)
    matched_text_search = _matches_query(condition, query)
    if matched_text_search:
        score += 7

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
        "sources": [SOURCES[source_id] for source_id in condition["source_ids"]],
    }


def _matches_query(condition: dict[str, Any], query: str) -> bool:
    if not query:
        return False
    haystacks = [
        condition["slug"].replace("_", " "),
        condition["name_en"].lower(),
        condition["name_zh"].lower(),
        *(synonym.lower() for synonym in condition.get("synonyms", [])),
    ]
    return any(query in value or value in query for value in haystacks)


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
