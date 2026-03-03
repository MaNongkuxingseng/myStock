#!/usr/bin/env python3
"""
快速分析昨日数据并生成开盘报告
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def main():
    print("快速分析昨日数据...")
    
    # 加载现有数据
    df = pd.read_csv("stock_data.csv", encoding='utf-8-sig')
    print(f"数据加载成功: {len(df)} 行, {len(df.columns)} 列")
    
    # 持仓股
    holdings = [
        {'code': '000731', 'name': '四川美丰'},
        {'code': '600118', 'name': '中国卫星'},
        {'code': '600157', 'name': '永泰能源'}
    ]
    
    # 分析每只持仓股
    reports = []
    
    for stock in holdings:
        code = stock['code']
        
        # 在数据中查找（尝试前6位匹配）
        mask = df['code'].astype(str).str[:6] == code
        if mask.any():
            stock_data = df[mask]
            latest = stock_data.iloc[-1]
            
            report = f"""
🔹 {stock['name']} ({code})
昨日收盘价: {latest.get('new_price', 'N/A')}
涨跌幅: {latest.get('change_rate', 'N/A')}%
最高价: {latest.get('high', 'N/A')}
最低价: {latest.get('low', 'N/A')}
成交量: {latest.get('volume', 'N/A')}
"""
            reports.append(report)
        else:
            reports.append(f"\n🔹 {stock['name']} ({code}): 未找到数据")
    
    # 生成完整报告
    full_report = f"""📊 基于昨日数据的开盘分析报告
生成时间: {datetime.now().strftime('%H:%M:%S')}
========================================

📈 市场概况
昨日全市场数据: {len(df)} 只股票
今日关注: 开盘价与昨日收盘价对比

📋 持仓股昨日数据汇总
"""
    
    for report in reports:
        full_report += report
    
    full_report += """

🎯 今日开盘操作建议
1. 观察集合竞价（09:15-09:25）
2. 对比昨日收盘价与今日开盘价
3. 关注成交量是否放大
4. 根据技术信号决定操作

⚠️ 风险提示
• 开盘波动较大，谨慎操作
• 设置好止损位
• 控制仓位风险

📞 09:30将发送基于实时数据的详细开盘分析
"""
    
    # 保存报告
    with open("opening_report_0930_preview.txt", "w", encoding="utf-8") as f:
        f.write(full_report)
    
    print("报告已生成: opening_report_0930_preview.txt")
    
    # 显示报告预览
    print("\n" + "="*60)
    print("报告预览:")
    print("="*60)
    print(full_report[:500] + "...")
    
    return full_report

if __name__ == "__main__":
    report = main()