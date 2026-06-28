# Local launch readiness design

## Goal

Make the MVP easier to start, verify, and diagnose locally after code changes or machine restarts.

## Scope

- Add a lightweight JSON health endpoint at `/health/`.
- Add a standard-library smoke check script for local service verification.
- Add a Windows start script for the Django dev server.
- Update README and progress with the operating path.

## Health endpoint

`GET /health/` returns JSON:

```json
{
  "status": "ok",
  "service": "clinical_differential_support",
  "checks": {
    "database": "ok"
  }
}
```

If the database check fails, it returns HTTP 503 with `"status": "error"` and no secret or patient-like details.

## Smoke check

The smoke check script accepts `--base-url` and validates:

- `/health/` returns 200 and `status=ok`.
- `/` returns 200 with `Clinical Differential Support`.
- `/review/login/` returns 200 with `Reviewer Login`.
- `/review/queue/` returns 200 with `Reviewer Queue`.
- `/review/sources/new/` returns 302 to `/review/login/?next=/review/sources/new/`.

## Windows start script

`Start_Local_Server.cmd` runs migrations, loads the MVP fixture, and starts Django at `127.0.0.1:8000` with `--noreload`.

## Constraints

- No credentials in scripts or docs.
- No production deployment behavior.
- No patient-identifying data.
- No diagnosis or treatment order behavior.
- No trading or order API behavior.
