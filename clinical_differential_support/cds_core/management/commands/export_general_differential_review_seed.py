import json

from django.core.management.base import BaseCommand

from cds_core.differential_catalog_review_seed import (
    build_general_differential_review_seed,
)


class Command(BaseCommand):
    help = "Export the general differential catalog as a reviewable JSON seed."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Pretty-print the JSON payload.",
        )

    def handle(self, *args, **options):
        payload = build_general_differential_review_seed()
        indent = 2 if options["pretty"] else None
        self.stdout.write(json.dumps(payload, indent=indent))
