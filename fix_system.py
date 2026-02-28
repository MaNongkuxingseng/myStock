#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🔧 {description}")
    print(f"   命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"   ✅ 成功")
            if result.stdout.strip():
                print(f"   输出: {result.stdout[:200]}...")
        else:
            print(f"   ❌ 失败 (代码: {result.returncode})")
            if result.stderr:
                print(f"   错误: {result.stderr[:200]}...")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  超时")
        return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def main():
    print("=== myStock系统修复工具 ===")
    
    # 切换到myStock目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    print(f"工作目录: {base_dir}")
    
    # 1. 检查虚拟环境
    venv_python = os.path.join(base_dir, ".venv-mystock", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        print(f"\n❌ 虚拟环境不存在: {venv_python}")
        print("请先创建虚拟环境: python -m venv .venv-mystock")
        return
    
    print(f"\n✅ 虚拟环境: {venv_python}")
    
    # 2. 检查依赖安装状态
    success = True
    
    # 测试关键依赖
    test_cmds = [
        (f'"{venv_python}" -c "import pandas; print(\"pandas:\", pandas.__version__)"', "检查pandas"),
        (f'"{venv_python}" -c "import numpy; print(\"numpy:\", numpy.__version__)"', "检查numpy"),
        (f'"{venv_python}" -c "import pymysql; print(\"pymysql:\", pymysql.__version__)"', "检查pymysql"),
        (f'"{venv_python}" -c "import talib; print(\"talib: OK\")"', "检查talib"),
    ]
    
    for cmd, desc in test_cmds:
        if not run_command(cmd, desc):
            success = False
    
    if not success:
        print(f"\n⚠️  部分依赖缺失，正在安装...")
        install_cmd = f'"{venv_python}" -m pip install -r requirements.txt'
        run_command(install_cmd, "安装依赖")
    
    # 3. 测试数据库连接
    print(f"\n📊 测试数据库连接...")
    test_db = f'"{venv_python}" -c "'
    test_db += 'import sys; sys.path.append(\".\"); '
    test_db += 'from instock.lib import database; '
    test_db += 'print(f\"数据库配置: {database.db_host}:{database.db_port}/{database.db_database}\"); '
    test_db += 'import pymysql; '
    test_db += 'conn = pymysql.connect(host=database.db_host, user=database.db_user, '
    test_db += 'password=database.db_password, database=database.db_database, '
    test_db += 'port=database.db_port, charset=database.db_charset); '
    test_db += 'print(\"✅ 数据库连接成功\"); conn.close()"'
    
    run_command(test_db, "数据库连接测试")
    
    # 4. 测试数据抓取
    print(f"\n🌐 测试数据抓取功能...")
    test_fetch = f'"{venv_python}" -c "'
    test_fetch += 'import sys; sys.path.append(\"./instock\"); '
    test_fetch += 'from core.crawling.stock_hist_em import stock_zh_a_hist; '
    test_fetch += 'try: '
    test_fetch += '    df = stock_zh_a_hist(symbol=\"000001\", period=\"daily\", start_date=\"2025-01-01\", end_date=\"2025-01-10\"); '
    test_fetch += '    print(f\"✅ 数据抓取成功，获取{len(df)}条记录\"); '
    test_fetch += '    print(df[[\"日期\", \"开盘\", \"收盘\", \"成交量\"]].head()); '
    test_fetch += 'except Exception as e: '
    test_fetch += '    print(f\"❌ 数据抓取失败: {e}\")"'
    
    run_command(test_fetch, "东方财富数据抓取测试")
    
    # 5. 创建修复建议
    print(f"\n📋 修复建议:")
    print(f"1. 检查东方财富Cookie: instock/config/eastmoney_cookie.txt")
    print(f"2. 检查代理配置: instock/config/proxy.txt")
    print(f"3. 验证数据库权限: MySQL root/root")
    print(f"4. 测试完整流程: python instock/job/basic_data_daily_job.py")
    
    print(f"\n✅ 系统检查完成")

if __name__ == "__main__":
    main()