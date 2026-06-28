import io
import json
import tempfile
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse


class DeploymentStatusTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def setUp(self):
        cache.clear()

    def create_staff_reviewer(self):
        return get_user_model().objects.create_user(
            "deployment-status-reviewer",
            password="test-pass",
            is_staff=True,
        )

    def verified_evidence_path(self):
        tmp_dir = tempfile.TemporaryDirectory()
        evidence_path = Path(tmp_dir.name) / "final-verification-evidence.json"
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
                        },
                        {
                            "command_id": "django_system_check",
                            "status": "passed",
                            "exit_code": 0,
                        },
                        {
                            "command_id": "live_smoke",
                            "status": "passed",
                            "exit_code": 0,
                        },
                        {
                            "command_id": "next_action_shell",
                            "status": "passed",
                            "exit_code": 0,
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        return tmp_dir, evidence_path

    def public_deploy_evidence_path(self):
        tmp_dir = tempfile.TemporaryDirectory()
        evidence_path = Path(tmp_dir.name) / "render-public-deployment.json"
        evidence_path.write_text(
            json.dumps(
                {
                    "artifact_type": "render_public_deployment_verification",
                    "status": "live",
                    "service_url": "https://clinical-differential-support.onrender.com",
                    "health_url": "https://clinical-differential-support.onrender.com/health/",
                    "http_status": 200,
                    "checks": {"database": "ok"},
                    "render_service_id": "srv-test",
                    "render_deploy_id": "dep-test",
                    "commit": "abc1234",
                    "verified_at": "2026-06-28T11:24:51+08:00",
                }
            ),
            encoding="utf-8",
        )
        return tmp_dir, evidence_path

    def runner(
        self,
        git_remote_stdout="",
        render_version_exit=1,
        render_whoami_exit=1,
        git_publish_stdout="",
    ):
        from cds_core.deployment_status import CommandProbeResult
        from cds_core.git_publish_status import PUBLISH_STATUS_COMMAND

        def fake_runner(command, cwd):
            if command == PUBLISH_STATUS_COMMAND:
                return CommandProbeResult(
                    exit_code=0,
                    stdout=git_publish_stdout,
                    stderr="",
                )
            if command == "git branch --show-current":
                return CommandProbeResult(exit_code=0, stdout="master\n", stderr="")
            if command == "git remote -v":
                return CommandProbeResult(
                    exit_code=0,
                    stdout=git_remote_stdout,
                    stderr="",
                )
            if command == "render --version":
                return CommandProbeResult(
                    exit_code=render_version_exit,
                    stdout="render version 2.3.0" if render_version_exit == 0 else "",
                    stderr="" if render_version_exit == 0 else "not installed",
                )
            if command == "render whoami -o json":
                return CommandProbeResult(
                    exit_code=render_whoami_exit,
                    stdout='{"email":"operator@example.com"}'
                    if render_whoami_exit == 0
                    else "",
                    stderr="" if render_whoami_exit == 0 else "not authenticated",
                )
            raise AssertionError(f"Unexpected command: {command}")

        return fake_runner

    def test_report_points_to_git_remote_when_local_ready_but_no_remote_exists(self):
        from cds_core.deployment_status import build_deployment_status_report

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)

        report = build_deployment_status_report(
            base_url="http://127.0.0.1:8000/",
            today=date(2026, 6, 26),
            evidence_path=evidence_path,
            command_runner=self.runner(git_remote_stdout=""),
        )

        checks = {check["check_id"]: check for check in report["deployment_checks"]}
        self.assertEqual(report["report_type"], "deployment_status")
        self.assertEqual(report["status"], "ready_for_remote_setup")
        self.assertEqual(report["exit_code"], 2)
        self.assertEqual(report["deployment_url"], "http://127.0.0.1:8000/deployment/")
        self.assertEqual(report["next_action"]["action_id"], "create_git_remote")
        self.assertIn("Configure_Git_Remote.cmd", report["next_action"]["command"])
        self.assertIn("--remote-url <your-repo-url>", report["next_action"]["command"])
        self.assertNotIn("git remote add origin", report["next_action"]["command"])
        self.assertEqual(checks["local_final_gate"]["status"], "passed")
        self.assertEqual(checks["render_blueprint"]["status"], "passed")
        self.assertEqual(checks["git_remote"]["status"], "action_required")
        self.assertTrue(report["safety_scope"]["does_not_store_credentials"])
        self.assertTrue(report["safety_scope"]["no_clinical_production_approval"])

    def test_report_advances_to_render_cli_when_remote_exists_but_cli_is_missing(self):
        from cds_core.deployment_status import build_deployment_status_report

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)

        report = build_deployment_status_report(
            today=date(2026, 6, 26),
            evidence_path=evidence_path,
            command_runner=self.runner(
                git_remote_stdout="origin https://github.com/example/cds.git (fetch)",
                render_version_exit=1,
            ),
        )

        self.assertEqual(report["status"], "ready_for_render_cli_install")
        self.assertEqual(report["next_action"]["action_id"], "install_or_use_render_dashboard")
        self.assertIn("Render Dashboard", report["next_action"]["detail_en"])

    def test_report_reports_public_deploy_live_when_verified_evidence_exists(self):
        from cds_core.deployment_status import build_deployment_status_report

        self.create_staff_reviewer()
        tmp_dir, final_evidence_path = self.verified_evidence_path()
        public_tmp_dir, public_evidence_path = self.public_deploy_evidence_path()
        self.addCleanup(tmp_dir.cleanup)
        self.addCleanup(public_tmp_dir.cleanup)

        report = build_deployment_status_report(
            today=date(2026, 6, 28),
            evidence_path=final_evidence_path,
            deployment_evidence_path=public_evidence_path,
            command_runner=self.runner(
                git_remote_stdout="origin https://github.com/example/cds.git (fetch)",
                render_version_exit=1,
            ),
        )

        checks = {check["check_id"]: check for check in report["deployment_checks"]}
        self.assertEqual(report["status"], "public_deploy_live")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["next_action"]["action_id"], "monitor_public_deploy")
        self.assertEqual(report["external_blockers"], [])
        self.assertEqual(checks["public_deploy"]["status"], "passed")
        self.assertEqual(checks["public_deploy"]["value"], "https://clinical-differential-support.onrender.com")
        self.assertEqual(checks["render_cli"]["status"], "skipped")
        self.assertEqual(report["public_deployment"]["render_deploy_id"], "dep-test")

    def test_report_skips_render_cli_probe_when_public_deploy_is_verified(self):
        from cds_core.deployment_status import (
            CommandProbeResult,
            build_deployment_status_report,
        )
        from cds_core.git_publish_status import PUBLISH_STATUS_COMMAND

        self.create_staff_reviewer()
        tmp_dir, final_evidence_path = self.verified_evidence_path()
        public_tmp_dir, public_evidence_path = self.public_deploy_evidence_path()
        self.addCleanup(tmp_dir.cleanup)
        self.addCleanup(public_tmp_dir.cleanup)
        calls = []

        def runner(command, cwd):
            calls.append(command)
            if command == PUBLISH_STATUS_COMMAND:
                return CommandProbeResult(exit_code=0, stdout="", stderr="")
            if command == "git branch --show-current":
                return CommandProbeResult(exit_code=0, stdout="master\n", stderr="")
            if command == "git remote -v":
                return CommandProbeResult(
                    exit_code=0,
                    stdout="origin https://github.com/example/cds.git (fetch)",
                    stderr="",
                )
            if command.startswith("render "):
                raise AssertionError("Render CLI should not be probed after live public evidence.")
            raise AssertionError(f"Unexpected command: {command}")

        report = build_deployment_status_report(
            today=date(2026, 6, 28),
            evidence_path=final_evidence_path,
            deployment_evidence_path=public_evidence_path,
            command_runner=runner,
        )

        self.assertEqual(report["status"], "public_deploy_live")
        self.assertNotIn("render --version", calls)
        self.assertNotIn("render whoami -o json", calls)

    def test_public_deploy_live_does_not_require_local_sqlite_schema(self):
        from cds_core.deployment_status import build_deployment_status_report

        public_tmp_dir, public_evidence_path = self.public_deploy_evidence_path()
        self.addCleanup(public_tmp_dir.cleanup)
        missing_database = {
            "database_ready": False,
            "missing_tables": ["auth_user", "cds_core_chiefcomplaint"],
            "error": "",
        }

        with patch(
            "cds_core.local_launch._inspect_local_database",
            return_value=missing_database,
        ):
            report = build_deployment_status_report(
                today=date(2026, 6, 28),
                deployment_evidence_path=public_evidence_path,
                command_runner=self.runner(
                    git_remote_stdout="origin https://github.com/example/cds.git (fetch)",
                    render_version_exit=1,
                ),
            )

        checks = {check["check_id"]: check for check in report["deployment_checks"]}
        self.assertEqual(report["status"], "public_deploy_live")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["next_action"]["action_id"], "monitor_public_deploy")
        self.assertEqual(checks["public_deploy"]["status"], "passed")
        self.assertEqual(
            checks["local_final_gate"]["value"],
            "manual_setup_required",
        )

    def test_report_advances_to_dashboard_when_remote_cli_and_auth_exist(self):
        from cds_core.deployment_status import build_deployment_status_report

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)

        report = build_deployment_status_report(
            today=date(2026, 6, 26),
            evidence_path=evidence_path,
            command_runner=self.runner(
                git_remote_stdout="origin https://github.com/example/cds.git (fetch)",
                render_version_exit=0,
                render_whoami_exit=0,
            ),
        )

        self.assertEqual(report["status"], "ready_for_dashboard_deploy")
        self.assertEqual(report["next_action"]["action_id"], "open_render_blueprint")
        self.assertIn("https://dashboard.render.com/blueprint/new", report["next_action"]["url"])

    def test_formatter_outputs_next_step_and_no_credential_material(self):
        from cds_core.deployment_status import (
            build_deployment_status_report,
            format_deployment_status_report,
        )

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)

        report = build_deployment_status_report(
            today=date(2026, 6, 26),
            evidence_path=evidence_path,
            command_runner=self.runner(git_remote_stdout=""),
        )
        output = format_deployment_status_report(report)

        self.assertIn("Deployment Operations Center", output)
        self.assertIn("ready_for_remote_setup", output)
        self.assertIn("create_git_remote", output)
        self.assertIn("Deploy_Status.cmd", output)
        self.assertIn("Configure_Git_Remote.cmd", output)
        self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", output)
        self.assertNotIn("--password", output)

    def test_cli_outputs_json_and_text_without_credentials(self):
        from scripts.deployment_status import main

        self.create_staff_reviewer()
        tmp_dir, evidence_path = self.verified_evidence_path()
        self.addCleanup(tmp_dir.cleanup)
        deployment_evidence_path = Path(tmp_dir.name) / "missing-public-deploy.json"

        json_stdout = io.StringIO()
        with redirect_stdout(json_stdout):
            exit_code = main(
                [
                    "--json",
                    "--evidence-path",
                    str(evidence_path),
                    "--deployment-evidence-path",
                    str(deployment_evidence_path),
                ],
                command_runner=self.runner(git_remote_stdout=""),
            )

        payload = json.loads(json_stdout.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["status"], "ready_for_remote_setup")
        self.assertEqual(payload["next_action"]["action_id"], "create_git_remote")
        self.assertIn("Configure_Git_Remote.cmd", payload["next_action"]["command"])

        text_stdout = io.StringIO()
        with redirect_stdout(text_stdout):
            main(
                [
                    "--evidence-path",
                    str(evidence_path),
                    "--deployment-evidence-path",
                    str(deployment_evidence_path),
                ],
                command_runner=self.runner(git_remote_stdout=""),
            )
        text = text_stdout.getvalue()
        self.assertIn("Deployment Operations Center", text)
        self.assertNotIn("test-pass", text)

    def test_windows_entrypoint_wraps_deployment_status_without_credentials(self):
        script_path = Path(__file__).resolve().parents[2] / "Deploy_Status.cmd"

        body = script_path.read_text(encoding="utf-8")
        raw_body = script_path.read_bytes()

        self.assertEqual(raw_body.count(b"\r\n"), raw_body.count(b"\n"))
        self.assertIn("deployment_status.py", body)
        self.assertIn("CDS_DEPLOY_STATUS_NO_PAUSE", body)
        self.assertIn("Deployment status exit code", body)
        self.assertNotIn("createsuperuser", body)
        self.assertNotIn("DJANGO_SUPERUSER_PASSWORD", body)
        self.assertNotIn("--password", body)

    def test_public_deployment_status_page_renders_next_action(self):
        response = self.client.get(reverse("cds_core:deployment_status"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Deployment Operations Center")
        self.assertContains(response, "Deployment Checks")
        self.assertContains(response, "Next Deployment Action")
        self.assertContains(response, "Deploy_Status.cmd")
        self.assertContains(response, "refresh=1")
        self.assertContains(response, "process-local")
        self.assertNotContains(response, "DJANGO_SUPERUSER_PASSWORD")

    def test_deployment_status_reuses_cached_report_on_normal_navigation(self):
        url = reverse("cds_core:deployment_status")

        self.client.get(url)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            len(queries),
            80,
            "Deployment Status should reuse the cached status report on ordinary navigation.",
        )

    def test_docs_link_to_deployment_status_entrypoints(self):
        project_dir = Path(__file__).resolve().parents[2]
        for filename in ["README.md", "QUICK_START.zh.md", "DEPLOYMENT.md"]:
            with self.subTest(filename=filename):
                body = (project_dir / filename).read_text(encoding="utf-8-sig")
                self.assertIn("Deploy_Status.cmd", body)
                self.assertIn("/deployment/", body)
