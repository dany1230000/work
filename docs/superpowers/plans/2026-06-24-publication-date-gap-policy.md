# Publication Date Gap Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document and surface the source publication-date gap policy so staff know the next action without inferring missing official dates.

**Architecture:** Keep all behavior in `cds_core.source_freshness`; views remain thin and templates render the report. No schema changes are needed because the governed fixtures already preserve blank publication dates.

**Tech Stack:** Django, Django TestCase, existing staff-only views, existing smoke script.

---

### Task 1: Red Tests For Policy

**Files:**
- Modify: `clinical_differential_support/cds_core/tests/test_source_freshness.py`

- [ ] Require `publication_date_gap_policy` in the selector output.
- [ ] Require missing-date rows to expose manual-review metadata.
- [ ] Require the first action to be regression/smoke when there are no stale sources.
- [ ] Require page and JSON export to expose the policy.
- [ ] Run targeted source-freshness tests and confirm they fail.

### Task 2: Implement Policy

**Files:**
- Modify: `clinical_differential_support/cds_core/source_freshness.py`
- Modify: `clinical_differential_support/cds_core/templates/cds_core/source_freshness.html`

- [ ] Add the no-inference policy block.
- [ ] Add per-source publication-date review fields.
- [ ] Update next-action generation so documented blank dates are not stale blockers.
- [ ] Render the policy and per-row status in the staff page.
- [ ] Re-run targeted tests and confirm they pass.

### Task 3: Verification And Progress

**Files:**
- Modify: `.planning/2026-06-22-clinical-differential-support/progress.md`

- [ ] Run full regression.
- [ ] Run Django system check.
- [ ] Restart local server.
- [ ] Run live smoke.
- [ ] Verify live DB source freshness summary and first source action.
- [ ] Record progress and safety boundary.
