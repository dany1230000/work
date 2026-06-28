# Findings

## Workspace Findings

- Current workspace root is `C:\新增資料夾`.
- Existing major projects are `tw_quant_v2` and `shop_report_lite`.
- No existing medical decision-support app was found in the workspace.
- `shop_report_lite` store metadata explicitly says it does not provide medical advice, so this new product should be planned separately.
- The repository has many existing dirty changes, especially under `tw_quant_v2`; this planning work should avoid touching unrelated files.
- 2026-06-28 publish finding: the root Git HEAD tracks `tw_quant_v2/`, so a direct root push would publish unrelated trading research. The clinical app should be published from an isolated clinical-only tree instead.
- 2026-06-28 deployment finding: Render Blueprint URL for the pushed clinical repository redirects to Render sign-in when no authenticated Dashboard session is available; deployment cannot continue autonomously without user account authorization.
- 2026-06-28 deployment finding: once authenticated, the Render Blueprint page reads `render.yaml` from `dany1230000/work`, lists database `clinical-differential-support-db` and web service `clinical-differential-support`, and exposes a final `Deploy Blueprint` button that creates cloud resources.
- 2026-06-28 deployment finding: first Render deploy failed during build because `build.sh` ran plain `migrate`; `cds_core` has no migrations, so PostgreSQL lacked `cds_core_chiefcomplaint` when fixtures loaded. Production build needs `migrate --run-syncdb`.
- 2026-06-28 deployment finding: after pushing commit `2a246ba`, Render auto-deployed `dep-d9096a99rddc73a8ure0` to `live`; `/health/` returned 200 with database ok.

## Shared Conversation Findings

- The shared conversation is titled "鑑別診斷程式開發".
- Core concept: a clinical pathway / differential diagnosis knowledge-base system.
- Recommended product positioning from the shared conversation: clinical reference and teaching support, not AI diagnosis.
- Suggested workflow from the shared conversation: symptom -> red flags -> differential diagnosis -> confirmatory workup -> clinical context -> treatment options -> medication safety checks.

## External Research Findings

### Deployment Readiness Findings

- Render's Django deployment guide recommends using Render PostgreSQL instead of SQLite, configuring WhiteNoise static files, adding `dj-database-url`, PostgreSQL client dependencies, and a production web server such as Gunicorn.
  Source: https://render.com/docs/deploy-django
- Render's Django deployment guide shows production settings driven by environment variables such as `SECRET_KEY`, `DATABASE_URL`, `DEBUG`/production mode, and `RENDER_EXTERNAL_HOSTNAME`.
  Source: https://render.com/docs/deploy-django
- Render Blueprint files live at repo root as `render.yaml` and can define services, databases, build commands, start commands, health checks, generated secret values, and database-backed environment variables.
  Source: https://render.com/docs/blueprint-spec
- Current local deployment blockers are external, not app-code blockers: this workspace has no Git remote configured and `render` CLI is not installed.

### Regulatory and Safety Boundary Sources

- Taiwan TFDA announced the "人工智慧/機器學習技術之醫療器材軟體查驗登記技術指引" on 2020-09-11 as a reference for AI/ML medical-device software registration preparation.
  Source: https://www.fda.gov.tw/tc/siteListContent.aspx?id=34961&sid=3787
- Taiwan AIMD search results also show later software lifecycle items such as medical-device software post-market change guidance and AI/ML predetermined change-control plan guidance. Some AIMD detail pages timed out during fetch, so those should be rechecked before any production/regulatory claim.
  Sources attempted: https://aimd.fda.gov.tw/regulation/detail/94 and https://aimd.fda.gov.tw/regulation/detail/17
- FDA Clinical Decision Support Software guidance, current as of 2026-01-29, distinguishes non-device CDS from device software and emphasizes four criteria: no medical image/signal/pattern acquisition or analysis, use of medical/patient information such as peer-reviewed clinical studies and guidelines, recommendations to health care professionals, and enabling the professional to independently review the recommendation basis so they do not primarily rely on the software.
  Source: https://www.fda.gov/media/109618/download
- FDA AI-enabled medical device page notes a 2025 draft guidance for AI-enabled device software lifecycle management and marketing submission recommendations.
  Source: https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-software-medical-device
- IMDRF SaMD clinical evaluation framework centers on valid clinical association, analytical validation, and clinical validation. It treats clinical evaluation as an ongoing activity for intended use, safety, effectiveness, and performance.
  Source: https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation
- WHO AI-for-health ethics guidance emphasizes ethics, human rights, accountability, and responsiveness to healthcare workers and affected communities.
  Source: https://www.who.int/publications/i/item/9789240029200

### Headache MVP Source Candidates

- NICE CG150 provides structured headache assessment, red flags for further investigation/referral, headache-diary items, and feature tables for tension-type headache, migraine, and cluster headache. It was amended in places through 2025, so version/date should be shown per recommendation.
  Source: https://www.nice.org.uk/guidance/cg150/chapter/recommendations
- ACR Appropriateness Criteria for Headache is intended to guide radiologists and referring physicians in imaging decisions, with final decisions made by physicians/radiologists in context.
  Source: https://acsearch.acr.org/docs/69482/Narrative/
- ICHD-3 provides the standard headache classification and explicit diagnostic criteria; useful as classification reference rather than an autonomous diagnostic engine.
  Source: https://ichd-3.org/
