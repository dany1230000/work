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

    def test_public_symptom_pages_show_a_three_step_workflow(self):
        route_expectations = [
            ("headache", "頭痛結構化問診", "Headache Intake"),
            ("chest_pain", "胸痛結構化問診", "Chest Pain Intake"),
            ("abdominal_pain", "腹痛結構化問診", "Abdominal Pain Intake"),
            ("dyspnea", "呼吸困難結構化問診", "Dyspnea Intake"),
        ]

        for route_name, title_zh, title_en in route_expectations:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(f"cds_core:{route_name}"))
                body = response.content.decode("utf-8")

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, title_zh)
                self.assertContains(response, title_en)
                self.assertContains(response, "操作步驟 / Workflow")
                self.assertContains(response, "步驟 1/3")
                self.assertContains(response, "輸入結構化發現")
                self.assertContains(response, "步驟 2/3")
                self.assertContains(response, "按下評估")
                self.assertContains(response, "步驟 3/3")
                self.assertContains(response, "查看下一步要問")
                self.assertNotIn("結構化 finding", body)
                self.assert_no_mojibake(body)

    def test_reviewer_login_shows_staff_access_steps(self):
        response = self.client.get(reverse("cds_core:review_login"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "審核者登入")
        self.assertContains(response, "Reviewer Login")
        self.assertContains(response, "操作步驟 / Workflow")
        self.assertContains(response, "步驟 1/3")
        self.assertContains(response, "輸入 staff 帳號")
        self.assertContains(response, "步驟 2/3")
        self.assertContains(response, "登入審核佇列")
        self.assertContains(response, "步驟 3/3")
        self.assertContains(response, "處理來源缺口")
        self.assert_no_mojibake(body)

    def test_review_queue_shows_prioritized_review_steps(self):
        response = self.client.get(reverse("cds_core:review_queue"))
        body = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "審核佇列")
        self.assertContains(response, "Reviewer Queue")
        self.assertContains(response, "審核流程 / Review Workflow")
        self.assertContains(response, "步驟 1/3")
        self.assertContains(response, "先處理來源缺口")
        self.assertContains(response, "步驟 2/3")
        self.assertContains(response, "處理到期審核")
        self.assertContains(response, "步驟 3/3")
        self.assertContains(response, "打開項目並記錄決策")
        self.assert_no_mojibake(body)
