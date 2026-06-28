"""Summary-only next-action selector for product coverage expansion."""

from datetime import date
from typing import Any

from django.db.models import Count
from django.utils import timezone

from .coverage_depth import build_coverage_depth_report
from .governance import build_case_validation_rows
from .models import ChiefComplaint, ClinicalItem
from .source_freshness import build_source_freshness_report


EXPANSION_TARGETS = [
    {"slug": "chest-pain", "title_zh": "胸痛", "title_en": "Chest pain"},
    {"slug": "abdominal-pain", "title_zh": "腹痛", "title_en": "Abdominal pain"},
    {"slug": "dyspnea", "title_zh": "呼吸困難", "title_en": "Dyspnea"},
]


def build_next_action_plan(today: date | None = None) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    complaints = list(ChiefComplaint.objects.order_by("title"))
    current_count = len(complaints)
    current_slugs = {complaint.slug for complaint in complaints}
    headache_only = current_slugs == {"headache"}
    next_target = _next_expansion_target(current_slugs)
    expansion_complete = next_target["slug"] == "coverage-depth-review"
    minimum_next_stage_count = current_count + (0 if expansion_complete else 1)

    items = ClinicalItem.objects.annotate(source_count=Count("sources", distinct=True))
    case_rows = build_case_validation_rows()
    failed_case_rows = [row for row in case_rows if not row["all_matched"]]
    governance = {
        "clinical_item_count": items.count(),
        "case_validation_count": len(case_rows),
        "failed_case_count": len(failed_case_rows),
        "source_gap_count": items.filter(source_count=0).count(),
        "non_approved_count": items.exclude(
            status=ClinicalItem.Status.APPROVED
        ).count(),
        "review_due_count": items.filter(review_due_at__lte=current_date).count(),
    }
    downstream_readiness = _build_downstream_readiness(
        enabled=expansion_complete,
        today=current_date,
    )
    completion_status = _build_completion_status(
        headache_only=headache_only,
        expansion_complete=expansion_complete,
        governance=governance,
        downstream_readiness=downstream_readiness,
    )

    return {
        "plan_type": "next_action_plan",
        "service": "clinical_differential_support",
        "audience": "staff_content_governance",
        "generated_on": current_date.isoformat(),
        "completion_status": completion_status,
        "coverage": {
            "current_count": current_count,
            "minimum_next_stage_count": minimum_next_stage_count,
            "gap_count": max(minimum_next_stage_count - current_count, 0),
            "headache_only": headache_only,
            "current_chief_complaints": [
                {
                    "slug": complaint.slug,
                    "title": complaint.title,
                    "summary": complaint.summary,
                }
                for complaint in complaints
            ],
            "next_target": next_target,
        },
        "governance": governance,
        "downstream_readiness": downstream_readiness,
        "next_actions": build_next_actions(
            headache_only=headache_only,
            next_target=next_target,
            governance=governance,
            downstream_readiness=downstream_readiness,
        ),
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


def build_next_actions(
    headache_only: bool,
    next_target: dict[str, str],
    governance: dict[str, int],
    downstream_readiness: dict[str, Any],
) -> list[dict[str, Any]]:
    if next_target["slug"] != "coverage-depth-review":
        return _build_expansion_actions(headache_only, next_target)

    if _has_governance_blockers(governance):
        return [
            _action(
                1,
                "resolve_governance_blockers",
                "ready_to_start",
                "修正治理 blocker",
                "Resolve governance blockers",
                "還有未核准、來源缺口、到期審查或失敗病例驗證。",
                "Non-approved, source-gap, due-review, or failed-case blockers remain.",
                "Resolve governance blockers before downstream handoff gates.",
            ),
            _regression_action(2, "pending_governance_fixes"),
        ]

    if downstream_readiness["status"] == "coverage_depth_gaps":
        return [
            _action(
                1,
                "run_coverage_depth_review",
                "ready_to_start",
                "執行覆蓋深度審查",
                "Run coverage depth review",
                "Coverage-depth report still has complaint-level gaps.",
                "Coverage-depth report still has complaint-level gaps.",
                "Use Coverage Depth Review to identify case, rule, or source-depth gaps.",
            ),
            _regression_action(2, "pending_depth_review"),
        ]

    if downstream_readiness["status"] == "source_refresh_required":
        return [
            _action(
                1,
                "audit_source_freshness",
                "ready_to_start",
                "審查來源新鮮度",
                "Audit source freshness",
                "至少一個來源已超過 freshness threshold。",
                "At least one source is beyond the freshness threshold.",
                "Refresh or review stale source metadata before final regression.",
            ),
            _regression_action(2, "pending_source_review"),
        ]

    return [_regression_action(1, "ready_to_run")]


def _build_expansion_actions(
    headache_only: bool, next_target: dict[str, str]
) -> list[dict[str, Any]]:
    target_title_zh = next_target["title_zh"]
    target_title_en = next_target["title_en"]
    target_action_slug = next_target["slug"].replace("-", "_")
    coverage_reason_zh = (
        "目前只有 1 個主訴，還不是多主訴專業版。"
        if headache_only
        else f"多主訴擴充已開始，下一個缺口是 {target_title_zh}。"
    )
    coverage_reason_en = (
        "Coverage is currently headache-only, so this is not the final multi-complaint version."
        if headache_only
        else f"Multi-complaint expansion has started; the {target_title_en.lower()} module still needs completion."
    )

    return [
        _action(
            1,
            f"add_{target_action_slug}_module",
            "ready_to_start",
            f"新增 {target_title_zh} 模組",
            f"Add {target_title_en.lower()} module",
            coverage_reason_zh,
            coverage_reason_en,
            f"Create {target_title_en.lower()} chief-complaint data, intake fields, rules, validation cases, and governance review flow.",
        ),
        _action(
            2,
            f"collect_official_{target_action_slug}_sources",
            "required_before_clinical_content",
            f"收集 {target_title_zh} 官方來源",
            f"Collect official {target_title_en.lower()} sources",
            "臨床擴充必須先有可追溯來源。",
            "Clinical expansion needs traceable sources before content is added.",
            "Add source metadata and keep next-action JSON summary-only.",
        ),
        _action(
            3,
            f"create_{target_action_slug}_cases_and_rules",
            "pending_sources",
            f"建立 {target_title_zh} 規則與驗證病例",
            f"Create {target_title_en.lower()} rules and validation cases",
            "每個新主訴都需要非病人 fixture 驗證 rule output。",
            "Each new chief complaint needs non-patient fixtures to validate rule output.",
            "Add fixture cases, expected outputs, and regression tests.",
        ),
        _action(
            4,
            "submit_new_content_to_review_queue",
            "pending_content",
            "送交 reviewer queue",
            "Submit new content to review queue",
            "新增內容必須等 staff review 後才可視為 approved。",
            "New content must not be treated as approved until staff review is recorded.",
            "Drafts, source links, and review records are visible in governance views.",
        ),
        _regression_action(5, "pending_implementation"),
    ]


def _build_downstream_readiness(enabled: bool, today: date) -> dict[str, Any]:
    if not enabled:
        return {
            "status": "not_applicable_until_expansion_complete",
            "coverage_depth": None,
            "source_freshness": None,
        }

    coverage_report = build_coverage_depth_report(today=today)
    source_report = build_source_freshness_report(today=today)
    coverage_summary = coverage_report["summary"]
    source_summary = source_report["summary"]
    source_policy = source_report["publication_date_gap_policy"]
    coverage_first_action = coverage_report["next_actions"][0]["action_id"]
    source_first_action = source_report["next_actions"][0]["action_id"]

    if coverage_summary["complaints_with_gaps"]:
        status = "coverage_depth_gaps"
    elif source_summary["stale_source_count"]:
        status = "source_refresh_required"
    else:
        status = "ready_for_regression_gate"

    return {
        "status": status,
        "coverage_depth": {
            "chief_complaint_count": coverage_summary["chief_complaint_count"],
            "complaints_with_gaps": coverage_summary["complaints_with_gaps"],
            "case_count": coverage_summary["case_count"],
            "failed_case_count": coverage_summary["failed_case_count"],
            "rule_count": coverage_summary["rule_count"],
            "first_action": coverage_first_action,
        },
        "source_freshness": {
            "source_count": source_summary["source_count"],
            "stale_source_count": source_summary["stale_source_count"],
            "missing_publication_date_count": source_summary[
                "missing_publication_date_count"
            ],
            "publication_date_gap_policy": source_policy["policy_id"],
            "publication_date_gap_review_status": source_policy["review_status"],
            "first_action": source_first_action,
        },
    }


def _build_completion_status(
    headache_only: bool,
    expansion_complete: bool,
    governance: dict[str, int],
    downstream_readiness: dict[str, Any],
) -> str:
    if headache_only:
        return "not_final_beyond_headache"
    if not expansion_complete:
        return "expansion_in_progress"
    if _has_governance_blockers(governance):
        return "governance_blocked"
    return downstream_readiness["status"]


def _has_governance_blockers(governance: dict[str, int]) -> bool:
    return bool(
        governance["source_gap_count"]
        or governance["non_approved_count"]
        or governance["review_due_count"]
        or governance["failed_case_count"]
    )


def _regression_action(priority: int, status: str) -> dict[str, Any]:
    return _action(
        priority,
        "run_full_regression_and_smoke_checks",
        status,
        "執行完整回歸與 smoke check",
        "Run full regression and smoke checks",
        "下游審查已整理完成，下一步是驗證整個產品仍可運作。",
        "Downstream audits are clear; the next practical gate is full regression and live smoke verification.",
        "Django tests, Django check, live smoke, and database next-action status pass.",
    )


def _action(
    priority: int,
    action_id: str,
    status: str,
    title_zh: str,
    title_en: str,
    reason_zh: str,
    reason_en: str,
    deliverable_en: str,
) -> dict[str, Any]:
    return {
        "priority": priority,
        "action_id": action_id,
        "status": status,
        "title_zh": title_zh,
        "title_en": title_en,
        "reason_zh": reason_zh,
        "reason_en": reason_en,
        "deliverable_en": deliverable_en,
    }


def _next_expansion_target(current_slugs: set[str]) -> dict[str, str]:
    for target in EXPANSION_TARGETS:
        if target["slug"] not in current_slugs:
            return target
    return {
        "slug": "coverage-depth-review",
        "title_zh": "覆蓋深度審查",
        "title_en": "Coverage depth review",
    }
