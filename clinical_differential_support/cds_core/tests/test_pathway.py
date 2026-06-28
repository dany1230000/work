from django.test import TestCase
from django.urls import reverse

from cds_core.models import ChiefComplaint, ClinicalItem, Rule, Source
from cds_core.services import evaluate_headache_pathway


class HeadachePathwayTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def test_eight_seeded_scenarios_have_expected_primary_outputs(self):
        scenarios = [
            ({"onset_peak_minutes": 1, "severe_intensity": True}, "Thunderclap headache"),
            ({"fever": True, "meningism": True}, "Fever or meningism"),
            ({"neurologic_deficit": True}, "New neurologic deficit"),
            ({"altered_mental_status": True}, "Altered mental status"),
            ({"recent_trauma": True}, "Recent head trauma"),
            ({"immunocompromised": True}, "Immunocompromised status"),
            ({"malignancy_history": True}, "History of malignancy"),
            ({"age": 55, "jaw_claudication": True}, "Giant cell arteritis concern"),
        ]

        for findings, expected_title in scenarios:
            with self.subTest(expected_title=expected_title):
                result = evaluate_headache_pathway(findings)
        titles = [entry["item"].title for entry in result["outputs"]]
        self.assertIn(expected_title, titles)

    def test_view_shows_professional_safety_copy_and_sources(self):
        response = self.client.post(
            reverse("cds_core:headache"),
            {"onset_peak_minutes": "1", "severe_intensity": "on"},
        )

        self.assertContains(response, "For qualified medical professionals")
        self.assertContains(response, "Reference support only")
        self.assertContains(response, "限合格醫療專業人員使用")
        self.assertContains(response, "僅供參考")
        self.assertContains(response, "雷擊樣頭痛")
        self.assertContains(response, "Thunderclap headache")
        self.assertContains(response, "NICE")

    def test_view_renders_chinese_primary_and_english_secondary(self):
        response = self.client.post(
            reverse("cds_core:headache"),
            {"onset_peak_minutes": "1", "severe_intensity": "on"},
        )
        content = response.content.decode("utf-8")

        self.assertLess(content.index("雷擊樣頭痛"), content.index("Thunderclap headache"))
        self.assertContains(response, "為什麼顯示")
        self.assertContains(response, "Why shown")

    def test_red_flags_sort_before_routine_considerations(self):
        result = evaluate_headache_pathway(
            {
                "onset_peak_minutes": 1,
                "severe_intensity": True,
                "headache_days_per_month": 20,
                "acute_medication_days_per_month": 15,
            }
        )

        item_types = [entry["item"].item_type for entry in result["outputs"]]
        self.assertEqual(item_types[0], ClinicalItem.ItemType.RED_FLAG)

    def test_unsupported_case_returns_not_covered_message(self):
        result = evaluate_headache_pathway({"eye_color": "blue"})

        self.assertEqual(result["outputs"], [])
        self.assertIn("not covered in this MVP", result["empty_state"])


class SeedContentTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def test_seed_content_has_source_linked_published_items(self):
        self.assertTrue(ChiefComplaint.objects.filter(slug="headache").exists())
        self.assertGreaterEqual(Source.objects.count(), 3)
        self.assertGreaterEqual(Rule.objects.count(), 8)

        for item in ClinicalItem.objects.filter(status=ClinicalItem.Status.APPROVED):
            self.assertTrue(item.sources.exists(), item.title)
