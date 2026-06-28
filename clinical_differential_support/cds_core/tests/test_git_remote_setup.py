import io
import json
import tempfile
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase


class GitRemoteSetupTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def verified_evidence_path(self):
        tmp_dir = tempfile.TemporaryDirectory()
        evidence_path = Path(tmp_dir.name) / "final-verification-evidence.json"
        evidence_path.write_text(
            json.dumps(
                {
                    "artifact_type": "final_verification_evidence",
                    "overall_status": "verified",
                    "generated_on": "2026-06-26",
                    "gate_status_at_recording": "ready_for_final_verification",
                    "command_results": [
                        {"command_id": "full_regression", "status": "passed", "exit_code": 0},
                        {"command_id": "django_system_check", "status": "passed", "exit_code": 0},
                        {"command_id": "live_smoke", "status": "passed", "exit_code": 0},
                        {"command_id": "next_action_shell", "status": "passed", "exit_code": 0},
                    ],
                }
            ),
            encoding="utf-8",
        )
        return tmp_dir, evidence_path

    def create_staff_reviewer(self):
        return get_user_model().objects.create_user(
            "git-remote-reviewer",
            is_staff=True,
        )

    def runner(self, remote_stdout="", branch_stdout="master"):
        from cds_core.git_remote_setup import CommandResult

        calls = []

        def fake_runner(command, cwd):
            calls.append(command)
            if command == "git remote -v":
                return CommandResult(exit_code=0, stdout=remote_stdout, stderr="")
            if command.startswith("git remote add origin "):
                return CommandResult(exit_code=0, stdout="", stderr="")
            if command == "git branch --show-current":
                return CommandResult(exit_code=0, stdout=f"{branch_stdout}\n", stderr="")
            if command.startswith("git push -u origin "):
                return CommandResult(exit_code=0, stdout="pushed", stderr="")
            raise AssertionError(f"Unexpected command: {command}")

        fake_runner.calls = calls
        return fake_runner

    def test_missing_remote_url_reports_step_by_step_command_without_mutation(self):
        from cds_core.git_remote_setup import build_git_remote_setup_report

        fake_runner = self.runner(remote_stdout="")

        report = build_git_remote_setup_report(
            today=date(2026, 6, 26),
            command_runner=fake_runner,
        )

        self.assertEqual(report["report_type"], "git_remote_setup")
        self.assertEqual(report["status"], "remote_url_required")
        self.assertEqual(report["exit_code"], 2)
        self.assertEqual(report["existing_origin"], "")
        self.assertEqual(report["commands_run"], ["git remote -v"])
        self.assertIn("Configure_Git_Remote.cmd", report["next_action"]["command"])
        self.assertIn("--remote-url <your-repo-url>", report["next_action"]["command"])
        self.assertFalse(report["push_requested"])
        self.assertTrue(report["safety_scope"]["does_not_store_credentials"])
        self.assertTrue(report["safety_scope"]["push_requires_explicit_flag"])

    def test_rejects_https_remote_url_with_embedded_credentials_without_echoing_secret(self):
        from cds_core.git_remote_setup import (
            build_git_remote_setup_report,
            format_git_remote_setup_report,
        )

        credential_url = (
            "https://"
            + "operator"
            + ":"
            + "token-value"
            + "@github.com/example/clinical-support.git"
        )
        fake_runner = self.runner(remote_stdout="")

        report = build_git_remote_setup_report(
            remote_url=credential_url,
            today=date(2026, 6, 26),
            command_runner=fake_runner,
        )
        text = format_git_remote_setup_report(report)
        payload = json.dumps(report, ensure_ascii=False)

        self.assertEqual(report["status"], "invalid_remote_url")
        self.assertEqual(report["exit_code"], 2)
        self.assertEqual(fake_runner.calls, ["git remote -v"])
        self.assertNotIn("token-value", payload)
        self.assertNotIn("token-value", text)
        self.assertIn("embedded credentials", report["validation_error"])

    def test_adds_origin_for_supported_https_remote_without_push(self):
        from cds_core.git_remote_setup import build_git_remote_setup_report

        fake_runner = self.runner(remote_stdout="")

        report = build_git_remote_setup_report(
            remote_url="https://github.com/example/clinical-support.git",
            today=date(2026, 6, 26),
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "remote_configured")
        self.assertEqual(report["exit_code"], 0)
        self.assertIn(
            "git remote add origin https://github.com/example/clinical-support.git",
            fake_runner.calls,
        )
        self.assertNotIn("git push -u origin master", fake_runner.calls)
        self.assertIn("--push", report["next_action"]["detail_en"])

    def test_refuses_to_overwrite_different_existing_origin(self):
        from cds_core.git_remote_setup import build_git_remote_setup_report

        fake_runner = self.runner(
            remote_stdout="origin https://github.com/example/other.git (fetch)\n"
        )

        report = build_git_remote_setup_report(
            remote_url="https://github.com/example/clinical-support.git",
            today=date(2026, 6, 26),
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "remote_conflict")
        self.assertEqual(report["exit_code"], 2)
        self.assertNotIn(
            "git remote set-url origin https://github.com/example/clinical-support.git",
            fake_runner.calls,
        )
        self.assertNotIn(
            "git remote add origin https://github.com/example/clinical-support.git",
            fake_runner.calls,
        )
        self.assertIn("existing origin", report["next_action"]["detail_en"])

    def test_push_requires_explicit_flag_and_uses_current_branch(self):
        from cds_core.git_remote_setup import build_git_remote_setup_report

        fake_runner = self.runner(
            remote_stdout="origin https://github.com/example/clinical-support.git (fetch)\n",
            branch_stdout="main",
        )

        report = build_git_remote_setup_report(
            remote_url="https://github.com/example/clinical-support.git",
            push=True,
            today=date(2026, 6, 26),
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "remote_pushed")
        self.assertEqual(report["exit_code"], 0)
        self.assertIn("git branch --show-current", fake_runner.calls)
        self.assertIn("git push -u origin main", fake_runner.calls)
        self.assertTrue(report["push_requested"])

    def test_cli_outputs_json_and_text_without_credentials(self):
        from scripts.configure_git_remote import main

        json_stdout = io.StringIO()
        with redirect_stdout(json_stdout):
            exit_code = main(["--json"], command_runner=self.runner(remote_stdout=""))

        payload = json.loads(json_stdout.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["status"], "remote_url_required")
        self.assertIn("Configure_Git_Remote.cmd", payload["next_action"]["command"])

        text_stdout = io.StringIO()
        with redirect_stdout(text_stdout):
            main([], command_runner=self.runner(remote_stdout=""))
        text = text_stdout.getvalue()
        self.assertIn("Git Remote Setup Assistant", text)
        self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", text)

    def test_windows_entrypoint_wraps_configure_script_without_credentials(self):
        script_path = Path(__file__).resolve().parents[2] / "Configure_Git_Remote.cmd"

        body = script_path.read_text(encoding="utf-8")
        raw_body = script_path.read_bytes()

        self.assertEqual(raw_body.count(b"\r\n"), raw_body.count(b"\n"))
        self.assertIn("configure_git_remote.py", body)
        self.assertIn("CDS_GIT_REMOTE_NO_PAUSE", body)
        self.assertIn("Git remote setup exit code", body)
        self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", body)
        self.assertNotIn("--password", body)

    def test_deployment_status_and_docs_point_to_remote_setup_assistant(self):
        from cds_core.deployment_status import build_deployment_status_report
        from cds_core.git_remote_setup import CONFIGURE_GIT_REMOTE_BATCH_COMMAND

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)

        def deployment_runner(command, cwd):
            from cds_core.deployment_status import CommandProbeResult
            from cds_core.git_publish_status import PUBLISH_STATUS_COMMAND

            if command == PUBLISH_STATUS_COMMAND:
                return CommandProbeResult(exit_code=0, stdout="", stderr="")
            if command == "git branch --show-current":
                return CommandProbeResult(exit_code=0, stdout="master\n", stderr="")
            if command == "git remote -v":
                return CommandProbeResult(exit_code=0, stdout="", stderr="")
            if command == "render --version":
                return CommandProbeResult(exit_code=1, stdout="", stderr="missing")
            raise AssertionError(f"Unexpected command: {command}")

        report = build_deployment_status_report(
            today=date(2026, 6, 26),
            evidence_path=evidence_path,
            command_runner=deployment_runner,
        )

        self.assertEqual(report["status"], "ready_for_remote_setup")
        self.assertEqual(report["next_action"]["action_id"], "create_git_remote")
        self.assertIn(CONFIGURE_GIT_REMOTE_BATCH_COMMAND, report["next_action"]["command"])
        self.assertIn("--remote-url <your-repo-url>", report["next_action"]["command"])
        self.assertNotIn("git remote add origin", report["next_action"]["command"])

        project_dir = Path(__file__).resolve().parents[2]
        for filename in ["README.md", "QUICK_START.zh.md", "DEPLOYMENT.md"]:
            with self.subTest(filename=filename):
                body = (project_dir / filename).read_text(encoding="utf-8-sig")
                self.assertIn("Configure_Git_Remote.cmd", body)
                self.assertIn("--remote-url <your-repo-url>", body)
