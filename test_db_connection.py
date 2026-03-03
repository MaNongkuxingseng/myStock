#!/usr/bin/env python3
"""
测试数据库连接
"""

import pymysql
import sys

def test_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    
    # 尝试不同的连接参数
    test_configs = [
        {
            "name": "标准连接",
            "host": "localhost",
            "user": "root",
            "password": "123456",
            "database": "mystock",
            "charset": "utf8mb4"
        },
        {
            "name": "无密码连接",
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "mystock",
            "charset": "utf8mb4"
        },
        {
            "name": "使用旧认证方式",
            "host": "localhost",
            "user": "root",
            "password": "123456",
            "database": "mystock",
            "charset": "utf8mb4",
            "auth_plugin": "mysql_native_password"
        }
    ]
    
    for config in test_configs:
        print(f"\n尝试: {config['name']}")
        try:
            # 移除auth_plugin参数，因为pymysql可能不支持
            connection_params = {k: v for k, v in config.items() if k != 'auth_plugin' and k != 'name'}
            
            connection = pymysql.connect(**connection_params)
            print("[OK] 连接成功!")
            
            # 测试查询
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL版本: {version[0]}")
            
            # 检查数据库
            cursor.execute("SHOW DATABASES LIKE 'mystock'")
            db_exists = cursor.fetchone()
            if db_exists:
                print("[OK] mystock数据库存在")
                
                # 切换到mystock数据库
                cursor.execute("USE mystock")
                
                # 检查表
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"找到 {len(tables)} 张表")
                
                # 显示前5张表
                for i, table in enumerate(tables[:5]):
                    print(f"  {i+1}. {table[0]}")
                    
            else:
                print("[ERROR] mystock数据库不存在")
            
            cursor.close()
            connection.close()
            return True
            
        except pymysql.Error as e:
            print(f"[ERROR] 连接失败: {e}")
            continue
    
    return False

def check_mysql_service():
    """检查MySQL服务状态"""
    print("\n检查MySQL服务状态...")
    try:
        import subprocess
        result = subprocess.run(['sc', 'query', 'MySQLValen'], 
                              capture_output=True, text=True, shell=True)
        if 'RUNNING' in result.stdout:
            print("[OK] MySQL服务正在运行")
            return True
        else:
            print("[ERROR] MySQL服务未运行")
            print(f"服务状态: {result.stdout}")
            return False
    except Exception as e:
        print(f"[ERROR] 检查服务状态时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("数据库连接测试")
    print("=" * 60)
    
    # 检查服务状态
    service_ok = check_mysql_service()
    if not service_ok:
        print("\n[ERROR] MySQL服务有问题，请先启动服务")
        return
    
    # 测试连接
    connection_ok = test_connection()
    
    if connection_ok:
        print("\n[OK] 数据库连接测试通过")
    else:
        print("\n[ERROR] 数据库连接测试失败")
        print("\n建议:")
        print("1. 检查MySQL服务是否运行")
        print("2. 检查用户名和密码是否正确")
        print("3. 尝试使用命令行连接: mysql -u root -p")
        print("4. 检查防火墙设置")
        print("5. 尝试重启MySQL服务")

if __name__ == "__main__":
    main()