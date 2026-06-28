import csv
import io
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cds_core.models import ChiefComplaint, ClinicalItem, Source


def read_csv_response(response):
    return list(csv.DictReader(io.StringIO(response.content.decode("utf-8"))))


class GovernanceExportTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def assertReviewerLoginRedirect(self, response, expected_next):
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        self.assertEqual(parsed.path, reverse("cds_core:review_login"))
        self.assertEqual(parse_qs(parsed.query).get("next"), [expected_next])

    def staff_login(self):
        reviewer = get_user_model().objects.create_user(
            "export-reviewer", password="test-pass", is_staff=True
        )
        self.client.force_login(reviewer)
        return reviewer

    def test_unauthenticated_clinical_item_export_redirects_to_reviewer_login(self):
        export_path = reverse("cds_core:export_clinical_items_csv")

        response = self.client.get(export_path)

        self.assertReviewerLoginRedirect(response, export_path)

    def test_staff_can_export_clinical_items_csv(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_clinical_items_csv"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn(
            "clinical-items.csv",
            response["Content-Disposition"],
        )
        rows = read_csv_response(response)
        thunderclap = next(row for row in rows if row["title_en"] == "Thunderclap headache")
        self.assertEqual(thunderclap["status"], ClinicalItem.Status.APPROVED)
        self.assertEqual(thunderclap["source_count"], "2")
        self.assertEqual(thunderclap["source_publishers"], "ACR; NICE")
        self.assertIn("ACR Appropriateness Criteria", thunderclap["source_titles"])

    def test_staff_can_export_sources_csv(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:export_sources_csv"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("sources.csv", response["Content-Disposition"])
        rows = read_csv_response(response)
        acr = next(row for row in rows if row["publisher"] == "ACR")
        self.assertEqual(acr["linked_item_count"], "2")
        self.assertIn("Thunderclap headache", acr["linked_item_titles"])

    def test_clinical_item_export_sanitizes_formula_like_cells(self):
        self.staff_login()
        complaint = ChiefComplaint.objects.get(slug="headache")
        source = Source.objects.create(
            publisher="Internal QA",
            title="Formula guard source",
            url="https://example.org/formula-guard",
            access_date="2026-06-24",
            version_label="QA",
        )
        item = ClinicalItem.objects.create(
            chief_complaint=complaint,
            item_type=ClinicalItem.ItemType.DIFFERENTIAL,
            title="=unsafe",
            title_zh="=不安全",
            title_en="=unsafe",
            summary="+unsafe summary",
            summary_zh="+不安全摘要",
            summary_en="+unsafe summary",
            urgency=ClinicalItem.Urgency.ROUTINE,
            status=ClinicalItem.Status.DRAFT,
        )
        item.sources.add(source)

        response = self.client.get(reverse("cds_core:export_clinical_items_csv"))

        rows = read_csv_response(response)
        exported = next(row for row in rows if row["id"] == str(item.pk))
        self.assertEqual(exported["title_zh"], "'=不安全")
        self.assertEqual(exported["title_en"], "'=unsafe")
        self.assertEqual(exported["summary_en"], "'+unsafe summary")

    def test_staff_dashboard_links_to_governance_exports(self):
        self.staff_login()

        response = self.client.get(reverse("cds_core:review_dashboard"))

        self.assertContains(response, "Governance exports")
        self.assertContains(response, "Clinical item CSV")
        self.assertContains(response, "Source CSV")
        self.assertContains(response, reverse("cds_core:export_clinical_items_csv"))
        self.assertContains(response, reverse("cds_core:export_sources_csv"))
