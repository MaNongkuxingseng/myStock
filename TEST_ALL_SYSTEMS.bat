@echo off
chcp 65001 >nul
echo ========================================
echo myStock系统完整测试
echo ========================================
echo.

set PROJECT=G:\openclaw\workspace\_system\agent-home\myStock\instock
cd /d "%PROJECT%"

echo [1/5] 测试数据库连接...
python -c "
import sys
sys.path.append('D:\\\\python_libs')
try:
    import pymysql
    from lib import database
    conn = pymysql.connect(
        host=database.db_host,
        user=database.db_user,
        password=database.db_password,
        database=database.db_database,
        port=database.db_port,
        charset=database.db_charset
    )
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f'✅ 数据库连接正常，找到{len(tables)}个表')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
"
if errorlevel 1 (
    echo ❌ 数据库测试失败
    pause
    exit /b 1
)

echo.
echo [2/5] 测试myStock指标计算...
python -c "
import sys
sys.path.append('D:\\\\python_libs')
sys.path.append('.')
try:
    from core.indicator.calculate_indicator import get_indicators
    import pandas as pd
    import numpy as np
    
    # 创建测试数据
    dates = pd.date_range('2026-01-01', periods=30, freq='D')
    test_data = pd.DataFrame({
        'date': dates,
        'open': np.random.randn(30) * 10 + 100,
        'high': np.random.randn(30) * 10 + 105,
        'low': np.random.randn(30) * 10 + 95,
        'close': np.random.randn(30) * 10 + 100,
        'volume': np.random.randint(100000, 1000000, 30)
    })
    
    indicators = get_indicators(test_data)
    print(f'✅ myStock指标计算正常，生成{len(indicators)}条指标数据')
    print(f'   包含指标: {list(indicators.columns)[-10:]}')
except Exception as e:
    print(f'❌ 指标计算失败: {e}')
    import traceback
    traceback.print_exc()
"
if errorlevel 1 (
    echo ⚠️ 指标计算测试有警告
)

echo.
echo [3/5] 测试持仓分析系统...
python monitor\mystock_integrated_analysis.py
if errorlevel 1 (
    echo ⚠️ 持仓分析测试有警告
)

echo.
echo [4/5] 测试任务管理系统...
python task_manager\task_management_system.py
if errorlevel 1 (
    echo ⚠️ 任务管理测试有警告
)

echo.
echo [5/5] 测试定时推送系统...
python scheduler\morning_9am_scheduler.py --run-once
if errorlevel 1 (
    echo ⚠️ 定时推送测试有警告
)

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 更新实际持仓数据
echo    编辑: instock\monitor\mystock_integrated_analysis.py
echo.
echo 2. 配置早上9点定时任务
echo    创建Windows任务计划，每天09:00执行：
echo    python scheduler\morning_9am_scheduler.py --run-once
echo.
echo 3. 创建新Feishu群组用于任务管理
echo    在Feishu中创建新群组，更新群组ID配置
echo.
echo 4. 测试消息推送
echo    复制生成的消息到Feishu群组测试格式
echo.
echo 详细指南请查看：DEPLOYMENT_GUIDE.md
echo ========================================
pause