@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0\.."

set "PUBLISH_JSON_MODE=0"
for %%A in (%*) do (
  if /I "%%~A"=="--json" set "PUBLISH_JSON_MODE=1"
)

if not "%PUBLISH_JSON_MODE%"=="1" (
  echo Git Publish Readiness Assistant
  echo.
)

py -B .\clinical_differential_support\scripts\git_publish_status.py %*
set "PUBLISH_STATUS_EXIT_CODE=%ERRORLEVEL%"

if not "%PUBLISH_JSON_MODE%"=="1" (
  echo.
  echo Git publish readiness exit code: %PUBLISH_STATUS_EXIT_CODE%
  echo.
  echo Deployment status: clinical_differential_support\Deploy_Status.cmd
  echo Deployment URL: http://127.0.0.1:8000/deployment/
)

if not "%CDS_PUBLISH_STATUS_NO_PAUSE%"=="1" (
  echo.
  pause
)

exit /b %PUBLISH_STATUS_EXIT_CODE%
