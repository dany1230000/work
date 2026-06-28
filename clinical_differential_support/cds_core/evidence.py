from django.utils import timezone

from .governance import build_release_readiness_report
from .models import AuditEvent, ReviewRecord, Source


def build_release_evidence_package(now=None, today=None):
    generated_at = now or timezone.now()
    readiness_report = build_release_readiness_report(today=today)
    return {
        "package_type": "release_evidence",
        "service": "clinical_differential_support",
        "generated_at": generated_at.isoformat(),
        "staff_only": True,
        "readiness": {
            "ready_for_handoff": readiness_report["ready_for_handoff"],
            "total_items": readiness_report["total_items"],
            "approved_count": readiness_report["approved_count"],
            "non_approved_count": readiness_report["non_approved_count"],
            "source_gap_count": readiness_report["source_gap_count"],
            "review_due_count": readiness_report["review_due_count"],
            "failed_case_count": readiness_report["failed_case_count"],
        },
        "validation": {
            "case_count": readiness_report["case_count"],
            "failed_case_count": readiness_report["failed_case_count"],
        },
        "governance_record_counts": {
            "sources": Source.objects.count(),
            "review_records": ReviewRecord.objects.count(),
            "audit_events": AuditEvent.objects.count(),
        },
        "exports": {
            "clinical_items_csv": "/review/exports/clinical-items.csv",
            "sources_csv": "/review/exports/sources.csv",
            "release_evidence_json": "/review/exports/release-evidence.json",
            "handoff_report_markdown": "/review/exports/handoff-report.md",
            "handoff_bundle_zip": "/review/exports/handoff-bundle.zip",
            "release_readiness": "/review/readiness/",
        },
        "safety_scope": {
            "no_patient_identifying_data": True,
            "no_diagnosis_or_treatment_orders": True,
            "no_credentials": True,
            "no_trading_or_order_api": True,
            "content_governance_only": True,
        },
    }
