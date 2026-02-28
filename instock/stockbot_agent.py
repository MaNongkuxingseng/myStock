#!/usr/bin/env python3
"""
StockBot核心Agent
集成技术指标分析、实时监控和智能推送
"""

import sys
import os
sys.path.append('D:\\python_libs')

import json
import time
from datetime import datetime, timedelta
from real_time_data import RealTimeDataFetcher
from technical_indicators import TechnicalIndicators

class StockBotAgent:
    """StockBot核心Agent"""
    
    def __init__(self, config_path=None):
        # 配置文件路径
        if config_path is None:
            self.config_path = os.path.join(os.path.dirname(__file__), "price_monitor_config.json")
        else:
            self.config_path = config_path
        
        # 加载配置
        self.load_config()
        
        # 初始化组件
        self.data_fetcher = RealTimeDataFetcher()
        self.technical_analyzer = TechnicalIndicators()
        
        # 状态跟踪
        self.last_analysis_time = None
        self.analysis_history = []
        self.alert_history = []
        
        # Agent技能配置
        self.skills = {
            'price_monitoring': True,
            'technical_analysis': True,
            'risk_assessment': True,
            'portfolio_analysis': True,
            'market_sentiment': True,
            'alert_generation': True,
            'report_generation': True
        }
    
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"StockBot配置加载成功，监控{len(self.config['monitored_stocks'])}只股票")
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config = {
                'monitored_stocks': [],
                'notification_settings': {
                    'feishu_group': 'oc_b99df765824c2e59b3fabf287e8d14a2',
                    'check_interval_minutes': 5
                }
            }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def update_stock_prices(self):
        """更新所有股票的真实价格"""
        updated_count = 0
        
        for stock in self.config['monitored_stocks']:
            code = stock['code']
            
            # 获取真实价格
            data = self.data_fetcher.get_stock_data(code, fallback=True)
            
            if data and 'error' not in data:
                old_price = stock.get('current_price', 0)
                new_price = data['price']
                
                if old_price != new_price:
                    stock['current_price'] = new_price
                    updated_count += 1
                    
                    # 记录价格更新
                    self.record_price_update(code, old_price, new_price)
        
        if updated_count > 0:
            self.config['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.save_config()
            print(f"更新了{updated_count}只股票的价格")
        
        return updated_count
    
    def record_price_update(self, code, old_price, new_price):
        """记录价格更新"""
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'old_price': old_price,
            'new_price': new_price,
            'change': new_price - old_price,
            'change_percent': ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
        }
        
        # 添加到历史记录
        self.analysis_history.append({
            'type': 'price_update',
            'data': update_record
        })
    
    def analyze_stock_technicals(self, code, days_history=30):
        """分析股票技术指标"""
        print(f"分析股票技术指标: {code}")
        
        # 获取历史数据（这里简化，实际应该从数据库或API获取）
        # 暂时使用模拟数据
        history_data = self.generate_simulated_history(code, days_history)
        
        if not history_data:
            return None
        
        # 技术分析
        analysis = self.technical_analyzer.analyze_stock_technicals(history_data)
        
        if analysis:
            # 记录分析结果
            analysis_record = {
                'timestamp': datetime.now().isoformat(),
                'code': code,
                'analysis': analysis,
                'current_price': history_data['current_price']
            }
            
            self.analysis_history.append({
                'type': 'technical_analysis',
                'data': analysis_record
            })
        
        return analysis
    
    def generate_simulated_history(self, code, days):
        """生成模拟历史数据（实际应该从数据库获取）"""
        # 获取当前价格
        current_data = self.data_fetcher.get_stock_data(code, fallback=True)
        
        if not current_data or 'error' in current_data:
            return None
        
        current_price = current_data['price']
        
        # 生成模拟历史数据
        history = []
        base_price = current_price * 0.9  # 从当前价格的90%开始
        
        for i in range(days):
            # 模拟价格波动
            volatility = 0.02  # 2%的日波动
            change = (np.random.random() - 0.5) * 2 * volatility
            
            price = base_price * (1 + change)
            high = price * (1 + np.random.random() * 0.01)  # 最高价
            low = price * (1 - np.random.random() * 0.01)   # 最低价
            volume = int(1000000 * (1 + np.random.random()))  # 成交量
            
            history.append({
                'date': (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d'),
                'open': price * 0.99,
                'high': high,
                'low': low,
                'close': price,
                'volume': volume
            })
            
            base_price = price
        
        return {
            'code': code,
            'name': current_data.get('name', ''),
            'current_price': current_price,
            'history': history
        }
    
    def check_price_alerts(self):
        """检查价格警报"""
        alerts = []
        
        for stock in self.config['monitored_stocks']:
            code = stock['code']
            name = stock['name']
            rules = stock['monitor_rules']
            
            # 获取当前价格
            data = self.data_fetcher.get_stock_data(code, fallback=True)
            
            if not data or 'error' in data:
                continue
            
            current_price = data['price']
            change = data.get('change_percent', 0)
            
            # 检查各种警报规则
            stock_alerts = self.check_single_stock_alerts(stock, current_price, change)
            alerts.extend(stock_alerts)
        
        return alerts
    
    def check_single_stock_alerts(self, stock, current_price, change):
        """检查单只股票的警报"""
        alerts = []
        code = stock['code']
        name = stock['name']
        rules = stock['monitor_rules']
        
        # 止损警报
        if 'stop_loss' in rules and current_price <= rules['stop_loss']:
            alerts.append({
                'level': 'critical',
                'type': 'stop_loss',
                'code': code,
                'name': name,
                'message': f"{code} {name} 触发止损位 {rules['stop_loss']}元",
                'current_price': current_price,
                'threshold': rules['stop_loss'],
                'change': change
            })
        
        # 买入机会
        if 'buy_alert' in rules and current_price <= rules['buy_alert']:
            alerts.append({
                'level': 'warning',
                'type': 'buy_opportunity',
                'code': code,
                'name': name,
                'message': f"{code} {name} 达到买入价 {rules['buy_alert']}元",
                'current_price': current_price,
                'threshold': rules['buy_alert'],
                'change': change
            })
        
        # 目标价
        if 'sell_alert' in rules and current_price >= rules['sell_alert']:
            alerts.append({
                'level': 'warning',
                'type': 'sell_opportunity',
                'code': code,
                'name': name,
                'message': f"{code} {name} 达到目标价 {rules['sell_alert']}元",
                'current_price': current_price,
                'threshold': rules['sell_alert'],
                'change': change
            })
        
        # 涨跌幅
        if 'change_threshold' in rules and abs(change) >= rules['change_threshold']:
            direction = "上涨" if change > 0 else "下跌"
            alerts.append({
                'level': 'warning' if abs(change) > 5 else 'info',
                'type': 'price_change',
                'code': code,
                'name': name,
                'message': f"{code} {name} {direction}{abs(change):.1f}%",
                'current_price': current_price,
                'change': change,
                'threshold': rules['change_threshold']
            })
        
        return alerts
    
    def analyze_portfolio(self):
        """分析投资组合"""
        portfolio = {
            'total_value': 0,
            'total_profit': 0,
            'stocks': [],
            'risk_assessment': {},
            'recommendations': []
        }
        
        # 这里应该从数据库获取实际持仓数据
        # 暂时使用配置中的监控股票作为持仓
        
        for stock in self.config['monitored_stocks']:
            code = stock['code']
            name = stock['name']
            
            # 获取当前价格
            data = self.data_fetcher.get_stock_data(code, fallback=True)
            
            if not data or 'error' in data:
                continue
            
            current_price = data['price']
            
            # 模拟持仓数据（实际应该从数据库获取）
            # 假设每只股票持有1000股
            shares = 1000
            cost_price = current_price * 0.95  # 假设成本价比当前价低5%
            
            market_value = current_price * shares
            cost_value = cost_price * shares
            profit = market_value - cost_value
            profit_percent = (profit / cost_value * 100) if cost_value > 0 else 0
            
            stock_info = {
                'code': code,
                'name': name,
                'shares': shares,
                'cost_price': cost_price,
                'current_price': current_price,
                'market_value': market_value,
                'profit': profit,
                'profit_percent': profit_percent,
                'weight': 0  # 稍后计算
            }
            
            portfolio['stocks'].append(stock_info)
            portfolio['total_value'] += market_value
            portfolio['total_profit'] += profit
        
        # 计算权重
        for stock in portfolio['stocks']:
            if portfolio['total_value'] > 0:
                stock['weight'] = (stock['market_value'] / portfolio['total_value']) * 100
        
        # 风险评估
        portfolio['risk_assessment'] = self.assess_portfolio_risk(portfolio)
        
        # 生成建议
        portfolio['recommendations'] = self.generate_portfolio_recommendations(portfolio)
        
        return portfolio
    
    def assess_portfolio_risk(self, portfolio):
        """评估投资组合风险"""
        risk = {
            'level': 'medium',
            'concentration_risk': False,
            'volatility_risk': False,
            'market_risk': False,
            'score': 50  # 0-100，越高风险越大
        }
        
        # 检查集中度风险
        if portfolio['stocks']:
            max_weight = max(stock['weight'] for stock in portfolio['stocks'])
            if max_weight > 40:  # 单只股票权重超过40%
                risk['concentration_risk'] = True
                risk['score'] += 20
        
        # 检查波动性风险
        total_profit_percent = portfolio['total_profit'] / (portfolio['total_value'] - portfolio['total_profit']) * 100 if portfolio['total_value'] > portfolio['total_profit'] else 0
        if abs(total_profit_percent) > 10:  # 整体盈亏超过10%
            risk['volatility_risk'] = True
            risk['score'] += 15
        
        # 确定风险等级
        if risk['score'] >= 70:
            risk['level'] = 'high'
        elif risk['score'] >= 40:
            risk['level'] = 'medium'
        else:
            risk['level'] = 'low'
        
        return risk
    
    def generate_portfolio_recommendations(self, portfolio):
        """生成投资组合建议"""
        recommendations = []
        
        # 检查集中度
        for stock in portfolio['stocks']:
            if stock['weight'] > 40:
                recommendations.append({
                    'type': 'reduce_concentration',
                    'stock': f"{stock['code']} {stock['name']}",
                    'message': f"仓位过重({stock['weight']:.1f}%)，建议减仓",
                    'priority': 'high'
                })
        
        # 检查亏损股票
        for stock in portfolio['stocks']:
            if stock['profit_percent'] < -10:  # 亏损超过10%
                recommendations.append({
                    'type': 'cut_losses',
                    'stock': f"{stock['code']} {stock['name']}",
                    'message': f"亏损较大({stock['profit_percent']:.1f}%)，考虑止损",
                    'priority': 'medium'
                })
        
        # 检查盈利股票
        for stock in portfolio['stocks']:
            if stock['profit_percent'] > 20:  # 盈利超过20%
                recommendations.append({
                    'type': 'take_profit',
                    'stock': f"{stock['code']} {stock['name']}",
                    'message': f"盈利较多({stock['profit_percent']:.1f}%)，考虑部分获利了结",
                    'priority': 'medium'
                })
        
        return recommendations
    
    def generate_analysis_report(self):
        """生成分析报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'market_overview': self.get_market_overview(),
            'stock_analysis': [],
            'portfolio_analysis': None,
            'alerts': [],
            'recommendations': []
        }
        
        # 股票分析
        for stock in self.config['monitored_stocks']:
            code = stock['code']
            
            # 技术分析
            technicals = self.analyze_stock_technicals(code)
            
            # 价格数据
            price_data = self.data_fetcher.get_stock_data(code, fallback=True)
            
            if price_data and 'error' not in price_data:
                stock_analysis = {
                    'code': code,
                    'name': stock['name'],
                    'current_price': price_data['price'],
                    'change': price_data.get('change_percent', 0),
                    'technicals': technicals,
                    'monitor_rules': stock['monitor_rules']
                }
                
                report['stock_analysis'].append(stock_analysis)
        
        # 投资组合分析
        report['portfolio_analysis'] = self.analyze_portfolio()
        
        # 检查警报
        report['alerts'] = self.check_price_alerts()
        
        # 生成建议
        report['recommendations'] = self.generate_overall_recommendations(report)
        
        return report
    
    def get_market_overview(self):
        """获取市场概览"""
        market_data = self.data_fetcher.get_market_index()
        
        overview = {
            'indices': market_data,
            'sentiment': 'neutral',
            'trend': 'sideways'
        }
        
        # 分析市场情绪
        up_count = 0
        down_count = 0
        
        for name, data in market_data.items():
            if 'error' not in data:
                if data['change_percent'] > 0:
                    up_count += 1
                elif data['change_percent'] < 0:
                    down_count += 1
        
        if up_count > down_count:
            overview['sentiment'] = 'bullish'
        elif down_count > up_count:
            overview['sentiment'] = 'bearish'
        
        return overview
    
    def generate_overall_recommendations(self, report):
        """生成总体建议"""
        recommendations = []
        
        # 基于市场情绪
        if report['market_overview']['sentiment'] == 'bearish':
            recommendations.append({
                'type': 'market',
                'message': '市场情绪偏空，建议谨慎操作',
                'priority': 'medium'
            })
        elif report['market_overview']['sentiment'] == 'bullish':
            recommendations.append({
                'type': 'market',
                'message': '市场情绪偏多，可适当积极',
                'priority': 'medium'
            })
        
        # 基于警报
        for alert in report['alerts']:
            if alert['level'] == 'critical':
                recommendations.append({
                    'type': 'alert',
                    'message': f"紧急: {alert['message']}",
                    'priority': 'high'
                })
        
        # 基于投资组合
        portfolio_recs = report['portfolio_analysis']['recommendations']
        recommendations.extend(portfolio_recs)
        
        return recommendations
    
    def format_report_for_feishu(self, report):
        """格式化报告为Feishu消息"""
        timestamp = datetime.fromisoformat(report['timestamp']).strftime('%Y-%m-%d %H:%M')
        
        message = f"📊 **StockBot分析报告** {timestamp}\n\n"
        
        # 市场概览
        message += "🌐 **市场概览**\n"
        for name, data in report['market_overview']['indices'].items():
            if 'error' not in data:
                change_emoji = "🟢" if data['change_percent'] > 0 else "🔴" if data['change_percent'] < 0 else "🟡"
                message += f"{change_emoji} {name}: {data['price']} ({data['change_percent']:+.2f}%)\n"
        
        message += f"市场情绪: {report['market_overview']['sentiment']}\n\n"
        
        # 股票分析
        message += "📈 **股票分析**\n"
        for stock in report['stock_analysis']:
            change_emoji = "🟢" if stock['change'] > 0 else "🔴" if stock['change'] < 0 else "🟡"
            message += f"{change_emoji} {stock['code']} {stock['name']}: {stock['current_price']}元 ({stock['change']:+.1f}%)\n"
            
            if stock['technicals']:
                tech_summary = stock['technicals']['summary']
                message += f"   技术评分: {tech_summary['technical_score']}/100 | 趋势: {tech_summary['trend_strength']} | 建议: {tech_summary['recommendation']}\n"
        
        message += "\n"
        
        # 投资组合
        portfolio = report['portfolio_analysis']
        message += "💰 **投资组合**\n"
        message += f"总市值: {portfolio['total_value']:,.0f}元\n"
        message += f"总盈亏: {portfolio['total_profit']:+,.0f}元\n"
        message += f"风险等级: {portfolio['risk_assessment']['level']}\n\n"
        
        # 警报
        if report['alerts']:
            message += "🚨 **警报列表**\n"
            for alert in report['alerts'][:3]:  # 显示最多3个警报
                level_emoji = "🔴" if alert['level'] == 'critical' else "🟡" if alert['level'] == 'warning' else "🟢"
                message += f"{level_emoji} {alert['message']}\n"
            message += "\n"
        
        # 建议
        if report['recommendations']:
            message += "💡 **操作建议**\n"
            for rec in report['recommendations'][:5]:  # 显示最多5个建议
                priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                message += f"{priority_emoji} {rec['message']}\n"
        
        message += f"\n---\nStockBot Agent v1.0 | 数据源: 新浪财经实时API"
        
        return message
    
    def send_feishu_message(self, message):
        """发送Feishu消息"""
        # 这里应该调用Feishu API
        # 暂时打印到控制台
        
        print("="*60)
        print("发送Feishu消息:")
        print("="*60)
        print(message)
        print("="*60)
        
        # 记录发送历史
        self.alert_history.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'sent': True
        })
        
        return True
    
    def run_single_analysis(self):
        """执行单次分析并推送"""
        print("StockBot执行单次分析...")
        print("="*60)
        
        # 更新价格
        self.update_stock_prices()
        
        # 生成报告
        report = self.generate_analysis_report()
        
        # 格式化消息
        message = self.format_report_for_feishu(report)
        
        # 发送消息
        self.send_feishu_message(message)
        
        # 记录分析时间
        self.last_analysis_time = datetime.now()
        
        print(f"分析完成，报告已生成")
        print(f"分析时间: {self.last_analysis_time.strftime('%H:%M:%S')}")
        
        return report
    
    def run_continuous_monitoring(self, interval_minutes=5):
        """持续监控"""
        print("StockBot持续监控启动...")
        print("="*60)
        print(f"监控间隔: {interval_minutes}分钟")
        print(f"监控股票: {len(self.config['monitored_stocks'])}只")
        print("="*60)
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"\n监控周期 #{cycle_count} - {current_time}")
                
                # 执行分析
                report = self.run_single_analysis()
                
                # 等待下一次检查
                print(f"\n等待 {interval_minutes} 分钟后再次检查...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
            
            # 生成总结报告
            summary = self.generate_summary_report()
            print("\n" + "="*60)
            print("监控总结报告:")
            print("="*60)
            print(summary)
    
    def generate_summary_report(self):
        """生成总结报告"""
        total_cycles = len(self.analysis_history)
        total_alerts = len(self.alert_history)
        
        summary = f"📋 **StockBot监控总结**\n\n"
        summary += f"监控开始: {self.analysis_history[0]['timestamp'] if self.analysis_history else 'N/A'}\n"
        summary += f"监控结束: {datetime.now().isoformat()}\n"
        summary += f"总分析次数: {total_cycles}\n"
        summary += f"总警报数量: {total_alerts}\n"
        summary += f"最后分析: {self.last_analysis_time.strftime('%H:%M:%S') if self.last_analysis_time else 'N/A'}\n\n"
        
        # 统计警报类型
        alert_types = {}
        for alert in self.alert_history:
            # 简单统计
            alert_types['total'] = alert_types.get('total', 0) + 1
        
        summary += f"警报统计: {alert_types}\n\n"
        
        summary += "💡 **系统状态**\n"
        for skill, enabled in self.skills.items():
            status = "✅" if enabled else "❌"
            summary += f"{status} {skill}: {'启用' if enabled else '禁用'}\n"
        
        summary += f"\n---\nStockBot Agent v1.0 | 下次启动: 明天09:00"
        
        return summary

def main():
    """主函数"""
    agent = StockBotAgent()
    
    print("StockBot Agent v1.0")
    print("="*60)
    print("选择操作模式:")
    print("1. 执行单次分析并推送")
    print("2. 启动持续监控")
    print("3. 测试技术指标")
    print("4. 查看系统状态")
    
    try:
        choice = input("请输入选择 (1-4): ").strip()
    except:
        choice = "1"  # 默认选择
    
    if choice == '1':
        agent.run_single_analysis()
    elif choice == '2':
        interval = agent.config['notification_settings'].get('check_interval_minutes', 5)
        agent.run_continuous_monitoring(interval)
    elif choice == '3':
        from technical_indicators import test_technical_indicators
        test_technical_indicators()
    elif choice == '4':
        summary = agent.generate_summary_report()
        print(summary)
    else:
        print("无效选择，执行单次分析")
        agent.run_single_analysis()

if __name__ == "__main__":
    # 需要numpy库
    try:
        import numpy as np
        main()
    except ImportError:
        print("需要安装numpy库: pip install numpy")
        print("正在安装...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        import numpy as np
        main()