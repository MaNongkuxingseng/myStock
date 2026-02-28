#!/usr/bin/env python3
"""
myStock Launch Script - 一键启动持仓分析系统
"""

import sys
import os
from datetime import datetime

# Setup paths
sys.path.append('D:\\python_libs')
sys.path.append('instock')

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_database():
    """Check database connection"""
    print_section("Database Check")
    
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
        
        cursor = conn.cursor()
        
        # Check portfolio tables
        cursor.execute("SHOW TABLES LIKE 'portfolio%'")
        portfolio_tables = [t[0] for t in cursor.fetchall()]
        print(f"Portfolio tables: {len(portfolio_tables)} found")
        
        # Check holdings
        cursor.execute("SELECT COUNT(*) FROM portfolio_holdings")
        holdings_count = cursor.fetchone()[0]
        print(f"Portfolio holdings: {holdings_count} records")
        
        # Check portfolio overview
        cursor.execute("SELECT * FROM portfolio_overview")
        overview = cursor.fetchall()
        
        print("\nPortfolio Overview:")
        for row in overview:
            print(f"  {row[0]}: {row[1]} holdings, Cost: {row[2]:,.0f}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Database error: {e}")
        return False

def generate_portfolio_report():
    """Generate portfolio report"""
    print_section("Portfolio Report")
    
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
        
        # Get portfolio summary
        cursor.execute("""
            SELECT portfolio_name, 
                   COUNT(*) as holdings,
                   SUM(quantity * cost_price) as total_cost,
                   GROUP_CONCAT(DISTINCT code) as codes
            FROM portfolio_holdings 
            WHERE is_active = 1
            GROUP BY portfolio_name
        """)
        
        portfolios = cursor.fetchall()
        
        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        print(f"Report Date: {today}")
        print(f"Portfolios: {len(portfolios)}")
        
        for p in portfolios:
            print(f"\n📊 {p['portfolio_name']}")
            print(f"   Holdings: {p['holdings']} stocks")
            print(f"   Total Cost: {p['total_cost']:,.2f} CNY")
            print(f"   Stocks: {p['codes']}")
        
        cursor.close()
        conn.close()
        
        return portfolios
        
    except Exception as e:
        print(f"Report error: {e}")
        return []

def show_next_steps():
    """Show next steps"""
    print_section("Next Steps")
    
    steps = [
        "1. UPDATE YOUR HOLDINGS:",
        "   Edit portfolio_holdings table with your actual holdings",
        "   Columns: portfolio_name, code, name, quantity, cost_price",
        "",
        "2. SCHEDULE AUTOMATIC RUNS:",
        "   Create Windows Task Scheduler tasks:",
        "   • 16:20 - After market close analysis",
        "   • 20:30 - Evening portfolio report", 
        "   • 08:40 - Pre-market alerts",
        "",
        "3. TEST FEISHU MESSAGES:",
        "   Run this script and copy output to Feishu group",
        "   Group ID: oc_b99df765824c2e59b3fabf287e8d14a2",
        "",
        "4. MONITORING RULES:",
        "   • Price alerts: >10% change",
        "   • Volume alerts: >3x or <0.3x average",
        "   • Concentration: >20% in single stock",
        "",
        "5. FUTURE ENHANCEMENTS:",
        "   • Real-time price updates",
        "   • Broker auto-sync (next phase)",
        "   • Advanced analytics",
    ]
    
    for step in steps:
        print(step)

def main():
    """Main function"""
    print("="*60)
    print("myStock Portfolio Analysis System")
    print("="*60)
    
    # Check system
    if not check_database():
        print("\n❌ System check failed. Please fix database issues first.")
        return
    
    # Generate report
    portfolios = generate_portfolio_report()
    
    if not portfolios:
        print("\n❌ No portfolio data found.")
        print("Please add holdings to portfolio_holdings table.")
    
    # Show Feishu message template
    print_section("Feishu Message Template")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    message = f"""myStock Portfolio Report - {today}

System Status: ✅ Active
Portfolios: {len(portfolios)}

📊 Current Holdings:"""
    
    for p in portfolios:
        message += f"""
{p['portfolio_name']}:
• Stocks: {p['holdings']}
• Total Cost: {p['total_cost']:,.0f} CNY
• Codes: {p['codes']}"""
    
    message += f"""

🔔 Monitoring Active:
• Price alerts (>10% change)
• Volume alerts (abnormal volume)
• Concentration warnings

📱 Delivered to: myStock监控群组
🔄 Next update: 16:20 (market close)
"""
    
    print(message)
    
    # Show next steps
    show_next_steps()
    
    print("\n" + "="*60)
    print("✅ myStock is ready for deployment!")
    print("="*60)

if __name__ == "__main__":
    main()