#!/usr/bin/env python3
"""
修复MySQL认证方式
将用户认证方式改为mysql_native_password
"""

import subprocess
import sys

def run_mysql_command(command):
    """运行MySQL命令"""
    try:
        # 尝试使用mysql命令行
        cmd = f'mysql -u root -p123456 -e "{command}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[OK] 命令执行成功: {command}")
            return True
        else:
            print(f"[ERROR] 命令执行失败: {command}")
            print(f"错误输出: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 执行命令时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("修复MySQL认证方式")
    print("=" * 60)
    
    # 尝试修改用户认证方式
    commands = [
        "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';",
        "FLUSH PRIVILEGES;",
        "SELECT user, host, plugin FROM mysql.user WHERE user='root';"
    ]
    
    success = True
    for cmd in commands:
        if not run_mysql_command(cmd):
            success = False
            break
    
    if success:
        print("\n[OK] MySQL认证方式修复完成")
        print("现在可以尝试使用mysql_native_password连接")
    else:
        print("\n[ERROR] MySQL认证方式修复失败")
        print("\n备用方案: 使用PyMySQL的兼容模式")
        
        # 创建使用兼容模式的连接脚本
        create_compatible_script()
    
    return success

def create_compatible_script():
    """创建兼容模式的连接脚本"""
    script_content = '''#!/usr/bin/env python3
"""
兼容模式数据库连接
使用更简单的连接方式
"""

import pymysql

def get_db_connection():
    """获取数据库连接（兼容模式）"""
    try:
        # 使用更简单的连接参数
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='mystock',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            # 尝试禁用SSL
            ssl=None,
            # 使用更兼容的选项
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30
        )
        print("[OK] 数据库连接成功（兼容模式）")
        return connection
    except Exception as e:
        print(f"[ERROR] 数据库连接失败: {e}")
        
        # 尝试更简单的连接（不带数据库）
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='123456',
                charset='utf8mb4'
            )
            print("[OK] 基础连接成功，可以访问MySQL")
            
            # 检查数据库是否存在
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES LIKE 'mystock'")
            result = cursor.fetchone()
            
            if result:
                print("[OK] mystock数据库存在")
                cursor.execute("USE mystock")
                print("[OK] 已切换到mystock数据库")
            else:
                print("[WARN] mystock数据库不存在")
                
            cursor.close()
            return connection
            
        except Exception as e2:
            print(f"[ERROR] 即使基础连接也失败: {e2}")
            return None

def test_connection():
    """测试连接"""
    print("测试数据库连接...")
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL版本: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"找到 {len(tables)} 张表")
            
            for table in tables[:5]:
                print(f"  - {table[0]}")
                
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] 查询时出错: {e}")
            return False
    else:
        return False

if __name__ == "__main__":
    test_connection()
'''
    
    with open("compatible_db_connection.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("[OK] 已创建兼容模式连接脚本: compatible_db_connection.py")

if __name__ == "__main__":
    main()