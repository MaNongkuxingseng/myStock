#!/usr/bin/env python3
"""
Portfolio Monitoring System for myStock
重点：持仓分析及异动提醒
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('D:\\python_libs')

try:
    import pandas as pd
    import pymysql
    from lib import database
    
    class PortfolioMonitor:
        def __init__(self):
            self.db_config = {
                'host': database.db_host,
                'user': database.db_user,
                'password': database.db_password,
                'database': database.db_database,
                'port': database.db_port,
                'charset': database.db_charset
            }
            self.today = datetime.now().strftime('%Y-%m-%d')
            
        def update_portfolio_prices(self):
            """更新持仓股票的最新价格"""
            print("Updating portfolio prices...")
            
            conn = pymysql.connect(**self.db_config)
            
            # 获取持仓股票代码
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT code, name 
                FROM portfolio_holdings 
                WHERE is_active = 1
            """)
            holdings = cursor.fetchall()
            
            if not holdings:
                print("No active holdings found")
                return 0
            
            updated_count = 0
            
            for code, name in holdings:
                try:
                    # 这里应该调用myStock的数据获取接口
                    # 暂时使用模拟数据
                    cursor.execute("""
                        SELECT close FROM cn_stock_selection 
                        WHERE code = %s AND date = %s 
                        ORDER BY date DESC LIMIT 1
                    """, (code, self.today))
                    
                    result = cursor.fetchone()
                    if result:
                        current_price = float(result[0])
                        
                        # 更新持仓价格
                        cursor.execute("""
                            UPDATE portfolio_holdings 
                            SET current_price = %s,
                                updated_at = NOW()
                            WHERE code = %s AND is_active = 1
                        """, (current_price, code))
                        
                        updated_count += 1
                        print(f"  Updated {code} {name}: {current_price}")
                    else:
                        print(f"  No price data for {code} {name}")
                        
                except Exception as e:
                    print(f"  Error updating {code}: {e}")
                    continue
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Updated {updated_count} holdings")
            return updated_count
        
        def calculate_portfolio_values(self):
            """计算持仓市值和盈亏"""
            print("Calculating portfolio values...")
            
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 计算并更新市值盈亏
            cursor.execute("""
                UPDATE portfolio_holdings 
                SET market_value = quantity * current_price,
                    profit_loss = (quantity * current_price) - (quantity * cost_price),
                    profit_loss_rate = ROUND(
                        ((quantity * current_price) - (quantity * cost_price)) / 
                        (quantity * cost_price) * 100, 2
                    ),
                    weight = ROUND(
                        (quantity * current_price) / (
                            SELECT SUM(quantity * current_price) 
                            FROM portfolio_holdings ph2 
                            WHERE ph2.portfolio_name = portfolio_holdings.portfolio_name 
                            AND ph2.is_active = 1
                        ) * 100, 2
                    ),
                    updated_at = NOW()
                WHERE is_active = 1 AND current_price IS NOT NULL
            """)
            
            updated = cursor.rowcount
            conn.commit()
            
            cursor.close()
            conn.close()
            
            print(f"Calculated values for {updated} holdings")
            return updated
        
        def check_portfolio_alerts(self):
            """检查持仓异动"""
            print("Checking portfolio alerts...")
            
            conn = pymysql.connect(**self.db_config)
            
            alerts = []
            
            # 1. 检查单只股票盈亏预警
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT portfolio_name, code, name, 
                       profit_loss_rate, profit_loss, market_value
                FROM portfolio_holdings 
                WHERE is_active = 1 
                AND current_price IS NOT NULL
                AND ABS(profit_loss_rate) > 10
                ORDER BY ABS(profit_loss_rate) DESC
            """)
            
            profit_alerts = cursor.fetchall()
            for alert in profit_alerts:
                rate = alert['profit_loss_rate']
                level = "HIGH" if abs(rate) > 20 else "MEDIUM"
                direction = "profit" if rate > 0 else "loss"
                
                alerts.append({
                    'portfolio': alert['portfolio_name'],
                    'code': alert['code'],
                    'name': alert['name'],
                    'type': f'profit_loss_{direction}',
                    'level': level,
                    'current_value': rate,
                    'threshold': 10,
                    'description': f"{direction.upper()} {abs(rate):.2f}%",
                    'suggested_action': "Consider taking profit" if rate > 20 else "Review position" if rate < -10 else "Monitor"
                })
            
            # 2. 检查仓位集中度预警
            cursor.execute("""
                SELECT portfolio_name, code, name, weight
                FROM portfolio_holdings 
                WHERE is_active = 1 
                AND weight > 20
                ORDER BY weight DESC
            """)
            
            concentration_alerts = cursor.fetchall()
            for alert in concentration_alerts:
                alerts.append({
                    'portfolio': alert['portfolio_name'],
                    'code': alert['code'],
                    'name': alert['name'],
                    'type': 'concentration',
                    'level': "HIGH" if alert['weight'] > 30 else "MEDIUM",
                    'current_value': alert['weight'],
                    'threshold': 20,
                    'description': f"High concentration: {alert['weight']:.2f}%",
                    'suggested_action': "Consider diversification"
                })
            
            # 3. 保存预警到数据库
            if alerts:
                for alert in alerts:
                    cursor.execute("""
                        INSERT INTO portfolio_alerts 
                        (portfolio_name, code, name, alert_type, alert_level,
                         current_value, threshold_value, change_rate,
                         description, suggested_action)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        alert['portfolio'], alert['code'], alert['name'],
                        alert['type'], alert['level'], alert['current_value'],
                        alert['threshold'], alert.get('change_rate'),
                        alert['description'], alert['suggested_action']
                    ))
                
                conn.commit()
                print(f"Saved {len(alerts)} alerts to database")
            
            cursor.close()
            conn.close()
            
            return alerts
        
        def generate_portfolio_report(self):
            """生成持仓报告"""
            print("Generating portfolio report...")
            
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 获取组合概览
            cursor.execute("SELECT * FROM portfolio_overview")
            overview = cursor.fetchall()
            
            # 获取行业分布
            cursor.execute("SELECT * FROM portfolio_industry_distribution")
            industry_dist = cursor.fetchall()
            
            # 获取风险分析
            cursor.execute("SELECT * FROM portfolio_risk_analysis")
            risk_analysis = cursor.fetchall()
            
            # 获取今日预警
            cursor.execute("""
                SELECT * FROM portfolio_alerts 
                WHERE DATE(alert_time) = %s 
                ORDER BY alert_level DESC, alert_time DESC
                LIMIT 10
            """, (self.today,))
            today_alerts = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # 生成报告
            report = {
                'report_date': self.today,
                'overview': overview,
                'industry_distribution': industry_dist,
                'risk_analysis': risk_analysis,
                'today_alerts': today_alerts,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return report
        
        def generate_feishu_message(self, report):
            """生成Feishu消息"""
            if not report['overview']:
                return "No portfolio data available"
            
            message = "📊 **持仓分析报告**\n"
            message += f"日期: {self.today}\n"
            message += f"生成时间: {report['generated_at']}\n\n"
            
            # 组合概览
            message += "## 📈 组合概览\n"
            for portfolio in report['overview']:
                pl_rate = portfolio['total_profit_loss_rate'] or 0
                pl_emoji = "📈" if pl_rate > 0 else "📉" if pl_rate < 0 else "➡️"
                
                message += f"**{portfolio['portfolio_name']}**\n"
                message += f"持仓数量: {portfolio['holding_count']} 只\n"
                message += f"总市值: {portfolio['total_value']:,.2f} 元\n"
                message += f"总成本: {portfolio['total_cost']:,.2f} 元\n"
                message += f"总盈亏: {pl_emoji} {portfolio['total_profit_loss']:+,.2f} 元 ({pl_rate:+.2f}%)\n"
                message += f"行业分布: {portfolio['industries']}\n\n"
            
            # 今日预警
            if report['today_alerts']:
                message += "## ⚠️ 今日异动预警\n"
                for alert in report['today_alerts'][:5]:  # 最多显示5个
                    level_emoji = "🔴" if alert['alert_level'] == 'HIGH' else "🟡"
                    message += f"{level_emoji} **{alert['code']} {alert['name']}**\n"
                    message += f"类型: {alert['alert_type']}\n"
                    message += f"描述: {alert['description']}\n"
                    message += f"建议: {alert['suggested_action']}\n\n"
            
            # 风险提示
            if report['risk_analysis']:
                message += "## 🛡️ 风险分析\n"
                for risk in report['risk_analysis']:
                    if risk['risk_weight'] > 30:  # 高风险权重
                        message += f"⚠️ {risk['portfolio_name']} - {risk['risk_level']}风险: {risk['risk_weight']:.1f}%\n"
            
            message += "\n---\n"
            message += "📱 消息推送至: myStock监控群组\n"
            message += "🔄 下次更新: 收盘后16:20"
            
            return message
        
        def run_full_monitoring(self):
            """运行完整监控流程"""
            print("="*60)
            print("Portfolio Monitoring System")
            print(f"Date: {self.today}")
            print("="*60)
            
            # 1. 更新价格
            updated = self.update_portfolio_prices()
            if updated == 0:
                print("Warning: No prices updated. May need to run data collection first.")
            
            # 2. 计算市值
            self.calculate_portfolio_values()
            
            # 3. 检查异动
            alerts = self.check_portfolio_alerts()
            if alerts:
                print(f"Found {len(alerts)} portfolio alerts")
            
            # 4. 生成报告
            report = self.generate_portfolio_report()
            
            # 5. 生成Feishu消息
            feishu_message = self.generate_feishu_message(report)
            
            print("\n" + "="*60)
            print("Feishu Message Ready:")
            print("="*60)
            print(feishu_message)
            print("="*60)
            
            return feishu_message
    
    # 主执行函数
    def main():
        monitor = PortfolioMonitor()
        message = monitor.run_full_monitoring()
        
        # 这里可以添加Feishu推送代码
        # 消息将发送到当前群组: oc_b99df765824c2e59b3fabf287e8d14a2
        
        print("\nMonitoring completed successfully!")
        print("Next: Configure Feishu webhook for automatic delivery")
        
        return message
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Error in portfolio monitor: {e}")
    import traceback
    traceback.print_exc()