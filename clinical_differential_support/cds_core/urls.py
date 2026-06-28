from django.urls import path

from . import views

app_name = "cds_core"

urlpatterns = [
    path("", views.home_dashboard, name="home"),
    path("headache/", views.headache_workspace, name="headache"),
    path("launch/", views.launch_guide, name="launch_guide"),
    path("completion/", views.completion_gate, name="completion_gate"),
    path("deployment/", views.deployment_status, name="deployment_status"),
    path("chest-pain/", views.chest_pain_workspace, name="chest_pain"),
    path("abdominal-pain/", views.abdominal_pain_workspace, name="abdominal_pain"),
    path("dyspnea/", views.dyspnea_workspace, name="dyspnea"),
    path("health/", views.health_check, name="health_check"),
    path("cases/", views.case_index, name="case_index"),
    path("cases/<slug:slug>/", views.case_detail, name="case_detail"),
    path("review/", views.review_dashboard, name="review_dashboard"),
    path("review/login/", views.ReviewerLoginView.as_view(), name="review_login"),
    path("review/logout/", views.ReviewerLogoutView.as_view(), name="review_logout"),
    path("review/queue/", views.review_queue, name="review_queue"),
    path("review/readiness/", views.release_readiness, name="release_readiness"),
    path("review/next-actions/", views.next_actions, name="next_actions"),
    path("review/coverage-depth/", views.coverage_depth, name="coverage_depth"),
    path("review/source-freshness/", views.source_freshness, name="source_freshness"),
    path(
        "review/final-verification/",
        views.final_verification,
        name="final_verification",
    ),
    path(
        "review/exports/next-actions.json",
        views.export_next_actions_json,
        name="export_next_actions_json",
    ),
    path(
        "review/exports/coverage-depth.json",
        views.export_coverage_depth_json,
        name="export_coverage_depth_json",
    ),
    path(
        "review/exports/source-freshness.json",
        views.export_source_freshness_json,
        name="export_source_freshness_json",
    ),
    path(
        "review/exports/final-verification.json",
        views.export_final_verification_json,
        name="export_final_verification_json",
    ),
    path(
        "review/exports/clinical-items.csv",
        views.export_clinical_items_csv,
        name="export_clinical_items_csv",
    ),
    path(
        "review/exports/sources.csv",
        views.export_sources_csv,
        name="export_sources_csv",
    ),
    path(
        "review/exports/release-evidence.json",
        views.export_release_evidence_json,
        name="export_release_evidence_json",
    ),
    path(
        "review/exports/handoff-report.md",
        views.export_handoff_report_markdown,
        name="export_handoff_report_markdown",
    ),
    path(
        "review/exports/handoff-bundle.zip",
        views.export_handoff_bundle_zip,
        name="export_handoff_bundle_zip",
    ),
    path("review/sources/", views.source_index, name="source_index"),
    path("review/sources/new/", views.source_create, name="source_create"),
    path("review/sources/<int:pk>/", views.source_detail, name="source_detail"),
    path("review/sources/<int:pk>/edit/", views.source_edit, name="source_edit"),
    path("review/items/new/", views.review_item_create, name="review_item_create"),
    path("review/items/<int:pk>/", views.review_item_detail, name="review_item_detail"),
    path("review/items/<int:pk>/edit/", views.review_item_edit, name="review_item_edit"),
    path(
        "review/items/<int:pk>/sources/",
        views.review_item_sources,
        name="review_item_sources",
    ),
    path(
        "review/items/<int:pk>/decision/",
        views.review_item_decision,
        name="review_item_decision",
    ),
]
