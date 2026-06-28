from django.contrib import admin

from .models import (
    AuditEvent,
    CaseScenario,
    ChiefComplaint,
    ClinicalItem,
    ClinicalItemSource,
    ReviewRecord,
    Rule,
    Source,
)


class ClinicalItemSourceInline(admin.TabularInline):
    model = ClinicalItemSource
    extra = 1


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("publisher", "title", "version_label", "access_date")
    search_fields = ("publisher", "title", "url")


@admin.register(ChiefComplaint)
class ChiefComplaintAdmin(admin.ModelAdmin):
    list_display = ("slug", "title")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ClinicalItem)
class ClinicalItemAdmin(admin.ModelAdmin):
    list_display = (
        "primary_title",
        "secondary_title",
        "item_type",
        "urgency",
        "status",
        "last_reviewed_at",
    )
    list_filter = ("status", "item_type", "urgency", "review_due_at")
    search_fields = ("title", "title_zh", "title_en", "summary", "summary_zh", "summary_en")
    inlines = [ClinicalItemSourceInline]
    actions = ["submit_for_review", "retire_items"]

    @admin.action(description="Submit selected items for review")
    def submit_for_review(self, request, queryset):
        queryset.update(status=ClinicalItem.Status.IN_REVIEW)

    @admin.action(description="Retire selected items")
    def retire_items(self, request, queryset):
        queryset.update(status=ClinicalItem.Status.RETIRED)


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("slug", "chief_complaint", "output_item", "priority", "active")
    list_filter = ("active", "chief_complaint")
    search_fields = ("slug", "output_item__title")


@admin.register(CaseScenario)
class CaseScenarioAdmin(admin.ModelAdmin):
    list_display = ("primary_title", "secondary_title", "chief_complaint", "active")
    list_filter = ("chief_complaint", "active")
    search_fields = ("slug", "title_zh", "title_en", "summary_zh", "summary_en")


@admin.register(ReviewRecord)
class ReviewRecordAdmin(admin.ModelAdmin):
    list_display = ("clinical_item", "reviewer", "decision", "created_at")
    list_filter = ("decision", "created_at")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("clinical_item", "event_type", "actor", "created_at")
    list_filter = ("event_type", "created_at")
