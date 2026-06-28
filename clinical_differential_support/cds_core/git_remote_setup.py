"""Safe Git remote setup assistant for deployment handoff."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse


CONFIGURE_GIT_REMOTE_BATCH_COMMAND = (
    r"clinical_differential_support\Configure_Git_Remote.cmd"
)
CONFIGURE_GIT_REMOTE_SHELL_COMMAND = (
    r"py -B .\clinical_differential_support\scripts\configure_git_remote.py"
)
DEPLOY_STATUS_BATCH_COMMAND = r"clinical_differential_support\Deploy_Status.cmd"
SUPPORTED_HOSTS = {"github.com", "gitlab.com", "bitbucket.org"}
SAFE_BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


CommandRunner = Callable[[str, Path], CommandResult]


@dataclass(frozen=True)
class RemoteValidation:
    valid: bool
    safe_url: str
    host: str
    path: str
    error: str


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


def build_git_remote_setup_report(
    remote_url: str = "",
    push: bool = False,
    workspace_root: str | Path | None = None,
    command_runner: CommandRunner = default_command_runner,
    today: date | None = None,
) -> dict[str, Any]:
    workspace_path = Path(workspace_root) if workspace_root else _default_workspace_root()
    current_date = today or date.today()
    requested_url = (remote_url or "").strip()
    commands_run: list[str] = []

    def run(command: str) -> CommandResult:
        commands_run.append(command)
        return command_runner(command, workspace_path)

    remote_probe = run("git remote -v")
    existing_origin = _first_origin_url(remote_probe.stdout)
    validation = _validate_remote_url(requested_url) if requested_url else None

    status = "remote_url_required"
    exit_code = 2
    validation_error = ""
    configured_remote = existing_origin

    if not requested_url:
        if existing_origin:
            status = "remote_already_configured"
            exit_code = 0
        else:
            status = "remote_url_required"
            exit_code = 2
    elif validation is None or not validation.valid:
        status = "invalid_remote_url"
        exit_code = 2
        validation_error = validation.error if validation else "Remote URL is invalid."
    elif existing_origin and _remote_key(existing_origin) != _remote_key(requested_url):
        status = "remote_conflict"
        exit_code = 2
        configured_remote = existing_origin
    else:
        configured_remote = requested_url or existing_origin
        if not existing_origin:
            add_result = run(f"git remote add origin {requested_url}")
            if add_result.exit_code != 0:
                status = "git_remote_add_failed"
                exit_code = 1
                validation_error = _first_line(add_result.stderr) or _first_line(add_result.stdout)
            else:
                status = "remote_configured"
                exit_code = 0
        else:
            status = "remote_already_configured"
            exit_code = 0

        if exit_code == 0 and push:
            branch_result = run("git branch --show-current")
            branch_name = _first_line(branch_result.stdout)
            if branch_result.exit_code != 0 or not _safe_branch_name(branch_name):
                status = "git_branch_unavailable"
                exit_code = 1
                validation_error = _first_line(branch_result.stderr) or "Current Git branch is unavailable."
            else:
                push_result = run(f"git push -u origin {branch_name}")
                if push_result.exit_code == 0:
                    status = "remote_pushed"
                    exit_code = 0
                else:
                    status = "git_push_failed"
                    exit_code = 1
                    validation_error = _first_line(push_result.stderr) or _first_line(push_result.stdout)

    safe_requested_url = _safe_remote_url(requested_url)
    next_action = _next_action(status, safe_requested_url)

    return {
        "report_type": "git_remote_setup",
        "service": "clinical_differential_support",
        "generated_on": current_date.isoformat(),
        "status": status,
        "exit_code": exit_code,
        "workspace_root": str(workspace_path),
        "existing_origin": existing_origin,
        "requested_remote_url": safe_requested_url,
        "configured_remote_url": _safe_remote_url(configured_remote),
        "remote_host": validation.host if validation and validation.valid else "",
        "push_requested": bool(push),
        "commands_run": commands_run,
        "validation_error": validation_error,
        "next_action": next_action,
        "safety_scope": {
            "does_not_create_git_host_repository": True,
            "does_not_create_render_account": True,
            "does_not_store_credentials": True,
            "does_not_print_credentials": True,
            "does_not_accept_embedded_https_credentials": True,
            "does_not_overwrite_existing_origin": True,
            "push_requires_explicit_flag": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
            "no_trading_or_broker_behavior": True,
        },
    }


def format_git_remote_setup_report(report: dict[str, Any]) -> str:
    lines = [
        "Git Remote Setup Assistant",
        "Git remote setup assistant",
        f"Service: {report['service']}",
        f"Status: {report['status']}",
        f"exit_code={report['exit_code']}",
        f"Existing origin: {report['existing_origin'] or 'missing'}",
        f"Requested remote: {report['requested_remote_url'] or 'not_provided'}",
        f"Push requested: {report['push_requested']}",
    ]
    if report.get("validation_error"):
        lines.append(f"Validation: {report['validation_error']}")

    next_action = report["next_action"]
    lines.extend(
        [
            "",
            (
                "Next Action: "
                f"{next_action['action_id']} - "
                f"{next_action['title_zh']} / {next_action['title_en']}"
            ),
            f"Detail: {next_action['detail_zh']} / {next_action['detail_en']}",
        ]
    )
    if next_action.get("command"):
        lines.append(f"Command: {next_action['command']}")

    lines.extend(
        [
            "",
            "Safety Scope",
            "- Does not create Git hosting or Render accounts.",
            "- Does not create, print, or store passwords or tokens.",
            "- Does not overwrite a different existing origin.",
            "- Does not push unless --push is explicitly supplied.",
            "- No clinical, patient-data, trading, broker, or live-order behavior.",
        ]
    )
    return "\n".join(lines)


def _next_action(status: str, safe_remote_url: str) -> dict[str, str]:
    setup_command = f"{CONFIGURE_GIT_REMOTE_BATCH_COMMAND} --remote-url <your-repo-url>"
    if status == "remote_url_required":
        return {
            "action_id": "provide_git_remote_url",
            "status": "action_required",
            "title_zh": "輸入遠端 repository URL",
            "title_en": "Provide Git remote repository URL",
            "detail_zh": "請先在 GitHub、GitLab 或 Bitbucket 建立空 repo，再把 URL 交給這個助手。",
            "detail_en": "Create an empty GitHub, GitLab, or Bitbucket repo first, then pass its URL to this assistant.",
            "command": setup_command,
        }
    if status == "invalid_remote_url":
        return {
            "action_id": "replace_invalid_git_remote_url",
            "status": "action_required",
            "title_zh": "改用安全的 Git remote URL",
            "title_en": "Use a safe Git remote URL",
            "detail_zh": "只接受 GitHub、GitLab 或 Bitbucket 的 HTTPS/SSH URL，且 HTTPS URL 不可包含帳號、密碼或 token。",
            "detail_en": "Use a GitHub, GitLab, or Bitbucket HTTPS/SSH URL. HTTPS URLs must not contain embedded credentials.",
            "command": setup_command,
        }
    if status == "remote_conflict":
        return {
            "action_id": "inspect_existing_origin",
            "status": "action_required",
            "title_zh": "檢查既有 origin",
            "title_en": "Inspect existing origin",
            "detail_zh": "目前已有不同的 origin；助手不會自動覆寫，請人工確認後再變更。",
            "detail_en": "A different existing origin is already configured. The assistant will not overwrite it automatically.",
            "command": "git remote -v",
        }
    if status in {"git_remote_add_failed", "git_branch_unavailable", "git_push_failed"}:
        return {
            "action_id": "resolve_git_command_error",
            "status": "blocked",
            "title_zh": "修正 Git 指令錯誤",
            "title_en": "Resolve Git command error",
            "detail_zh": "Git 指令失敗；請先查看錯誤並修正本機 Git 狀態。",
            "detail_en": "A Git command failed. Inspect the local Git state before retrying.",
            "command": "git status",
        }
    if status == "remote_pushed":
        return {
            "action_id": "return_to_deployment_status",
            "status": "ready",
            "title_zh": "回到部署操作中心",
            "title_en": "Return to Deployment Operations Center",
            "detail_zh": "remote 已設定且已 push；請重新檢查部署狀態。",
            "detail_en": "The remote is configured and pushed. Re-run deployment status.",
            "command": DEPLOY_STATUS_BATCH_COMMAND,
        }
    return {
        "action_id": "review_remote_then_optionally_push",
        "status": "ready",
        "title_zh": "檢查 remote 後再決定是否 push",
        "title_en": "Review remote, then optionally push",
        "detail_zh": "origin 已設定。確認遠端正確後，只有在你明確要推送時才加上 --push。",
        "detail_en": (
            "origin is configured. After checking the remote, add --push only when "
            "you explicitly want to run git push."
        ),
        "command": (
            f"{CONFIGURE_GIT_REMOTE_BATCH_COMMAND} --remote-url "
            f"{safe_remote_url or '<your-repo-url>'} --push"
        ),
    }


def _default_workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _first_origin_url(stdout: str) -> str:
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "origin":
            return parts[1]
    return ""


def _validate_remote_url(remote_url: str) -> RemoteValidation:
    safe_url = _safe_remote_url(remote_url)
    if not remote_url:
        return RemoteValidation(False, "", "", "", "Remote URL is required.")
    if any(char in remote_url for char in " \t\r\n\"'`;&|<>"):
        return RemoteValidation(
            False,
            safe_url,
            "",
            "",
            "Remote URL contains unsafe shell characters.",
        )

    parsed = urlparse(remote_url)
    if parsed.scheme in {"http", "https"}:
        if parsed.scheme != "https":
            return RemoteValidation(False, safe_url, "", "", "Only HTTPS remotes are allowed for web URLs.")
        if parsed.username or parsed.password or "@" in parsed.netloc:
            return RemoteValidation(
                False,
                safe_url,
                parsed.hostname or "",
                "",
                "HTTPS remote URLs with embedded credentials are not allowed.",
            )
        host = (parsed.hostname or "").lower()
        path = parsed.path.strip("/")
    elif remote_url.startswith("git@") and ":" in remote_url:
        host_path = remote_url[4:]
        host, path = host_path.split(":", 1)
        host = host.lower()
        path = path.strip("/")
    elif parsed.scheme == "ssh":
        host = (parsed.hostname or "").lower()
        path = parsed.path.strip("/")
    else:
        return RemoteValidation(
            False,
            safe_url,
            "",
            "",
            "Remote URL must be GitHub, GitLab, or Bitbucket HTTPS/SSH.",
        )

    if host not in SUPPORTED_HOSTS:
        return RemoteValidation(
            False,
            safe_url,
            host,
            path,
            "Remote URL host must be github.com, gitlab.com, or bitbucket.org.",
        )
    if len([part for part in path.split("/") if part]) < 2:
        return RemoteValidation(
            False,
            safe_url,
            host,
            path,
            "Remote URL must include owner and repository path.",
        )
    return RemoteValidation(True, safe_url, host, path, "")


def _remote_key(remote_url: str) -> str:
    validation = _validate_remote_url(remote_url)
    if not validation.valid:
        return remote_url.strip().removesuffix(".git")
    path = validation.path.removesuffix(".git")
    return f"{validation.host}/{path}".lower()


def _safe_remote_url(remote_url: str) -> str:
    if not remote_url:
        return ""
    parsed = urlparse(remote_url)
    if parsed.scheme in {"http", "https"} and "@" in parsed.netloc:
        host = parsed.hostname or "unknown-host"
        return f"{parsed.scheme}://<credentials>@{host}{parsed.path}"
    return remote_url


def _safe_branch_name(branch_name: str) -> bool:
    if not branch_name or branch_name.startswith("-"):
        return False
    return bool(SAFE_BRANCH_PATTERN.fullmatch(branch_name))


def _first_line(text: str) -> str:
    return text.strip().splitlines()[0] if text.strip() else ""
