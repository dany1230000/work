import hashlib
import io
import json
import zipfile

from .evidence import build_release_evidence_package
from .exports import (
    CLINICAL_ITEM_EXPORT_HEADERS,
    SOURCE_EXPORT_HEADERS,
    build_clinical_item_export_rows,
    build_csv_text,
    build_source_export_rows,
)
from .handoff import build_handoff_report_markdown


def build_handoff_instructions_markdown():
    return "\n".join(
        [
            "# Handoff Instructions",
            "",
            "## 交付包 / Handoff Bundle",
            "",
            "這個 ZIP 是 staff-only 的內容治理交付包。",
            "This ZIP is a staff-only content-governance handoff bundle.",
            "",
            "## 驗證方式 / Verification",
            "",
            "下載或複製 ZIP 後，先執行：",
            "",
            "```powershell",
            "py -B clinical_differential_support\\scripts\\verify_handoff_bundle.py path\\to\\handoff-bundle.zip",
            "```",
            "",
            "如果需要從本地資料庫重新產生交付包，執行：",
            "",
            "```powershell",
            "py -B clinical_differential_support\\scripts\\export_handoff_bundle.py --output handoff-bundle.zip --overwrite",
            "```",
            "",
            "## 檔案內容 / Files",
            "",
            "- `manifest.json`: 檔案清單、SHA-256、byte size、交付狀態與安全範圍。",
            "- `handoff-report.md`: 人類可讀的 summary-only 交付報告。",
            "- `release-evidence.json`: 機器可讀的 summary-only 交付證據。",
            "- `clinical-items.csv`: staff-only 臨床內容治理匯出。",
            "- `sources.csv`: staff-only 來源治理匯出。",
            "- `handoff-instructions.md`: 這份交付與驗證說明。",
            "",
            "## 安全範圍 / Safety Scope",
            "",
            "- Not clinical deployment approval.",
            "- Reference support only; not a diagnosis or treatment order.",
            "- Do not enter or store patient-identifying data in this MVP.",
            "- Do not include credentials in handoff files.",
            "- No trading, broker, or order API behavior is part of this project.",
            "",
        ]
    )


def _payload_metadata(payload):
    return {
        "byte_size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def build_handoff_bundle_manifest(package, payloads):
    return {
        "package_type": "handoff_bundle",
        "service": package["service"],
        "generated_at": package["generated_at"],
        "staff_only": True,
        "files": [
            {
                "filename": "manifest.json",
                "content_type": "application/json",
                "summary": "Bundle metadata, file list, readiness, and safety scope.",
                "integrity_excluded": True,
                "integrity_note": (
                    "Manifest hashes exclude manifest.json to avoid "
                    "a self-referential digest."
                ),
            },
            {
                "filename": "handoff-report.md",
                "content_type": "text/markdown; charset=utf-8",
                "summary": "Human-readable summary-only handoff report.",
                **_payload_metadata(payloads["handoff-report.md"]),
            },
            {
                "filename": "handoff-instructions.md",
                "content_type": "text/markdown; charset=utf-8",
                "summary": "Self-contained handoff verification and safety instructions.",
                **_payload_metadata(payloads["handoff-instructions.md"]),
            },
            {
                "filename": "release-evidence.json",
                "content_type": "application/json",
                "summary": "Machine-readable summary-only release evidence.",
                **_payload_metadata(payloads["release-evidence.json"]),
            },
            {
                "filename": "clinical-items.csv",
                "content_type": "text/csv; charset=utf-8",
                "summary": "Staff-only clinical item governance export.",
                **_payload_metadata(payloads["clinical-items.csv"]),
            },
            {
                "filename": "sources.csv",
                "content_type": "text/csv; charset=utf-8",
                "summary": "Staff-only source governance export.",
                **_payload_metadata(payloads["sources.csv"]),
            },
        ],
        "exports": package["exports"],
        "readiness": package["readiness"],
        "validation": package["validation"],
        "safety_scope": package["safety_scope"],
    }


def _json_text(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def build_handoff_bundle_zip(now=None, today=None):
    package = build_release_evidence_package(now=now, today=today)
    clinical_csv = build_csv_text(
        CLINICAL_ITEM_EXPORT_HEADERS,
        build_clinical_item_export_rows(),
    )
    sources_csv = build_csv_text(
        SOURCE_EXPORT_HEADERS,
        build_source_export_rows(),
    )
    payloads = {
        "handoff-instructions.md": build_handoff_instructions_markdown().encode(
            "utf-8"
        ),
        "handoff-report.md": build_handoff_report_markdown(package=package).encode(
            "utf-8"
        ),
        "release-evidence.json": _json_text(package).encode("utf-8"),
        "clinical-items.csv": clinical_csv.encode("utf-8"),
        "sources.csv": sources_csv.encode("utf-8"),
    }
    manifest = build_handoff_bundle_manifest(package, payloads)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", _json_text(manifest).encode("utf-8"))
        for filename, payload in payloads.items():
            archive.writestr(filename, payload)
    return buffer.getvalue()
