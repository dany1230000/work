"""Coverage-depth review selectors for staff planning."""

from datetime import date, timedelta
from typing import Any

from django.db.models import Count
from django.utils import timezone

from .governance import build_case_validation_rows
from .models import CaseScenario, ChiefComplaint, ClinicalItem, Rule, Source


MIN_CASES_PER_COMPLAINT = 4
MIN_RULES_PER_COMPLAINT = 8
SOURCE_STALE_AFTER_DAYS = 180


def build_coverage_depth_report(today: date | None = None) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    complaints = list(ChiefComplaint.objects.order_by("title"))
    case_rows = build_case_validation_rows()
    case_rows_by_complaint: dict[int, list[dict[str, Any]]] = {}
    for row in case_rows:
        case_rows_by_complaint.setdefault(row["scenario"].chief_complaint_id, []).append(
            row
        )

    complaint_rows = [
        _build_complaint_row(complaint, case_rows_by_complaint, current_date)
        for complaint in complaints
    ]

    items = ClinicalItem.objects.annotate(source_count=Count("sources", distinct=True))
    failed_case_rows = [row for row in case_rows if not row["all_matched"]]
    stale_threshold_date = current_date - timedelta(days=SOURCE_STALE_AFTER_DAYS)
    stale_sources = Source.objects.filter(access_date__lt=stale_threshold_date)

    summary = {
        "chief_complaint_count": len(complaint_rows),
        "clinical_item_count": items.count(),
        "approved_item_count": items.filter(
            status=ClinicalItem.Status.APPROVED
        ).count(),
        "non_approved_count": items.exclude(
            status=ClinicalItem.Status.APPROVED
        ).count(),
        "source_count": Source.objects.count(),
        "source_gap_count": items.filter(source_count=0).count(),
        "review_due_count": items.filter(review_due_at__lte=current_date).count(),
        "rule_count": Rule.objects.filter(active=True).count(),
        "case_count": len(case_rows),
        "failed_case_count": len(failed_case_rows),
        "complaints_with_gaps": sum(1 for row in complaint_rows if row["gap_codes"]),
    }

    return {
        "report_type": "coverage_depth_review",
        "service": "clinical_differential_support",
        "audience": "staff_content_governance",
        "generated_on": current_date.isoformat(),
        "summary": summary,
        "source_freshness": {
            "stale_after_days": SOURCE_STALE_AFTER_DAYS,
            "stale_threshold_date": stale_threshold_date.isoformat(),
            "stale_source_count": stale_sources.count(),
            "missing_publication_date_count": Source.objects.filter(
                publication_date__isnull=True
            ).count(),
        },
        "complaints": complaint_rows,
        "next_actions": _build_depth_next_actions(complaint_rows, summary),
        "safety_scope": {
            "staff_only": True,
            "summary_only": True,
            "no_source_urls": True,
            "no_detailed_clinical_item_text": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
            "no_trading_or_broker_behavior": True,
        },
    }


def _build_complaint_row(
    complaint: ChiefComplaint,
    case_rows_by_complaint: dict[int, list[dict[str, Any]]],
    current_date: date,
) -> dict[str, Any]:
    items = (
        ClinicalItem.objects.filter(chief_complaint=complaint)
        .annotate(source_count=Count("sources", distinct=True))
        .order_by("item_type", "urgency", "title")
    )
    rules = Rule.objects.filter(chief_complaint=complaint, active=True)
    case_count = CaseScenario.objects.filter(
        chief_complaint=complaint,
        active=True,
    ).count()
    complaint_case_rows = case_rows_by_complaint.get(complaint.pk, [])
    failed_case_count = sum(1 for row in complaint_case_rows if not row["all_matched"])
    source_ids = set()
    status_counts = {
        status: items.filter(status=status).count()
        for status, _label in ClinicalItem.Status.choices
    }
    item_type_counts = {
        item_type: items.filter(item_type=item_type).count()
        for item_type, _label in ClinicalItem.ItemType.choices
    }
    for item in items.prefetch_related("sources"):
        source_ids.update(item.sources.values_list("pk", flat=True))

    gap_codes: list[str] = []
    if items.filter(source_count=0).exists():
        gap_codes.append("source_gap")
    if items.exclude(status=ClinicalItem.Status.APPROVED).exists():
        gap_codes.append("non_approved_gap")
    if items.filter(review_due_at__lte=current_date).exists():
        gap_codes.append("review_due_gap")
    if failed_case_count:
        gap_codes.append("case_validation_gap")
    if case_count < MIN_CASES_PER_COMPLAINT:
        gap_codes.append("case_depth_gap")
    if rules.count() < MIN_RULES_PER_COMPLAINT:
        gap_codes.append("rule_depth_gap")

    return {
        "slug": complaint.slug,
        "title": complaint.title,
        "clinical_item_count": items.count(),
        "approved_item_count": status_counts[ClinicalItem.Status.APPROVED],
        "source_count": len(source_ids),
        "rule_count": rules.count(),
        "case_count": case_count,
        "failed_case_count": failed_case_count,
        "status_counts": status_counts,
        "item_type_counts": item_type_counts,
        "gap_codes": gap_codes,
    }


def _build_depth_next_actions(
    complaint_rows: list[dict[str, Any]], summary: dict[str, Any]
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if (
        summary["source_gap_count"]
        or summary["non_approved_count"]
        or summary["review_due_count"]
        or summary["failed_case_count"]
    ):
        actions.append(
            {
                "priority": len(actions) + 1,
                "action_id": "resolve_governance_blockers",
                "status": "ready_to_start",
                "title_zh": "修正治理阻塞",
                "title_en": "Resolve governance blockers",
                "reason_zh": "存在來源、審查、到期或案例驗證阻塞。",
                "reason_en": "Source, approval, due-review, or case-validation blockers exist.",
            }
        )

    if any("case_depth_gap" in row["gap_codes"] for row in complaint_rows):
        actions.append(
            {
                "priority": len(actions) + 1,
                "action_id": "expand_case_validation_matrix",
                "status": "ready_to_start",
                "title_zh": "擴充案例驗證矩陣",
                "title_en": "Expand case validation matrix",
                "reason_zh": "至少一個主訴的 active validation cases 少於 4 個。",
                "reason_en": "At least one chief complaint has fewer than 4 active validation cases.",
            }
        )

    if any("rule_depth_gap" in row["gap_codes"] for row in complaint_rows):
        actions.append(
            {
                "priority": len(actions) + 1,
                "action_id": "expand_rule_coverage",
                "status": "pending_case_matrix",
                "title_zh": "擴充規則覆蓋",
                "title_en": "Expand rule coverage",
                "reason_zh": "至少一個主訴的 active deterministic rules 少於 8 條。",
                "reason_en": "At least one chief complaint has fewer than 8 active deterministic rules.",
            }
        )

    actions.extend(
        [
            {
                "priority": len(actions) + 1,
                "action_id": "audit_source_freshness",
                "status": "ready_to_start",
                "title_zh": "審查來源新鮮度",
                "title_en": "Audit source freshness",
                "reason_zh": "確認來源版本、存取日與需要更新的來源。",
                "reason_en": "Confirm source versions, access dates, and any sources requiring refresh.",
            },
            {
                "priority": len(actions) + 2,
                "action_id": "run_full_regression_and_smoke_checks",
                "status": "pending_depth_updates",
                "title_zh": "執行完整回歸與 smoke check",
                "title_en": "Run full regression and smoke checks",
                "reason_zh": "深度改善後需重新驗證 clinician pages、governance、exports 與 protected routes。",
                "reason_en": "After depth improvements, reverify clinician pages, governance, exports, and protected routes.",
            },
        ]
    )
    return actions
