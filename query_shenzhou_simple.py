#!/usr/bin/env python3
"""
简单查询神州数码数据
"""

import pymysql

print("查询神州数码(000034)真实数据...")

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='785091',
        database='instockdb',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 查看cn_stock_selection表结构
    cursor.execute("DESCRIBE cn_stock_selection")
    columns = [col[0] for col in cursor.fetchall()]
    print(f"表字段: {columns}")
    
    # 查询神州数码数据
    query = "SELECT * FROM cn_stock_selection WHERE code = '000034' ORDER BY date DESC LIMIT 3"
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"\n找到{len(results)}条神州数码数据:")
        for row in results:
            print(f"\n日期: {row[columns.index('date')]}")
            print(f"代码: {row[columns.index('code')]}")
            print(f"名称: {row[columns.index('name')]}")
            
            # 价格数据
            if 'close' in columns:
                print(f"收盘价: {row[columns.index('close')]}")
            if 'open' in columns:
                print(f"开盘价: {row[columns.index('open')]}")
            if 'high' in columns:
                print(f"最高价: {row[columns.index('high')]}")
            if 'low' in columns:
                print(f"最低价: {row[columns.index('low')]}")
            if 'volume' in columns:
                volume = row[columns.index('volume')]
                print(f"成交量: {volume:,}手 ({volume/10000:.2f}万手)")
            if 'change_percent' in columns:
                print(f"涨跌幅: {row[columns.index('change_percent')]}%")
    else:
        print("未找到神州数码数据")
        
        # 查看有哪些股票数据
        cursor.execute("SELECT DISTINCT code, name FROM cn_stock_selection LIMIT 10")
        stocks = cursor.fetchall()
        print(f"\n数据库中的股票示例: {stocks}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"查询错误: {e}")