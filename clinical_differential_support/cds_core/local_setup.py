"""Local setup assistant selector for the clinician-support MVP."""

from datetime import date
from pathlib import Path
from typing import Any

from django.utils import timezone

from .local_launch import DEFAULT_BASE_URL, build_local_launch_status


def build_local_setup_assistant_report(
    base_url: str = DEFAULT_BASE_URL,
    today: date | None = None,
    evidence_path: str | Path | None = None,
) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    launch_report = build_local_launch_status(
        base_url=base_url,
        today=current_date,
        evidence_path=evidence_path,
    )
    is_ready = launch_report["operator_summary"]["status"] == "ready_for_local_operation"

    return {
        "report_type": "local_setup_assistant",
        "service": launch_report["service"],
        "generated_on": launch_report["generated_on"],
        "status": "ready" if is_ready else "setup_required",
        "exit_code": 0 if is_ready else 2,
        "launch_control_url": launch_report["urls"]["launch_guide"],
        "next_step": launch_report["next_step"],
        "operator_summary": launch_report["operator_summary"],
        "environment_checks": launch_report["environment_checks"],
        "manual_blockers": launch_report["manual_blockers"],
        "final_verification": launch_report["final_verification"],
        "next_actions": launch_report["next_actions"],
        "safety_scope": {
            "local_only": True,
            "staff_only_for_governance": True,
            "does_not_create_credentials": True,
            "does_not_print_credentials": True,
            "does_not_store_plaintext_credentials": True,
            "does_not_bypass_authentication": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_trading_or_broker_behavior": True,
        },
    }


def format_local_setup_assistant_report(report: dict[str, Any]) -> str:
    next_step = report["next_step"]
    lines = [
        "本機設定助手 / Local Setup Assistant",
        f"服務 / Service: {report['service']}",
        f"狀態 / Status: {report['status']}",
        f"exit_code={report['exit_code']}",
        f"Launch Control: {report['launch_control_url']}",
        "",
        (
            "下一步 / Next step: "
            f"步驟 {next_step['step_number']}/{next_step['total_steps']} "
            f"{next_step['title_zh']} / {next_step['title_en']}"
        ),
    ]

    if next_step.get("command"):
        lines.append(f"命令 / Command: {next_step['command']}")
    if next_step.get("entry_command") and next_step.get("entry_command") != next_step.get("command"):
        lines.append(f"Windows entry: {next_step['entry_command']}")
    if next_step.get("raw_command"):
        lines.append(f"Raw Django command: {next_step['raw_command']}")
    if next_step.get("url"):
        lines.append(f"網址 / URL: {next_step['url']}")

    lines.extend(
        [
            f"說明 / Detail: {next_step['detail_zh']} / {next_step['detail_en']}",
            "",
            "環境檢查 / Environment Checks",
        ]
    )

    for check in report["environment_checks"]:
        lines.append(
            f"- {check['title_zh']} / {check['title_en']}: "
            f"{check['status']} ({check['value']})"
        )

    lines.append("")
    lines.append("手動阻擋 / Manual Blockers")
    if report["manual_blockers"]:
        for blocker in report["manual_blockers"]:
            lines.append(
                f"- {blocker['title_zh']} / {blocker['title_en']}: "
                f"{blocker['detail_zh']} / {blocker['detail_en']}"
            )
            if blocker.get("entry_command"):
                lines.append(f"  Windows entry: {blocker['entry_command']}")
            if blocker.get("raw_command"):
                lines.append(f"  Raw Django command: {blocker['raw_command']}")
            if blocker.get("command") and not blocker.get("entry_command"):
                lines.append(f"  命令 / Command: {blocker['command']}")
    else:
        lines.append("- 無 / None")

    lines.extend(
        [
            "",
            "驗收證據 / Verification Evidence",
            f"- Gate: {report['final_verification']['gate_status']}",
            f"- Evidence: {report['final_verification']['latest_evidence_status']}",
            f"- Commands: {report['final_verification']['command_count']}",
            f"- Failed: {report['final_verification']['failed_command_count']}",
            "",
            "安全範圍 / Safety Scope",
            "- 不會建立、列印或保存密碼 / Does not create, print, or store passwords.",
            "- 不新增病人識別資料、診斷指令、治療指令或用藥指令。",
            "- No patient-identifying data, diagnosis orders, treatment orders, or medication orders.",
            "- No trading, broker API, live orders, or real capital behavior.",
        ]
    )
    return "\n".join(lines)
