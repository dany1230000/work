from django.test import SimpleTestCase

from cds_core.rules import FindingSet, evaluate_rule_condition, evaluate_rules


class RuleEngineTests(SimpleTestCase):
    def test_thunderclap_rule_matches_and_explains_clause(self):
        findings = FindingSet({"onset_peak_minutes": 1, "severe_intensity": True})
        rules = [
            {
                "id": "rf_thunderclap",
                "output_id": "item_thunderclap",
                "source_ids": ["nice_cg150"],
                "condition": {
                    "all": [
                        {"field": "onset_peak_minutes", "operator": "lte", "value": 5},
                        {"field": "severe_intensity", "operator": "equals", "value": True},
                    ]
                },
            }
        ]

        matches = evaluate_rules(findings, rules)

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["output_id"], "item_thunderclap")
        self.assertEqual(matches[0]["source_ids"], ["nice_cg150"])
        self.assertIn("onset_peak_minutes lte 5", matches[0]["explanation"])

    def test_absent_operator_matches_missing_or_false_values(self):
        findings = FindingSet({"fever": False})

        self.assertTrue(
            evaluate_rule_condition(
                findings, {"field": "fever", "operator": "absent"}
            )
        )
        self.assertTrue(
            evaluate_rule_condition(
                findings, {"field": "meningism", "operator": "absent"}
            )
        )

    def test_no_match_returns_empty_list(self):
        findings = FindingSet({"fever": False})
        rules = [
            {
                "id": "rf_fever_meningism",
                "output_id": "item_meningitis",
                "source_ids": ["nice_cg150"],
                "condition": {
                    "all": [
                        {"field": "fever", "operator": "equals", "value": True},
                        {"field": "meningism", "operator": "equals", "value": True},
                    ]
                },
            }
        ]

        self.assertEqual(evaluate_rules(findings, rules), [])
