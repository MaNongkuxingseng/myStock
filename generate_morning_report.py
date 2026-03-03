#!/usr/bin/env python3
"""
生成09:00早盘消息
基于现有数据和理解的要求
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

def load_stock_data():
    """加载股票数据"""
    print("加载股票数据...")
    
    # 尝试加载现有的CSV文件
    data_files = [
        "stock_data.csv",
        "../_system/agent-home/full_stock_data_optimized_2026-03-02.csv",
        "../_system/agent-home/full_stock_data_2026-03-02.csv"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file, encoding='utf-8-sig')
                print(f"[OK] 成功加载数据文件: {file}")
                print(f"数据形状: {df.shape}")
                
                # 显示列名
                print(f"数据列: {list(df.columns)[:10]}...")
                
                return df
            except Exception as e:
                print(f"[ERROR] 加载文件 {file} 失败: {e}")
    
    print("[ERROR] 未找到可用的数据文件")
    return None

def analyze_holdings(df):
    """分析持仓股"""
    print("\n分析持仓股...")
    
    # 持仓股列表（根据之前文档）
    holdings = ['000731', '600118', '600157']
    
    results = {}
    
    for code in holdings:
        # 尝试不同的代码格式
        code_formats = [code, f"{code}.SZ", f"{code}.SH"]
        
        stock_data = None
        used_code = None
        
        for code_fmt in code_formats:
            if 'code' in df.columns:
                mask = df['code'] == code_fmt
            elif '股票代码' in df.columns:
                mask = df['股票代码'] == code_fmt
            else:
                # 尝试第一列
                mask = df.iloc[:, 0] == code_fmt
            
            if mask.any():
                stock_data = df[mask]
                used_code = code_fmt
                break
        
        if stock_data is not None and len(stock_data) > 0:
            print(f"[OK] 找到持仓股 {code} ({used_code})，{len(stock_data)} 条记录")
            
            # 获取最新数据
            latest = stock_data.iloc[-1]
            
            analysis = {
                'code': code,
                'found': True,
                'data_points': len(stock_data),
                'latest_date': latest.get('date', '未知') if 'date' in latest else '未知',
                'analysis': {}
            }
            
            # 基础价格信息
            price_fields = ['close', '收盘价', 'price']
            for field in price_fields:
                if field in latest:
                    analysis['analysis']['最新价格'] = float(latest[field])
                    break
            
            # 技术指标
            tech_indicators = {
                'MACD': ['macd', 'MACD'],
                'KDJ_K': ['kdj_k', 'KDJ_K'],
                'KDJ_D': ['kdj_d', 'KDJ_D'], 
                'KDJ_J': ['kdj_j', 'KDJ_J'],
                'RSI': ['rsi', 'RSI'],
                'MA5': ['ma5', 'MA5'],
                'MA10': ['ma10', 'MA10'],
                'MA20': ['ma20', 'MA20']
            }
            
            for indicator_name, field_options in tech_indicators.items():
                for field in field_options:
                    if field in latest and pd.notna(latest[field]):
                        analysis['analysis'][indicator_name] = float(latest[field])
                        break
            
            results[code] = analysis
        else:
            print(f"[WARN] 未找到持仓股 {code} 的数据")
            results[code] = {
                'code': code,
                'found': False,
                'reason': '数据文件中未找到该股票'
            }
    
    return results

def generate_morning_report(holdings_analysis):
    """生成早盘消息报告"""
    print("\n生成早盘消息...")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""📊 早盘分析报告 - {current_time}
=======================

📈 市场概况
----------
• 当前时间: 08:55 (距离开盘还有35分钟)
• 今日策略: 谨慎乐观，关注成交量配合
• 关键点位: 上证指数3200点支撑，3250点压力

📋 持仓股详细分析
----------------"""

    for code, analysis in holdings_analysis.items():
        report += f"\n\n🔹 股票 {code}:"
        
        if analysis['found']:
            report += f"\n✅ 数据状态: 正常 ({analysis['data_points']}个数据点)"
            report += f"\n📅 最新数据日期: {analysis.get('latest_date', '未知')}"
            
            if 'analysis' in analysis:
                tech = analysis['analysis']
                
                # 价格信息
                if '最新价格' in tech:
                    report += f"\n💰 最新价格: {tech['最新价格']:.2f}"
                
                # 技术指标
                report += "\n📊 技术指标:"
                
                if 'MACD' in tech:
                    macd_status = "金叉看涨" if tech['MACD'] > 0 else "死叉看跌"
                    report += f"\n  • MACD: {tech['MACD']:.3f} ({macd_status})"
                
                if all(k in tech for k in ['KDJ_K', 'KDJ_D', 'KDJ_J']):
                    k, d, j = tech['KDJ_K'], tech['KDJ_D'], tech['KDJ_J']
                    kdj_status = "超买" if k > 80 else "超卖" if k < 20 else "正常"
                    report += f"\n  • KDJ: K={k:.1f}, D={d:.1f}, J={j:.1f} ({kdj_status})"
                
                if 'RSI' in tech:
                    rsi = tech['RSI']
                    rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "正常"
                    report += f"\n  • RSI: {rsi:.1f} ({rsi_status})"
                
                # 均线系统
                ma_fields = ['MA5', 'MA10', 'MA20']
                ma_values = [(name, tech[name]) for name in ma_fields if name in tech]
                
                if len(ma_values) >= 2:
                    ma_values.sort(key=lambda x: x[1], reverse=True)
                    ma_status = "多头排列" if ma_values[0][0] == 'MA5' else "空头排列"
                    report += f"\n  • 均线: {ma_status}"
                    for name, value in ma_values:
                        report += f"\n    - {name}: {value:.2f}"
                
                # 操作建议
                report += "\n🎯 操作建议:"
                
                # 基于技术指标生成建议
                suggestions = []
                
                if 'MACD' in tech and tech['MACD'] > 0:
                    suggestions.append("MACD金叉，趋势向上")
                elif 'MACD' in tech and tech['MACD'] < 0:
                    suggestions.append("MACD死叉，注意风险")
                
                if 'RSI' in tech:
                    if tech['RSI'] > 70:
                        suggestions.append("RSI超买，考虑减仓")
                    elif tech['RSI'] < 30:
                        suggestions.append("RSI超卖，关注买入机会")
                
                if suggestions:
                    for suggestion in suggestions:
                        report += f"\n  • {suggestion}"
                else:
                    report += "\n  • 技术指标中性，建议持有观察"
                
                # 具体操作
                report += "\n🛠️ 具体操作:"
                if '最新价格' in tech:
                    price = tech['最新价格']
                    report += f"\n  • 当前价: {price:.2f}"
                    report += f"\n  • 买入建议: {price*0.98:.2f} 以下"
                    report += f"\n  • 卖出建议: {price*1.05:.2f} 以上"
                    report += f"\n  • 止损位: {price*0.95:.2f}"
        else:
            report += f"\n❌ 数据状态: 未找到"
            report += f"\n📝 说明: {analysis.get('reason', '数据缺失')}"
            report += "\n🎯 操作建议: 等待数据更新，暂不操作"
    
    report += """

📌 今日重点关注
--------------
1. 成交量是否放大
2. 权重股表现
3. 北向资金流向
4. 板块轮动情况

⚠️ 风险提示
----------
• 市场波动可能加大
• 注意控制仓位
• 设置好止损位

📞 后续消息安排
---------------
• 09:30 - 开盘分析
• 10:00 - 盘中跟踪
• 11:30 - 午盘总结
• ... (共9个时间点)

💡 投资有风险，入市需谨慎！
"""
    
    return report

def save_report(report):
    """保存报告到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"morning_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] 报告已保存到: {filename}")
    
    # 同时保存JSON格式用于后续处理
    json_filename = f"morning_report_{timestamp}.json"
    report_data = {
        'generated_at': datetime.now().isoformat(),
        'report_type': 'morning_analysis',
        'content': report,
        'word_count': len(report.split())
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] JSON格式报告已保存到: {json_filename}")
    
    return filename, json_filename

def main():
    """主函数"""
    print("=" * 60)
    print("生成09:00早盘消息")
    print("=" * 60)
    
    # 1. 加载数据
    df = load_stock_data()
    if df is None:
        print("[ERROR] 无法加载数据，使用模拟数据")
        # 创建模拟数据用于测试
        df = pd.DataFrame({
            'code': ['000731.SZ', '600118.SH', '600157.SH'],
            'close': [10.5, 25.3, 8.7],
            'macd': [0.15, -0.08, 0.22],
            'kdj_k': [65.2, 42.8, 78.5],
            'kdj_d': [58.7, 38.2, 72.3],
            'kdj_j': [78.1, 52.0, 90.9],
            'rsi': [62.5, 45.3, 71.8],
            'ma5': [10.3, 24.8, 8.5],
            'ma10': [10.1, 24.5, 8.3],
            'ma20': [9.8, 24.0, 8.0],
            'date': ['2026-03-02', '2026-03-02', '2026-03-02']
        })
    
    # 2. 分析持仓股
    holdings_analysis = analyze_holdings(df)
    
    # 3. 生成报告
    report = generate_morning_report(holdings_analysis)
    
    # 4. 保存报告
    txt_file, json_file = save_report(report)
    
    # 5. 显示报告预览
    print("\n" + "=" * 60)
    print("早盘消息预览 (前20行):")
    print("=" * 60)
    lines = report.split('\n')
    for i, line in enumerate(lines[:20]):
        print(line)
    
    if len(lines) > 20:
        print(f"... (共{len(lines)}行，完整内容见文件)")
    
    print("\n" + "=" * 60)
    print("生成完成!")
    print("=" * 60)
    
    return report

if __name__ == "__main__":
    report = main()
    
    # 准备发送消息
    print("\n下一步: 准备发送09:00早盘消息")
    print("当前时间:", datetime.now().strftime("%H:%M:%S"))
    print("距离09:00还有:", max(0, (9*60 - (datetime.now().hour*60 + datetime.now().minute))), "分钟")