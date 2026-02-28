#!/usr/bin/env python3
"""
简化版实时分析 - 不依赖外部库
"""

import sys
import os
from datetime import datetime
import random

class SimpleRealtimeAnalyzer:
    """简化版实时分析器"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 实际持仓数据
        self.holdings = [
            {'code': '603949', 'name': '雪龙集团', 'quantity': 2900, 'cost_price': 20.597, 'industry': '汽车零部件'},
            {'code': '600343', 'name': '航天动力', 'quantity': 800, 'cost_price': 35.871, 'industry': '航天军工'},
            {'code': '002312', 'name': '川发龙蟒', 'quantity': 1600, 'cost_price': 13.324, 'industry': '化工'}
        ]
        
        # 模拟实时价格（基于时间变化）
        self.current_hour = datetime.now().hour
        self.current_minute = datetime.now().minute
        
    def get_simulated_realtime_price(self, code):
        """模拟实时价格"""
        # 基础价格
        base_prices = {
            '603949': 19.60,  # 雪龙集团
            '600343': 36.14,  # 航天动力  
            '002312': 13.62   # 川发龙蟒
        }
        
        base_price = base_prices.get(code, 10.0)
        
        # 基于时间的波动模拟
        time_factor = (self.current_hour * 60 + self.current_minute) / 1440.0
        
        # 模拟日内波动模式
        if time_factor < 0.25:  # 早盘
            volatility = 0.02
        elif time_factor < 0.5:  # 午前
            volatility = 0.015
        elif time_factor < 0.75:  # 午后
            volatility = 0.01
        else:  # 尾盘
            volatility = 0.005
        
        # 添加随机波动
        random.seed(hash(f"{code}{self.current_hour}{self.current_minute}") % 1000)
        fluctuation = random.uniform(-volatility, volatility)
        
        current_price = base_price * (1 + fluctuation)
        change_percent = fluctuation * 100
        
        return {
            'code': code,
            'price': round(current_price, 3),
            'change': round(change_percent, 2),
            'volume': random.randint(50000, 200000) * 100,
            'time': self.today
        }
    
    def get_market_sentiment(self):
        """获取市场情绪"""
        # 模拟市场数据
        indices = {
            '上证指数': 3250.45 + random.uniform(-20, 20),
            '深证成指': 11234.67 + random.uniform(-50, 50),
            '创业板指': 2345.78 + random.uniform(-10, 10)
        }
        
        # 计算平均变化
        avg_change = random.uniform(-0.5, 0.3)
        
        if avg_change > 0.3:
            sentiment = '强势'
            color = '🟢'
        elif avg_change > 0:
            sentiment = '偏强'
            color = '🟡'
        elif avg_change > -0.3:
            sentiment = '震荡'
            color = '🟡'
        else:
            sentiment = '弱势'
            color = '🔴'
        
        return {
            'sentiment': sentiment,
            'color': color,
            'avg_change': round(avg_change, 2),
            'indices': indices
        }
    
    def get_stock_context(self, code):
        """获取股票背景信息"""
        context_map = {
            '603949': {
                'sector': '汽车零部件',
                'trend': '行业震荡，新能源转型',
                'key_news': '汽车促消费政策有望出台',
                'risk': '中高',
                'outlook': '中性'
            },
            '600343': {
                'sector': '航天军工',
                'trend': '政策支持，国防预算增长',
                'key_news': '军工企业改革深化',
                'risk': '高',
                'outlook': '积极'
            },
            '002312': {
                'sector': '化工',
                'trend': '价格企稳，环保要求提升',
                'key_news': '化工品价格小幅反弹',
                'risk': '中',
                'outlook': '稳定'
            }
        }
        
        return context_map.get(code, {
            'sector': '未知',
            'trend': '--',
            'key_news': '暂无',
            'risk': '中',
            'outlook': '中性'
        })
    
    def analyze_holding(self, holding):
        """分析单个持仓"""
        # 获取实时数据
        realtime = self.get_simulated_realtime_price(holding['code'])
        context = self.get_stock_context(holding['code'])
        
        # 计算关键指标
        current_price = realtime['price']
        cost_price = holding['cost_price']
        quantity = holding['quantity']
        
        market_value = quantity * current_price
        cost_value = quantity * cost_price
        profit_loss = market_value - cost_value
        profit_loss_rate = (profit_loss / cost_value) * 100
        
        # 判断趋势
        if realtime['change'] > 1.5:
            trend = '强势上涨'
            action = '持有'
        elif realtime['change'] > 0.5:
            trend = '小幅上涨'
            action = '持有观望'
        elif realtime['change'] > -0.5:
            trend = '震荡整理'
            action = '观望'
        elif realtime['change'] > -1.5:
            trend = '小幅下跌'
            action = '谨慎持有'
        else:
            trend = '弱势下跌'
            action = '考虑减仓'
        
        # 风险评估
        if abs(profit_loss_rate) > 8:
            risk = '高'
        elif abs(profit_loss_rate) > 5:
            risk = '中高'
        else:
            risk = '中'
        
        return {
            'holding': holding,
            'realtime': realtime,
            'context': context,
            'metrics': {
                'current_price': current_price,
                'market_value': market_value,
                'profit_loss': profit_loss,
                'profit_loss_rate': profit_loss_rate,
                'trend': trend,
                'action': action,
                'risk': risk
            }
        }
    
    def generate_concise_report(self):
        """生成简洁报告"""
        print("生成实时分析报告...")
        
        # 获取市场情绪
        market = self.get_market_sentiment()
        
        # 分析每个持仓
        analyses = []
        for holding in self.holdings:
            analysis = self.analyze_holding(holding)
            analyses.append(analysis)
        
        # 计算组合指标
        total_value = sum(a['metrics']['market_value'] for a in analyses)
        total_cost = sum(h['quantity'] * h['cost_price'] for h in self.holdings)
        total_profit = total_value - total_cost
        total_profit_rate = (total_profit / total_cost) * 100
        
        # 计算权重
        for analysis in analyses:
            mv = analysis['metrics']['market_value']
            analysis['metrics']['weight'] = (mv / total_value) * 100
        
        # 生成报告
        report = self.format_concise_report(market, analyses, total_value, total_profit, total_profit_rate)
        
        return report
    
    def format_concise_report(self, market, analyses, total_value, total_profit, total_profit_rate):
        """格式化简洁报告"""
        report = f"📊 **myStock实时关键分析** {self.today}\n\n"
        
        # 市场概况
        report += f"{market['color']} **市场**: {market['sentiment']} (平均{market['avg_change']:+.1f}%)\n\n"
        
        # 组合概况
        profit_color = "🟢" if total_profit_rate > 0 else "🔴" if total_profit_rate < 0 else "🟡"
        report += f"{profit_color} **组合**: {total_value:,.0f}元 ({total_profit_rate:+.1f}%)\n\n"
        
        # 关键持仓分析
        report += "🔍 **关键持仓分析**\n"
        
        for analysis in analyses:
            h = analysis['holding']
            m = analysis['metrics']
            r = analysis['realtime']
            c = analysis['context']
            
            # 涨跌符号
            if r['change'] > 0:
                change_symbol = "▲"
            elif r['change'] < 0:
                change_symbol = "▼"
            else:
                change_symbol = "●"
            
            # 盈亏状态
            if m['profit_loss_rate'] > 2:
                pl_status = "盈利"
                pl_color = "🟢"
            elif m['profit_loss_rate'] < -2:
                pl_status = "亏损"
                pl_color = "🔴"
            else:
                pl_status = "持平"
                pl_color = "🟡"
            
            report += f"\n{pl_color} **{h['code']} {h['name']}**\n"
            report += f"{change_symbol} 现价: {r['price']} ({r['change']:+.1f}%)\n"
            report += f"盈亏: {m['profit_loss_rate']:+.1f}% | 权重: {m['weight']:.1f}%\n"
            report += f"趋势: {m['trend']} | 操作: {m['action']}\n"
            report += f"行业: {c['sector']} ({c['risk']}风险)\n"
            report += f"消息: {c['key_news']}\n"
        
        # 关键问题
        report += f"\n⚠️ **关键问题**\n"
        
        key_issues = []
        for analysis in analyses:
            m = analysis['metrics']
            h = analysis['holding']
            
            if m['weight'] > 40:
                key_issues.append(f"{h['name']} 仓位过重 ({m['weight']:.1f}%)")
            if m['profit_loss_rate'] < -5:
                key_issues.append(f"{h['name']} 亏损较大 ({m['profit_loss_rate']:.1f}%)")
        
        if key_issues:
            for issue in key_issues:
                report += f"• {issue}\n"
        else:
            report += "• 暂无重大问题\n"
        
        # 今日操作要点
        report += f"\n🎯 **今日操作要点**\n"
        
        actions = []
        for analysis in analyses:
            m = analysis['metrics']
            h = analysis['holding']
            
            if m['weight'] > 40:
                actions.append(f"减仓 {h['name']} (权重{m['weight']:.1f}%→30%)")
            elif m['profit_loss_rate'] < -8:
                actions.append(f"止损 {h['name']} (亏损{m['profit_loss_rate']:.1f}%)")
            elif m['profit_loss_rate'] < -5:
                actions.append(f"减仓 {h['name']} (亏损{m['profit_loss_rate']:.1f}%)")
            elif r['change'] > 2 and m['profit_loss_rate'] > 0:
                actions.append(f"持有 {h['name']} (强势上涨)")
        
        if actions:
            for i, action in enumerate(actions[:3], 1):
                report += f"{i}. {action}\n"
        else:
            report += "暂无紧急操作，建议观望\n"
        
        # 趋势预测
        report += f"\n📈 **短期趋势预测**\n"
        
        for analysis in analyses:
            h = analysis['holding']
            m = analysis['metrics']
            r = analysis['realtime']
            
            if m['profit_loss_rate'] < 0:
                target = h['cost_price'] * 1.02  # 回本+2%
                gap = ((target - r['price']) / r['price']) * 100
                report += f"• {h['name']}: 目标回本价{target:.2f} (+{gap:.1f}%)\n"
            else:
                target = r['price'] * 1.05  # 上涨5%
                report += f"• {h['name']}: 目标{target:.2f} (+5%)\n"
        
        # 系统信息
        report += f"\n---\n"
        report += f"分析时间: {self.today}\n"
        report += f"数据: 模拟实时行情\n"
        report += f"下次更新: 收盘后16:20\n"
        
        return report

def main():
    """主函数"""
    analyzer = SimpleRealtimeAnalyzer()
    
    print("="*60)
    print("myStock实时关键分析系统")
    print("="*60)
    
    report = analyzer.generate_concise_report()
    
    # 保存报告
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    today_str = datetime.now().strftime('%Y%m%d_%H%M')
    report_file = os.path.join(output_dir, f"key_analysis_{today_str}.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {report_file}")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        
        # 显示报告摘要
        print("\n" + "="*60)
        print("关键分析摘要:")
        print("="*60)
        
        # 只显示关键信息
        lines = report.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['市场', '组合', '关键持仓', '关键问题', '操作要点', '趋势预测']):
                print(line)
            elif line.startswith('•') or line.startswith(('1.', '2.', '3.')):
                print(line)
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()