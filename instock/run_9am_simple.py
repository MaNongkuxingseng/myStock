#!/usr/bin/env python3
"""
简化版9点分析脚本（无表情符号，避免编码问题）
"""

import sys
import os
from datetime import datetime

# 实际持仓数据
HOLDINGS = [
    {'code': '603949', 'name': '雪龙集团', 'quantity': 2900, 'cost_price': 20.597, 'current_price': 19.600, 'industry': '汽车零部件'},
    {'code': '600343', 'name': '航天动力', 'quantity': 800, 'cost_price': 35.871, 'current_price': 36.140, 'industry': '航天军工'},
    {'code': '002312', 'name': '川发龙蟒', 'quantity': 1600, 'cost_price': 13.324, 'current_price': 13.620, 'industry': '化工'}
]

def calculate_metrics():
    """计算基础指标"""
    total_value = 0
    total_cost = 0
    
    for h in HOLDINGS:
        h['market_value'] = h['quantity'] * h['current_price']
        h['cost_value'] = h['quantity'] * h['cost_price']
        h['profit_loss'] = h['market_value'] - h['cost_value']
        h['profit_loss_rate'] = (h['profit_loss'] / h['cost_value']) * 100
        
        total_value += h['market_value']
        total_cost += h['cost_value']
    
    for h in HOLDINGS:
        h['weight'] = (h['market_value'] / total_value) * 100
    
    total_profit = total_value - total_cost
    total_profit_rate = (total_profit / total_cost) * 100
    
    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'total_profit_rate': total_profit_rate,
        'holdings': HOLDINGS
    }

def generate_report(metrics):
    """生成报告"""
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    report = f"myStock持仓分析报告 {today}\n\n"
    report += "组合概览\n"
    report += f"• 持仓数量: {len(metrics['holdings'])} 只\n"
    report += f"• 总市值: {metrics['total_value']:,.2f} 元\n"
    report += f"• 总成本: {metrics['total_cost']:,.2f} 元\n"
    report += f"• 总盈亏: {metrics['total_profit']:+,.2f} 元 ({metrics['total_profit_rate']:+.2f}%)\n\n"
    
    report += "持仓明细\n"
    for h in metrics['holdings']:
        status = "盈利" if h['profit_loss_rate'] > 0 else "亏损"
        report += f"{h['code']} {h['name']}\n"
        report += f"  持仓: {h['quantity']}股 | 成本: {h['cost_price']:.3f} | 现价: {h['current_price']:.3f}\n"
        report += f"  市值: {h['market_value']:,.2f}元 | {status}: {abs(h['profit_loss_rate']):.2f}% | 权重: {h['weight']:.1f}%\n"
        report += f"  行业: {h['industry']}\n\n"
    
    # 风险提示
    report += "风险提示\n"
    for h in metrics['holdings']:
        if h['profit_loss_rate'] < -5:
            report += f"• {h['code']} {h['name']}: 亏损{h['profit_loss_rate']:.2f}%，需关注\n"
        if h['weight'] > 30:
            report += f"• {h['code']} {h['name']}: 仓位较重({h['weight']:.1f}%)，注意分散风险\n"
    
    report += f"\n系统状态\n"
    report += f"• 分析时间: {today}\n"
    report += f"• 数据源: 实际持仓数据\n"
    report += f"• 推送机制: 定时任务\n\n"
    
    report += "---\n"
    report += "myStock智能分析系统 | 早上9点报告\n"
    report += f"下次报告: 今日收盘后 16:20\n"
    
    return report

def main():
    """主函数"""
    print("="*70)
    print("myStock早上9点持仓分析")
    print("="*70)
    
    # 计算指标
    print("\n计算持仓指标...")
    metrics = calculate_metrics()
    
    print(f"总市值: {metrics['total_value']:,.2f}元")
    print(f"总盈亏: {metrics['total_profit']:+,.2f}元 ({metrics['total_profit_rate']:+.2f}%)")
    
    # 生成报告
    print("\n生成分析报告...")
    report = generate_report(metrics)
    
    print(f"报告生成完成，长度: {len(report)} 字符")
    
    # 保存报告
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    report_file = os.path.join(output_dir, f"9am_report_{today_date}.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告保存到: {report_file}")
    
    # 显示摘要
    print("\n" + "="*70)
    print("报告摘要:")
    print("="*70)
    print(report[:500] + "..." if len(report) > 500 else report)
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        print("\n" + "="*70)
        print("分析完成！可配置定时任务自动运行。")
        print("="*70)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()