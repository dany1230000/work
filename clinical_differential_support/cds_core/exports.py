import csv
import io
from collections.abc import Iterable
from datetime import date, datetime

from django.db.models import Count
from django.http import HttpResponse

from .models import ClinicalItem, Source

DANGEROUS_CSV_PREFIXES = ("=", "+", "-", "@")

CLINICAL_ITEM_EXPORT_HEADERS = [
    "id",
    "chief_complaint",
    "item_type",
    "urgency",
    "status",
    "title_zh",
    "title_en",
    "summary_zh",
    "summary_en",
    "version_label",
    "last_reviewed_at",
    "review_due_at",
    "source_count",
    "source_publishers",
    "source_titles",
]

SOURCE_EXPORT_HEADERS = [
    "id",
    "publisher",
    "title",
    "url",
    "publication_date",
    "access_date",
    "version_label",
    "linked_item_count",
    "linked_item_titles",
]


def safe_csv_value(value):
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (list, tuple, set)):
        text = "; ".join(str(entry) for entry in value)
    else:
        text = str(value)
    if text.startswith(DANGEROUS_CSV_PREFIXES):
        return f"'{text}"
    return text


def joined(values: Iterable[str]) -> str:
    return "; ".join(value for value in values if value)


def build_csv_text(headers, rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow({header: safe_csv_value(row.get(header, "")) for header in headers})
    return output.getvalue()


def build_clinical_item_export_rows():
    items = (
        ClinicalItem.objects.select_related("chief_complaint")
        .prefetch_related("sources")
        .order_by("item_type", "urgency", "title")
    )
    rows = []
    for item in items:
        sources = list(item.sources.all())
        rows.append(
            {
                "id": item.pk,
                "chief_complaint": item.chief_complaint.slug if item.chief_complaint else "",
                "item_type": item.item_type,
                "urgency": item.urgency,
                "status": item.status,
                "title_zh": item.title_zh,
                "title_en": item.title_en,
                "summary_zh": item.summary_zh,
                "summary_en": item.summary_en,
                "version_label": item.version_label,
                "last_reviewed_at": item.last_reviewed_at,
                "review_due_at": item.review_due_at,
                "source_count": len(sources),
                "source_publishers": joined(source.publisher for source in sources),
                "source_titles": joined(source.title for source in sources),
            }
        )
    return rows


def build_source_export_rows():
    sources = (
        Source.objects.prefetch_related("clinicalitem_set")
        .annotate(linked_item_count=Count("clinicalitem", distinct=True))
        .order_by("publisher", "title")
    )
    rows = []
    for source in sources:
        linked_items = list(source.clinicalitem_set.all().order_by("title"))
        rows.append(
            {
                "id": source.pk,
                "publisher": source.publisher,
                "title": source.title,
                "url": source.url,
                "publication_date": source.publication_date,
                "access_date": source.access_date,
                "version_label": source.version_label,
                "linked_item_count": source.linked_item_count,
                "linked_item_titles": joined(item.secondary_title for item in linked_items),
            }
        )
    return rows


def csv_response(filename, headers, rows):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(build_csv_text(headers, rows))
    return response
