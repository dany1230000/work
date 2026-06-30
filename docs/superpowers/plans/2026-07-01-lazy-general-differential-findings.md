# Lazy General Differential Findings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/differential/` fast to navigate by removing the full finding checkbox library from the initial HTML and loading it only when the clinician opens the library.

**Architecture:** Keep the main workbench as the clinical form and result page. Move the finding library markup into a reusable partial served by a new `/differential/findings/` endpoint, and add a small JavaScript loader that injects the partial on demand while preserving selected findings through hidden inputs.

**Tech Stack:** Django views, Django templates, Django test client, vanilla JavaScript, existing packaged differential catalog.

---

### Task 1: Lock The Lazy Loading Contract

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_general_differential_ui.py`

- [ ] **Step 1: Write the failing tests**

Add or update tests so a GET to `reverse("cds_core:general_differential")` still shows the stepwise workbench, metrics, drawer summary, and JavaScript functions, but does not include `data-finding-filter-form="true"`, `data-finding-option="true"`, or large finding labels such as `Recent cancer treatment`.

Add a second test for `reverse("cds_core:general_differential_findings")` that expects:

```python
self.assertContains(response, 'data-finding-filter-form="true"')
self.assertContains(response, 'data-finding-option="true"')
self.assertContains(response, "Recent cancer treatment")
self.assertContains(response, "Chest pain /")
self.assertContains(response, 'data-finding-search-index="chest pain')
```

Add a third test that calls the findings endpoint with `?selected=chest_pain&selected=dyspnea` and expects both selected checkboxes to render with `checked` and selected marker attributes.

- [ ] **Step 2: Verify RED**

Run:

```powershell
py -B manage.py test cds_core.tests.test_general_differential_ui -v 2
```

Expected: failures because `cds_core:general_differential_findings` does not exist and the initial page still renders the full finding library.

### Task 2: Add The Partial Endpoint

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Create: `clinical_differential_support/cds_core/templates/cds_core/partials/general_differential_finding_library.html`

- [ ] **Step 1: Add selected label helper**

Create a small helper beside `_build_finding_groups` that maps selected slugs to the existing title fields:

```python
def _build_selected_finding_labels(selected_findings):
    selected = set(selected_findings)
    labels = []
    for group in FINDING_GROUPS:
        for finding in group.findings:
            if finding.slug in selected:
                labels.append(finding)
    return labels
```

- [ ] **Step 2: Add the endpoint**

Add `general_differential_findings(request)` that reads repeated `selected` query params and renders the new partial with `_build_finding_groups(selected_findings)`.

- [ ] **Step 3: Wire the URL**

Add:

```python
path("differential/findings/", views.general_differential_findings, name="general_differential_findings")
```

- [ ] **Step 4: Move the finding library markup**

Move the current filter controls, complaint presets, finding stack, and finding error rendering from `general_differential.html` into `partials/general_differential_finding_library.html`.

- [ ] **Step 5: Verify GREEN for endpoint tests**

Run the same UI test module and confirm the endpoint-related assertions pass.

### Task 3: Keep The Initial Page Lightweight

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/general_differential.html`

- [ ] **Step 1: Trim main view context**

Make `general_differential_workspace` pass `finding_library_url`, `selected_finding_labels`, and `selected_findings`. Do not pass full `finding_groups` to the main page.

- [ ] **Step 2: Add hidden selected finding inputs**

Inside the main form, render:

```django
{% for slug in selected_findings %}
  <input type="hidden" name="findings" value="{{ slug }}" data-selected-finding-hidden="true">
{% endfor %}
```

This keeps POST results repeatable before the lazy library is opened.

- [ ] **Step 3: Add lazy container**

Replace the embedded library body with a container carrying:

```html
data-finding-library-container="true"
data-finding-library-url="{{ finding_library_url }}"
data-selected-findings="{{ selected_findings|join:',' }}"
```

- [ ] **Step 4: Add JavaScript loader**

Add `initializeFindingLibraryLoader(root)`. On drawer open, fetch the partial URL, append repeated `selected` params from `data-selected-findings`, inject the HTML, set a loaded marker, disable hidden selected inputs, and call `initializeFindingFilters(root)`.

- [ ] **Step 5: Verify initial page stays light**

Run:

```powershell
py -B manage.py test cds_core.tests.test_general_differential_ui -v 2
```

Expected: all tests in the module pass.

### Task 4: Full Verification And Commit

**Files:**
- New and modified files from Tasks 1-3 only.

- [ ] **Step 1: Run focused tests**

```powershell
py -B manage.py test cds_core.tests.test_general_differential_ui -v 2
```

- [ ] **Step 2: Run full tests**

```powershell
py -B manage.py test -v 2
```

- [ ] **Step 3: Run catalog validator**

```powershell
py -B manage.py validate_general_differential_catalog --fail-on-warning
```

- [ ] **Step 4: Smoke local or deployed pages**

Check `/differential/`, `/differential/findings/`, and POST `/differential/` with CSRF/session handling.

- [ ] **Step 5: Commit only related files**

Confirm `clinical_differential_support/cds_core/templates/cds_core/home.html` remains unstaged. Commit this phase with a message focused on lazy-loading the general differential findings.
