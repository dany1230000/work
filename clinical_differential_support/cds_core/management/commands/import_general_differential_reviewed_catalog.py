from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from cds_core.differential_catalog_data import load_reviewed_catalog_payload
from cds_core.differential_catalog_import import (
    preview_general_differential_review_import,
    write_reviewed_catalog_payload,
)


class Command(BaseCommand):
    help = "Preview or apply a reviewed general differential catalog JSON payload."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            required=True,
            help="Path to a reviewed catalog JSON payload.",
        )
        parser.add_argument(
            "--output",
            help="Output path for reviewed catalog JSON. Required with --apply.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write the reviewed catalog payload to --output after validation.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Allow replacing an existing output file.",
        )

    def handle(self, *args, **options):
        payload = load_reviewed_catalog_payload(options["path"])
        preview = preview_general_differential_review_import(payload)
        summary = preview["summary"]

        if not preview["ready_to_apply"]:
            self.stdout.write(
                "BLOCKED reviewed catalog import preview: "
                f"{summary['condition_count']} conditions, "
                f"{summary['source_count']} sources, "
                f"blocking issues: {summary['blocking_issue_count']}"
            )
            for issue in preview["blocking_issues"]:
                self.stdout.write(
                    f"- {issue['code']}: {issue['subject']} - {issue['message_en']}"
                )
            raise CommandError("Reviewed catalog import has blocking issues.")

        if not options["apply"]:
            self.stdout.write(
                "READY reviewed catalog import preview: "
                f"{summary['condition_count']} conditions, "
                f"{summary['source_count']} sources, "
                "apply required to write output"
            )
            self.stdout.write(
                "Post-apply checks: "
                + ", ".join(preview["required_post_apply_checks"])
            )
            return

        output = options.get("output")
        if not output:
            raise CommandError("--output is required when --apply is used.")

        output_path = Path(output)
        if output_path.exists() and not options["overwrite"]:
            raise CommandError("Output already exists; pass --overwrite to replace it.")

        written = write_reviewed_catalog_payload(payload, output_path)
        self.stdout.write(
            "APPLIED reviewed catalog import: "
            f"{written['condition_count']} conditions, "
            f"{written['source_count']} sources, "
            f"path: {written['path']}"
        )
        self.stdout.write(
            "Run post-apply checks: "
            + ", ".join(preview["required_post_apply_checks"])
        )
