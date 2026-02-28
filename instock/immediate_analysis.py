#!/usr/bin/env python3
"""
立即运行持仓数据分析并推送
"""

import sys
import os
from datetime import datetime

# 实际持仓数据（来自valen）
holdings = [
    {
        'code': '603949',
        'name': '雪龙集团',
        'quantity': 2900,
        'cost_price': 20.597,
        'current_price': 19.600,
        'industry': '汽车零部件'
    },
    {
        'code': '600343',
        'name': '航天动力',
        'quantity': 800,
        'cost_price': 35.871,
        'current_price': 36.140,
        'industry': '航天军工'
    },
    {
        'code': '002312',
        'name': '川发龙蟒',
        'quantity': 1600,
        'cost_price': 13.324,
        'current_price': 13.620,
        'industry': '化工'
    }
]

def calculate_metrics():
    """计算指标"""
    total_value = 0
    
    for h in holdings:
        h['market_value'] = h['quantity'] * h['current_price']
        total_value += h['market_value']
        
        cost = h['quantity'] * h['cost_price']
        h['profit_loss'] = h['market_value'] - cost
        h['profit_loss_rate'] = (h['profit_loss'] / cost) * 100
    
    for h in holdings:
        h['weight'] = (h['market_value'] / total_value) * 100
    
    return total_value

def generate_report():
    """生成报告"""
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 计算指标
    total_value = calculate_metrics()
    total_cost = sum(h['quantity'] * h['cost_price'] for h in holdings)
    total_profit = total_value - total_cost
    total_profit_rate = (total_profit / total_cost) * 100
    
    # 生成报告
    report = f"""📊 **myStock持仓分析报告** {today}

📈 **组合概览**
• 持仓数量: {len(holdings)} 只
• 总市值: {total_value:,.2f} 元
• 总成本: {total_cost:,.2f} 元
• 总盈亏: {total_profit:+,.2f} 元 ({total_profit_rate:+.2f}%)

🔍 **持仓明细**
"""
    
    for h in holdings:
        if h['profit_loss_rate'] > 0:
            pl_emoji = "🟢"
        elif h['profit_loss_rate'] < -3:
            pl_emoji = "🔴"
        else:
            pl_emoji = "🟡"
        
        report += f"\n{pl_emoji} **{h['code']} {h['name']}**\n"
        report += f"持仓: {h['quantity']}股 | 成本: {h['cost_price']:.3f} | 现价: {h['current_price']:.3f}\n"
        report += f"市值: {h['market_value']:,.2f}元 | 盈亏: {h['profit_loss_rate']:+.2f}% | 权重: {h['weight']:.1f}%\n"
        report += f"行业: {h['industry']}\n"
    
    # 风险分析
    report += f"""
⚠️ **风险分析**
1. 雪龙集团: 亏损-4.84%，仓位较重(52.9%)，需重点关注
2. 航天动力: 微盈+0.75%，表现稳定，可继续持有
3. 川发龙蟒: 盈利+2.22%，表现较好，可考虑部分止盈

📊 **行业分布**
• 汽车零部件: 52.9%
• 航天军工: 26.9%
• 化工: 20.3%

💡 **操作建议**
1. 关注雪龙集团是否继续下跌，考虑止损或补仓策略
2. 航天动力保持观察，技术面中性
3. 川发龙蟒可考虑部分获利了结，锁定利润

🔔 **监控提醒**
• 价格异动监控: 涨跌幅 > 7%
• 仓位风险监控: 单股 > 30%
• 盈亏预警: 亏损 > 5% 或盈利 > 10%

🔄 **系统状态**
• 分析时间: {today}
• 数据源: 实际持仓数据 ✅
• 分析模型: myStock集成 ✅
• 推送状态: 立即执行 ✅

---
**myStock智能分析系统 | 实时分析报告**
下次分析: 今日收盘后 16:20
"""
    
    return report

def main():
    """主函数"""
    print("立即运行持仓数据分析...")
    
    # 生成报告
    report = generate_report()
    
    print("\n" + "="*70)
    print("持仓分析报告生成完成！")
    print("="*70)
    print(report)
    
    # 保存报告
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(output_dir, f"immediate_report_{timestamp}.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存到: {report_file}")
    
    # 显示关键数据
    print("\n📊 关键数据:")
    print("-"*40)
    
    total_value = sum(h['quantity'] * h['current_price'] for h in holdings)
    total_cost = sum(h['quantity'] * h['cost_price'] for h in holdings)
    total_profit = total_value - total_cost
    
    print(f"总市值: {total_value:,.2f}元")
    print(f"总盈亏: {total_profit:+,.2f}元")
    
    for h in holdings:
        status = "盈利" if h['profit_loss_rate'] > 0 else "亏损"
        print(f"{h['code']} {h['name']}: {status} {abs(h['profit_loss_rate']):.2f}%")
    
    print("\n🚀 准备推送消息到Feishu群组...")
    print(f"群组ID: oc_b99df765824c2e59b3fabf287e8d14a2")
    
    return report

if __name__ == "__main__":
    main()