@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0..\.."
set "VENV=%ROOT%\..\.venv-mystock\Scripts\python.exe"
if not exist "%VENV%" (
  echo [ERROR] Python venv not found: %VENV%
  exit /b 1
)

set "db_host=127.0.0.1"
set "db_user=root"
set "db_password=785091"
set "db_database=instockdb"

cd /d "%ROOT%\instock\job"
echo [INFO] run main execute_daily_job.py %*
"%VENV%" execute_daily_job.py %*
if errorlevel 1 exit /b %errorlevel%

echo [INFO] run post_run_validate.py
"%VENV%" post_run_validate.py
exit /b %errorlevel%
