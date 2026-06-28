import json
from datetime import date
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.final_verification import build_final_verification_gate


class FinalVerificationGateTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "final-verification-reviewer",
            password="test-pass",
            is_staff=True,
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_report_lists_final_gate_status_commands_and_exports(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp_dir:
            report = build_final_verification_gate(
                today=date(2026, 6, 24),
                evidence_path=Path(tmp_dir) / "missing-evidence.json",
            )

        self.assertEqual(report["report_type"], "final_verification_gate")
        self.assertEqual(report["gate_status"], "ready_for_final_verification")
        self.assertEqual(
            report["next_action"]["action_id"],
            "run_required_verification_commands",
        )
        self.assertEqual(report["next_action"]["status"], "ready_to_run")
        self.assertEqual(
            report["required_commands"][0]["command"],
            r"py -B .\clinical_differential_support\manage.py test -v 2",
        )
        self.assertEqual(report["required_commands"][0]["expected_result"], "203 tests pass")
        self.assertEqual(
            report["handoff_exports"]["handoff_bundle_zip"],
            "/review/exports/handoff-bundle.zip",
        )
        self.assertTrue(report["safety_scope"]["staff_only"])
        self.assertTrue(report["safety_scope"]["summary_only"])
        self.assertEqual(report["latest_evidence"]["status"], "not_recorded")

    def test_next_action_shell_command_quotes_python_code_for_windows_shell(self):
        report = build_final_verification_gate(today=date(2026, 6, 24))

        command = next(
            command["command"]
            for command in report["required_commands"]
            if command["command_id"] == "next_action_shell"
        )

        self.assertIn('-c "', command)
        self.assertTrue(command.endswith('"'))

    def test_report_reads_verified_latest_evidence(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "final-verification-evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "artifact_type": "final_verification_evidence",
                        "overall_status": "verified",
                        "generated_on": "2026-06-24",
                        "gate_status_at_recording": "ready_for_final_verification",
                        "command_results": [
                            {
                                "command_id": "full_regression",
                                "status": "passed",
                                "exit_code": 0,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = build_final_verification_gate(
                today=date(2026, 6, 24),
                evidence_path=evidence_path,
            )

        self.assertEqual(report["latest_evidence"]["status"], "verified")
        self.assertEqual(report["latest_evidence"]["command_count"], 1)
        self.assertEqual(
            report["latest_evidence"]["gate_status_at_recording"],
            "ready_for_final_verification",
        )

    def test_unauthenticated_final_verification_page_redirects_to_reviewer_login(self):
        path = reverse("cds_core:final_verification")

        response = self.client.get(path)

        self.assertReviewerLoginRedirect(response, path)

    def test_staff_final_verification_page_renders_commands_and_exports(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:final_verification"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Final Verification Gate")
        self.assertContains(response, "ready_for_final_verification")
        self.assertContains(response, "run_required_verification_commands")
        self.assertContains(response, "manage.py test -v 2")
        self.assertContains(response, "handoff-bundle.zip")

    def test_unauthenticated_final_verification_json_redirects_to_reviewer_login(self):
        path = reverse("cds_core:export_final_verification_json")

        response = self.client.get(path)

        self.assertReviewerLoginRedirect(response, path)

    def test_staff_final_verification_json_is_summary_only(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_final_verification_json"))
        body = response.content.decode("utf-8")
        payload = json.loads(body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["gate_status"], "ready_for_final_verification")
        self.assertIn("final-verification.json", response["Content-Disposition"])
        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("Possible acute coronary syndrome", body)
        self.assertNotIn("https://", body)

    def test_next_action_and_release_readiness_link_to_final_verification(self):
        self.staff_login()

        next_action_response = self.client.get(reverse("cds_core:next_actions"))
        readiness_response = self.client.get(reverse("cds_core:release_readiness"))

        self.assertContains(next_action_response, "Final Verification Gate")
        self.assertContains(next_action_response, reverse("cds_core:final_verification"))
        self.assertContains(readiness_response, "Final Verification Gate")
        self.assertContains(readiness_response, reverse("cds_core:final_verification"))
