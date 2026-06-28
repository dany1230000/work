import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ExportResult:
    ok: bool
    output_path: Path
    bytes_written: int
    messages: list[str]
    errors: list[str]


def _result(output_path, bytes_written, messages, errors):
    return ExportResult(
        ok=not errors,
        output_path=output_path,
        bytes_written=bytes_written,
        messages=messages,
        errors=errors,
    )


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


def export_bundle(output_path, overwrite=False, verify=True):
    ensure_django()
    from cds_core.bundle import build_handoff_bundle_zip
    from scripts.verify_handoff_bundle import verify_bundle

    output = Path(output_path)
    messages = []
    errors = []
    if output.exists() and not overwrite:
        return _result(output, 0, messages, [f"{output}: already exists"])

    output.parent.mkdir(parents=True, exist_ok=True)
    bundle_bytes = build_handoff_bundle_zip()
    output.write_bytes(bundle_bytes)
    messages.append(f"exported: {output}")

    if verify:
        verification = verify_bundle(output)
        messages.extend(verification.messages)
        errors.extend(verification.errors)
        if verification.ok:
            messages.append("verified: ok")

    return _result(output, len(bundle_bytes), messages, errors)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Export and verify the Clinical Differential Support handoff bundle."
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-verify", action="store_true")
    args = parser.parse_args(argv)

    result = export_bundle(
        args.output,
        overwrite=args.overwrite,
        verify=not args.no_verify,
    )
    for message in result.messages:
        print(message)
    for error in result.errors:
        print(error, file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
