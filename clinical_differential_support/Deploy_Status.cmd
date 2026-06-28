@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0\.."

echo ?函蔡??銝剖? / Deployment Operations Center
echo.
py -B .\clinical_differential_support\scripts\deployment_status.py %*
set "DEPLOY_STATUS_EXIT_CODE=%ERRORLEVEL%"

echo.
echo Deployment status exit code: %DEPLOY_STATUS_EXIT_CODE%
echo.
echo Deployment URL: http://127.0.0.1:8000/deployment/
echo Launch Control: http://127.0.0.1:8000/launch/

if not "%CDS_DEPLOY_STATUS_NO_PAUSE%"=="1" (
  echo.
  pause
)

exit /b %DEPLOY_STATUS_EXIT_CODE%
