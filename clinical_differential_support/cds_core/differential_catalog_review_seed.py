"""Reviewable export shape for the general differential catalog."""

from __future__ import annotations

from typing import Any

from .differential_catalog import CATALOG_VERSION, CONDITIONS, SOURCES
from .differential_catalog_quality import (
    build_general_differential_catalog_quality_report,
)


REVIEW_SEED_FORMAT_VERSION = "general-differential-review-seed-v1"
REVIEW_SEED_EXPORT_COMMAND = "py -B manage.py export_general_differential_review_seed --pretty"


def build_general_differential_review_seed() -> dict[str, Any]:
    quality_report = build_general_differential_catalog_quality_report()
    return {
        "format_version": REVIEW_SEED_FORMAT_VERSION,
        "catalog": {
            "catalog_version": CATALOG_VERSION,
            "condition_count": len(CONDITIONS),
            "source_count": len(SOURCES),
            "quality": quality_report["summary"],
        },
        "safety_scope": {
            "clinician_only": True,
            "review_required_before_publication": True,
            "contains_patient_data": False,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
        },
        "import_policy": {
            "review_status_default": "seed_needs_clinician_review",
            "required_blocking_gate": "validate_general_differential_catalog",
            "source_backed_required": True,
            "patient_identifiers_allowed": False,
        },
        "conditions": [_build_condition_row(condition) for condition in CONDITIONS],
        "sources": [_build_source_row(source_id, source) for source_id, source in SOURCES.items()],
    }


def _build_condition_row(condition: dict[str, Any]) -> dict[str, Any]:
    return {
        "slug": condition["slug"],
        "review_status": "seed_needs_clinician_review",
        "name_zh": condition["name_zh"],
        "name_en": condition["name_en"],
        "system": condition["system"],
        "urgency": condition["urgency"],
        "summary_zh": condition["summary_zh"],
        "summary_en": condition["summary_en"],
        "signals": condition["signals"],
        "synonyms": condition["synonyms"],
        "ask_next": condition["ask_next"],
        "source_ids": condition["source_ids"],
    }


def _build_source_row(source_id: str, source: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "publisher": source["publisher"],
        "title": source["title"],
        "url": source["url"],
    }
