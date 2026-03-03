#!/usr/bin/env python3
"""
简单数据分析脚本
使用本地CSV文件进行7天数据分析
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_existing_data():
    """加载现有数据文件"""
    print("=" * 60)
    print("加载现有数据")
    print("=" * 60)
    
    data_files = []
    
    # 检查当前目录的数据文件
    for file in os.listdir('.'):
        if file.endswith('.csv') and 'stock' in file.lower():
            data_files.append(file)
    
    if not data_files:
        print("[ERROR] 未找到股票数据CSV文件")
        return None
    
    print(f"找到 {len(data_files)} 个数据文件:")
    for file in data_files:
        file_size = os.path.getsize(file) / 1024  # KB
        print(f"  {file} ({file_size:.1f} KB)")
    
    # 尝试加载最新的文件
    latest_file = max(data_files, key=os.path.getmtime)
    print(f"\n加载最新文件: {latest_file}")
    
    try:
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        print(f"[OK] 成功加载数据，共 {len(df)} 行，{len(df.columns)} 列")
        
        # 显示基本信息
        print(f"\n数据基本信息:")
        print(f"日期范围: {df['date'].min()} 到 {df['date'].max()}")
        print(f"股票数量: {df['code'].nunique()}")
        print(f"交易日数: {df['date'].nunique()}")
        
        return df
    except Exception as e:
        print(f"[ERROR] 加载数据失败: {e}")
        return None

def analyze_7days_data(df):
    """分析7天数据"""
    print("\n" + "=" * 60)
    print("7天数据分析")
    print("=" * 60)
    
    if df is None or len(df) == 0:
        print("[ERROR] 无数据可分析")
        return None
    
    # 检查数据天数
    unique_dates = sorted(df['date'].unique())
    num_days = len(unique_dates)
    
    print(f"实际数据天数: {num_days} 天")
    print(f"日期列表: {unique_dates}")
    
    if num_days < 7:
        print(f"[WARN] 数据不足7天，只有{num_days}天")
        print("将使用现有数据进行有限分析")
    
    # 分析持仓股（如果有的话）
    holdings = ['000731', '600118', '600157']  # 示例持仓股
    holdings_data = df[df['code'].isin(holdings)].copy()
    
    if len(holdings_data) > 0:
        print(f"\n持仓股分析 (共 {len(holdings_data)} 条记录):")
        
        for code in holdings:
            stock_data = holdings_data[holdings_data['code'] == code]
            if len(stock_data) > 0:
                print(f"\n股票 {code}:")
                print(f"  数据天数: {stock_data['date'].nunique()}")
                print(f"  最新收盘价: {stock_data['close'].iloc[-1]:.2f}")
                
                if 'volume' in stock_data.columns:
                    avg_volume = stock_data['volume'].mean()
                    print(f"  平均成交量: {avg_volume:,.0f}")
            else:
                print(f"\n股票 {code}: 无数据")
    
    # 技术指标分析
    print("\n" + "=" * 60)
    print("技术指标分析")
    print("=" * 60)
    
    technical_indicators = ['macd', 'kdj_k', 'kdj_d', 'kdj_j', 'rsi', 'ma5', 'ma10', 'ma20']
    
    indicator_status = {}
    for indicator in technical_indicators:
        if indicator in df.columns:
            has_data = df[indicator].notnull().any()
            missing = df[indicator].isnull().sum()
            total = len(df)
            missing_pct = missing / total * 100
            
            indicator_status[indicator] = {
                'has_data': has_data,
                'missing': missing,
                'missing_pct': missing_pct
            }
            
            if has_data:
                if missing_pct > 50:
                    print(f"[WARN] {indicator}: 有数据但缺失 {missing_pct:.1f}%")
                else:
                    print(f"[OK] {indicator}: 有数据 (缺失 {missing_pct:.1f}%)")
            else:
                print(f"[ERROR] {indicator}: 无数据")
        else:
            indicator_status[indicator] = {'has_data': False, 'missing': 'N/A', 'missing_pct': 100}
            print(f"[ERROR] {indicator}: 列不存在")
    
    return indicator_status

def generate_analysis_report(df, indicator_status):
    """生成分析报告"""
    print("\n" + "=" * 60)
    print("生成分析报告")
    print("=" * 60)
    
    report = {
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_summary": {
            "total_records": len(df),
            "unique_stocks": df['code'].nunique(),
            "trading_days": df['date'].nunique(),
            "date_range": f"{df['date'].min()} 到 {df['date'].max()}"
        },
        "data_quality": {
            "completeness": {},
            "issues": []
        },
        "technical_indicators": indicator_status,
        "recommendations": []
    }
    
    # 数据完整性评估
    expected_days = 7
    actual_days = df['date'].nunique()
    completeness_pct = actual_days / expected_days * 100
    
    report["data_quality"]["completeness"] = {
        "expected_days": expected_days,
        "actual_days": actual_days,
        "completeness_percentage": f"{completeness_pct:.1f}%"
    }
    
    if completeness_pct < 100:
        issue = f"数据不完整: 只有{actual_days}天数据，缺少{expected_days - actual_days}天"
        report["data_quality"]["issues"].append(issue)
        report["recommendations"].append("需要补充缺失的数据")
    
    # 技术指标评估
    missing_indicators = [ind for ind, status in indicator_status.items() 
                         if not status.get('has_data', False)]
    
    if missing_indicators:
        issue = f"技术指标缺失: {', '.join(missing_indicators)}"
        report["data_quality"]["issues"].append(issue)
        report["recommendations"].append("需要重新计算技术指标")
    
    # 生成报告文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"7days_analysis_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 分析报告已保存到: {report_file}")
    
    # 同时生成文本格式报告
    txt_report_file = f"7days_analysis_report_{timestamp}.txt"
    with open(txt_report_file, 'w', encoding='utf-8') as f:
        f.write("7天数据分析报告\n")
        f.write("=" * 60 + "\n")
        f.write(f"报告时间: {report['report_date']}\n")
        f.write(f"数据记录: {report['data_summary']['total_records']} 条\n")
        f.write(f"股票数量: {report['data_summary']['unique_stocks']} 只\n")
        f.write(f"交易日数: {report['data_summary']['trading_days']} 天\n")
        f.write(f"日期范围: {report['data_summary']['date_range']}\n")
        f.write(f"数据完整性: {report['data_quality']['completeness']['completeness_percentage']}\n")
        
        f.write("\n数据质量问题:\n")
        if report["data_quality"]["issues"]:
            for issue in report["data_quality"]["issues"]:
                f.write(f"  - {issue}\n")
        else:
            f.write("  - 无重大问题\n")
        
        f.write("\n技术指标状态:\n")
        for indicator, status in indicator_status.items():
            if status.get('has_data', False):
                f.write(f"  - {indicator}: 有数据")
                if 'missing_pct' in status and status['missing_pct'] > 0:
                    f.write(f" (缺失 {status['missing_pct']:.1f}%)")
                f.write("\n")
            else:
                f.write(f"  - {indicator}: 无数据\n")
        
        f.write("\n建议:\n")
        if report["recommendations"]:
            for rec in report["recommendations"]:
                f.write(f"  - {rec}\n")
        else:
            f.write("  - 数据质量良好，可以继续进行分析\n")
    
    print(f"[OK] 文本报告已保存到: {txt_report_file}")
    
    return report

def main():
    """主函数"""
    print("开始7天数据分析...")
    
    # 1. 加载现有数据
    df = load_existing_data()
    if df is None:
        print("[ERROR] 无法加载数据，分析终止")
        return
    
    # 2. 分析7天数据
    indicator_status = analyze_7days_data(df)
    
    # 3. 生成报告
    report = generate_analysis_report(df, indicator_status)
    
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)
    
    # 显示关键结论
    completeness = report["data_quality"]["completeness"]["completeness_percentage"]
    issues_count = len(report["data_quality"]["issues"])
    
    print(f"数据完整性: {completeness}")
    print(f"发现问题: {issues_count} 个")
    
    if issues_count == 0:
        print("[OK] 数据质量良好，可以进行下一步分析")
    else:
        print("[WARN] 发现数据质量问题，需要先修复")
        for issue in report["data_quality"]["issues"]:
            print(f"  - {issue}")

if __name__ == "__main__":
    main()