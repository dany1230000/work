from django.contrib.auth import get_user_model
from django.test import TestCase

from cds_core.models import AuditEvent, ClinicalItem, ReviewRecord


class ReviewWorkflowTests(TestCase):
    def test_approve_review_record_publishes_item_and_records_audit(self):
        reviewer = get_user_model().objects.create_user("reviewer")
        item = ClinicalItem.objects.create(
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Migraine",
            summary="Consider migraine when compatible recurrent headache features exist.",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.IN_REVIEW,
        )

        ReviewRecord.objects.create(
            clinical_item=item,
            reviewer=reviewer,
            decision=ReviewRecord.Decision.APPROVED,
            notes="Approved for MVP.",
        )
        item.refresh_from_db()

        self.assertEqual(item.status, ClinicalItem.Status.APPROVED)
        self.assertTrue(
            AuditEvent.objects.filter(
                clinical_item=item, event_type=AuditEvent.EventType.APPROVED
            ).exists()
        )

    def test_only_approved_items_are_clinician_visible(self):
        ClinicalItem.objects.create(
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Draft item",
            summary="Should not be visible.",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.DRAFT,
        )
        ClinicalItem.objects.create(
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Retired item",
            summary="Should not be visible.",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.RETIRED,
        )
        approved = ClinicalItem.objects.create(
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Approved item",
            summary="Visible.",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.APPROVED,
        )

        self.assertEqual(list(ClinicalItem.objects.clinician_visible()), [approved])
