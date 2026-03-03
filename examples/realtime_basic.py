#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock实时数据模块 - 基本使用示例
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from instock.realtime import RealtimeDataManager, RealtimeAnalyzer

def main():
    print("="*80)
    print("myStock实时数据模块 - 基本使用示例")
    print("="*80)
    
    # 1. 初始化数据管理器
    data_manager = RealtimeDataManager()
    
    # 2. 创建实时数据表（如果不存在）
    data_manager.create_realtime_table()
    
    # 3. 获取单只股票实时数据
    print("\n📊 获取单只股票实时数据:")
    stock_code = "000034"  # 神州数码
    realtime_data = data_manager.get_realtime_data(stock_code)
    
    if realtime_data:
        print(f"股票代码: {realtime_data['code']}")
        print(f"股票名称: {realtime_data['name']}")
        print(f"当前价格: {realtime_data['current']:.2f}元")
        print(f"涨跌幅: {realtime_data.get('change_percent', 0):.2f}%")
        print(f"成交量: {realtime_data['volume']:,}")
        print(f"数据来源: {realtime_data['source']}")
        print(f"更新时间: {realtime_data['time']}")
    else:
        print(f"❌ 获取{stock_code}实时数据失败")
    
    # 4. 分析实时信号
    print("\n📈 分析实时信号:")
    analyzer = RealtimeAnalyzer(data_manager)
    signal = data_manager.analyze_realtime_signal(stock_code)
    
    if signal:
        print(f"股票: {signal['code']}/{signal['name']}")
        print(f"当前价: {signal['current_price']:.2f}元")
        print(f"涨跌幅: {signal['change_percent']:.2f}%")
        print(f"信号: {', '.join(signal['signals'])}")
        print(f"建议: {signal['recommendation']}")
        print(f"信心度: {signal['confidence']}")
    
    # 5. 批量获取实时数据
    print("\n📊 批量获取实时数据:")
    stock_codes = ["000034", "603949", "000001"]  # 神州数码、雪龙集团、平安银行
    batch_data = data_manager.batch_get_realtime(stock_codes)
    
    print(f"成功获取{len(batch_data)}只股票数据:")
    for code, data in batch_data.items():
        print(f"  {code}: {data['current']:.2f}元 ({data.get('change_percent', 0):.2f}%)")
    
    # 6. 生成实时报告
    print("\n📋 生成实时报告:")
    analyzer.generate_realtime_report(stock_codes)

if __name__ == "__main__":
    main()
