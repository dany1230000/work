import json
import tempfile
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.project_completion import (
    build_project_completion_report,
    format_project_completion_report,
)


class ProjectCompletionGateTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def build_report(self, evidence_payload=None):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "final-verification-evidence.json"
            if evidence_payload is not None:
                evidence_path.write_text(json.dumps(evidence_payload), encoding="utf-8")
            return build_project_completion_report(
                base_url="http://127.0.0.1:8000/",
                today=date(2026, 6, 24),
                evidence_path=evidence_path,
            )

    def create_staff_reviewer(self):
        return get_user_model().objects.create_user(
            "completion-reviewer",
            password="test-pass",
            is_staff=True,
        )

    def verified_evidence(self):
        return {
            "artifact_type": "final_verification_evidence",
            "overall_status": "verified",
            "generated_on": "2026-06-24",
            "gate_status_at_recording": "ready_for_final_verification",
            "command_results": [
                {"command_id": "full_regression", "status": "passed", "exit_code": 0},
                {"command_id": "django_system_check", "status": "passed", "exit_code": 0},
                {"command_id": "live_smoke", "status": "passed", "exit_code": 0},
                {"command_id": "next_action_shell", "status": "passed", "exit_code": 0},
            ],
        }

    def test_gate_reports_manual_setup_required_until_staff_reviewer_exists(self):
        report = self.build_report(evidence_payload=self.verified_evidence())

        self.assertEqual(report["report_type"], "project_completion_gate")
        self.assertEqual(report["status"], "manual_setup_required")
        self.assertEqual(report["exit_code"], 2)
        self.assertEqual(report["completion_url"], "http://127.0.0.1:8000/completion/")
        self.assertEqual(report["next_action"]["action_id"], "create_staff_reviewer")
        self.assertIn("Create_Staff_Reviewer.cmd", report["next_action"]["command"])
        self.assertIn("createsuperuser", report["next_action"]["raw_command"])
        self.assertIn("Final_Check.cmd", report["final_check"]["command"])
        self.assertTrue(report["safety_scope"]["does_not_create_credentials"])
        self.assertTrue(report["safety_scope"]["does_not_print_credentials"])

    def test_gate_reports_final_complete_when_all_checks_pass(self):
        self.create_staff_reviewer()

        report = self.build_report(evidence_payload=self.verified_evidence())

        self.assertEqual(report["status"], "final_complete")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["next_action"]["action_id"], "project_final_complete")
        self.assertEqual(report["manual_blockers"], [])
        self.assertEqual(report["deployment_status"]["url"], "http://127.0.0.1:8000/deployment/")
        self.assertIn("Deploy_Status.cmd", report["deployment_status"]["windows_entry_command"])
        self.assertTrue(all(check["status"] == "passed" for check in report["completion_checks"]))

    def test_formatter_outputs_chinese_first_final_gate(self):
        report = self.build_report(evidence_payload=self.verified_evidence())

        output = format_project_completion_report(report)

        self.assertIn("最終版完成判斷 / Final Project Gate", output)
        self.assertIn("manual_setup_required", output)
        self.assertIn("exit_code=2", output)
        self.assertIn("Final_Check.cmd", output)
        self.assertIn("http://127.0.0.1:8000/completion/", output)
        self.assertIn("Create_Staff_Reviewer.cmd", output)
        self.assertIn("createsuperuser", output)

    def test_windows_final_check_entrypoint_wraps_completion_cli_without_credentials(self):
        script_path = Path(__file__).resolve().parents[2] / "Final_Check.cmd"

        body = script_path.read_text(encoding="utf-8")
        raw_body = script_path.read_bytes()

        self.assertEqual(raw_body.count(b"\r\n"), raw_body.count(b"\n"))
        self.assertIn("project_completion_status.py", body)
        self.assertIn("CDS_FINAL_CHECK_NO_PAUSE", body)
        self.assertIn("Final gate exit code", body)
        self.assertIn("pause", body.lower())
        self.assertNotIn("createsuperuser", body)
        self.assertNotIn("test-pass", body)

    def test_public_completion_page_renders_final_gate_and_next_action(self):
        response = self.client.get(reverse("cds_core:completion_gate"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "最終版完成判斷 / Final Project Gate")
        self.assertContains(response, "manual_setup_required")
        self.assertContains(response, "Final_Check.cmd")
        self.assertContains(response, "Deployment Operations Center")
        self.assertContains(response, "Deploy_Status.cmd")
        self.assertContains(response, "/deployment/")
        self.assertContains(response, "create_staff_reviewer")
        self.assertContains(response, "Create_Staff_Reviewer.cmd")
        self.assertNotIn("�", body)
