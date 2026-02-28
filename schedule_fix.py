#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock定时任务修复脚本
确保消息推送不再落后
"""

import os
import sys
import datetime
import subprocess
from pathlib import Path

def check_scheduled_tasks():
    """检查定时任务状态"""
    print("检查定时任务状态...")
    
    # 检查Windows任务计划
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/tn", "myStock_Analysis"],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if "myStock_Analysis" in result.stdout:
            print("✅ Windows定时任务已存在")
            return True
        else:
            print("❌ Windows定时任务不存在")
            return False
            
    except Exception as e:
        print(f"⚠️ 检查定时任务失败: {e}")
        return False

def create_scheduled_task():
    """创建Windows定时任务"""
    print("创建Windows定时任务...")
    
    # 获取当前脚本路径
    script_path = Path(__file__).parent / "instock" / "morning_9am_scheduler.py"
    python_path = sys.executable
    
    # 创建任务XML
    task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-02-27T15:45:00</Date>
    <Author>myStock System</Author>
    <Description>myStock每日09:00持仓分析推送</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-02-28T09:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_path}"</Command>
      <Arguments>"{script_path}"</Arguments>
    </Exec>
  </Actions>
</Task>'''
    
    # 保存XML文件
    xml_path = Path(__file__).parent / "myStock_task.xml"
    with open(xml_path, 'w', encoding='utf-16') as f:
        f.write(task_xml)
    
    try:
        # 创建任务
        result = subprocess.run(
            ["schtasks", "/create", "/tn", "myStock_Analysis", "/xml", str(xml_path), "/f"],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if result.returncode == 0:
            print("✅ Windows定时任务创建成功")
            # 删除临时XML文件
            xml_path.unlink(missing_ok=True)
            return True
        else:
            print(f"❌ 创建任务失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 创建任务异常: {e}")
        return False

def create_simple_scheduler():
    """创建简单的Python调度器"""
    print("创建Python调度器...")
    
    scheduler_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock简单调度器
用于确保消息推送不落后
"""

import schedule
import time
import subprocess
import datetime
from pathlib import Path

def run_morning_analysis():
    """运行早上9点分析"""
    print(f"[{datetime.datetime.now()}] 运行早上9点分析...")
    try:
        script_path = Path(__file__).parent / "instock" / "morning_9am_scheduler.py"
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"分析完成: {result.returncode}")
    except Exception as e:
        print(f"分析失败: {e}")

def run_afternoon_analysis():
    """运行下午3点分析"""
    print(f"[{datetime.datetime.now()}] 运行下午3点分析...")
    try:
        script_path = Path(__file__).parent / "instock" / "enhanced_analysis.py"
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"分析完成: {result.returncode}")
    except Exception as e:
        print(f"分析失败: {e}")

def main():
    """主调度函数"""
    print("myStock调度器启动...")
    print(f"启动时间: {datetime.datetime.now()}")
    
    # 设置定时任务
    schedule.every().day.at("09:00").do(run_morning_analysis)
    schedule.every().day.at("15:00").do(run_afternoon_analysis)
    
    # 立即运行一次（测试）
    print("立即运行测试分析...")
    run_morning_analysis()
    
    print("调度器运行中，按Ctrl+C停止...")
    
    # 主循环
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("调度器停止")
    except Exception as e:
        print(f"调度器错误: {e}")
'''
    
    scheduler_path = Path(__file__).parent / "simple_scheduler.py"
    with open(scheduler_path, 'w', encoding='utf-8') as f:
        f.write(scheduler_code)
    
    print(f"✅ Python调度器创建: {scheduler_path}")
    return scheduler_path

def create_batch_file():
    """创建批处理文件"""
    print("创建启动批处理文件...")
    
    batch_content = '''@echo off
echo myStock消息推送系统启动...
echo 启动时间: %date% %time%
echo.

REM 设置Python路径
set PYTHON_PATH=python

REM 运行调度器
echo 启动Python调度器...
%PYTHON_PATH% "%~dp0simple_scheduler.py"

if %errorlevel% neq 0 (
    echo 调度器启动失败，尝试直接运行分析...
    %PYTHON_PATH% "%~dp0instock\\enhanced_analysis.py"
)

echo.
echo myStock系统运行结束
pause
'''
    
    batch_path = Path(__file__).parent / "start_mystock.bat"
    with open(batch_path, 'w', encoding='gbk') as f:
        f.write(batch_content)
    
    print(f"✅ 批处理文件创建: {batch_path}")
    return batch_path

def create_manual_check():
    """创建手动检查脚本"""
    print("创建手动检查脚本...")
    
    check_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock手动检查脚本
用于快速检查持仓状态
"""

import datetime
import json

def quick_check():
    """快速检查持仓"""
    print("=" * 60)
    print(f"myStock持仓快速检查 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 实际持仓
    holdings = [
        ("603949", "雪龙集团", 2900, 20.597, 19.60),
        ("600343", "航天动力", 800, 35.871, 36.14),
        ("002312", "川发龙蟒", 1600, 13.324, 13.62)
    ]
    
    total_value = 0
    total_cost = 0
    
    for code, name, shares, cost, price in holdings:
        value = shares * price
        cost_total = shares * cost
        pnl = value - cost_total
        pnl_pct = (pnl / cost_total) * 100
        weight = (value / sum(h[2] * h[4] for h in holdings)) * 100
        
        total_value += value
        total_cost += cost_total
        
        status = "盈利" if pnl >= 0 else "亏损"
        print(f"{code} {name} [{status}]")
        print(f"  持仓: {shares}股 | 成本: {cost:.3f}元")
        print(f"  现价: {price:.3f}元 | 市值: {value:.2f}元")
        print(f"  盈亏: {pnl:+.2f}元 ({pnl_pct:+.2f}%)")
        print(f"  权重: {weight:.1f}%")
        print()
    
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost) * 100
    
    print("=" * 60)
    print("组合汇总:")
    print(f"  总市值: {total_value:.2f}元")
    print(f"  总成本: {total_cost:.2f}元")
    print(f"  总盈亏: {total_pnl:+.2f}元 ({total_pnl_pct:+.2f}%)")
    print()
    
    # 风险检查
    max_weight = max((h[2] * h[4] / total_value * 100) for h in holdings)
    if max_weight > 40:
        print("⚠️ 高风险警报: 单只股票权重超过40%")
    elif max_weight > 30:
        print("⚠️ 中风险提示: 单只股票权重超过30%")
    else:
        print("✅ 持仓结构合理")
    
    print("=" * 60)

if __name__ == "__main__":
    quick_check()
'''
    
    check_path = Path(__file__).parent / "quick_check.py"
    with open(check_path, 'w', encoding='utf-8') as f:
        f.write(check_code)
    
    print(f"✅ 手动检查脚本创建: {check_path}")
    return check_path

def main():
    """主函数"""
    print("=" * 60)
    print("myStock定时任务修复系统")
    print(f"运行时间: {datetime.datetime.now()}")
    print("=" * 60)
    
    # 1. 检查现有定时任务
    has_task = check_scheduled_tasks()
    
    if not has_task:
        print("\n创建新的定时任务...")
        # 2. 尝试创建Windows定时任务
        task_created = create_scheduled_task()
        
        if not task_created:
            print("\nWindows定时任务创建失败，使用Python调度器...")
            # 3. 创建Python调度器
            scheduler_path = create_simple_scheduler()
            batch_path = create_batch_file()
            
            print(f"\n✅ 备用方案已创建:")
            print(f"   1. Python调度器: {scheduler_path}")
            print(f"   2. 批处理启动文件: {batch_path}")
            print(f"\n启动命令: 双击 {batch_path}")
    
    # 4. 创建手动检查脚本
    check_path = create_manual_check()
    
    print("\n" + "=" * 60)
    print("修复完成!")
    print("=" * 60)
    print("\n下一步操作:")
    print("1. 手动检查持仓: python quick_check.py")
    print("2. 启动调度器: 双击 start_mystock.bat")
    print("3. 明日09:00自动推送持仓分析")
    print("\n确保消息推送不再落后! 🚀")

if __name__ == "__main__":
    main()