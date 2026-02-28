@echo off
chcp 65001 >nul
echo myStock Scheduled Task
echo.

set PYTHON=python
set PROJECT=G:\openclaw\workspace\_system\agent-home\myStock\instock

echo [%time%] Running monitor...
cd /d "%PROJECT%"
"%PYTHON%" monitor\stock_monitor.py

echo.
echo Task completed
pause
