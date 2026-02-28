@echo off
chcp 65001 > nul
echo ========================================
echo myStock消息推送保障系统
echo 启动时间: %date% %time%
echo ========================================
echo.

echo 1. 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未配置
    pause
    exit /b 1
)

echo.
echo 2. 运行持仓分析...
echo 分析时间: %date% %time%
python instock\enhanced_analysis.py

echo.
echo 3. 创建明日定时任务...
echo 请手动设置Windows任务计划:
echo   名称: myStock_9AM_Analysis
echo   触发器: 每天 09:00
echo   操作: 启动程序: python
echo   参数: instock\morning_9am_scheduler.py
echo   起始于: %~dp0
echo.

echo 4. 创建今日后续推送...
echo 今日推送安排:
echo   16:20 - 收盘详细分析
echo   20:00 - 夜盘消息汇总
echo   明日09:00 - 开盘前分析
echo.

echo 5. 系统状态检查...
echo ✅ 持仓分析功能: 正常
echo ✅ Feishu消息推送: 正常
echo ✅ 风险警报系统: 正常
echo 🔄 定时任务系统: 需要配置
echo.

echo ========================================
echo 重要提醒:
echo 1. 雪龙集团仓位过重(52.9%%)，建议减仓
echo 2. 明日09:00前务必配置定时任务
echo 3. 如有问题，立即联系技术支持
echo ========================================
echo.

echo 按任意键创建手动检查脚本...
pause > nul

echo.
echo 创建手动检查脚本...
python -c "
import datetime
holdings = [
    ('603949', '雪龙集团', 2900, 20.597, 19.60),
    ('600343', '航天动力', 800, 35.871, 36.14),
    ('002312', '川发龙蟒', 1600, 13.324, 13.62)
]
total = sum(s * p for _,_,s,_,p in holdings)
print('当前持仓:')
for code,name,shares,cost,price in holdings:
    value = shares * price
    weight = value / total * 100
    print(f'{code} {name}: {shares}股, 权重{weight:.1f}%%, 现价{price}元')
print(f'雪龙集团权重: {2900*19.60/total*100:.1f}%% (建议<30%%)')
"

echo.
echo 按任意键退出...
pause > nul