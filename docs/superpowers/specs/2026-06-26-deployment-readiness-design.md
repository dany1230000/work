# Deployment Readiness Design

## Goal

Make the clinical differential support app deploy-ready beyond localhost while preserving the existing clinician-reference safety scope.

## Scope

- Keep the app behavior unchanged for local use.
- Add production-safe Django settings driven by environment variables.
- Add Render-compatible build, start, database, static-file, and health-check configuration.
- Add Chinese-first deployment instructions with English labels where useful.
- Stop before real public deployment when Git remote, cloud account, or secrets are unavailable.

## Non-Goals

- No real clinical production launch approval.
- No patient-facing workflow.
- No diagnosis, treatment, prescription, dose, or order automation.
- No committed credentials or generated staff passwords.
- No broker, trading, order, or Shioaji behavior.

## Design

### Runtime Settings

Local defaults remain developer-friendly: SQLite, localhost hosts, and debug enabled. Production mode is selected with `DJANGO_DEBUG=0` or Render's runtime environment. In production mode the app requires `DJANGO_SECRET_KEY`, accepts `DATABASE_URL`, uses WhiteNoise for static files, trusts Render's forwarded HTTPS header, and supports explicit host/CSRF origin configuration.

### Deployment Target

Render is the first deploy-ready target because it can provision a Python web service and PostgreSQL database from `render.yaml`. The Blueprint will live at the repository root and use `bash ./clinical_differential_support/build.sh` so Windows executable-bit differences do not block deployment.

### Staff Account Setup

Staff reviewer creation remains interactive after deployment. The deploy guide instructs the operator to use Render Shell and run Django `createsuperuser`; it does not store, print, or automate credentials.

### Verification

Add deployment-readiness tests before implementation. Then verify:

- targeted deployment tests
- full Django regression
- Django production checks
- production collectstatic
- Final_Check
- local smoke check
- safety scans for credentials and forbidden trading/order markers
