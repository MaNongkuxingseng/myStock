#!/usr/bin/env python3
"""
Simple alert system using existing tables
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
    
    # Connect to database
    conn = pymysql.connect(
        host=database.db_host,
        user=database.db_user,
        password=database.db_password,
        database=database.db_database,
        port=database.db_port,
        charset=database.db_charset
    )
    
    cursor = conn.cursor()
    
    print("="*60)
    print("myStock System Status Check")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # Check table status
    print("\n📊 Database Tables Status:")
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    
    for table in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        count = cursor.fetchone()[0]
        cursor.execute(f"SELECT MAX(date) FROM `{table}` WHERE date IS NOT NULL")
        latest_date = cursor.fetchone()[0]
        
        status = "✅" if count > 0 else "⚠️ "
        print(f"{status} {table:30} | Records: {count:6} | Latest: {latest_date or 'N/A'}")
    
    # Check if we have today's data
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n📅 Checking for today's data ({today}):")
    
    has_today_data = False
    for table in tables:
        if 'date' in table.lower() or table in ['cn_stock_selection', 'cn_stock_lhb']:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE date = %s", (today,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"✅ {table} has {count} records for today")
                has_today_data = True
    
    if not has_today_data:
        print("⚠️  No data found for today")
        print("   Run: python execute_daily_job.py to fetch today's data")
    
    # Generate system status message
    print("\n" + "="*60)
    print("System Status Summary:")
    
    total_records = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        total_records += cursor.fetchone()[0]
    
    print(f"• Total tables: {len(tables)}")
    print(f"• Total records: {total_records}")
    print(f"• Has today's data: {'Yes' if has_today_data else 'No'}")
    print(f"• Database: {database.db_database}")
    
    # Feishu message template
    feishu_message = f"""
📈 myStock System Status
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Database Status:
• Tables: {len(tables)}
• Total Records: {total_records}
• Today's Data: {'✅ Available' if has_today_data else '⚠️ Not Available'}

Next Actions:
1. {'Monitor is ready' if has_today_data else 'Run data collection: python execute_daily_job.py'}
2. Check config files in instock/config/
3. Schedule tasks using run_task.bat

System ID: {database.db_database}
"""
    
    print("\n" + "="*60)
    print("Feishu Message Template:")
    print(feishu_message)
    print("="*60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check MySQL service is running")
    print("2. Verify database password in lib/database.py")
    print("3. Run: python execute_daily_job.py to initialize data")

if __name__ == "__main__":
    print("\nSystem check completed.")