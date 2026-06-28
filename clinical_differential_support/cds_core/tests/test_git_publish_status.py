import io
import json
import tempfile
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase


DIRTY_PACKAGE_STATUS = "\n".join(
    [
        "?? .planning/2026-06-22-clinical-differential-support/",
        "?? clinical_differential_support/",
        "?? docs/superpowers/",
        "?? render.yaml",
    ]
)


class GitPublishStatusTests(TestCase):
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
                    "generated_on": "2026-06-27",
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
            "git-publish-reviewer",
            is_staff=True,
        )

    def runner(self, status_stdout=DIRTY_PACKAGE_STATUS, branch_stdout="master"):
        from cds_core.git_publish_status import CommandResult, PUBLISH_STATUS_COMMAND

        calls = []

        def fake_runner(command, cwd):
            calls.append(command)
            if command == PUBLISH_STATUS_COMMAND:
                return CommandResult(exit_code=0, stdout=status_stdout, stderr="")
            if command == "git branch --show-current":
                return CommandResult(exit_code=0, stdout=f"{branch_stdout}\n", stderr="")
            raise AssertionError(f"Unexpected command: {command}")

        fake_runner.calls = calls
        return fake_runner

    def deployment_runner(self, publish_status_stdout=DIRTY_PACKAGE_STATUS):
        from cds_core.deployment_status import CommandProbeResult
        from cds_core.git_publish_status import PUBLISH_STATUS_COMMAND

        def fake_runner(command, cwd):
            if command == PUBLISH_STATUS_COMMAND:
                return CommandProbeResult(
                    exit_code=0,
                    stdout=publish_status_stdout,
                    stderr="",
                )
            if command == "git branch --show-current":
                return CommandProbeResult(exit_code=0, stdout="master\n", stderr="")
            if command == "git remote -v":
                return CommandProbeResult(exit_code=0, stdout="", stderr="")
            if command == "render --version":
                return CommandProbeResult(exit_code=1, stdout="", stderr="missing")
            raise AssertionError(f"Unexpected command: {command}")

        return fake_runner

    def test_report_detects_scoped_uncommitted_package_without_mutation(self):
        from cds_core.git_publish_status import (
            PUBLISH_STATUS_BATCH_COMMAND,
            PUBLISH_STATUS_COMMAND,
            build_git_publish_status_report,
        )

        fake_runner = self.runner(status_stdout=DIRTY_PACKAGE_STATUS)

        report = build_git_publish_status_report(
            today=date(2026, 6, 27),
            command_runner=fake_runner,
        )

        self.assertEqual(report["report_type"], "git_publish_status")
        self.assertEqual(report["status"], "publish_package_uncommitted")
        self.assertEqual(report["exit_code"], 2)
        self.assertEqual(report["dirty_count"], 4)
        self.assertEqual(report["commands_run"], [PUBLISH_STATUS_COMMAND, "git branch --show-current"])
        self.assertIn(PUBLISH_STATUS_BATCH_COMMAND, report["next_action"]["command"])
        self.assertIn("git status --short --", report["suggested_commands"]["review"])
        self.assertIn("git add -- clinical_differential_support", report["suggested_commands"]["stage"])
        self.assertIn("git commit -m", report["suggested_commands"]["commit"])
        self.assertTrue(report["safety_scope"]["read_only"])
        self.assertTrue(report["safety_scope"]["does_not_commit"])
        self.assertTrue(report["safety_scope"]["does_not_push"])

    def test_report_marks_clean_package_ready_for_remote_setup(self):
        from cds_core.git_publish_status import (
            CONFIGURE_GIT_REMOTE_BATCH_COMMAND,
            build_git_publish_status_report,
        )

        report = build_git_publish_status_report(
            today=date(2026, 6, 27),
            command_runner=self.runner(status_stdout=""),
        )

        self.assertEqual(report["status"], "publish_package_ready")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["dirty_count"], 0)
        self.assertEqual(report["next_action"]["action_id"], "configure_git_remote")
        self.assertIn(CONFIGURE_GIT_REMOTE_BATCH_COMMAND, report["next_action"]["command"])

    def test_formatter_outputs_stepwise_commands_without_credentials(self):
        from cds_core.git_publish_status import (
            build_git_publish_status_report,
            format_git_publish_status_report,
        )

        report = build_git_publish_status_report(
            today=date(2026, 6, 27),
            command_runner=self.runner(status_stdout=DIRTY_PACKAGE_STATUS),
        )
        output = format_git_publish_status_report(report)

        self.assertIn("Git Publish Readiness Assistant", output)
        self.assertIn("publish_package_uncommitted", output)
        self.assertIn("git status --short --", output)
        self.assertIn("git add -- clinical_differential_support", output)
        self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", output)
        self.assertNotIn("--password", output)

    def test_cli_outputs_json_and_text_without_mutating_git(self):
        from scripts.git_publish_status import main

        json_stdout = io.StringIO()
        with redirect_stdout(json_stdout):
            exit_code = main(["--json"], command_runner=self.runner(status_stdout=DIRTY_PACKAGE_STATUS))

        payload = json.loads(json_stdout.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["status"], "publish_package_uncommitted")
        self.assertIn("Publish_Status.cmd", payload["next_action"]["command"])

        text_stdout = io.StringIO()
        with redirect_stdout(text_stdout):
            main([], command_runner=self.runner(status_stdout=DIRTY_PACKAGE_STATUS))
        text = text_stdout.getvalue()
        self.assertIn("Git Publish Readiness Assistant", text)
        self.assertNotIn("git push", text)

    def test_windows_entrypoint_wraps_publish_status_without_git_mutation(self):
        script_path = Path(__file__).resolve().parents[2] / "Publish_Status.cmd"

        body = script_path.read_text(encoding="utf-8")
        raw_body = script_path.read_bytes()

        self.assertEqual(raw_body.count(b"\r\n"), raw_body.count(b"\n"))
        self.assertIn("git_publish_status.py", body)
        self.assertIn("CDS_PUBLISH_STATUS_NO_PAUSE", body)
        self.assertIn("PUBLISH_JSON_MODE", body)
        self.assertIn('if not "%PUBLISH_JSON_MODE%"=="1"', body)
        self.assertIn("Git publish readiness exit code", body)
        self.assertNotIn("git add", body)
        self.assertNotIn("git commit", body)
        self.assertNotIn("git push", body)
        self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", body)

    def test_deployment_status_blocks_remote_when_publish_package_is_dirty(self):
        from cds_core.deployment_status import build_deployment_status_report

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)

        report = build_deployment_status_report(
            today=date(2026, 6, 27),
            evidence_path=evidence_path,
            command_runner=self.deployment_runner(publish_status_stdout=DIRTY_PACKAGE_STATUS),
        )

        checks = {check["check_id"]: check for check in report["deployment_checks"]}
        self.assertEqual(report["status"], "ready_for_publish_package")
        self.assertEqual(report["next_action"]["action_id"], "review_commit_publish_package")
        self.assertIn("Publish_Status.cmd", report["next_action"]["command"])
        self.assertNotIn("Configure_Git_Remote.cmd", report["next_action"]["command"])
        self.assertEqual(checks["git_publish_package"]["status"], "action_required")
        self.assertEqual(checks["git_publish_package"]["value"], "4 uncommitted")

    def test_deployment_status_advances_to_remote_when_publish_package_is_clean(self):
        from cds_core.deployment_status import build_deployment_status_report

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)

        report = build_deployment_status_report(
            today=date(2026, 6, 27),
            evidence_path=evidence_path,
            command_runner=self.deployment_runner(publish_status_stdout=""),
        )

        self.assertEqual(report["status"], "ready_for_remote_setup")
        self.assertEqual(report["next_action"]["action_id"], "create_git_remote")
        self.assertIn("Configure_Git_Remote.cmd", report["next_action"]["command"])

    def test_docs_link_to_publish_status_before_remote_setup(self):
        project_dir = Path(__file__).resolve().parents[2]
        for filename in ["README.md", "QUICK_START.zh.md", "DEPLOYMENT.md"]:
            with self.subTest(filename=filename):
                body = (project_dir / filename).read_text(encoding="utf-8-sig")
                self.assertIn("Publish_Status.cmd", body)
                self.assertIn("Configure_Git_Remote.cmd", body)
