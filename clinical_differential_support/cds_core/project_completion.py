"""Final project completion gate for the clinician-support MVP."""

from datetime import date
from pathlib import Path
from typing import Any

from django.utils import timezone

from .local_launch import (
    CREATE_STAFF_COMMAND,
    CREATE_STAFF_REVIEWER_ENTRY_COMMAND,
    DEFAULT_BASE_URL,
    DEPLOY_STATUS_BATCH_COMMAND,
    DEPLOYMENT_STATUS_COMMAND,
    FINAL_CHECK_BATCH_COMMAND,
    PROJECT_COMPLETION_COMMAND,
)
from .local_setup import build_local_setup_assistant_report


def build_project_completion_report(
    base_url: str = DEFAULT_BASE_URL,
    today: date | None = None,
    evidence_path: str | Path | None = None,
) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    normalized_base_url = base_url.rstrip("/")
    setup_report = build_local_setup_assistant_report(
        base_url=normalized_base_url,
        today=current_date,
        evidence_path=evidence_path,
    )
    completion_checks = _build_completion_checks(setup_report)
    is_complete = all(check["status"] == "passed" for check in completion_checks)
    completion_url = f"{normalized_base_url}/completion/"

    return {
        "report_type": "project_completion_gate",
        "service": setup_report["service"],
        "generated_on": setup_report["generated_on"],
        "status": "final_complete" if is_complete else "manual_setup_required",
        "exit_code": 0 if is_complete else 2,
        "completion_url": completion_url,
        "launch_control_url": setup_report["launch_control_url"],
        "completion_checks": completion_checks,
        "manual_blockers": [] if is_complete else setup_report["manual_blockers"],
        "next_action": _build_next_action(
            setup_report=setup_report,
            completion_url=completion_url,
            is_complete=is_complete,
        ),
        "final_check": {
            "command": FINAL_CHECK_BATCH_COMMAND,
            "shell_command": PROJECT_COMPLETION_COMMAND,
            "url": completion_url,
        },
        "deployment_status": {
            "title_zh": "部署操作中心",
            "title_en": "Deployment Operations Center",
            "status": "available",
            "command": DEPLOYMENT_STATUS_COMMAND,
            "windows_entry_command": DEPLOY_STATUS_BATCH_COMMAND,
            "url": f"{normalized_base_url}/deployment/",
        },
        "final_verification": setup_report["final_verification"],
        "next_actions": setup_report["next_actions"],
        "safety_scope": {
            "local_only": True,
            "summary_only": True,
            "does_not_create_credentials": True,
            "does_not_print_credentials": True,
            "does_not_store_plaintext_credentials": True,
            "does_not_bypass_authentication": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
            "no_trading_or_broker_behavior": True,
        },
    }


def format_project_completion_report(report: dict[str, Any]) -> str:
    next_action = report["next_action"]
    lines = [
        "最終版完成判斷 / Final Project Gate",
        f"服務 / Service: {report['service']}",
        f"狀態 / Status: {report['status']}",
        f"exit_code={report['exit_code']}",
        f"Completion URL: {report['completion_url']}",
        f"Launch Control: {report['launch_control_url']}",
        f"Windows command: {report['final_check']['command']}",
        f"Shell command: {report['final_check']['shell_command']}",
        "",
        "完成條件 / Completion Checks",
    ]

    for check in report["completion_checks"]:
        lines.append(
            f"- {check['title_zh']} / {check['title_en']}: "
            f"{check['status']} ({check['value']})"
        )

    lines.extend(
        [
            "",
            (
                "下一步 / Next action: "
                f"{next_action['action_id']} - "
                f"{next_action['title_zh']} / {next_action['title_en']}"
            ),
        ]
    )
    if next_action.get("command"):
        lines.append(f"命令 / Command: {next_action['command']}")
    if next_action.get("raw_command"):
        lines.append(f"Raw Django command: {next_action['raw_command']}")
    if next_action.get("url"):
        lines.append(f"網址 / URL: {next_action['url']}")
    lines.append(f"說明 / Detail: {next_action['detail_zh']} / {next_action['detail_en']}")

    lines.extend(
        [
            "",
            "安全範圍 / Safety Scope",
            "- 不會建立、列印或保存密碼 / Does not create, print, or store passwords.",
            "- 不新增病人識別資料、診斷指令、治療指令或用藥指令。",
            "- No patient-identifying data, diagnosis orders, treatment orders, or medication orders.",
            "- No trading, broker API, live orders, or real capital behavior.",
        ]
    )
    return "\n".join(lines)


def _build_completion_checks(setup_report: dict[str, Any]) -> list[dict[str, str]]:
    env_checks = {
        check["check_id"]: check for check in setup_report["environment_checks"]
    }
    final_verification = setup_report["final_verification"]
    next_actions = setup_report["next_actions"]

    staff_check = env_checks["staff_reviewer"]
    content_check = env_checks["governed_content"]
    return [
        {
            "check_id": "staff_reviewer",
            "status": staff_check["status"],
            "title_zh": "Staff reviewer 帳號",
            "title_en": "Staff reviewer account",
            "value": staff_check["value"],
        },
        {
            "check_id": "final_verification_gate",
            "status": (
                "passed"
                if final_verification["gate_status"] == "ready_for_final_verification"
                else "action_required"
            ),
            "title_zh": "Final Verification Gate",
            "title_en": "Final Verification Gate",
            "value": final_verification["gate_status"],
        },
        {
            "check_id": "final_evidence",
            "status": (
                "passed"
                if final_verification["latest_evidence_status"] == "verified"
                and final_verification["failed_command_count"] == 0
                else "action_required"
            ),
            "title_zh": "最終驗收證據",
            "title_en": "Final verification evidence",
            "value": final_verification["latest_evidence_status"],
        },
        {
            "check_id": "governed_content",
            "status": content_check["status"],
            "title_zh": "治理內容資料",
            "title_en": "Governed content data",
            "value": content_check["value"],
        },
        {
            "check_id": "next_action_gate",
            "status": (
                "passed"
                if next_actions["completion_status"] == "ready_for_regression_gate"
                else "action_required"
            ),
            "title_zh": "下一步 gate",
            "title_en": "Next-action gate",
            "value": next_actions["completion_status"],
        },
    ]


def _build_next_action(
    setup_report: dict[str, Any],
    completion_url: str,
    is_complete: bool,
) -> dict[str, str]:
    if is_complete:
        return {
            "action_id": "project_final_complete",
            "status": "done",
            "title_zh": "專案最終版已完成",
            "title_en": "Project final version is complete",
            "detail_zh": "所有本機最終版條件都已通過。",
            "detail_en": "All local final-version checks have passed.",
            "command": "",
            "raw_command": "",
            "url": completion_url,
        }

    step = setup_report["next_step"]
    entry_command = str(step.get("entry_command", ""))
    raw_command = str(step.get("raw_command", ""))
    command = entry_command or str(step.get("command", ""))
    if str(step["action_id"]) == "create_staff_reviewer":
        command = CREATE_STAFF_REVIEWER_ENTRY_COMMAND
        raw_command = raw_command or CREATE_STAFF_COMMAND

    return {
        "action_id": str(step["action_id"]),
        "status": str(step["status"]),
        "title_zh": str(step["title_zh"]),
        "title_en": str(step["title_en"]),
        "detail_zh": str(step["detail_zh"]),
        "detail_en": str(step["detail_en"]),
        "command": command,
        "raw_command": raw_command,
        "url": str(step.get("url", "")),
    }
