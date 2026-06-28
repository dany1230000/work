@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0\.."

echo 最終版完成判斷 / Final Project Gate
echo.
py -B .\clinical_differential_support\scripts\project_completion_status.py %*
set "FINAL_GATE_EXIT_CODE=%ERRORLEVEL%"

echo.
echo Final gate exit code: %FINAL_GATE_EXIT_CODE%
echo.
echo Completion URL: http://127.0.0.1:8000/completion/
echo Launch Control: http://127.0.0.1:8000/launch/

if not "%CDS_FINAL_CHECK_NO_PAUSE%"=="1" (
  echo.
  pause
)

exit /b %FINAL_GATE_EXIT_CODE%
