import json
import tempfile
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase

from cds_core.local_launch import build_local_launch_status, format_local_launch_status


class LocalLaunchStatusTests(TestCase):
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
            return build_local_launch_status(
                base_url="http://127.0.0.1:8000/",
                today=date(2026, 6, 24),
                evidence_path=evidence_path,
            )

    def create_staff_reviewer(self):
        return get_user_model().objects.create_user(
            "local-launch-reviewer",
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

    def test_status_tells_user_to_create_staff_reviewer_first(self):
        report = self.build_report()

        self.assertEqual(report["report_type"], "local_launch_status")
        self.assertEqual(report["operator_summary"]["status"], "needs_manual_setup")
        self.assertFalse(report["environment"]["staff_account_exists"])
        self.assertEqual(report["environment_checks"][0]["check_id"], "staff_reviewer")
        self.assertEqual(report["environment_checks"][0]["status"], "action_required")
        self.assertEqual(report["manual_blockers"][0]["action_id"], "create_staff_reviewer")
        self.assertTrue(report["manual_blockers"][0]["manual_only"])
        self.assertTrue(report["manual_blockers"][0]["does_not_store_credentials"])
        self.assertEqual(report["next_step"]["action_id"], "create_staff_reviewer")
        self.assertEqual(report["current_step"]["step_number"], 1)
        self.assertEqual(report["steps"][0]["status"], "current")
        self.assertEqual(report["steps"][0]["action_id"], "create_staff_reviewer")
        self.assertTrue(report["steps"][0]["manual_required"])
        self.assertEqual(report["steps"][0]["command_kind"], "manual_shell")
        self.assertEqual(report["steps"][1]["status"], "locked")
        self.assertEqual(report["steps"][2]["status"], "locked")
        self.assertIn("Create_Staff_Reviewer.cmd", report["next_step"]["command"])
        self.assertIn("createsuperuser", report["next_step"]["raw_command"])
        self.assertEqual(
            report["urls"]["next_actions"],
            "http://127.0.0.1:8000/review/next-actions/",
        )
        self.assertTrue(report["safety_scope"]["staff_only_for_governance"])

    def test_status_runs_recorder_when_staff_exists_but_evidence_is_missing(self):
        self.create_staff_reviewer()

        report = self.build_report()

        self.assertEqual(report["operator_summary"]["status"], "needs_verification")
        self.assertTrue(report["environment"]["staff_account_exists"])
        self.assertEqual(report["environment_checks"][0]["status"], "passed")
        self.assertEqual(report["environment_checks"][1]["check_id"], "final_evidence")
        self.assertEqual(report["environment_checks"][1]["status"], "action_required")
        self.assertEqual(
            report["manual_blockers"][0]["action_id"],
            "run_final_verification_recorder",
        )
        self.assertEqual(report["final_verification"]["latest_evidence_status"], "not_recorded")
        self.assertEqual(report["next_step"]["action_id"], "run_final_verification_recorder")
        self.assertEqual(report["current_step"]["step_number"], 2)
        self.assertEqual(report["steps"][0]["status"], "done")
        self.assertEqual(report["steps"][1]["status"], "current")
        self.assertEqual(report["steps"][2]["status"], "locked")
        self.assertIn(
            "record_final_verification_evidence.py",
            report["next_step"]["command"],
        )

    def test_status_starts_server_when_staff_and_evidence_are_ready(self):
        self.create_staff_reviewer()

        report = self.build_report(evidence_payload=self.verified_evidence())

        self.assertEqual(report["operator_summary"]["status"], "ready_for_local_operation")
        self.assertEqual(report["manual_blockers"], [])
        self.assertTrue(all(check["status"] == "passed" for check in report["environment_checks"]))
        self.assertEqual(report["next_step"]["action_id"], "start_local_server")
        self.assertIn("Start_Local_Server.cmd", report["next_step"]["command"])
        self.assertEqual(report["current_step"]["step_number"], 3)
        self.assertEqual(report["steps"][0]["status"], "done")
        self.assertEqual(report["steps"][1]["status"], "done")
        self.assertEqual(report["steps"][2]["status"], "current")
        self.assertEqual(report["steps"][3]["status"], "ready")
        self.assertEqual(
            report["steps"][5]["url"],
            "http://127.0.0.1:8000/review/final-verification/",
        )
        self.assertEqual(report["final_verification"]["latest_evidence_status"], "verified")
        self.assertEqual(report["final_verification"]["failed_command_count"], 0)

    def test_formatter_outputs_numbered_chinese_first_step_guide(self):
        self.create_staff_reviewer()
        report = self.build_report(evidence_payload=self.verified_evidence())

        output = format_local_launch_status(report)

        self.assertIn("一步一步", output)
        self.assertIn("步驟 1/6", output)
        self.assertIn("步驟 3/6", output)
        self.assertIn("現在", output)
        self.assertIn("Final Verification Gate", output)
        self.assertIn("http://127.0.0.1:8000/", output)
        self.assertIn("verified", output)
        self.assertIn("環境檢查", output)
        self.assertIn("ready_for_local_operation", output)
