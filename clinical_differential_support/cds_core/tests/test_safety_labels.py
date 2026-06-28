from django.test import TestCase
from django.urls import reverse


class SafetyLabelTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def test_clinician_pages_include_safety_scope(self):
        response = self.client.get(reverse("cds_core:headache"))

        self.assertContains(response, "限合格醫療專業人員使用")
        self.assertContains(response, "非診斷或治療醫囑")
        self.assertContains(response, "For qualified medical professionals")
        self.assertContains(response, "not a diagnosis or treatment order")

    def test_clinician_pages_avoid_unsafe_labels(self):
        response = self.client.post(
            reverse("cds_core:headache"),
            {"onset_peak_minutes": "1", "severe_intensity": "on"},
        )
        content = response.content.decode("utf-8").lower()

        forbidden = [
            "final diagnosis",
            "prescribe",
            "order medication",
            "patient instruction",
            "ai diagnosis",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, content)

    def test_unsupported_case_shows_mvp_boundary(self):
        response = self.client.post(reverse("cds_core:headache"), {"age": ""})

        self.assertContains(response, "not covered in this MVP")
