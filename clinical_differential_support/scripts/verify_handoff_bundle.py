import argparse
import hashlib
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = {
    "manifest.json",
    "handoff-instructions.md",
    "handoff-report.md",
    "release-evidence.json",
    "clinical-items.csv",
    "sources.csv",
}


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    messages: list[str]
    errors: list[str]


def _result(messages, errors):
    return VerificationResult(ok=not errors, messages=messages, errors=errors)


def _read_manifest(archive, errors):
    try:
        manifest_bytes = archive.read("manifest.json")
    except KeyError:
        errors.append("manifest.json: missing from ZIP")
        return None

    try:
        return json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"manifest.json: invalid JSON ({error})")
        return None


def _validate_manifest_header(manifest, errors):
    if manifest.get("package_type") != "handoff_bundle":
        errors.append("manifest.json: package_type is not handoff_bundle")
    if manifest.get("service") != "clinical_differential_support":
        errors.append("manifest.json: service is not clinical_differential_support")
    if manifest.get("staff_only") is not True:
        errors.append("manifest.json: staff_only must be true")


def _file_entries(manifest, errors):
    entries = {}
    files = manifest.get("files")
    if not isinstance(files, list):
        errors.append("manifest.json: files must be a list")
        return entries

    for entry in files:
        if not isinstance(entry, dict):
            errors.append("manifest.json: file entry is not an object")
            continue
        filename = entry.get("filename")
        if not filename:
            errors.append("manifest.json: file entry missing filename")
            continue
        entries[filename] = entry
    return entries


def _validate_manifest_entry(entries, errors):
    entry = entries.get("manifest.json")
    if not entry:
        errors.append("manifest.json: missing manifest file entry")
        return
    if entry.get("integrity_excluded") is not True:
        errors.append("manifest.json: integrity_excluded must be true")


def _validate_payload_entry(archive, entries, filename, errors):
    entry = entries.get(filename)
    if not entry:
        errors.append(f"{filename}: missing manifest file entry")
        return
    try:
        payload = archive.read(filename)
    except KeyError:
        errors.append(f"{filename}: missing from ZIP")
        return

    expected_size = entry.get("byte_size")
    if expected_size != len(payload):
        errors.append(f"{filename}: byte_size mismatch")

    expected_sha256 = entry.get("sha256")
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if expected_sha256 != actual_sha256:
        errors.append(f"{filename}: sha256 mismatch")


def verify_bundle(bundle_path):
    path = Path(bundle_path)
    messages = []
    errors = []
    if not path.exists():
        return _result(messages, [f"{path}: file does not exist"])
    if not path.is_file():
        return _result(messages, [f"{path}: not a file"])

    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            missing_required = sorted(REQUIRED_FILES - names)
            for filename in missing_required:
                errors.append(f"{filename}: missing from ZIP")

            manifest = _read_manifest(archive, errors)
            if manifest is None:
                return _result(messages, errors)

            _validate_manifest_header(manifest, errors)
            entries = _file_entries(manifest, errors)
            _validate_manifest_entry(entries, errors)
            for filename in sorted(REQUIRED_FILES - {"manifest.json"}):
                _validate_payload_entry(archive, entries, filename, errors)
    except zipfile.BadZipFile:
        return _result(messages, [f"{path}: not a valid ZIP file"])

    if not errors:
        messages.append("handoff-bundle.zip: ok")
    return _result(messages, errors)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify a downloaded Clinical Differential Support handoff bundle."
    )
    parser.add_argument("bundle_path")
    args = parser.parse_args(argv)

    result = verify_bundle(args.bundle_path)
    for message in result.messages:
        print(message)
    for error in result.errors:
        print(error, file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
