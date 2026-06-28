import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class DeploymentReadinessTests(SimpleTestCase):
    def run_settings_probe(self, env_overrides):
        env = os.environ.copy()
        for key in [
            "DATABASE_URL",
            "DJANGO_ALLOWED_HOSTS",
            "DJANGO_CSRF_TRUSTED_ORIGINS",
            "DJANGO_DB_SSL_REQUIRE",
            "DJANGO_DEBUG",
            "DJANGO_SECRET_KEY",
            "DJANGO_SECURE_SSL_REDIRECT",
            "RENDER",
            "RENDER_EXTERNAL_HOSTNAME",
            "SECRET_KEY",
        ]:
            env.pop(key, None)
        env.update(env_overrides)

        probe = """
import json
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinical_differential_support.settings")
from django.conf import settings
print(json.dumps({
    "allowed_hosts": list(settings.ALLOWED_HOSTS),
    "csrf_trusted_origins": list(getattr(settings, "CSRF_TRUSTED_ORIGINS", [])),
    "database_engine": settings.DATABASES["default"]["ENGINE"],
    "debug": settings.DEBUG,
    "middleware": list(settings.MIDDLEWARE),
    "secret_key": settings.SECRET_KEY,
    "secure_proxy_ssl_header": getattr(settings, "SECURE_PROXY_SSL_HEADER", None),
    "secure_ssl_redirect": getattr(settings, "SECURE_SSL_REDIRECT", None),
    "static_root": str(getattr(settings, "STATIC_ROOT", "")),
    "staticfiles_backend": settings.STORAGES["staticfiles"]["BACKEND"],
}))
"""
        return subprocess.run(
            [sys.executable, "-B", "-c", probe],
            cwd=settings.BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_production_settings_are_environment_driven(self):
        result = self.run_settings_probe(
            {
                "DATABASE_URL": "postgres://user:pass@localhost:5432/clinical_test",
                "DJANGO_ALLOWED_HOSTS": "clinical.example.com",
                "DJANGO_DEBUG": "0",
                "DJANGO_SECRET_KEY": "deploy-test-secret",
                "DJANGO_SECURE_SSL_REDIRECT": "1",
                "RENDER": "true",
                "RENDER_EXTERNAL_HOSTNAME": "clinical-render.onrender.com",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["debug"])
        self.assertEqual(payload["secret_key"], "deploy-test-secret")
        self.assertIn("clinical.example.com", payload["allowed_hosts"])
        self.assertIn("clinical-render.onrender.com", payload["allowed_hosts"])
        self.assertEqual(payload["database_engine"], "django.db.backends.postgresql")
        self.assertIn("whitenoise.middleware.WhiteNoiseMiddleware", payload["middleware"])
        self.assertTrue(payload["static_root"].endswith("staticfiles"))
        self.assertEqual(
            payload["staticfiles_backend"],
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
        )
        self.assertEqual(
            payload["secure_proxy_ssl_header"],
            ["HTTP_X_FORWARDED_PROTO", "https"],
        )
        self.assertTrue(payload["secure_ssl_redirect"])
        self.assertIn(
            "https://clinical-render.onrender.com",
            payload["csrf_trusted_origins"],
        )

    def test_production_mode_requires_external_secret(self):
        result = self.run_settings_probe({"DJANGO_DEBUG": "0"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_requirements_include_deployment_runtime_dependencies(self):
        requirements = (settings.BASE_DIR / "requirements.txt").read_text(encoding="utf-8")

        for dependency in [
            "dj-database-url",
            "gunicorn",
            "psycopg2-binary",
            "whitenoise[brotli]",
        ]:
            with self.subTest(dependency=dependency):
                self.assertIn(dependency, requirements)

    def test_render_blueprint_uses_managed_database_and_generated_secret(self):
        blueprint = settings.BASE_DIR.parent / "render.yaml"

        self.assertTrue(blueprint.exists())
        content = blueprint.read_text(encoding="utf-8")
        for expected in [
            "runtime: python",
            "buildCommand: bash ./clinical_differential_support/build.sh",
            "startCommand: cd clinical_differential_support && gunicorn clinical_differential_support.wsgi:application",
            "healthCheckPath: /health/",
            "fromDatabase:",
            "property: connectionString",
            "DJANGO_SECRET_KEY",
            "generateValue: true",
            "DJANGO_DEBUG",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, content)

        blocked_markers = ["local-mvp-not-for-production", "PASSWORD=", "--password"]
        for marker in blocked_markers:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, content)

    def test_build_script_prepares_static_database_and_fixtures_without_credentials(self):
        build_script = settings.BASE_DIR / "build.sh"

        self.assertTrue(build_script.exists())
        content = build_script.read_text(encoding="utf-8")
        for expected in [
            "pip install -r clinical_differential_support/requirements.txt",
            "collectstatic --no-input",
            "migrate --run-syncdb",
            "loaddata headache_mvp chest_pain_mvp abdominal_pain_mvp dyspnea_mvp",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, content)

        for blocked in ["createsuperuser", "DJANGO_SUPERUSER_PASSWORD", "--password"]:
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, content)

    def test_deployment_docs_explain_next_steps_without_claiming_public_launch(self):
        deployment_doc = settings.BASE_DIR / "DEPLOYMENT.md"
        readme = settings.BASE_DIR / "README.md"
        quick_start = settings.BASE_DIR / "QUICK_START.zh.md"

        self.assertTrue(deployment_doc.exists())
        deployment_content = deployment_doc.read_text(encoding="utf-8-sig")
        readme_content = readme.read_text(encoding="utf-8-sig")
        quick_start_content = quick_start.read_text(encoding="utf-8-sig")

        for expected in [
            "部署就緒",
            "Render Blueprint",
            "render.yaml",
            "DATABASE_URL",
            "DJANGO_SECRET_KEY",
            "Render Shell",
            "createsuperuser",
            "不是正式臨床上線核准",
            "No patient data",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, deployment_content)

        self.assertIn("DEPLOYMENT.md", readme_content)
        self.assertIn("DEPLOYMENT.md", quick_start_content)
        self.assertNotIn("已公開部署完成", deployment_content)
