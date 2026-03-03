#!/usr/bin/env python3
"""
简单数据拉取脚本
用于测试7天数据拉取功能
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import pymysql
from pymysql import Error

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host='localhost',
            database='mystock',
            user='root',
            password='123456',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

def get_7days_stock_data():
    """获取7天股票数据"""
    print("=" * 60)
    print("7天股票数据拉取")
    print("=" * 60)
    
    connection = get_db_connection()
    if not connection:
        print("❌ 无法连接数据库")
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 计算7天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"数据范围: {start_date} 到 {end_date}")
        
        # 查询7天数据
        query = """
        SELECT 
            code, name, date, 
            open, high, low, close, volume,
            macd, kdj_k, kdj_d, kdj_j, rsi,
            ma5, ma10, ma20, ma30, ma60
        FROM cn_stock_selection 
        WHERE date >= %s AND date <= %s
        ORDER BY date DESC, code
        LIMIT 10000
        """
        
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        
        print(f"查询到 {len(results)} 条记录")
        
        if len(results) == 0:
            print("[ERROR] 未找到数据")
            return None
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        # 统计信息
        print("\n数据统计:")
        print(f"股票数量: {df['code'].nunique()}")
        print(f"日期范围: {df['date'].min()} 到 {df['date'].max()}")
        print(f"交易日数: {df['date'].nunique()}")
        
        # 检查数据完整性
        date_counts = df.groupby('date').size()
        print("\n每日数据量:")
        for date, count in date_counts.items():
            print(f"  {date}: {count} 条记录")
        
        # 保存到CSV文件
        output_file = f"7days_stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n[OK] 数据已保存到: {output_file}")
        
        # 生成数据质量报告
        generate_data_quality_report(df, start_date, end_date)
        
        return df
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_data_quality_report(df, start_date, end_date):
    """生成数据质量报告"""
    print("\n" + "=" * 60)
    print("数据质量报告")
    print("=" * 60)
    
    report = {
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_range": f"{start_date} 到 {end_date}",
        "total_records": len(df),
        "unique_stocks": df['code'].nunique(),
        "trading_days": df['date'].nunique(),
        "data_completeness": {},
        "missing_values": {},
        "data_quality_issues": []
    }
    
    # 检查数据完整性
    expected_days = 7
    actual_days = df['date'].nunique()
    completeness = actual_days / expected_days * 100
    
    report["data_completeness"] = {
        "expected_days": expected_days,
        "actual_days": actual_days,
        "completeness_percentage": f"{completeness:.1f}%"
    }
    
    print(f"数据完整性: {actual_days}/{expected_days} 天 ({completeness:.1f}%)")
    
    if completeness < 100:
        report["data_quality_issues"].append(f"数据不完整: 只有{actual_days}天数据，缺少{expected_days - actual_days}天")
        print(f"⚠️  数据不完整: 只有{actual_days}天数据")
    
    # 检查缺失值
    numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'macd', 'kdj_k', 'kdj_d', 'kdj_j', 'rsi']
    for col in numeric_columns:
        if col in df.columns:
            missing = df[col].isnull().sum()
            total = len(df)
            missing_percentage = missing / total * 100 if total > 0 else 0
            
            report["missing_values"][col] = {
                "missing_count": int(missing),
                "total_count": total,
                "missing_percentage": f"{missing_percentage:.1f}%"
            }
            
            if missing_percentage > 10:
                report["data_quality_issues"].append(f"高缺失率: {col} 缺失 {missing_percentage:.1f}%")
                print(f"[WARN]  {col}: 缺失 {missing} 条 ({missing_percentage:.1f}%)")
            elif missing > 0:
                print(f"[INFO]  {col}: 缺失 {missing} 条 ({missing_percentage:.1f}%)")
    
    # 检查技术指标数据
    technical_indicators = ['macd', 'kdj_k', 'kdj_d', 'kdj_j', 'rsi']
    for indicator in technical_indicators:
        if indicator in df.columns:
            has_data = df[indicator].notnull().any()
            if not has_data:
                report["data_quality_issues"].append(f"技术指标缺失: {indicator} 无数据")
                print(f"[ERROR] {indicator}: 无数据")
            else:
                print(f"[OK] {indicator}: 有数据")
    
    # 保存报告
    report_file = f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 数据质量报告已保存到: {report_file}")
    
    return report

def check_technical_indicators():
    """检查技术指标数据"""
    print("\n" + "=" * 60)
    print("技术指标检查")
    print("=" * 60)
    
    connection = get_db_connection()
    if not connection:
        print("❌ 无法连接数据库")
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 检查技术指标表
        tables_to_check = [
            'cn_stock_indicators_sell',
            'cn_stock_indicators_buy',
            'cn_stock_technical_indicators'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            exists = cursor.fetchone() is not None
            
            if exists:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"✅ {table}: 存在，有 {count} 条记录")
            else:
                print(f"❌ {table}: 不存在")
        
        # 检查指标字段
        if 'cn_stock_technical_indicators' in tables_to_check:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'cn_stock_technical_indicators'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print("\n技术指标表字段:")
            for col in columns:
                print(f"  {col['column_name']} ({col['data_type']})")
        
    except Error as e:
        print(f"数据库查询错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """主函数"""
    print("开始7天数据拉取和分析...")
    
    # 检查数据库连接
    print("\n1. 检查数据库连接...")
    connection = get_db_connection()
    if connection:
        print("✅ 数据库连接成功")
        connection.close()
    else:
        print("❌ 数据库连接失败")
        return
    
    # 检查技术指标
    check_technical_indicators()
    
    # 拉取7天数据
    print("\n2. 拉取7天股票数据...")
    df = get_7days_stock_data()
    
    if df is not None:
        print("\n✅ 7天数据拉取完成")
        
        # 显示样本数据
        print("\n样本数据 (前5行):")
        print(df.head())
        
        # 显示统计信息
        print("\n基本统计信息:")
        print(df.describe())
        
    else:
        print("\n❌ 数据拉取失败")
    
    print("\n" + "=" * 60)
    print("数据拉取和分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main()