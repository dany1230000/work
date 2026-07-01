"""Local launch status selector for the clinician-support MVP."""

from datetime import date
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.db import connection
from django.db.utils import DatabaseError, OperationalError, ProgrammingError
from django.utils import timezone

from .final_verification import (
    RECORDER_COMMAND,
    build_final_verification_gate,
    load_latest_evidence,
)
from .models import ChiefComplaint, ClinicalItem
from .next_actions import build_next_action_plan


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
INITIALIZE_LOCAL_DATABASE_COMMAND = (
    r"py -B .\clinical_differential_support\manage.py migrate --run-syncdb && "
    r"py -B .\clinical_differential_support\manage.py loaddata "
    r"headache_mvp chest_pain_mvp abdominal_pain_mvp dyspnea_mvp"
)
CREATE_STAFF_COMMAND = r"py -B .\clinical_differential_support\manage.py createsuperuser"
CREATE_STAFF_REVIEWER_ENTRY_COMMAND = (
    r"clinical_differential_support\Create_Staff_Reviewer.cmd"
)
START_SERVER_COMMAND = r"clinical_differential_support\Start_Local_Server.cmd"
NEXT_STEP_BATCH_COMMAND = r"clinical_differential_support\Next_Step.cmd"
FINAL_CHECK_BATCH_COMMAND = r"clinical_differential_support\Final_Check.cmd"
DEPLOY_STATUS_BATCH_COMMAND = r"clinical_differential_support\Deploy_Status.cmd"
PROJECT_COMPLETION_COMMAND = (
    r"py -B .\clinical_differential_support\scripts\project_completion_status.py"
)
DEPLOYMENT_STATUS_COMMAND = (
    r"py -B .\clinical_differential_support\scripts\deployment_status.py"
)
SETUP_ASSISTANT_COMMAND = (
    r"py -B .\clinical_differential_support\scripts\local_setup_assistant.py"
)

STATUS_LABELS_ZH = {
    "done": "已完成",
    "current": "現在",
    "ready": "可執行",
    "locked": "等待",
}
STATUS_LABELS_EN = {
    "done": "Done",
    "current": "Now",
    "ready": "Ready",
    "locked": "Waiting",
}

LOCAL_OPERATION_NEXT_ACTION_STATUSES = {
    "ready_for_regression_gate",
    "general_catalog_import_ready",
}


def build_local_launch_status(
    base_url: str = DEFAULT_BASE_URL,
    today: date | None = None,
    evidence_path: str | Path | None = None,
) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    normalized_base_url = base_url.rstrip("/")
    urls = _build_urls(normalized_base_url)
    database_state = _inspect_local_database()
    database_ready = bool(database_state["database_ready"])
    if database_ready:
        staff_account_exists = get_user_model().objects.filter(is_staff=True).exists()
        chief_complaint_count = ChiefComplaint.objects.count()
        clinical_item_count = ClinicalItem.objects.count()
        next_action_plan = build_next_action_plan(today=current_date)
        final_gate = build_final_verification_gate(
            today=current_date,
            evidence_path=evidence_path,
        )
    else:
        staff_account_exists = False
        chief_complaint_count = 0
        clinical_item_count = 0
        next_action_plan = _build_database_setup_next_action_plan(current_date)
        final_gate = _build_database_setup_final_gate(current_date, evidence_path)

    report = {
        "report_type": "local_launch_status",
        "service": "clinical_differential_support",
        "generated_on": current_date.isoformat(),
        "base_url": normalized_base_url,
        "urls": urls,
        "environment": {
            "database_ready": database_ready,
            "missing_database_tables": database_state["missing_tables"],
            "database_error": database_state.get("error", ""),
            "staff_account_exists": staff_account_exists,
            "chief_complaint_count": chief_complaint_count,
            "clinical_item_count": clinical_item_count,
        },
        "next_actions": {
            "completion_status": next_action_plan["completion_status"],
            "first_action": next_action_plan["next_actions"][0]["action_id"],
            "first_action_status": next_action_plan["next_actions"][0]["status"],
            "allows_local_operation": _next_action_allows_local_operation(
                next_action_plan["completion_status"],
            ),
            "url": urls["next_actions"],
        },
        "final_verification": {
            "gate_status": final_gate["gate_status"],
            "latest_evidence_status": final_gate["latest_evidence"]["status"],
            "command_count": final_gate["latest_evidence"]["command_count"],
            "failed_command_count": final_gate["latest_evidence"].get(
                "failed_command_count",
                0,
            ),
            "url": urls["final_verification"],
        },
        "operator_summary": {},
        "environment_checks": [],
        "manual_blockers": [],
        "safety_scope": {
            "local_only": True,
            "staff_only_for_governance": True,
            "does_not_create_credentials": True,
            "does_not_bypass_authentication": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_trading_or_broker_behavior": True,
        },
    }
    report["operator_summary"] = _build_operator_summary(report)
    report["environment_checks"] = _build_environment_checks(report)
    report["manual_blockers"] = _build_manual_blockers(report)
    report["steps"] = _build_steps(report)
    report["current_step"] = _find_current_step(report["steps"])
    report["next_step"] = report["current_step"]
    report["setup_assistant"] = _build_setup_assistant(report)
    report["project_completion"] = _build_project_completion_link(report)
    report["deployment_status"] = _build_deployment_status_link(report)
    return report


def format_local_launch_status(report: dict[str, Any]) -> str:
    lines = [
        "本機啟動狀態 / Local Launch Status",
        f"服務 / Service: {report['service']}",
        f"首頁 / Home: {report['urls']['home']}",
        f"治理登入 / Staff login: {report['urls']['staff_login']}",
        (
            "Final Verification: "
            f"{report['final_verification']['gate_status']} / "
            f"{report['final_verification']['latest_evidence_status']}"
        ),
        f"控制台狀態 / Control status: {report['operator_summary']['status']}",
        "",
        "環境檢查 / Environment Checks",
    ]

    for check in report["environment_checks"]:
        lines.append(
            f"- {check['title_zh']} / {check['title_en']}: {check['status']} "
            f"({check['value']})"
        )

    if report["manual_blockers"]:
        lines.append("")
        lines.append("手動阻擋 / Manual Blockers")
        for blocker in report["manual_blockers"]:
            lines.append(
                f"- {blocker['title_zh']} / {blocker['title_en']}: "
                f"{blocker['detail_zh']} / {blocker['detail_en']}"
            )
            if blocker.get("entry_command"):
                lines.append(f"  Windows entry: {blocker['entry_command']}")
            if blocker.get("raw_command"):
                lines.append(f"  Raw Django command: {blocker['raw_command']}")

    lines.extend(
        [
        "",
        "一步一步 / Step-by-step",
        ]
    )

    for step in report["steps"]:
        zh_status = STATUS_LABELS_ZH[step["status"]]
        en_status = STATUS_LABELS_EN[step["status"]]
        lines.append(
            f"步驟 {step['step_number']}/{step['total_steps']} "
            f"[{zh_status} / {en_status}] "
            f"{step['title_zh']} / {step['title_en']}"
        )
        if step["status"] == "current":
            lines.append("  現在做這個 / Do this now")
        if step.get("command"):
            lines.append(f"  執行 / Run: {step['command']}")
        if step.get("entry_command") and step.get("entry_command") != step.get("command"):
            lines.append(f"  Windows entry: {step['entry_command']}")
        if step.get("raw_command"):
            lines.append(f"  Raw Django command: {step['raw_command']}")
        if step.get("url"):
            lines.append(f"  打開 / Open: {step['url']}")
        if step.get("secondary_url"):
            lines.append(f"  下載 / Download: {step['secondary_url']}")
        lines.append(f"  說明 / Detail: {step['detail_zh']} / {step['detail_en']}")

    current = report["current_step"]
    lines.extend(
        [
            "",
            (
                "下一步 / Next step: "
                f"步驟 {current['step_number']}/{current['total_steps']} "
                f"{current['title_zh']} / {current['title_en']}"
            ),
        ]
    )
    return "\n".join(lines)


def _build_urls(base_url: str) -> dict[str, str]:
    return {
        "home": f"{base_url}/",
        "launch_guide": f"{base_url}/launch/",
        "completion_gate": f"{base_url}/completion/",
        "deployment_status": f"{base_url}/deployment/",
        "health": f"{base_url}/health/",
        "staff_login": f"{base_url}/review/login/",
        "review_dashboard": f"{base_url}/review/",
        "next_actions": f"{base_url}/review/next-actions/",
        "final_verification": f"{base_url}/review/final-verification/",
        "handoff_bundle": f"{base_url}/review/exports/handoff-bundle.zip",
    }


def _build_operator_summary(report: dict[str, Any]) -> dict[str, str]:
    database_ready = report["environment"]["database_ready"]
    staff_exists = report["environment"]["staff_account_exists"]
    evidence_verified = _evidence_verified(report)

    if not database_ready:
        status = "needs_database_setup"
        title_zh = "初始化本機資料庫"
        title_en = "Initialize the local database"
    elif not staff_exists:
        status = "needs_manual_setup"
        title_zh = "需要先建立本機審核者"
        title_en = "Create the local reviewer first"
    elif not evidence_verified:
        status = "needs_verification"
        title_zh = "需要重新產生驗收證據"
        title_en = "Refresh final verification evidence"
    else:
        status = "ready_for_local_operation"
        title_zh = "可進入本機操作"
        title_en = "Ready for local operation"

    return {
        "status": status,
        "title_zh": title_zh,
        "title_en": title_en,
    }


def _build_environment_checks(report: dict[str, Any]) -> list[dict[str, str]]:
    database_ready = report["environment"]["database_ready"]
    missing_tables = report["environment"].get("missing_database_tables", [])
    staff_exists = report["environment"]["staff_account_exists"]
    chief_count = report["environment"]["chief_complaint_count"]
    item_count = report["environment"]["clinical_item_count"]
    evidence_verified = _evidence_verified(report)
    next_action_ready = _next_action_allows_local_operation(
        report["next_actions"]["completion_status"],
    )

    return [
        {
            "check_id": "local_database",
            "status": "passed" if database_ready else "action_required",
            "title_zh": "本機資料庫",
            "title_en": "Local database",
            "value": "ready"
            if database_ready
            else f"missing tables: {', '.join(missing_tables)}",
            "detail_zh": "需要先建立 SQLite schema 並載入內建臨床 fixture。",
            "detail_en": "Requires SQLite schema and bundled clinical fixtures.",
        },
        {
            "check_id": "staff_reviewer",
            "status": "passed" if staff_exists else "action_required",
            "title_zh": "Staff reviewer 帳號",
            "title_en": "Staff reviewer account",
            "value": "exists"
            if staff_exists
            else ("blocked_by_database_setup" if not database_ready else "missing"),
            "detail_zh": "治理頁面需要 staff 帳號。",
            "detail_en": "Governance pages require a staff account.",
        },
        {
            "check_id": "final_evidence",
            "status": "passed" if evidence_verified else "action_required",
            "title_zh": "最終驗收證據",
            "title_en": "Final verification evidence",
            "value": report["final_verification"]["latest_evidence_status"],
            "detail_zh": "需要 verified 且 failed command count 為 0。",
            "detail_en": "Requires verified evidence with zero failed commands.",
        },
        {
            "check_id": "governed_content",
            "status": "passed"
            if chief_count > 0 and item_count > 0
            else "action_required",
            "title_zh": "治理內容資料",
            "title_en": "Governed content data",
            "value": f"{chief_count} complaints / {item_count} items",
            "detail_zh": "需要已載入主訴與臨床項目。",
            "detail_en": "Requires loaded chief complaints and clinical items.",
        },
        {
            "check_id": "next_action_gate",
            "status": "passed" if next_action_ready else "action_required",
            "title_zh": "下一步 gate",
            "title_en": "Next-action gate",
            "value": report["next_actions"]["completion_status"],
            "detail_zh": "需要 downstream readiness 已進入 regression gate。",
            "detail_en": "Requires downstream readiness to reach the regression gate.",
        },
    ]


def _build_manual_blockers(report: dict[str, Any]) -> list[dict[str, str | bool]]:
    if not report["environment"]["database_ready"]:
        return [
            {
                "action_id": "initialize_local_database",
                "title_zh": "初始化本機資料庫",
                "title_en": "Initialize the local database",
                "detail_zh": "先建立本機 SQLite schema 並載入內建 fixture，狀態中心才能讀取下一步。",
                "detail_en": "Create the local SQLite schema and load bundled fixtures before status tools read the next step.",
                "command": INITIALIZE_LOCAL_DATABASE_COMMAND,
                "manual_only": False,
                "does_not_store_credentials": True,
            }
        ]

    if not report["environment"]["staff_account_exists"]:
        return [
            {
                "action_id": "create_staff_reviewer",
                "title_zh": "建立本機 staff reviewer 帳號",
                "title_en": "Create a local staff reviewer account",
                "detail_zh": "密碼必須由使用者在本機互動輸入；系統不會自動建立或保存密碼。",
                "detail_en": "The password must be entered locally by the user; the system does not create or store it.",
                "entry_command": CREATE_STAFF_REVIEWER_ENTRY_COMMAND,
                "command": CREATE_STAFF_REVIEWER_ENTRY_COMMAND,
                "raw_command": CREATE_STAFF_COMMAND,
                "manual_only": True,
                "does_not_store_credentials": True,
            }
        ]

    if not _evidence_verified(report):
        return [
            {
                "action_id": "run_final_verification_recorder",
                "title_zh": "重新產生最終驗收證據",
                "title_en": "Refresh final verification evidence",
                "detail_zh": "執行 recorder 重新跑測試、system check、live smoke 與 next-action shell。",
                "detail_en": "Run the recorder to rerun tests, system check, live smoke, and next-action shell.",
                "command": RECORDER_COMMAND,
                "manual_only": False,
                "does_not_store_credentials": True,
            }
        ]

    return []


def _build_setup_assistant(report: dict[str, Any]) -> dict[str, str | int]:
    is_ready = report["operator_summary"]["status"] == "ready_for_local_operation"
    return {
        "title_zh": "本機設定助手",
        "title_en": "Local Setup Assistant",
        "status": "ready" if is_ready else "setup_required",
        "exit_code": 0 if is_ready else 2,
        "command": SETUP_ASSISTANT_COMMAND,
        "windows_entry_command": NEXT_STEP_BATCH_COMMAND,
        "url": report["urls"]["launch_guide"],
        "next_action_id": str(report["next_step"]["action_id"]),
    }


def _build_project_completion_link(report: dict[str, Any]) -> dict[str, str | int]:
    is_ready = report["operator_summary"]["status"] == "ready_for_local_operation"
    return {
        "title_zh": "最終版完成判斷",
        "title_en": "Final Project Gate",
        "status": "final_complete_candidate" if is_ready else "manual_setup_required",
        "exit_code": 0 if is_ready else 2,
        "command": PROJECT_COMPLETION_COMMAND,
        "windows_entry_command": FINAL_CHECK_BATCH_COMMAND,
        "url": report["urls"]["completion_gate"],
    }


def _build_deployment_status_link(report: dict[str, Any]) -> dict[str, str | int]:
    return {
        "title_zh": "部署操作中心",
        "title_en": "Deployment Operations Center",
        "status": "available",
        "exit_code": 2,
        "command": DEPLOYMENT_STATUS_COMMAND,
        "windows_entry_command": DEPLOY_STATUS_BATCH_COMMAND,
        "url": report["urls"]["deployment_status"],
    }


def _evidence_verified(report: dict[str, Any]) -> bool:
    return (
        report["final_verification"]["latest_evidence_status"] == "verified"
        and report["final_verification"]["failed_command_count"] == 0
    )


def _next_action_allows_local_operation(completion_status: str) -> bool:
    return completion_status in LOCAL_OPERATION_NEXT_ACTION_STATUSES


def _build_steps(report: dict[str, Any]) -> list[dict[str, str | int]]:
    database_ready = report["environment"]["database_ready"]
    staff_exists = report["environment"]["staff_account_exists"]
    evidence_verified = _evidence_verified(report)
    current_action = _current_action_id(
        database_ready=database_ready,
        staff_exists=staff_exists,
        evidence_verified=evidence_verified,
    )

    definitions = [
        {
            "action_id": "initialize_local_database",
            "title_zh": "初始化本機資料庫",
            "title_en": "Initialize the local database",
            "detail_zh": "建立 SQLite schema 並載入頭痛、胸痛、腹痛、呼吸困難 fixture。",
            "detail_en": "Create the SQLite schema and load headache, chest-pain, abdominal-pain, and dyspnea fixtures.",
            "command": INITIALIZE_LOCAL_DATABASE_COMMAND,
            "command_kind": "local_shell",
            "manual_required": False,
            "url": report["urls"]["launch_guide"],
            "done": database_ready,
        },
        {
            "action_id": "create_staff_reviewer",
            "title_zh": "建立本機 staff reviewer 帳號",
            "title_en": "Create a local staff reviewer account",
            "detail_zh": "治理頁面需要 staff 登入。先建立本機審核者帳號。",
            "detail_en": "Staff governance pages require login. Create the local reviewer first.",
            "entry_command": CREATE_STAFF_REVIEWER_ENTRY_COMMAND,
            "command": CREATE_STAFF_REVIEWER_ENTRY_COMMAND,
            "raw_command": CREATE_STAFF_COMMAND,
            "command_kind": "manual_shell",
            "manual_required": True,
            "url": report["urls"]["staff_login"],
            "done": staff_exists,
        },
        {
            "action_id": "run_final_verification_recorder",
            "title_zh": "確認最終驗收證據",
            "title_en": "Verify final evidence",
            "detail_zh": "如果 evidence 不是 verified，就重跑最終驗收紀錄器。",
            "detail_en": "If evidence is not verified, rerun the final verification recorder.",
            "command": RECORDER_COMMAND,
            "command_kind": "local_shell",
            "manual_required": False,
            "url": report["urls"]["final_verification"],
            "done": evidence_verified,
        },
        {
            "action_id": "start_local_server",
            "title_zh": "啟動本機 server",
            "title_en": "Start the local server",
            "detail_zh": "啟動後瀏覽器會開到本機首頁。",
            "detail_en": "After launch, the browser opens the local home page.",
            "command": START_SERVER_COMMAND,
            "command_kind": "local_shell",
            "manual_required": False,
            "url": report["urls"]["home"],
            "done": False,
        },
        {
            "action_id": "login_staff_reviewer",
            "title_zh": "登入 staff reviewer",
            "title_en": "Log in as staff reviewer",
            "detail_zh": "使用剛建立的本機 staff reviewer 帳號登入。",
            "detail_en": "Use the local staff reviewer account you just created.",
            "command": "",
            "command_kind": "browser",
            "manual_required": True,
            "url": report["urls"]["staff_login"],
            "done": False,
        },
        {
            "action_id": "open_next_action_workbench",
            "title_zh": "查看 Next Action Workbench",
            "title_en": "Open the Next Action Workbench",
            "detail_zh": "確認系統現在建議的下一個專案動作。",
            "detail_en": "Confirm the current project next action.",
            "command": "",
            "command_kind": "browser",
            "manual_required": False,
            "url": report["urls"]["next_actions"],
            "done": False,
        },
        {
            "action_id": "open_final_verification_gate",
            "title_zh": "查看 Final Verification Gate 並下載交接包",
            "title_en": "Open the Final Verification Gate and download the handoff bundle",
            "detail_zh": "確認驗收狀態後，必要時下載 handoff bundle。",
            "detail_en": "Review the verification gate, then download the handoff bundle if needed.",
            "command": "",
            "command_kind": "browser",
            "manual_required": False,
            "url": report["urls"]["final_verification"],
            "secondary_url": report["urls"]["handoff_bundle"],
            "done": False,
        },
    ]

    total_steps = len(definitions)
    steps = []
    for index, definition in enumerate(definitions, start=1):
        action_id = str(definition["action_id"])
        status = _step_status(
            action_id=action_id,
            is_done=bool(definition["done"]),
            current_action=current_action,
            database_ready=database_ready,
            staff_exists=staff_exists,
            evidence_verified=evidence_verified,
        )
        step = {
            "step_number": index,
            "total_steps": total_steps,
            "status": status,
        }
        step.update({key: value for key, value in definition.items() if key != "done"})
        steps.append(step)
    return steps


def _current_action_id(
    database_ready: bool,
    staff_exists: bool,
    evidence_verified: bool,
) -> str:
    if not database_ready:
        return "initialize_local_database"
    if not staff_exists:
        return "create_staff_reviewer"
    if not evidence_verified:
        return "run_final_verification_recorder"
    return "start_local_server"


def _step_status(
    action_id: str,
    is_done: bool,
    current_action: str,
    database_ready: bool,
    staff_exists: bool,
    evidence_verified: bool,
) -> str:
    if is_done:
        return "done"
    if action_id == current_action:
        return "current"
    if not database_ready:
        return "locked"
    if action_id in {
        "initialize_local_database",
        "create_staff_reviewer",
        "run_final_verification_recorder",
    }:
        return "locked"
    if staff_exists and evidence_verified:
        return "ready"
    return "locked"


def _find_current_step(steps: list[dict[str, Any]]) -> dict[str, Any]:
    for step in steps:
        if step["status"] == "current":
            return step
    for step in steps:
        if step["status"] == "ready":
            return step
    return steps[-1]


def _inspect_local_database() -> dict[str, Any]:
    required_tables = _required_local_tables()
    try:
        existing_tables = set(connection.introspection.table_names())
    except (DatabaseError, OperationalError, ProgrammingError, OSError) as error:
        return {
            "database_ready": False,
            "missing_tables": sorted(required_tables),
            "error": str(error),
        }

    missing_tables = sorted(required_tables - existing_tables)
    return {
        "database_ready": not missing_tables,
        "missing_tables": missing_tables,
        "error": "",
    }


def _required_local_tables() -> set[str]:
    return {
        get_user_model()._meta.db_table,
        ChiefComplaint._meta.db_table,
        ClinicalItem._meta.db_table,
    }


def _build_database_setup_next_action_plan(current_date: date) -> dict[str, Any]:
    return {
        "plan_type": "next_action_plan",
        "service": "clinical_differential_support",
        "audience": "staff_content_governance",
        "generated_on": current_date.isoformat(),
        "completion_status": "local_database_setup_required",
        "coverage": {
            "current_count": 0,
            "minimum_next_stage_count": 4,
            "gap_count": 4,
            "headache_only": False,
            "current_chief_complaints": [],
            "next_target": {
                "slug": "initialize-local-database",
                "title_zh": "初始化本機資料庫",
                "title_en": "Initialize local database",
            },
        },
        "governance": {
            "clinical_item_count": 0,
            "case_validation_count": 0,
            "failed_case_count": 0,
            "source_gap_count": 0,
            "non_approved_count": 0,
            "review_due_count": 0,
        },
        "downstream_readiness": {
            "status": "blocked_until_local_database_initialized",
            "coverage_depth": None,
            "source_freshness": None,
        },
        "next_actions": [
            {
                "priority": 1,
                "action_id": "initialize_local_database",
                "status": "ready_to_start",
                "title_zh": "初始化本機資料庫",
                "title_en": "Initialize the local database",
                "reason_zh": "本機 SQLite schema 尚未建立，無法讀取治理內容或下一步狀態。",
                "reason_en": "The local SQLite schema is not initialized, so governed content and next-step status cannot be read.",
                "deliverable_en": "Run migrations and load bundled fixtures.",
            }
        ],
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


def _build_database_setup_final_gate(
    current_date: date,
    evidence_path: str | Path | None,
) -> dict[str, Any]:
    return {
        "report_type": "final_verification_gate",
        "service": "clinical_differential_support",
        "audience": "staff_content_governance",
        "generated_on": current_date.isoformat(),
        "gate_status": "blocked_until_local_database_initialized",
        "readiness": {
            "ready_for_handoff": False,
            "clinical_item_count": 0,
            "approved_count": 0,
            "source_gap_count": 0,
            "review_due_count": 0,
            "failed_case_count": 0,
        },
        "next_action_gate": {
            "completion_status": "local_database_setup_required",
            "first_action": "initialize_local_database",
            "first_action_status": "ready_to_start",
            "downstream_status": "blocked_until_local_database_initialized",
        },
        "required_commands": [],
        "next_action": {
            "action_id": "initialize_local_database",
            "status": "ready_to_start",
            "title_zh": "初始化本機資料庫",
            "title_en": "Initialize the local database",
        },
        "latest_evidence": load_latest_evidence(evidence_path=evidence_path),
        "handoff_exports": {},
        "evidence_policy": {
            "external_command_output_required": True,
            "do_not_embed_command_output_in_app": True,
            "recorder_command": RECORDER_COMMAND,
            "future_recorder_needed_for_persistent_evidence": False,
        },
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
