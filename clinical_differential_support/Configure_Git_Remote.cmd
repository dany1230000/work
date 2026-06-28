@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0\.."

echo Git Remote Setup Assistant
echo.
py -B .\clinical_differential_support\scripts\configure_git_remote.py %*
set "GIT_REMOTE_EXIT_CODE=%ERRORLEVEL%"

echo.
echo Git remote setup exit code: %GIT_REMOTE_EXIT_CODE%
echo.
echo Deployment status: clinical_differential_support\Deploy_Status.cmd
echo Deployment URL: http://127.0.0.1:8000/deployment/

if not "%CDS_GIT_REMOTE_NO_PAUSE%"=="1" (
  echo.
  pause
)

exit /b %GIT_REMOTE_EXIT_CODE%
