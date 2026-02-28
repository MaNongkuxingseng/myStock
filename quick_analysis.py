#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock快速持仓分析脚本
用于紧急情况下的持仓分析
"""

import datetime
import json

def analyze_holdings():
    """分析实际持仓"""
    # 实际持仓数据
    holdings = [
        {'code': '603949', 'name': '雪龙集团', 'shares': 2900, 'cost': 20.597, 'current_price': 19.60},
        {'code': '600343', 'name': '航天动力', 'shares': 800, 'cost': 35.871, 'current_price': 36.14},
        {'code': '002312', 'name': '川发龙蟒', 'shares': 1600, 'cost': 13.324, 'current_price': 13.62}
    ]
    
    # 计算持仓分析
    total_value = 0
    total_cost = 0
    analysis_results = []
    
    for stock in holdings:
        stock_value = stock['shares'] * stock['current_price']
        stock_cost = stock['shares'] * stock['cost']
        stock_pnl = stock_value - stock_cost
        stock_pnl_pct = (stock_pnl / stock_cost) * 100 if stock_cost > 0 else 0
        stock_weight = (stock_value / (sum(h['shares'] * h['current_price'] for h in holdings))) * 100
        
        total_value += stock_value
        total_cost += stock_cost
        
        analysis_results.append({
            'code': stock['code'],
            'name': stock['name'],
            'shares': stock['shares'],
            'cost': stock['cost'],
            'current_price': stock['current_price'],
            'value': stock_value,
            'pnl': stock_pnl,
            'pnl_pct': stock_pnl_pct,
            'weight': stock_weight
        })
    
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
    
    # 生成分析报告
    report = []
    report.append("=" * 60)
    report.append(f"📊 myStock快速持仓分析报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    report.append("")
    
    report.append("🔍 持仓明细:")
    report.append("")
    
    for stock in analysis_results:
        emoji = "🟢" if stock['pnl_pct'] >= 0 else "🔴"
        report.append(f"{emoji} {stock['code']} {stock['name']}")
        report.append(f"   持仓: {stock['shares']}股 | 成本: {stock['cost']:.3f}元 | 现价: {stock['current_price']:.3f}元")
        report.append(f"   市值: {stock['value']:.2f}元 | 权重: {stock['weight']:.1f}%")
        report.append(f"   盈亏: {stock['pnl']:+.2f}元 ({stock['pnl_pct']:+.2f}%)")
        report.append("")
    
    report.append("📈 组合汇总:")
    report.append(f"   总市值: {total_value:.2f}元")
    report.append(f"   总成本: {total_cost:.2f}元")
    report.append(f"   总盈亏: {total_pnl:+.2f}元 ({total_pnl_pct:+.2f}%)")
    report.append("")
    
    # 风险分析
    max_weight_stock = max(analysis_results, key=lambda x: x['weight'])
    losing_stocks = [s for s in analysis_results if s['pnl_pct'] < 0]
    
    report.append("⚠️ 风险提示:")
    report.append(f"   1. 集中度风险: {max_weight_stock['name']}权重{max_weight_stock['weight']:.1f}% (建议<30%)")
    report.append(f"   2. 亏损持仓: {len(losing_stocks)}/{len(holdings)}只")
    if losing_stocks:
        report.append(f"      - {', '.join([s['name'] for s in losing_stocks])}")
    report.append("")
    
    # 操作建议
    report.append("💡 操作建议:")
    if max_weight_stock['weight'] > 40:
        report.append(f"   1. 立即减仓: {max_weight_stock['name']} (当前权重{max_weight_stock['weight']:.1f}%)")
        report.append(f"      - 建议减仓至30%以下")
    else:
        report.append("   1. 持仓结构相对合理，可继续持有")
    
    if total_pnl_pct < -5:
        report.append("   2. 组合整体亏损，建议调整持仓结构")
    elif total_pnl_pct > 5:
        report.append("   2. 组合盈利良好，可考虑部分止盈")
    else:
        report.append("   2. 组合盈亏平衡，建议观望")
    
    report.append("")
    report.append("⏰ 下次分析: 今日收盘后 16:20")
    report.append("=" * 60)
    
    return "\n".join(report)

def main():
    """主函数"""
    try:
        report = analyze_holdings()
        print(report)
        
        # 保存报告
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        report_file = f"quick_analysis_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 分析报告已保存: {report_file}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    main()