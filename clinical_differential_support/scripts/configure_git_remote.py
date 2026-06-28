import argparse
import json
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


def ensure_project_path():
    project_path = str(PROJECT_DIR)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)


def main(argv=None, command_runner=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Safely configure the Git remote for deployment handoff.",
    )
    parser.add_argument("--remote-url", default="")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    ensure_project_path()
    from cds_core.git_remote_setup import (
        build_git_remote_setup_report,
        default_command_runner,
        format_git_remote_setup_report,
    )

    report = build_git_remote_setup_report(
        remote_url=args.remote_url,
        push=args.push,
        command_runner=command_runner or default_command_runner,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_git_remote_setup_report(report))
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
