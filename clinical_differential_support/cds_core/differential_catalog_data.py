"""Load reviewable general differential catalog data for runtime use."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any


DEFAULT_REVIEWED_CATALOG_RESOURCE = "data/general_differential_catalog_reviewed.json"


def load_default_reviewed_catalog_payload() -> dict[str, Any]:
    resource = files("cds_core").joinpath(DEFAULT_REVIEWED_CATALOG_RESOURCE)
    with resource.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_reviewed_catalog_payload(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def build_runtime_catalog_from_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sources = {
        source["source_id"]: {
            "publisher": source["publisher"],
            "title": source["title"],
            "url": source["url"],
        }
        for source in payload.get("sources", [])
    }
    conditions = [
        {
            key: value
            for key, value in condition.items()
            if key != "review_status"
        }
        for condition in payload.get("conditions", [])
    ]

    return {
        "catalog_version": payload.get("catalog", {}).get(
            "catalog_version",
            "unknown-reviewed-catalog",
        ),
        "sources": sources,
        "conditions": conditions,
    }
