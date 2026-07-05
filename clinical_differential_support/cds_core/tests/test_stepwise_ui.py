from django.test import TestCase
from django.urls import reverse


MOJIBAKE_MARKERS = [
    "\ufffd",
    "??",
    "\ue03d",
    "\ue434",
    "\ue87c",
    "\ue956",
    "\uefdc",
    "蝯",
    "甇",
    "銝",
    "撖",
    "靘",
    "雿",
    "瘝",
    "摰",
    "隢",
    "頛",
    "璆",
    "摮",
    "蝬",
    "餃",
]


class StepwiseUiTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def assert_no_mojibake(self, body: str) -> None:
        for marker in MOJIBAKE_MARKERS:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, body)

    def test_home_dashboard_shows_next_steps_and_all_workflows(self):
        response = self.client.get(reverse("cds_core:home"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="app-main"')
        self.assertContains(response, "data-fast-nav-root")
        self.assertContains(response, "data-fast-nav-progress")
        self.assertContains(response, "fetch(targetUrl")
        self.assertContains(response, 'data-fast-nav-prefetch="true"')
        self.assertContains(response, "fastNavCache")
        self.assertContains(response, "prefetchPrimaryNavigation")
        self.assertContains(response, "getCachedPage")
        self.assertContains(response, "sessionStorage")
        self.assertContains(response, "FAST_NAV_STORAGE_PREFIX")
        self.assertContains(response, "FAST_NAV_PROGRESS_DELAY_MS")
        self.assertContains(response, "FAST_NAV_PROGRESS_DELAY_MS = 480")
        self.assertContains(response, "工作台 / Dashboard")
        self.assertContains(response, "下一步 / Next Steps")
        self.assertContains(response, "頭痛 / Headache")
        self.assertContains(response, "胸痛 / Chest pain")
        self.assertContains(response, "腹痛 / Abdominal pain")
        self.assertContains(response, "呼吸困難 / Dyspnea")
        self.assertContains(response, "開始評估 / Start")
        self.assert_no_mojibake(body)

    def test_fast_navigation_prefetches_on_hover_and_focus(self):
        response = self.client.get(reverse("cds_core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-fast-nav-status="idle"')
        self.assertContains(response, "prefetchFastNavTarget")
        self.assertContains(response, "data-fast-nav-prefetched")
        self.assertContains(response, "pointerenter")
        self.assertContains(response, "focusin")
        self.assertContains(response, "Loading workspace")
        self.assertContains(response, "Workspace ready")
        self.assertContains(response, '"X-Fast-Nav": "1"')

    def test_fast_navigation_cached_pages_skip_progress_toast(self):
        response = self.client.get(reverse("cds_core:home"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "var cachedPage = getCachedPage(targetUrl);")
        cached_branch = body[
            body.index("if (cachedPage) {") : body.index("startProgress();")
        ]
        self.assertIn("replaceMainFromHtml(cachedPage.html, targetUrl, pushHistory);", cached_branch)
        self.assertNotIn("setFastNavStatus", cached_branch)

    def test_public_symptom_pages_show_a_three_step_workflow(self):
        route_expectations = [
            ("headache", "頭痛結構化問診", "Headache Intake", "達到最痛時間（分鐘） / Time to peak, minutes"),
            ("chest_pain", "胸痛結構化問診", "Chest Pain Intake", "持續胸痛 / Ongoing chest pain"),
            ("abdominal_pain", "腹痛結構化問診", "Abdominal Pain Intake", "腹痛持續時間（小時） / Pain duration, hours"),
            ("dyspnea", "呼吸困難結構化問診", "Dyspnea Intake", "急性呼吸困難 / Acute dyspnea"),
        ]

        for route_name, title_zh, title_en, field_label in route_expectations:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(f"cds_core:{route_name}"))
                body = response.content.decode("utf-8")

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, title_zh)
                self.assertContains(response, title_en)
                self.assertContains(response, "三步驟工作流程 / 3-Step Workflow")
                self.assertContains(response, "步驟 1/3")
                self.assertContains(response, "輸入結構化發現 / Enter structured findings")
                self.assertContains(response, "步驟 2/3")
                self.assertContains(response, "執行參考路徑 / Run the reference pathway")
                self.assertContains(response, "步驟 3/3")
                self.assertContains(response, "檢視下一步問題 / Review ask-next prompts")
                self.assertContains(response, "產生參考輸出 / Evaluate reference pathway")
                self.assertContains(response, field_label)
                self.assert_no_mojibake(body)

    def test_reviewer_login_shows_staff_access_steps(self):
        response = self.client.get(reverse("cds_core:review_login"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "審核者登入")
        self.assertContains(response, "Reviewer Login")
        self.assertContains(response, "三步驟工作流程 / 3-Step Workflow")
        self.assertContains(response, "步驟 1/3")
        self.assertContains(response, "輸入 staff 帳號 / Enter staff credentials")
        self.assertContains(response, "步驟 2/3")
        self.assertContains(response, "開啟審核佇列 / Open the reviewer queue")
        self.assertContains(response, "步驟 3/3")
        self.assertContains(response, "先處理來源缺口 / Handle source gaps first")
        self.assert_no_mojibake(body)

    def test_review_queue_shows_prioritized_review_steps(self):
        response = self.client.get(reverse("cds_core:review_queue"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "審核佇列")
        self.assertContains(response, "Reviewer Queue")
        self.assertContains(response, "審核工作流程 / Review Workflow")
        self.assertContains(response, "步驟 1/3")
        self.assertContains(response, "先處理來源缺口 / Resolve source gaps first")
        self.assertContains(response, "步驟 2/3")
        self.assertContains(response, "檢查到期審核 / Review due items")
        self.assertContains(response, "步驟 3/3")
        self.assertContains(response, "開啟項目並記錄決策 / Open the item and record a decision")
        self.assert_no_mojibake(body)
