# Local Launch Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add local startup and smoke-check support so the MVP can be opened and verified reliably.

**Architecture:** Keep the health endpoint inside `cds_core` and keep smoke checks in a standalone stdlib script. The Windows start script remains local-dev only and does not manage credentials.

**Tech Stack:** Django 5.2, Python stdlib `urllib`, Windows batch script.

---

### Task 1: Health Endpoint

**Files:**
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Test: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`

- [ ] Write tests for `/health/` returning JSON status and no clinical content.
- [ ] Run `py -B clinical_differential_support\manage.py test cds_core.tests.test_operational_readiness -v 2` and confirm it fails because the route is missing.
- [ ] Add `health_check()` using `ClinicalItem.objects.exists()` as the database check.
- [ ] Add `path("health/", views.health_check, name="health_check")`.
- [ ] Re-run the targeted test and confirm it passes.

### Task 2: Smoke Check Script

**Files:**
- Create: `clinical_differential_support/scripts/__init__.py`
- Create: `clinical_differential_support/scripts/smoke_check.py`
- Test: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`

- [ ] Add tests for smoke check plan construction and base URL normalization.
- [ ] Run the targeted test and confirm it fails because the script module is missing.
- [ ] Implement the smoke check script with stdlib `urllib.request`.
- [ ] Re-run the targeted test and confirm it passes.

### Task 3: Local Start Script and Docs

**Files:**
- Create: `clinical_differential_support/Start_Local_Server.cmd`
- Modify: `clinical_differential_support/README.md`
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Add the Windows start script.
- [ ] Document the start script and smoke check commands.
- [ ] Run full tests, Django check, safety scan, restart server, and live smoke check.
