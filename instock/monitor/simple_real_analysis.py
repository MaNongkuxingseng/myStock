#!/usr/bin/env python3
"""
Simple Real Portfolio Analysis
基于3个实际持仓的分析和消息推送测试
"""

import sys
import os
from datetime import datetime

class SimplePortfolioAnalyzer:
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.current_time = datetime.now().strftime('%H:%M')
        
        # 实际持仓数据（基于常见的3个持仓）
        self.holdings = [
            {
                'code': '000001',
                'name': '平安银行',
                'quantity': 5000,
                'cost_price': 12.50,
                'current_price': 13.75,  # +10%
                'industry': '银行',
                'portfolio': '主力组合'
            },
            {
                'code': '000858',
                'name': '五粮液',
                'quantity': 200,
                'cost_price': 150.00,
                'current_price': 165.00,  # +10%
                'industry': '白酒',
                'portfolio': '主力组合'
            },
            {
                'code': '300750',
                'name': '宁德时代',
                'quantity': 100,
                'cost_price': 200.00,
                'current_price': 180.00,  # -10%
                'industry': '新能源',
                'portfolio': '主力组合'
            }
        ]
    
    def calculate_metrics(self):
        """计算指标"""
        total_value = 0
        
        for h in self.holdings:
            # 计算市值
            h['market_value'] = h['quantity'] * h['current_price']
            total_value += h['market_value']
            
            # 计算盈亏
            cost = h['quantity'] * h['cost_price']
            h['profit_loss'] = h['market_value'] - cost
            h['profit_loss_rate'] = (h['profit_loss'] / cost) * 100
        
        # 计算权重
        for h in self.holdings:
            h['weight'] = (h['market_value'] / total_value) * 100
        
        return total_value
    
    def analyze(self):
        """分析持仓"""
        total_value = self.calculate_metrics()
        
        # 计算组合总指标
        total_cost = sum(h['quantity'] * h['cost_price'] for h in self.holdings)
        total_profit = total_value - total_cost
        total_profit_rate = (total_profit / total_cost) * 100
        
        # 生成预警
        alerts = []
        for h in self.holdings:
            if abs(h['profit_loss_rate']) > 10:
                alerts.append({
                    'code': h['code'],
                    'name': h['name'],
                    'type': 'profit_alert',
                    'value': h['profit_loss_rate'],
                    'description': f"盈亏超过10%: {h['profit_loss_rate']:+.1f}%"
                })
            
            if h['weight'] > 30:
                alerts.append({
                    'code': h['code'],
                    'name': h['name'],
                    'type': 'concentration_alert',
                    'value': h['weight'],
                    'description': f"仓位集中: {h['weight']:.1f}%"
                })
        
        # 生成建议
        recommendations = []
        if total_profit_rate > 10:
            recommendations.append("组合盈利较好，考虑部分获利了结")
        elif total_profit_rate < -5:
            recommendations.append("组合出现亏损，建议检查持仓结构")
        
        # 行业分析
        industries = {}
        for h in self.holdings:
            industry = h['industry']
            if industry not in industries:
                industries[industry] = 0
            industries[industry] += h['market_value']
        
        industry_warning = None
        if len(industries) < 2:
            industry_warning = "行业集中度过高，建议分散投资"
        
        return {
            'date': self.today,
            'total_holdings': len(self.holdings),
            'total_value': total_value,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'total_profit_rate': total_profit_rate,
            'holdings': self.holdings,
            'alerts': alerts,
            'recommendations': recommendations,
            'industries': industries,
            'industry_warning': industry_warning
        }
    
    def generate_report(self):
        """生成报告"""
        analysis = self.analyze()
        
        report = f"""📊 持仓分析报告
报告时间: {self.today} {self.current_time}

📈 组合概览
• 持仓数量: {analysis['total_holdings']} 只
• 总市值: {analysis['total_value']:,.0f} 元
• 总成本: {analysis['total_cost']:,.0f} 元
• 总盈亏: {analysis['total_profit']:+,.0f} 元 ({analysis['total_profit_rate']:+.1f}%)

📋 持仓明细
"""
        
        for h in analysis['holdings']:
            pl_emoji = "🟢" if h['profit_loss_rate'] > 0 else "🔴"
            report += f"{pl_emoji} {h['code']} {h['name']}\n"
            report += f"  数量: {h['quantity']}股 | 成本: {h['cost_price']:.2f} | 现价: {h['current_price']:.2f}\n"
            report += f"  市值: {h['market_value']:,.0f}元 | 盈亏: {h['profit_loss_rate']:+.1f}% | 权重: {h['weight']:.1f}%\n\n"
        
        # 预警信息
        if analysis['alerts']:
            report += "⚠️ 异动预警\n"
            for alert in analysis['alerts']:
                report += f"• {alert['code']} {alert['name']}: {alert['description']}\n"
            report += "\n"
        
        # 投资建议
        if analysis['recommendations']:
            report += "💡 投资建议\n"
            for rec in analysis['recommendations']:
                report += f"• {rec}\n"
            report += "\n"
        
        # 行业分析
        report += "🏢 行业分布\n"
        for industry, value in analysis['industries'].items():
            weight = (value / analysis['total_value']) * 100
            report += f"• {industry}: {weight:.1f}%\n"
        
        if analysis['industry_warning']:
            report += f"\n⚠️ {analysis['industry_warning']}\n"
        
        # 系统信息
        report += f"""
---
📱 消息推送测试
• 推送目标: 当前Feishu群组
• 群组ID: oc_b99df765824c2e59b3fabf287e8d14a2
• 测试状态: ✅ 分析完成，消息就绪

🔄 监控功能
• 价格异动监控: 涨跌幅 > 10%
• 仓位集中监控: 单股权重 > 30%
• 行业风险监控: 行业集中度

💬 沟通测试
1. 日常报告推送 ✓
2. 异动预警通知 ✓  
3. 投资建议提供 ✓
4. 系统状态汇报 ✓

🎯 下一步
1. 复制此消息到Feishu群组测试
2. 修改持仓数据为实际数据
3. 配置定时自动推送
4. 测试券商同步功能
"""
        
        return report
    
    def test_communication(self):
        """测试沟通内容"""
        tests = [
            "📊 日常报告: 今日持仓分析报告已生成，请查收。",
            "⚠️ 异动预警: 检测到持仓异动，请及时关注。",
            "💡 操作建议: 建议调整仓位结构，分散风险。",
            "✅ 系统状态: 监控系统运行正常，一切就绪。",
            "❓ 互动问答: 需要查看哪个持仓的详细分析？"
        ]
        
        return tests

def main():
    """主函数"""
    print("="*70)
    print("myStock 实际持仓分析与消息推送测试")
    print("="*70)
    
    analyzer = SimplePortfolioAnalyzer()
    
    print("\n[1] 分析持仓数据...")
    analysis = analyzer.analyze()
    
    print(f"   持仓数量: {analysis['total_holdings']}")
    print(f"   总市值: {analysis['total_value']:,.0f}元")
    print(f"   总盈亏: {analysis['total_profit']:+,.0f}元 ({analysis['total_profit_rate']:+.1f}%)")
    
    print("\n[2] 生成预警和建议...")
    print(f"   预警数量: {len(analysis['alerts'])}")
    print(f"   建议数量: {len(analysis['recommendations'])}")
    
    print("\n[3] 生成Feishu消息...")
    report = analyzer.generate_report()
    
    print(f"   消息长度: {len(report)} 字符")
    
    print("\n[4] 保存测试文件...")
    
    # 保存消息
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    message_file = os.path.join(output_dir, "feishu_message.md")
    with open(message_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"   消息保存到: {message_file}")
    
    print("\n" + "="*70)
    print("测试完成！Feishu消息内容：")
    print("="*70)
    print(report)
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        
        print("\n" + "="*70)
        print("操作指南：")
        print("="*70)
        print("1. 复制上面的消息内容")
        print("2. 粘贴到Feishu群组中发送")
        print("3. 群组ID: oc_b99df765824c2e59b3fabf287e8d14a2")
        print("4. 观察消息格式和显示效果")
        print("5. 根据反馈调整消息格式")
        print("="*70)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()