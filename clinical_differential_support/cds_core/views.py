from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from .auth import staff_required
from .bundle import build_handoff_bundle_zip
from .coverage_depth import build_coverage_depth_report
from .deployment_status import (
    build_deployment_status_report,
    default_public_deployment_evidence_path,
)
from .evidence import build_release_evidence_package
from .exports import (
    CLINICAL_ITEM_EXPORT_HEADERS,
    SOURCE_EXPORT_HEADERS,
    build_clinical_item_export_rows,
    build_source_export_rows,
    csv_response,
)
from .final_verification import build_final_verification_gate
from .forms import (
    AbdominalPainIntakeForm,
    ClinicalItemDraftForm,
    ClinicalItemSourceLinkForm,
    ChestPainIntakeForm,
    DyspneaIntakeForm,
    GeneralDifferentialForm,
    HeadacheIntakeForm,
    ReviewDecisionForm,
    SourceForm,
    localize_intake_form_labels,
)
from .governance import (
    build_release_readiness_report,
    build_review_dashboard,
    build_review_item_detail,
    build_review_queue,
)
from .general_differential import (
    evaluate_general_differential,
    get_general_differential_catalog_summary,
)
from .differential_catalog import CONDITIONS, FINDING_GROUPS
from .differential_catalog_quality import (
    build_general_differential_catalog_quality_report,
)
from .differential_catalog_workbench import (
    build_general_differential_import_workbench,
)
from .handoff import build_handoff_report_markdown
from .local_launch import build_local_launch_status
from .models import AuditEvent, CaseScenario, ClinicalItem, ReviewRecord, Source
from .next_actions import build_next_action_plan
from .project_completion import build_project_completion_report
from .services import (
    evaluate_abdominal_pain_pathway,
    evaluate_case_scenario,
    evaluate_chest_pain_pathway,
    evaluate_dyspnea_pathway,
    evaluate_headache_pathway,
)
from .source_freshness import build_source_freshness_report


CLINICIAN_SAFETY_COPY = (
    "限合格醫療專業人員使用；僅供參考，非診斷或治療醫囑。 "
    "For qualified medical professionals. Reference support only; "
    "not a diagnosis or treatment order."
)

CASE_SAFETY_COPY = (
    "病例模擬使用非病人資料情境，供規則驗證與教學審核。 "
    "Case simulations use non-patient fixture data for rule validation and teaching review."
)

GOVERNANCE_SAFETY_COPY = (
    "臨床內容治理頁僅供合格醫療專業人員審核 MVP 內容、來源與測試案例。 "
    "Clinical governance view for qualified medical professionals "
    "to review MVP content, sources, and validation cases."
)

ITEM_REVIEW_SAFETY_COPY = (
    "臨床項目審核頁僅供合格醫療專業人員檢視內容、來源、規則與稽核紀錄。 "
    "Clinical item review view for qualified medical professionals "
    "to inspect content, sources, rules, and audit history."
)

DRAFT_SAFETY_COPY = (
    "臨床項目草稿僅供內容治理；核准仍需經由審核決策。 "
    "Clinical item drafts are for content governance only; "
    "approval still requires a review decision."
)

READINESS_SAFETY_COPY = (
    "交付整備報告僅供 staff 內容治理使用，不代表臨床上線核准。 "
    "Release readiness is for staff content governance only; "
    "it is not clinical deployment approval."
)

REVIEWER_ACCESS_SAFETY_COPY = (
    "審核者入口僅供 staff 內容治理使用。請勿輸入真實病人識別資料、診斷指令或治療指令。 "
    "Staff reviewer access is for content governance only. "
    "Reference support only; not a diagnosis or treatment order. "
    "Do not enter patient-identifying data, diagnosis orders, or treatment orders."
)

NEXT_ACTION_SAFETY_COPY = (
    "下一步工作台僅供 staff 內容治理與專案規劃使用；它不是臨床部署核准，"
    "也不是診斷或治療指令。 "
    "Next Action Workbench is for staff content governance and project planning only; "
    "it is not clinical deployment approval, diagnosis, or treatment instruction."
)

COVERAGE_DEPTH_SAFETY_COPY = (
    "覆蓋深度審查僅供 staff 內容治理與專案規劃使用；"
    "不包含病人資料、診斷指令、治療指令或用藥指令。 "
    "Coverage Depth Review is for staff content governance and project planning only; "
    "it does not include patient data, diagnosis orders, treatment orders, or medication orders."
)

SOURCE_FRESHNESS_SAFETY_COPY = (
    "來源新鮮度審查僅供 staff 內容治理使用；不會自動修改來源、推論日期、"
    "建立診斷或治療指令。 "
    "Source Freshness Audit is for staff content governance only; "
    "it does not automatically edit sources, infer dates, or create diagnosis or treatment orders."
)

FINAL_VERIFICATION_SAFETY_COPY = (
    "最終驗收門檻僅供 staff 內容治理與交付檢查使用；"
    "它不會執行外部命令、不保存病人資料，也不是臨床部署核准。 "
    "Final Verification Gate is for staff content governance and handoff checks only; "
    "it does not run external commands, store patient data, or approve clinical deployment."
)

PROJECT_COMPLETION_SAFETY_COPY = (
    "最終版完成判斷只彙整本機驗證與手動 blocker；不建立帳號、不略過登入、"
    "不保存密碼、不包含病人資料，也不是臨床部署核准。 "
    "Final Project Gate summarizes local readiness only; it does not create "
    "accounts, bypass login, store passwords, store patient data, or approve "
    "clinical deployment."
)

DEPLOYMENT_STATUS_SAFETY_COPY = (
    "部署操作中心只彙整部署下一步與外部 blocker；不會建立 Git remote、登入 Render、"
    "保存密碼、建立帳號、輸入病人資料或核准正式臨床上線。 "
    "Deployment Operations Center reports deployment next steps only; it does not "
    "create remotes, authenticate Render, store credentials, create accounts, "
    "store patient data, or approve clinical production use."
)


CLINICIAN_SAFETY_COPY = (
    "僅供合格醫療專業人員作為參考支援；不是診斷、治療、用藥或醫囑。"
    "請勿輸入病人識別資料。 "
    "For qualified medical professionals only. Reference support, not a diagnosis, "
    "treatment, medication, or clinical order. Do not enter patient-identifying data."
)

CASE_SAFETY_COPY = (
    "案例使用非病人測試資料，用於規則驗證與教學審閱。 "
    "Case simulations use non-patient fixture data for rule validation and teaching review."
)

GOVERNANCE_SAFETY_COPY = (
    "內容治理區僅供合格醫療專業人員審閱 MVP 內容、來源與驗證案例。 "
    "Clinical governance is for qualified medical professionals to review MVP content, sources, and validation cases."
)

ITEM_REVIEW_SAFETY_COPY = (
    "審核頁用於檢查內容、來源、規則與稽核紀錄；不是臨床指令。 "
    "Review pages inspect content, sources, rules, and audit history; they are not clinical orders."
)

DRAFT_SAFETY_COPY = (
    "草稿僅供內容治理使用；正式可用仍需要審核決策。 "
    "Drafts are for content governance only; approval still requires a review decision."
)

READINESS_SAFETY_COPY = (
    "發布準備度僅供 staff 內容治理使用；不代表臨床部署核准。 "
    "Release readiness is for staff content governance only and is not clinical deployment approval."
)

REVIEWER_ACCESS_SAFETY_COPY = (
    "審核者登入僅供 staff 內容治理使用。請勿輸入病人識別資料、診斷指令或治療指令。 "
    "Staff reviewer access is for content governance only. Reference support only. "
    "Do not enter patient identifiers, diagnosis orders, or treatment orders."
)

NEXT_ACTION_SAFETY_COPY = (
    "下一步工作台僅供 staff 內容治理與專案規劃使用；不是臨床部署、診斷或治療指示。 "
    "Next Action Workbench is for staff content governance and project planning only."
)

COVERAGE_DEPTH_SAFETY_COPY = (
    "覆蓋深度審查僅供 staff 內容治理與專案規劃使用，不包含病人資料或臨床指令。 "
    "Coverage Depth Review is for staff governance and planning; it contains no patient data or clinical orders."
)

SOURCE_FRESHNESS_SAFETY_COPY = (
    "來源新鮮度稽核僅供 staff 內容治理使用；不會自動編輯來源或推論日期。 "
    "Source Freshness Audit is for staff content governance only and does not automatically edit sources or infer dates."
)

FINAL_VERIFICATION_SAFETY_COPY = (
    "最終驗證閘門僅供 staff 內容治理與交付檢查使用；不儲存病人資料，也不核准臨床部署。 "
    "Final Verification Gate is for staff governance and handoff checks only."
)

PROJECT_COMPLETION_SAFETY_COPY = (
    "最終專案閘門只總結本機完成度；不建立帳號、不略過登入、不儲存密碼或病人資料，也不核准臨床使用。 "
    "Final Project Gate summarizes local readiness only and does not approve clinical deployment."
)

DEPLOYMENT_STATUS_SAFETY_COPY = (
    "部署狀態頁只回報下一步與健康檢查；不建立遠端、不登入 Render、不儲存憑證或病人資料，也不核准臨床正式使用。 "
    "Deployment Operations Center reports next steps and health only; it does not authenticate, store credentials, or approve clinical production use."
)

LOCAL_LAUNCH_SAFETY_COPY = (
    "啟動導覽只回報本機下一步；不建立帳號、不略過登入、不儲存密碼或病人資料，也不核准臨床部署。 "
    "Local launch guidance only; it does not create accounts, bypass login, store patient data, or approve clinical deployment."
)


GENERAL_DIFFERENTIAL_IMPORT_SAFETY_COPY = (
    "通用鑑別匯入工作台僅供 staff 審核者規劃 catalog 擴充；"
    "不得輸入病人識別資料，也不得把未審核批次當成診斷、治療、用藥或醫囑。 "
    "General differential import governance is staff-only; no patient data, "
    "diagnosis, treatment, medication, or clinical orders."
)


FINDING_SEARCH_SYNONYMS = {
    "chest_pain": "acs mi heart attack myocardial infarction angina coronary",
    "dyspnea": "shortness of breath sob respiratory distress hypoxia",
    "radiating_arm_jaw_pain": "acs mi heart attack myocardial infarction angina coronary",
    "diaphoresis": "sweating sweat clammy acs hypoglycemia",
    "neurologic_deficit": "stroke tia cva weakness numbness facial droop",
    "unilateral_weakness": "stroke tia cva hemiparesis facial droop",
    "speech_vision_changes": "stroke tia cva aphasia dysarthria vision loss",
    "thunderclap_headache": "sah subarachnoid hemorrhage aneurysm",
    "neck_stiffness": "meningitis encephalitis sah",
    "abdominal_pain": "abdomen belly appendicitis cholecystitis pancreatitis",
    "rlq_pain": "appendicitis ectopic ovarian torsion",
    "ruq_pain": "cholecystitis gallbladder hepatitis biliary",
    "pelvic_pain": "pid ectopic ovarian torsion pregnancy",
    "cervical_motion_tenderness": "pid pelvic inflammatory disease toa",
    "vaginal_discharge": "pid sti cervicitis",
    "fever": "sepsis infection meningitis pneumonia pyelonephritis",
    "cough_sputum": "pneumonia bronchitis respiratory infection",
    "pleuritic_pain": "pe pulmonary embolism pneumothorax pneumonia",
    "hemoptysis": "pe pulmonary embolism tuberculosis cancer",
    "unilateral_leg_swelling": "dvt pe pulmonary embolism clot",
    "severe_hyperglycemia_dehydration_confusion": "dka hhs diabetes hyperosmolar",
    "acute_hot_swollen_joint": "septic arthritis gout pseudogout",
    "tense_compartment_or_pain_with_passive_stretch": "compartment syndrome limb ischemia",
    "preeclampsia_warning_features": "eclampsia pregnancy hypertension seizure",
    "suicidal_ideation": "suicide self harm safety psychiatric emergency",
    "hallucinations_delusions": "psychosis schizophrenia mania delirium",
    "purulent_skin_lesion": "abscess cellulitis mrsa skin infection",
    "vesicular_dermatomal_rash": "shingles zoster herpes",
    "mucosal_lesions": "sjs ten stevens johnson toxic epidermal necrolysis",
}


STATUS_REPORT_CACHE_SECONDS = 300
LAUNCH_GUIDE_REPORT_CACHE_KEY = "cds_core:launch_guide_report:v1"
DEPLOYMENT_STATUS_REPORT_CACHE_KEY = "cds_core:deployment_status_report:v1"


class ReviewerLoginView(LoginView):
    template_name = "cds_core/review_login.html"
    redirect_authenticated_user = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.get_user().is_staff:
            messages.error(
                self.request,
                "此帳號沒有 staff 審核權限。 Staff reviewer access is required.",
            )
            return self.form_invalid(form)
        messages.success(self.request, "審核者登入成功。 Reviewer signed in.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("cds_core:review_queue")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["safety_copy"] = REVIEWER_ACCESS_SAFETY_COPY
        return context


class ReviewerLogoutView(LogoutView):
    next_page = reverse_lazy("cds_core:review_login")


def health_check(request):
    try:
        ClinicalItem.objects.exists()
    except DatabaseError:
        return JsonResponse(
            {
                "status": "error",
                "service": "clinical_differential_support",
                "checks": {"database": "error"},
            },
            status=503,
        )

    return JsonResponse(
        {
            "status": "ok",
            "service": "clinical_differential_support",
            "checks": {"database": "ok"},
        }
    )


def home_dashboard(request):
    workflows = [
        {
            "title_zh": "通用鑑別",
            "title_en": "General differential",
            "description_zh": "從跨系統紅旗、主訴搜尋與已知發現開始，產生必須排除的疾病與下一步問題。",
            "description_en": "Start from cross-system red flags, complaint search, and known findings to rank must-not-miss conditions and ask-next prompts.",
            "url": reverse("cds_core:general_differential"),
        },
        {
            "title_zh": "頭痛",
            "title_en": "Headache",
            "description_zh": "用紅旗、偏頭痛、緊縮型與叢發型特徵，產生參考輸出與下一步問題。",
            "description_en": "Use red flags and headache phenotype features to generate reference output and ask-next prompts.",
            "url": reverse("cds_core:headache"),
        },
        {
            "title_zh": "胸痛",
            "title_en": "Chest pain",
            "description_zh": "檢查急性冠心症、主動脈、肺栓塞與穩定型胸痛相關提示。",
            "description_en": "Review prompts for ACS, aortic, pulmonary embolism, and stable exertional chest pain patterns.",
            "url": reverse("cds_core:chest_pain"),
        },
        {
            "title_zh": "腹痛",
            "title_en": "Abdominal pain",
            "description_zh": "依腹痛位置、腹膜刺激、感染、阻塞與懷孕相關風險整理下一步。",
            "description_en": "Organize next steps by location, peritoneal signs, infection, obstruction, and pregnancy-related risks.",
            "url": reverse("cds_core:abdominal_pain"),
        },
        {
            "title_zh": "呼吸困難",
            "title_en": "Dyspnea",
            "description_zh": "以急性與慢性呼吸困難、低氧、胸痛、感染與心肺線索產生提示。",
            "description_en": "Generate prompts from acute/chronic dyspnea, hypoxemia, chest pain, infection, and cardiopulmonary clues.",
            "url": reverse("cds_core:dyspnea"),
        },
    ]
    return render(
        request,
        "cds_core/home.html",
        {
            "workflows": workflows,
            "safety_copy": CLINICIAN_SAFETY_COPY,
        },
    )


def general_differential_workspace(request):
    result = None
    form = GeneralDifferentialForm(request.POST or None)
    selected_findings = request.POST.getlist("findings") if request.method == "POST" else []
    if request.method == "POST" and form.is_valid():
        selected_findings = _dedupe_findings(
            form.cleaned_data.get("findings", selected_findings)
        )
        form.cleaned_data["findings"] = selected_findings
        result = evaluate_general_differential(form.cleaned_data)
    return render(
        request,
        "cds_core/general_differential.html",
        {
            "form": form,
            "finding_library_url": reverse("cds_core:general_differential_findings"),
            "selected_findings": selected_findings,
            "selected_finding_labels": _build_selected_finding_labels(selected_findings),
            "catalog_quick_entries": _build_catalog_quick_entries(),
            "catalog_summary": get_general_differential_catalog_summary(),
            "catalog_quality": build_general_differential_catalog_quality_report(),
            "result": result,
            "safety_copy": CLINICIAN_SAFETY_COPY,
        },
    )


def general_differential_findings(request):
    selected_findings = _selected_findings_from_query(request)
    form = GeneralDifferentialForm()
    return render(
        request,
        "cds_core/partials/general_differential_finding_library.html",
        {
            "form": form,
            "finding_groups": _build_finding_groups(selected_findings),
            "selected_findings": selected_findings,
        },
    )


def _dedupe_findings(findings):
    return list(dict.fromkeys(findings))


def _selected_findings_from_query(request):
    selected_findings = []
    for value in request.GET.getlist("selected"):
        selected_findings.extend(part for part in value.split(",") if part)
    return _dedupe_findings(selected_findings)


def _build_selected_finding_labels(selected_findings):
    selected = set(selected_findings)
    labels = []
    for group in FINDING_GROUPS:
        for slug, title_en, title_zh in group["findings"]:
            if slug in selected:
                labels.append(
                    {
                        "slug": slug,
                        "title_en": title_en,
                        "title_zh": title_zh,
                    }
                )
    return labels


def _build_catalog_quick_entries():
    entries = [
        {
            "entry_id": "genetic-congenital",
            "title": "基因 / 先天 | Genetic / congenital",
            "query": "genetic congenital developmental",
            "description": "先從遺傳、先天、兒科與結締組織線索切入。",
            "system_tokens": ("Genetic", "Pediatric", "Connective tissue", "Skeletal"),
        },
        {
            "entry_id": "blood-immune",
            "title": "血液 / 免疫 | Blood / immune",
            "query": "anemia bleeding immune",
            "description": "適合貧血、出血、免疫缺陷、血液腫瘤或感染風險線索。",
            "system_tokens": ("Hematology", "Immunology", "Immune", "Oncology"),
        },
        {
            "entry_id": "endocrine-metabolic",
            "title": "內分泌 / 代謝 | Endocrine / metabolic",
            "query": "endocrine metabolic newborn screen",
            "description": "適合低血糖、電解質、甲狀腺、腎上腺或新生兒篩檢線索。",
            "system_tokens": ("Endocrine", "Metabolic"),
        },
        {
            "entry_id": "neurodevelopmental",
            "title": "神經發展 | Neurodevelopmental",
            "query": "seizure developmental regression neurodevelopmental",
            "description": "適合癲癇、發展遲緩、退化、行為或神經肌肉線索。",
            "system_tokens": ("Neurodevelopmental", "Neurologic", "Neuromuscular"),
        },
    ]
    for entry in entries:
        entry["count"] = _count_catalog_systems(entry["system_tokens"])
    return entries


def _count_catalog_systems(tokens):
    return sum(
        1
        for condition in CONDITIONS
        if any(token in str(condition.get("system", "")) for token in tokens)
    )


def _build_finding_groups(selected_findings):
    selected = set(selected_findings)
    groups = []
    for group in FINDING_GROUPS:
        findings = [
            {
                "slug": slug,
                "title_en": title_en,
                "title_zh": title_zh,
                "search_terms": FINDING_SEARCH_SYNONYMS.get(slug, ""),
                "selected": slug in selected,
            }
            for slug, title_en, title_zh in group["findings"]
        ]
        groups.append(
            {
                "group_en": group["group_en"],
                "group_zh": group["group_zh"],
                "default_open": group["group_en"] == "Immediate safety",
                "count": len(findings),
                "selected_count": sum(1 for finding in findings if finding["selected"]),
                "findings": findings,
            }
        )
    return groups


def _refresh_requested(request):
    return request.GET.get("refresh") == "1"


def _status_report_cache_scope():
    backend = settings.CACHES["default"]["BACKEND"]
    if backend == "django.core.cache.backends.db.DatabaseCache":
        return "shared"
    return "process-local"


def _cached_status_report(cache_key, refresh_requested, report_builder):
    if not refresh_requested:
        cached_report = cache.get(cache_key)
        if cached_report is not None:
            return cached_report, {
                "cache_status": "cached",
                "cache_scope": _status_report_cache_scope(),
                "ttl_seconds": STATUS_REPORT_CACHE_SECONDS,
            }

    report = report_builder()
    cache.set(cache_key, report, STATUS_REPORT_CACHE_SECONDS)
    return report, {
        "cache_status": "refreshed" if refresh_requested else "generated",
        "cache_scope": _status_report_cache_scope(),
        "ttl_seconds": STATUS_REPORT_CACHE_SECONDS,
    }


def launch_guide(request):
    report, report_cache = _cached_status_report(
        LAUNCH_GUIDE_REPORT_CACHE_KEY,
        _refresh_requested(request),
        build_local_launch_status,
    )
    return render(
        request,
        "cds_core/launch_guide.html",
        {
            "report": report,
            "report_cache": report_cache,
            "safety_copy": (
                "本頁只提供本機啟動與治理導覽，不建立帳號、不略過登入、"
                "不包含病人資料，也不是臨床部署核准。 "
                "Local launch guidance only; it does not create accounts, "
                "bypass login, store patient data, or approve clinical deployment."
            ),
            "safety_copy": LOCAL_LAUNCH_SAFETY_COPY,
        },
    )


def completion_gate(request):
    return render(
        request,
        "cds_core/project_completion.html",
        {
            "report": build_project_completion_report(),
            "safety_copy": PROJECT_COMPLETION_SAFETY_COPY,
        },
    )


def deployment_status(request):
    report, report_cache = _cached_status_report(
        DEPLOYMENT_STATUS_REPORT_CACHE_KEY,
        _refresh_requested(request),
        lambda: build_deployment_status_report(
            deployment_evidence_path=default_public_deployment_evidence_path()
        ),
    )
    return render(
        request,
        "cds_core/deployment_status.html",
        {
            "report": report,
            "report_cache": report_cache,
            "safety_copy": DEPLOYMENT_STATUS_SAFETY_COPY,
        },
    )


def headache_workspace(request):
    result = None
    localize_intake_form_labels(HeadacheIntakeForm)
    form = HeadacheIntakeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        result = evaluate_headache_pathway(form.cleaned_data)
    return render(
        request,
        "cds_core/headache.html",
        {
            "form": form,
            "result": result,
            "safety_copy": CLINICIAN_SAFETY_COPY,
        },
    )


def chest_pain_workspace(request):
    result = None
    localize_intake_form_labels(ChestPainIntakeForm)
    form = ChestPainIntakeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        result = evaluate_chest_pain_pathway(form.cleaned_data)
    return render(
        request,
        "cds_core/chest_pain.html",
        {
            "form": form,
            "result": result,
            "safety_copy": CLINICIAN_SAFETY_COPY,
        },
    )


def abdominal_pain_workspace(request):
    result = None
    localize_intake_form_labels(AbdominalPainIntakeForm)
    form = AbdominalPainIntakeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        result = evaluate_abdominal_pain_pathway(form.cleaned_data)
    return render(
        request,
        "cds_core/abdominal_pain.html",
        {
            "form": form,
            "result": result,
            "safety_copy": CLINICIAN_SAFETY_COPY,
        },
    )


def dyspnea_workspace(request):
    result = None
    localize_intake_form_labels(DyspneaIntakeForm)
    form = DyspneaIntakeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        result = evaluate_dyspnea_pathway(form.cleaned_data)
    return render(
        request,
        "cds_core/dyspnea.html",
        {
            "form": form,
            "result": result,
            "safety_copy": CLINICIAN_SAFETY_COPY,
        },
    )


def case_index(request):
    scenarios = CaseScenario.objects.filter(active=True).select_related("chief_complaint")
    return render(
        request,
        "cds_core/case_index.html",
        {
            "scenarios": scenarios,
            "safety_copy": CASE_SAFETY_COPY,
        },
    )


def case_detail(request, slug):
    scenario = get_object_or_404(CaseScenario, slug=slug, active=True)
    evaluation = evaluate_case_scenario(scenario)
    return render(
        request,
        "cds_core/case_detail.html",
        {
            "scenario": scenario,
            "evaluation": evaluation,
            "safety_copy": CASE_SAFETY_COPY,
        },
    )


def review_dashboard(request):
    dashboard = build_review_dashboard()
    return render(
        request,
        "cds_core/review_dashboard.html",
        {
            "dashboard": dashboard,
            "safety_copy": GOVERNANCE_SAFETY_COPY,
        },
    )


def review_queue(request):
    queue = build_review_queue(
        filters={
            "status": request.GET.get("status", ""),
            "urgency": request.GET.get("urgency", ""),
            "q": request.GET.get("q", ""),
        }
    )
    return render(
        request,
        "cds_core/review_queue.html",
        {
            "queue": queue,
            "safety_copy": (
                "審核佇列僅供內容治理、來源覆蓋與到期審核排序。"
                "Reviewer queue is for content governance, source coverage, "
                "and due-review prioritization only."
            ),
        },
    )


@staff_required
def release_readiness(request):
    return render(
        request,
        "cds_core/release_readiness.html",
        {
            "report": build_release_readiness_report(),
            "safety_copy": READINESS_SAFETY_COPY,
        },
    )


@staff_required
def next_actions(request):
    return render(
        request,
        "cds_core/next_actions.html",
        {
            "plan": build_next_action_plan(),
            "safety_copy": NEXT_ACTION_SAFETY_COPY,
        },
    )


@staff_required
def coverage_depth(request):
    return render(
        request,
        "cds_core/coverage_depth.html",
        {
            "report": build_coverage_depth_report(),
            "safety_copy": COVERAGE_DEPTH_SAFETY_COPY,
        },
    )


@staff_required
def general_differential_import(request):
    return render(
        request,
        "cds_core/general_differential_import.html",
        {
            "report": build_general_differential_import_workbench(),
            "safety_copy": GENERAL_DIFFERENTIAL_IMPORT_SAFETY_COPY,
        },
    )


@staff_required
def source_freshness(request):
    return render(
        request,
        "cds_core/source_freshness.html",
        {
            "report": build_source_freshness_report(),
            "safety_copy": SOURCE_FRESHNESS_SAFETY_COPY,
        },
    )


@staff_required
def final_verification(request):
    return render(
        request,
        "cds_core/final_verification.html",
        {
            "report": build_final_verification_gate(),
            "safety_copy": FINAL_VERIFICATION_SAFETY_COPY,
        },
    )


@staff_required
def export_next_actions_json(request):
    response = JsonResponse(
        build_next_action_plan(),
        json_dumps_params={"indent": 2},
    )
    response["Content-Disposition"] = 'attachment; filename="next-actions.json"'
    return response


@staff_required
def export_coverage_depth_json(request):
    response = JsonResponse(
        build_coverage_depth_report(),
        json_dumps_params={"indent": 2},
    )
    response["Content-Disposition"] = 'attachment; filename="coverage-depth.json"'
    return response


@staff_required
def export_general_differential_import_json(request):
    response = JsonResponse(
        build_general_differential_import_workbench(),
        json_dumps_params={"indent": 2},
    )
    response["Content-Disposition"] = (
        'attachment; filename="general-differential-import.json"'
    )
    return response


@staff_required
def export_source_freshness_json(request):
    response = JsonResponse(
        build_source_freshness_report(),
        json_dumps_params={"indent": 2},
    )
    response["Content-Disposition"] = 'attachment; filename="source-freshness.json"'
    return response


@staff_required
def export_final_verification_json(request):
    response = JsonResponse(
        build_final_verification_gate(),
        json_dumps_params={"indent": 2},
    )
    response["Content-Disposition"] = 'attachment; filename="final-verification.json"'
    return response


@staff_required
def export_clinical_items_csv(request):
    return csv_response(
        "clinical-items.csv",
        CLINICAL_ITEM_EXPORT_HEADERS,
        build_clinical_item_export_rows(),
    )


@staff_required
def export_sources_csv(request):
    return csv_response(
        "sources.csv",
        SOURCE_EXPORT_HEADERS,
        build_source_export_rows(),
    )


@staff_required
def export_release_evidence_json(request):
    response = JsonResponse(
        build_release_evidence_package(),
        json_dumps_params={"indent": 2},
    )
    response["Content-Disposition"] = 'attachment; filename="release-evidence.json"'
    return response


@staff_required
def export_handoff_report_markdown(request):
    response = HttpResponse(
        build_handoff_report_markdown(),
        content_type="text/markdown; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="handoff-report.md"'
    return response


@staff_required
def export_handoff_bundle_zip(request):
    response = HttpResponse(
        build_handoff_bundle_zip(),
        content_type="application/zip",
    )
    response["Content-Disposition"] = 'attachment; filename="handoff-bundle.zip"'
    return response


def source_index(request):
    sources = Source.objects.all().prefetch_related("clinicalitem_set")
    return render(
        request,
        "cds_core/source_index.html",
        {
            "sources": sources,
            "safety_copy": (
                "來源庫用於檢視 MVP 內容依據與覆蓋情形。"
                "Source library for reviewing MVP evidence coverage."
            ),
        },
    )


def source_detail(request, pk):
    source = get_object_or_404(
        Source.objects.prefetch_related("clinicalitem_set"),
        pk=pk,
    )
    linked_items = source.clinicalitem_set.all().order_by(
        "item_type", "urgency", "title"
    )
    return render(
        request,
        "cds_core/source_detail.html",
        {
            "source": source,
            "linked_items": linked_items,
            "safety_copy": (
                "來源詳情用於檢視內容依據與引用範圍。"
                "Source detail view for reviewing evidence and citation coverage."
            ),
        },
    )


def review_item_detail(request, pk):
    item = get_object_or_404(
        ClinicalItem.objects.select_related("chief_complaint").prefetch_related(
            "sources"
        ),
        pk=pk,
    )
    detail = build_review_item_detail(item)
    return render(
        request,
        "cds_core/review_item_detail.html",
        {
            "detail": detail,
            "decision_form": ReviewDecisionForm(),
            "source_link_form": ClinicalItemSourceLinkForm(item=item),
            "safety_copy": ITEM_REVIEW_SAFETY_COPY,
        },
    )


@staff_required
def source_create(request):
    form = SourceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        source = form.save()
        messages.success(request, "來源已建立。 Source created.")
        return redirect("cds_core:source_detail", pk=source.pk)
    return render(
        request,
        "cds_core/source_form.html",
        {
            "form": form,
            "mode": "create",
            "page_title": "新增來源",
            "page_title_en": "New source",
            "submit_label": "建立來源 / Create source",
            "safety_copy": (
                "來源資料僅供內容治理與證據覆蓋檢視。"
                "Source metadata is for content governance and evidence coverage review."
            ),
        },
    )


@staff_required
def source_edit(request, pk):
    source = get_object_or_404(Source, pk=pk)
    form = SourceForm(request.POST or None, instance=source)
    if request.method == "POST" and form.is_valid():
        source = form.save()
        for item in source.clinicalitem_set.all():
            AuditEvent.objects.create(
                clinical_item=item,
                event_type=AuditEvent.EventType.SOURCES_UPDATED,
                actor=request.user,
                notes=f"Source metadata updated: {source.publisher}: {source.title}",
            )
        messages.success(request, "來源已更新。 Source updated.")
        return redirect("cds_core:source_detail", pk=source.pk)
    return render(
        request,
        "cds_core/source_form.html",
        {
            "form": form,
            "source": source,
            "mode": "edit",
            "page_title": "編輯來源",
            "page_title_en": "Edit source",
            "submit_label": "更新來源 / Update source",
            "safety_copy": (
                "來源資料僅供內容治理與證據覆蓋檢視。"
                "Source metadata is for content governance and evidence coverage review."
            ),
        },
    )


@staff_required
def review_item_create(request):
    form = ClinicalItemDraftForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        messages.success(request, "草稿已建立。Draft clinical item created.")
        return redirect("cds_core:review_item_detail", pk=item.pk)
    return render(
        request,
        "cds_core/review_item_form.html",
        {
            "form": form,
            "mode": "create",
            "page_title": "新增臨床項目",
            "page_title_en": "New clinical item",
            "submit_label": "建立草稿 / Create draft",
            "safety_copy": DRAFT_SAFETY_COPY,
        },
    )


@staff_required
def review_item_edit(request, pk):
    item = get_object_or_404(ClinicalItem, pk=pk)
    was_approved = item.status == ClinicalItem.Status.APPROVED
    form = ClinicalItemDraftForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        if was_approved:
            item.status = ClinicalItem.Status.IN_REVIEW
            item.save(update_fields=["status"])
            AuditEvent.objects.create(
                clinical_item=item,
                event_type=AuditEvent.EventType.SUBMITTED,
                actor=request.user,
                notes="Clinical item edited after approval and returned to review.",
            )
            messages.success(
                request,
                "內容已更新並返回審核。 Clinical item updated and returned to review.",
            )
        else:
            messages.success(request, "草稿已更新。 Draft clinical item updated.")
        return redirect("cds_core:review_item_detail", pk=item.pk)
    return render(
        request,
        "cds_core/review_item_form.html",
        {
            "form": form,
            "item": item,
            "mode": "edit",
            "page_title": "編輯草稿",
            "page_title_en": "Edit draft",
            "submit_label": "更新草稿 / Update draft",
            "safety_copy": DRAFT_SAFETY_COPY,
        },
    )


@staff_required
def review_item_sources(request, pk):
    item = get_object_or_404(ClinicalItem, pk=pk)
    if request.method != "POST":
        return redirect("cds_core:review_item_detail", pk=item.pk)

    form = ClinicalItemSourceLinkForm(request.POST, item=item)
    if form.is_valid():
        selected_sources = form.save()
        source_names = ", ".join(
            f"{source.publisher}: {source.title}" for source in selected_sources
        )
        if not source_names:
            source_names = "No sources linked"
        AuditEvent.objects.create(
            clinical_item=item,
            event_type=AuditEvent.EventType.SOURCES_UPDATED,
            actor=request.user,
            notes=f"Source links updated: {source_names}",
        )
        messages.success(request, "來源連結已更新。 Source links updated.")
        return redirect("cds_core:review_item_detail", pk=item.pk)

    messages.error(request, "來源連結未儲存。 Source links were not saved.")
    detail = build_review_item_detail(item)
    return render(
        request,
        "cds_core/review_item_detail.html",
        {
            "detail": detail,
            "decision_form": ReviewDecisionForm(),
            "source_link_form": form,
            "safety_copy": ITEM_REVIEW_SAFETY_COPY,
        },
    )


@staff_required
def review_item_decision(request, pk):
    item = get_object_or_404(ClinicalItem, pk=pk)
    if request.method != "POST":
        return redirect("cds_core:review_item_detail", pk=item.pk)

    form = ReviewDecisionForm(request.POST)
    if form.is_valid():
        ReviewRecord.objects.create(
            clinical_item=item,
            reviewer=request.user,
            decision=form.cleaned_data["decision"],
            notes=form.cleaned_data["notes"],
        )
        messages.success(request, "審核決策已記錄。 Review decision recorded.")
        return redirect("cds_core:review_item_detail", pk=item.pk)

    messages.error(request, "審核決策未儲存。 Review decision was not saved.")
    detail = build_review_item_detail(item)
    return render(
        request,
        "cds_core/review_item_detail.html",
        {
            "detail": detail,
            "decision_form": form,
            "source_link_form": ClinicalItemSourceLinkForm(item=item),
            "safety_copy": ITEM_REVIEW_SAFETY_COPY,
        },
    )
