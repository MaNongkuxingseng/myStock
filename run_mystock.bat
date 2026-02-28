@echo off
chcp 65001 >nul
echo ========================================
echo myStock System Launcher
echo ========================================
echo.

REM Set Python paths
set PYTHONPATH=D:\python_libs;G:\openclaw\workspace\_system\agent-home\myStock\instock
set PATH=D:\Program Files\Python;%PATH%

REM Change to project directory
cd /d "G:\openclaw\workspace\_system\agent-home\myStock\instock\job"

echo [Step 1] Initializing database...
python -c "import sys; sys.path.append('D:\\python_libs'); import pymysql; print('pymysql OK')"
if errorlevel 1 (
    echo ERROR: Python dependencies not found
    echo Please install: pip install pandas pymysql requests
    pause
    exit /b 1
)

echo [Step 2] Running data collection...
python execute_daily_job.py
if errorlevel 1 (
    echo WARNING: Data collection had issues
    echo This may be due to API limits or cookie issues
)

echo [Step 3] Checking system status...
cd /d ".."
python monitor\simple_alert.py

echo.
echo ========================================
echo myStock Launch Complete
echo ========================================
echo Next steps:
echo 1. Check database for today's data
echo 2. Configure持仓数据提交
echo 3. Test monitoring alerts
echo ========================================
pause