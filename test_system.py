#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目路径
cpath_current = os.path.dirname(os.path.abspath(__file__))
instock_path = os.path.join(cpath_current, "instock")
sys.path.append(instock_path)

print("=== myStock系统测试 ===")

# 测试1: 检查Python环境
print("\n1. 检查Python环境:")
print(f"Python版本: {sys.version}")
print(f"工作目录: {os.getcwd()}")

# 测试2: 检查关键模块
print("\n2. 检查关键模块:")
try:
    import pandas as pd
    print(f"✅ pandas版本: {pd.__version__}")
except ImportError as e:
    print(f"❌ pandas导入失败: {e}")

try:
    import numpy as np
    print(f"✅ numpy版本: {np.__version__}")
except ImportError as e:
    print(f"❌ numpy导入失败: {e}")

try:
    import pymysql
    print(f"✅ pymysql版本: {pymysql.__version__}")
except ImportError as e:
    print(f"❌ pymysql导入失败: {e}")

# 测试3: 检查数据库配置
print("\n3. 检查数据库配置:")
try:
    from lib import database
    print(f"✅ 数据库配置加载成功")
    print(f"   主机: {database.db_host}")
    print(f"   数据库: {database.db_database}")
except ImportError as e:
    print(f"❌ 数据库配置加载失败: {e}")

# 测试4: 检查数据抓取模块
print("\n4. 检查数据抓取模块:")
try:
    from core.crawling import stock_hist_em
    print(f"✅ 数据抓取模块加载成功")
except ImportError as e:
    print(f"❌ 数据抓取模块加载失败: {e}")

# 测试5: 检查指标计算模块
print("\n5. 检查指标计算模块:")
try:
    from core.indicator import calculate_indicator
    print(f"✅ 指标计算模块加载成功")
except ImportError as e:
    print(f"❌ 指标计算模块加载失败: {e}")

print("\n=== 测试完成 ===")