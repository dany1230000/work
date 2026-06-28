@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0\.."

echo 本機下一步助手 / Local Next Step
echo.
py -B .\clinical_differential_support\scripts\local_setup_assistant.py %*
set "ASSISTANT_EXIT_CODE=%ERRORLEVEL%"

echo.
echo Assistant exit code: %ASSISTANT_EXIT_CODE%
echo.
echo Launch Control: http://127.0.0.1:8000/launch/

if not "%CDS_NEXT_STEP_NO_PAUSE%"=="1" (
  echo.
  pause
)

exit /b %ASSISTANT_EXIT_CODE%
