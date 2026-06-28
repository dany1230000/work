from django.contrib.auth import get_user_model
from django.test import TestCase

from cds_core.models import ClinicalItem, ReviewRecord, Source


class ClinicalModelTests(TestCase):
    def test_draft_item_is_not_publishable_until_approved(self):
        source = Source.objects.create(
            publisher="NICE",
            title="Headaches in over 12s",
            url="https://www.nice.org.uk/guidance/cg150",
            version_label="CG150",
            access_date="2026-06-22",
        )
        item = ClinicalItem.objects.create(
            item_type=ClinicalItem.ItemType.RED_FLAG,
            title="Thunderclap headache",
            summary="Sudden severe headache should trigger urgent assessment.",
            title_zh="雷擊樣頭痛",
            title_en="Thunderclap headache",
            summary_zh="突然且快速達到最高強度的嚴重頭痛，應優先評估危險性次發原因。",
            summary_en="Sudden severe headache should trigger urgent assessment.",
            urgency=ClinicalItem.Urgency.EMERGENT,
            status=ClinicalItem.Status.DRAFT,
        )
        item.sources.add(source)

        self.assertFalse(item.is_publishable)

        reviewer = get_user_model().objects.create_user("reviewer")
        ReviewRecord.objects.create(
            clinical_item=item,
            reviewer=reviewer,
            decision=ReviewRecord.Decision.APPROVED,
            notes="Source and wording reviewed.",
        )
        item.refresh_from_db()

        self.assertEqual(item.status, ClinicalItem.Status.APPROVED)
        self.assertTrue(item.is_publishable)

    def test_clinical_item_stores_chinese_first_bilingual_content(self):
        item = ClinicalItem.objects.create(
            item_type=ClinicalItem.ItemType.RED_FLAG,
            title="Thunderclap headache",
            summary="Sudden severe headache should trigger urgent assessment.",
            title_zh="雷擊樣頭痛",
            title_en="Thunderclap headache",
            summary_zh="突然且快速達到最高強度的嚴重頭痛，應優先評估危險性次發原因。",
            summary_en="Sudden severe headache should trigger urgent assessment.",
            urgency=ClinicalItem.Urgency.EMERGENT,
            status=ClinicalItem.Status.DRAFT,
        )

        self.assertEqual(item.primary_title, "雷擊樣頭痛")
        self.assertEqual(item.secondary_title, "Thunderclap headache")
        self.assertIn("危險性次發原因", item.primary_summary)
        self.assertIn("Sudden severe headache", item.secondary_summary)
