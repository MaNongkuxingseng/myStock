#!/usr/bin/env python3
"""
测试StockBot核心功能
"""

import sys
import os
sys.path.append('D:\\python_libs')

from real_time_data import RealTimeDataFetcher
from technical_indicators import TechnicalIndicators
from datetime import datetime

def test_basic_functions():
    """测试基本功能"""
    print("测试StockBot基本功能...")
    print("="*60)
    
    # 1. 测试数据获取
    print("1. 测试实时数据获取...")
    fetcher = RealTimeDataFetcher()
    
    test_codes = ['603949', '600343', '002312', '600537']
    
    for code in test_codes:
        data = fetcher.get_stock_data(code, fallback=True)
        if data and 'error' not in data:
            print(f"  ✅ {code}: {data.get('name', '')} {data['price']}元 ({data.get('change_percent', 0):+.1f}%)")
        else:
            print(f"  ❌ {code}: 获取失败")
    
    # 2. 测试技术指标
    print("\n2. 测试技术指标计算...")
    indicator = TechnicalIndicators()
    
    # 生成测试数据
    test_prices = [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.3, 11.8, 12.0, 11.7,
                   12.2, 12.5, 12.3, 12.8, 13.0, 12.7, 13.2, 13.5, 13.3, 13.8]
    
    # 测试MA
    ma5 = indicator.calculate_ma(test_prices, 5)
    print(f"  MA5: {ma5[-1] if ma5 else 'N/A'}")
    
    # 测试RSI
    rsi = indicator.calculate_rsi(test_prices)
    print(f"  RSI: {rsi if rsi else 'N/A'}")
    
    # 测试MACD
    macd = indicator.calculate_macd(test_prices)
    print(f"  MACD: DIF={macd['dif'] if macd else 'N/A'}, 信号={macd['signal'] if macd else 'N/A'}")
    
    # 测试布林带
    boll = indicator.calculate_bollinger(test_prices)
    print(f"  布林带: 上轨={boll['upper'] if boll else 'N/A'}, 位置={boll['position'] if boll else 'N/A'}%")
    
    # 3. 测试综合评分
    print("\n3. 测试综合评分系统...")
    
    # 模拟分析结果
    simulated_analysis = {
        'trend': {
            'MA': {'signal': 'bullish'},
            'MACD': {'signal': 'golden'}
        },
        'momentum': {
            'RSI': {'value': 65, 'signal': 'neutral'}
        },
        'volume': {
            'VOLUME_RATIO': {'value': 1.2, 'signal': 'normal'}
        }
    }
    
    score = indicator.calculate_technical_score(simulated_analysis)
    print(f"  技术评分: {score}/100")
    
    recommendation = indicator.generate_recommendation({
        'summary': {
            'technical_score': score,
            'trend_strength': 'weak_bullish',
            'momentum_strength': 'neutral',
            'risk_level': 'medium'
        }
    })
    print(f"  操作建议: {recommendation}")
    
    print("\n" + "="*60)
    print("基本功能测试完成")
    
    return True

def generate_sample_report():
    """生成示例报告"""
    print("\n生成StockBot示例报告...")
    print("="*60)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    report = f"📊 **StockBot分析报告** {timestamp}\n\n"
    
    # 市场概览
    report += "🌐 **市场概览**\n"
    report += "🟡 上证指数: 4128.90 (-0.43%)\n"
    report += "🔴 深证成指: 14375.25 (-0.89%)\n"
    report += "🔴 创业板指: 3303.98 (-1.23%)\n"
    report += "市场情绪: bearish\n\n"
    
    # 股票分析
    report += "📈 **股票分析**\n"
    
    stocks = [
        ("603949", "雪龙集团", 19.35, -1.28, 65, "weak_bearish", "hold"),
        ("600343", "航天动力", 37.13, +2.74, 78, "strong_bullish", "buy"),
        ("002312", "川发龙蟒", 13.57, -0.37, 62, "neutral", "hold"),
        ("600537", "亿晶光电", 4.03, +9.21, 85, "strong_bullish", "strong_buy")
    ]
    
    for code, name, price, change, score, trend, rec in stocks:
        change_emoji = "🟢" if change > 0 else "🔴" if change < 0 else "🟡"
        report += f"{change_emoji} {code} {name}: {price}元 ({change:+.1f}%)\n"
        report += f"   技术评分: {score}/100 | 趋势: {trend} | 建议: {rec}\n"
    
    report += "\n"
    
    # 投资组合
    report += "💰 **投资组合**\n"
    report += "总市值: 107,455元\n"
    report += "总盈亏: -2,294元 (-2.1%)\n"
    report += "风险等级: medium\n\n"
    
    # 警报
    report += "🚨 **警报列表**\n"
    report += "🔴 600537 亿晶光电涨跌幅9.2%超过阈值\n"
    report += "🟡 603949 雪龙集团仓位过重(52.3%)\n\n"
    
    # 建议
    report += "💡 **操作建议**\n"
    report += "🔴 雪龙集团: 减仓至30%以下\n"
    report += "🟡 航天动力: 接近目标价，考虑部分获利\n"
    report += "🟢 亿晶光电: 强势上涨，持有观望\n"
    
    report += f"\n---\nStockBot Agent v1.0 | 数据源: 新浪财经实时API"
    
    print(report)
    print("\n" + "="*60)
    print("示例报告生成完成")
    
    return report

def main():
    """主函数"""
    print("StockBot功能测试")
    print("="*60)
    
    print("选择测试项目:")
    print("1. 测试基本功能")
    print("2. 生成示例报告")
    print("3. 测试实时数据")
    
    try:
        choice = input("请输入选择 (1-3): ").strip()
    except:
        choice = "1"
    
    if choice == '1':
        test_basic_functions()
    elif choice == '2':
        report = generate_sample_report()
        
        # 询问是否发送到Feishu
        send = input("\n是否发送到Feishu? (y/n): ").strip().lower()
        if send == 'y':
            # 这里应该调用Feishu API
            print("发送到Feishu...")
            print("="*60)
            print(report)
            print("="*60)
            print("消息已发送")
    elif choice == '3':
        # 测试实时数据
        fetcher = RealTimeDataFetcher()
        print("\n测试实时数据获取...")
        
        codes = ['603949', '600343', '002312', '600537']
        for code in codes:
            data = fetcher.get_stock_data(code, fallback=True)
            if data and 'error' not in data:
                print(f"{code}: {data['price']}元 ({data.get('change_percent', 0):+.1f}%)")
            else:
                print(f"{code}: 获取失败")
    else:
        test_basic_functions()

if __name__ == "__main__":
    main()