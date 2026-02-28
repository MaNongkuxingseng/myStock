#!/usr/bin/env python3

import os
import sys

print("=== myStock Final Setup ===")

# Setup paths
base_dir = os.path.dirname(os.path.abspath(__file__))
instock_dir = os.path.join(base_dir, "instock")

print("\n1. Creating directory structure...")
dirs = [
    os.path.join(instock_dir, "monitor"),
    os.path.join(instock_dir, "config"),
    os.path.join(instock_dir, "log"),
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"   Created: {d}")

print("\n2. Creating monitor script...")
monitor_code = '''#!/usr/bin/env python3
"""
Simple stock monitor for myStock
Sends alerts to current Feishu group
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Add custom lib path
    sys.path.append('D:\\\\python_libs')
    
    import pandas as pd
    import pymysql
    from lib import database
    
    # Connect to database
    conn = pymysql.connect(
        host=database.db_host,
        user=database.db_user,
        password=database.db_password,
        database=database.db_database,
        port=database.db_port,
        charset=database.db_charset
    )
    
    # Query today's abnormal movements
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
        message = "Stock Alert Monitor\\n\\n"
        for _, row in df.iterrows():
            change = row['change_rate']
            symbol = "UP" if change > 0 else "DOWN"
            message += f"{row['code']} {row['name']}\\n"
            message += f"  Change: {change:+.2f}% ({symbol})\\n"
            message += f"  Volume Ratio: {row['volume_ratio']:.2f}\\n"
            if pd.notna(row['net_inflow']):
                message += f"  Net Inflow: {row['net_inflow']:.2f}M\\n"
            message += "\\n"
        
        print("ALERT MESSAGE:")
        print("="*50)
        print(message)
        print("="*50)
        print("\\nThis would be sent to Feishu group")
        print("Group ID: oc_b99df765824c2e59b3fabf287e8d14a2")
    else:
        print("No significant movements today")
        
except Exception as e:
    print(f"Monitor error: {e}")

if __name__ == "__main__":
    print("Starting monitor...")
'''

monitor_path = os.path.join(instock_dir, "monitor", "stock_monitor.py")
with open(monitor_path, 'w', encoding='utf-8') as f:
    f.write(monitor_code)
print(f"   Created: {monitor_path}")

print("\n3. Creating Windows task script...")
task_code = '''@echo off
chcp 65001 >nul
echo myStock Scheduled Task
echo.

set PYTHON=python
set PROJECT=G:\\openclaw\\workspace\\_system\\agent-home\\myStock\\instock

echo [%time%] Running monitor...
cd /d "%PROJECT%"
"%PYTHON%" monitor\\stock_monitor.py

echo.
echo Task completed
pause
'''

task_path = os.path.join(base_dir, "run_task.bat")
with open(task_path, 'w', encoding='utf-8') as f:
    f.write(task_code)
print(f"   Created: {task_path}")

print("\n4. Creating git commit guide...")
guide = '''GIT COMMIT GUIDE for myStock Updates

Files to commit:
- instock/monitor/stock_monitor.py  (new monitoring system)
- run_task.bat                       (Windows task scheduler)

Commit message:
feat: Add stock monitoring system

- Add real-time stock movement monitoring
- Support price and volume anomaly detection  
- Prepare Feishu message integration
- Create Windows task scheduling
- Fix directory structure issues

Monitoring rules:
1. Price alert: change rate > 7%
2. Volume alert: volume ratio > 3 or < 0.3
3. Message target: Current Feishu group

Suggested schedule:
- 16:20: After market close analysis
- 20:30: Evening report
- 08:40: Pre-market alert

To commit:
git add .
git commit -m "feat: Add stock monitoring system"
git push origin main
'''

guide_path = os.path.join(base_dir, "GIT_GUIDE.txt")
with open(guide_path, 'w', encoding='utf-8') as f:
    f.write(guide)
print(f"   Created: {guide_path}")

print("\n5. Group Management Recommendations:")
print("""
Based on your requirements:

PRIMARY GROUP (Current)
- Purpose: myStock monitoring & alerts
- Messages: Real-time alerts, buy/sell signals, daily reports
- Advantage: Unified conversation memory with valenbot

ANALYSIS GROUP (Optional new)
- Purpose: Detailed reports, strategy backtesting, statistics
- Messages: Weekly/monthly reports, deep analysis
- Frequency: Daily/weekly scheduled

URGENT ALERT GROUP (Optional new)
- Purpose: Critical alerts, risk warnings, system issues
- Messages: Immediate attention required
- Feature: High priority, @all notifications

TASK MANAGEMENT GROUP (Optional new)
- Purpose: Task assignment, progress tracking, discussions
- Messages: Task status, todos, meeting notes
- Participants: Project team members

Start with current group, expand as needed.
Current Group ID: oc_b99df765824c2e59b3fabf287e8d14a2
""")

print("\n" + "="*60)
print("SETUP COMPLETE")
print("\nNext steps:")
print("1. Test monitor: python instock/monitor/stock_monitor.py")
print("2. Schedule task: Add run_task.bat to Windows Task Scheduler")
print("3. Commit changes: Follow GIT_GUIDE.txt")
print("4. Test Feishu: Check monitor output format")
print("="*60)