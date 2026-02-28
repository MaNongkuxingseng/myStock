#!/usr/bin/env python3
"""
Test database connection for myStock
"""

import sys
sys.path.append('D:\\python_libs')

try:
    import pymysql
    
    # Try different passwords
    passwords = ['root', '785091', 'password', '']
    
    for pwd in passwords:
        try:
            print(f"Trying password: {pwd}")
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password=pwd,
                database='instockdb',
                port=3306,
                charset='utf8mb4'
            )
            print(f"SUCCESS with password: {pwd}")
            
            # Check tables
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Found {len(tables)} tables")
            
            for table in tables[:10]:  # Show first 10 tables
                print(f"  - {table[0]}")
            
            cursor.close()
            conn.close()
            break
            
        except pymysql.Error as e:
            print(f"  Failed: {e}")
            continue
            
except Exception as e:
    print(f"Error: {e}")