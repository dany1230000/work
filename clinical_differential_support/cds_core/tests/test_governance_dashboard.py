from datetime import date, timedelta
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.models import AuditEvent, ChiefComplaint, ClinicalItem, ReviewRecord, Source


class GovernanceDashboardTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        location = response["Location"]
        parsed = urlparse(location)
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def test_governance_service_reports_fixture_baseline(self):
        from cds_core.governance import build_review_dashboard

        dashboard = build_review_dashboard(today=date(2026, 6, 22))

        self.assertEqual(dashboard["total_items"], 13)
        self.assertEqual(dashboard["status_counts"]["approved"], 13)
        self.assertEqual(dashboard["source_gap_items"], [])
        self.assertEqual(dashboard["review_due_items"], [])
        self.assertEqual(len(dashboard["clinical_items"]), 13)
        self.assertGreaterEqual(len(dashboard["case_rows"]), 8)
        self.assertTrue(all(row["all_matched"] for row in dashboard["case_rows"]))

    def test_governance_service_flags_review_due_and_source_gap_items(self):
        from cds_core.governance import build_review_dashboard

        complaint = ChiefComplaint.objects.get(slug="headache")
        item = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Needs review source gap",
            title_zh="需要審核且缺少來源",
            title_en="Needs review source gap",
            summary="Created only for the governance dashboard test.",
            summary_zh="僅供治理儀表板測試使用。",
            summary_en="Created only for the governance dashboard test.",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.IN_REVIEW,
            last_reviewed_at=date(2026, 1, 1),
            review_due_at=date(2026, 6, 1),
        )

        dashboard = build_review_dashboard(today=date(2026, 6, 22))

        self.assertIn(item, dashboard["review_due_items"])
        self.assertIn(item, dashboard["source_gap_items"])
        self.assertEqual(dashboard["status_counts"]["in_review"], 1)

    def test_review_dashboard_page_is_chinese_first_with_english_secondary(self):
        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "臨床內容治理")
        self.assertContains(response, "Clinical Governance")
        self.assertContains(response, "來源覆蓋")
        self.assertContains(response, "Source coverage")
        self.assertContains(response, "案例驗證")
        self.assertContains(response, "Case validation")
        self.assertContains(response, "13")
        self.assertContains(response, "8")

    def test_review_dashboard_links_to_source_library(self):
        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertContains(response, "來源庫")
        self.assertContains(response, "Source library")
        self.assertContains(response, reverse("cds_core:source_index"))

    def test_review_dashboard_links_to_clinical_item_detail(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")

        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertContains(response, "臨床項目清單")
        self.assertContains(response, "Clinical item inventory")
        self.assertContains(
            response,
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk}),
        )
        self.assertContains(response, item.primary_title)
        self.assertContains(response, item.secondary_title)

    def test_staff_review_dashboard_links_to_new_clinical_item_form(self):
        reviewer = get_user_model().objects.create_user(
            "draft-link-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertContains(response, "新增臨床項目")
        self.assertContains(response, "New clinical item")
        self.assertContains(response, reverse("cds_core:review_item_create"))

    def test_review_item_detail_selector_includes_sources_rules_and_audit(self):
        from cds_core.governance import build_review_item_detail

        item = ClinicalItem.objects.get(title="Thunderclap headache")

        detail = build_review_item_detail(item)

        self.assertEqual(detail["item"], item)
        self.assertEqual([source.publisher for source in detail["sources"]], ["ACR", "NICE"])
        self.assertEqual([rule.slug for rule in detail["rules"]], ["rf_thunderclap"])
        self.assertEqual(detail["audit_events"], [])

    def test_review_item_detail_page_is_chinese_first_with_review_metadata(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")

        response = self.client.get(
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "臨床項目審核")
        self.assertContains(response, "Clinical Item Review")
        self.assertContains(response, item.primary_title)
        self.assertContains(response, "Thunderclap headache")
        self.assertContains(response, "來源 / Sources")
        self.assertContains(response, "ACR")
        self.assertContains(response, "NICE")
        self.assertContains(response, "規則觸發 / Rule triggers")
        self.assertContains(response, "rf_thunderclap")
        self.assertContains(response, "最後審核 / Last reviewed")
        self.assertContains(response, "下次審核 / Review due")

    def test_staff_review_item_detail_links_to_edit_form(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        reviewer = get_user_model().objects.create_user(
            "edit-link-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk})
        )

        self.assertContains(response, "編輯草稿")
        self.assertContains(response, "Edit draft")
        self.assertContains(
            response,
            reverse("cds_core:review_item_edit", kwargs={"pk": item.pk}),
        )

    def test_staff_review_item_detail_shows_decision_form(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        reviewer = get_user_model().objects.create_user(
            "staff-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk})
        )

        self.assertContains(response, "審核決策")
        self.assertContains(response, "Review decision")
        self.assertContains(response, "送出審核決策")
        self.assertContains(
            response,
            reverse("cds_core:review_item_decision", kwargs={"pk": item.pk}),
        )

    def test_unauthenticated_review_decision_post_is_blocked(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        decision_path = reverse("cds_core:review_item_decision", kwargs={"pk": item.pk})

        response = self.client.post(
            decision_path,
            {
                "decision": ReviewRecord.Decision.RETIRED,
                "notes": "This should not be accepted.",
            },
        )

        self.assertReviewerLoginRedirect(response, decision_path)
        self.assertFalse(ReviewRecord.objects.filter(clinical_item=item).exists())

    def test_staff_review_decision_creates_review_record_and_audit_event(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        item.status = ClinicalItem.Status.IN_REVIEW
        item.last_reviewed_at = None
        item.save(update_fields=["status", "last_reviewed_at"])
        reviewer = get_user_model().objects.create_user(
            "approver", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:review_item_decision", kwargs={"pk": item.pk}),
            {
                "decision": ReviewRecord.Decision.APPROVED,
                "notes": "Source links and rule behavior reviewed for MVP governance.",
            },
        )

        item.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk}),
        )
        self.assertEqual(item.status, ClinicalItem.Status.APPROVED)
        self.assertIsNotNone(item.last_reviewed_at)
        self.assertTrue(
            ReviewRecord.objects.filter(
                clinical_item=item,
                reviewer=reviewer,
                decision=ReviewRecord.Decision.APPROVED,
            ).exists()
        )
        self.assertTrue(
            AuditEvent.objects.filter(
                clinical_item=item,
                actor=reviewer,
                event_type=AuditEvent.EventType.APPROVED,
            ).exists()
        )

    def test_staff_review_decision_rejects_invalid_decision_without_audit(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        reviewer = get_user_model().objects.create_user(
            "invalid-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:review_item_decision", kwargs={"pk": item.pk}),
            {
                "decision": "publish_live",
                "notes": "This decision value is not part of governance policy.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")
        self.assertFalse(ReviewRecord.objects.filter(clinical_item=item).exists())
        self.assertFalse(AuditEvent.objects.filter(clinical_item=item).exists())

    def test_staff_review_success_message_and_audit_note_render_after_redirect(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        reviewer = get_user_model().objects.create_user(
            "message-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        notes = "Reviewed source links, rule trigger, and bilingual summary."

        response = self.client.post(
            reverse("cds_core:review_item_decision", kwargs={"pk": item.pk}),
            {
                "decision": ReviewRecord.Decision.CHANGES_REQUESTED,
                "notes": notes,
            },
            follow=True,
        )

        item.refresh_from_db()
        self.assertEqual(item.status, ClinicalItem.Status.DRAFT)
        self.assertContains(response, "審核決策已記錄")
        self.assertContains(response, "Review decision recorded")
        self.assertContains(response, notes)
        self.assertContains(response, "Changes requested")

    def test_approved_review_decision_sets_next_review_due_date(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        item.status = ClinicalItem.Status.IN_REVIEW
        item.review_due_at = None
        item.save(update_fields=["status", "review_due_at"])
        reviewer = get_user_model().objects.create_user(
            "due-date-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        self.client.post(
            reverse("cds_core:review_item_decision", kwargs={"pk": item.pk}),
            {
                "decision": ReviewRecord.Decision.APPROVED,
                "notes": "Approved after source and rule validation.",
            },
        )

        item.refresh_from_db()
        self.assertEqual(item.review_due_at, item.last_reviewed_at + timedelta(days=180))

    def test_unauthenticated_clinical_item_create_is_blocked(self):
        create_path = reverse("cds_core:review_item_create")
        response = self.client.get(create_path)

        self.assertReviewerLoginRedirect(response, create_path)

    def test_staff_can_create_draft_clinical_item(self):
        complaint = ChiefComplaint.objects.get(slug="headache")
        reviewer = get_user_model().objects.create_user(
            "draft-creator", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:review_item_create"),
            {
                "chief_complaint": complaint.pk,
                "item_type": ClinicalItem.ItemType.DIFFERENTIAL,
                "title": "Draft secondary headache pattern",
                "title_zh": "草稿次發性頭痛型態",
                "title_en": "Draft secondary headache pattern",
                "summary": "Draft summary for reviewer workflow.",
                "summary_zh": "供審核流程測試的草稿摘要。",
                "summary_en": "Draft summary for reviewer workflow.",
                "urgency": ClinicalItem.Urgency.URGENT,
                "status": ClinicalItem.Status.IN_REVIEW,
                "review_due_at": "2026-12-22",
                "missing_questions_text": "pregnancy\nblood pressure",
                "supporting_findings_text": "new onset",
                "opposing_findings_text": "",
            },
            follow=True,
        )

        item = ClinicalItem.objects.get(title="Draft secondary headache pattern")
        self.assertEqual(item.status, ClinicalItem.Status.IN_REVIEW)
        self.assertEqual(item.missing_questions, ["pregnancy", "blood pressure"])
        self.assertEqual(item.supporting_findings, ["new onset"])
        self.assertRedirects(
            response,
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk}),
        )
        self.assertContains(response, "草稿已建立")
        self.assertContains(response, "Draft clinical item created")

    def test_staff_can_edit_draft_clinical_item(self):
        complaint = ChiefComplaint.objects.get(slug="headache")
        item = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Editable draft",
            title_zh="可編輯草稿",
            title_en="Editable draft",
            summary="Original draft summary.",
            summary_zh="原始草稿摘要。",
            summary_en="Original draft summary.",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.DRAFT,
        )
        reviewer = get_user_model().objects.create_user(
            "draft-editor", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:review_item_edit", kwargs={"pk": item.pk}),
            {
                "chief_complaint": complaint.pk,
                "item_type": ClinicalItem.ItemType.DIFFERENTIAL,
                "title": "Edited draft",
                "title_zh": "已編輯草稿",
                "title_en": "Edited draft",
                "summary": "Edited draft summary.",
                "summary_zh": "已編輯草稿摘要。",
                "summary_en": "Edited draft summary.",
                "urgency": ClinicalItem.Urgency.SOON,
                "status": ClinicalItem.Status.DRAFT,
                "review_due_at": "2026-12-31",
                "missing_questions_text": "new neurologic symptoms",
                "supporting_findings_text": "",
                "opposing_findings_text": "normal neurologic exam",
            },
            follow=True,
        )

        item.refresh_from_db()
        self.assertEqual(item.title, "Edited draft")
        self.assertEqual(item.primary_title, "已編輯草稿")
        self.assertEqual(item.urgency, ClinicalItem.Urgency.SOON)
        self.assertEqual(item.missing_questions, ["new neurologic symptoms"])
        self.assertEqual(item.opposing_findings, ["normal neurologic exam"])
        self.assertRedirects(
            response,
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk}),
        )
        self.assertContains(response, "草稿已更新")
        self.assertContains(response, "Draft clinical item updated")

    def test_source_library_lists_sources_and_item_coverage(self):
        source = Source.objects.get(publisher="ACR")

        response = self.client.get(reverse("cds_core:source_index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "來源庫")
        self.assertContains(response, "Source library")
        self.assertContains(response, "ACR")
        self.assertContains(response, "NICE")
        self.assertContains(response, "Clinical items")
        self.assertContains(response, reverse("cds_core:source_detail", kwargs={"pk": source.pk}))

    def test_source_detail_lists_linked_clinical_items(self):
        source = Source.objects.get(publisher="ACR")

        response = self.client.get(reverse("cds_core:source_detail", kwargs={"pk": source.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "來源詳情")
        self.assertContains(response, "Source detail")
        self.assertContains(response, "ACR")
        self.assertContains(response, "ACR Appropriateness Criteria")
        self.assertContains(response, "Thunderclap headache")
        self.assertContains(response, "Recent head trauma")

    def test_unauthenticated_source_create_is_blocked(self):
        source_create_path = reverse("cds_core:source_create")
        response = self.client.get(source_create_path)

        self.assertReviewerLoginRedirect(response, source_create_path)

    def test_staff_source_library_links_to_new_source_form(self):
        reviewer = get_user_model().objects.create_user(
            "source-link-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.get(reverse("cds_core:source_index"))

        self.assertContains(response, "New source")
        self.assertContains(response, reverse("cds_core:source_create"))

    def test_staff_can_create_source(self):
        reviewer = get_user_model().objects.create_user(
            "source-creator", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:source_create"),
            {
                "publisher": "ICHD",
                "title": "International Classification of Headache Disorders",
                "url": "https://ichd-3.org/",
                "publication_date": "2018-01-01",
                "access_date": "2026-06-23",
                "version_label": "ICHD-3",
            },
            follow=True,
        )

        source = Source.objects.get(publisher="ICHD")
        self.assertRedirects(
            response, reverse("cds_core:source_detail", kwargs={"pk": source.pk})
        )
        self.assertContains(response, "Source created")
        self.assertContains(response, "International Classification of Headache Disorders")

    def test_staff_source_detail_links_to_edit_form(self):
        source = Source.objects.get(publisher="ACR")
        reviewer = get_user_model().objects.create_user(
            "source-edit-link-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.get(reverse("cds_core:source_detail", kwargs={"pk": source.pk}))

        self.assertContains(response, "Edit source")
        self.assertContains(response, reverse("cds_core:source_edit", kwargs={"pk": source.pk}))

    def test_staff_can_edit_source(self):
        source = Source.objects.get(publisher="ACR")
        reviewer = get_user_model().objects.create_user(
            "source-editor", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:source_edit", kwargs={"pk": source.pk}),
            {
                "publisher": "ACR",
                "title": "Updated ACR Appropriateness Criteria",
                "url": source.url,
                "publication_date": "2022-01-01",
                "access_date": "2026-06-23",
                "version_label": "Updated evidence review",
            },
            follow=True,
        )

        source.refresh_from_db()
        self.assertEqual(source.title, "Updated ACR Appropriateness Criteria")
        self.assertEqual(source.version_label, "Updated evidence review")
        self.assertContains(response, "Source updated")
        self.assertContains(response, "Updated ACR Appropriateness Criteria")

    def test_unauthenticated_item_source_update_is_blocked(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        original_source_ids = set(item.sources.values_list("pk", flat=True))
        source_link_path = reverse("cds_core:review_item_sources", kwargs={"pk": item.pk})

        response = self.client.post(
            source_link_path,
            {"sources": []},
        )

        item.refresh_from_db()
        self.assertReviewerLoginRedirect(response, source_link_path)
        self.assertEqual(set(item.sources.values_list("pk", flat=True)), original_source_ids)

    def test_review_login_page_is_chinese_first_with_english_secondary(self):
        response = self.client.get(reverse("cds_core:review_login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "審核者登入")
        self.assertContains(response, "Reviewer Login")
        self.assertContains(response, "Staff reviewer access")
        self.assertContains(response, "Reference support only")

    def test_staff_can_login_through_reviewer_login_and_continue_to_source_form(self):
        reviewer = get_user_model().objects.create_user(
            "login-reviewer", password="test-pass", is_staff=True
        )
        source_create_path = reverse("cds_core:source_create")

        response = self.client.post(
            reverse("cds_core:review_login"),
            {
                "username": reviewer.username,
                "password": "test-pass",
                "next": source_create_path,
            },
            follow=True,
        )

        self.assertRedirects(response, source_create_path)
        self.assertContains(response, "New source")

    def test_non_staff_authenticated_user_is_blocked_from_staff_route(self):
        non_staff = get_user_model().objects.create_user(
            "viewer-only", password="test-pass", is_staff=False
        )
        self.client.force_login(non_staff)
        source_create_path = reverse("cds_core:source_create")

        response = self.client.get(source_create_path)

        self.assertReviewerLoginRedirect(response, source_create_path)

    def test_staff_review_item_detail_shows_source_link_form(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        reviewer = get_user_model().objects.create_user(
            "source-form-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk})
        )

        self.assertContains(response, "Manage source links")
        self.assertContains(response, reverse("cds_core:review_item_sources", kwargs={"pk": item.pk}))

    def test_staff_can_update_item_source_links_and_audit_event(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        source = Source.objects.create(
            publisher="Internal QA",
            title="Reviewed internal headache evidence packet",
            url="https://example.org/internal-headache-evidence",
            access_date=date(2026, 6, 23),
            version_label="QA-2026-06",
        )
        reviewer = get_user_model().objects.create_user(
            "source-link-editor", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:review_item_sources", kwargs={"pk": item.pk}),
            {"sources": [source.pk]},
            follow=True,
        )

        item.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("cds_core:review_item_detail", kwargs={"pk": item.pk}),
        )
        self.assertEqual(list(item.sources.values_list("publisher", flat=True)), ["Internal QA"])
        self.assertContains(response, "Source links updated")
        self.assertTrue(
            AuditEvent.objects.filter(
                clinical_item=item,
                actor=reviewer,
                event_type=AuditEvent.EventType.SOURCES_UPDATED,
                notes__contains="Internal QA",
            ).exists()
        )

    def test_review_queue_selector_groups_and_filters_items(self):
        from cds_core.governance import build_review_queue

        complaint = ChiefComplaint.objects.get(slug="headache")
        source = Source.objects.get(publisher="NICE")
        draft_gap = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Draft queue source gap",
            title_zh="佇列草稿來源缺口",
            title_en="Draft queue source gap",
            summary="Queue test draft without a linked source.",
            summary_zh="佇列測試用草稿，尚未連結來源。",
            summary_en="Queue test draft without a linked source.",
            urgency=ClinicalItem.Urgency.SOON,
            status=ClinicalItem.Status.DRAFT,
        )
        due_item = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.WORKUP,
            title="Urgent queue review due",
            title_zh="佇列急件到期審核",
            title_en="Urgent queue review due",
            summary="Queue test item due for review.",
            summary_zh="佇列測試用到期審核項目。",
            summary_en="Queue test item due for review.",
            urgency=ClinicalItem.Urgency.URGENT,
            status=ClinicalItem.Status.IN_REVIEW,
            review_due_at=date(2026, 6, 1),
        )
        due_item.sources.add(source)

        queue = build_review_queue(today=date(2026, 6, 23))

        self.assertIn(draft_gap, queue["source_gap_items"])
        self.assertIn(draft_gap, queue["draft_items"])
        self.assertIn(due_item, queue["review_due_items"])
        self.assertIn(due_item, queue["in_review_items"])

        draft_queue = build_review_queue(
            filters={"status": ClinicalItem.Status.DRAFT},
            today=date(2026, 6, 23),
        )
        self.assertEqual(list(draft_queue["results"]), [draft_gap])

        urgent_search_queue = build_review_queue(
            filters={"urgency": ClinicalItem.Urgency.URGENT, "q": "queue review"},
            today=date(2026, 6, 23),
        )
        self.assertEqual(list(urgent_search_queue["results"]), [due_item])

    def test_review_dashboard_links_to_reviewer_queue(self):
        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertContains(response, "Reviewer Queue")
        self.assertContains(response, reverse("cds_core:review_queue"))

    def test_review_queue_page_lists_prioritized_work(self):
        complaint = ChiefComplaint.objects.get(slug="headache")
        ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Queue source gap item",
            title_zh="佇列來源缺口項目",
            title_en="Queue source gap item",
            summary="Queue test source gap.",
            summary_zh="佇列測試來源缺口。",
            summary_en="Queue test source gap.",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.DRAFT,
        )
        due_item = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.WORKUP,
            title="Queue due review item",
            title_zh="佇列到期審核項目",
            title_en="Queue due review item",
            summary="Queue test due review.",
            summary_zh="佇列測試到期審核。",
            summary_en="Queue test due review.",
            urgency=ClinicalItem.Urgency.URGENT,
            status=ClinicalItem.Status.IN_REVIEW,
            review_due_at=date(2026, 6, 1),
        )

        response = self.client.get(reverse("cds_core:review_queue"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "審核佇列")
        self.assertContains(response, "Reviewer Queue")
        self.assertContains(response, "Source gaps")
        self.assertContains(response, "Review due")
        self.assertContains(response, "Queue source gap item")
        self.assertContains(response, "Queue due review item")
        self.assertContains(
            response,
            reverse("cds_core:review_item_detail", kwargs={"pk": due_item.pk}),
        )

    def test_review_queue_filters_by_status_urgency_and_search(self):
        complaint = ChiefComplaint.objects.get(slug="headache")
        draft_item = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="Filtered draft queue item",
            title_zh="篩選草稿佇列項目",
            title_en="Filtered draft queue item",
            summary="Queue filter test draft.",
            summary_zh="佇列篩選測試草稿。",
            summary_en="Queue filter test draft.",
            urgency=ClinicalItem.Urgency.SOON,
            status=ClinicalItem.Status.DRAFT,
        )
        ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.WORKUP,
            title="Filtered urgent queue item",
            title_zh="篩選急件佇列項目",
            title_en="Filtered urgent queue item",
            summary="Queue filter test urgent item.",
            summary_zh="佇列篩選測試急件。",
            summary_en="Queue filter test urgent item.",
            urgency=ClinicalItem.Urgency.URGENT,
            status=ClinicalItem.Status.IN_REVIEW,
        )

        response = self.client.get(
            reverse("cds_core:review_queue"),
            {
                "status": ClinicalItem.Status.DRAFT,
                "urgency": ClinicalItem.Urgency.SOON,
                "q": "Filtered draft",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Filtered draft queue item")
        self.assertContains(response, reverse("cds_core:review_item_detail", kwargs={"pk": draft_item.pk}))
        self.assertNotContains(response, "Filtered urgent queue item")

    def test_review_queue_search_matches_source_publisher(self):
        response = self.client.get(reverse("cds_core:review_queue"), {"q": "ACR"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thunderclap headache")
        self.assertContains(response, "Recent head trauma")

    def test_review_queue_tracks_changes_requested_items(self):
        from cds_core.governance import build_review_queue

        item = ClinicalItem.objects.get(title="Thunderclap headache")
        reviewer = get_user_model().objects.create_user(
            "changes-request-reviewer", password="test-pass", is_staff=True
        )
        notes = "Please clarify the escalation wording before approval."
        ReviewRecord.objects.create(
            clinical_item=item,
            reviewer=reviewer,
            decision=ReviewRecord.Decision.CHANGES_REQUESTED,
            notes=notes,
        )

        queue = build_review_queue(today=date(2026, 6, 23))
        response = self.client.get(reverse("cds_core:review_queue"))

        self.assertIn(item, queue["changes_requested_items"])
        self.assertContains(response, "Changes requested")
        self.assertContains(response, "Thunderclap headache")
        self.assertContains(response, notes)

    def test_review_queue_shows_recent_reviewer_notes(self):
        from cds_core.governance import build_review_queue

        item = ClinicalItem.objects.get(title="Recent head trauma")
        reviewer = get_user_model().objects.create_user(
            "note-reviewer", password="test-pass", is_staff=True
        )
        notes = "Reviewer note queue should surface this source-review comment."
        record = ReviewRecord.objects.create(
            clinical_item=item,
            reviewer=reviewer,
            decision=ReviewRecord.Decision.CHANGES_REQUESTED,
            notes=notes,
        )

        queue = build_review_queue(today=date(2026, 6, 23))
        response = self.client.get(reverse("cds_core:review_queue"))

        self.assertEqual(queue["recent_review_records"][0], record)
        self.assertContains(response, "Reviewer notes")
        self.assertContains(response, "note-reviewer")
        self.assertContains(response, notes)

    def test_staff_editing_approved_item_resubmits_it_for_review(self):
        item = ClinicalItem.objects.get(title="Thunderclap headache")
        reviewer = get_user_model().objects.create_user(
            "approved-editor", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("cds_core:review_item_edit", kwargs={"pk": item.pk}),
            {
                "chief_complaint": item.chief_complaint.pk,
                "item_type": item.item_type,
                "title": item.title,
                "title_zh": item.title_zh,
                "title_en": item.title_en,
                "summary": item.summary + " Updated by content governance.",
                "summary_zh": item.summary_zh,
                "summary_en": item.summary_en + " Updated by content governance.",
                "urgency": item.urgency,
                "status": ClinicalItem.Status.DRAFT,
                "review_due_at": item.review_due_at.isoformat(),
                "missing_questions_text": "\n".join(item.missing_questions),
                "supporting_findings_text": "\n".join(item.supporting_findings),
                "opposing_findings_text": "\n".join(item.opposing_findings),
            },
            follow=True,
        )

        item.refresh_from_db()
        self.assertEqual(item.status, ClinicalItem.Status.IN_REVIEW)
        self.assertContains(response, "returned to review")
        self.assertTrue(
            AuditEvent.objects.filter(
                clinical_item=item,
                actor=reviewer,
                event_type=AuditEvent.EventType.SUBMITTED,
                notes__contains="edited after approval",
            ).exists()
        )
