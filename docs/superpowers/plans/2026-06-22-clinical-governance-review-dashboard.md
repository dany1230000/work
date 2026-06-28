# Clinical Governance Review Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Chinese-first, English-secondary clinical governance dashboard that lets reviewers see content status, source coverage, review-due items, recent audit activity, and case-scenario validation for the professional MVP.

**Architecture:** Keep this phase as a governance/read-only layer. Add one focused service module that aggregates existing models, one route/template for the dashboard, and tests that prove the dashboard is source-backed, bilingual, and aligned with the current 13-item / 8-case fixture baseline.

**Tech Stack:** Django 5.2, SQLite local MVP database, Django TestCase, existing `headache_mvp` fixture.

---

## Scope

中文主軸：下一階段先做「臨床內容治理 / Clinical Governance」，不要先擴充更多主訴或診斷。這個階段要讓專業版看得出內容來源、審核狀態、案例驗證結果與 audit trail，而不是只是一個表單。

English secondary: Build reviewer-facing governance visibility before expanding clinical coverage. The dashboard remains read-only in this phase and does not introduce patient data, live trading, broker integrations, or any TWQuant execution behavior.

## File Map

- Create: `clinical_differential_support/cds_core/governance.py`
  - Aggregates review counts, source gaps, due reviews, case validation rows, and recent audit records.
- Create: `clinical_differential_support/cds_core/tests/test_governance_dashboard.py`
  - Locks the governance service and `/review/` page against fixture-backed expectations.
- Modify: `clinical_differential_support/cds_core/views.py`
  - Adds `review_dashboard`.
- Modify: `clinical_differential_support/cds_core/urls.py`
  - Adds `review/` route named `review_dashboard`.
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
  - Adds navigation to the review dashboard.
- Create: `clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html`
  - Chinese-first dashboard UI.
- Modify: `clinical_differential_support/README.md`
  - Documents the new route and governance purpose.
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`
  - Records implementation and verification evidence.

---

### Task 1: Failing Governance Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_governance_dashboard.py`

- [x] **Step 1: Add the failing service and route tests**

```python
from datetime import date

from django.test import TestCase
from django.urls import reverse

from cds_core.models import ChiefComplaint, ClinicalItem


class GovernanceDashboardTests(TestCase):
    fixtures = ["headache_mvp.json"]

    def test_governance_service_reports_fixture_baseline(self):
        from cds_core.governance import build_review_dashboard

        dashboard = build_review_dashboard(today=date(2026, 6, 22))

        self.assertEqual(dashboard["total_items"], 13)
        self.assertEqual(dashboard["status_counts"]["approved"], 13)
        self.assertEqual(dashboard["source_gap_items"], [])
        self.assertEqual(dashboard["review_due_items"], [])
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
```

- [x] **Step 2: Run the narrow test and confirm it fails for missing implementation**

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_governance_dashboard -v 2
```

Expected before implementation:

```text
FAILED ... ModuleNotFoundError: No module named 'cds_core.governance'
```

or, after `governance.py` exists but before routes are wired:

```text
django.urls.exceptions.NoReverseMatch: Reverse for 'review_dashboard' not found
```

### Task 2: Governance Aggregation Service

**Files:**
- Create: `clinical_differential_support/cds_core/governance.py`

- [x] **Step 1: Implement the read-only governance service**

```python
"""Read-only clinical governance dashboard selectors."""

from datetime import date
from typing import Any

from django.db.models import Count
from django.utils import timezone

from .models import AuditEvent, CaseScenario, ClinicalItem
from .services import evaluate_case_scenario


def build_review_dashboard(today: date | None = None) -> dict[str, Any]:
    current_date = today or timezone.localdate()
    items = ClinicalItem.objects.all().prefetch_related("sources")

    status_counts = {
        status: items.filter(status=status).count()
        for status, _label in ClinicalItem.Status.choices
    }
    source_gap_items = list(
        items.annotate(source_count=Count("sources"))
        .filter(source_count=0)
        .order_by("item_type", "urgency", "title")
    )
    review_due_items = list(
        items.filter(review_due_at__lte=current_date).order_by(
            "review_due_at", "item_type", "urgency", "title"
        )
    )

    return {
        "total_items": items.count(),
        "status_counts": status_counts,
        "source_gap_items": source_gap_items,
        "review_due_items": review_due_items,
        "case_rows": build_case_validation_rows(),
        "recent_audit_events": list(
            AuditEvent.objects.select_related("clinical_item", "actor")[:10]
        ),
    }


def build_case_validation_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scenarios = CaseScenario.objects.filter(active=True).select_related(
        "chief_complaint"
    )
    for scenario in scenarios:
        evaluation = evaluate_case_scenario(scenario)
        expected_outputs = evaluation["expected_outputs"]
        missing_titles = [
            expected["title"]
            for expected in expected_outputs
            if not expected["matched"]
        ]
        rows.append(
            {
                "scenario": scenario,
                "expected_count": len(expected_outputs),
                "matched_count": len(expected_outputs) - len(missing_titles),
                "missing_titles": missing_titles,
                "all_matched": not missing_titles,
            }
        )
    return rows
```

- [x] **Step 2: Run the governance test again**

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_governance_dashboard -v 2
```

Expected at this point: service tests pass, route test still fails with `NoReverseMatch`.

### Task 3: Review Dashboard Route and View

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`

- [x] **Step 1: Add the view**

Add this import and view to `views.py`:

```python
from .governance import build_review_dashboard


def review_dashboard(request):
    dashboard = build_review_dashboard()
    return render(
        request,
        "cds_core/review_dashboard.html",
        {
            "dashboard": dashboard,
            "safety_copy": (
                "臨床內容治理頁僅供合格醫療專業人員審核 MVP 內容、來源與測試案例。"
                "Clinical governance view for qualified medical professionals "
                "to review MVP content, sources, and validation cases."
            ),
        },
    )
```

- [x] **Step 2: Wire the URL**

Add this path to `cds_core/urls.py`:

```python
path("review/", views.review_dashboard, name="review_dashboard"),
```

- [x] **Step 3: Run the route test and confirm it now fails only because the template is missing**

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_governance_dashboard -v 2
```

Expected:

```text
django.template.exceptions.TemplateDoesNotExist: cds_core/review_dashboard.html
```

### Task 4: Chinese-First Dashboard UI

**Files:**
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Create: `clinical_differential_support/cds_core/templates/cds_core/review_dashboard.html`

- [x] **Step 1: Add navigation**

Add the review link next to the existing intake and case links in `base.html`:

```html
<a href="{% url 'cds_core:review_dashboard' %}">臨床內容治理<br><span>Clinical Governance</span></a>
```

- [x] **Step 2: Create the review dashboard template**

```html
{% extends "cds_core/base.html" %}

{% block title %}臨床內容治理 / Clinical Governance{% endblock %}

{% block content %}
<section class="hero">
  <p class="eyebrow">臨床內容治理 / Clinical Governance</p>
  <h1>審核狀態、來源覆蓋與案例驗證</h1>
  <p>{{ safety_copy }}</p>
</section>

<section class="grid metrics">
  <article>
    <span class="metric">{{ dashboard.total_items }}</span>
    <h2>臨床項目</h2>
    <p>Clinical items</p>
  </article>
  <article>
    <span class="metric">{{ dashboard.status_counts.approved }}</span>
    <h2>已核准</h2>
    <p>Approved</p>
  </article>
  <article>
    <span class="metric">{{ dashboard.source_gap_items|length }}</span>
    <h2>來源缺口</h2>
    <p>Source gaps</p>
  </article>
  <article>
    <span class="metric">{{ dashboard.case_rows|length }}</span>
    <h2>案例驗證</h2>
    <p>Case validation</p>
  </article>
</section>

<section class="panel">
  <h2>來源覆蓋 / Source coverage</h2>
  {% if dashboard.source_gap_items %}
    <ul class="review-list">
      {% for item in dashboard.source_gap_items %}
        <li>
          <strong>{{ item.primary_title }}</strong>
          <span>{{ item.secondary_title }}</span>
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>目前沒有缺少來源的臨床項目。No clinical items are missing sources.</p>
  {% endif %}
</section>

<section class="panel">
  <h2>到期審核 / Review due</h2>
  {% if dashboard.review_due_items %}
    <ul class="review-list">
      {% for item in dashboard.review_due_items %}
        <li>
          <strong>{{ item.primary_title }}</strong>
          <span>{{ item.review_due_at }} · {{ item.secondary_title }}</span>
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>目前沒有到期審核項目。No content is currently due for review.</p>
  {% endif %}
</section>

<section class="panel">
  <h2>案例驗證 / Case validation</h2>
  <table>
    <thead>
      <tr>
        <th>案例 / Case</th>
        <th>匹配 / Matched</th>
        <th>狀態 / Status</th>
      </tr>
    </thead>
    <tbody>
      {% for row in dashboard.case_rows %}
        <tr>
          <td>
            <strong>{{ row.scenario.primary_title }}</strong><br>
            <span>{{ row.scenario.secondary_title }}</span>
          </td>
          <td>{{ row.matched_count }} / {{ row.expected_count }}</td>
          <td>
            {% if row.all_matched %}
              通過 / Passed
            {% else %}
              缺少：{{ row.missing_titles|join:", " }} / Missing expected output
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</section>

<section class="panel">
  <h2>最近稽核紀錄 / Recent audit trail</h2>
  {% if dashboard.recent_audit_events %}
    <ul class="review-list">
      {% for event in dashboard.recent_audit_events %}
        <li>
          <strong>{{ event.clinical_item.primary_title }}</strong>
          <span>{{ event.get_event_type_display }} · {{ event.created_at }}</span>
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>目前尚無稽核紀錄。No audit events have been recorded yet.</p>
  {% endif %}
</section>
{% endblock %}
```

- [x] **Step 3: Run the dashboard tests**

Run:

```powershell
py -B clinical_differential_support\manage.py test cds_core.tests.test_governance_dashboard -v 2
```

Expected: all governance dashboard tests pass.

### Task 5: Documentation and Live Verification

**Files:**
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [x] **Step 1: Update README route list**

Add:

```markdown
- `http://127.0.0.1:8000/review/` - 臨床內容治理 / Clinical Governance
```

- [x] **Step 2: Run full app verification**

Run:

```powershell
py -B clinical_differential_support\manage.py test
py -B clinical_differential_support\manage.py check
```

Expected:

```text
OK
System check identified no issues
```

- [x] **Step 3: Start or reuse the local server**

Run:

```powershell
py -B clinical_differential_support\manage.py runserver 127.0.0.1:8000 --noreload
```

If port 8000 is already occupied by the background dev server, keep the existing server and run the HTTP checks instead.

- [x] **Step 4: Verify the live route**

Run:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/review/ -TimeoutSec 10 |
  Select-Object StatusCode,@{Name='HasZh';Expression={$_.Content -like '*臨床內容治理*'}},@{Name='HasEn';Expression={$_.Content -like '*Clinical Governance*'}}
```

Expected:

```text
StatusCode HasZh HasEn
---------- ----- -----
       200  True  True
```

- [x] **Step 5: Record progress**

Append a dated note to `.planning/2026-06-22-clinical-differential-support/progress.md` with:

```markdown
## 2026-06-22 Clinical Governance Plan

- Planned next phase: Chinese-first bilingual clinical governance dashboard.
- Scope remains read-only reviewer visibility; no patient data, no orders, no broker APIs, and no `PAPER_TRADABLE` or `LIVE_TRADABLE` labels.
- Planned route: `/review/`.
- Planned verification: governance dashboard tests, full Django tests, Django check, and live `/review/` HTTP 200 check.
```

## Acceptance Criteria

- `/review/` renders Chinese-first and English-secondary governance copy.
- Dashboard shows total clinical items, approved count, source gaps, review-due items, case validation status, and recent audit events.
- Current fixture baseline remains visible: 13 clinical items, 13 approved items, 5 sources, and at least 8 active case scenarios.
- Source gap list is empty for the current fixture and non-empty when a test creates a review item without sources.
- Case validation rows show all current headache scenarios as matched.
- No diagnosis, treatment order, live trading, broker order API, or credential behavior is added.
- `py -B clinical_differential_support\manage.py test` passes.
- `py -B clinical_differential_support\manage.py check` passes.
- Live `http://127.0.0.1:8000/review/` returns HTTP 200 and contains both `臨床內容治理` and `Clinical Governance`.
