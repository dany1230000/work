@echo off
setlocal
chcp 65001 >nul

set "APP_DIR=%~dp0"
for %%I in ("%APP_DIR%..") do set "ROOT_DIR=%%~fI"
cd /d "%ROOT_DIR%"

echo Clinical Differential Support local launcher
echo.
echo [1/4] Applying local database migrations...
py -B .\clinical_differential_support\manage.py migrate --run-syncdb
if errorlevel 1 goto fail

echo.
echo [2/4] Loading MVP fixture data...
py -B .\clinical_differential_support\manage.py loaddata headache_mvp chest_pain_mvp abdominal_pain_mvp dyspnea_mvp
if errorlevel 1 goto fail

echo.
echo [3/4] Printing next local action...
py -B .\clinical_differential_support\scripts\local_launch_status.py
if errorlevel 1 goto fail

echo.
echo [4/4] Starting http://127.0.0.1:8000/launch/
start "" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://127.0.0.1:8000/launch/'"
py -B .\clinical_differential_support\manage.py runserver 127.0.0.1:8000
exit /b %errorlevel%

:fail
echo.
echo Local launch failed. Review the error above.
pause
exit /b 1
