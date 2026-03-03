#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据抓取任务
每5分钟抓取一次关注的股票实时数据
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

from instock.realtime import RealtimeDataManager

def main():
    """主函数"""
    print("="*80)
    print("实时数据抓取任务")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 初始化数据管理器
    data_manager = RealtimeDataManager()
    
    # 确保实时数据表存在
    data_manager.create_realtime_table()
    
    # 获取关注的股票（前50只）
    stocks = data_manager.get_stock_list(limit=50)
    if not stocks:
        print("❌ 未找到股票数据")
        return
    
    stock_codes = [stock[0] for stock in stocks]
    print(f"✅ 获取到{len(stock_codes)}只关注股票")
    
    # 抓取实时数据
    success_count = 0
    fail_count = 0
    
    for code in stock_codes:
        try:
            data = data_manager.get_realtime_data(code, use_cache=False)
            if data:
                # 保存到数据库
                if data_manager.save_realtime_data(data):
                    success_count += 1
                    print(f"  ✅ {code}: {data.get('current', 0):.2f}元")
                else:
                    fail_count += 1
                    print(f"  ❌ {code}: 保存失败")
            else:
                fail_count += 1
                print(f"  ❌ {code}: 获取数据失败")
            
            # 避免请求过快
            time.sleep(0.2)
            
        except Exception as e:
            fail_count += 1
            print(f"  ❌ {code}: 异常 - {e}")
    
    print(f"\n📊 抓取结果:")
    print(f"  成功: {success_count}只")
    print(f"  失败: {fail_count}只")
    print(f"  成功率: {success_count/(success_count+fail_count)*100:.1f}%")
    
    print(f"\n✅ 任务完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
