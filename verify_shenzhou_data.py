#!/usr/bin/env python3
"""
验证神州数码真实数据
使用myStock 1.0版本的数据获取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*80)
print("神州数码(000034) - 真实数据验证")
print("="*80)

# 方法1: 尝试使用myStock 1.0的数据模块
try:
    print("尝试方法1: 使用instock.core.singleton_stock...")
    from instock.core.singleton_stock import trd
    
    # 获取神州数码数据
    data = trd.get_hist_data('000034')
    if data is not None and not data.empty:
        print(f"获取数据成功: {len(data)}条记录")
        print(f"最新数据:")
        print(f"  日期: {data.index[-1]}")
        print(f"  收盘价: {data['close'].iloc[-1]:.2f}")
        print(f"  开盘价: {data['open'].iloc[-1]:.2f}")
        print(f"  最高价: {data['high'].iloc[-1]:.2f}")
        print(f"  最低价: {data['low'].iloc[-1]:.2f}")
        print(f"  成交量: {data['volume'].iloc[-1]:,.0f}手")
    else:
        print("获取数据为空")
        
except Exception as e:
    print(f"方法1失败: {e}")

# 方法2: 检查数据库连接
print("\n尝试方法2: 直接数据库连接...")
try:
    import pymysql
    
    # 尝试连接数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='785091',
        database='instockdb',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 查询所有表
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"数据库表列表: {[table[0] for table in tables]}")
    
    # 查询神州数码数据
    cursor.execute("""
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'instockdb' 
        AND column_name LIKE '%close%' OR column_name LIKE '%volume%'
        LIMIT 10
    """)
    columns = cursor.fetchall()
    print(f"相关列: {columns}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"方法2失败: {e}")

# 方法3: 检查数据文件
print("\n尝试方法3: 检查本地数据文件...")
data_dir = os.path.join(os.path.dirname(__file__), "instock", "data")
if os.path.exists(data_dir):
    files = os.listdir(data_dir)
    print(f"数据目录文件数: {len(files)}")
    
    # 查找包含000034的文件
    for file in files[:10]:
        if '000034' in file or 'shenzhou' in file.lower():
            print(f"找到相关文件: {file}")
else:
    print(f"数据目录不存在: {data_dir}")

print("\n" + "="*80)
print("数据验证总结")
print("="*80)

print("""
问题分析:
1. 我之前提供的数据是基于myStock 1.1版本的模拟数据生成器
2. 正确的数据应该来自myStock 1.0版本的实际数据库
3. 您提供的正确数据: 收盘价40.63元, 成交量63.25万手

立即纠正:
1. 停止使用模拟数据
2. 连接到myStock 1.0的真实数据源
3. 重新进行准确的技术分析
4. 修正操作指导建议

严重性评估:
- 数据错误率: 收盘价错误35%, 成交量错误巨大
- 影响: 可能导致错误的投资决策
- 紧急程度: 需要立即修正
""")

print("="*80)