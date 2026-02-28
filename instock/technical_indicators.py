#!/usr/bin/env python3
"""
技术指标计算模块
为StockBot提供专业的技术分析指标
"""

import numpy as np
from datetime import datetime, timedelta
import json
import os

class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        self.indicators_config = {
            'trend_indicators': ['MA', 'EMA', 'MACD', 'BOLL'],
            'momentum_indicators': ['RSI', 'KDJ', 'WR', 'CCI'],
            'volume_indicators': ['OBV', 'VOLRATIO', 'MFI'],
            'volatility_indicators': ['ATR', 'BBWIDTH']
        }
    
    def calculate_ma(self, prices, period=5):
        """计算移动平均线"""
        if len(prices) < period:
            return None
        
        ma_values = []
        for i in range(len(prices) - period + 1):
            ma = sum(prices[i:i+period]) / period
            ma_values.append(round(ma, 3))
        
        return ma_values
    
    def calculate_ema(self, prices, period=12):
        """计算指数移动平均线"""
        if len(prices) < period:
            return None
        
        ema_values = []
        multiplier = 2 / (period + 1)
        
        # 第一个EMA是简单MA
        first_ema = sum(prices[:period]) / period
        ema_values.append(round(first_ema, 3))
        
        # 计算后续EMA
        for i in range(period, len(prices)):
            ema = (prices[i] - ema_values[-1]) * multiplier + ema_values[-1]
            ema_values.append(round(ema, 3))
        
        return ema_values
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        if len(prices) < slow:
            return None
        
        # 计算快慢EMA
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        if not ema_fast or not ema_slow:
            return None
        
        # 调整长度
        min_len = min(len(ema_fast), len(ema_slow))
        ema_fast = ema_fast[-min_len:]
        ema_slow = ema_slow[-min_len:]
        
        # 计算DIF
        dif = [fast_val - slow_val for fast_val, slow_val in zip(ema_fast, ema_slow)]
        
        # 计算DEA (DIF的EMA)
        dea = self.calculate_ema(dif, signal) if len(dif) >= signal else None
        
        # 计算MACD柱
        macd_hist = None
        if dea and len(dif) == len(dea):
            macd_hist = [d - e for d, e in zip(dif, dea)]
        
        return {
            'dif': dif[-1] if dif else None,
            'dea': dea[-1] if dea else None,
            'macd': macd_hist[-1] if macd_hist else None,
            'signal': 'golden' if dif and dea and dif[-1] > dea[-1] else 'dead' if dif and dea and dif[-1] < dea[-1] else 'neutral'
        }
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI相对强弱指数"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # 计算平均增益和平均损失
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # 计算RSI
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_bollinger(self, prices, period=20, std_dev=2):
        """计算布林带指标"""
        if len(prices) < period:
            return None
        
        # 计算中轨 (MA)
        middle_band = sum(prices[-period:]) / period
        
        # 计算标准差
        variance = sum((x - middle_band) ** 2 for x in prices[-period:]) / period
        std = variance ** 0.5
        
        # 计算上下轨
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        # 当前价格位置
        current_price = prices[-1]
        position = (current_price - lower_band) / (upper_band - lower_band) * 100 if upper_band > lower_band else 50
        
        return {
            'upper': round(upper_band, 3),
            'middle': round(middle_band, 3),
            'lower': round(lower_band, 3),
            'width': round((upper_band - lower_band) / middle_band * 100, 2),  # 布林带宽度百分比
            'position': round(position, 1),  # 价格在布林带中的位置百分比
            'signal': 'overbought' if position > 80 else 'oversold' if position < 20 else 'normal'
        }
    
    def calculate_kdj(self, high_prices, low_prices, close_prices, period=9):
        """计算KDJ指标"""
        if len(close_prices) < period:
            return None
        
        # 计算RSV
        rsv_values = []
        for i in range(period-1, len(close_prices)):
            highest_high = max(high_prices[i-period+1:i+1])
            lowest_low = min(low_prices[i-period+1:i+1])
            
            if highest_high != lowest_low:
                rsv = (close_prices[i] - lowest_low) / (highest_high - lowest_low) * 100
            else:
                rsv = 50
            
            rsv_values.append(rsv)
        
        # 计算K、D、J值
        k_values = [50]  # 初始K值
        d_values = [50]  # 初始D值
        
        for rsv in rsv_values:
            k = (2/3) * k_values[-1] + (1/3) * rsv
            d = (2/3) * d_values[-1] + (1/3) * k
            k_values.append(k)
            d_values.append(d)
        
        # J值 = 3K - 2D
        j_values = [3*k - 2*d for k, d in zip(k_values, d_values)]
        
        return {
            'K': round(k_values[-1], 2),
            'D': round(d_values[-1], 2),
            'J': round(j_values[-1], 2),
            'signal': 'golden' if k_values[-1] > d_values[-1] and k_values[-2] <= d_values[-2] else 
                     'dead' if k_values[-1] < d_values[-1] and k_values[-2] >= d_values[-2] else 
                     'overbought' if k_values[-1] > 80 else 'oversold' if k_values[-1] < 20 else 'neutral'
        }
    
    def calculate_volume_ratio(self, volumes, period=5):
        """计算量比"""
        if len(volumes) < period:
            return None
        
        current_volume = volumes[-1]
        avg_volume = sum(volumes[-period:]) / period
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        return round(volume_ratio, 2)
    
    def calculate_atr(self, high_prices, low_prices, close_prices, period=14):
        """计算平均真实波幅(ATR)"""
        if len(close_prices) < period + 1:
            return None
        
        tr_values = []
        for i in range(1, len(close_prices)):
            tr1 = high_prices[i] - low_prices[i]  # 当日高低差
            tr2 = abs(high_prices[i] - close_prices[i-1])  # 当日最高-前日收盘
            tr3 = abs(low_prices[i] - close_prices[i-1])   # 当日最低-前日收盘
            tr = max(tr1, tr2, tr3)
            tr_values.append(tr)
        
        # 计算ATR
        atr = sum(tr_values[-period:]) / period
        
        return round(atr, 3)
    
    def analyze_stock_technicals(self, stock_data, history_days=30):
        """综合分析股票技术指标"""
        if not stock_data or 'history' not in stock_data:
            return None
        
        history = stock_data['history']
        if len(history) < 20:  # 至少需要20天数据
            return None
        
        # 提取数据
        closes = [day['close'] for day in history]
        highs = [day['high'] for day in history]
        lows = [day['low'] for day in history]
        volumes = [day['volume'] for day in history]
        
        current_price = closes[-1]
        
        # 计算各项指标
        analysis = {
            'trend': {},
            'momentum': {},
            'volume': {},
            'volatility': {},
            'summary': {}
        }
        
        # 趋势指标
        ma5 = self.calculate_ma(closes, 5)
        ma10 = self.calculate_ma(closes, 10)
        ma20 = self.calculate_ma(closes, 20)
        
        if ma5 and ma10:
            analysis['trend']['MA'] = {
                'MA5': ma5[-1] if ma5 else None,
                'MA10': ma10[-1] if ma10 else None,
                'MA20': ma20[-1] if ma20 else None,
                'signal': 'bullish' if current_price > ma5[-1] > ma10[-1] > ma20[-1] else 
                         'bearish' if current_price < ma5[-1] < ma10[-1] < ma20[-1] else 
                         'neutral'
            }
        
        # MACD
        macd = self.calculate_macd(closes)
        if macd:
            analysis['trend']['MACD'] = macd
        
        # 布林带
        boll = self.calculate_bollinger(closes)
        if boll:
            analysis['trend']['BOLL'] = boll
        
        # 动量指标
        rsi = self.calculate_rsi(closes)
        if rsi:
            analysis['momentum']['RSI'] = {
                'value': rsi,
                'signal': 'overbought' if rsi > 70 else 'oversold' if rsi < 30 else 'neutral'
            }
        
        # KDJ
        kdj = self.calculate_kdj(highs, lows, closes)
        if kdj:
            analysis['momentum']['KDJ'] = kdj
        
        # 成交量指标
        volume_ratio = self.calculate_volume_ratio(volumes)
        if volume_ratio:
            analysis['volume']['VOLUME_RATIO'] = {
                'value': volume_ratio,
                'signal': 'high' if volume_ratio > 2 else 'low' if volume_ratio < 0.5 else 'normal'
            }
        
        # 波动率指标
        atr = self.calculate_atr(highs, lows, closes)
        if atr:
            analysis['volatility']['ATR'] = {
                'value': atr,
                'percent': round(atr / current_price * 100, 2)
            }
        
        # 综合评分
        score = self.calculate_technical_score(analysis)
        analysis['summary'] = {
            'technical_score': score,
            'trend_strength': self.assess_trend_strength(analysis),
            'momentum_strength': self.assess_momentum_strength(analysis),
            'risk_level': self.assess_risk_level(analysis),
            'recommendation': self.generate_recommendation(analysis)
        }
        
        return analysis
    
    def calculate_technical_score(self, analysis):
        """计算技术分析综合评分(0-100)"""
        score = 50  # 基础分
        
        # 趋势得分
        if 'MA' in analysis['trend']:
            ma_signal = analysis['trend']['MA']['signal']
            if ma_signal == 'bullish':
                score += 15
            elif ma_signal == 'bearish':
                score -= 15
        
        if 'MACD' in analysis['trend']:
            macd_signal = analysis['trend']['MACD']['signal']
            if macd_signal == 'golden':
                score += 10
            elif macd_signal == 'dead':
                score -= 10
        
        # 动量得分
        if 'RSI' in analysis['momentum']:
            rsi_value = analysis['momentum']['RSI']['value']
            if 30 <= rsi_value <= 70:
                score += 5
            elif rsi_value < 30:  # 超卖
                score += 10
            else:  # 超买
                score -= 5
        
        # 成交量得分
        if 'VOLUME_RATIO' in analysis['volume']:
            vol_ratio = analysis['volume']['VOLUME_RATIO']['value']
            if 0.8 <= vol_ratio <= 1.5:
                score += 5
            elif vol_ratio > 1.5:  # 放量
                score += 10
        
        # 确保分数在0-100之间
        return max(0, min(100, score))
    
    def assess_trend_strength(self, analysis):
        """评估趋势强度"""
        strength = 'weak'
        
        bullish_signals = 0
        bearish_signals = 0
        
        # 检查趋势指标
        if 'MA' in analysis['trend'] and analysis['trend']['MA']['signal'] == 'bullish':
            bullish_signals += 1
        elif 'MA' in analysis['trend'] and analysis['trend']['MA']['signal'] == 'bearish':
            bearish_signals += 1
        
        if 'MACD' in analysis['trend'] and analysis['trend']['MACD']['signal'] == 'golden':
            bullish_signals += 1
        elif 'MACD' in analysis['trend'] and analysis['trend']['MACD']['signal'] == 'dead':
            bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            strength = 'strong_bullish' if bullish_signals >= 2 else 'weak_bullish'
        elif bearish_signals > bullish_signals:
            strength = 'strong_bearish' if bearish_signals >= 2 else 'weak_bearish'
        
        return strength
    
    def assess_momentum_strength(self, analysis):
        """评估动量强度"""
        if 'RSI' not in analysis['momentum']:
            return 'neutral'
        
        rsi_value = analysis['momentum']['RSI']['value']
        
        if rsi_value > 70:
            return 'overbought'
        elif rsi_value < 30:
            return 'oversold'
        elif rsi_value > 60:
            return 'strong_bullish'
        elif rsi_value < 40:
            return 'strong_bearish'
        else:
            return 'neutral'
    
    def assess_risk_level(self, analysis):
        """评估风险等级"""
        risk = 'medium'
        
        # 检查超买超卖
        if 'RSI' in analysis['momentum']:
            rsi_signal = analysis['momentum']['RSI']['signal']
            if rsi_signal in ['overbought', 'oversold']:
                risk = 'high'
        
        # 检查布林带位置
        if 'BOLL' in analysis['trend']:
            boll_signal = analysis['trend']['BOLL']['signal']
            if boll_signal in ['overbought', 'oversold']:
                risk = 'high'
        
        # 检查波动率
        if 'ATR' in analysis['volatility']:
            atr_percent = analysis['volatility']['ATR']['percent']
            if atr_percent > 3:
                risk = 'high'
            elif atr_percent < 1:
                risk = 'low'
        
        return risk
    
    def generate_recommendation(self, analysis):
        """生成操作建议"""
        if 'summary' not in analysis:
            return 'hold'
            
        score = analysis['summary'].get('technical_score', 50)
        trend = analysis['summary'].get('trend_strength', 'neutral')
        momentum = analysis['summary'].get('momentum_strength', 'neutral')
        risk = analysis['summary'].get('risk_level', 'medium')
        
        if score >= 70 and trend.startswith('bullish') and risk == 'low':
            return 'strong_buy'
        elif score >= 60 and trend.startswith('bullish'):
            return 'buy'
        elif score >= 50 and trend == 'neutral':
            return 'hold'
        elif score < 40 and trend.startswith('bearish') and risk == 'high':
            return 'strong_sell'
        elif score < 50 and trend.startswith('bearish'):
            return 'sell'
        elif momentum == 'overbought':
            return 'reduce_position'
        elif momentum == 'oversold':
            return 'accumulate'
        else:
            return 'hold'

def test_technical_indicators():
    """测试技术指标计算"""
    print("测试技术指标计算模块...")
    print("="*60)
    
    indicator = TechnicalIndicators()
    
    # 测试数据
    test_prices = [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.3, 11.8, 12.0, 11.7,
                   12.2, 12.5, 12.3, 12.8, 13.0, 12.7, 13.2, 13.5, 13.3, 13.8]
    
    test_highs = [p * 1.02 for p in test_prices]
    test_lows = [p * 0.98 for p in test_prices]
    test_volumes = [1000000 * (1 + i*0.1) for i in range(len(test_prices))]
    
    # 测试MA
    ma5 = indicator.calculate_ma(test_prices, 5)
    print(f"MA5: {ma5[-1] if ma5 else 'N/A'}")
    
    # 测试RSI
    rsi = indicator.calculate_rsi(test_prices)
    print(f"RSI: {rsi if rsi else 'N/A'}")
    
    # 测试MACD
    macd = indicator.calculate_macd(test_prices)
    print(f"MACD: {macd}")
    
    # 测试布林带
    boll = indicator.calculate_bollinger(test_prices)
    print(f"布林带: {boll}")
    
    # 测试KDJ
    kdj = indicator.calculate_kdj(test_highs, test_lows, test_prices)
    print(f"KDJ: {kdj}")
    
    # 测试量比
    vol_ratio = indicator.calculate_volume_ratio(test_volumes)
    print(f"量比: {vol_ratio}")
    
    print("\n" + "="*60)
    print("测试完成")
    
    return True

if __name__ == "__main__":
    test_technical_indicators()