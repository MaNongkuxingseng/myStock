@echo off
chcp 65001 >nul
echo ========================================
echo myStock早上9点持仓分析任务
echo ========================================
echo.

set PROJECT=G:\openclaw\workspace\_system\agent-home\myStock\instock
cd /d "%PROJECT%"

echo [1/3] 运行持仓分析...
python immediate_analysis.py

echo.
echo [2/3] 检查分析结果...
if exist reports\* (
    echo 分析报告已生成
    dir reports\*.md | findstr /i "report"
) else (
    echo 警告: 未找到分析报告
)

echo.
echo [3/3] 任务执行完成
echo 时间: %date% %time%
echo ========================================

REM 保持窗口打开以便查看结果
pause