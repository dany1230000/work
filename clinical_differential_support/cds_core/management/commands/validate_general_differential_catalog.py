from django.core.management.base import BaseCommand, CommandError

from cds_core.differential_catalog_quality import (
    build_general_differential_catalog_quality_report,
)


class Command(BaseCommand):
    help = "Validate the general differential catalog quality gate."

    def handle(self, *args, **options):
        report = build_general_differential_catalog_quality_report()
        summary = report["summary"]
        status = "READY" if summary["ready_for_public_reference"] else "BLOCKED"

        self.stdout.write(
            (
                f"{status} general differential catalog: "
                f"{summary['condition_count']} conditions, "
                f"{summary['source_count']} sources, "
                f"blocking issues: {summary['blocking_issue_count']}, "
                f"warnings: {summary['warning_count']}"
            )
        )

        for issue in report["blocking_issues"]:
            self.stdout.write(
                f"BLOCKER {issue['code']} {issue['subject']}: {issue['message_en']}"
            )

        if report["blocking_issues"]:
            raise CommandError("General differential catalog has blocking issues.")
