from django.test import TestCase
from django.urls import reverse

from cds_core.differential_catalog import CONDITIONS, SOURCES


class GeneralDifferentialUiTests(TestCase):
    fixtures = [
        "headache_mvp.json",
        "chest_pain_mvp.json",
        "abdominal_pain_mvp.json",
        "dyspnea_mvp.json",
    ]

    def test_dashboard_links_to_general_differential_workbench(self):
        response = self.client.get(reverse("cds_core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "通用鑑別 / General differential")
        self.assertContains(response, reverse("cds_core:general_differential"))

    def test_general_differential_page_shows_stepwise_workflow_and_limits(self):
        response = self.client.get(reverse("cds_core:general_differential"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-compact-differential-layout="true"')
        self.assertContains(response, 'data-differential-workbench="true"')
        self.assertContains(response, 'data-differential-form="true"')
        self.assertContains(response, 'data-differential-submit-button="true"')
        self.assertContains(response, 'data-differential-submit-status="idle"')
        self.assertContains(response, 'data-differential-selected-summary="true"')
        self.assertContains(response, 'data-differential-results-panel="true"')
        self.assertContains(response, 'data-step="safety"')
        self.assertContains(response, 'data-step="findings"')
        self.assertContains(response, 'data-step="results"')
        self.assertContains(response, 'data-step-command-bar="true"')
        self.assertContains(response, 'href="#case-input"')
        self.assertContains(response, 'href="#finding-selection"')
        self.assertContains(response, 'href="#reference-results"')
        self.assertContains(response, 'href="#catalog-governance"')
        self.assertContains(response, 'id="case-input"')
        self.assertContains(response, 'id="finding-selection"')
        self.assertContains(response, 'id="reference-results"')
        self.assertContains(response, 'id="catalog-governance"')
        self.assertContains(response, "通用鑑別工作台 / General Differential Workbench")
        self.assertContains(response, "下一步 / Next step")
        self.assertContains(response, "不包含病人識別資料")
        self.assertContains(response, "starter catalog")
        self.assertContains(response, "Runtime source: packaged reviewed catalog data")
        self.assertContains(response, f"{len(CONDITIONS)} conditions")
        self.assertContains(response, f"{len(SOURCES)} sources")
        self.assertContains(response, "<summary>")
        self.assertContains(response, 'data-finding-library-drawer="true"')
        self.assertContains(response, 'data-finding-library-summary="true"')
        self.assertContains(response, 'data-finding-library-container="true"')
        self.assertContains(response, 'data-finding-library-placeholder="true"')
        self.assertContains(response, 'data-finding-library-url="/differential/findings/"')
        self.assertContains(response, "initializeFindingFilters")
        self.assertContains(response, "initializeFindingLibraryLoader")
        self.assertContains(response, "initializeFindingPresets")
        self.assertContains(response, "initializeAddFindingShortcuts")
        self.assertContains(response, "initializeResultFocusToolbar")
        self.assertContains(response, "initializeGeneralDifferentialFetchSubmit")
        self.assertContains(response, "replaceDifferentialWorkspaceSections")
        self.assertContains(response, "setDifferentialResultsRefreshing")
        self.assertContains(response, "captureDifferentialReviewPosition")
        self.assertContains(response, "restoreDifferentialReviewPosition")
        self.assertContains(response, "X-Differential-Submit")
        self.assertContains(response, "findingMatchesQuery")
        self.assertContains(response, "termMatchesSearchIndex")
        self.assertContains(response, "findingQueryMode")
        self.assertContains(response, ".finding-option[hidden]")
        self.assertContains(response, 'class="compact-governance"')
        self.assertContains(response, "Catalog governance")
        self.assertContains(response, "0 blocking issues")
        self.assertContains(response, "Convert static catalog to reviewed data import")
        self.assertContains(response, "export_general_differential_review_seed")
        self.assertContains(response, "validate_general_differential_review_seed")
        self.assertContains(response, "export_general_differential_batch_template")
        self.assertNotContains(response, 'class="finding-group"')
        self.assertNotContains(response, 'data-finding-filter-form="true"')
        self.assertNotContains(response, 'data-finding-option="true"')
        self.assertNotContains(response, 'data-finding-search-index="chest pain')
        self.assertNotContains(response, "Recent cancer treatment")
        self.assertNotContains(response, "Easy bruising or bleeding")
        self.assertNotContains(response, "Chest pain / 胸痛")

    def test_repeated_ajax_submit_keeps_results_visible_with_inline_status(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "chest pain dyspnea",
                "findings": ["chest_pain", "dyspnea"],
                "clinician_notes": "",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_DIFFERENTIAL_SUBMIT="1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-differential-results-panel="true"')
        self.assertContains(response, 'data-differential-results-refresh-state="idle"')
        self.assertContains(response, 'data-differential-results-status="idle"')
        self.assertContains(response, 'data-differential-results-body="true"')
        self.assertContains(response, 'data-candidate-scan-table="true"')
        self.assertContains(response, "setDifferentialResultsRefreshing")
        self.assertContains(response, "captureDifferentialReviewPosition")
        self.assertContains(response, "restoreDifferentialReviewPosition")
        self.assertContains(response, "initializeAddFindingShortcuts")
        self.assertContains(response, "initializeResultFocusToolbar")
        self.assertContains(response, "keepReviewPosition")
        self.assertContains(response, "Updating results")
        self.assertContains(response, "setDifferentialResultsRefreshing(main, true")

    def test_posted_results_start_with_case_pathway_before_details(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-case-pathway="true"')
        self.assertContains(response, 'data-compact-decision-board="true"')
        self.assertContains(response, 'data-case-pathway-step="safety_gate"')
        self.assertContains(response, 'data-case-pathway-current="true"')
        self.assertContains(response, 'data-compact-step-summary="true"')
        self.assertContains(response, 'data-case-pathway-step-detail="true"')
        self.assertContains(response, 'data-progressive-detail-drawer="command-center"')
        self.assertContains(response, "下一步決策板 / Next-step decision board")
        self.assertContains(response, "Follow these steps")
        self.assertLess(
            content.index('data-case-pathway="true"'),
            content.index('data-next-step-command-center="true"'),
        )
        self.assertLess(
            content.index('data-case-pathway="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_results_start_with_current_action_plan(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-current-action-plan="true"')
        self.assertContains(response, 'data-current-action-step="ask_missing_finding"')
        self.assertContains(response, 'data-current-action-command="true"')
        self.assertContains(response, 'data-current-action-jump="true"')
        self.assertContains(response, 'data-add-finding-shortcut="true"')
        self.assertContains(response, 'data-finding-id="hemodynamic_instability"')
        self.assertContains(response, 'data-current-action-steps="true"')
        self.assertContains(response, 'data-current-action-step-item="minimum_data"')
        self.assertContains(response, 'data-current-action-status="current"')
        self.assertContains(response, "現在先做 / Now do this")
        self.assertContains(response, "Ask this gap now")
        self.assertContains(response, "Ask next: Hemodynamic instability")
        self.assertContains(response, "This is a clinician reference step")
        self.assertLess(
            content.index('data-current-action-plan="true"'),
            content.index('data-case-pathway="true"'),
        )
        self.assertLess(
            content.index('data-current-action-plan="true"'),
            content.index('data-candidate-comparison-panel="true"'),
        )
        self.assertLess(
            content.index('data-current-action-plan="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_results_show_focus_modes_for_stepwise_review(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-result-focus-toolbar="true"')
        self.assertContains(response, 'data-result-focus-default="next"')
        self.assertContains(response, 'data-result-focus-control="true"')
        self.assertContains(response, 'data-result-focus-mode="next"')
        self.assertContains(response, 'data-result-focus-mode="compare"')
        self.assertContains(response, 'data-result-focus-mode="sources"')
        self.assertContains(response, 'data-result-focus-mode="all"')
        self.assertContains(response, 'aria-pressed="true">下一步 / Next')
        self.assertContains(response, "比較 / Compare")
        self.assertContains(response, "來源 / Sources")
        self.assertContains(response, "完整 / All")
        self.assertContains(response, 'data-result-focus-section="next all"')
        self.assertContains(response, 'data-result-focus-section="next compare all"')
        self.assertContains(response, 'data-result-focus-section="compare all"')
        self.assertContains(response, 'data-result-focus-section="sources compare all"')
        self.assertContains(response, 'data-result-focus-section="sources all"')
        self.assertContains(response, "initializeResultFocusToolbar")
        self.assertContains(response, "applyFocusMode")
        self.assertNotIn('hidden data-result-focus-section="compare all"', content)
        self.assertLess(
            content.index('data-result-focus-toolbar="true"'),
            content.index('data-current-action-plan="true"'),
        )
        self.assertLess(
            content.index('data-result-focus-toolbar="true"'),
            content.index('data-candidate-comparison-panel="true"'),
        )
        self.assertLess(
            content.index('data-result-focus-toolbar="true"'),
            content.index('data-source-provenance-panel="true"'),
        )

    def test_posted_results_show_candidate_comparison_before_detail_drawers(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-candidate-comparison-panel="true"')
        self.assertContains(
            response,
            'data-candidate-comparison-row="acute_coronary_syndrome"',
        )
        self.assertContains(response, 'data-comparison-support="true"')
        self.assertContains(response, 'data-comparison-against="true"')
        self.assertContains(response, 'data-comparison-next-question="true"')
        self.assertContains(response, 'data-candidate-comparison-caution="true"')
        self.assertContains(response, "Supports")
        self.assertContains(response, "Against or gap")
        self.assertContains(response, "Next question")
        self.assertContains(response, "Chest pain")
        self.assertContains(response, "Arm or jaw radiation")
        self.assertContains(
            response,
            "No negative findings entered; absence of a checkbox is not exclusion",
        )
        self.assertContains(
            response,
            "absent negative findings do not rule out disease",
        )
        self.assertContains(response, "ECG")
        self.assertLess(
            content.index('data-case-pathway="true"'),
            content.index('data-candidate-comparison-panel="true"'),
        )
        self.assertLess(
            content.index('data-candidate-comparison-panel="true"'),
            content.index('data-progressive-detail-drawer="command-center"'),
        )
        self.assertLess(
            content.index('data-candidate-comparison-panel="true"'),
            content.index('data-source-provenance-panel="true"'),
        )
        self.assertLess(
            content.index('data-candidate-comparison-panel="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_results_show_intake_gap_tracker_as_next_step(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-intake-gap-tracker="true"')
        self.assertContains(response, 'data-intake-gap-priority="true"')
        self.assertContains(response, 'data-intake-gap-primary-next="true"')
        self.assertContains(
            response,
            'data-intake-gap-row="acute_coronary_syndrome"',
        )
        self.assertContains(response, 'data-intake-gap-known="true"')
        self.assertContains(response, 'data-intake-gap-missing="true"')
        self.assertContains(response, 'data-intake-gap-next-step="true"')
        self.assertContains(response, "Intake gap tracker")
        self.assertContains(response, "Ask these next")
        self.assertContains(response, "Already entered")
        self.assertContains(response, "Missing data")
        self.assertContains(response, "Hemodynamic instability")
        self.assertContains(response, "Syncope")
        self.assertContains(response, "Ask next: Hemodynamic instability")
        self.assertContains(response, "not a negative finding or exclusion")
        self.assertLess(
            content.index('data-candidate-comparison-panel="true"'),
            content.index('data-intake-gap-tracker="true"'),
        )
        self.assertLess(
            content.index('data-intake-gap-tracker="true"'),
            content.index('data-progressive-detail-drawer="command-center"'),
        )
        self.assertLess(
            content.index('data-intake-gap-tracker="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_general_differential_page_keeps_replaceable_fetch_sections(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {"query": "pertussis", "clinician_notes": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_DIFFERENTIAL_SUBMIT="1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-differential-workbench="true"')
        self.assertContains(response, 'data-differential-selected-summary="true"')
        self.assertContains(response, 'data-differential-results-panel="true"')
        self.assertContains(response, 'data-workflow-stepper="true"')
        self.assertContains(response, "Pertussis")
        self.assertContains(response, "CDC - Symptoms of Whooping Cough")

    def test_general_differential_page_collapses_full_finding_library_by_default(self):
        response = self.client.get(reverse("cds_core:general_differential"))

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-finding-library-drawer="true"')
        self.assertContains(response, 'data-finding-library-summary="true"')
        self.assertContains(response, 'data-finding-library-container="true"')
        self.assertContains(response, 'data-finding-library-url="/differential/findings/"')
        self.assertContains(response, "Open full finding library")
        self.assertLess(
            content.index('data-finding-library-summary="true"'),
            content.index('data-finding-library-container="true"'),
        )
        self.assertNotIn('data-finding-filter-form="true"', content)

    def test_general_differential_page_shows_catalog_quick_entry_shortcuts(self):
        response = self.client.get(reverse("cds_core:general_differential"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-catalog-quick-entry="true"')
        self.assertContains(response, 'data-catalog-system-entry="genetic-congenital"')
        self.assertContains(response, 'data-catalog-system-entry="blood-immune"')
        self.assertContains(response, 'data-catalog-system-entry="endocrine-metabolic"')
        self.assertContains(response, 'data-catalog-system-entry="neurodevelopmental"')
        self.assertContains(response, 'data-catalog-quick-query="true"')
        self.assertContains(response, "Genetic / congenital")
        self.assertContains(response, "Blood / immune")

    def test_general_differential_findings_endpoint_renders_full_library(self):
        response = self.client.get("/differential/findings/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-finding-filter-form="true"')
        self.assertContains(response, 'data-finding-filter-input="true"')
        self.assertContains(response, 'data-selected-only-toggle="true"')
        self.assertContains(response, 'data-clear-finding-filter="true"')
        self.assertContains(response, 'data-finding-match-count="true"')
        self.assertContains(response, 'data-no-finding-matches="true"')
        self.assertContains(response, 'data-complaint-preset-bar="true"')
        self.assertContains(response, 'data-finding-preset="true"')
        self.assertContains(response, 'data-finding-preset-query="cardiopulmonary"')
        self.assertContains(response, 'data-finding-preset-mode="any"')
        self.assertContains(response, 'data-active-preset-label="true"')
        self.assertContains(response, 'data-finding-group-default-open="true"')
        self.assertContains(response, 'class="finding-group"')
        self.assertContains(response, 'data-finding-option="true"')
        self.assertContains(response, 'data-finding-search-index="chest pain')
        self.assertContains(response, "chest_pain acs mi heart attack")
        self.assertContains(response, "neurologic_deficit stroke tia cva")
        self.assertContains(response, "先選主訴 / Start by complaint")
        self.assertContains(response, "快速篩選 findings / Filter findings")
        self.assertContains(response, "Recent cancer treatment")
        self.assertContains(response, "Easy bruising or bleeding")
        self.assertContains(response, "Chest pain / 胸痛")
        self.assertContains(response, "Neurologic deficit / 神經學缺損")

    def test_general_differential_findings_endpoint_preserves_selected_findings(self):
        response = self.client.get(
            "/differential/findings/",
            {"selected": ["chest_pain", "dyspnea"]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="findings" value="chest_pain" checked')
        self.assertContains(response, 'name="findings" value="dyspnea" checked')
        self.assertContains(response, 'data-finding-selected="true"', count=2)

    def test_posted_findings_put_results_before_catalog_governance(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertLess(content.index('data-result-card="true"'), content.index("Catalog governance"))
        self.assertContains(response, 'data-ask-next-drawer="true"')
        self.assertContains(response, "下一步問題 / Ask-next prompts")
        self.assertContains(response, "已選 findings / Selected findings")
        self.assertContains(response, 'data-selected-finding-hidden="true"')
        self.assertContains(response, 'name="findings" value="chest_pain"')
        self.assertNotContains(response, 'data-finding-option="true"')

    def test_posted_findings_show_top_results_before_secondary_candidates(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-primary-result-list="true"')
        self.assertContains(response, 'data-secondary-result-drawer="true"')
        self.assertContains(response, "More candidates")
        self.assertLess(
            content.index('data-primary-result-list="true"'),
            content.index('data-secondary-result-drawer="true"'),
        )

    def test_posted_findings_show_ranked_conditions_ask_next_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "急性冠心症")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertContains(response, "emergent")
        self.assertContains(response, "下一步要問 / Ask next")
        self.assertContains(response, "American Heart Association")
        self.assertContains(response, "starter catalog")
        self.assertContains(response, f"{len(CONDITIONS)} conditions")
        self.assertContains(response, f"{len(SOURCES)} sources")
        self.assertContains(response, "不是 diagnosis order")

    def test_posted_findings_show_action_checklist_before_condition_cards(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-action-checklist="true"')
        self.assertContains(response, "下一步行動 / Action checklist")
        self.assertContains(response, "安全再確認 / Safety check")
        self.assertContains(response, "補資料 / Data to add")
        self.assertContains(response, "看來源 / Source review")
        self.assertContains(response, "Re-run")
        self.assertLess(
            content.index('data-action-checklist="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_findings_show_case_action_queue_before_long_results(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-case-action-queue="true"')
        self.assertContains(response, 'data-action-queue-current="true"')
        self.assertContains(response, 'data-action-queue-link="top-candidates"')
        self.assertContains(response, 'data-action-queue-link="coverage"')
        self.assertContains(response, "Do now")
        self.assertContains(response, "Top candidates")
        self.assertContains(response, 'id="top-candidates"')
        self.assertLess(
            content.index('data-case-action-queue="true"'),
            content.index('data-guided-follow-up="true"'),
        )
        self.assertLess(
            content.index('data-case-action-queue="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_findings_show_scan_first_results_brief(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-results-brief="true"')
        self.assertContains(response, 'data-results-brief-card="top-candidate"')
        self.assertContains(response, 'data-results-brief-card="next-step"')
        self.assertContains(response, 'data-results-brief-card="hidden-count"')
        self.assertContains(response, "Highest ranked")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertContains(response, "Safety first")
        self.assertContains(response, "More hidden")
        self.assertLess(
            content.index('data-results-brief="true"'),
            content.index('data-case-action-queue="true"'),
        )
        self.assertLess(
            content.index('data-results-brief="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_findings_show_next_step_summary_strip_before_long_sections(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-next-step-summary-strip="true"')
        self.assertContains(response, 'data-next-step-summary-item="do-now"')
        self.assertContains(response, 'data-next-step-summary-item="top-candidate"')
        self.assertContains(response, 'data-next-step-summary-item="ask-next"')
        self.assertContains(response, 'data-next-step-summary-item="sources"')
        self.assertContains(response, "Do now")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertLess(
            content.index('data-next-step-summary-strip="true"'),
            content.index('data-results-brief="true"'),
        )
        self.assertLess(
            content.index('data-next-step-summary-strip="true"'),
            content.index('data-case-action-queue="true"'),
        )
        self.assertLess(
            content.index('data-next-step-summary-strip="true"'),
            content.index('data-guided-follow-up="true"'),
        )
        self.assertLess(
            content.index('data-next-step-summary-strip="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_results_start_with_concise_next_action_summary(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-concise-result-summary="true"')
        self.assertContains(response, 'data-primary-next-action="true"')
        self.assertContains(response, 'data-danger-check-list="true"')
        self.assertContains(response, 'data-concise-top-candidate="true"')
        self.assertContains(response, "下一步 / Next action")
        self.assertContains(response, "Danger checks")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertLess(
            content.index('data-concise-result-summary="true"'),
            content.index('data-next-step-summary-strip="true"'),
        )
        self.assertLess(
            content.index('data-concise-result-summary="true"'),
            content.index('data-source-provenance-panel="true"'),
        )
        self.assertLess(
            content.index('data-concise-result-summary="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_results_show_complaint_guided_intake_before_long_sections(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-complaint-guided-intake="true"')
        self.assertContains(response, 'data-complaint-intake-card="cardiopulmonary"')
        self.assertContains(response, 'data-complaint-intake-minimum-data="true"')
        self.assertContains(response, 'data-complaint-intake-shortcut="chest_pain"')
        self.assertContains(response, 'data-complaint-intake-shortcut="dyspnea"')
        self.assertContains(response, "主訴導向 / Complaint-guided intake")
        self.assertContains(response, "Chest pain or dyspnea")
        self.assertLess(
            content.index('data-complaint-guided-intake="true"'),
            content.index('data-candidate-scan-table="true"'),
        )
        self.assertLess(
            content.index('data-complaint-guided-intake="true"'),
            content.index('data-source-provenance-panel="true"'),
        )
        self.assertLess(
            content.index('data-complaint-guided-intake="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_results_show_command_center_before_long_sections(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-next-step-command-center="true"')
        self.assertContains(response, 'data-command-center-card="safety_gate"')
        self.assertContains(response, 'data-command-center-card="complaint_minimum_data"')
        self.assertContains(response, 'data-command-center-card="leading_candidate_review"')
        self.assertContains(response, 'data-command-center-card="source_review"')
        self.assertContains(response, "下一步指令中心 / Next-step command center")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-stepwise-next-rail="true"'),
        )
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-patient-workflow="true"'),
        )
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-complaint-guided-intake="true"'),
        )
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-candidate-scan-table="true"'),
        )
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-source-provenance-panel="true"'),
        )
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_results_collapse_long_sections_into_progressive_drawers(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-next-step-command-center="true"')
        self.assertContains(response, 'data-progressive-detail-drawer="clinical-context"')
        self.assertContains(response, 'data-progressive-detail-drawer="workflow"')
        self.assertContains(response, 'data-progressive-detail-drawer="evidence"')
        self.assertContains(response, "Clinical context, groups, and detailed next steps")
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-progressive-detail-drawer="workflow"'),
        )
        self.assertLess(
            content.index('data-progressive-detail-drawer="workflow"'),
            content.index('data-stepwise-next-rail="true"'),
        )
        self.assertLess(
            content.index('data-progressive-detail-drawer="clinical-context"'),
            content.index('data-concise-result-summary="true"'),
        )
        self.assertLess(
            content.index('data-progressive-detail-drawer="clinical-context"'),
            content.index('data-result-groups="true"'),
        )
        self.assertLess(
            content.index('data-progressive-detail-drawer="clinical-context"'),
            content.index('data-progressive-detail-drawer="evidence"'),
        )
        self.assertLess(
            content.index('data-progressive-detail-drawer="evidence"'),
            content.index('data-candidate-scan-table="true"'),
        )
        self.assertLess(
            content.index('data-progressive-detail-drawer="evidence"'),
            content.index('data-source-provenance-panel="true"'),
        )

    def test_posted_results_show_priority_lane_before_progressive_drawers(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-priority-lane="critical_first"')
        self.assertContains(response, "Priority lane")
        self.assertLess(
            content.index('data-next-step-command-center="true"'),
            content.index('data-priority-lane="critical_first"'),
        )
        self.assertLess(
            content.index('data-priority-lane="critical_first"'),
            content.index('data-progressive-detail-drawer="workflow"'),
        )
        self.assertLess(
            content.index('data-priority-lane="critical_first"'),
            content.index('data-progressive-detail-drawer="evidence"'),
        )

    def test_posted_results_show_first_screen_brief_before_progressive_drawers(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-first-screen-brief="true"')
        self.assertContains(response, "First-screen next steps")
        self.assertLess(
            content.index('data-priority-lane="critical_first"'),
            content.index('data-first-screen-brief="true"'),
        )
        self.assertLess(
            content.index('data-first-screen-brief="true"'),
            content.index('data-progressive-detail-drawer="workflow"'),
        )
        self.assertLess(
            content.index('data-first-screen-brief="true"'),
            content.index('data-progressive-detail-drawer="evidence"'),
        )

    def test_posted_findings_show_result_groups_before_long_candidate_cards(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-result-groups="true"')
        self.assertContains(response, 'data-result-group="emergent"')
        self.assertContains(response, 'data-result-group-candidate="acute_coronary_syndrome"')
        self.assertContains(response, "Candidate groups")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertLess(
            content.index('data-result-groups="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_findings_show_candidate_scan_table_before_collapsed_cards(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-candidate-scan-table="true"')
        self.assertContains(response, 'data-candidate-scan-row="acute_coronary_syndrome"')
        self.assertContains(response, 'data-primary-result-drawer="true"')
        self.assertContains(response, "Open detailed candidate cards")
        self.assertLess(
            content.index('data-candidate-scan-table="true"'),
            content.index('data-primary-result-drawer="true"'),
        )
        self.assertLess(
            content.index('data-primary-result-drawer="true"'),
            content.index('data-result-card="true"'),
        )

    def test_candidate_scan_table_shows_source_shortcuts_and_mobile_density_markers(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-candidate-scan-table="true"')
        self.assertContains(response, 'data-candidate-scan-density="compact"')
        self.assertContains(response, 'data-candidate-source-shortcut="true"')
        self.assertContains(response, 'data-candidate-source-count="true"')
        self.assertContains(response, "Review sources")
        self.assertLess(
            content.index('data-candidate-source-shortcut="true"'),
            content.index('data-primary-result-drawer="true"'),
        )

    def test_candidate_scan_table_shows_quick_urgency_and_system_filters(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-candidate-scan-filter-panel="true"')
        self.assertContains(response, 'data-candidate-scan-filter-control="true"')
        self.assertContains(response, 'data-candidate-scan-filter-type="urgency"')
        self.assertContains(response, 'data-candidate-scan-filter-type="system"')
        self.assertContains(response, 'data-candidate-scan-row="acute_coronary_syndrome"')
        self.assertContains(response, 'data-candidate-scan-urgency="emergent"')
        self.assertContains(response, 'data-candidate-scan-system=')
        self.assertContains(response, 'data-candidate-scan-empty="true"')
        self.assertContains(response, "Filter scan")
        self.assertContains(response, "initializeCandidateScanFilters")
        self.assertLess(
            content.index('data-candidate-scan-filter-panel="true"'),
            content.index('data-candidate-scan-row="acute_coronary_syndrome"'),
        )
        self.assertLess(
            content.index('data-candidate-scan-table="true"'),
            content.index('data-primary-result-drawer="true"'),
        )

    def test_posted_results_show_filterable_source_provenance_before_candidate_cards(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-source-provenance-panel="true"')
        self.assertContains(response, 'data-source-provenance-filter="true"')
        self.assertContains(response, 'data-source-provenance-row="true"')
        self.assertContains(response, 'data-source-provenance-count="true"')
        self.assertContains(response, 'data-source-publisher=')
        self.assertContains(response, "Source provenance")
        self.assertContains(response, "initializeSourceProvenanceFilters")
        self.assertLess(
            content.index('data-candidate-scan-table="true"'),
            content.index('data-source-provenance-panel="true"'),
        )
        self.assertLess(
            content.index('data-source-provenance-panel="true"'),
            content.index('data-primary-result-drawer="true"'),
        )

    def test_posted_results_show_filterable_secondary_candidate_drawer(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-secondary-result-drawer="true"')
        self.assertContains(response, 'data-secondary-filter-panel="true"')
        self.assertContains(response, 'data-secondary-filter-control="true"')
        self.assertContains(response, 'data-secondary-filter-type="urgency"')
        self.assertContains(response, 'data-secondary-filter-type="system"')
        self.assertContains(response, 'data-secondary-filter-row="true"')
        self.assertContains(response, 'data-secondary-filter-empty="true"')
        self.assertContains(response, "Filter more candidates")
        self.assertContains(response, "initializeSecondaryCandidateFilters")
        self.assertLess(
            content.index('data-primary-result-drawer="true"'),
            content.index('data-secondary-result-drawer="true"'),
        )
        self.assertLess(
            content.index('data-secondary-filter-panel="true"'),
            content.index('data-secondary-filter-row="true"'),
        )

    def test_posted_findings_show_compact_step_rail_before_long_workflow(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-stepwise-next-rail="true"')
        self.assertContains(response, 'data-stepwise-next-rail-item="true"')
        self.assertContains(response, "Follow in order")
        self.assertLess(
            content.index('data-stepwise-next-rail="true"'),
            content.index('data-patient-workflow="true"'),
        )
        self.assertLess(
            content.index('data-stepwise-next-rail="true"'),
            content.index('data-candidate-scan-table="true"'),
        )

    def test_posted_result_cards_show_primary_action_before_full_action_drawer(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-result-action-compact="true"')
        self.assertContains(response, 'data-result-primary-action="true"')
        self.assertContains(response, 'data-result-actions-detail="true"')
        self.assertContains(response, "Primary action")
        self.assertContains(response, "More actions")
        self.assertLess(
            content.index('data-result-primary-action="true"'),
            content.index('data-result-actions-detail="true"'),
        )
        self.assertLess(
            content.index('data-result-actions-detail="true"'),
            content.index('data-result-detail="true"'),
        )

    def test_posted_findings_show_step_by_step_patient_workflow_before_long_results(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "chest_pain",
                    "dyspnea",
                    "diaphoresis",
                    "radiating_arm_jaw_pain",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-patient-workflow="true"')
        self.assertContains(response, 'data-patient-workflow-step="rule_out_immediate_danger"')
        self.assertContains(response, 'data-patient-workflow-step="complete_missing_context"')
        self.assertContains(response, 'data-patient-workflow-step="compare_leading_candidates"')
        self.assertContains(response, 'data-patient-workflow-step="handoff_or_rerun"')
        self.assertContains(response, 'data-patient-workflow-handoff="true"')
        self.assertContains(response, "Step-by-step patient workflow")
        self.assertContains(response, "Rule out immediate danger")
        self.assertContains(response, "Complete missing context")
        self.assertContains(response, "Compare leading candidates")
        self.assertContains(response, "Handoff or re-run")
        self.assertContains(response, "Acute coronary syndrome")
        self.assertLess(
            content.index('data-patient-workflow="true"'),
            content.index('data-result-card="true"'),
        )

    def test_sparse_post_shows_minimum_data_checklist_before_empty_state(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-patient-workflow="true"')
        self.assertContains(response, 'data-workflow-minimum-data="true"')
        self.assertContains(response, 'data-minimum-data-item="chief_complaint_onset"')
        self.assertContains(response, 'data-minimum-data-item="vitals_stability"')
        self.assertContains(response, 'data-minimum-data-item="red_flags"')
        self.assertContains(response, 'data-minimum-data-item="pertinent_context"')
        self.assertContains(response, 'data-minimum-data-item="rerun_with_findings"')
        self.assertContains(response, "Minimum data to collect")
        self.assertContains(response, "Not enough structured data")
        self.assertLess(
            content.index('data-workflow-minimum-data="true"'),
            content.index("Not enough findings to rank yet"),
        )

    def test_posted_findings_use_stepwise_compact_result_layout(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "ruq_pain",
                    "fever",
                    "vomiting",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-workflow-stepper="true"')
        self.assertContains(response, 'data-workflow-step="case"')
        self.assertContains(response, 'data-workflow-step="next"')
        self.assertContains(response, 'data-workflow-step="differential"')
        self.assertContains(response, 'data-primary-next-step="true"')
        self.assertContains(response, 'data-result-summary="true"')
        self.assertContains(response, 'data-result-detail="true"')
        self.assertContains(response, 'data-source-detail="true"')
        self.assertLess(
            content.index('data-primary-next-step="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_findings_show_guided_follow_up_before_result_cards(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "abdominal_pain",
                    "fever",
                    "vomiting",
                ],
                "clinician_notes": "",
            },
        )

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-guided-follow-up="true"')
        self.assertContains(response, 'data-guided-step="safety"')
        self.assertContains(response, 'data-guided-step="context"')
        self.assertContains(response, 'data-guided-step="top_differential"')
        self.assertContains(response, 'data-guided-step="rerun"')
        self.assertContains(response, 'data-guided-follow-up-body="true"')
        self.assertContains(response, "Guided follow-up")
        self.assertContains(response, "Abdominal or urinary context")
        self.assertLess(
            content.index('data-guided-follow-up="true"'),
            content.index('data-guided-follow-up-body="true"'),
        )
        self.assertLess(
            content.index('data-guided-follow-up="true"'),
            content.index('data-result-card="true"'),
        )

    def test_posted_gynecologic_findings_show_pid_toa_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "pelvic_pain",
                    "fever",
                    "vaginal_discharge",
                    "cervical_motion_tenderness",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "骨盆腔發炎性疾病")
        self.assertContains(response, "Pelvic inflammatory disease")
        self.assertContains(response, "輸卵管卵巢膿瘍")
        self.assertContains(response, "Tubo-ovarian abscess")
        self.assertContains(response, "下一步要問 / Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "CDC")

    def test_posted_mental_health_findings_show_safety_and_psychosis_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "suicidal_ideation",
                    "self_harm_behavior",
                    "hallucinations_delusions",
                    "severe_agitation",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "自殺或自傷風險")
        self.assertContains(response, "Suicide or self-harm risk")
        self.assertContains(response, "急性精神病性症狀")
        self.assertContains(response, "Acute psychosis")
        self.assertContains(response, "下一步要問 / Ask next")
        self.assertContains(response, "NIMH")
        self.assertContains(response, "NICE")

    def test_posted_skin_findings_show_sjs_ten_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "rash",
                    "mucosal_lesions",
                    "skin_sloughing_or_blistering",
                    "new_medication_exposure",
                    "fever",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "史蒂文斯-強森症候群")
        self.assertContains(response, "Stevens-Johnson syndrome")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "DermNet")

    def test_posted_cardiovascular_findings_show_pericarditis_limb_ischemia_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "positional_pleuritic_chest_pain",
                    "acute_limb_pain_pallor_pulselessness",
                    "severe_pain",
                    "neurologic_deficit",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acute pericarditis or myocarditis")
        self.assertContains(response, "Acute limb ischemia")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "Society for Vascular Surgery")

    def test_posted_gastrointestinal_findings_show_mesenteric_ischemia_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "pain_out_of_proportion_to_exam",
                    "abdominal_pain",
                    "severe_pain",
                    "vomiting",
                    "bloody_diarrhea",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acute mesenteric ischemia")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "World Society of Emergency Surgery")

    def test_posted_musculoskeletal_emergency_findings_show_joint_and_compartment_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "acute_hot_swollen_joint",
                    "tense_compartment_or_pain_with_passive_stretch",
                    "recent_trauma",
                    "severe_pain",
                    "fever",
                    "neurologic_deficit",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Septic arthritis")
        self.assertContains(response, "Acute compartment syndrome")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")

    def test_posted_eye_and_obstetric_findings_show_orbital_and_preeclampsia_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "painful_eye_movement_or_proptosis",
                    "eye_pain_redness",
                    "fever",
                    "visual_disturbance",
                    "pregnancy_possible",
                    "preeclampsia_warning_features",
                    "ruq_pain",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Orbital cellulitis")
        self.assertContains(response, "Preeclampsia or eclampsia")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "ACOG")
        self.assertContains(response, "WHO")

    def test_posted_ent_airway_findings_show_deep_neck_and_airway_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "severe_sore_throat_drooling_or_stridor",
                    "trismus_muffled_voice_uvula_deviation",
                    "neck_stiffness_swelling_dysphagia",
                    "fever",
                    "respiratory_distress",
                    "severe_pain",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Epiglottitis")
        self.assertContains(response, "Peritonsillar abscess")
        self.assertContains(response, "Retropharyngeal abscess")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "MSD Manuals Professional")

    def test_posted_pediatric_metabolic_findings_show_hhs_intussusception_and_kawasaki(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "severe_hyperglycemia_dehydration_confusion",
                    "extreme_thirst_polyuria",
                    "altered_mental_status",
                    "intermittent_colicky_abdominal_pain_or_currant_jelly_stool",
                    "vomiting",
                    "persistent_fever_mucocutaneous_changes",
                    "fever",
                    "rash",
                    "eye_pain_redness",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hyperosmolar hyperglycemic state")
        self.assertContains(response, "Intussusception")
        self.assertContains(response, "Kawasaki disease")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "Merck Manual Professional")
        self.assertContains(response, "CDC")

    def test_posted_toxicology_findings_show_carbon_monoxide_and_sources(self):
        response = self.client.post(
            reverse("cds_core:general_differential"),
            {
                "query": "",
                "findings": [
                    "carbon_monoxide_or_combustion_exposure",
                    "multiple_people_same_symptoms",
                    "altered_mental_status",
                    "syncope",
                    "vomiting",
                ],
                "clinician_notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carbon monoxide poisoning")
        self.assertContains(response, "emergent")
        self.assertContains(response, "Ask next")
        self.assertContains(response, "CDC")
        self.assertContains(response, "Merck Manual Professional")
