import json
import tempfile
from datetime import date
from pathlib import Path

from django.test import TestCase
from django.urls import reverse

from cds_core.local_launch import build_local_launch_status
from cds_core.local_setup import (
    build_local_setup_assistant_report,
    format_local_setup_assistant_report,
)
from cds_core.project_completion import (
    build_project_completion_report,
    format_project_completion_report,
)


class StaffSetupEntryTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

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

    def build_reports(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "final-verification-evidence.json"
            evidence_path.write_text(
                json.dumps(self.verified_evidence()),
                encoding="utf-8",
            )
            return (
                build_local_launch_status(
                    base_url="http://127.0.0.1:8000/",
                    today=date(2026, 6, 24),
                    evidence_path=evidence_path,
                ),
                build_local_setup_assistant_report(
                    base_url="http://127.0.0.1:8000/",
                    today=date(2026, 6, 24),
                    evidence_path=evidence_path,
                ),
                build_project_completion_report(
                    base_url="http://127.0.0.1:8000/",
                    today=date(2026, 6, 24),
                    evidence_path=evidence_path,
                ),
            )

    def test_create_staff_reviewer_entrypoint_wraps_django_prompt_safely(self):
        script_path = Path(__file__).resolve().parents[2] / "Create_Staff_Reviewer.cmd"

        body = script_path.read_text(encoding="utf-8")
        raw_body = script_path.read_bytes()

        self.assertEqual(raw_body.count(b"\r\n"), raw_body.count(b"\n"))
        self.assertIn("createsuperuser", body)
        self.assertIn("project_completion_status.py", body)
        self.assertIn("CDS_CREATE_STAFF_NO_PAUSE", body)
        self.assertIn("Django createsuperuser exit code", body)
        self.assertIn("pause", body.lower())
        self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", body)
        self.assertNotIn("--password", body)
        self.assertNotIn("test-pass", body)

    def test_reports_expose_safe_staff_setup_entry_and_raw_fallback(self):
        launch_report, setup_report, completion_report = self.build_reports()

        launch_blocker = launch_report["manual_blockers"][0]
        launch_step = next(
            step
            for step in launch_report["steps"]
            if step["action_id"] == "create_staff_reviewer"
        )
        setup_blocker = setup_report["manual_blockers"][0]
        completion_action = completion_report["next_action"]

        self.assertIn("Create_Staff_Reviewer.cmd", launch_blocker["entry_command"])
        self.assertIn("createsuperuser", launch_blocker["raw_command"])
        self.assertIn("Create_Staff_Reviewer.cmd", launch_step["entry_command"])
        self.assertIn("createsuperuser", launch_step["raw_command"])
        self.assertIn("Create_Staff_Reviewer.cmd", setup_blocker["entry_command"])
        self.assertIn("Create_Staff_Reviewer.cmd", completion_action["command"])
        self.assertIn("createsuperuser", completion_action["raw_command"])

        setup_output = format_local_setup_assistant_report(setup_report)
        completion_output = format_project_completion_report(completion_report)

        self.assertIn("Create_Staff_Reviewer.cmd", setup_output)
        self.assertIn("createsuperuser", setup_output)
        self.assertIn("Create_Staff_Reviewer.cmd", completion_output)
        self.assertIn("createsuperuser", completion_output)

    def test_launch_and_completion_pages_show_staff_setup_entry(self):
        launch_response = self.client.get(reverse("cds_core:launch_guide"))
        completion_response = self.client.get(reverse("cds_core:completion_gate"))

        self.assertEqual(launch_response.status_code, 200)
        self.assertEqual(completion_response.status_code, 200)
        self.assertContains(launch_response, "Create_Staff_Reviewer.cmd")
        self.assertContains(launch_response, "createsuperuser")
        self.assertContains(completion_response, "Create_Staff_Reviewer.cmd")
        self.assertContains(completion_response, "createsuperuser")

    def test_docs_point_staff_setup_to_safe_entrypoint(self):
        project_root = Path(__file__).resolve().parents[2]

        readme = (project_root / "README.md").read_text(encoding="utf-8")
        quick_start = (project_root / "QUICK_START.zh.md").read_text(encoding="utf-8")

        self.assertIn("Create_Staff_Reviewer.cmd", readme)
        self.assertIn("Create_Staff_Reviewer.cmd", quick_start)
        self.assertIn("createsuperuser", readme)
        self.assertIn("createsuperuser", quick_start)
