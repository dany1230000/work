# Final Verification Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a staff-only Final Verification Gate that converts regression-ready state into an exact final checklist and handoff/export path.

**Architecture:** Add `cds_core.final_verification` as a summary selector. Views remain thin. JSON avoids detailed clinical content and source URLs.

**Tech Stack:** Django, Django TestCase, existing smoke script.

---

### Task 1: Red Tests

**Files:**
- Create: `clinical_differential_support/cds_core/tests/test_final_verification.py`
- Modify: `clinical_differential_support/cds_core/tests/test_operational_readiness.py`

- [ ] Test selector status, command list, and handoff export routes.
- [ ] Test staff-only page and JSON protection.
- [ ] Test page and JSON are summary-only.
- [ ] Test Next Action and Release Readiness links.
- [ ] Test smoke check route plan includes protected final-verification routes.
- [ ] Run targeted tests and confirm failure.

### Task 2: Implementation

**Files:**
- Create: `clinical_differential_support/cds_core/final_verification.py`
- Create: `clinical_differential_support/cds_core/templates/cds_core/final_verification.html`
- Modify: `clinical_differential_support/cds_core/views.py`
- Modify: `clinical_differential_support/cds_core/urls.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/next_actions.html`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/release_readiness.html`
- Modify: `clinical_differential_support/scripts/smoke_check.py`

- [ ] Implement `build_final_verification_gate(today=None)`.
- [ ] Add staff-only page and JSON export.
- [ ] Link from Next Action and Release Readiness.
- [ ] Extend smoke route plan.
- [ ] Re-run targeted tests.

### Task 3: Verification

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Run full regression.
- [ ] Run Django system check.
- [ ] Restart local server.
- [ ] Run live smoke.
- [ ] Verify live final-verification summary.
- [ ] Record progress and safety boundary.
