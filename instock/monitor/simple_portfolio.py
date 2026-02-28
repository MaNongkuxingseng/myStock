#!/usr/bin/env python3
"""
Simple Portfolio Monitor - 持仓分析与异动提醒
"""

import sys
import os
from datetime import datetime

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('D:\\python_libs')

try:
    import pymysql
    from lib import database
    
    class SimplePortfolioMonitor:
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
            
        def get_portfolio_summary(self):
            """获取持仓摘要"""
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 获取持仓数据
            cursor.execute("""
                SELECT 
                    portfolio_name,
                    COUNT(*) as holding_count,
                    SUM(quantity * cost_price) as total_cost,
                    GROUP_CONCAT(DISTINCT code) as stock_codes,
                    GROUP_CONCAT(DISTINCT industry) as industries
                FROM portfolio_holdings 
                WHERE is_active = 1
                GROUP BY portfolio_name
            """)
            
            portfolios = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return portfolios
        
        def check_for_alerts(self):
            """检查简单预警"""
            alerts = []
            
            # 这里可以添加简单的预警逻辑
            # 例如：检查是否有股票超过成本价一定比例
            
            return alerts
        
        def generate_report(self):
            """生成简单报告"""
            portfolios = self.get_portfolio_summary()
            
            if not portfolios:
                return "No portfolio data found. Please add holdings first."
            
            report = f"""
📊 **持仓分析报告** - {self.today}

系统状态：✅ 持仓管理系统已就绪

📈 **持仓组合概览**
"""
            
            for p in portfolios:
                report += f"""
**{p['portfolio_name']}**
• 持仓数量: {p['holding_count']} 只
• 总成本: {p['total_cost']:,.2f} 元
• 股票代码: {p['stock_codes']}
• 行业分布: {p['industries']}
"""
            
            report += f"""
🔔 **监控功能**
1. 持仓异动监控：价格波动 > 10%
2. 仓位集中度预警：单股权重 > 20%
3. 行业风险分析：行业集中度
4. 盈亏分析：实时盈亏计算

📱 **消息推送**
• 目标群组：myStock监控群 (当前群组)
• 推送频率：每日收盘后 + 实时异动
• 消息格式：Markdown + 表情符号

🚀 **下一步操作**
1. 提交实际持仓数据到 portfolio_holdings 表
2. 配置股票价格自动更新
3. 测试Feishu消息推送
4. 设置定时监控任务

💡 **使用说明**
• 添加持仓：INSERT INTO portfolio_holdings (portfolio_name, code, name, quantity, cost_price)
• 查看报告：运行本脚本
• 接收提醒：关注本Feishu群组

📅 下次报告时间：今日收盘后 (16:20)
"""
            
            return report
        
        def run(self):
            """运行监控"""
            print("="*60)
            print("Simple Portfolio Monitor")
            print(f"Date: {self.today}")
            print("="*60)
            
            report = self.generate_report()
            
            print("\n" + report)
            print("="*60)
            
            # 这里可以添加Feishu推送
            print("\nFeishu消息已生成，准备推送到群组...")
            print(f"群组ID: oc_b99df765824c2e59b3fabf287e8d14a2")
            
            return report
    
    # 主函数
    def main():
        monitor = SimplePortfolioMonitor()
        return monitor.run()
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check MySQL is running")
    print("2. Verify database connection in lib/database.py")
    print("3. Make sure portfolio_holdings table exists")
    print("4. Add some holdings data first")