"""Import validation helpers for reviewable differential catalog payloads."""

from __future__ import annotations

from typing import Any

from .differential_catalog_review_seed import REVIEW_SEED_FORMAT_VERSION


BATCH_TEMPLATE_FORMAT_VERSION = "general-differential-review-batch-v1"
REQUIRED_CONDITION_FIELDS = (
    "slug",
    "review_status",
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
REQUIRED_SOURCE_FIELDS = ("source_id", "publisher", "title", "url")


def validate_general_differential_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    format_version = payload.get("format_version")
    if format_version not in {REVIEW_SEED_FORMAT_VERSION, BATCH_TEMPLATE_FORMAT_VERSION}:
        issues.append(
            _issue(
                "unsupported_format_version",
                str(format_version),
                "Payload format_version is not supported.",
            )
        )

    safety_scope = payload.get("safety_scope", {})
    if safety_scope.get("contains_patient_data") is not False:
        issues.append(
            _issue(
                "patient_data_not_allowed",
                "safety_scope.contains_patient_data",
                "Catalog import payloads must not contain patient data.",
            )
        )

    conditions = list(payload.get("conditions", []))
    sources = list(payload.get("sources", []))
    source_ids = _source_ids(sources, issues)
    _validate_conditions(conditions, source_ids, issues)

    return {
        "valid": not issues,
        "summary": {
            "format_version": format_version,
            "condition_count": len(conditions),
            "source_count": len(sources),
            "blocking_issue_count": len(issues),
        },
        "blocking_issues": issues,
    }


def build_general_differential_batch_template() -> dict[str, Any]:
    return {
        "format_version": BATCH_TEMPLATE_FORMAT_VERSION,
        "catalog": {
            "catalog_version": "general-differential-batch-template",
            "condition_count": 1,
            "source_count": 1,
        },
        "safety_scope": {
            "clinician_only": True,
            "review_required_before_publication": True,
            "contains_patient_data": False,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
        },
        "sources": [
            {
                "source_id": "replace_with_source_id",
                "publisher": "Replace with publisher",
                "title": "Replace with source title",
                "url": "https://example.org/replace-with-source",
            }
        ],
        "conditions": [
            {
                "slug": "replace_with_condition_slug",
                "review_status": "draft_needs_clinician_review",
                "name_zh": "替換為中文疾病名稱",
                "name_en": "Replace with English condition name",
                "system": "Replace with system",
                "urgency": "emergent|urgent|soon|routine",
                "summary_zh": "替換為中文臨床摘要；不得包含病人識別資料。",
                "summary_en": "Replace with English clinical summary; no patient identifiers.",
                "signals": {"replace_with_finding_key": 1},
                "synonyms": ["replace synonym"],
                "ask_next": ["Replace with a clinician-facing ask-next prompt."],
                "source_ids": ["replace_with_source_id"],
            }
        ],
    }


def _source_ids(sources: list[dict[str, Any]], issues: list[dict[str, str]]) -> set[str]:
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        subject = str(source.get("source_id", f"source_{index}"))
        for field in REQUIRED_SOURCE_FIELDS:
            if not source.get(field):
                issues.append(
                    _issue(
                        "missing_source_field",
                        subject,
                        f"Source is missing required field: {field}.",
                    )
                )
        if subject in source_ids:
            issues.append(
                _issue(
                    "duplicate_source_id",
                    subject,
                    "Source id must be unique.",
                )
            )
        source_ids.add(subject)
    return source_ids


def _validate_conditions(
    conditions: list[dict[str, Any]],
    source_ids: set[str],
    issues: list[dict[str, str]],
) -> None:
    seen_slugs: set[str] = set()
    for index, condition in enumerate(conditions):
        slug = str(condition.get("slug", f"condition_{index}"))
        if slug in seen_slugs:
            issues.append(_issue("duplicate_condition_slug", slug, "Condition slug must be unique."))
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

        for source_id in condition.get("source_ids", []):
            if source_id not in source_ids:
                issues.append(
                    _issue(
                        "unknown_source_id",
                        slug,
                        f"Condition references unknown source id: {source_id}.",
                    )
                )


def _issue(code: str, subject: str, message_en: str) -> dict[str, str]:
    return {
        "code": code,
        "subject": subject,
        "message_en": message_en,
    }
