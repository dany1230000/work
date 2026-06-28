import json

from django.core.management.base import BaseCommand

from cds_core.differential_catalog_import import (
    build_general_differential_batch_template,
)


class Command(BaseCommand):
    help = "Export a template for the next reviewed general differential batch."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Pretty-print the JSON payload.",
        )

    def handle(self, *args, **options):
        payload = build_general_differential_batch_template()
        indent = 2 if options["pretty"] else None
        self.stdout.write(json.dumps(payload, indent=indent))
