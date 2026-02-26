@echo off
chcp 65001 >nul
setlocal
set "BIN=%~dp0"

echo [INFO] Starting myStock job (new window)...
start "myStock-Job" cmd /k ""%BIN%run_job_local.bat""

timeout /t 2 >nul

echo [INFO] Starting myStock web (new window)...
start "myStock-Web" cmd /k ""%BIN%run_web_local.bat""

echo [OK] Both windows started.
exit /b 0
