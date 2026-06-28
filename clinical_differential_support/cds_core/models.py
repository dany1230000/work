from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Source(models.Model):
    publisher = models.CharField(max_length=120)
    title = models.CharField(max_length=240)
    url = models.URLField()
    publication_date = models.DateField(null=True, blank=True)
    access_date = models.DateField()
    version_label = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["publisher", "title"]

    def __str__(self) -> str:
        return f"{self.publisher}: {self.title}"


class ChiefComplaint(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class ClinicalItemQuerySet(models.QuerySet):
    def clinician_visible(self):
        return self.filter(status=ClinicalItem.Status.APPROVED)


class ClinicalItem(models.Model):
    class ItemType(models.TextChoices):
        RED_FLAG = "red_flag", "Red flag"
        DIFFERENTIAL = "differential", "Differential consideration"
        WORKUP = "workup", "Workup prompt"
        MANAGEMENT = "management", "Management note"
        MEDICATION_SAFETY = "medication_safety", "Medication safety"

    class Urgency(models.TextChoices):
        EMERGENT = "emergent", "Emergent"
        URGENT = "urgent", "Urgent"
        SOON = "soon", "Soon"
        ROUTINE = "routine", "Routine"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In review"
        APPROVED = "approved", "Approved"
        RETIRED = "retired", "Retired"

    chief_complaint = models.ForeignKey(
        ChiefComplaint, null=True, blank=True, on_delete=models.CASCADE
    )
    item_type = models.CharField(max_length=32, choices=ItemType.choices)
    title = models.CharField(max_length=180)
    summary = models.TextField()
    title_zh = models.CharField(max_length=180, blank=True)
    title_en = models.CharField(max_length=180, blank=True)
    summary_zh = models.TextField(blank=True)
    summary_en = models.TextField(blank=True)
    urgency = models.CharField(
        max_length=24, choices=Urgency.choices, default=Urgency.ROUTINE
    )
    status = models.CharField(
        max_length=24, choices=Status.choices, default=Status.DRAFT
    )
    version_label = models.CharField(max_length=80, default="MVP-1")
    last_reviewed_at = models.DateField(null=True, blank=True)
    review_due_at = models.DateField(null=True, blank=True)
    missing_questions = models.JSONField(default=list, blank=True)
    supporting_findings = models.JSONField(default=list, blank=True)
    opposing_findings = models.JSONField(default=list, blank=True)
    sources = models.ManyToManyField(Source, through="ClinicalItemSource", blank=True)

    objects = ClinicalItemQuerySet.as_manager()

    class Meta:
        ordering = ["item_type", "urgency", "title"]

    def __str__(self) -> str:
        return self.primary_title

    @property
    def is_publishable(self) -> bool:
        return self.status == self.Status.APPROVED and self.sources.exists()

    @property
    def primary_title(self) -> str:
        return self.title_zh or self.title

    @property
    def secondary_title(self) -> str:
        return self.title_en or self.title

    @property
    def primary_summary(self) -> str:
        return self.summary_zh or self.summary

    @property
    def secondary_summary(self) -> str:
        return self.summary_en or self.summary


class ClinicalItemSource(models.Model):
    clinical_item = models.ForeignKey(ClinicalItem, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("clinical_item", "source")]


class Rule(models.Model):
    chief_complaint = models.ForeignKey(ChiefComplaint, on_delete=models.CASCADE)
    output_item = models.ForeignKey(ClinicalItem, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    condition = models.JSONField()
    source_ids = models.JSONField(default=list, blank=True)
    priority = models.PositiveIntegerField(default=100)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["priority", "slug"]

    def __str__(self) -> str:
        return self.slug


class CaseScenario(models.Model):
    chief_complaint = models.ForeignKey(ChiefComplaint, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    title_zh = models.CharField(max_length=180)
    title_en = models.CharField(max_length=180)
    summary_zh = models.TextField()
    summary_en = models.TextField()
    findings = models.JSONField()
    expected_item_titles = models.JSONField(default=list)
    display_order = models.PositiveIntegerField(default=100)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "slug"]

    def __str__(self) -> str:
        return self.primary_title

    @property
    def primary_title(self) -> str:
        return self.title_zh

    @property
    def secondary_title(self) -> str:
        return self.title_en

    @property
    def primary_summary(self) -> str:
        return self.summary_zh

    @property
    def secondary_summary(self) -> str:
        return self.summary_en


class AuditEvent(models.Model):
    class EventType(models.TextChoices):
        CREATED = "created", "Created"
        SUBMITTED = "submitted", "Submitted for review"
        APPROVED = "approved", "Approved"
        CHANGES_REQUESTED = "changes_requested", "Changes requested"
        RETIRED = "retired", "Retired"
        SOURCES_UPDATED = "sources_updated", "Sources updated"

    clinical_item = models.ForeignKey(ClinicalItem, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ReviewRecord(models.Model):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        CHANGES_REQUESTED = "changes_requested", "Changes requested"
        RETIRED = "retired", "Retired"

    clinical_item = models.ForeignKey(ClinicalItem, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    decision = models.CharField(max_length=32, choices=Decision.choices)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not is_new:
            return

        item = self.clinical_item
        event_type = AuditEvent.EventType.CHANGES_REQUESTED
        if self.decision == self.Decision.APPROVED:
            item.status = ClinicalItem.Status.APPROVED
            item.last_reviewed_at = timezone.localdate()
            item.review_due_at = item.last_reviewed_at + timedelta(days=180)
            event_type = AuditEvent.EventType.APPROVED
        elif self.decision == self.Decision.RETIRED:
            item.status = ClinicalItem.Status.RETIRED
            event_type = AuditEvent.EventType.RETIRED
        else:
            item.status = ClinicalItem.Status.DRAFT

        item.save(update_fields=["status", "last_reviewed_at", "review_due_at"])
        AuditEvent.objects.create(
            clinical_item=item,
            event_type=event_type,
            actor=self.reviewer,
            notes=self.notes,
        )
