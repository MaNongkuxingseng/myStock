"""
myStock 1.1版本 - 技术指标计算模块
提供各种技术指标的计算功能
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.helpers import Timer

logger = logging.getLogger("mystock.analysis.indicators")

class IndicatorType(Enum):
    """技术指标类型枚举"""
    TREND = "trend"          # 趋势指标
    MOMENTUM = "momentum"    # 动量指标
    VOLATILITY = "volatility" # 波动率指标
    VOLUME = "volume"        # 成交量指标
    OSCILLATOR = "oscillator" # 震荡指标

@dataclass
class IndicatorResult:
    """指标计算结果"""
    name: str
    type: IndicatorType
    values: pd.Series
    signals: Optional[pd.Series] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "type": self.type.value,
            "values": self.values.tolist() if len(self.values) > 0 else [],
            "signals": self.signals.tolist() if self.signals is not None and len(self.signals) > 0 else None,
            "metadata": self.metadata
        }

class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        logger.info("技术指标计算器初始化完成")
    
    def calculate_macd(self, close_prices: pd.Series, 
                      fast_period: int = 12,
                      slow_period: int = 26,
                      signal_period: int = 9) -> IndicatorResult:
        """
        计算MACD指标
        
        Args:
            close_prices: 收盘价序列
            fast_period: 快线周期 (默认12)
            slow_period: 慢线周期 (默认26)
            signal_period: 信号线周期 (默认9)
        
        Returns:
            IndicatorResult: MACD指标结果
        """
        with Timer("计算MACD指标"):
            try:
                # 计算EMA
                ema_fast = close_prices.ewm(span=fast_period, adjust=False).mean()
                ema_slow = close_prices.ewm(span=slow_period, adjust=False).mean()
                
                # 计算DIF (差离值)
                dif = ema_fast - ema_slow
                
                # 计算DEA (信号线)
                dea = dif.ewm(span=signal_period, adjust=False).mean()
                
                # 计算MACD柱状图
                macd_bar = (dif - dea) * 2
                
                # 生成信号
                signals = pd.Series(index=close_prices.index, dtype=str)
                for i in range(1, len(dif)):
                    if dif.iloc[i] > dea.iloc[i] and dif.iloc[i-1] <= dea.iloc[i-1]:
                        signals.iloc[i] = "golden_cross"  # 金叉
                    elif dif.iloc[i] < dea.iloc[i] and dif.iloc[i-1] >= dea.iloc[i-1]:
                        signals.iloc[i] = "death_cross"  # 死叉
                    else:
                        signals.iloc[i] = "hold"
                
                metadata = {
                    "fast_period": fast_period,
                    "slow_period": slow_period,
                    "signal_period": signal_period,
                    "dif": dif.tolist(),
                    "dea": dea.tolist(),
                    "macd_bar": macd_bar.tolist()
                }
                
                logger.debug(f"MACD计算完成: 数据长度={len(close_prices)}")
                return IndicatorResult(
                    name="MACD",
                    type=IndicatorType.TREND,
                    values=dif,  # 使用DIF作为主要值
                    signals=signals,
                    metadata=metadata
                )
                
            except Exception as e:
                logger.error(f"MACD计算失败: {e}")
                return IndicatorResult(
                    name="MACD",
                    type=IndicatorType.TREND,
                    values=pd.Series(dtype=float),
                    metadata={"error": str(e)}
                )
    
    def calculate_rsi(self, close_prices: pd.Series, 
                     period: int = 14) -> IndicatorResult:
        """
        计算RSI指标
        
        Args:
            close_prices: 收盘价序列
            period: 计算周期 (默认14)
        
        Returns:
            IndicatorResult: RSI指标结果
        """
        with Timer(f"计算RSI指标 (周期={period})"):
            try:
                # 计算价格变化
                delta = close_prices.diff()
                
                # 分离上涨和下跌
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                
                # 计算平均增益和平均损失
                avg_gain = gain.rolling(window=period).mean()
                avg_loss = loss.rolling(window=period).mean()
                
                # 计算RS
                rs = avg_gain / avg_loss
                
                # 计算RSI
                rsi = 100 - (100 / (1 + rs))
                
                # 生成信号
                signals = pd.Series(index=close_prices.index, dtype=str)
                for i in range(len(rsi)):
                    if pd.isna(rsi.iloc[i]):
                        signals.iloc[i] = "na"
                    elif rsi.iloc[i] > 70:
                        signals.iloc[i] = "overbought"  # 超买
                    elif rsi.iloc[i] < 30:
                        signals.iloc[i] = "oversold"    # 超卖
                    else:
                        signals.iloc[i] = "neutral"
                
                metadata = {
                    "period": period,
                    "avg_gain": avg_gain.tolist(),
                    "avg_loss": avg_loss.tolist(),
                    "rs": rs.tolist()
                }
                
                logger.debug(f"RSI计算完成: 数据长度={len(close_prices)}")
                return IndicatorResult(
                    name=f"RSI_{period}",
                    type=IndicatorType.OSCILLATOR,
                    values=rsi,
                    signals=signals,
                    metadata=metadata
                )
                
            except Exception as e:
                logger.error(f"RSI计算失败: {e}")
                return IndicatorResult(
                    name=f"RSI_{period}",
                    type=IndicatorType.OSCILLATOR,
                    values=pd.Series(dtype=float),
                    metadata={"error": str(e)}
                )
    
    def calculate_kdj(self, high_prices: pd.Series,
                     low_prices: pd.Series,
                     close_prices: pd.Series,
                     n: int = 9, m1: int = 3, m2: int = 3) -> IndicatorResult:
        """
        计算KDJ指标
        
        Args:
            high_prices: 最高价序列
            low_prices: 最低价序列
            close_prices: 收盘价序列
            n: RSV周期 (默认9)
            m1: K值平滑周期 (默认3)
            m2: D值平滑周期 (默认3)
        
        Returns:
            IndicatorResult: KDJ指标结果
        """
        with Timer("计算KDJ指标"):
            try:
                # 计算RSV
                lowest_low = low_prices.rolling(window=n).min()
                highest_high = high_prices.rolling(window=n).max()
                
                rsv = 100 * ((close_prices - lowest_low) / (highest_high - lowest_low))
                rsv = rsv.replace([np.inf, -np.inf], np.nan)
                
                # 计算K值
                k = rsv.ewm(alpha=1/m1, adjust=False).mean()
                
                # 计算D值
                d = k.ewm(alpha=1/m2, adjust=False).mean()
                
                # 计算J值
                j = 3 * k - 2 * d
                
                # 生成信号
                signals = pd.Series(index=close_prices.index, dtype=str)
                for i in range(1, len(k)):
                    if pd.isna(k.iloc[i]) or pd.isna(d.iloc[i]):
                        signals.iloc[i] = "na"
                    elif k.iloc[i] > d.iloc[i] and k.iloc[i-1] <= d.iloc[i-1]:
                        signals.iloc[i] = "golden_cross"  # 金叉
                    elif k.iloc[i] < d.iloc[i] and k.iloc[i-1] >= d.iloc[i-1]:
                        signals.iloc[i] = "death_cross"  # 死叉
                    elif k.iloc[i] > 80:
                        signals.iloc[i] = "overbought"   # 超买
                    elif k.iloc[i] < 20:
                        signals.iloc[i] = "oversold"     # 超卖
                    else:
                        signals.iloc[i] = "hold"
                
                metadata = {
                    "n": n,
                    "m1": m1,
                    "m2": m2,
                    "k": k.tolist(),
                    "d": d.tolist(),
                    "j": j.tolist(),
                    "rsv": rsv.tolist()
                }
                
                logger.debug(f"KDJ计算完成: 数据长度={len(close_prices)}")
                return IndicatorResult(
                    name="KDJ",
                    type=IndicatorType.OSCILLATOR,
                    values=k,  # 使用K值作为主要值
                    signals=signals,
                    metadata=metadata
                )
                
            except Exception as e:
                logger.error(f"KDJ计算失败: {e}")
                return IndicatorResult(
                    name="KDJ",
                    type=IndicatorType.OSCILLATOR,
                    values=pd.Series(dtype=float),
                    metadata={"error": str(e)}
                )
    
    def calculate_bollinger_bands(self, close_prices: pd.Series,
                                 period: int = 20,
                                 std_dev: float = 2.0) -> IndicatorResult:
        """
        计算布林带指标
        
        Args:
            close_prices: 收盘价序列
            period: 移动平均周期 (默认20)
            std_dev: 标准差倍数 (默认2.0)
        
        Returns:
            IndicatorResult: 布林带指标结果
        """
        with Timer("计算布林带指标"):
            try:
                # 计算中轨 (移动平均线)
                middle_band = close_prices.rolling(window=period).mean()
                
                # 计算标准差
                std = close_prices.rolling(window=period).std()
                
                # 计算上轨和下轨
                upper_band = middle_band + (std * std_dev)
                lower_band = middle_band - (std * std_dev)
                
                # 计算布林带宽度和位置
                band_width = (upper_band - lower_band) / middle_band
                band_position = (close_prices - lower_band) / (upper_band - lower_band)
                
                # 生成信号
                signals = pd.Series(index=close_prices.index, dtype=str)
                for i in range(len(close_prices)):
                    if pd.isna(upper_band.iloc[i]) or pd.isna(lower_band.iloc[i]):
                        signals.iloc[i] = "na"
                    elif close_prices.iloc[i] > upper_band.iloc[i]:
                        signals.iloc[i] = "upper_breakout"  # 突破上轨
                    elif close_prices.iloc[i] < lower_band.iloc[i]:
                        signals.iloc[i] = "lower_breakout"  # 突破下轨
                    elif band_width.iloc[i] > 0.1:  # 带宽较大，波动剧烈
                        signals.iloc[i] = "high_volatility"
                    elif band_width.iloc[i] < 0.05:  # 带宽较小，波动平静
                        signals.iloc[i] = "low_volatility"
                    else:
                        signals.iloc[i] = "normal"
                
                metadata = {
                    "period": period,
                    "std_dev": std_dev,
                    "upper_band": upper_band.tolist(),
                    "middle_band": middle_band.tolist(),
                    "lower_band": lower_band.tolist(),
                    "band_width": band_width.tolist(),
                    "band_position": band_position.tolist()
                }
                
                logger.debug(f"布林带计算完成: 数据长度={len(close_prices)}")
                return IndicatorResult(
                    name="Bollinger_Bands",
                    type=IndicatorType.VOLATILITY,
                    values=band_width,  # 使用带宽作为主要值
                    signals=signals,
                    metadata=metadata
                )
                
            except Exception as e:
                logger.error(f"布林带计算失败: {e}")
                return IndicatorResult(
                    name="Bollinger_Bands",
                    type=IndicatorType.VOLATILITY,
                    values=pd.Series(dtype=float),
                    metadata={"error": str(e)}
                )
    
    def calculate_cci(self, high_prices: pd.Series,
                     low_prices: pd.Series,
                     close_prices: pd.Series,
                     period: int = 20) -> IndicatorResult:
        """
        计算CCI指标
        
        Args:
            high_prices: 最高价序列
            low_prices: 最低价序列
            close_prices: 收盘价序列
            period: 计算周期 (默认20)
        
        Returns:
            IndicatorResult: CCI指标结果
        """
        with Timer("计算CCI指标"):
            try:
                # 计算典型价格
                typical_price = (high_prices + low_prices + close_prices) / 3
                
                # 计算简单移动平均
                sma = typical_price.rolling(window=period).mean()
                
                # 计算平均偏差
                mean_deviation = typical_price.rolling(window=period).apply(
                    lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
                )
                
                # 计算CCI
                cci = (typical_price - sma) / (0.015 * mean_deviation)
                
                # 生成信号
                signals = pd.Series(index=close_prices.index, dtype=str)
                for i in range(len(cci)):
                    if pd.isna(cci.iloc[i]):
                        signals.iloc[i] = "na"
                    elif cci.iloc[i] > 100:
                        signals.iloc[i] = "overbought"  # 超买
                    elif cci.iloc[i] < -100:
                        signals.iloc[i] = "oversold"    # 超卖
                    elif cci.iloc[i] > 0:
                        signals.iloc[i] = "bullish"     # 看涨
                    else:
                        signals.iloc[i] = "bearish"     # 看跌
                
                metadata = {
                    "period": period,
                    "typical_price": typical_price.tolist(),
                    "sma": sma.tolist(),
                    "mean_deviation": mean_deviation.tolist()
                }
                
                logger.debug(f"CCI计算完成: 数据长度={len(close_prices)}")
                return IndicatorResult(
                    name="CCI",
                    type=IndicatorType.OSCILLATOR,
                    values=cci,
                    signals=signals,
                    metadata=metadata
                )
                
            except Exception as e:
                logger.error(f"CCI计算失败: {e}")
                return IndicatorResult(
                    name="CCI",
                    type=IndicatorType.OSCILLATOR,
                    values=pd.Series(dtype=float),
                    metadata={"error": str(e)}
                )
    
    def calculate_atr(self, high_prices: pd.Series,
                     low_prices: pd.Series,
                     close_prices: pd.Series,
                     period: int = 14) -> IndicatorResult:
        """
        计算ATR指标
        
        Args:
            high_prices: 最高价序列
            low_prices: 最低价序列
            close_prices: 收盘价序列
            period: 计算周期 (默认14)
        
        Returns:
            IndicatorResult: ATR指标结果
        """
        with Timer("计算ATR指标"):
            try:
                # 计算真实波幅
                high_low = high_prices - low_prices
                high_close = np.abs(high_prices - close_prices.shift(1))
                low_close = np.abs(low_prices - close_prices.shift(1))
                
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                
                # 计算ATR
                atr = true_range.rolling(window=period).mean()
                
                # 计算ATR百分比
                atr_percent = atr / close_prices * 100
                
                # 生成信号
                signals = pd.Series(index=close_prices.index, dtype=str)
                atr_mean = atr_percent.mean()
                for i in range(len(atr_percent)):
                    if pd.isna(atr_percent.iloc[i]):
                        signals.iloc[i] = "na"
                    elif atr_percent.iloc[i] > atr_mean * 1.5:
                        signals.iloc[i] = "high_volatility"  # 高波动
                    elif atr_percent.iloc[i] < atr_mean * 0.5:
                        signals.iloc[i] = "low_volatility"   # 低波动
                    else:
                        signals.iloc[i] = "normal"
                
                metadata = {
                    "period": period,
                    "true_range": true_range.tolist(),
                    "atr": atr.tolist(),
                    "atr_percent": atr_percent.tolist(),
                    "mean_atr_percent": atr_mean
                }
                
                logger.debug(f"ATR计算完成: 数据长度={len(close_prices)}")
                return IndicatorResult(
                    name="ATR",
                    type=IndicatorType.VOLATILITY,
                    values=atr_percent,  # 使用ATR百分比作为主要值
                    signals=signals,
                    metadata=metadata
                )
                
            except Exception as e:
                logger.error(f"ATR计算失败: {e}")
                return IndicatorResult(
                    name="ATR",
                    type=IndicatorType.VOLATILITY,
                    values=pd.Series(dtype=float),
                    metadata={"error": str(e)}
                )
    
    def calculate_williams_r(self, high_prices: pd.Series,
                           low_prices: pd.Series,
                           close_prices: pd.Series,
                           period: int = 14) -> IndicatorResult:
        """
        计算威廉指标
        
        Args:
            high_prices: 最高价序列
            low_prices: 最低价序列
            close_prices: 收盘价序列
            period: 计算周期 (默认14)
        
        Returns:
            IndicatorResult: 威廉指标结果
        """
        with Timer("计算威廉指标"):
            try:
                # 计算最高价和最低价
                highest_high = high_prices.rolling(window=period).max()
                lowest_low = low_prices.rolling(window=period).min()
                
                # 计算威廉R值
                williams_r = -100 * ((highest_high - close_prices) / (highest_high - lowest_low))
                williams_r = williams_r.replace([np.inf, -np.inf], np.nan)
                
                # 生成信号
                signals = pd.Series(index=close_prices.index, dtype=str)
                for i in range(len(williams_r)):
                    if pd.isna(williams_r.iloc[i]):
                        signals.iloc[i] = "na"
                    elif williams_r.iloc[i] > -20:
                        signals.iloc[i] = "overbought"  # 超买
                    elif williams_r.iloc[i] < -80:
                        signals.iloc[i] = "oversold"    # 超卖
                    else:
                        signals.iloc[i] = "neutral"
                
                metadata = {
                    "period": period,
                    "highest_high": highest_high.tolist(),
                    "lowest_low": lowest_low.tolist(),
                    "williams_r": williams_r.tolist()
                }
                
                logger.debug(f"威廉指标计算完成: 数据长度={len(close_prices)}")
                return IndicatorResult(
                    name="Williams_R",
                    type=IndicatorType.OSCILLATOR,
                    values=williams_r,
                    signals=signals,
                    metadata=metadata
                )
                
            except Exception as e:
                logger.error(f"威廉指标计算失败: {e}")
                return IndicatorResult(
                    name="Williams_R",
                    type=IndicatorType.OSCILLATOR,
                    values=pd.Series(dtype=float),
                    metadata={"error": str(e)}
                )
    
    def calculate_all_indicators(self, stock_data: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """
        计算所有技术指标
        
        Args:
            stock_data: 股票数据DataFrame，需要包含以下列:
                - 'close': 收盘价
                - 'high': 最高价
                - 'low': 最低价
                - 'volume': 成交量 (可选)
        
        Returns:
            Dict[str, IndicatorResult]: 所有指标计算结果
        """
        with Timer("计算所有技术指标"):
            results = {}
            
            # 提取数据序列
            close = stock_data['close']
            high = stock_data['high']
            low = stock_data['low']
            
            # 计算各个指标
            results['macd'] = self.calculate_macd(close)
            results['rsi_14'] = self.calculate_rsi(close, period=14)
            results['rsi_6'] = self.calculate_rsi(close, period=6)
            results['rsi_24'] = self.calculate_rsi(close, period=24)
            results['kdj'] = self.calculate_kdj(high, low, close)
            results['bollinger'] = self.calculate_bollinger_bands(close)
            results['cci'] = self.calculate_cci(high, low, close)
            results['atr'] = self.calculate_atr(high, low, close)
            results['williams_r'] = self.calculate_williams_r(high, low, close)
            
            logger.info(f"所有技术指标计算完成: 共{len(results)}个指标")
            return results
    
    def generate_indicator_report(self, indicator_results: Dict[str, IndicatorResult]) -> Dict[str, Any]:
        """
        生成指标分析报告
        
        Args:
            indicator_results: 指标计算结果
        
        Returns:
            Dict[str, Any]: 分析报告
        """
        with Timer("生成指标分析报告"):
            report = {
                "timestamp": pd.Timestamp.now().isoformat(),
                "total_indicators": len(indicator_results),
                "indicators": {},
                "summary": {
                    "buy_signals": 0,
                    "sell_signals": 0,
                    "neutral_signals": 0,
                    "strong_indicators": [],
                    "weak_indicators": []
                }
            }
            
            # 分析每个指标
            for name, result in indicator_results.items():
                if result.values.empty:
                    continue
                
                # 获取最新信号
                latest_signal = result.signals.iloc[-1] if result.signals is not None else "unknown"
                latest_value = result.values.iloc[-1] if not result.values.empty else None
                
                # 统计信号
                if "buy" in str(latest_signal).lower() or "golden" in str(latest_signal).lower():
                    report["summary"]["buy_signals"] += 1
                    signal_strength = "buy"
                elif "sell" in str(latest_signal).lower() or "death" in str(latest_signal).lower():
                    report["summary"]["sell_signals"] += 1
                    signal_strength = "sell"
                else:
                    report["summary"]["neutral_signals"] += 1
                    signal_strength = "neutral"
                
                # 记录指标信息
                report["indicators"][name] = {
                    "type": result.type.value,
                    "latest_value": float(latest_value) if latest_value is not None else None,
                    "latest_signal": latest_signal,
                    "signal_strength": signal_strength,
                    "metadata_keys": list(result.metadata.keys()) if result.metadata else []
                }
            
            # 判断整体趋势
            buy_ratio = report["summary"]["buy_signals"] / max(report["total_indicators"], 1)
            sell_ratio = report["summary"]["sell_signals"] / max(report["total_indicators"], 1)
            
            if buy_ratio > 0.6:
                overall_trend = "strong_bullish"
            elif buy_ratio > 0.4:
                overall_trend = "bullish"
            elif sell_ratio > 0.6:
                overall_trend = "strong_bearish"
            elif sell_ratio > 0.4:
                overall_trend = "bearish"
            else:
                overall_trend = "neutral"
            
            report["summary"]["overall_trend"] = overall_trend
            report["summary"]["buy_ratio"] = buy_ratio
            report["summary"]["sell_ratio"] = sell_ratio
            
            logger.info(f"指标分析报告生成完成: 整体趋势={overall_trend}")
            return report

# 全局技术指标计算器实例
technical_indicators = TechnicalIndicators()

def init_technical_indicators():
    """初始化技术指标计算器"""
    logger.info("技术指标计算器初始化完成")
    return technical_indicators

if __name__ == "__main__":
    # 测试技术指标模块
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    print("=== 技术指标模块测试 ===")
    
    # 初始化
    indicators = init_technical_indicators()
    
    # 创建测试数据
    dates = pd.date_range(start='2026-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    test_data = pd.DataFrame({
        'date': dates,
        'open': 10 + np.random.randn(100).cumsum() * 0.1,
        'high': 10.5 + np.random.randn(100).cumsum() * 0.1,
        'low': 9.5 + np.random.randn(100).cumsum() * 0.1,
        'close': 10 + np.random.randn(100).cumsum() * 0.1,
        'volume': 1000000 + np.random.randn(100).cumsum() * 10000
    })
    test_data.set_index('date', inplace=True)
    
    print(f"测试数据形状: {test_data.shape}")
    print(f"数据列: {list(test_data.columns)}")
    
    # 测试单个指标
    print("\n测试MACD指标:")
    macd_result = indicators.calculate_macd(test_data['close'])
    print(f"  MACD计算完成: 数据长度={len(macd_result.values)}")
    print(f"  最新值: {macd_result.values.iloc[-1] if not macd_result.values.empty else 'N/A'}")
    print(f"  最新信号: {macd_result.signals.iloc[-1] if macd_result.signals is not None else 'N/A'}")
    
    # 测试RSI指标
    print("\n测试RSI指标:")
    rsi_result = indicators.calculate_rsi(test_data['close'], period=14)
    print(f"  RSI计算完成: 数据长度={len(rsi_result.values)}")
    print(f"  最新值: {rsi_result.values.iloc[-1] if not rsi_result.values.empty else 'N/A'}")
    print(f"  最新信号: {rsi_result.signals.iloc[-1] if rsi_result.signals is not None else 'N/A'}")
    
    # 测试所有指标
    print("\n测试所有指标计算:")
    all_results = indicators.calculate_all_indicators(test_data)
    print(f"  共计算{len(all_results)}个指标:")
    for name, result in all_results.items():
        print(f"    {name}: {result.type.value} - 数据长度={len(result.values)}")
    
    # 测试分析报告
    print("\n测试指标分析报告:")
    report = indicators.generate_indicator_report(all_results)
    print(f"  整体趋势: {report['summary']['overall_trend']}")
    print(f"  买入信号: {report['summary']['buy_signals']}")
    print(f"  卖出信号: {report['summary']['sell_signals']}")
    print(f"  中性信号: {report['summary']['neutral_signals']}")
    
    print("\n" + "=" * 40)