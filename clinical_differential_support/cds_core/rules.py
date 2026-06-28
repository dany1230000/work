"""Deterministic clinical rule evaluation."""

from dataclasses import dataclass
from typing import Any


MISSING_VALUES = (None, "", [], {})


@dataclass(frozen=True)
class FindingSet:
    values: dict[str, Any]

    def get(self, field: str) -> Any:
        return self.values.get(field)


def _is_present(value: Any) -> bool:
    if value is False:
        return False
    return value not in MISSING_VALUES


def evaluate_rule_condition(findings: FindingSet, condition: dict[str, Any]) -> bool:
    if "all" in condition:
        return all(evaluate_rule_condition(findings, part) for part in condition["all"])
    if "any" in condition:
        return any(evaluate_rule_condition(findings, part) for part in condition["any"])

    field = condition["field"]
    operator = condition["operator"]
    expected = condition.get("value")
    actual = findings.get(field)

    if operator == "equals":
        return actual == expected
    if operator == "in":
        return actual in expected
    if operator == "present":
        return _is_present(actual)
    if operator == "absent":
        return not _is_present(actual)
    if operator == "gte":
        return actual is not None and actual >= expected
    if operator == "lte":
        return actual is not None and actual <= expected

    raise ValueError(f"Unsupported rule operator: {operator}")


def _matched_clause_text(findings: FindingSet, condition: dict[str, Any]) -> list[str]:
    if "all" in condition:
        clauses: list[str] = []
        for part in condition["all"]:
            clauses.extend(_matched_clause_text(findings, part))
        return clauses
    if "any" in condition:
        clauses = []
        for part in condition["any"]:
            if evaluate_rule_condition(findings, part):
                clauses.extend(_matched_clause_text(findings, part))
        return clauses

    field = condition["field"]
    operator = condition["operator"]
    if "value" in condition:
        return [f"{field} {operator} {condition['value']}"]
    return [f"{field} {operator}"]


def _rule_to_dict(rule: Any) -> dict[str, Any]:
    if isinstance(rule, dict):
        return rule
    return {
        "id": rule.slug,
        "output_id": rule.output_item_id,
        "source_ids": rule.source_ids,
        "condition": rule.condition,
        "priority": rule.priority,
    }


def evaluate_rules(
    findings: FindingSet, rules: list[dict[str, Any]] | Any
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for rule in rules:
        data = _rule_to_dict(rule)
        if not evaluate_rule_condition(findings, data["condition"]):
            continue

        clauses = _matched_clause_text(findings, data["condition"])
        matches.append(
            {
                "rule_id": data["id"],
                "output_id": data["output_id"],
                "source_ids": data.get("source_ids", []),
                "explanation": "; ".join(clauses),
                "priority": data.get("priority", 100),
            }
        )
    return sorted(matches, key=lambda match: match["priority"])
