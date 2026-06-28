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


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Print the next safe local setup action for the clinician-support MVP.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    ensure_django()
    from cds_core.local_setup import (
        build_local_setup_assistant_report,
        format_local_setup_assistant_report,
    )

    report = build_local_setup_assistant_report(
        base_url=args.base_url,
        evidence_path=args.evidence_path,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_local_setup_assistant_report(report))
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
