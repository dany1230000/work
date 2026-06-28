"""Read-only clinical governance dashboard selectors."""

from datetime import date
from typing import Any

from django.db.models import Count, Q
from django.utils import timezone

from .models import AuditEvent, CaseScenario, ClinicalItem, ReviewRecord, Rule
from .services import evaluate_case_scenario


def build_review_dashboard(today: date | None = None) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    items = ClinicalItem.objects.all().prefetch_related("sources")

    status_counts = {
        status: items.filter(status=status).count()
        for status, _label in ClinicalItem.Status.choices
    }
    source_gap_items = list(
        items.annotate(source_count=Count("sources"))
        .filter(source_count=0)
        .order_by("item_type", "urgency", "title")
    )
    review_due_items = list(
        items.filter(review_due_at__lte=current_date).order_by(
            "review_due_at", "item_type", "urgency", "title"
        )
    )

    return {
        "total_items": items.count(),
        "status_counts": status_counts,
        "clinical_items": list(
            items.select_related("chief_complaint").order_by(
                "item_type", "urgency", "title"
            )
        ),
        "source_gap_items": source_gap_items,
        "review_due_items": review_due_items,
        "case_rows": build_case_validation_rows(),
        "recent_audit_events": list(
            AuditEvent.objects.select_related("clinical_item", "actor")[:10]
        ),
    }


def build_release_readiness_report(today: date | None = None) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    items = (
        ClinicalItem.objects.select_related("chief_complaint")
        .prefetch_related("sources")
        .annotate(source_count=Count("sources", distinct=True))
    )
    ordered_items = items.order_by("item_type", "urgency", "title")
    non_approved_items = list(
        ordered_items.exclude(status=ClinicalItem.Status.APPROVED)
    )
    source_gap_items = list(
        ordered_items.filter(source_count=0).order_by("urgency", "title")
    )
    review_due_items = list(
        ordered_items.filter(review_due_at__lte=current_date).order_by(
            "review_due_at", "urgency", "title"
        )
    )
    case_rows = build_case_validation_rows()
    failed_case_rows = [row for row in case_rows if not row["all_matched"]]

    ready_for_handoff = not (
        non_approved_items
        or source_gap_items
        or review_due_items
        or failed_case_rows
    )

    return {
        "ready_for_handoff": ready_for_handoff,
        "total_items": ordered_items.count(),
        "approved_count": ordered_items.filter(
            status=ClinicalItem.Status.APPROVED
        ).count(),
        "non_approved_count": len(non_approved_items),
        "source_gap_count": len(source_gap_items),
        "review_due_count": len(review_due_items),
        "failed_case_count": len(failed_case_rows),
        "case_count": len(case_rows),
        "non_approved_items": non_approved_items,
        "source_gap_items": source_gap_items,
        "review_due_items": review_due_items,
        "failed_case_rows": failed_case_rows,
    }


def build_review_queue(
    filters: dict[str, str] | None = None, today: date | None = None
) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    raw_filters = filters or {}
    valid_statuses = {value for value, _label in ClinicalItem.Status.choices}
    valid_urgencies = {value for value, _label in ClinicalItem.Urgency.choices}
    status = raw_filters.get("status", "").strip()
    urgency = raw_filters.get("urgency", "").strip()
    query = raw_filters.get("q", "").strip()
    if status not in valid_statuses:
        status = ""
    if urgency not in valid_urgencies:
        urgency = ""

    items = (
        ClinicalItem.objects.select_related("chief_complaint")
        .prefetch_related("sources")
        .annotate(source_count=Count("sources", distinct=True))
    )
    ordered_items = items.order_by("item_type", "urgency", "title")
    result_items = ordered_items

    if status:
        result_items = result_items.filter(status=status)
    if urgency:
        result_items = result_items.filter(urgency=urgency)
    if query:
        result_items = result_items.filter(
            Q(title__icontains=query)
            | Q(title_zh__icontains=query)
            | Q(title_en__icontains=query)
            | Q(summary__icontains=query)
            | Q(summary_zh__icontains=query)
            | Q(summary_en__icontains=query)
            | Q(sources__publisher__icontains=query)
            | Q(sources__title__icontains=query)
            | Q(sources__version_label__icontains=query)
        ).distinct()

    source_gap_items = list(
        ordered_items.filter(source_count=0).order_by("urgency", "title")
    )
    review_due_items = list(
        ordered_items.filter(review_due_at__lte=current_date).order_by(
            "review_due_at", "urgency", "title"
        )
    )
    changes_requested_items = list(
        ordered_items.filter(
            status=ClinicalItem.Status.DRAFT,
            auditevent__event_type=AuditEvent.EventType.CHANGES_REQUESTED,
        )
        .distinct()
        .order_by("urgency", "title")
    )
    results = list(result_items)
    result_ids = {item.pk for item in results}

    return {
        "filters": {
            "status": status,
            "urgency": urgency,
            "q": query,
        },
        "status_choices": [
            {"value": value, "label": label, "selected": value == status}
            for value, label in ClinicalItem.Status.choices
        ],
        "urgency_choices": [
            {"value": value, "label": label, "selected": value == urgency}
            for value, label in ClinicalItem.Urgency.choices
        ],
        "source_gap_items": source_gap_items,
        "review_due_items": review_due_items,
        "filtered_source_gap_items": [
            item for item in source_gap_items if item.pk in result_ids
        ],
        "filtered_review_due_items": [
            item for item in review_due_items if item.pk in result_ids
        ],
        "changes_requested_items": changes_requested_items,
        "filtered_changes_requested_items": [
            item for item in changes_requested_items if item.pk in result_ids
        ],
        "draft_items": list(
            ordered_items.filter(status=ClinicalItem.Status.DRAFT).order_by(
                "urgency", "title"
            )
        ),
        "in_review_items": list(
            ordered_items.filter(status=ClinicalItem.Status.IN_REVIEW).order_by(
                "urgency", "title"
            )
        ),
        "results": results,
        "recent_review_records": list(
            ReviewRecord.objects.select_related("clinical_item", "reviewer")[:10]
        ),
    }


def build_case_validation_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scenarios = CaseScenario.objects.filter(active=True).select_related(
        "chief_complaint"
    )
    for scenario in scenarios:
        evaluation = evaluate_case_scenario(scenario)
        expected_outputs = evaluation["expected_outputs"]
        missing_titles = [
            expected["title"]
            for expected in expected_outputs
            if not expected["matched"]
        ]
        rows.append(
            {
                "scenario": scenario,
                "expected_count": len(expected_outputs),
                "matched_count": len(expected_outputs) - len(missing_titles),
                "missing_titles": missing_titles,
                "all_matched": not missing_titles,
            }
        )
    return rows


def build_review_item_detail(item: ClinicalItem) -> dict[str, Any]:
    return {
        "item": item,
        "sources": list(item.sources.all()),
        "rules": list(
            Rule.objects.filter(output_item=item).order_by("priority", "slug")
        ),
        "audit_events": list(
            AuditEvent.objects.filter(clinical_item=item).select_related("actor")[:10]
        ),
    }
