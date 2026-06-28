#!/usr/bin/env python
"""Django command-line entrypoint."""

import os
import sys
from pathlib import Path


def main() -> None:
    script_path = Path(__file__).resolve()
    sys.argv[0] = str(script_path)
    os.chdir(script_path.parent)
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "clinical_differential_support.settings"
    )
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
