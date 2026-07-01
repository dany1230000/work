"""Quality gates for the general differential catalog."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .differential_catalog import CATALOG_VERSION, CONDITIONS, SOURCES, URGENCY_ORDER


MIN_PUBLIC_CONDITIONS = 50
MIN_PUBLIC_SOURCES = 5
EXPANSION_TARGET_CONDITIONS = 325

REQUIRED_CONDITION_FIELDS = (
    "slug",
    "name_zh",
    "name_en",
    "system",
    "urgency",
    "summary_zh",
    "summary_en",
    "signals",
    "synonyms",
    "ask_next",
    "source_ids",
)
REQUIRED_SOURCE_FIELDS = ("publisher", "title", "url")

SYSTEM_BUCKET_TARGETS = {
    "Cardiovascular": {"tokens": ("Cardiovascular", "Vascular"), "target": 8},
    "Pulmonary": {"tokens": ("Pulmonary", "Respiratory"), "target": 6},
    "Infectious": {"tokens": ("Infectious",), "target": 8},
    "Neurologic": {"tokens": ("Neurologic",), "target": 8},
    "Gastrointestinal/Hepatic": {
        "tokens": ("Gastrointestinal", "Hepatic"),
        "target": 10,
    },
    "Renal/Urologic": {"tokens": ("Renal", "Urologic", "Urinary"), "target": 6},
    "Endocrine/Metabolic": {"tokens": ("Endocrine", "Metabolic"), "target": 6},
    "Hematology/Oncology": {
        "tokens": ("Hematology", "Hematologic", "Oncology"),
        "target": 6,
    },
    "Mental health": {"tokens": ("Mental health",), "target": 6},
    "Toxicology/Environmental": {
        "tokens": ("Toxicology", "Environmental"),
        "target": 6,
    },
    "Skin/Soft tissue": {"tokens": ("Skin", "Soft tissue"), "target": 5},
    "Gynecologic": {"tokens": ("Gynecologic",), "target": 5},
}


def build_general_differential_catalog_quality_report(
    *,
    conditions: list[dict[str, Any]] | None = None,
    sources: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    catalog_conditions = list(conditions if conditions is not None else CONDITIONS)
    catalog_sources = dict(sources if sources is not None else SOURCES)

    blocking_issues = _find_blocking_issues(catalog_conditions, catalog_sources)
    warnings = _find_warnings(catalog_conditions)
    system_counts = Counter(str(condition.get("system", "unknown")) for condition in catalog_conditions)
    urgency_counts = Counter(str(condition.get("urgency", "unknown")) for condition in catalog_conditions)
    system_buckets = _build_system_buckets(catalog_conditions)

    summary = {
        "catalog_version": CATALOG_VERSION,
        "condition_count": len(catalog_conditions),
        "source_count": len(catalog_sources),
        "blocking_issue_count": len(blocking_issues),
        "warning_count": len(warnings),
        "ready_for_public_reference": (
            not blocking_issues
            and len(catalog_conditions) >= MIN_PUBLIC_CONDITIONS
            and len(catalog_sources) >= MIN_PUBLIC_SOURCES
        ),
        "expansion_target_condition_count": EXPANSION_TARGET_CONDITIONS,
    }

    return {
        "report_type": "general_differential_catalog_quality",
        "service": "clinical_differential_support",
        "audience": "clinician_reference_governance",
        "summary": summary,
        "system_counts": dict(sorted(system_counts.items())),
        "urgency_counts": dict(sorted(urgency_counts.items())),
        "system_buckets": system_buckets,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "next_actions": _build_next_actions(summary, system_buckets, warnings),
        "safety_scope": {
            "clinician_only": True,
            "source_backed_catalog_only": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
        },
    }


def _find_blocking_issues(
    conditions: list[dict[str, Any]], sources: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    seen_slugs: set[str] = set()

    for index, condition in enumerate(conditions):
        slug = str(condition.get("slug", f"condition_{index}"))
        if slug in seen_slugs:
            issues.append(
                _issue(
                    "duplicate_condition_slug",
                    slug,
                    "Condition slug must be unique before publication.",
                )
            )
        seen_slugs.add(slug)

        for field in REQUIRED_CONDITION_FIELDS:
            value = condition.get(field)
            if value in (None, "", [], {}):
                issues.append(
                    _issue(
                        "missing_condition_field",
                        slug,
                        f"Condition is missing required field: {field}.",
                    )
                )

        if condition.get("urgency") not in URGENCY_ORDER:
            issues.append(
                _issue(
                    "unknown_urgency",
                    slug,
                    "Urgency must be one of the engine-supported urgency values.",
                )
            )

        for source_id in condition.get("source_ids", []):
            if source_id not in sources:
                issues.append(
                    _issue(
                        "unknown_source_id",
                        slug,
                        f"Condition references unknown source id: {source_id}.",
                    )
                )

    for source_id, source in sources.items():
        for field in REQUIRED_SOURCE_FIELDS:
            if not source.get(field):
                issues.append(
                    _issue(
                        "missing_source_field",
                        source_id,
                        f"Source is missing required field: {field}.",
                    )
                )

    return issues


def _find_warnings(conditions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for condition in conditions:
        slug = str(condition.get("slug", "unknown"))
        if len(condition.get("source_ids", [])) < 2:
            warnings.append(
                _issue(
                    "single_source_condition",
                    slug,
                    "Condition has fewer than two supporting source references.",
                )
            )
        if len(condition.get("synonyms", [])) < 2:
            warnings.append(
                _issue(
                    "low_synonym_depth",
                    slug,
                    "Condition has fewer than two searchable synonyms.",
                )
            )
    return warnings


def _build_system_buckets(
    conditions: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for bucket_name, bucket_config in SYSTEM_BUCKET_TARGETS.items():
        tokens = bucket_config["tokens"]
        count = sum(
            1
            for condition in conditions
            if any(token in str(condition.get("system", "")) for token in tokens)
        )
        target = int(bucket_config["target"])
        buckets[bucket_name] = {
            "condition_count": count,
            "target_count": target,
            "gap_count": max(target - count, 0),
            "status": "target_met" if count >= target else "needs_expansion",
        }
    return buckets


def _build_next_actions(
    summary: dict[str, Any],
    system_buckets: dict[str, dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    expansion_target = summary["expansion_target_condition_count"]
    expansion_done = summary["condition_count"] >= expansion_target
    actions = [
        {
            "priority": 1,
            "action_id": "convert_static_catalog_to_reviewed_data_import",
            "status": "ready_to_start",
            "title_zh": "把靜態 catalog 轉成可審核資料匯入",
            "title_en": "Convert static catalog to reviewed data import",
            "reason_zh": f"{summary['condition_count']} 個條目的 starter catalog 已可用，但大規模擴充需要版本化資料檔、審核欄位與匯入驗證。",
            "reason_en": "The starter catalog is usable; large-scale expansion needs versioned data files, review fields, and import validation.",
        },
        {
            "priority": 2,
            "action_id": f"expand_condition_catalog_to_{expansion_target}",
            "status": "done" if expansion_done else "pending_import_gate",
            "title_zh": f"??? {expansion_target} ????????",
            "title_en": f"Expand to {expansion_target} high-priority differential entries",
            "reason_zh": f"?? {summary['condition_count']} / {expansion_target} ???????????????????????????????????",
            "reason_en": f"Current coverage is {summary['condition_count']} / {expansion_target}; broad first-pass differential support needs more common, emergency, and must-not-miss diseases across specialties.",
        },
    ]

    weakest_bucket = _weakest_bucket(system_buckets)
    if weakest_bucket:
        actions.append(
            {
                "priority": len(actions) + 1,
                "action_id": "fill_weakest_system_bucket",
                "status": "ready_after_import_gate",
                "title_zh": f"補齊 {weakest_bucket['bucket']} 系統缺口",
                "title_en": f"Fill {weakest_bucket['bucket']} system gap",
                "reason_zh": f"目前 {weakest_bucket['condition_count']} / {weakest_bucket['target_count']} 個條目。",
                "reason_en": f"Current coverage is {weakest_bucket['condition_count']} / {weakest_bucket['target_count']} entries.",
            }
        )

    if warnings:
        actions.append(
            {
                "priority": len(actions) + 1,
                "action_id": "deepen_condition_sources_and_synonyms",
                "status": "parallel_after_import_gate",
                "title_zh": "補強來源與搜尋同義詞",
                "title_en": "Deepen condition sources and search synonyms",
                "reason_zh": "部分條目只有單一來源或同義詞深度不足，會影響可信度與搜尋命中。",
                "reason_en": "Some entries have thin source support or limited synonyms, which affects trust and search recall.",
            }
        )

    if not summary["ready_for_public_reference"]:
        actions.insert(
            0,
            {
                "priority": 1,
                "action_id": "resolve_catalog_blockers",
                "status": "blocking",
                "title_zh": "先修正 catalog blocking issues",
                "title_en": "Resolve catalog blocking issues",
                "reason_zh": "blocking issues 未清除前，不應發布新的 catalog 版本。",
                "reason_en": "New catalog versions should not be published while blocking issues remain.",
            },
        )
        for priority, action in enumerate(actions, start=1):
            action["priority"] = priority

    return actions


def _weakest_bucket(system_buckets: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    gaps = [
        {"bucket": bucket, **row}
        for bucket, row in system_buckets.items()
        if row["gap_count"] > 0
    ]
    if not gaps:
        return None
    return sorted(gaps, key=lambda row: (-row["gap_count"], row["bucket"]))[0]


def _issue(code: str, subject: str, message_en: str) -> dict[str, str]:
    return {
        "code": code,
        "subject": subject,
        "message_en": message_en,
    }
