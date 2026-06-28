# Abdominal Pain Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add abdominal pain as the third source-backed clinician-reference chief complaint and advance the next-action workbench to dyspnea.

**Architecture:** Reuse the existing generic rule evaluator and fixture-driven content model. Add one form, one view, one route/template, one fixture, one targeted test file, README/smoke updates, and progress notes.

**Tech Stack:** Django 5.2, SQLite fixtures, server-rendered templates, Python `unittest`, deterministic JSON rules.

---

### Task 1: Abdominal pain tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_abdominal_pain_pathway.py`

- [ ] **Step 1: Write failing tests**

```python
from django.test import TestCase
from django.urls import reverse

from cds_core.models import CaseScenario, ChiefComplaint, ClinicalItem, Rule, Source
from cds_core.services import evaluate_abdominal_pain_pathway, evaluate_case_scenario


class AbdominalPainPathwayTests(TestCase):
    fixtures = ["headache_mvp.json", "chest_pain_mvp.json", "abdominal_pain_mvp.json"]

    def test_seed_content_adds_source_linked_abdominal_pain_module(self):
        self.assertEqual(ChiefComplaint.objects.count(), 3)
        self.assertTrue(ChiefComplaint.objects.filter(slug="abdominal-pain").exists())
        self.assertTrue(Source.objects.filter(version_label="ACR acute nonlocalized abdominal pain").exists())
        self.assertGreaterEqual(ClinicalItem.objects.filter(chief_complaint__slug="abdominal-pain").count(), 8)
        self.assertGreaterEqual(Rule.objects.filter(chief_complaint__slug="abdominal-pain").count(), 8)
        for item in ClinicalItem.objects.filter(chief_complaint__slug="abdominal-pain", status=ClinicalItem.Status.APPROVED):
            self.assertTrue(item.sources.exists(), item.title)
```

- [ ] **Step 2: Run RED**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_abdominal_pain_pathway -v 2`

Expected: fail because `evaluate_abdominal_pain_pathway` and `abdominal_pain_mvp` do not exist yet.

### Task 2: Abdominal pain implementation

**Files:**
- Modify: `clinical_differential_support/cds_core/forms.py`
- Modify: `clinical_differential_support/cds_core/services.py`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/base.html`
- Create: `clinical_differential_support/cds_core/templates/cds_core/abdominal_pain.html`
- Create: `clinical_differential_support/cds_core/fixtures/abdominal_pain_mvp.json`

- [ ] **Step 1: Add `AbdominalPainIntakeForm`**

Fields: `age`, `pain_duration_hours`, `generalized_abdominal_pain`, `severe_abdominal_pain`, `rebound_guarding`, `rigid_abdomen`, `hemodynamic_instability`, `fever`, `right_lower_quadrant_pain`, `leukocytosis`, `migration_to_rlq`, `right_upper_quadrant_pain`, `postprandial_ruq_pain`, `jaundice`, `vomiting`, `abdominal_distension`, `no_flatus`, `recent_abdominal_surgery`, `neutropenia`, `immunocompromised`, `pregnancy_possible`, `positive_pregnancy_test`, `vaginal_bleeding`, `syncope`, `clinically_stable`, `clinician_notes`.

- [ ] **Step 2: Add evaluator, view, route, and template**

Add `evaluate_abdominal_pain_pathway()` that calls `evaluate_pathway("abdominal-pain", raw_findings)`. Add `/abdominal-pain/` with the same clinician-reference layout pattern as headache and chest pain.

- [ ] **Step 3: Add abdominal pain fixture**

Create sources, eight approved clinical items, source links, deterministic rules, and three non-patient case scenarios. Use primary keys that do not overlap the existing fixtures.

- [ ] **Step 4: Run GREEN**

Run: `py -B clinical_differential_support\manage.py test cds_core.tests.test_abdominal_pain_pathway -v 2`

Expected: all abdominal pain tests pass.

### Task 3: Operational and documentation updates

**Files:**
- Modify: `clinical_differential_support/scripts/smoke_check.py`
- Modify: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] **Step 1: Add smoke coverage**

Add `/abdominal-pain/` as a 200 OK smoke check with expected text `Abdominal Pain Intake`.

- [ ] **Step 2: Update README setup**

Change fixture loading to `loaddata headache_mvp chest_pain_mvp abdominal_pain_mvp` and list `/abdominal-pain/`.

- [ ] **Step 3: Verify**

Run:

```powershell
py -B clinical_differential_support\manage.py test -v 2
py -B clinical_differential_support\manage.py check
py -B clinical_differential_support\manage.py loaddata abdominal_pain_mvp
py -B clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
```

Expected: tests pass, system check has no issues, fixture installs locally, smoke check passes after server restart.
