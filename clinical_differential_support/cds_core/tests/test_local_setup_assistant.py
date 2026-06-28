import json
import tempfile
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase

from cds_core.local_setup import (
    build_local_setup_assistant_report,
    format_local_setup_assistant_report,
)


class LocalSetupAssistantTests(TestCase):
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
            return build_local_setup_assistant_report(
                base_url="http://127.0.0.1:8000/",
                today=date(2026, 6, 24),
                evidence_path=evidence_path,
            )

    def create_staff_reviewer(self):
        return get_user_model().objects.create_user(
            "setup-assistant-reviewer",
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

    def test_assistant_reports_manual_setup_required_without_staff_reviewer(self):
        report = self.build_report()

        self.assertEqual(report["report_type"], "local_setup_assistant")
        self.assertEqual(report["status"], "setup_required")
        self.assertEqual(report["exit_code"], 2)
        self.assertEqual(report["next_step"]["action_id"], "create_staff_reviewer")
        self.assertIn("Create_Staff_Reviewer.cmd", report["next_step"]["command"])
        self.assertIn("createsuperuser", report["next_step"]["raw_command"])
        self.assertEqual(report["launch_control_url"], "http://127.0.0.1:8000/launch/")
        self.assertTrue(report["safety_scope"]["does_not_create_credentials"])
        self.assertTrue(report["safety_scope"]["does_not_print_credentials"])

    def test_assistant_reports_ready_when_staff_and_evidence_are_ready(self):
        self.create_staff_reviewer()

        report = self.build_report(evidence_payload=self.verified_evidence())

        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["next_step"]["action_id"], "start_local_server")
        self.assertIn("Start_Local_Server.cmd", report["next_step"]["command"])
        self.assertEqual(report["launch_control_url"], "http://127.0.0.1:8000/launch/")

    def test_formatter_outputs_chinese_first_next_step_and_exit_code(self):
        report = self.build_report()

        output = format_local_setup_assistant_report(report)

        self.assertIn("本機設定助手", output)
        self.assertIn("Local Setup Assistant", output)
        self.assertIn("setup_required", output)
        self.assertIn("exit_code=2", output)
        self.assertIn("createsuperuser", output)
        self.assertIn("http://127.0.0.1:8000/launch/", output)

    def test_windows_next_step_entrypoint_wraps_assistant_without_credentials(self):
        script_path = Path(__file__).resolve().parents[2] / "Next_Step.cmd"

        body = script_path.read_text(encoding="utf-8")
        raw_body = script_path.read_bytes()

        self.assertEqual(raw_body.count(b"\r\n"), raw_body.count(b"\n"))
        self.assertIn("local_setup_assistant.py", body)
        self.assertIn("CDS_NEXT_STEP_NO_PAUSE", body)
        self.assertIn("Assistant exit code", body)
        self.assertIn("pause", body.lower())
        self.assertNotIn("createsuperuser", body)
        self.assertNotIn("test-pass", body)
