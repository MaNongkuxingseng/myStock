#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目路径
cpath_current = os.path.dirname(os.path.abspath(__file__))
instock_path = os.path.join(cpath_current, "instock")
sys.path.append(instock_path)

print("=== 检查myStock数据库表 ===")

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
    
    # 首先检查cn_stock_selection表
    print("\n1. 检查cn_stock_selection表:")
    cursor.execute("SHOW TABLES LIKE 'cn_stock_selection'")
    result = cursor.fetchone()
    if result:
        # 检查记录数和结构
        cursor.execute("SELECT COUNT(*) FROM `cn_stock_selection`")
        count = cursor.fetchone()[0]
        print(f"   ✅ 存在 ({count} 条记录)")
        
        # 查看表结构
        cursor.execute("DESCRIBE `cn_stock_selection`")
        columns = cursor.fetchall()
        print(f"   表结构:")
        for col in columns[:10]:  # 只显示前10列
            print(f"     - {col[0]} ({col[1]})")
        if len(columns) > 10:
            print(f"     ... 还有{len(columns)-10}列")
            
        # 查看一些示例数据
        cursor.execute("SELECT * FROM `cn_stock_selection` LIMIT 3")
        rows = cursor.fetchall()
        if rows:
            print(f"   示例数据 (前3行):")
            for i, row in enumerate(rows):
                print(f"     第{i+1}行: {row[:5]}...")  # 只显示前5个字段
    else:
        print("   ❌ 不存在")
    
    # 检查其他关键表
    print("\n2. 检查其他关键表:")
    tables_to_check = [
        'cn_stock_indicators',
        'cn_stock_indicators_daily',
        'cn_stock_pattern',
        'cn_stock_strategy_enter',
        'cn_stock_basic'
    ]
    
    for table in tables_to_check:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        result = cursor.fetchone()
        if result:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"   {table}: ✅ 存在 ({count} 条记录)")
        else:
            print(f"   {table}: ❌ 不存在")
    
    # 检查是否有任何股票数据表
    print("\n3. 检查所有股票相关表:")
    cursor.execute("SHOW TABLES LIKE 'cn_stock_%'")
    all_cn_tables = cursor.fetchall()
    if all_cn_tables:
        print(f"   找到 {len(all_cn_tables)} 个中国股票相关表:")
        for table in all_cn_tables[:10]:  # 只显示前10个
            print(f"     - {table[0]}")
        if len(all_cn_tables) > 10:
            print(f"     ... 还有{len(all_cn_tables)-10}个表")
    else:
        print("   未找到任何中国股票相关表")
    
    cursor.close()
    conn.close()
    
except pymysql.Error as e:
    print(f"❌ 数据库连接失败: {e}")
    print("可能的原因:")
    print("1. MySQL服务未启动")
    print("2. 数据库用户密码错误")
    print("3. 数据库不存在")
    print(f"4. 连接信息: {database.db_user}@{database.db_host}:{database.db_port}/{database.db_database}")

print("\n=== 检查完成 ===")