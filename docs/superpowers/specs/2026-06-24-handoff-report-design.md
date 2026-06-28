# Handoff report design

## Goal

新增 staff-only Markdown 交付報告，讓 reviewer 或交付接手者可以用人類可讀格式快速確認 MVP 是否可交付。報告以中文為主、英文輔助，並保持 summary-only。

## Scope

- Add `GET /review/exports/handoff-report.md`.
- Reuse the existing release evidence/readiness summary instead of adding a new clinical-content query.
- Link the Markdown report from `/review/readiness/`.
- Keep access staff-only through the existing reviewer guard.
- Update README and progress notes.

## Report content

The Markdown report includes:

- `Clinical Differential Support Handoff Report` title.
- 交付狀態 / Handoff Status.
- 治理摘要 / Governance Summary.
- 匯出路徑 / Export Routes.
- 安全範圍 / Safety Scope.
- Notes that the report is summary-only.

The report intentionally excludes detailed clinical item titles, summaries, source titles, source URLs, case narratives, credentials, diagnosis orders, treatment orders, and trading/order fields.

## Acceptance checks

- Anonymous requests redirect to `/review/login/?next=/review/exports/handoff-report.md`.
- Staff requests return `text/markdown; charset=utf-8` with `handoff-report.md` in `Content-Disposition`.
- The report includes handoff status, item counts, case validation counts, and links to CSV/JSON/readiness exports.
- The report does not include fixture clinical text such as `Thunderclap headache` or `ACR Appropriateness Criteria`.
- The release readiness page links to the Markdown report.
