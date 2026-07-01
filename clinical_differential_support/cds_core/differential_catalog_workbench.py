"""Staff governance workbench for general differential catalog expansion."""

from __future__ import annotations

from typing import Any

from .differential_catalog_import import BATCH_TEMPLATE_FORMAT_VERSION
from .differential_catalog_quality import (
    build_general_differential_catalog_quality_report,
)
from .differential_catalog_review_seed import (
    REVIEW_SEED_EXPORT_COMMAND,
    REVIEW_SEED_FORMAT_VERSION,
)


NEXT_BATCH_RECOMMENDED_SIZE = 12
LOW_COVERAGE_BUCKET_LIMIT = 6


def build_general_differential_import_workbench() -> dict[str, Any]:
    quality = build_general_differential_catalog_quality_report()
    summary = quality["summary"]
    lowest_coverage_buckets = _build_lowest_coverage_buckets(
        quality["system_buckets"]
    )

    return {
        "report_type": "general_differential_import_workbench",
        "service": "clinical_differential_support",
        "audience": "clinician_reference_governance",
        "summary": {
            **summary,
            "batch_template_format_version": BATCH_TEMPLATE_FORMAT_VERSION,
            "review_seed_format_version": REVIEW_SEED_FORMAT_VERSION,
            "catalog_target_met": (
                summary["condition_count"]
                >= summary["expansion_target_condition_count"]
            ),
            "condition_total_label": f"{summary['condition_count']} conditions",
            "source_total_label": f"{summary['source_count']} sources",
        },
        "next_batch": {
            "strategy": "expand_lowest_coverage_buckets_first",
            "strategy_zh": "先補目前覆蓋最薄的專科桶，且只接受已審核、可追溯來源的資料。",
            "strategy_en": (
                "Expand the lowest-coverage specialty buckets first, using only "
                "reviewed and source-backed catalog rows."
            ),
            "recommended_batch_size": NEXT_BATCH_RECOMMENDED_SIZE,
            "lowest_coverage_buckets": lowest_coverage_buckets,
        },
        "import_pipeline": _build_import_pipeline(),
        "safety_scope": {
            **quality["safety_scope"],
            "staff_only": True,
            "contains_patient_data": False,
            "review_required_before_publication": True,
        },
        "exports": {
            "json_filename": "general-differential-import.json",
        },
    }


def _build_lowest_coverage_buckets(
    system_buckets: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for system, bucket in system_buckets.items():
        rows.append(
            {
                "system": system,
                "condition_count": bucket["condition_count"],
                "target_count": bucket["target_count"],
                "gap_count": bucket["gap_count"],
                "status": bucket["status"],
                "recommended_batch_size": NEXT_BATCH_RECOMMENDED_SIZE,
                "review_focus_zh": "新增前先確認中文/英文名稱、鑑別訊號、下一步問題與來源。",
                "review_focus_en": (
                    "Before adding rows, verify bilingual names, differentiating "
                    "signals, ask-next prompts, and source links."
                ),
            }
        )
    return sorted(rows, key=lambda row: (row["condition_count"], row["system"]))[
        :LOW_COVERAGE_BUCKET_LIMIT
    ]


def _build_import_pipeline() -> list[dict[str, str]]:
    return [
        {
            "step_id": "export_review_seed",
            "label_zh": "匯出目前審核基準",
            "label_en": "Export current review seed",
            "command": REVIEW_SEED_EXPORT_COMMAND,
            "expected_result": "review-seed JSON containing the current catalog baseline",
        },
        {
            "step_id": "export_batch_template",
            "label_zh": "匯出下一批匯入模板",
            "label_en": "Export next reviewed-batch template",
            "command": "py -B manage.py export_general_differential_batch_template --pretty",
            "expected_result": "empty reviewed-batch template with required fields",
        },
        {
            "step_id": "validate_review_seed",
            "label_zh": "驗證審核基準",
            "label_en": "Validate review seed",
            "command": "py -B manage.py validate_general_differential_review_seed",
            "expected_result": "READY general differential review seed",
        },
        {
            "step_id": "validate_reviewed_catalog_data",
            "label_zh": "驗證已審核 catalog 資料",
            "label_en": "Validate reviewed catalog data",
            "command": "py -B manage.py validate_general_differential_reviewed_catalog_data",
            "expected_result": "READY reviewed general differential catalog data",
        },
        {
            "step_id": "validate_runtime_catalog",
            "label_zh": "驗證執行中的通用鑑別 catalog",
            "label_en": "Validate runtime general differential catalog",
            "command": "py -B manage.py validate_general_differential_catalog",
            "expected_result": "READY general differential catalog",
        },
    ]
