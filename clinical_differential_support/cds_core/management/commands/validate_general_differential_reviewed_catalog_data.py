from django.core.management.base import BaseCommand, CommandError

from cds_core.differential_catalog_data import (
    load_default_reviewed_catalog_payload,
    load_reviewed_catalog_payload,
)
from cds_core.differential_catalog_import import (
    validate_general_differential_review_payload,
)


class Command(BaseCommand):
    help = "Validate packaged or supplied reviewed general differential catalog data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            help="Optional path to a reviewed catalog JSON payload. Defaults to packaged data.",
        )

    def handle(self, *args, **options):
        path = options.get("path")
        payload = (
            load_reviewed_catalog_payload(path)
            if path
            else load_default_reviewed_catalog_payload()
        )
        report = validate_general_differential_review_payload(payload)
        status = "READY" if report["valid"] else "NOT_READY"
        summary = report["summary"]
        self.stdout.write(
            f"{status} reviewed general differential catalog data: "
            f"{summary['condition_count']} conditions, "
            f"{summary['source_count']} sources, "
            f"blocking issues: {summary['blocking_issue_count']}"
        )

        if not report["valid"]:
            for issue in report["blocking_issues"]:
                self.stdout.write(
                    f"- {issue['code']}: {issue['subject']} - {issue['message_en']}"
                )
            raise CommandError("Reviewed catalog data has blocking issues.")
