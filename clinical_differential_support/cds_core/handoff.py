from .evidence import build_release_evidence_package


def build_handoff_report_markdown(now=None, today=None, package=None):
    package = package or build_release_evidence_package(now=now, today=today)
    readiness = package["readiness"]
    validation = package["validation"]
    counts = package["governance_record_counts"]
    exports = package["exports"]
    safety_scope = package["safety_scope"]
    status = (
        "Ready for handoff"
        if readiness["ready_for_handoff"]
        else "Needs governance work"
    )
    case_validations_passed = (
        validation["case_count"] - validation["failed_case_count"]
    )

    lines = [
        "# Clinical Differential Support Handoff Report",
        "",
        "## 交付狀態 / Handoff Status",
        f"- Status: {status}",
        f"- Generated at: {package['generated_at']}",
        f"- Staff-only: {'yes' if package['staff_only'] else 'no'}",
        "",
        "## 治理摘要 / Governance Summary",
        f"- Clinical items: {readiness['total_items']}",
        f"- Approved items: {readiness['approved_count']}",
        f"- Non-approved items: {readiness['non_approved_count']}",
        f"- Source gaps: {readiness['source_gap_count']}",
        f"- Review due: {readiness['review_due_count']}",
        f"- Case validation failures: {readiness['failed_case_count']}",
        f"- Case validations passed: {case_validations_passed}",
        f"- Source records: {counts['sources']}",
        f"- Review records: {counts['review_records']}",
        f"- Audit events: {counts['audit_events']}",
        "",
        "## 匯出路徑 / Export Routes",
        f"- Clinical item CSV: {exports['clinical_items_csv']}",
        f"- Source CSV: {exports['sources_csv']}",
        f"- Release evidence JSON: {exports['release_evidence_json']}",
        f"- Handoff report Markdown: {exports['handoff_report_markdown']}",
        f"- Handoff bundle ZIP: {exports['handoff_bundle_zip']}",
        f"- Release readiness page: {exports['release_readiness']}",
        "",
        "## 安全範圍 / Safety Scope",
        "- Content governance only: "
        f"{'yes' if safety_scope['content_governance_only'] else 'no'}",
        "- No patient-identifying data: "
        f"{'yes' if safety_scope['no_patient_identifying_data'] else 'no'}",
        "- No diagnosis or treatment orders: "
        f"{'yes' if safety_scope['no_diagnosis_or_treatment_orders'] else 'no'}",
        f"- No credentials: {'yes' if safety_scope['no_credentials'] else 'no'}",
        "- No trading or order API behavior: "
        f"{'yes' if safety_scope['no_trading_or_order_api'] else 'no'}",
        "",
        "## 注意 / Notes",
        "- This report is summary-only and intentionally excludes detailed clinical item text.",
        "- The MVP remains local clinical-reference support for qualified medical professionals.",
        "",
    ]
    return "\n".join(lines)
