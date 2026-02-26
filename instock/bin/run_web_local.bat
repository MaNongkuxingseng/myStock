@echo off
chcp 65001 >nul
setlocal

REM ===== myStock web stable runner (Windows) =====
set "ROOT=%~dp0..\.."
set "VENV=%ROOT%\..\.venv-mystock\Scripts\python.exe"

if not exist "%VENV%" (
  echo [ERROR] Python venv not found: %VENV%
  pause
  exit /b 1
)

set "db_host=127.0.0.1"
set "db_user=root"
set "db_password=785091"
set "db_database=instockdb"

cd /d "%ROOT%\instock\web"
echo [INFO] Starting web_service.py on http://127.0.0.1:9988 ...
"%VENV%" web_service.py
set ERR=%ERRORLEVEL%
echo [INFO] Exit code: %ERR%
pause
exit /b %ERR%
