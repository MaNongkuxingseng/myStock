#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock实时数据更新脚本
"""

import pymysql
from datetime import datetime
import time

def create_realtime_table():
    """创建实时数据表"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='785091',
            database='instockdb',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 创建实时数据表
        create_sql = """
        CREATE TABLE IF NOT EXISTS stock_realtime (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_code VARCHAR(10) NOT NULL,
            stock_name VARCHAR(50),
            current_price DECIMAL(10,2),
            change_rate DECIMAL(10,2),
            volume BIGINT,
            amount DECIMAL(15,2),
            update_time DATETIME NOT NULL,
            data_source VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_stock_code (stock_code),
            INDEX idx_update_time (update_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        cursor.execute(create_sql)
        conn.commit()
        
        print("实时数据表创建成功")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"创建实时数据表失败: {e}")
        return False

def update_stock_realtime(stock_code, price_data):
    """更新股票实时数据"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='785091',
            database='instockdb',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO stock_realtime 
        (stock_code, stock_name, current_price, change_rate, volume, amount, update_time, data_source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            stock_code,
            price_data.get('name', ''),
            price_data.get('price', 0),
            price_data.get('change_rate', 0),
            price_data.get('volume', 0),
            price_data.get('amount', 0),
            datetime.now(),
            price_data.get('source', 'manual')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"更新{stock_code}实时数据成功")
        return True
        
    except Exception as e:
        print(f"更新{stock_code}实时数据失败: {e}")
        return False

def get_latest_stock_data():
    """获取最新股票数据（模拟）"""
    # 在实际应用中，这里应该调用实时数据API
    # 暂时返回模拟数据
    
    return [
        {
            'code': '000034',
            'name': '神州数码',
            'price': 40.30,
            'change_rate': -0.81,
            'volume': 1000000,
            'amount': 40300000,
            'source': 'simulated'
        },
        {
            'code': '603949',
            'name': '雪龙集团',
            'price': 18.73,
            'change_rate': -2.70,
            'volume': 500000,
            'amount': 9365000,
            'source': 'simulated'
        }
    ]

def main():
    """主函数"""
    print("="*80)
    print("myStock实时数据更新系统")
    print("="*80)
    
    # 1. 创建实时数据表
    print("\n1. 检查实时数据表...")
    if create_realtime_table():
        print("  实时数据表检查完成")
    else:
        print("  实时数据表创建失败")
        return
    
    # 2. 获取实时数据
    print("\n2. 获取实时数据...")
    stock_data = get_latest_stock_data()
    print(f"  获取到{len(stock_data)}只股票数据")
    
    # 3. 更新数据
    print("\n3. 更新实时数据...")
    success_count = 0
    for data in stock_data:
        if update_stock_realtime(data['code'], data):
            success_count += 1
    
    print(f"\n更新完成: {success_count}/{len(stock_data)} 成功")
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 4. 显示更新结果
    print("\n4. 更新结果:")
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='785091',
            database='instockdb',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        query = """
        SELECT stock_code, stock_name, current_price, change_rate, update_time
        FROM stock_realtime
        ORDER BY update_time DESC
        LIMIT 5
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("  最新5条实时数据:")
        for row in results:
            print(f"    {row[0]}/{row[1]}: {row[2]:.2f}元 ({row[3]:+.2f}%) - {row[4]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  查询实时数据失败: {e}")
    
    print("\n" + "="*80)
    print("系统优化说明:")
    print("="*80)
    print("\n已完成的优化:")
    print("  1. 创建实时数据表结构")
    print("  2. 实现实时数据更新功能")
    print("  3. 集成到现有myStock系统")
    print("  4. 提供实时数据分析接口")
    
    print("\n下一步优化建议:")
    print("  1. 集成真实实时数据API（新浪、腾讯等）")
    print("  2. 实现定时自动更新")
    print("  3. 添加实时信号预警")
    print("  4. 创建Web监控界面")
    
    print("\n使用方法:")
    print("  1. 运行实时分析: python real_time_core.py")
    print("  2. 更新实时数据: python update_realtime.py")
    print("  3. 定时任务: 可配置cron或计划任务")

if __name__ == "__main__":
    main()