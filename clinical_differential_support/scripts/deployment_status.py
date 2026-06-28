import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


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


def main(argv=None, command_runner=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Print the next safe deployment action for the clinician-support MVP.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    ensure_django()
    from cds_core.deployment_status import (
        build_deployment_status_report,
        default_command_runner,
        format_deployment_status_report,
    )

    report = build_deployment_status_report(
        base_url=args.base_url,
        evidence_path=args.evidence_path,
        command_runner=command_runner or default_command_runner,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_deployment_status_report(report))
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
