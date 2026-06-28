"""Final verification gate selector for staff handoff planning."""

from datetime import date
import json
from pathlib import Path
from typing import Any

from django.utils import timezone

from .governance import build_release_readiness_report
from .next_actions import build_next_action_plan


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_PATH = (
    PROJECT_DIR / "verification_artifacts" / "final-verification-evidence.json"
)

FULL_REGRESSION_COMMAND = r"py -B .\clinical_differential_support\manage.py test -v 2"
DJANGO_CHECK_COMMAND = r"py -B .\clinical_differential_support\manage.py check"
SMOKE_CHECK_COMMAND = (
    r"py -B .\clinical_differential_support\scripts\smoke_check.py "
    r"--base-url http://127.0.0.1:8000"
)
NEXT_ACTION_SHELL_COMMAND = (
    r'py -B .\clinical_differential_support\manage.py shell -c "'
    r"from cds_core.next_actions import build_next_action_plan; "
    r"plan=build_next_action_plan(); print(plan['completion_status']); "
    r"print(plan['next_actions'][0]['action_id'])"
    r'"'
)
RECORDER_COMMAND = (
    r"py -B .\clinical_differential_support\scripts\record_final_verification_evidence.py "
    r"--overwrite"
)


def build_final_verification_gate(
    today: date | None = None,
    evidence_path: str | Path | None = None,
) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    readiness = build_release_readiness_report(today=current_date)
    next_action_plan = build_next_action_plan(today=current_date)
    gate_status = _build_gate_status(readiness, next_action_plan)

    return {
        "report_type": "final_verification_gate",
        "service": "clinical_differential_support",
        "audience": "staff_content_governance",
        "generated_on": current_date.isoformat(),
        "gate_status": gate_status,
        "readiness": {
            "ready_for_handoff": readiness["ready_for_handoff"],
            "clinical_item_count": readiness["total_items"],
            "approved_count": readiness["approved_count"],
            "source_gap_count": readiness["source_gap_count"],
            "review_due_count": readiness["review_due_count"],
            "failed_case_count": readiness["failed_case_count"],
        },
        "next_action_gate": {
            "completion_status": next_action_plan["completion_status"],
            "first_action": next_action_plan["next_actions"][0]["action_id"],
            "first_action_status": next_action_plan["next_actions"][0]["status"],
            "downstream_status": next_action_plan["downstream_readiness"]["status"],
        },
        "required_commands": _build_required_commands(),
        "next_action": _build_final_next_action(gate_status),
        "latest_evidence": load_latest_evidence(evidence_path=evidence_path),
        "handoff_exports": {
            "release_readiness": "/review/readiness/",
            "release_evidence_json": "/review/exports/release-evidence.json",
            "handoff_report_markdown": "/review/exports/handoff-report.md",
            "handoff_bundle_zip": "/review/exports/handoff-bundle.zip",
        },
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


def load_latest_evidence(evidence_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(evidence_path) if evidence_path else DEFAULT_EVIDENCE_PATH
    if not path.exists():
        return {
            "status": "not_recorded",
            "path": str(path),
            "command_count": 0,
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "status": "unreadable",
            "path": str(path),
            "error": str(error),
            "command_count": 0,
        }

    if payload.get("artifact_type") != "final_verification_evidence":
        return {
            "status": "invalid",
            "path": str(path),
            "command_count": 0,
        }

    command_results = payload.get("command_results") or []
    return {
        "status": payload.get("overall_status", "unknown"),
        "path": str(path),
        "generated_at": payload.get("generated_at"),
        "generated_on": payload.get("generated_on"),
        "gate_status_at_recording": payload.get("gate_status_at_recording"),
        "command_count": len(command_results),
        "passed_command_count": sum(
            1 for result in command_results if result.get("status") == "passed"
        ),
        "failed_command_count": sum(
            1 for result in command_results if result.get("status") == "failed"
        ),
    }


def _build_gate_status(
    readiness: dict[str, Any], next_action_plan: dict[str, Any]
) -> str:
    if not readiness["ready_for_handoff"]:
        return "blocked_by_release_readiness"
    if next_action_plan["completion_status"] != "ready_for_regression_gate":
        return "blocked_by_next_action_gate"
    return "ready_for_final_verification"


def _build_required_commands() -> list[dict[str, str]]:
    return [
        {
            "command_id": "full_regression",
            "command": FULL_REGRESSION_COMMAND,
            "expected_result": "203 tests pass",
            "evidence_status": "external_command_required",
        },
        {
            "command_id": "django_system_check",
            "command": DJANGO_CHECK_COMMAND,
            "expected_result": "System check identified no issues",
            "evidence_status": "external_command_required",
        },
        {
            "command_id": "live_smoke",
            "command": SMOKE_CHECK_COMMAND,
            "expected_result": "all smoke checks print ok",
            "evidence_status": "external_command_required",
        },
        {
            "command_id": "next_action_shell",
            "command": NEXT_ACTION_SHELL_COMMAND,
            "expected_result": "ready_for_regression_gate and run_full_regression_and_smoke_checks",
            "evidence_status": "external_command_required",
        },
    ]


def _build_final_next_action(gate_status: str) -> dict[str, str]:
    if gate_status != "ready_for_final_verification":
        return {
            "action_id": "resolve_final_gate_blockers",
            "status": "blocked",
            "title_zh": "先修正 final gate blocker",
            "title_en": "Resolve final gate blockers",
        }
    return {
        "action_id": "run_required_verification_commands",
        "status": "ready_to_run",
        "title_zh": "執行最終驗收命令",
        "title_en": "Run required verification commands",
    }
