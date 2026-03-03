#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock实时数据模块 - 实时监控示例
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from instock.realtime import RealtimeDataManager

def simple_monitor(stock_codes, interval=30):
    """简单实时监控"""
    data_manager = RealtimeDataManager()
    
    print(f"🚀 启动实时监控，监控{len(stock_codes)}只股票")
    print(f"监控间隔: {interval}秒")
    print("按Ctrl+C停止监控\n")
    
    try:
        while True:
            print(f"\n📊 监控更新 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-"*60)
            
            for code in stock_codes:
                try:
                    data = data_manager.get_realtime_data(code, use_cache=False)
                    if data:
                        current = data.get('current', 0)
                        change = data.get('change_percent', 0)
                        volume = data.get('volume', 0)
                        
                        # 简单信号判断
                        if change > 2:
                            signal = "🟢 强势"
                        elif change > 0:
                            signal = "🟡 上涨"
                        elif change > -2:
                            signal = "⚪ 平稳"
                        else:
                            signal = "🔴 下跌"
                        
                        print(f"{signal} {code}: {current:.2f}元 ({change:+.2f}%) 成交量: {volume:,}")
                        
                        # 保存到数据库
                        data_manager.save_realtime_data(data)
                    
                    time.sleep(0.2)  # 避免请求过快
                    
                except Exception as e:
                    print(f"❌ {code}: 监控失败 - {e}")
            
            print("-"*60)
            print(f"下次更新: {interval}秒后")
            
            # 等待间隔时间
            for i in range(interval):
                time.sleep(1)
                if i % 10 == 0:
                    print(f"  ...等待{interval-i}秒", end='\r')
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")

def main():
    print("="*80)
    print("myStock实时数据模块 - 实时监控示例")
    print("="*80)
    
    # 初始化数据管理器
    data_manager = RealtimeDataManager()
    
    # 获取关注的股票
    stocks = data_manager.get_stock_list(limit=10)
    if not stocks:
        print("❌ 未找到股票数据")
        return
    
    stock_codes = [stock[0] for stock in stocks]
    print(f"监控股票: {', '.join(stock_codes)}")
    
    # 启动简单监控
    simple_monitor(stock_codes, interval=60)

if __name__ == "__main__":
    main()
