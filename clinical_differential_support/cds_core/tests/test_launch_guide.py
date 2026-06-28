from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse


class LaunchGuidePageTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def setUp(self):
        cache.clear()

    def test_public_launch_guide_renders_numbered_steps_and_current_action(self):
        response = self.client.get(reverse("cds_core:launch_guide"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "啟動控制台 / Local Control Panel")
        self.assertContains(response, "環境檢查 / Environment Checks")
        self.assertContains(response, "手動阻擋項 / Manual Blockers")
        self.assertContains(response, "複製命令 / Copy Command")
        self.assertContains(response, "密碼保持手動輸入 / Passwords stay manual")
        self.assertContains(response, "驗證證據 / Verification Evidence")
        self.assertContains(response, "本機設定助理 / Local Setup Assistant")
        self.assertContains(response, "Next_Step.cmd")
        self.assertContains(response, "local_setup_assistant.py")
        self.assertContains(response, "最終專案閘門 / Final Project Gate")
        self.assertContains(response, "Final_Check.cmd")
        self.assertContains(response, "/completion/")
        self.assertContains(response, "Deployment Operations Center")
        self.assertContains(response, "Deploy_Status.cmd")
        self.assertContains(response, "/deployment/")
        self.assertContains(response, "Create_Staff_Reviewer.cmd")
        self.assertContains(response, "逐步啟動指南")
        self.assertContains(response, "步驟 1/7")
        self.assertContains(response, "Initialize the local database")
        self.assertContains(response, "Create a local staff reviewer account")
        self.assertContains(response, "現在要做 / Do this now")
        self.assertContains(response, "Final Verification Gate")
        self.assertContains(response, "Reviewer Login")
        self.assertContains(response, "refresh=1")
        self.assertNotIn("嚙", body)

    def test_launch_guide_reuses_cached_report_on_normal_navigation(self):
        url = reverse("cds_core:launch_guide")

        self.client.get(url)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            len(queries),
            80,
            "Launch Guide should reuse the cached status report on ordinary navigation.",
        )

    def test_launch_guide_is_linked_from_shared_navigation(self):
        response = self.client.get(reverse("cds_core:launch_guide"))

        self.assertContains(response, "啟動導覽 / Launch Guide")
        self.assertContains(response, reverse("cds_core:launch_guide"))
        self.assertContains(response, "Deployment")
        self.assertContains(response, reverse("cds_core:deployment_status"))
