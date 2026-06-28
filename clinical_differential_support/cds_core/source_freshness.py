"""Source freshness audit selectors for staff governance."""

from datetime import date, timedelta
from typing import Any

from django.db.models import Count
from django.utils import timezone

from .models import Source


STALE_AFTER_DAYS = 180


def build_source_freshness_report(today: date | None = None) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    stale_threshold_date = current_date - timedelta(days=STALE_AFTER_DAYS)
    sources = Source.objects.annotate(
        clinical_item_count=Count("clinicalitem", distinct=True)
    ).order_by("publisher", "title")
    source_rows = [
        _build_source_row(source, current_date, stale_threshold_date)
        for source in sources
    ]
    stale_count = sum(1 for row in source_rows if row["freshness_status"] == "stale")
    missing_publication_date_count = sum(
        1
        for row in source_rows
        if row["publication_date_status"] == "not_listed_in_fixture"
    )

    return {
        "report_type": "source_freshness_audit",
        "service": "clinical_differential_support",
        "audience": "staff_content_governance",
        "generated_on": current_date.isoformat(),
        "summary": {
            "source_count": len(source_rows),
            "current_source_count": len(source_rows) - stale_count,
            "stale_source_count": stale_count,
            "missing_publication_date_count": missing_publication_date_count,
            "stale_after_days": STALE_AFTER_DAYS,
            "stale_threshold_date": stale_threshold_date.isoformat(),
        },
        "publication_date_gap_policy": _build_publication_date_gap_policy(
            missing_publication_date_count
        ),
        "sources": source_rows,
        "next_actions": _build_source_next_actions(
            stale_count=stale_count,
            missing_publication_date_count=missing_publication_date_count,
        ),
        "safety_scope": {
            "staff_only": True,
            "metadata_only": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
            "no_automatic_external_writes": True,
            "no_trading_or_broker_behavior": True,
        },
    }


def _build_source_row(
    source: Source, current_date: date, stale_threshold_date: date
) -> dict[str, Any]:
    days_since_access = (current_date - source.access_date).days
    freshness_status = (
        "stale" if source.access_date < stale_threshold_date else "current"
    )
    publication_date_status = (
        "recorded" if source.publication_date else "not_listed_in_fixture"
    )
    publication_date_review_status = (
        "recorded" if source.publication_date else "manual_review_required"
    )

    return {
        "id": source.pk,
        "publisher": source.publisher,
        "title": source.title,
        "version_label": source.version_label,
        "url": source.url,
        "publication_date": (
            source.publication_date.isoformat()
            if source.publication_date
            else None
        ),
        "publication_date_status": publication_date_status,
        "publication_date_review_status": publication_date_review_status,
        "publication_date_gap_is_stale_blocker": False,
        "access_date": source.access_date.isoformat(),
        "days_since_access": days_since_access,
        "freshness_status": freshness_status,
        "clinical_item_count": source.clinical_item_count,
    }


def _build_publication_date_gap_policy(
    missing_publication_date_count: int,
) -> dict[str, Any]:
    return {
        "policy_id": "do_not_infer_missing_publication_dates",
        "missing_publication_date_count": missing_publication_date_count,
        "review_status": (
            "documented_pending_manual_verification"
            if missing_publication_date_count
            else "no_missing_publication_dates"
        ),
        "blank_dates_are_not_stale_blockers": True,
        "manual_review_trigger": (
            "record_an_official_date_only_when_the_source_page_explicitly_lists_one"
        ),
        "rule_zh": (
            "不要從 access date、copyright year、URL 或頁面 metadata 推論缺少的 "
            "publication date。"
        ),
        "rule_en": (
            "Do not infer missing publication dates from access dates, copyright "
            "years, URL paths, or page metadata."
        ),
        "completion_condition_zh": (
            "若來源未逾期，已記錄的空白 publication date 是 metadata 限制，"
            "不是來源新鮮度 blocker。"
        ),
        "completion_condition_en": (
            "When no source is stale, documented blank publication dates are a "
            "known metadata limitation rather than a freshness blocker."
        ),
    }


def _build_source_next_actions(
    stale_count: int, missing_publication_date_count: int
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if stale_count:
        actions.append(
            {
                "priority": len(actions) + 1,
                "action_id": "refresh_stale_sources",
                "status": "ready_to_start",
                "title_zh": "刷新逾期來源",
                "title_en": "Refresh stale sources",
                "reason_zh": "至少一個來源的 access date 已超過 180 天。",
                "reason_en": "At least one source access date is older than 180 days.",
            }
        )

    regression_status = "pending_source_review" if stale_count else "ready_to_run"
    if missing_publication_date_count:
        missing_date_note_zh = (
            f"{missing_publication_date_count} 個來源缺 publication date，"
            "已依政策標示為人工查核；不推論日期，也不作為 stale blocker。"
        )
        missing_date_note_en = (
            f"{missing_publication_date_count} sources lack a publication date and "
            "are documented for manual review; do not infer dates and do not treat "
            "them as stale blockers."
        )
    else:
        missing_date_note_zh = "所有來源都有 publication date 或不需缺口標記。"
        missing_date_note_en = "No publication-date gap remains."

    actions.append(
        {
            "priority": len(actions) + 1,
            "action_id": "run_full_regression_and_smoke_checks",
            "status": regression_status,
            "title_zh": "執行完整回歸與 smoke check",
            "title_en": "Run full regression and smoke checks",
            "reason_zh": missing_date_note_zh,
            "reason_en": missing_date_note_en,
        }
    )
    return actions
