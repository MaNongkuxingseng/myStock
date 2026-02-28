#!/usr/bin/env python3
"""
增强版持仓分析 - 包含技术指标和深度分析
"""

import sys
import os
from datetime import datetime
import random

# 实际持仓数据
HOLDINGS = [
    {'code': '603949', 'name': '雪龙集团', 'quantity': 2900, 'cost_price': 20.597, 'current_price': 19.600, 'industry': '汽车零部件'},
    {'code': '600343', 'name': '航天动力', 'quantity': 800, 'cost_price': 35.871, 'current_price': 36.140, 'industry': '航天军工'},
    {'code': '002312', 'name': '川发龙蟒', 'quantity': 1600, 'cost_price': 13.324, 'current_price': 13.620, 'industry': '化工'}
]

class EnhancedPortfolioAnalyzer:
    """增强版持仓分析器"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 行业风险评级
        self.industry_risk = {
            '汽车零部件': {'risk': '中高', 'outlook': '中性', 'trend': '震荡'},
            '航天军工': {'risk': '高', 'outlook': '积极', 'trend': '上升'},
            '化工': {'risk': '中', 'outlook': '稳定', 'trend': '平稳'}
        }
    
    def calculate_basic_metrics(self):
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
    
    def generate_technical_indicators(self, code):
        """生成技术指标（模拟）"""
        # 基于代码的确定性随机
        random.seed(hash(code) % 1000)
        
        indicators = {
            'rsi': random.randint(30, 70),  # RSI相对强弱指数
            'macd_signal': random.choice(['金叉', '死叉', '中性']),
            'bollinger_position': random.choice(['上轨', '中轨', '下轨']),
            'volume_ratio': round(random.uniform(0.8, 1.5), 2),  # 量比
            'support_level': round(random.uniform(0.85, 0.98), 3),
            'resistance_level': round(random.uniform(1.02, 1.15), 3),
            'trend_strength': random.randint(40, 80),  # 趋势强度
            'volatility': round(random.uniform(0.02, 0.08), 4),  # 波动率
        }
        
        # 计算综合技术评分
        tech_score = 50  # 基础分
        
        # RSI评分
        if 40 <= indicators['rsi'] <= 60:
            tech_score += 15  # 正常区间
        elif indicators['rsi'] < 30:
            tech_score += 5   # 超卖
        elif indicators['rsi'] > 70:
            tech_score += 10  # 超买
        
        # MACD评分
        if indicators['macd_signal'] == '金叉':
            tech_score += 20
        elif indicators['macd_signal'] == '中性':
            tech_score += 10
        
        # 布林带位置评分
        if indicators['bollinger_position'] == '中轨':
            tech_score += 15
        elif indicators['bollinger_position'] == '下轨':
            tech_score += 10  # 可能有反弹
        
        # 量比评分
        if 0.9 <= indicators['volume_ratio'] <= 1.2:
            tech_score += 10  # 正常量能
        elif indicators['volume_ratio'] > 1.2:
            tech_score += 5   # 放量
        
        indicators['technical_score'] = min(100, max(0, tech_score))
        
        # 技术趋势判断
        if indicators['technical_score'] >= 70:
            indicators['trend'] = '强势'
            indicators['action'] = '持有或加仓'
        elif indicators['technical_score'] >= 50:
            indicators['trend'] = '中性'
            indicators['action'] = '观望'
        else:
            indicators['trend'] = '弱势'
            indicators['action'] = '减仓或止损'
        
        return indicators
    
    def analyze_risk_exposure(self, metrics):
        """分析风险暴露"""
        risk_analysis = {
            'concentration_risk': 0,
            'industry_concentration': {},
            'profit_risk': 0,
            'liquidity_concern': False
        }
        
        # 集中度风险
        weights = [h['weight'] for h in metrics['holdings']]
        risk_analysis['concentration_risk'] = max(weights)
        
        # 行业集中度
        industry_exposure = {}
        for h in metrics['holdings']:
            industry = h['industry']
            if industry not in industry_exposure:
                industry_exposure[industry] = 0
            industry_exposure[industry] += h['weight']
        
        risk_analysis['industry_concentration'] = industry_exposure
        
        # 盈亏风险
        losing_count = sum(1 for h in metrics['holdings'] if h['profit_loss_rate'] < 0)
        risk_analysis['profit_risk'] = (losing_count / len(metrics['holdings'])) * 100
        
        # 流动性关注
        risk_analysis['liquidity_concern'] = any(h['weight'] > 40 for h in metrics['holdings'])
        
        return risk_analysis
    
    def generate_trading_recommendations(self, metrics, risk_analysis):
        """生成交易建议"""
        recommendations = []
        
        # 整体盈亏建议
        if metrics['total_profit_rate'] > 10:
            recommendations.append({
                'type': 'profit_taking',
                'priority': '中',
                'message': f'组合整体盈利{metrics["total_profit_rate"]:.1f}%，考虑部分获利了结'
            })
        elif metrics['total_profit_rate'] < -5:
            recommendations.append({
                'type': 'risk_control',
                'priority': '高',
                'message': f'组合整体亏损{abs(metrics["total_profit_rate"]):.1f}%，建议加强风险控制'
            })
        
        # 集中度风险建议
        if risk_analysis['concentration_risk'] > 40:
            recommendations.append({
                'type': 'diversification',
                'priority': '高',
                'message': f'最大持仓权重{risk_analysis["concentration_risk"]:.1f}%，建议分散投资'
            })
        
        # 行业集中度建议
        if len(risk_analysis['industry_concentration']) < 3:
            recommendations.append({
                'type': 'industry_diversification',
                'priority': '中',
                'message': f'行业集中({len(risk_analysis["industry_concentration"])}个行业)，建议跨行业配置'
            })
        
        # 个股具体建议
        for h in metrics['holdings']:
            if h['profit_loss_rate'] < -8:
                recommendations.append({
                    'type': 'individual_stop_loss',
                    'priority': '高',
                    'stock': f'{h["code"]} {h["name"]}',
                    'message': f'亏损{h["profit_loss_rate"]:.1f}%，考虑止损'
                })
            elif h['weight'] > 35:
                recommendations.append({
                    'type': 'position_adjustment',
                    'priority': '中',
                    'stock': f'{h["code"]} {h["name"]}',
                    'message': f'仓位较重({h["weight"]:.1f}%)，建议适当减仓'
                })
        
        # 按优先级排序
        priority_order = {'高': 3, '中': 2, '低': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return recommendations[:5]  # 返回最重要的5个建议
    
    def generate_report(self):
        """生成增强版分析报告"""
        print("运行增强版持仓分析...")
        
        # 1. 计算基础指标
        metrics = self.calculate_basic_metrics()
        
        # 2. 生成技术指标
        for h in metrics['holdings']:
            h['technical'] = self.generate_technical_indicators(h['code'])
            h['industry_info'] = self.industry_risk.get(h['industry'], {})
        
        # 3. 分析风险
        risk_analysis = self.analyze_risk_exposure(metrics)
        
        # 4. 生成建议
        recommendations = self.generate_trading_recommendations(metrics, risk_analysis)
        
        # 5. 生成报告文本
        report = self.format_report(metrics, risk_analysis, recommendations)
        
        return report
    
    def format_report(self, metrics, risk_analysis, recommendations):
        """格式化报告"""
        report = f"📊 **myStock增强版持仓分析报告** {self.today}\n\n"
        
        # 组合概览
        report += "📈 **组合概览**\n"
        report += f"• 持仓数量: {len(metrics['holdings'])} 只\n"
        report += f"• 总市值: {metrics['total_value']:,.2f} 元\n"
        report += f"• 总成本: {metrics['total_cost']:,.2f} 元\n"
        report += f"• 总盈亏: {metrics['total_profit']:+,.2f} 元 ({metrics['total_profit_rate']:+.2f}%)\n\n"
        
        # 持仓明细
        report += "🔍 **持仓明细（含技术分析）**\n"
        
        for h in metrics['holdings']:
            # 盈亏状态
            if h['profit_loss_rate'] > 5:
                status_emoji = "🟢"
                status_text = "盈利"
            elif h['profit_loss_rate'] < -5:
                status_emoji = "🔴"
                status_text = "亏损"
            else:
                status_emoji = "🟡"
                status_text = "小幅波动"
            
            # 技术趋势
            tech = h['technical']
            if tech['technical_score'] >= 70:
                tech_emoji = "📈"
            elif tech['technical_score'] >= 50:
                tech_emoji = "➡️"
            else:
                tech_emoji = "📉"
            
            report += f"\n{tech_emoji} **{h['code']} {h['name']}** {status_emoji}\n"
            report += f"{status_emoji} 盈亏: {h['profit_loss_rate']:+.2f}% | 权重: {h['weight']:.1f}%\n"
            report += f"持仓: {h['quantity']}股 | 成本: {h['cost_price']:.3f} | 现价: {h['current_price']:.3f}\n"
            report += f"市值: {h['market_value']:,.2f}元 | 行业: {h['industry']}\n"
            
            # 技术指标
            report += f"技术评分: {tech['technical_score']}/100 ({tech['trend']})\n"
            report += f"RSI: {tech['rsi']} | MACD: {tech['macd_signal']} | 布林带: {tech['bollinger_position']}\n"
            report += f"支撑位: {h['current_price'] * tech['support_level']:.3f} | 阻力位: {h['current_price'] * tech['resistance_level']:.3f}\n"
            report += f"操作建议: {tech['action']}\n"
        
        # 风险分析
        report += f"\n⚠️ **风险分析**\n"
        report += f"• 集中度风险: {risk_analysis['concentration_risk']:.1f}% (最大持仓权重)\n"
        report += f"• 行业分布: {len(risk_analysis['industry_concentration'])}个行业\n"
        
        for industry, weight in risk_analysis['industry_concentration'].items():
            industry_risk = self.industry_risk.get(industry, {})
            risk_level = industry_risk.get('risk', '中')
            report += f"  - {industry}: {weight:.1f}% (风险: {risk_level})\n"
        
        report += f"• 亏损持仓: {risk_analysis['profit_risk']:.1f}%\n"
        if risk_analysis['liquidity_concern']:
            report += f"• 流动性关注: 存在重仓股\n"
        
        # 投资建议
        report += f"\n💡 **投资建议**\n"
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = "🔴" if rec['priority'] == '高' else "🟡" if rec['priority'] == '中' else "🟢"
                stock_info = f" ({rec['stock']})" if 'stock' in rec else ""
                report += f"{priority_emoji} 建议{i}{stock_info}: {rec['message']}\n"
        else:
            report += "🟢 当前持仓结构合理，无需重大调整\n"
        
        # 市场展望
        report += f"\n🌐 **市场展望**\n"
        for industry, info in self.industry_risk.items():
            if industry in risk_analysis['industry_concentration']:
                report += f"• {industry}: {info['outlook']}展望，{info['trend']}趋势\n"
        
        # 系统信息
        report += f"\n⚙️ **系统信息**\n"
        report += f"• 分析时间: {self.today}\n"
        report += f"• 数据源: 实际持仓数据 + 模拟技术指标\n"
        report += f"• 分析模型: 增强版多维度分析\n"
        report += f"• 下次分析: 今日收盘后 16:20\n\n"
        
        report += "---\n"
        report += "myStock智能分析系统 | 增强版分析报告\n"
        report += "注: 技术指标为模拟数据，实际投资请参考实时行情\n"
        
        return report

def main():
    """主函数"""
    analyzer = EnhancedPortfolioAnalyzer()
    
    print("="*70)
    print("myStock增强版持仓分析系统")
    print("="*70)
    
    report = analyzer.generate_report()
    
    print("\n分析完成！报告内容:")
    print("="*70)
    
    # 保存报告
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    today_date = datetime.now().strftime('%Y%m%d_%H%M')
    report_file = os.path.join(output_dir, f"enhanced_report_{today_date}.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存到: {report_file}")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        # 打印报告前500字符（避免编码问题）
        print(report[:1000])
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()