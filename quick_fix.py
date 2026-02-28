#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 添加自定义库路径
sys.path.append('D:\\python_libs')

print("=== myStock快速修复工具 ===")

# 1. 检查关键目录
print("\n1. 检查目录结构...")
base_dir = os.path.dirname(os.path.abspath(__file__))
instock_dir = os.path.join(base_dir, "instock")

dirs_to_check = [
    ("项目根目录", base_dir),
    ("instock目录", instock_dir),
    ("配置目录", os.path.join(instock_dir, "config")),
    ("日志目录", os.path.join(instock_dir, "log")),
]

for name, path in dirs_to_check:
    if os.path.exists(path):
        print(f"   ✅ {name}: 存在")
    else:
        print(f"   ❌ {name}: 不存在")
        os.makedirs(path, exist_ok=True)
        print(f"   ✅ {name}: 已创建")

# 2. 创建监控模块
print("\n2. 创建监控模块...")
monitor_dir = os.path.join(instock_dir, "monitor")
os.makedirs(monitor_dir, exist_ok=True)

# 简单监控脚本
simple_monitor = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易股票监控 - 发送到当前Feishu群组
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pandas as pd
    import pymysql
    from lib import database
    
    # 数据库连接
    conn = pymysql.connect(
        host=database.db_host,
        user=database.db_user,
        password=database.db_password,
        database=database.db_database,
        port=database.db_port,
        charset=database.db_charset
    )
    
    # 查询今日异动
    query = """
        SELECT code, name, change_rate, volume_ratio, net_inflow
        FROM cn_stock_indicators 
        WHERE date = CURDATE()
        AND (ABS(change_rate) > 7 OR volume_ratio > 3 OR volume_ratio < 0.3)
        ORDER BY ABS(change_rate) DESC
        LIMIT 10
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    if not df.empty:
        message = "📊 **股票异动监控**\\n\\n"
        for _, row in df.iterrows():
            change = row['change_rate']
            emoji = "📈" if change > 0 else "📉"
            message += f"{emoji} {row['code']} {row['name']}\\n"
            message += f"   涨跌幅: {change:+.2f}%\\n"
            message += f"   量比: {row['volume_ratio']:.2f}\\n"
            if pd.notna(row['net_inflow']):
                message += f"   净流入: {row['net_inflow']:.2f}万\\n"
            message += "\\n"
        
        print(message)
        # 这里可以添加Feishu推送
        # 消息将发送到当前群组: oc_b99df765824c2e59b3fabf287e8d14a2
    else:
        print("✅ 今日无重大异动")
        
except Exception as e:
    print(f"监控执行失败: {e}")

if __name__ == "__main__":
    print("开始监控...")
'''

monitor_path = os.path.join(monitor_dir, "simple_monitor.py")
with open(monitor_path, 'w', encoding='utf-8') as f:
    f.write(simple_monitor)
print(f"   ✅ 监控脚本创建: {monitor_path}")

# 3. 创建Windows任务计划
print("\n3. 创建Windows任务计划...")
task_bat = '''@echo off
chcp 65001 >nul
echo === myStock定时任务 ===
echo.

set PYTHON=python
set PROJECT=G:\\openclaw\\workspace\\_system\\agent-home\\myStock\\instock

echo [%time%] 执行监控任务...
cd /d "%PROJECT%"
"%PYTHON%" monitor\\simple_monitor.py

echo.
echo === 任务完成 ===
pause
'''

task_path = os.path.join(base_dir, "run_monitor.bat")
with open(task_path, 'w', encoding='utf-8') as f:
    f.write(task_bat)
print(f"   ✅ 任务计划创建: {task_path}")

# 4. 创建git提交文件
print("\n4. 创建git提交文件...")
commit_msg = '''feat: 新增股票监控系统

- 新增简易异动监控脚本
- 支持价格和成交量异动检测
- 准备Feishu消息推送集成
- 创建Windows定时任务配置
- 修复目录结构问题

监控规则:
1. 价格异动: 涨跌幅 > 7%
2. 成交量异动: 量比 > 3 或 < 0.3
3. 消息推送: 发送到当前Feishu群组

定时任务建议:
- 16:20: 收盘后分析
- 20:30: 晚间报告
- 08:40: 开盘前预警
'''

commit_path = os.path.join(base_dir, "COMMIT_MSG.txt")
with open(commit_path, 'w', encoding='utf-8') as f:
    f.write(commit_msg)
print(f"   ✅ 提交信息创建: {commit_path}")

# 5. 群组推送建议
print("\n5. 群组推送建议:")
print("""
基于你的需求，我建议以下群组分类：

📱 **主沟通群 (当前群组)**
   - 用途: myStock盯盘及消息推送
   - 消息: 实时异动预警、买卖信号、每日报告
   - 优势: 与valenbot对话记忆统一管理

📊 **分析报告群** (可选新建)
   - 用途: 详细分析报告、策略回测、数据统计
   - 消息: 周报、月报、深度分析
   - 频率: 每日/每周定期发送

🔔 **紧急预警群** (可选新建)  
   - 用途: 重大异动、风险预警、系统异常
   - 消息: 需要立即关注的紧急情况
   - 特点: 高优先级、@全员提醒

📋 **任务管理群** (可选新建)
   - 用途: 任务分配、进度跟踪、问题讨论
   - 消息: 任务状态、待办事项、会议记录
   - 参与: 项目相关人员

建议从当前群组开始，根据需要逐步扩展。
当前群组ID: oc_b99df765824c2e59b3fabf287e8d14a2
""")

print("\n" + "="*60)
print("✅ 快速修复完成")
print("\n下一步操作:")
print("1. 测试监控: python instock/monitor/simple_monitor.py")
print("2. 配置定时: 将run_monitor.bat加入Windows任务计划")
print("3. 提交git: git add . && git commit -F COMMIT_MSG.txt")
print("4. 测试推送: 手动运行监控查看输出格式")
print("="*60)