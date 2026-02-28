#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
myStock系统修复脚本
目标：修复数据源问题，恢复核心功能
"""

import os
import sys
import json
import pymysql
from datetime import datetime

class MyStockFixer:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.instock_dir = os.path.join(self.base_dir, "instock")
        sys.path.append(self.instock_dir)
        
    def check_database(self):
        """检查数据库连接"""
        print("1. 检查数据库连接...")
        try:
            from lib import database
            print(f"   数据库配置: {database.db_host}:{database.db_port}/{database.db_database}")
            
            conn = pymysql.connect(
                host=database.db_host,
                user=database.db_user,
                password=database.db_password,
                database=database.db_database,
                port=database.db_port,
                charset=database.db_charset
            )
            
            cursor = conn.cursor()
            
            # 检查关键表
            tables = ['cn_stock_selection', 'cn_stock_indicators', 'cn_stock_pattern']
            for table in tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if cursor.fetchone():
                    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {table}: {count} 条记录")
                else:
                    print(f"   ❌ {table}: 表不存在")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"   ❌ 数据库连接失败: {e}")
            return False
    
    def check_config_files(self):
        """检查配置文件"""
        print("\n2. 检查配置文件...")
        
        configs = [
            ("东方财富Cookie", "config/eastmoney_cookie.txt"),
            ("代理配置", "config/proxy.txt"),
            ("交易客户端配置", "config/trade_client.json"),
        ]
        
        for name, path in configs:
            full_path = os.path.join(self.instock_dir, path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"   ✅ {name}: 存在 ({size} 字节)")
            else:
                print(f"   ⚠️  {name}: 不存在")
    
    def check_python_modules(self):
        """检查Python模块"""
        print("\n3. 检查Python模块...")
        
        modules = [
            ("pandas", "数据分析"),
            ("numpy", "数值计算"),
            ("pymysql", "数据库连接"),
            ("requests", "网络请求"),
            ("talib", "技术指标"),
        ]
        
        for module, desc in modules:
            try:
                __import__(module)
                print(f"   ✅ {module}: 已安装 ({desc})")
            except ImportError:
                print(f"   ❌ {module}: 未安装")
    
    def create_fix_suggestions(self):
        """创建修复建议"""
        print("\n4. 修复建议:")
        
        suggestions = [
            "a. 更新东方财富Cookie: 访问 https://quote.eastmoney.com 获取新Cookie",
            "b. 配置代理服务器: 编辑 instock/config/proxy.txt",
            "c. 验证数据库权限: 确保MySQL用户有足够权限",
            "d. 安装缺失模块: pip install -r requirements.txt",
            "e. 测试数据抓取: python instock/job/basic_data_daily_job.py",
        ]
        
        for suggestion in suggestions:
            print(f"   {suggestion}")
    
    def create_monitoring_module(self):
        """创建监控模块模板"""
        print("\n5. 创建监控模块模板...")
        
        monitor_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock异动监控模块
监控规则：
1. 价格异动：单日涨跌幅 > 7%
2. 成交量异动：量比 > 3 或 < 0.3
3. 资金异动：主力净流入/流出超阈值
4. 技术信号：多个指标同时发出买卖信号
"""

import pandas as pd
import pymysql
from datetime import datetime, timedelta

class StockMonitor:
    def __init__(self):
        from lib import database
        self.db_config = {
            'host': database.db_host,
            'user': database.db_user,
            'password': database.db_password,
            'database': database.db_database,
            'port': database.db_port,
            'charset': database.db_charset
        }
    
    def check_price_abnormal(self, threshold=7.0):
        """检查价格异动"""
        conn = pymysql.connect(**self.db_config)
        query = """
            SELECT code, name, change_rate, volume_ratio, net_inflow
            FROM cn_stock_indicators 
            WHERE date = CURDATE()
            AND ABS(change_rate) > %s
            ORDER BY ABS(change_rate) DESC
            LIMIT 20
        """
        df = pd.read_sql(query, conn, params=[threshold])
        conn.close()
        return df
    
    def check_volume_abnormal(self, ratio_threshold=3.0):
        """检查成交量异动"""
        conn = pymysql.connect(**self.db_config)
        query = """
            SELECT code, name, volume_ratio, change_rate, turnoverrate
            FROM cn_stock_indicators 
            WHERE date = CURDATE()
            AND (volume_ratio > %s OR volume_ratio < 1/%s)
            ORDER BY ABS(volume_ratio - 1) DESC
            LIMIT 20
        """
        df = pd.read_sql(query, conn, params=[ratio_threshold, ratio_threshold])
        conn.close()
        return df
    
    def generate_alert_message(self, alerts):
        """生成预警消息"""
        if alerts.empty:
            return None
        
        message = "📈 股票异动预警\\n\\n"
        for _, row in alerts.iterrows():
            message += f"• {row['code']} {row['name']}\\n"
            message += f"  涨跌幅: {row['change_rate']:.2f}%\\n"
            message += f"  量比: {row.get('volume_ratio', 'N/A'):.2f}\\n"
            message += f"  净流入: {row.get('net_inflow', 'N/A'):.2f}万\\n"
        
        return message

if __name__ == "__main__":
    monitor = StockMonitor()
    
    # 检查各种异动
    price_alerts = monitor.check_price_abnormal(7.0)
    volume_alerts = monitor.check_volume_abnormal(3.0)
    
    # 合并结果
    all_alerts = pd.concat([price_alerts, volume_alerts]).drop_duplicates()
    
    if not all_alerts.empty:
        message = monitor.generate_alert_message(all_alerts)
        print(message)
        # 这里可以添加Feishu消息推送
    else:
        print("✅ 今日无重大异动")
'''
        
        monitor_path = os.path.join(self.instock_dir, "monitor", "stock_monitor.py")
        os.makedirs(os.path.dirname(monitor_path), exist_ok=True)
        
        with open(monitor_path, 'w', encoding='utf-8') as f:
            f.write(monitor_code)
        
        print(f"   ✅ 监控模块已创建: {monitor_path}")
    
    def create_windows_task(self):
        """创建Windows任务计划配置"""
        print("\n6. 创建Windows任务计划配置...")
        
        task_config = '''@echo off
chcp 65001 >nul
echo === myStock定时任务 ===
echo.

REM 设置Python路径
set PYTHON_PATH=G:\\openclaw\\workspace\\_system\\agent-home\\myStock\\.venv-mystock\\Scripts\\python.exe
set PROJECT_PATH=G:\\openclaw\\workspace\\_system\\agent-home\\myStock\\instock

REM 检查Python环境
if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python虚拟环境不存在
    pause
    exit /b 1
)

REM 任务1: 收盘后数据更新 (16:20)
echo [INFO] 执行收盘后数据更新...
cd /d "%PROJECT_PATH%"
"%PYTHON_PATH%" execute_daily_job.py

REM 任务2: 晚间分析报告 (20:30)  
echo [INFO] 执行晚间分析报告...
cd /d "%PROJECT_PATH%"
"%PYTHON_PATH%" monitor/stock_monitor.py

REM 任务3: 开盘前预警 (08:40)
echo [INFO] 执行开盘前预警...
cd /d "%PROJECT_PATH%"
"%PYTHON_PATH%" -c "
import sys
sys.path.append('.')
from monitor.stock_monitor import StockMonitor
monitor = StockMonitor()
alerts = monitor.check_price_abnormal(5.0)
if not alerts.empty:
    print('📊 开盘前异动预警')
    print(alerts[['code', 'name', 'change_rate']].to_string())
"

echo.
echo === 任务执行完成 ===
pause
'''
        
        task_path = os.path.join(self.base_dir, "run_tasks.bat")
        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(task_config)
        
        print(f"   ✅ 任务计划配置已创建: {task_path}")
        print("   建议的Windows任务计划:")
        print("   • 16:20 - 收盘后数据更新")
        print("   • 20:30 - 晚间分析报告")
        print("   • 08:40 - 开盘前预警")

def main():
    print("=" * 60)
    print("myStock系统修复与增强工具")
    print("=" * 60)
    
    fixer = MyStockFixer()
    
    # 执行检查
    fixer.check_database()
    fixer.check_config_files()
    fixer.check_python_modules()
    fixer.create_fix_suggestions()
    fixer.create_monitoring_module()
    fixer.create_windows_task()
    
    print("\n" + "=" * 60)
    print("✅ 修复工具执行完成")
    print("下一步:")
    print("1. 按照修复建议处理问题")
    print("2. 测试监控模块: python instock/monitor/stock_monitor.py")
    print("3. 配置Windows任务计划")
    print("4. 提交git: git add . && git commit -m '修复myStock系统'")
    print("=" * 60)

if __name__ == "__main__":
    main()