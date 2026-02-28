#!/usr/bin/env python3
"""
技术指标计算模块 - 优化版本
包含高准确率技术指标计算
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import talib
from dataclasses import dataclass
from datetime import datetime

@dataclass
class IndicatorConfig:
    """指标配置"""
    # MACD配置
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # RSI配置
    rsi_period: int = 14
    rsi_periods: List[int] = None  # 多周期RSI
    
    # KDJ配置
    kdj_period: int = 9
    kdj_slowk: int = 3
    kdj_slowd: int = 3
    
    # 布林带配置
    bollinger_period: int = 20
    bollinger_std: float = 2.0
    
    # CCI配置
    cci_period: int = 20
    
    # ATR配置
    atr_period: int = 14
    
    # 威廉指标配置
    williams_period: int = 14
    
    def __post_init__(self):
        if self.rsi_periods is None:
            self.rsi_periods = [6, 12, 24]

class TechnicalIndicators:
    """技术指标计算类"""
    
    def __init__(self, config: Optional[IndicatorConfig] = None):
        self.config = config or IndicatorConfig()
    
    def calculate_all_indicators(self, 
                                prices: pd.DataFrame,
                                volumes: pd.Series) -> Dict:
        """
        计算所有技术指标
        
        Args:
            prices: 价格数据DataFrame，包含open, high, low, close
            volumes: 成交量数据Series
        
        Returns:
            包含所有技术指标的字典
        """
        results = {}
        
        # 基本价格数据
        close_prices = prices['close'].values
        high_prices = prices['high'].values
        low_prices = prices['low'].values
        
        # 1. MACD指标
        results.update(self.calculate_macd(close_prices))
        
        # 2. RSI指标
        results.update(self.calculate_rsi(close_prices))
        
        # 3. KDJ指标
        results.update(self.calculate_kdj(high_prices, low_prices, close_prices))
        
        # 4. 布林带指标
        results.update(self.calculate_bollinger(close_prices))
        
        # 5. CCI指标
        results.update(self.calculate_cci(high_prices, low_prices, close_prices))
        
        # 6. ATR指标
        results.update(self.calculate_atr(high_prices, low_prices, close_prices))
        
        # 7. 威廉指标
        results.update(self.calculate_williams(high_prices, low_prices, close_prices))
        
        # 8. 成交量指标
        results.update(self.calculate_volume_indicators(volumes.values))
        
        # 9. 均线系统
        results.update(self.calculate_moving_averages(close_prices))
        
        return results
    
    def calculate_macd(self, close_prices: np.ndarray) -> Dict:
        """计算MACD指标"""
        try:
            macd, signal, histogram = talib.MACD(
                close_prices,
                fastperiod=self.config.macd_fast,
                slowperiod=self.config.macd_slow,
                signalperiod=self.config.macd_signal
            )
            
            # 计算金叉死叉信号
            macd_golden_fork = self._detect_golden_fork(macd, signal)
            macd_dead_fork = self._detect_dead_fork(macd, signal)
            
            return {
                'macd': macd[-1] if not np.isnan(macd[-1]) else 0,
                'macd_signal': signal[-1] if not np.isnan(signal[-1]) else 0,
                'macd_histogram': histogram[-1] if not np.isnan(histogram[-1]) else 0,
                'macd_golden_fork': int(macd_golden_fork),
                'macd_dead_fork': int(macd_dead_fork)
            }
        except Exception as e:
            print(f"MACD计算错误: {e}")
            return self._get_default_macd()
    
    def calculate_rsi(self, close_prices: np.ndarray) -> Dict:
        """计算RSI指标（多周期）"""
        results = {}
        
        for period in self.config.rsi_periods:
            try:
                rsi = talib.RSI(close_prices, timeperiod=period)
                current_rsi = rsi[-1] if not np.isnan(rsi[-1]) else 50
                
                results[f'rsi_{period}'] = float(current_rsi)
                
                # 主RSI周期（默认14）
                if period == self.config.rsi_period:
                    results['rsi'] = float(current_rsi)
                    results['rsi_overbought'] = int(current_rsi > 70)
                    results['rsi_oversold'] = int(current_rsi < 30)
            except Exception as e:
                print(f"RSI计算错误(周期{period}): {e}")
                results[f'rsi_{period}'] = 50.0
        
        return results
    
    def calculate_kdj(self, 
                     high_prices: np.ndarray,
                     low_prices: np.ndarray,
                     close_prices: np.ndarray) -> Dict:
        """计算KDJ指标"""
        try:
            # 使用talib的STOCH函数计算KDJ
            slowk, slowd = talib.STOCH(
                high_prices,
                low_prices,
                close_prices,
                fastk_period=self.config.kdj_period,
                slowk_period=self.config.kdj_slowk,
                slowk_matype=0,
                slowd_period=self.config.kdj_slowd,
                slowd_matype=0
            )
            
            # 计算J值: J = 3K - 2D
            slowj = 3 * slowk - 2 * slowd
            
            current_k = slowk[-1] if not np.isnan(slowk[-1]) else 50
            current_d = slowd[-1] if not np.isnan(slowd[-1]) else 50
            current_j = slowj[-1] if not np.isnan(slowj[-1]) else 50
            
            # 计算金叉死叉信号
            kdj_golden_fork = self._detect_golden_fork(slowk, slowd)
            kdj_dead_fork = self._detect_dead_fork(slowk, slowd)
            
            return {
                'kdjk': float(current_k),
                'kdjd': float(current_d),
                'kdjj': float(current_j),
                'kdj_golden_fork': int(kdj_golden_fork),
                'kdj_dead_fork': int(kdj_dead_fork),
                'kdj_overbought': int(current_k > 80),
                'kdj_oversold': int(current_k < 20)
            }
        except Exception as e:
            print(f"KDJ计算错误: {e}")
            return self._get_default_kdj()
    
    def calculate_bollinger(self, close_prices: np.ndarray) -> Dict:
        """计算布林带指标"""
        try:
            upper, middle, lower = talib.BBANDS(
                close_prices,
                timeperiod=self.config.bollinger_period,
                nbdevup=self.config.bollinger_std,
                nbdevdn=self.config.bollinger_std,
                matype=0
            )
            
            current_close = close_prices[-1]
            current_upper = upper[-1] if not np.isnan(upper[-1]) else current_close * 1.1
            current_middle = middle[-1] if not np.isnan(middle[-1]) else current_close
            current_lower = lower[-1] if not np.isnan(lower[-1]) else current_close * 0.9
            
            # 计算布林带宽度和位置
            boll_width = (current_upper - current_lower) / current_middle if current_middle > 0 else 0
            boll_position = (current_close - current_lower) / (current_upper - current_lower) if (current_upper - current_lower) > 0 else 0.5
            
            # 判断突破信号
            break_upper = int(current_close > current_upper)
            break_lower = int(current_close < current_lower)
            
            return {
                'boll_upper': float(current_upper),
                'boll_middle': float(current_middle),
                'boll_lower': float(current_lower),
                'boll_width': float(boll_width),
                'boll_position': float(boll_position),
                'break_boll_upper': break_upper,
                'break_boll_lower': break_lower
            }
        except Exception as e:
            print(f"布林带计算错误: {e}")
            return self._get_default_bollinger(close_prices[-1])
    
    def calculate_cci(self,
                     high_prices: np.ndarray,
                     low_prices: np.ndarray,
                     close_prices: np.ndarray) -> Dict:
        """计算CCI顺势指标"""
        try:
            cci = talib.CCI(
                high_prices,
                low_prices,
                close_prices,
                timeperiod=self.config.cci_period
            )
            
            current_cci = cci[-1] if not np.isnan(cci[-1]) else 0
            
            # CCI信号判断
            cci_overbought = int(current_cci > 100)
            cci_oversold = int(current_cci < -100)
            cci_trend_up = int(current_cci > 0)
            cci_trend_down = int(current_cci < 0)
            
            return {
                'cci': float(current_cci),
                'cci_overbought': cci_overbought,
                'cci_oversold': cci_oversold,
                'cci_trend_up': cci_trend_up,
                'cci_trend_down': cci_trend_down
            }
        except Exception as e:
            print(f"CCI计算错误: {e}")
            return {'cci': 0.0, 'cci_overbought': 0, 'cci_oversold': 0, 'cci_trend_up': 0, 'cci_trend_down': 0}
    
    def calculate_atr(self,
                     high_prices: np.ndarray,
                     low_prices: np.ndarray,
                     close_prices: np.ndarray) -> Dict:
        """计算ATR平均真实波幅"""
        try:
            atr = talib.ATR(
                high_prices,
                low_prices,
                close_prices,
                timeperiod=self.config.atr_period
            )
            
            current_atr = atr[-1] if not np.isnan(atr[-1]) else 0
            atr_percent = current_atr / close_prices[-1] * 100 if close_prices[-1] > 0 else 0
            
            return {
                'atr': float(current_atr),
                'atr_percent': float(atr_percent),
                'high_volatility': int(atr_percent > 3.0)  # 高波动率标志
            }
        except Exception as e:
            print(f"ATR计算错误: {e}")
            return {'atr': 0.0, 'atr_percent': 0.0, 'high_volatility': 0}
    
    def calculate_williams(self,
                          high_prices: np.ndarray,
                          low_prices: np.ndarray,
                          close_prices: np.ndarray) -> Dict:
        """计算威廉指标"""
        try:
            williams = talib.WILLR(
                high_prices,
                low_prices,
                close_prices,
                timeperiod=self.config.williams_period
            )
            
            current_williams = williams[-1] if not np.isnan(williams[-1]) else -50
            
            # 威廉指标信号判断（注意：威廉指标是反向的）
            williams_overbought = int(current_williams > -20)  # 大于-20为超买
            williams_oversold = int(current_williams < -80)    # 小于-80为超卖
            
            return {
                'williams_r': float(current_williams),
                'williams_overbought': williams_overbought,
                'williams_oversold': williams_oversold
            }
        except Exception as e:
            print(f"威廉指标计算错误: {e}")
            return {'williams_r': -50.0, 'williams_overbought': 0, 'williams_oversold': 0}
    
    def calculate_volume_indicators(self, volumes: np.ndarray) -> Dict:
        """计算成交量指标"""
        try:
            if len(volumes) < 5:
                return self._get_default_volume()
            
            # 成交量均线
            volume_ma5 = np.mean(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
            volume_ma10 = np.mean(volumes[-10:]) if len(volumes) >= 10 else volumes[-1]
            volume_ma20 = np.mean(volumes[-20:]) if len(volumes) >= 20 else volumes[-1]
            
            # 量比（当前成交量/5日均量）
            volume_ratio = volumes[-1] / volume_ma5 if volume_ma5 > 0 else 1.0
            
            # 成交量变化率
            if len(volumes) >= 2:
                volume_change = (volumes[-1] - volumes[-2]) / volumes[-2] * 100 if volumes[-2] > 0 else 0
            else:
                volume_change = 0
            
            return {
                'volume': float(volumes[-1]),
                'volume_ma5': float(volume_ma5),
                'volume_ma10': float(volume_ma10),
                'volume_ma20': float(volume_ma20),
                'volume_ratio': float(volume_ratio),
                'volume_change': float(volume_change),
                'high_volume': int(volume_ratio > 2.0)  # 高量比标志
            }
        except Exception as e:
            print(f"成交量指标计算错误: {e}")
            return self._get_default_volume()
    
    def calculate_moving_averages(self, close_prices: np.ndarray) -> Dict:
        """计算均线系统"""
        try:
            ma_periods = [5, 10, 20, 30, 60, 120, 250]
            results = {}
            
            for period in ma_periods:
                if len(close_prices) >= period:
                    ma = talib.SMA(close_prices, timeperiod=period)
                    current_ma = ma[-1] if not np.isnan(ma[-1]) else close_prices[-1]
                else:
                    current_ma = close_prices[-1]
                
                results[f'ma_{period}'] = float(current_ma)
            
            # 均线排列判断
            if len(close_prices) >= 250:
                ma5 = results.get('ma_5', close_prices[-1])
                ma10 = results.get('ma_10', close_prices[-1])
                ma20 = results.get('ma_20', close_prices[-1])
                ma60 = results.get('ma_60', close_prices[-1])
                
                # 多头排列：短周期均线在上，长周期均线在下
                ma_bullish = int(ma5 > ma10 > ma20 > ma60)
                # 空头排列：短周期均线在下，长周期均线在上
                ma_bearish = int(ma5 < ma10 < ma20 < ma60)
                
                results['ma_bullish'] = ma_bullish
                results['ma_bearish'] = ma_bearish
            
            return results
        except Exception as e:
            print(f"均线计算错误: {e}")
            return self._get_default_moving_averages(close_prices[-1])
    
    def _detect_golden_fork(self, fast_line: np.ndarray, slow_line: np.ndarray) -> bool:
        """检测金叉"""
        if len(fast_line) < 2 or len(slow_line) < 2:
            return False
        
        # 当前快线在慢线之上，且上一时刻快线在慢线之下
        current_fast = fast_line[-1]
        current_slow = slow_line[-1]
        prev_fast = fast_line[-2]
        prev_slow = slow_line[-2]
        
        return (current_fast > current_slow) and (prev_fast <= prev_slow)
    
    def _detect_dead_fork(self, fast_line: np.ndarray, slow_line: np.ndarray) -> bool:
        """检测死叉"""
        if len(fast_line) < 2 or len(slow_line) < 2:
            return False
        
        # 当前快线在慢线之下，且上一时刻快线在慢线之上
        current_fast = fast_line[-1]
        current_slow = slow_line[-1]
        prev_fast = fast_line[-2]
        prev_slow = slow_line[-2]
        
        return (current_fast < current_slow) and (prev_fast >= prev_slow)
    
    def _get_default_macd(self) -> Dict:
        """获取默认MACD值"""
        return {
            'macd': 0.0,
            'macd_signal': 0.0,
            'macd_histogram': 0.0,
            'macd_golden_fork': 0,
            'macd_dead_fork': 0
        }
    
    def _get_default_kdj(self) -> Dict:
        """获取默认KDJ值"""
        return {
            'kdjk': 50.0,
            'kdjd': 50.0,
            'kdjj': 50.0,
            'kdj_golden_fork': 0,
            'kdj_dead_fork': 0,
            'kdj_overbought': 0,
            'kdj_oversold': 0
        }
    
    def _get_default_bollinger(self, current_price: float) -> Dict:
        """获取默认布林带值"""
        return {
            'boll_upper': current_price * 1.1,
            'boll_middle': current_price,
            'boll_lower': current_price * 0.9,
            'boll_width': 0.2,
            'boll_position': 0.5,
            'break_boll_upper': 0,
            'break_boll_lower': 0
        }
    
    def _get_default_volume(self) -> Dict:
        """获取默认成交量值"""
        return {
            'volume': 0.0,
            'volume_ma5': 0.0,
            'volume_ma10': 0.0,
            'volume_ma20': 0.0,
            'volume_ratio': 1.0,
            'volume_change': 0.0,
            'high_volume': 0
        }
    
    def _get_default_moving_averages(self, current_price: float) -> Dict:
        """获取默认均线值"""
        ma_periods = [5, 10, 20, 30, 60, 120, 250]
        results = {}
        
        for period in ma_periods:
            results[f'ma_{period}'] = float(current_price)
        
        results['ma_bullish'] = 0
        results['ma_bearish'] = 0
        
        return results


# 使用示例
if __name__ == "__main__":
    # 创建配置
    config = IndicatorConfig(
        macd_fast=8,      # 优化后的快速EMA
        macd_slow=17,     # 优化后的慢速EMA
        macd_signal=9,
        rsi_periods=[6, 12, 24, 14],  # 多周期RSI
        kdj_period=14,    # 优化后的KDJ周期
        bollinger_period=20,
        bollinger_std=2.0,
        cci_period=20,
        atr_period=14,
        williams_period=14
    )
    
    # 创建指标计算器
    calculator = TechnicalIndicators(config)
    
    # 模拟价格数据
    np.random.seed(42)
    n_days = 100
    prices = pd.DataFrame({
        'open': np.random.randn(n_days).cumsum() + 100,
        'high': np.random.randn(n_days).cumsum() + 102,
        'low': np.random.randn(n_days).cumsum() + 98,
        'close': np.random.randn(n_days).cumsum() + 100
    })
    
    volumes = pd.Series(np.random.randint(1000000, 10000000, n_days))
    
    # 计算所有指标
    print("计算技术指标...")
    indicators = calculator.calculate_all_indicators(prices, volumes)
    
    print(f"\n计算完成，共 {len(indicators)} 个指标")
    print("\n关键指标值:")
    print(f"  MACD: {indicators.get('macd', 0):.4f}")
    print(f"  RSI(14): {indicators.get('rsi', 0):.2f}")
    print(f"  KDJ K值: {indicators.get('kdjk', 0):.2f}")
    print(f"  布林带上轨: {indicators.get('boll_upper', 0):.2f}")
    print(f"  CCI: {indicators.get('cci', 0):.2f}")
    print(f"  ATR: {indicators.get('atr', 0):.4f}")
    print(f"  威廉指标: {indicators.get('williams_r', 0):.2f}")
    print(f"  量比: {indicators.get('volume_ratio', 0):.2f}")
    
    print("\n交易信号:")
    print(f"  MACD金叉: {indicators.get('macd_golden_fork', 0)}")
    print(f"  KDJ金叉: {indicators.get('kdj_golden_fork', 0)}")
    print(f"  RSI超买: {indicators.get('rsi_overbought', 0)}")
    print(f"  布林带突破上轨: {indicators.get('break_boll_upper', 0)}")
    print(f"  CCI超买: {indicators.get('cci_overbought', 0)}")