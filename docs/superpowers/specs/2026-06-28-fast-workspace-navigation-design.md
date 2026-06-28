# Fast Workspace Navigation Design

## Goal

Reduce the user's page-switching wait time before expanding the clinical differential knowledge base. This stage focuses on perceived navigation speed and the slow status pages. It does not claim broad disease coverage.

## Current Findings

- Public `/launch/` and `/deployment/` take about 4.6-4.9 seconds.
- Local profiling shows `/launch/` and `/deployment/` execute about 664 SQL queries per request.
- Clinical workflow pages such as `/headache/`, `/chest-pain/`, `/abdominal-pain/`, and `/dyspnea/` are already fast locally, but the browser still shows full-page loading because the app uses traditional multi-page navigation.

## Approach

Use a narrow two-part fix:

1. Add progressive in-page navigation for same-site GET links.
   - Keep normal links as fallback.
   - Intercept same-origin GET navigation in JavaScript.
   - Fetch the next page, replace only the main workspace content, update history, and show a small in-app loading indicator.
   - Do not intercept forms, downloads, external links, logout, or reviewer actions.

2. Add short-lived status report caching for expensive public status pages.
   - Cache Launch Control and Deployment Operations Center reports for a 5-minute TTL.
   - Provide a `refresh=1` query parameter and visible refresh link for forced recomputation.
   - Keep CLI commands uncached by default so scripts still report current command-line state.

## Success Criteria

- `/launch/` and `/deployment/` use cached reports on ordinary page views.
- Cached status pages perform far fewer queries than the current 664-query baseline.
- The main navigation no longer triggers browser full-page reloads when JavaScript is available.
- Tests cover the navigation shell, refresh controls, and cached status-page query budget.
- Existing clinical safety boundaries remain unchanged: clinician-only, source-backed, no patient identifiers, no diagnosis or treatment orders.

## Deferred

The next stage is a generic encounter and differential engine for broad disease coverage. That work needs new data structures for findings, conditions, evidence, and coverage status. It should not be hidden inside this performance patch.
