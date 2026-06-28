import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from cds_core.differential_catalog_import import (
    validate_general_differential_review_payload,
)
from cds_core.differential_catalog_review_seed import (
    build_general_differential_review_seed,
)


class Command(BaseCommand):
    help = "Validate a general differential review seed JSON payload."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            nargs="?",
            help="Optional JSON payload path. Defaults to the built-in review seed.",
        )

    def handle(self, *args, **options):
        payload = _load_payload(options.get("path"))
        report = validate_general_differential_review_payload(payload)
        status = "READY" if report["valid"] else "BLOCKED"
        summary = report["summary"]

        self.stdout.write(
            (
                f"{status} general differential review seed: "
                f"{summary['condition_count']} conditions, "
                f"{summary['source_count']} sources, "
                f"blocking issues: {summary['blocking_issue_count']}"
            )
        )
        for issue in report["blocking_issues"]:
            self.stdout.write(
                f"BLOCKER {issue['code']} {issue['subject']}: {issue['message_en']}"
            )
        if not report["valid"]:
            raise CommandError("General differential review seed has blocking issues.")


def _load_payload(path: str | None):
    if not path:
        return build_general_differential_review_seed()
    return json.loads(Path(path).read_text(encoding="utf-8"))
