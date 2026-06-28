"""Read-only Git publish readiness reporting for deployment handoff."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .git_remote_setup import CONFIGURE_GIT_REMOTE_BATCH_COMMAND


PUBLISH_SCOPE_PATHS = [
    "clinical_differential_support",
    "docs/superpowers",
    ".planning/2026-06-22-clinical-differential-support",
    "render.yaml",
]
PUBLISH_STATUS_COMMAND = "git status --short -- " + " ".join(PUBLISH_SCOPE_PATHS)
PUBLISH_STATUS_BATCH_COMMAND = r"clinical_differential_support\Publish_Status.cmd"
PUBLISH_STATUS_SHELL_COMMAND = (
    r"py -B .\clinical_differential_support\scripts\git_publish_status.py"
)


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


CommandRunner = Callable[[str, Path], CommandResult]


def default_command_runner(command: str, cwd: Path) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        capture_output=True,
        text=True,
    )
    return CommandResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def build_git_publish_status_report(
    workspace_root: str | Path | None = None,
    command_runner: CommandRunner = default_command_runner,
    today: date | None = None,
) -> dict[str, Any]:
    workspace_path = Path(workspace_root) if workspace_root else _default_workspace_root()
    current_date = today or date.today()
    commands_run: list[str] = []

    def run(command: str) -> CommandResult:
        commands_run.append(command)
        return command_runner(command, workspace_path)

    status_result = run(PUBLISH_STATUS_COMMAND)
    branch_result = run("git branch --show-current")
    dirty_entries = _parse_status_entries(status_result.stdout)
    dirty_count = len(dirty_entries)

    if status_result.exit_code != 0:
        status = "git_unavailable"
        exit_code = 1
    elif dirty_count:
        status = "publish_package_uncommitted"
        exit_code = 2
    else:
        status = "publish_package_ready"
        exit_code = 0

    branch = _first_line(branch_result.stdout) if branch_result.exit_code == 0 else ""

    return {
        "report_type": "git_publish_status",
        "service": "clinical_differential_support",
        "generated_on": current_date.isoformat(),
        "status": status,
        "exit_code": exit_code,
        "workspace_root": str(workspace_path),
        "branch": branch,
        "scope_paths": PUBLISH_SCOPE_PATHS,
        "dirty_count": dirty_count,
        "dirty_entries": dirty_entries,
        "commands_run": commands_run,
        "suggested_commands": _suggested_commands(),
        "next_action": _next_action(status),
        "safety_scope": {
            "read_only": True,
            "does_not_stage": True,
            "does_not_commit": True,
            "does_not_configure_remote": True,
            "does_not_push": True,
            "does_not_create_credentials": True,
            "does_not_print_credentials": True,
            "does_not_store_credentials": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
            "no_trading_or_broker_behavior": True,
        },
    }


def format_git_publish_status_report(report: dict[str, Any]) -> str:
    lines = [
        "Git Publish Readiness Assistant",
        "Git publish readiness",
        f"Service: {report['service']}",
        f"Status: {report['status']}",
        f"exit_code={report['exit_code']}",
        f"Branch: {report['branch'] or 'unknown'}",
        f"Dirty scoped entries: {report['dirty_count']}",
        "",
        "Scoped Paths",
    ]
    lines.extend(f"- {path}" for path in report["scope_paths"])

    if report["dirty_entries"]:
        lines.extend(["", "Uncommitted Scoped Entries"])
        for entry in report["dirty_entries"]:
            lines.append(f"- {entry['status']} {entry['path']}")

    commands = report["suggested_commands"]
    lines.extend(
        [
            "",
            "Suggested Review Commands",
            f"Review: {commands['review']}",
            f"Stage after review: {commands['stage']}",
            f"Commit after review: {commands['commit']}",
            "",
            (
                "Next Action: "
                f"{report['next_action']['action_id']} - "
                f"{report['next_action']['title_zh']} / {report['next_action']['title_en']}"
            ),
            f"Command: {report['next_action']['command']}",
            "",
            "Safety Scope",
            "- Read-only status command.",
            "- Does not stage, commit, configure remotes, or run push.",
            "- Does not create, print, or store credentials.",
            "- No clinical decision, patient-data, trading, broker, or live-order behavior.",
        ]
    )
    return "\n".join(lines)


def _next_action(status: str) -> dict[str, str]:
    if status == "publish_package_ready":
        return {
            "action_id": "configure_git_remote",
            "status": "ready",
            "title_zh": "設定 Git remote",
            "title_en": "Configure Git remote",
            "detail_zh": "scoped deployment package 已乾淨，可以進入 remote 設定。",
            "detail_en": "The scoped deployment package is clean, so remote setup can proceed.",
            "command": f"{CONFIGURE_GIT_REMOTE_BATCH_COMMAND} --remote-url <your-repo-url>",
        }
    if status == "git_unavailable":
        return {
            "action_id": "resolve_git_status_error",
            "status": "blocked",
            "title_zh": "修正 Git status 錯誤",
            "title_en": "Resolve Git status error",
            "detail_zh": "Git 無法檢查 scoped package；請先修正本機 Git 狀態。",
            "detail_en": "Git could not inspect the scoped package. Fix local Git state first.",
            "command": PUBLISH_STATUS_BATCH_COMMAND,
        }
    return {
        "action_id": "review_commit_publish_package",
        "status": "action_required",
        "title_zh": "審查並提交 deployment package",
        "title_en": "Review and commit deployment package",
        "detail_zh": "先審查 scoped files，再用明確的 git add/commit 指令提交；助手本身不會替你提交。",
        "detail_en": "Review the scoped files, then explicitly stage and commit them. This assistant does not commit for you.",
        "command": PUBLISH_STATUS_BATCH_COMMAND,
    }


def _suggested_commands() -> dict[str, str]:
    scoped_paths = " ".join(PUBLISH_SCOPE_PATHS)
    return {
        "review": PUBLISH_STATUS_COMMAND,
        "stage": f"git add -- {scoped_paths}",
        "commit": 'git commit -m "feat: prepare clinical deployment package"',
    }


def _parse_status_entries(stdout: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or line[:2]
        path = line[3:].strip() if len(line) > 3 else ""
        entries.append({"status": status, "path": path})
    return entries


def _default_workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _first_line(text: str) -> str:
    return text.strip().splitlines()[0] if text.strip() else ""
