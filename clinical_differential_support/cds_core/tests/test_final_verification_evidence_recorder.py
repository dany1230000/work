import json
import tempfile
from datetime import date
from pathlib import Path

from django.test import TestCase


class FinalVerificationEvidenceRecorderTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def test_recorder_writes_summary_only_verified_evidence(self):
        from scripts.record_final_verification_evidence import (
            CommandRunResult,
            record_final_verification_evidence,
        )

        calls = []

        def fake_runner(command, cwd):
            calls.append((command, cwd))
            return CommandRunResult(
                exit_code=0,
                stdout="173 tests passed\nThunderclap headache should be omitted",
                stderr="",
            )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "final-verification-evidence.json"

            result = record_final_verification_evidence(
                output_path=output_path,
                runner=fake_runner,
                today=date(2026, 6, 24),
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        self.assertEqual(len(calls), 4)
        self.assertEqual(payload["artifact_type"], "final_verification_evidence")
        self.assertEqual(payload["overall_status"], "verified")
        self.assertEqual(payload["gate_status_at_recording"], "ready_for_final_verification")
        self.assertEqual(payload["command_results"][0]["command_id"], "full_regression")
        self.assertEqual(payload["command_results"][0]["exit_code"], 0)
        self.assertEqual(payload["command_results"][0]["status"], "passed")
        self.assertIn("173 tests passed", payload["command_results"][0]["stdout_summary"])
        body = json.dumps(payload)
        self.assertNotIn("Thunderclap headache", body)
        self.assertNotIn("Possible acute coronary syndrome", body)
        self.assertNotIn("https://", body)

    def test_recorder_marks_failed_command_without_running_later_commands(self):
        from scripts.record_final_verification_evidence import (
            CommandRunResult,
            record_final_verification_evidence,
        )

        calls = []

        def fake_runner(command, cwd):
            calls.append(command)
            return CommandRunResult(
                exit_code=1,
                stdout="failure details",
                stderr="traceback should be summarized",
            )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "failed-evidence.json"

            result = record_final_verification_evidence(
                output_path=output_path,
                runner=fake_runner,
                today=date(2026, 6, 24),
            )
            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertFalse(result.ok)
        self.assertEqual(len(calls), 1)
        self.assertEqual(payload["overall_status"], "failed")
        self.assertEqual(payload["command_results"][0]["status"], "failed")
        self.assertEqual(payload["command_results"][0]["stderr_summary"], "traceback should be summarized")
