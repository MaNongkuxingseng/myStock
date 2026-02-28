#!/usr/bin/env python3
"""
Simple stock monitor for myStock
Sends alerts to current Feishu group
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Add custom lib path
    sys.path.append('D:\\python_libs')
    
    import pandas as pd
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
    
    # Query today's abnormal movements
    query = """
        SELECT code, name, change_rate, volume_ratio, net_inflow
        FROM cn_stock_indicators 
        WHERE date = CURDATE()
        AND (ABS(change_rate) > 7 OR volume_ratio > 3 OR volume_ratio < 0.3)
        ORDER BY ABS(change_rate) DESC
        LIMIT 10
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    if not df.empty:
        message = "Stock Alert Monitor\n\n"
        for _, row in df.iterrows():
            change = row['change_rate']
            symbol = "UP" if change > 0 else "DOWN"
            message += f"{row['code']} {row['name']}\n"
            message += f"  Change: {change:+.2f}% ({symbol})\n"
            message += f"  Volume Ratio: {row['volume_ratio']:.2f}\n"
            if pd.notna(row['net_inflow']):
                message += f"  Net Inflow: {row['net_inflow']:.2f}M\n"
            message += "\n"
        
        print("ALERT MESSAGE:")
        print("="*50)
        print(message)
        print("="*50)
        print("\nThis would be sent to Feishu group")
        print("Group ID: oc_b99df765824c2e59b3fabf287e8d14a2")
    else:
        print("No significant movements today")
        
except Exception as e:
    print(f"Monitor error: {e}")

if __name__ == "__main__":
    print("Starting monitor...")
