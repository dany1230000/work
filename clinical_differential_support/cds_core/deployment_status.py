"""Deployment readiness and external deployment next-step reporting."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from django.conf import settings
from django.utils import timezone

from .git_remote_setup import CONFIGURE_GIT_REMOTE_BATCH_COMMAND
from .git_publish_status import (
    PUBLISH_STATUS_BATCH_COMMAND,
    build_git_publish_status_report,
)
from .local_launch import (
    DEFAULT_BASE_URL,
    DEPLOY_STATUS_BATCH_COMMAND,
    DEPLOYMENT_STATUS_COMMAND,
    FINAL_CHECK_BATCH_COMMAND,
)
from .project_completion import build_project_completion_report


@dataclass(frozen=True)
class CommandProbeResult:
    exit_code: int
    stdout: str
    stderr: str


CommandRunner = Callable[[str, Path], CommandProbeResult]
PUBLIC_DEPLOYMENT_EVIDENCE_FILENAME = "render-public-deployment.json"


def default_command_runner(command: str, cwd: Path) -> CommandProbeResult:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        capture_output=True,
        text=True,
    )
    return CommandProbeResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def build_deployment_status_report(
    base_url: str = DEFAULT_BASE_URL,
    today: date | None = None,
    evidence_path: str | Path | None = None,
    deployment_evidence_path: str | Path | None = None,
    project_dir: str | Path | None = None,
    workspace_root: str | Path | None = None,
    command_runner: CommandRunner = default_command_runner,
) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    normalized_base_url = base_url.rstrip("/")
    project_path = Path(project_dir) if project_dir else Path(settings.BASE_DIR)
    workspace_path = Path(workspace_root) if workspace_root else project_path.parent
    completion = build_project_completion_report(
        base_url=normalized_base_url,
        today=current_date,
        evidence_path=evidence_path,
    )

    publish_status = build_git_publish_status_report(
        workspace_root=workspace_path,
        command_runner=command_runner,
        today=current_date,
    )
    public_deployment = _load_public_deployment_evidence(deployment_evidence_path)
    public_deployment_ok = _is_public_deployment_live(public_deployment)
    git_remote = command_runner("git remote -v", workspace_path)
    git_remote_url = _first_remote_url(git_remote.stdout)
    if public_deployment_ok:
        render_cli = CommandProbeResult(
            exit_code=0,
            stdout="skipped after public deployment evidence\n",
            stderr="",
        )
        render_auth = CommandProbeResult(
            exit_code=0,
            stdout="dashboard verified\n",
            stderr="",
        )
    else:
        render_cli = command_runner("render --version", workspace_path)
        render_auth = (
            command_runner("render whoami -o json", workspace_path)
            if render_cli.exit_code == 0
            else CommandProbeResult(exit_code=2, stdout="", stderr="render cli unavailable")
        )

    checks = _build_deployment_checks(
        project_path=project_path,
        workspace_path=workspace_path,
        completion=completion,
        publish_status=publish_status,
        git_remote=git_remote,
        git_remote_url=git_remote_url,
        render_cli=render_cli,
        render_auth=render_auth,
        public_deployment=public_deployment,
    )
    check_map = {check["check_id"]: check for check in checks}
    status = _deployment_status(check_map)
    next_action = _next_action(status, git_remote_url)
    steps = _build_steps(status)
    external_blockers = (
        []
        if status == "public_deploy_live"
        else [
            check
            for check in checks
            if check["status"] in {"action_required", "locked"}
        ]
    )

    return {
        "report_type": "deployment_status",
        "service": "clinical_differential_support",
        "generated_on": current_date.isoformat(),
        "status": status,
        "exit_code": 0 if status == "public_deploy_live" else 2,
        "deployment_url": f"{normalized_base_url}/deployment/",
        "launch_control_url": f"{normalized_base_url}/launch/",
        "completion_url": f"{normalized_base_url}/completion/",
        "deployment_docs": str(project_path / "DEPLOYMENT.md"),
        "windows_entry_command": DEPLOY_STATUS_BATCH_COMMAND,
        "shell_command": DEPLOYMENT_STATUS_COMMAND,
        "deployment_checks": checks,
        "external_blockers": external_blockers,
        "steps": steps,
        "next_action": next_action,
        "public_deployment": _public_deployment_summary(public_deployment),
        "render_dashboard": {
            "blueprint_url": _render_blueprint_url(git_remote_url),
            "requires_git_remote": True,
            "requires_render_auth": True,
        },
        "git_publish_status": {
            "status": publish_status["status"],
            "exit_code": publish_status["exit_code"],
            "dirty_count": publish_status["dirty_count"],
            "command": PUBLISH_STATUS_BATCH_COMMAND,
        },
        "local_completion": {
            "status": completion["status"],
            "exit_code": completion["exit_code"],
            "url": completion["completion_url"],
        },
        "safety_scope": {
            "summary_only": True,
            "does_not_create_credentials": True,
            "does_not_print_credentials": True,
            "does_not_store_credentials": True,
            "does_not_bypass_authentication": True,
            "no_patient_identifying_data": True,
            "no_diagnosis_order": True,
            "no_treatment_order": True,
            "no_medication_order": True,
            "no_trading_or_broker_behavior": True,
            "no_clinical_production_approval": True,
        },
    }


def format_deployment_status_report(report: dict[str, Any]) -> str:
    next_action = report["next_action"]
    public_deployment_line = (
        "- Public deploy verified by health evidence; no clinical production approval."
        if report["status"] == "public_deploy_live"
        else "- No clinical production approval and no public deployment claim."
    )
    lines = [
        "部署操作中心 / Deployment Operations Center",
        f"Service: {report['service']}",
        f"Status: {report['status']}",
        f"exit_code={report['exit_code']}",
        f"Deployment URL: {report['deployment_url']}",
        f"Windows command: {report['windows_entry_command']}",
        f"Shell command: {report['shell_command']}",
        "",
        "Deployment Checks",
    ]
    for check in report["deployment_checks"]:
        lines.append(
            f"- {check['title_zh']} / {check['title_en']}: "
            f"{check['status']} ({check['value']})"
        )

    lines.extend(
        [
            "",
            (
                "Next Deployment Action: "
                f"{next_action['action_id']} - "
                f"{next_action['title_zh']} / {next_action['title_en']}"
            ),
            f"Detail: {next_action['detail_zh']} / {next_action['detail_en']}",
        ]
    )
    if next_action.get("command"):
        lines.append(f"Command: {next_action['command']}")
    if next_action.get("url"):
        lines.append(f"URL: {next_action['url']}")

    lines.extend(
        [
            "",
            "Safety Scope",
            "- Does not create, print, or store passwords.",
            "- No patient-identifying data, diagnosis orders, treatment orders, or medication orders.",
            public_deployment_line,
            "- No trading, broker API, live orders, or real capital behavior.",
        ]
    )
    return "\n".join(lines)


def _build_deployment_checks(
    project_path: Path,
    workspace_path: Path,
    completion: dict[str, Any],
    publish_status: dict[str, Any],
    git_remote: CommandProbeResult,
    git_remote_url: str,
    render_cli: CommandProbeResult,
    render_auth: CommandProbeResult,
    public_deployment: dict[str, Any] | None,
) -> list[dict[str, str]]:
    requirements = project_path / "requirements.txt"
    requirement_text = (
        requirements.read_text(encoding="utf-8") if requirements.exists() else ""
    )
    dependency_names = [
        "dj-database-url",
        "gunicorn",
        "psycopg2-binary",
        "whitenoise[brotli]",
    ]
    deps_ok = all(name in requirement_text for name in dependency_names)
    render_cli_ok = render_cli.exit_code == 0
    render_auth_ok = render_auth.exit_code == 0
    remote_exists = git_remote.exit_code == 0 and bool(git_remote_url)
    publish_ready = publish_status["status"] == "publish_package_ready"
    public_deployment_ok = _is_public_deployment_live(public_deployment)

    return [
        {
            "check_id": "local_final_gate",
            "status": "passed" if completion["status"] == "final_complete" else "action_required",
            "title_zh": "本機最終版",
            "title_en": "Local final gate",
            "value": completion["status"],
            "detail_zh": "必須先通過本機 Final_Check。",
            "detail_en": "Local Final_Check must pass before deployment.",
        },
        _file_check(
            check_id="render_blueprint",
            path=workspace_path / "render.yaml",
            title_zh="Render Blueprint",
            title_en="Render Blueprint",
        ),
        _file_check(
            check_id="build_script",
            path=project_path / "build.sh",
            title_zh="Render build script",
            title_en="Render build script",
        ),
        _file_check(
            check_id="deployment_docs",
            path=project_path / "DEPLOYMENT.md",
            title_zh="部署文件",
            title_en="Deployment docs",
        ),
        {
            "check_id": "runtime_dependencies",
            "status": "passed" if deps_ok else "action_required",
            "title_zh": "部署相依套件",
            "title_en": "Deployment dependencies",
            "value": "present" if deps_ok else "missing",
            "detail_zh": "需要 database URL, Gunicorn, PostgreSQL, WhiteNoise runtime。",
            "detail_en": "Requires database URL, Gunicorn, PostgreSQL, and WhiteNoise runtime dependencies.",
        },
        {
            "check_id": "git_publish_package",
            "status": "passed" if publish_ready else "action_required",
            "title_zh": "Git publish package",
            "title_en": "Git publish package",
            "value": "clean" if publish_ready else f"{publish_status['dirty_count']} uncommitted",
            "detail_zh": "部署 package 必須先審查、stage、commit，才能設定 remote 並推送。",
            "detail_en": "Review, stage, and commit the deployment package before configuring a remote and publishing.",
        },
        {
            "check_id": "git_remote",
            "status": "passed" if remote_exists else "action_required",
            "title_zh": "Git remote",
            "title_en": "Git remote",
            "value": git_remote_url or "missing",
            "detail_zh": "Render Blueprint 需要已 push 的 Git repository。",
            "detail_en": "Render Blueprint requires a pushed Git repository.",
        },
        _public_deployment_check(public_deployment),
        {
            "check_id": "render_cli",
            "status": (
                "skipped"
                if public_deployment_ok
                else ("passed" if render_cli_ok else "action_required")
            ),
            "title_zh": "Render CLI",
            "title_en": "Render CLI",
            "value": (
                "not_required_after_dashboard_live_verification"
                if public_deployment_ok
                else (_first_line(render_cli.stdout) if render_cli_ok else "missing")
            ),
            "detail_zh": "可用 Render CLI 驗證與登入；也可改用 Render Dashboard。",
            "detail_en": "Render CLI can validate/authenticate; Render Dashboard remains an alternative.",
        },
        {
            "check_id": "render_auth",
            "status": (
                "passed"
                if public_deployment_ok or render_auth_ok
                else ("action_required" if render_cli_ok else "locked")
            ),
            "title_zh": "Render auth",
            "title_en": "Render auth",
            "value": (
                "dashboard_verified"
                if public_deployment_ok
                else ("authenticated" if render_auth_ok else "not_authenticated")
            ),
            "detail_zh": "需要 Render Dashboard 或 CLI/API key 登入。",
            "detail_en": "Requires Render Dashboard login or CLI/API key authentication.",
        },
    ]


def _file_check(check_id: str, path: Path, title_zh: str, title_en: str) -> dict[str, str]:
    exists = path.exists()
    return {
        "check_id": check_id,
        "status": "passed" if exists else "action_required",
        "title_zh": title_zh,
        "title_en": title_en,
        "value": str(path) if exists else "missing",
        "detail_zh": "部署檔案必須存在。",
        "detail_en": "Deployment file must exist.",
    }


def _deployment_status(checks: dict[str, dict[str, str]]) -> str:
    if checks["public_deploy"]["status"] == "passed":
        return "public_deploy_live"

    local_check_ids = {
        "local_final_gate",
        "render_blueprint",
        "build_script",
        "deployment_docs",
        "runtime_dependencies",
    }
    if any(checks[check_id]["status"] != "passed" for check_id in local_check_ids):
        return "local_deployment_readiness_required"
    if checks["git_publish_package"]["status"] != "passed":
        return "ready_for_publish_package"
    if checks["git_remote"]["status"] != "passed":
        return "ready_for_remote_setup"
    if checks["render_cli"]["status"] != "passed":
        return "ready_for_render_cli_install"
    if checks["render_auth"]["status"] != "passed":
        return "ready_for_render_auth"
    return "ready_for_dashboard_deploy"


def _next_action(status: str, git_remote_url: str) -> dict[str, str]:
    if status == "public_deploy_live":
        return {
            "action_id": "monitor_public_deploy",
            "status": "ready",
            "title_zh": "監控公開部署",
            "title_en": "Monitor public deployment",
            "detail_zh": "Render 公開部署已通過 health check；下一步是定期確認 health endpoint 與內容治理狀態。",
            "detail_en": "The Render public deploy passed health checks. Next, monitor the health endpoint and governed content status.",
            "command": DEPLOY_STATUS_BATCH_COMMAND,
            "url": "",
        }
    if status == "local_deployment_readiness_required":
        return {
            "action_id": "finish_local_deployment_readiness",
            "status": "action_required",
            "title_zh": "先完成本機部署就緒檢查",
            "title_en": "Finish local deployment readiness checks",
            "detail_zh": "先修正本機 final gate、render.yaml、build.sh、部署文件或相依套件。",
            "detail_en": "Fix local final gate, render.yaml, build.sh, deployment docs, or dependencies first.",
            "command": FINAL_CHECK_BATCH_COMMAND,
            "url": "",
        }
    if status == "ready_for_publish_package":
        return {
            "action_id": "review_commit_publish_package",
            "status": "action_required",
            "title_zh": "審查並提交 deployment package",
            "title_en": "Review and commit deployment package",
            "detail_zh": "目前 scoped deployment package 還有未提交內容；先用 publish status 檢查，再手動 stage/commit。",
            "detail_en": "The scoped deployment package has uncommitted content. Inspect publish status, then explicitly stage and commit it.",
            "command": PUBLISH_STATUS_BATCH_COMMAND,
            "url": "",
        }
    if status == "ready_for_remote_setup":
        return {
            "action_id": "create_git_remote",
            "status": "action_required",
            "title_zh": "設定 Git remote",
            "title_en": "Configure Git remote",
            "detail_zh": "先在 GitHub、GitLab 或 Bitbucket 建立空 repo，再用助手設定 origin。只有明確加上 --push 才會推送。",
            "detail_en": "Create an empty GitHub, GitLab, or Bitbucket repo first, then use the assistant to set origin. It pushes only when --push is explicit.",
            "command": f"{CONFIGURE_GIT_REMOTE_BATCH_COMMAND} --remote-url <your-repo-url>",
            "url": "",
        }
    if status == "ready_for_render_cli_install":
        return {
            "action_id": "install_or_use_render_dashboard",
            "status": "action_required",
            "title_zh": "安裝 Render CLI 或改用 Dashboard",
            "title_en": "Install Render CLI or use Render Dashboard",
            "detail_zh": "目前可先用 Render Dashboard 建 Blueprint；CLI 只是驗證與查詢用。",
            "detail_en": "Use the Render Dashboard for Blueprint deploys; CLI is optional for validation and inspection.",
            "command": "render --version",
            "url": _render_blueprint_url(git_remote_url),
        }
    if status == "ready_for_render_auth":
        return {
            "action_id": "authenticate_render",
            "status": "action_required",
            "title_zh": "登入 Render",
            "title_en": "Authenticate Render",
            "detail_zh": "用 Render Dashboard 登入，或用 CLI/API key 驗證帳號。",
            "detail_en": "Sign in through the Render Dashboard or authenticate CLI/API key access.",
            "command": "render login",
            "url": _render_blueprint_url(git_remote_url),
        }
    return {
        "action_id": "open_render_blueprint",
        "status": "action_required",
        "title_zh": "開啟 Render Blueprint",
        "title_en": "Open Render Blueprint",
        "detail_zh": "確認 render.yaml 已推到遠端 repo，然後在 Render Dashboard 套用 Blueprint。",
        "detail_en": "Confirm render.yaml is pushed to the remote repo, then apply the Blueprint in Render Dashboard.",
        "command": "",
        "url": _render_blueprint_url(git_remote_url),
    }


def _build_steps(status: str) -> list[dict[str, str | int]]:
    definitions = [
        ("finish_local_deployment_readiness", "本機部署就緒", "Local deployment readiness"),
        ("review_commit_publish_package", "提交 deployment package", "Commit deployment package"),
        ("create_git_remote", "建立 Git remote", "Create Git remote"),
        ("install_or_use_render_dashboard", "Render CLI 或 Dashboard", "Render CLI or Dashboard"),
        ("authenticate_render", "登入 Render", "Authenticate Render"),
        ("open_render_blueprint", "套用 Render Blueprint", "Apply Render Blueprint"),
        ("verify_public_deploy", "驗證公開部署", "Verify public deployment"),
        ("monitor_public_deploy", "監控公開部署", "Monitor public deployment"),
    ]
    current_action = _next_action(status, "")["action_id"]
    steps = []
    seen_current = False
    for index, (action_id, title_zh, title_en) in enumerate(definitions, start=1):
        if action_id == current_action:
            step_status = "current"
            seen_current = True
        elif seen_current:
            step_status = "locked"
        else:
            step_status = "done"
        steps.append(
            {
                "step_number": index,
                "total_steps": len(definitions),
                "action_id": action_id,
                "status": step_status,
                "title_zh": title_zh,
                "title_en": title_en,
            }
        )
    return steps


def _first_remote_url(stdout: str) -> str:
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            return parts[1]
    return ""


def _render_blueprint_url(git_remote_url: str) -> str:
    repo_url = _to_https_repo_url(git_remote_url)
    if not repo_url:
        return "https://dashboard.render.com/blueprint/new"
    return f"https://dashboard.render.com/blueprint/new?repo={quote(repo_url, safe=':/')}"


def _to_https_repo_url(remote_url: str) -> str:
    url = remote_url.strip()
    if not url:
        return ""
    if url.startswith("git@") and ":" in url:
        host_path = url[4:].replace(":", "/", 1)
        url = f"https://{host_path}"
    if url.endswith(".git"):
        url = url[:-4]
    return url


def _first_line(text: str) -> str:
    return text.strip().splitlines()[0] if text.strip() else ""


def default_public_deployment_evidence_path(project_dir: str | Path | None = None) -> Path:
    project_path = Path(project_dir) if project_dir else Path(settings.BASE_DIR)
    return project_path / "verification_artifacts" / PUBLIC_DEPLOYMENT_EVIDENCE_FILENAME


def _load_public_deployment_evidence(
    deployment_evidence_path: str | Path | None,
) -> dict[str, Any] | None:
    if not deployment_evidence_path:
        return None

    path = Path(deployment_evidence_path)
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "artifact_type": "render_public_deployment_verification",
            "status": "invalid",
            "evidence_path": str(path),
        }

    if isinstance(payload, dict):
        payload.setdefault("evidence_path", str(path))
        return payload

    return {
        "artifact_type": "render_public_deployment_verification",
        "status": "invalid",
        "evidence_path": str(path),
    }


def _public_deployment_check(
    public_deployment: dict[str, Any] | None,
) -> dict[str, str]:
    if _is_public_deployment_live(public_deployment):
        return {
            "check_id": "public_deploy",
            "status": "passed",
            "title_zh": "Render public deploy",
            "title_en": "Render public deploy",
            "value": str(public_deployment.get("service_url", "")),
            "detail_zh": "已用公開 health endpoint 驗證 Render 部署。",
            "detail_en": "Render deployment was verified through the public health endpoint.",
        }

    return {
        "check_id": "public_deploy",
        "status": "pending",
        "title_zh": "Render public deploy",
        "title_en": "Render public deploy",
        "value": "not_verified",
        "detail_zh": "尚未提供公開 health endpoint 驗證 evidence。",
        "detail_en": "No public health endpoint verification evidence has been provided yet.",
    }


def _is_public_deployment_live(public_deployment: dict[str, Any] | None) -> bool:
    if not public_deployment:
        return False
    checks = public_deployment.get("checks")
    return (
        public_deployment.get("artifact_type")
        == "render_public_deployment_verification"
        and public_deployment.get("status") == "live"
        and public_deployment.get("http_status") == 200
        and isinstance(checks, dict)
        and checks.get("database") == "ok"
        and bool(public_deployment.get("service_url"))
    )


def _public_deployment_summary(
    public_deployment: dict[str, Any] | None,
) -> dict[str, Any]:
    if not _is_public_deployment_live(public_deployment):
        return {"status": "not_verified"}

    keys = [
        "status",
        "service_url",
        "health_url",
        "http_status",
        "checks",
        "render_service_id",
        "render_deploy_id",
        "commit",
        "verified_at",
    ]
    return {key: public_deployment.get(key) for key in keys if key in public_deployment}
