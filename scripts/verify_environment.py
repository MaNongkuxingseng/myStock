#!/usr/bin/env python3
"""
myStock 1.1版本 - 环境验证脚本
验证开发环境是否准备就绪
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_status(name: str, status: bool, details: str = ""):
    """打印状态"""
    icon = "[OK]" if status else "[FAIL]"
    print(f"{icon} {name}: {details}")

def check_python():
    """检查Python环境"""
    print_header("Python环境检查")
    
    # 检查Python版本
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    is_valid = version >= (3, 8)
    print_status("Python版本", is_valid, version_str)
    
    # 检查必要模块
    required_modules = [
        "pandas", "numpy", "sqlalchemy", "mysql.connector",
        "requests", "schedule", "logging", "json", "datetime"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print_status(f"模块: {module}", True, "已安装")
        except ImportError:
            print_status(f"模块: {module}", False, "未安装")
    
    return is_valid

def check_git():
    """检查Git环境"""
    print_header("Git环境检查")
    
    try:
        # 检查Git版本
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print_status("Git", True, version)
        
        # 检查当前分支
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        branch = result.stdout.strip()
        print_status("当前分支", True, branch)
        
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("Git", False, "未安装或配置错误")
        return False

def check_mysql():
    """检查MySQL环境"""
    print_header("MySQL环境检查")
    
    try:
        # 尝试连接MySQL
        import mysql.connector
        
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=""
            )
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                print_status("MySQL服务", True, f"版本: {version}")
                return True
        except mysql.connector.Error as e:
            print_status("MySQL服务", False, f"连接失败: {e}")
            return False
            
    except ImportError:
        print_status("MySQL连接器", False, "mysql-connector-python未安装")
        return False

def check_project_structure():
    """检查项目结构"""
    print_header("项目结构检查")
    
    base_dir = Path(__file__).parent.parent
    required_dirs = [
        "src",
        "src/core",
        "src/core/data",
        "src/core/analysis", 
        "src/core/push",
        "src/core/utils",
        "src/api",
        "src/config",
        "src/tests",
        "docs",
        "scripts",
        "deployment"
    ]
    
    all_exists = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        exists = full_path.exists()
        print_status(f"目录: {dir_path}", exists)
        if not exists:
            all_exists = False
    
    # 检查必要文件
    required_files = [
        "src/config/settings.py",
        "src/core/utils/helpers.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file_path in required_files:
        full_path = base_dir / file_path
        exists = full_path.exists()
        print_status(f"文件: {file_path}", exists)
        if not exists:
            all_exists = False
    
    return all_exists

def check_development_status():
    """检查开发状态"""
    print_header("开发状态检查")
    
    base_dir = Path(__file__).parent.parent
    
    # 检查开发日志
    log_files = list(base_dir.glob("DEVELOPMENT_LOG_*.md"))
    if log_files:
        latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
        print_status("开发日志", True, f"最新: {latest_log.name}")
    else:
        print_status("开发日志", False, "未找到开发日志")
    
    # 检查Git提交
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            cwd=base_dir
        )
        commits = result.stdout.strip().split('\n')
        if commits and commits[0]:
            print_status("最近提交", True, commits[0])
        else:
            print_status("最近提交", False, "无提交记录")
    except:
        print_status("Git提交", False, "检查失败")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print(" myStock 1.1版本 - 环境验证工具")
    print("=" * 60)
    
    checks = [
        ("Python环境", check_python),
        ("Git环境", check_git),
        ("MySQL环境", check_mysql),
        ("项目结构", check_project_structure),
        ("开发状态", check_development_status)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n正在检查: {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"检查失败: {e}")
            results.append((name, False))
    
    # 总结
    print_header("环境验证总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"通过检查: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] All environment checks passed! Ready to start development.")
        return 0
    else:
        print("\n[WARNING] Some environment checks failed. Please fix the following issues:")
        for name, result in results:
            if not result:
                print(f"  • {name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())