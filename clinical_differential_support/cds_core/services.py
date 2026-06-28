"""Workflow orchestration services."""

from typing import Any

from .models import CaseScenario, ChiefComplaint, ClinicalItem, Rule
from .rules import FindingSet, evaluate_rules


URGENCY_ORDER = {
    ClinicalItem.Urgency.EMERGENT: 0,
    ClinicalItem.Urgency.URGENT: 1,
    ClinicalItem.Urgency.SOON: 2,
    ClinicalItem.Urgency.ROUTINE: 3,
}

TYPE_ORDER = {
    ClinicalItem.ItemType.RED_FLAG: 0,
    ClinicalItem.ItemType.WORKUP: 1,
    ClinicalItem.ItemType.DIFFERENTIAL: 2,
    ClinicalItem.ItemType.MEDICATION_SAFETY: 3,
    ClinicalItem.ItemType.MANAGEMENT: 4,
}


def evaluate_pathway(
    chief_complaint_slug: str, raw_findings: dict[str, Any]
) -> dict[str, Any]:
    complaint = ChiefComplaint.objects.get(slug=chief_complaint_slug)
    rules = Rule.objects.filter(
        chief_complaint=complaint,
        active=True,
        output_item__status=ClinicalItem.Status.APPROVED,
    ).select_related("output_item")
    matches = evaluate_rules(FindingSet(_clean_findings(raw_findings)), list(rules))
    item_ids = [match["output_id"] for match in matches]
    items = {
        item.id: item
        for item in ClinicalItem.objects.filter(id__in=item_ids).prefetch_related(
            "sources"
        )
    }

    outputs = []
    for match in matches:
        item = items.get(match["output_id"])
        if not item:
            continue
        outputs.append(
            {
                "item": item,
                "explanation": match["explanation"],
                "sources": list(item.sources.all()),
            }
        )

    outputs.sort(
        key=lambda entry: (
            TYPE_ORDER.get(entry["item"].item_type, 99),
            URGENCY_ORDER.get(entry["item"].urgency, 99),
            entry["item"].title,
        )
    )

    return {
        "outputs": outputs,
        "empty_state": (
            f"目前輸入不符合 {complaint.title} MVP 已覆蓋的規則；"
            "請檢視主要來源並使用臨床判斷。"
            "This presentation is not covered in this MVP. Review primary sources "
            "and use clinician judgment."
        ),
    }


def evaluate_headache_pathway(raw_findings: dict[str, Any]) -> dict[str, Any]:
    return evaluate_pathway("headache", raw_findings)


def evaluate_chest_pain_pathway(raw_findings: dict[str, Any]) -> dict[str, Any]:
    return evaluate_pathway("chest-pain", raw_findings)


def evaluate_abdominal_pain_pathway(raw_findings: dict[str, Any]) -> dict[str, Any]:
    return evaluate_pathway("abdominal-pain", raw_findings)


def evaluate_dyspnea_pathway(raw_findings: dict[str, Any]) -> dict[str, Any]:
    return evaluate_pathway("dyspnea", raw_findings)


def evaluate_case_scenario(scenario: CaseScenario) -> dict[str, Any]:
    pathway_result = evaluate_pathway(scenario.chief_complaint.slug, scenario.findings)
    actual_titles = {entry["item"].title for entry in pathway_result["outputs"]}
    expected_outputs = [
        {"title": title, "matched": title in actual_titles}
        for title in scenario.expected_item_titles
    ]
    return {
        "scenario": scenario,
        "pathway_result": pathway_result,
        "expected_outputs": expected_outputs,
    }


def _clean_findings(raw_findings: dict[str, Any]) -> dict[str, Any]:
    findings: dict[str, Any] = {}
    for key, value in raw_findings.items():
        if value in ("", None):
            continue
        if value == "on":
            findings[key] = True
            continue
        findings[key] = value
    return findings
