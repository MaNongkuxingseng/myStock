#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目路径
cpath_current = os.path.dirname(os.path.abspath(__file__))
instock_path = os.path.join(cpath_current, "instock")
sys.path.append(instock_path)

print("=== myStock数据库测试 ===")

try:
    from lib import database
    print(f"数据库配置加载成功")
    print(f"  主机: {database.db_host}")
    print(f"  端口: {database.db_port}")
    print(f"  数据库: {database.db_database}")
    print(f"  用户: {database.db_user}")
except Exception as e:
    print(f"数据库配置加载失败: {e}")
    sys.exit(1)

# 测试数据库连接
try:
    import pymysql
    conn = pymysql.connect(
        host=database.db_host,
        user=database.db_user,
        password=database.db_password,
        database=database.db_database,
        port=database.db_port,
        charset=database.db_charset
    )
    print("✅ 数据库连接成功")
    
    # 检查关键表
    cursor = conn.cursor()
    tables_to_check = [
        'cn_stock_selection',
        'cn_stock_indicators',
        'cn_stock_pattern',
        'cn_stock_strategy_enter'
    ]
    
    print("\n检查数据库表:")
    for table in tables_to_check:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        result = cursor.fetchone()
        if result:
            # 检查记录数
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"   {table}: ✅ 存在 ({count} 条记录)")
        else:
            print(f"   {table}: ❌ 不存在")
    
    cursor.close()
    conn.close()
    
except pymysql.Error as e:
    print(f"❌ 数据库连接失败: {e}")
    print("可能的原因:")
    print("1. MySQL服务未启动")
    print("2. 数据库用户密码错误")
    print("3. 数据库不存在")
    print(f"4. 连接信息: {database.db_user}@{database.db_host}:{database.db_port}/{database.db_database}")

print("\n=== 测试完成 ===")