#!/usr/bin/env python3
"""
拉取昨日收盘全量数据并分析
为09:30开盘报告做准备
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import os

def fetch_yesterday_market_data():
    """获取昨日市场数据"""
    print("=" * 60)
    print("拉取昨日（2026-03-02）收盘全量数据")
    print("=" * 60)
    
    # 昨日日期
    yesterday = "2026-03-02"
    
    print(f"目标日期: {yesterday}")
    
    # 首先检查本地是否有数据文件
    local_files = [
        "stock_data.csv",  # 当前目录的CSV
        "../_system/agent-home/full_stock_data_optimized_2026-03-02.csv",
        "../_system/agent-home/full_stock_data_2026-03-02.csv"
    ]
    
    for file in local_files:
        if os.path.exists(file):
            print(f"找到本地数据文件: {file}")
            try:
                df = pd.read_csv(file, encoding='utf-8-sig')
                print(f"成功加载: {len(df)} 条记录，{len(df.columns)} 列")
                
                # 检查数据日期
                if 'date' in df.columns:
                    dates = df['date'].unique()
                    print(f"数据中包含的日期: {dates[:5]}... (共{len(dates)}天)")
                
                return df
            except Exception as e:
                print(f"加载文件失败: {e}")
    
    print("未找到本地数据文件，尝试从API获取...")
    
    # 尝试从API获取数据
    api_data = fetch_from_api(yesterday)
    if api_data is not None:
        return api_data
    
    print("[ERROR] 无法获取昨日数据")
    return None

def fetch_from_api(date):
    """从API获取数据"""
    print(f"尝试从API获取 {date} 数据...")
    
    # 使用腾讯财经API
    api_urls = [
        f"http://qt.gtimg.cn/q=sh000001,sz399001",  # 指数
        # 这里可以添加更多API端点
    ]
    
    try:
        response = requests.get(api_urls[0], timeout=10)
        if response.status_code == 200:
            print(f"API响应成功，内容长度: {len(response.text)}")
            # 解析腾讯财经格式
            return parse_tencent_data(response.text, date)
        else:
            print(f"API请求失败: {response.status_code}")
    except Exception as e:
        print(f"API请求异常: {e}")
    
    return None

def parse_tencent_data(data, date):
    """解析腾讯财经数据格式"""
    print("解析腾讯财经数据...")
    
    # 腾讯财经格式示例: v_sh000001="上证指数,3200.12,3210.45,3195.67,3205.89,..."
    lines = data.strip().split(';')
    
    records = []
    for line in lines:
        if '=' in line:
            code_part, data_part = line.split('=', 1)
            code = code_part.split('_')[-1]  # 提取代码
            
            # 清理数据部分
            data_part = data_part.strip('"')
            fields = data_part.split(',')
            
            if len(fields) >= 32:  # 腾讯标准格式有32个字段
                record = {
                    'code': code,
                    'name': fields[0],
                    'open': float(fields[1]) if fields[1] else 0,
                    'pre_close': float(fields[2]) if fields[2] else 0,
                    'close': float(fields[3]) if fields[3] else 0,
                    'high': float(fields[4]) if fields[4] else 0,
                    'low': float(fields[5]) if fields[5] else 0,
                    'volume': int(fields[6]) if fields[6] else 0,
                    'amount': float(fields[7]) if fields[7] else 0,
                    'date': date
                }
                records.append(record)
    
    if records:
        df = pd.DataFrame(records)
        print(f"解析成功: {len(df)} 条记录")
        return df
    
    return None

def analyze_holdings_yesterday(df):
    """分析持仓股昨日数据"""
    print("\n" + "=" * 60)
    print("分析持仓股昨日（2026-03-02）数据")
    print("=" * 60)
    
    # 持仓股列表
    holdings = [
        {'code': '000731', 'name': '四川美丰', 'market': 'SZ'},
        {'code': '600118', 'name': '中国卫星', 'market': 'SH'},
        {'code': '600157', 'name': '永泰能源', 'market': 'SH'}
    ]
    
    results = {}
    
    for stock in holdings:
        code = stock['code']
        full_code = f"{code}.{stock['market']}"
        
        print(f"\n分析股票: {code} ({stock['name']})")
        
        # 尝试多种代码格式匹配
        code_variants = [
            code,  # 纯数字
            full_code,  # 带市场后缀
            f"sh{code}" if stock['market'] == 'SH' else f"sz{code}",  # 腾讯格式
            f"{stock['market']}{code}"  # 市场+代码
        ]
        
        stock_data = None
        matched_code = None
        
        for code_var in code_variants:
            if 'code' in df.columns:
                mask = df['code'] == code_var
            else:
                # 尝试第一列
                mask = df.iloc[:, 0].astype(str) == code_var
            
            if mask.any():
                stock_data = df[mask]
                matched_code = code_var
                print(f"  匹配成功: 使用代码格式 '{code_var}'，找到 {len(stock_data)} 条记录")
                break
        
        if stock_data is not None and len(stock_data) > 0:
            # 获取最新记录（应该是昨天的）
            latest = stock_data.iloc[-1]
            
            analysis = {
                'code': code,
                'name': stock['name'],
                'found': True,
                'matched_code': matched_code,
                'data_date': latest.get('date', '未知'),
                'yesterday_data': {},
                'technical_analysis': {},
                'signals': []
            }
            
            # 提取昨日数据
            price_fields = {
                '收盘价': ['close', '收盘价', 'new_price'],
                '开盘价': ['open', '开盘价'],
                '最高价': ['high', '最高价'],
                '最低价': ['low', '最低价'],
                '成交量': ['volume', '成交量', '成交额'],
                '涨跌幅': ['change_rate', '涨跌幅']
            }
            
            for field_cn, field_options in price_fields.items():
                for field in field_options:
                    if field in latest and pd.notna(latest[field]):
                        analysis['yesterday_data'][field_cn] = float(latest[field])
                        break
            
            # 技术指标（如果数据中有）
            tech_fields = {
                'MACD': ['macd', 'MACD'],
                'KDJ_K': ['kdj_k', 'KDJ_K'],
                'KDJ_D': ['kdj_d', 'KDJ_D'],
                'KDJ_J': ['kdj_j', 'KDJ_J'],
                'RSI': ['rsi', 'RSI'],
                'MA5': ['ma5', 'MA5', '5日均线'],
                'MA10': ['ma10', 'MA10', '10日均线'],
                'MA20': ['ma20', 'MA20', '20日均线']
            }
            
            for indicator, field_options in tech_fields.items():
                for field in field_options:
                    if field in latest and pd.notna(latest[field]):
                        analysis['technical_analysis'][indicator] = float(latest[field])
                        break
            
            # 生成交易信号
            signals = generate_signals(analysis)
            analysis['signals'] = signals
            
            results[code] = analysis
            
            # 打印简要分析
            print(f"  昨日收盘价: {analysis['yesterday_data'].get('收盘价', '未知')}")
            if '涨跌幅' in analysis['yesterday_data']:
                change = analysis['yesterday_data']['涨跌幅']
                print(f"  昨日涨跌幅: {change:.2f}%")
            
            if signals:
                print(f"  交易信号: {', '.join(signals)}")
                
        else:
            print(f"  未找到该股票的数据")
            results[code] = {
                'code': code,
                'name': stock['name'],
                'found': False,
                'reason': '数据文件中未找到该股票'
            }
    
    return results

def generate_signals(analysis):
    """生成交易信号"""
    signals = []
    tech = analysis.get('technical_analysis', {})
    
    # MACD信号
    if 'MACD' in tech:
        if tech['MACD'] > 0:
            signals.append('MACD金叉')
        else:
            signals.append('MACD死叉')
    
    # KDJ信号
    if all(k in tech for k in ['KDJ_K', 'KDJ_D']):
        k, d = tech['KDJ_K'], tech['KDJ_D']
        if k > 80 and d > 70:
            signals.append('KDJ超买')
        elif k < 20 and d < 30:
            signals.append('KDJ超卖')
    
    # RSI信号
    if 'RSI' in tech:
        rsi = tech['RSI']
        if rsi > 70:
            signals.append('RSI超买')
        elif rsi < 30:
            signals.append('RSI超卖')
    
    # 均线信号
    ma_fields = ['MA5', 'MA10', 'MA20']
    ma_values = [(name, tech[name]) for name in ma_fields if name in tech]
    
    if len(ma_values) >= 2:
        # 检查是否多头排列（短期均线在上）
        sorted_ma = sorted(ma_values, key=lambda x: x[1], reverse=True)
        expected_order = ['MA5', 'MA10', 'MA20'][:len(sorted_ma)]
        actual_order = [item[0] for item in sorted_ma]
        
        if actual_order == expected_order:
            signals.append('均线多头')
        elif actual_order == list(reversed(expected_order)):
            signals.append('均线空头')
    
    return signals

def generate_opening_report(holdings_analysis):
    """生成今日开盘详细报告"""
    print("\n" + "=" * 60)
    print("生成今日开盘详细报告")
    print("=" * 60)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""📊 今日开盘详细分析报告
生成时间: {current_time}
数据基准: 2026-03-02（昨日）收盘数据
========================================

📈 市场整体状况
---------------
• 数据日期: 2026-03-02（昨日）
• 分析时间: 09:15（集合竞价开始）
• 今日焦点: 开盘价与昨日收盘价对比
• 关键观察: 成交量、板块轮动、资金流向

📋 持仓股详细技术分析（基于昨日数据）
-----------------------------------"""

    for code, analysis in holdings_analysis.items():
        report += f"\n\n🔹 {analysis.get('name', '未知')} ({code})"
        
        if analysis['found']:
            yesterday = analysis['yesterday_data']
            tech = analysis['technical_analysis']
            signals = analysis['signals']
            
            report += f"\n✅ 数据状态: 正常（匹配代码: {analysis['matched_code']}）"
            
            # 昨日关键数据
            report += "\n📅 昨日关键数据:"
            if '收盘价' in yesterday:
                report += f"\n  • 收盘价: {yesterday['收盘价']:.2f}"
            if '涨跌幅' in yesterday:
                report += f"\n  • 涨跌幅: {yesterday['涨跌幅']:.2f}%"
            if '成交量' in yesterday:
                vol = yesterday['成交量']
                if vol > 10000:
                    report += f"\n  • 成交量: {vol/10000:.1f}万手"
                else:
                    report += f"\n  • 成交量: {vol:.0f}手"
            
            # 技术指标分析
            report += "\n📊 技术指标分析:"
            
            if 'MACD' in tech:
                macd = tech['MACD']
                status = "🔴 死叉看跌" if macd < 0 else "🟢 金叉看涨"
                report += f"\n  • MACD: {macd:.3f} ({status})"
            
            if all(k in tech for k in ['KDJ_K', 'KDJ_D', 'KDJ_J']):
                k, d, j = tech['KDJ_K'], tech['KDJ_D'], tech['KDJ_J']
                status = "🔴 超买" if k > 80 else "🟢 超卖" if k < 20 else "⚪ 正常"
                report += f"\n  • KDJ: K={k:.1f}, D={d:.1f}, J={j:.1f} ({status})"
            
            if 'RSI' in tech:
                rsi = tech['RSI']
                status = "🔴 超买" if rsi > 70 else "🟢 超卖" if rsi < 30 else "⚪ 正常"
                report += f"\n  • RSI(14): {rsi:.1f} ({status})"
            
            # 均线系统
            ma_fields = ['MA5', 'MA10', 'MA20']
            ma_values = [(name, tech[name]) for name in ma_fields if name in tech]
            
            if len(ma_values) >= 2:
                ma_values.sort(key=lambda x: x[1], reverse=True)
                if ma_values[0][0] == 'MA5':
                    report += "\n  • 均线排列: 🟢 多头排列（短期强势）"
                else:
                    report += "\n  • 均线排列: 🔴 空头排列（短期弱势）"
                
                for name, value in ma_values:
                    report += f"\n    - {name}: {value:.2f}"
            
            # 交易信号汇总
            report += "\n🎯 交易信号汇总:"
            if signals:
                for signal in signals:
                    if '金叉' in signal or '多头' in signal:
                        report += f"\n  • 🟢 {signal}"
                    elif '死叉' in signal or '空头' in signal:
                        report += f"\n  • 🔴 {signal}"
                    elif '超买' in signal:
                        report += f"\n  • 🟡 {signal}（注意风险）"
                    elif '超卖' in signal:
                        report += f"\n  • 🔵 {signal}（关注机会）"
                    else:
                        report += f"\n  • ⚪ {signal}"
            else:
                report += "\n  • ⚪ 无明显强烈信号"
            
            # 今日开盘操作建议
            report += "\n🛠️ 今日开盘操作建议:"
            if '收盘价' in yesterday:
                close_price = yesterday['收盘价']
                
                # 基于技术信号给出建议
                has_bullish = any(s in ['MACD金叉', '均线多头', 'KDJ超卖', 'RSI超卖'] for s in signals)
                has_bearish = any(s in ['MACD死叉', '均线空头', 'KDJ超买', 'RSI超买'] for s in signals)
                
                if has_bullish and not has_bearish:
                    report += "\n  • 总体信号: 🟢 偏多"
                    report += f"\n  • 建议操作: 逢低买入"
                    report += f"\n  • 买入区间: {close_price*0.98:.2f} - {close_price*1.01:.2f}"
                    report += f"\n  • 目标价位: {close_price*1.05:.2f}"
                    report += f"\n  • 止损价位: {close_price*0.95:.2f}"
                elif has_bearish and not has_bullish:
                    report += "\n  • 总体信号: 🔴 偏空"
                    report += f"\n  • 建议操作: 逢高卖出"
                    report += f"\n  • 卖出区间: {close_price*0.99:.2f} - {close_price*1.02:.