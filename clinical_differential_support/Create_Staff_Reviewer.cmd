@echo off
setlocal
chcp 65001 > nul
cd /d "%~dp0\.."

echo.
echo Create local staff reviewer / 建立本機 staff reviewer
echo You will enter username, email, and password locally.
echo This script does not create, print, pass, or store passwords.
echo.

py -B .\clinical_differential_support\manage.py createsuperuser %*
set "CREATE_STAFF_EXIT=%ERRORLEVEL%"
echo.
echo Django createsuperuser exit code: %CREATE_STAFF_EXIT%
echo.
echo Rechecking Final Project Gate...

py -B .\clinical_differential_support\scripts\project_completion_status.py
set "FINAL_GATE_EXIT=%ERRORLEVEL%"
echo.
echo Final gate exit code: %FINAL_GATE_EXIT%

if not "%CDS_CREATE_STAFF_NO_PAUSE%"=="1" (
    echo.
    pause
)

exit /b %FINAL_GATE_EXIT%
