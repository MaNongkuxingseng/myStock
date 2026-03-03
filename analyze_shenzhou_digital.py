#!/usr/bin/env python3
"""
神州数码(000034)开盘前分析
为2026-03-02开盘提供操作指导
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_mock_data():
    """创建模拟的神州数码数据（由于实时API不可用）"""
    print("创建神州数码(000034)模拟数据...")
    
    # 生成最近30个交易日的数据
    dates = pd.date_range(start='2026-01-01', periods=30, freq='D')
    
    # 神州数码基本特征：IT服务，中等波动性
    base_price = 25.0  # 基础价格
    volatility = 0.03  # 日波动率
    
    np.random.seed(34)  # 固定种子，确保可重复
    
    # 生成价格序列
    returns = np.random.randn(30) * volatility
    price_series = base_price * (1 + returns).cumprod()
    
    # 创建DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': price_series * (1 + np.random.randn(30) * 0.01),
        'high': price_series * (1 + np.abs(np.random.randn(30)) * 0.02),
        'low': price_series * (1 - np.abs(np.random.randn(30)) * 0.02),
        'close': price_series,
        'volume': 50000000 + np.random.randn(30).cumsum() * 1000000
    })
    
    # 确保高低价合理
    data['high'] = data[['open', 'close', 'high']].max(axis=1) * 1.01
    data['low'] = data[['open', 'close', 'low']].min(axis=1) * 0.99
    
    data.set_index('date', inplace=True)
    
    # 添加技术指标
    data = calculate_technical_indicators(data)
    
    return data

def calculate_technical_indicators(data):
    """计算技术指标"""
    # 移动平均线
    data['MA5'] = data['close'].rolling(window=5).mean()
    data['MA10'] = data['close'].rolling(window=10).mean()
    data['MA20'] = data['close'].rolling(window=20).mean()
    
    # RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = data['close'].ewm(span=12, adjust=False).mean()
    exp2 = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
    
    # 布林带
    data['BB_Middle'] = data['close'].rolling(window=20).mean()
    bb_std = data['close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
    data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
    
    # KDJ
    low_min = data['low'].rolling(window=9).min()
    high_max = data['high'].rolling(window=9).max()
    rsv = (data['close'] - low_min) / (high_max - low_min) * 100
    data['K'] = rsv.ewm(com=2).mean()
    data['D'] = data['K'].ewm(com=2).mean()
    data['J'] = 3 * data['K'] - 2 * data['D']
    
    return data

def analyze_stock(data):
    """分析股票数据"""
    current_price = data['close'].iloc[-1]
    prev_close = data['close'].iloc[-2] if len(data) > 1 else current_price
    price_change = current_price - prev_close
    price_change_pct = (price_change / prev_close) * 100
    
    analysis = {
        'stock_code': '000034',
        'stock_name': '神州数码',
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'target_date': '2026-03-02',
        'current_data': {
            'date': data.index[-1].strftime('%Y-%m-%d'),
            'close': round(current_price, 2),
            'open': round(data['open'].iloc[-1], 2),
            'high': round(data['high'].iloc[-1], 2),
            'low': round(data['low'].iloc[-1], 2),
            'volume': int(data['volume'].iloc[-1]),
            'price_change': round(price_change, 2),
            'price_change_pct': round(price_change_pct, 2)
        },
        'technical_indicators': {},
        'trend_analysis': {},
        'risk_assessment': {},
        'trading_signals': [],
        'opening_guidance': {}
    }
    
    # 技术指标分析
    analysis['technical_indicators'] = {
        'MA': {
            'MA5': round(data['MA5'].iloc[-1], 2) if not pd.isna(data['MA5'].iloc[-1]) else None,
            'MA10': round(data['MA10'].iloc[-1], 2) if not pd.isna(data['MA10'].iloc[-1]) else None,
            'MA20': round(data['MA20'].iloc[-1], 2) if not pd.isna(data['MA20'].iloc[-1]) else None,
            'position': analyze_ma_position(data, current_price)
        },
        'RSI': {
            'value': round(data['RSI'].iloc[-1], 1) if not pd.isna(data['RSI'].iloc[-1]) else None,
            'signal': analyze_rsi_signal(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else None
        },
        'MACD': {
            'value': round(data['MACD'].iloc[-1], 3) if not pd.isna(data['MACD'].iloc[-1]) else None,
            'signal': round(data['MACD_Signal'].iloc[-1], 3) if not pd.isna(data['MACD_Signal'].iloc[-1]) else None,
            'hist': round(data['MACD_Hist'].iloc[-1], 3) if not pd.isna(data['MACD_Hist'].iloc[-1]) else None,
            'trend': analyze_macd_trend(data)
        },
        'Bollinger_Bands': {
            'upper': round(data['BB_Upper'].iloc[-1], 2) if not pd.isna(data['BB_Upper'].iloc[-1]) else None,
            'middle': round(data['BB_Middle'].iloc[-1], 2) if not pd.isna(data['BB_Middle'].iloc[-1]) else None,
            'lower': round(data['BB_Lower'].iloc[-1], 2) if not pd.isna(data['BB_Lower'].iloc[-1]) else None,
            'position': analyze_bb_position(data, current_price)
        },
        'KDJ': {
            'K': round(data['K'].iloc[-1], 1) if not pd.isna(data['K'].iloc[-1]) else None,
            'D': round(data['D'].iloc[-1], 1) if not pd.isna(data['D'].iloc[-1]) else None,
            'J': round(data['J'].iloc[-1], 1) if not pd.isna(data['J'].iloc[-1]) else None,
            'signal': analyze_kdj_signal(data)
        }
    }
    
    # 趋势分析
    analysis['trend_analysis'] = analyze_trend(data)
    
    # 风险评估
    analysis['risk_assessment'] = assess_risk(data)
    
    # 交易信号
    analysis['trading_signals'] = generate_trading_signals(analysis)
    
    # 开盘指导
    analysis['opening_guidance'] = generate_opening_guidance(analysis)
    
    return analysis

def analyze_ma_position(data, current_price):
    """分析MA位置"""
    ma5 = data['MA5'].iloc[-1] if not pd.isna(data['MA5'].iloc[-1]) else None
    ma10 = data['MA10'].iloc[-1] if not pd.isna(data['MA10'].iloc[-1]) else None
    ma20 = data['MA20'].iloc[-1] if not pd.isna(data['MA20'].iloc[-1]) else None
    
    if ma5 is None or ma10 is None or ma20 is None:
        return "数据不足"
    
    # 判断多头/空头排列
    if current_price > ma5 > ma10 > ma20:
        return "强势多头排列"
    elif current_price < ma5 < ma10 < ma20:
        return "弱势空头排列"
    elif ma5 > ma10 > ma20:
        return "多头排列"
    elif ma5 < ma10 < ma20:
        return "空头排列"
    else:
        return "震荡排列"

def analyze_rsi_signal(rsi_value):
    """分析RSI信号"""
    if rsi_value >= 70:
        return "超买"
    elif rsi_value <= 30:
        return "超卖"
    elif rsi_value > 50:
        return "偏强"
    else:
        return "偏弱"

def analyze_macd_trend(data):
    """分析MACD趋势"""
    if len(data) < 2:
        return "数据不足"
    
    macd_current = data['MACD'].iloc[-1]
    macd_prev = data['MACD'].iloc[-2]
    hist_current = data['MACD_Hist'].iloc[-1]
    
    if pd.isna(macd_current) or pd.isna(macd_prev):
        return "数据不足"
    
    if macd_current > 0 and macd_current > macd_prev:
        return "强势上涨"
    elif macd_current > 0 and macd_current < macd_prev:
        return "上涨减弱"
    elif macd_current < 0 and macd_current > macd_prev:
        return "下跌减弱"
    elif macd_current < 0 and macd_current < macd_prev:
        return "强势下跌"
    else:
        return "震荡"

def analyze_bb_position(data, current_price):
    """分析布林带位置"""
    upper = data['BB_Upper'].iloc[-1] if not pd.isna(data['BB_Upper'].iloc[-1]) else None
    lower = data['BB_Lower'].iloc[-1] if not pd.isna(data['BB_Lower'].iloc[-1]) else None
    
    if upper is None or lower is None:
        return "数据不足"
    
    bb_width = upper - lower
    bb_position = (current_price - lower) / bb_width * 100
    
    if bb_position >= 80:
        return "上轨压力"
    elif bb_position <= 20:
        return "下轨支撑"
    elif bb_position > 50:
        return "中上轨"
    else:
        return "中下轨"

def analyze_kdj_signal(data):
    """分析KDJ信号"""
    if len(data) < 2:
        return "数据不足"
    
    k_current = data['K'].iloc[-1]
    d_current = data['D'].iloc[-1]
    k_prev = data['K'].iloc[-2]
    d_prev = data['D'].iloc[-2]
    
    if pd.isna(k_current) or pd.isna(d_current) or pd.isna(k_prev) or pd.isna(d_prev):
        return "数据不足"
    
    # 金叉死叉判断
    if k_prev < d_prev and k_current > d_current:
        return "金叉买入信号"
    elif k_prev > d_prev and k_current < d_current:
        return "死叉卖出信号"
    elif k_current > 80 and d_current > 80:
        return "超买区域"
    elif k_current < 20 and d_current < 20:
        return "超卖区域"
    else:
        return "震荡区域"

def analyze_trend(data):
    """趋势分析"""
    if len(data) < 20:
        return {"short_term": "数据不足", "medium_term": "数据不足", "long_term": "数据不足"}
    
    # 短期趋势 (5日)
    short_return = (data['close'].iloc[-1] / data['close'].iloc[-5] - 1) * 100 if len(data) >= 5 else 0
    
    # 中期趋势 (10日)
    medium_return = (data['close'].iloc[-1] / data['close'].iloc[-10] - 1) * 100 if len(data) >= 10 else 0
    
    # 长期趋势 (20日)
    long_return = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100 if len(data) >= 20 else 0
    
    return {
        'short_term': {
            'trend': "上涨" if short_return > 0 else "下跌",
            'return_pct': round(short_return, 2),
            'strength': "强势" if abs(short_return) > 3 else "温和"
        },
        'medium_term': {
            'trend': "上涨" if medium_return > 0 else "下跌",
            'return_pct': round(medium_return, 2),
            'strength': "强势" if abs(medium_return) > 5 else "温和"
        },
        'long_term': {
            'trend': "上涨" if long_return > 0 else "下跌",
            'return_pct': round(long_return, 2),
            'strength': "强势" if abs(long_return) > 8 else "温和"
        }
    }

def assess_risk(data):
    """风险评估"""
    if len(data) < 20:
        return {"volatility": "数据不足", "support_level": "数据不足", "resistance_level": "数据不足"}
    
    # 波动率评估
    returns = data['close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)  # 年化波动率
    
    # 支撑阻力位
    recent_lows = data['low'].tail(20).nsmallest(3).values
    recent_highs = data['high'].tail(20).nlargest(3).values
    
    return {
        'volatility': {
            'level': "高波动" if volatility > 0.3 else ("中等波动" if volatility > 0.2 else "低波动"),
            'value': round(volatility, 3)
        },
        'support_levels': [round(x, 2) for x in recent_lows],
        'resistance_levels': [round(x, 2) for x in recent_highs],
        'risk_level': "高风险" if volatility > 0.35 else ("中风险" if volatility > 0.25 else "低风险")
    }

def generate_trading_signals(analysis):
    """生成交易信号"""
    signals = []
    
    # MA信号
    ma_position = analysis['technical_indicators']['MA']['position']
    if "多头" in ma_position and "强势" in ma_position:
        signals.append({"type": "BUY", "strength": "STRONG", "indicator": "MA", "reason": "强势多头排列"})
    elif "空头" in ma_position and "弱势" in ma_position:
        signals.append({"type": "SELL", "strength": "STRONG", "indicator": "MA", "reason": "弱势空头排列"})
    
    # RSI信号
    rsi_signal = analysis['technical_indicators']['RSI']['signal']
    if rsi_signal == "超买":
        signals.append({"type": "SELL", "strength": "MEDIUM", "indicator": "RSI", "reason": "RSI超买"})
    elif rsi_signal == "超卖":
        signals.append({"type": "BUY", "strength": "MEDIUM", "indicator": "RSI", "reason": "RSI超卖"})
    
    # MACD信号
    macd_trend = analysis['technical_indicators']['MACD']['trend']
    if "强势上涨" in macd_trend:
        signals.append({"type": "BUY", "strength": "STRONG", "indicator": "MACD", "reason": "MACD强势上涨"})
    elif "强势下跌" in macd_trend:
        signals.append({"type": "SELL", "strength": "STRONG", "indicator": "MACD", "reason": "MACD强势下跌"})
    
    # KDJ信号
    kdj_signal = analysis['technical_indicators']['KDJ']['signal']
    if "金叉" in kdj_signal:
        signals.append({"type": "BUY", "strength": "MEDIUM", "indicator