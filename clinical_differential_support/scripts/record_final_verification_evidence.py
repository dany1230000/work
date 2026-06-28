import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_DIR.parent
DEFAULT_OUTPUT_PATH = (
    PROJECT_DIR / "verification_artifacts" / "final-verification-evidence.json"
)
FORBIDDEN_SUMMARY_PATTERNS = [
    "Thunderclap headache",
    "Possible acute coronary syndrome",
]


@dataclass(frozen=True)
class CommandRunResult:
    exit_code: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class EvidenceRecordResult:
    ok: bool
    output_path: Path
    command_count: int
    messages: list[str]
    errors: list[str]


def ensure_django():
    project_path = str(PROJECT_DIR)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "clinical_differential_support.settings",
    )
    import django
    from django.apps import apps

    if not apps.ready:
        django.setup()


def default_runner(command: str, cwd: Path) -> CommandRunResult:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        capture_output=True,
        text=True,
    )
    return CommandRunResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def record_final_verification_evidence(
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    runner=default_runner,
    today=None,
    overwrite: bool = True,
) -> EvidenceRecordResult:
    ensure_django()
    from cds_core.final_verification import build_final_verification_gate

    output = Path(output_path)
    if output.exists() and not overwrite:
        return EvidenceRecordResult(
            ok=False,
            output_path=output,
            command_count=0,
            messages=[],
            errors=[f"{output}: already exists"],
        )

    gate = build_final_verification_gate(today=today, evidence_path=output)
    command_results = []
    messages = []
    errors = []

    for command in gate["required_commands"]:
        run_result = runner(command["command"], WORKSPACE_ROOT)
        status = "passed" if run_result.exit_code == 0 else "failed"
        command_results.append(
            {
                "command_id": command["command_id"],
                "command": command["command"],
                "expected_result": command["expected_result"],
                "exit_code": run_result.exit_code,
                "status": status,
                "stdout_summary": summarize_output(run_result.stdout),
                "stderr_summary": summarize_output(run_result.stderr),
            }
        )
        messages.append(f"{command['command_id']}: {status}")
        if status == "failed":
            errors.append(f"{command['command_id']}: exit {run_result.exit_code}")
            break

    all_passed = len(command_results) == len(gate["required_commands"]) and not errors
    overall_status = (
        "verified"
        if all_passed and gate["gate_status"] == "ready_for_final_verification"
        else "failed"
    )
    payload = {
        "artifact_type": "final_verification_evidence",
        "service": "clinical_differential_support",
        "generated_at": _now_isoformat(),
        "generated_on": gate["generated_on"],
        "gate_status_at_recording": gate["gate_status"],
        "overall_status": overall_status,
        "command_results": command_results,
        "safety_scope": {
            "summary_only": True,
            "no_full_command_output": True,
            "no_source_urls": True,
            "no_detailed_clinical_item_text": True,
            "no_patient_identifying_data": True,
            "no_credentials": True,
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    messages.append(f"wrote: {output}")
    return EvidenceRecordResult(
        ok=overall_status == "verified",
        output_path=output,
        command_count=len(command_results),
        messages=messages,
        errors=errors,
    )


def summarize_output(text: str, max_chars: int = 500) -> str:
    if not text:
        return ""

    sanitized_lines = []
    for line in text.splitlines():
        sanitized = _sanitize_line(line.strip())
        if sanitized:
            sanitized_lines.append(sanitized)
        if len("\n".join(sanitized_lines)) >= max_chars:
            break

    summary = "\n".join(sanitized_lines).strip()
    return summary[:max_chars]


def _sanitize_line(line: str) -> str:
    if not line:
        return ""
    for forbidden in FORBIDDEN_SUMMARY_PATTERNS:
        if forbidden in line:
            return ""
    line = re.sub(r"https?://\S+", "[url-omitted]", line)
    return line


def _now_isoformat() -> str:
    from django.utils import timezone

    return timezone.now().isoformat()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run final verification commands and write summary evidence."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    result = record_final_verification_evidence(
        output_path=args.output,
        overwrite=args.overwrite,
    )
    for message in result.messages:
        print(message)
    for error in result.errors:
        print(error, file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
