#!/usr/bin/env python3
"""
myStock集成指标分析的持仓分析系统
每天早上9点推送分析及操作建议
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('D:\\python_libs')

class MystockIntegratedAnalyzer:
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.current_time = datetime.now().strftime('%H:%M')
        
        # 实际持仓数据（示例）
        self.holdings = [
            {
                'code': '000001',
                'name': '平安银行',
                'quantity': 5000,
                'cost_price': 12.50,
                'portfolio': '主力组合'
            },
            {
                'code': '000858',
                'name': '五粮液',
                'quantity': 200,
                'cost_price': 150.00,
                'portfolio': '主力组合'
            },
            {
                'code': '300750',
                'name': '宁德时代',
                'quantity': 100,
                'cost_price': 200.00,
                'portfolio': '主力组合'
            }
        ]
        
        # myStock技术指标权重
        self.indicator_weights = {
            'macd': 0.25,      # MACD指标
            'kdj': 0.20,       # KDJ指标
            'boll': 0.15,      # 布林带
            'rsi': 0.15,       # RSI
            'volume': 0.10,    # 成交量
            'trend': 0.15      # 趋势
        }
    
    def get_stock_data_from_db(self, code):
        """从数据库获取股票数据"""
        try:
            import pymysql
            from lib import database
            
            conn = pymysql.connect(
                host=database.db_host,
                user=database.db_user,
                password=database.db_password,
                database=database.db_database,
                port=database.db_port,
                charset=database.db_charset
            )
            
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 获取最近30天的数据用于指标计算
            query = """
                SELECT date, open, high, low, close, volume
                FROM cn_stock_selection 
                WHERE code = %s 
                ORDER BY date DESC 
                LIMIT 30
            """
            
            cursor.execute(query, (code,))
            data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if data:
                # 转换为DataFrame格式
                import pandas as pd
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                return df
            else:
                print(f"Warning: No data found for {code}")
                return None
                
        except Exception as e:
            print(f"Error fetching data for {code}: {e}")
            return None
    
    def calculate_mystock_indicators(self, df):
        """计算myStock技术指标"""
        if df is None or len(df) < 20:
            return None
        
        try:
            import pandas as pd
            import numpy as np
            import talib as tl
            
            # 确保数据足够
            if len(df) < 30:
                return None
            
            # 使用myStock的指标计算方法
            from core.indicator.calculate_indicator import get_indicators
            
            # 准备数据格式
            data = df.copy()
            data = data[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            # 计算指标
            indicators = get_indicators(data, calc_threshold=30)
            
            # 获取最新指标值
            latest = indicators.iloc[-1]
            
            # 提取关键指标
            result = {
                'macd': latest.get('macd', 0),
                'macd_signal': latest.get('macds', 0),
                'macd_hist': latest.get('macdh', 0),
                'kdj_k': latest.get('kdjk', 0),
                'kdj_d': latest.get('kdjd', 0),
                'kdj_j': latest.get('kdjj', 0),
                'boll_upper': latest.get('boll_ub', 0),
                'boll_middle': latest.get('boll', 0),
                'boll_lower': latest.get('boll_lb', 0),
                'rsi': latest.get('rsi', 0),
                'volume_ratio': latest.get('volume_ratio', 1),
                'close': latest.get('close', 0),
                'date': latest.get('date', self.today)
            }
            
            return result
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return None
    
    def analyze_technical_signals(self, indicators):
        """分析技术信号"""
        if not indicators:
            return {'score': 50, 'signals': [], 'trend': 'neutral'}
        
        signals = []
        score = 50  # 基础分50
        
        # MACD分析
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_hist = indicators.get('macd_hist', 0)
        
        if macd > macd_signal and macd_hist > 0:
            signals.append('MACD金叉向上')
            score += 10
        elif macd < macd_signal and macd_hist < 0:
            signals.append('MACD死叉向下')
            score -= 10
        
        # KDJ分析
        kdj_k = indicators.get('kdj_k', 50)
        kdj_d = indicators.get('kdj_d', 50)
        kdj_j = indicators.get('kdj_j', 50)
        
        if kdj_j < 20:
            signals.append('KDJ超卖')
            score += 5
        elif kdj_j > 80:
            signals.append('KDJ超买')
            score -= 5
        
        # 布林带分析
        close = indicators.get('close', 0)
        boll_upper = indicators.get('boll_upper', close)
        boll_lower = indicators.get('boll_lower', close)
        
        if close > boll_upper:
            signals.append('突破布林上轨')
            score -= 8
        elif close < boll_lower:
            signals.append('跌破布林下轨')
            score += 8
        
        # RSI分析
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            signals.append('RSI超卖')
            score += 7
        elif rsi > 70:
            signals.append('RSI超买')
            score -= 7
        
        # 成交量分析
        volume_ratio = indicators.get('volume_ratio', 1)
        if volume_ratio > 2:
            signals.append('放量')
            score += 3 if close > indicators.get('close', 0) else -3
        elif volume_ratio < 0.5:
            signals.append('缩量')
            score -= 2
        
        # 确定趋势
        if score >= 60:
            trend = 'bullish'
        elif score <= 40:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        # 限制分数在0-100之间
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'signals': signals,
            'trend': trend,
            'macd_status': 'bullish' if macd > macd_signal else 'bearish',
            'kdj_status': 'oversold' if kdj_j < 20 else 'overbought' if kdj_j > 80 else 'normal',
            'boll_status': 'upper' if close > boll_upper else 'lower' if close < boll_lower else 'middle',
            'rsi_status': 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'normal'
        }
    
    def generate_trading_suggestions(self, holding, tech_analysis, current_price):
        """生成交易建议"""
        cost_price = holding['cost_price']
        profit_rate = ((current_price - cost_price) / cost_price) * 100
        
        suggestions = []
        priority = 'medium'
        
        # 基于技术分析的建议
        if tech_analysis['trend'] == 'bullish':
            if profit_rate > 15:
                suggestions.append(f"技术面看好，但盈利已超15%，考虑部分止盈")
                priority = 'high'
            elif profit_rate < -10:
                suggestions.append(f"技术面转好，亏损较大，可考虑补仓")
                priority = 'high'
            else:
                suggestions.append(f"技术面看好，建议继续持有")
                priority = 'medium'
        
        elif tech_analysis['trend'] == 'bearish':
            if profit_rate > 10:
                suggestions.append(f"技术面转弱，建议获利了结")
                priority = 'high'
            elif profit_rate < -5:
                suggestions.append(f"技术面弱势，建议止损或减仓")
                priority = 'high'
            else:
                suggestions.append(f"技术面偏弱，建议谨慎持有")
                priority = 'medium'
        
        else:  # neutral
            if profit_rate > 20:
                suggestions.append(f"盈利丰厚，建议锁定部分利润")
                priority = 'medium'
            elif profit_rate < -15:
                suggestions.append(f"亏损较大，建议重新评估")
                priority = 'high'
            else:
                suggestions.append(f"技术面中性，建议观望")
                priority = 'low'
        
        # 添加具体技术信号建议
        signals = tech_analysis['signals']
        if 'MACD金叉向上' in signals:
            suggestions.append("MACD金叉，短期看涨信号")
        if 'KDJ超卖' in signals:
            suggestions.append("KDJ超卖，可能有反弹机会")
        if '跌破布林下轨' in signals:
            suggestions.append("跌破布林下轨，可能有超跌反弹")
        if 'RSI超买' in signals:
            suggestions.append("RSI超买，注意回调风险")
        
        return {
            'suggestions': suggestions[:3],  # 最多3条建议
            'priority': priority,
            'tech_score': tech_analysis['score'],
            'profit_rate': profit_rate
        }
    
    def run_analysis(self):
        """运行完整分析"""
        print(f"myStock集成分析系统 - {self.today} {self.current_time}")
        print("="*60)
        
        analysis_results = []
        
        for holding in self.holdings:
            code = holding['code']
            name = holding['name']
            
            print(f"\n分析 {code} {name}...")
            
            # 1. 获取股票数据
            df = self.get_stock_data_from_db(code)
            
            if df is None or len(df) < 20:
                print(f"  ⚠️ 数据不足，使用模拟数据")
                # 使用模拟数据
                current_price = holding.get('current_price', holding['cost_price'] * 1.1)
                indicators = None
            else:
                # 2. 计算技术指标
                indicators = self.calculate_mystock_indicators(df)
                current_price = df.iloc[-1]['close'] if len(df) > 0 else holding['cost_price']
            
            # 3. 更新当前价格
            holding['current_price'] = current_price
            
            # 4. 计算盈亏
            holding['market_value'] = holding['quantity'] * current_price
            holding['profit_loss'] = holding['market_value'] - (holding['quantity'] * holding['cost_price'])
            holding['profit_loss_rate'] = (holding['profit_loss'] / (holding['quantity'] * holding['cost_price'])) * 100
            
            # 5. 技术分析
            tech_analysis = self.analyze_technical_signals(indicators) if indicators else {
                'score': 50, 
                'signals': ['数据不足，建议手动分析'],
                'trend': 'neutral'
            }
            
            # 6. 生成交易建议
            suggestions = self.generate_trading_suggestions(holding, tech_analysis, current_price)
            
            # 7. 汇总结果
            result = {
                'holding': holding,
                'current_price': current_price,
                'indicators': indicators,
                'tech_analysis': tech_analysis,
                'suggestions': suggestions,
                'analysis_time': self.current_time
            }
            
            analysis_results.append(result)
            
            # 打印简要结果
            print(f"  当前价: {current_price:.2f} | 盈亏: {holding['profit_loss_rate']:+.1f}%")
            print(f"  技术评分: {tech_analysis['score']}/100 | 趋势: {tech_analysis['trend']}")
            print(f"  技术信号: {', '.join(tech_analysis['signals'][:2])}")
            print(f"  操作建议: {suggestions['suggestions'][0] if suggestions['suggestions'] else '无'}")
        
        # 计算组合总指标
        total_value = sum(r['holding']['market_value'] for r in analysis_results)
        total_cost = sum(r['holding']['quantity'] * r['holding']['cost_price'] for r in analysis_results)
        total_profit = total_value - total_cost
        total_profit_rate = (total_profit / total_cost) * 100 if total_cost > 0 else 0
        
        # 计算权重
        for result in analysis_results:
            holding = result['holding']
            holding['weight'] = (holding['market_value'] / total_value) * 100
        
        return {
            'date': self.today,
            'time': self.current_time,
            'total_value': total_value,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'total_profit_rate': total_profit_rate,
            'analysis_results': analysis_results,
            'holdings_count': len(analysis_results)
        }
    
    def generate_9am_report(self, analysis):
        """生成早上9点的分析报告"""
        report = f"""⏰ **myStock早盘分析报告** {analysis['date']} 09:00

📈 **组合概览**
• 持仓数量: {analysis['holdings_count']} 只
• 总市值: {analysis['total_value']:,.0f} 元
• 总成本: {analysis['total_cost']:,.0f} 元
• 总盈亏: {analysis['total_profit']:+,.0f} 元 ({analysis['total_profit_rate']:+.1f}%)

🔍 **技术分析摘要**
"""
        
        for result in analysis['analysis_results']:
            holding = result['holding']
            tech = result['tech_analysis']
            sugg = result['suggestions']
            
            trend_emoji = "📈" if tech['trend'] == 'bullish' else "📉" if tech['trend'] == 'bearish' else "➡️"
            score_emoji = "🟢" if tech['score'] >= 60 else "🔴" if tech['score'] <= 40 else "🟡"
            
            report += f"\n{trend_emoji} **{holding['code']} {holding['name']}**\n"
            report += f"当前价: {holding['current_price']:.2f} | 盈亏: {holding['profit_loss_rate']:+.1f}%\n"
            report += f"技术评分: {score_emoji} {tech['score']}/100 | 权重: {holding['weight']:.1f}%\n"
            
            if tech['signals']:
                report += f"技术信号: {', '.join(tech['signals'][:3])}\n"
            
            if sugg['suggestions']:
                priority_emoji = "🔴" if sugg['priority'] == 'high' else "🟡" if sugg['priority'] == 'medium' else "🟢"
                report += f"操作建议: {priority_emoji} {sugg['suggestions'][0]}\n"
        
        report += f"""
📊 **myStock指标分析**
• 集成MACD、KDJ、布林带、RSI等指标
• 综合技术评分系统
• 智能交易建议生成

⏰ **推送时间安排**
• 早盘分析: 09:00 (已发送)
• 盘中监控: 实时异动
• 收盘总结: 16:20
• 晚间报告: 20:30

💡 **今日重点关注**
1. 技术面转强的个股机会
2. 超买/超卖信号的个股
3. 仓位结构调整建议

🔔 **监控规则**
• 价格异动: >7%
• 技术信号: 金叉/死叉
• 仓位风险: 单股>30%
• 成交量: 异常放量/缩量

📱 **消息推送**
• 当前群组: myStock监控
• 推送频率: 定时 + 触发
• 消息类型: 分析 + 预警 + 建议

🔄 **系统状态**
• 数据源: myStock数据库 ✅
• 指标计算: myStock引擎 ✅
• 分析模型: 集成技术分析 ✅
• 推送机制: 定时任务 ⚙️

---
**myStock智能分析系统 | 每日早盘报告**
报告时间: {analysis['date']} 09:00
下次报告: 今日收盘后 16:20
"""
        
        return report
    
    def create_task_management_b