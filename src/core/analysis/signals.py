"""
myStock 1.1版本 - 信号生成模块
基于技术指标生成交易信号
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..utils.helpers import Timer, format_time
from .indicators import IndicatorResult, technical_indicators

logger = logging.getLogger("mystock.analysis.signals")

class SignalType(Enum):
    """信号类型枚举"""
    STRONG_BUY = "strong_buy"      # 强烈买入
    BUY = "buy"                    # 买入
    NEUTRAL = "neutral"            # 中性/持有
    SELL = "sell"                  # 卖出
    STRONG_SELL = "strong_sell"    # 强烈卖出

class SignalStrength(Enum):
    """信号强度枚举"""
    WEAK = "weak"      # 弱信号
    MODERATE = "moderate"  # 中等信号
    STRONG = "strong"  # 强信号

@dataclass
class TradingSignal:
    """交易信号"""
    signal_type: SignalType
    strength: SignalStrength
    confidence: float  # 置信度 0-1
    indicators: List[str]  # 产生信号的指标列表
    reasons: List[str]  # 信号产生原因
    timestamp: datetime
    price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "signal": self.signal_type.value,
            "strength": self.strength.value,
            "confidence": round(self.confidence, 2),
            "indicators": self.indicators,
            "reasons": self.reasons,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "target_price": self.target_price,
            "stop_loss": self.stop_loss
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.signal_type.value.upper()} ({self.strength.value}) - 置信度: {self.confidence:.0%}"

class SignalGenerator:
    """信号生成器"""
    
    def __init__(self):
        self.signal_rules = self._initialize_rules()
        logger.info("信号生成器初始化完成")
    
    def _initialize_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化信号规则"""
        return {
            "macd_golden_cross": {
                "type": SignalType.BUY,
                "strength": SignalStrength.MODERATE,
                "confidence": 0.6,
                "description": "MACD金叉 - 短期看涨"
            },
            "macd_death_cross": {
                "type": SignalType.SELL,
                "strength": SignalStrength.MODERATE,
                "confidence": 0.6,
                "description": "MACD死叉 - 短期看跌"
            },
            "rsi_oversold": {
                "type": SignalType.BUY,
                "strength": SignalStrength.STRONG,
                "confidence": 0.7,
                "description": "RSI超卖 - 反弹机会"
            },
            "rsi_overbought": {
                "type": SignalType.SELL,
                "strength": SignalStrength.STRONG,
                "confidence": 0.7,
                "description": "RSI超买 - 回调风险"
            },
            "kdj_golden_cross": {
                "type": SignalType.BUY,
                "strength": SignalStrength.WEAK,
                "confidence": 0.5,
                "description": "KDJ金叉 - 短期看涨"
            },
            "kdj_death_cross": {
                "type": SignalType.SELL,
                "strength": SignalStrength.WEAK,
                "confidence": 0.5,
                "description": "KDJ死叉 - 短期看跌"
            },
            "bollinger_upper_breakout": {
                "type": SignalType.SELL,
                "strength": SignalStrength.MODERATE,
                "confidence": 0.65,
                "description": "突破布林带上轨 - 超买回调"
            },
            "bollinger_lower_breakout": {
                "type": SignalType.BUY,
                "strength": SignalStrength.MODERATE,
                "confidence": 0.65,
                "description": "突破布林带下轨 - 超卖反弹"
            },
            "cci_overbought": {
                "type": SignalType.SELL,
                "strength": SignalStrength.MODERATE,
                "confidence": 0.6,
                "description": "CCI超买 - 趋势反转"
            },
            "cci_oversold": {
                "type": SignalType.BUY,
                "strength": SignalStrength.MODERATE,
                "confidence": 0.6,
                "description": "CCI超卖 - 趋势反转"
            },
            "williams_oversold": {
                "type": SignalType.BUY,
                "strength": SignalStrength.STRONG,
                "confidence": 0.75,
                "description": "威廉指标超卖 - 强烈买入信号"
            },
            "williams_overbought": {
                "type": SignalType.SELL,
                "strength": SignalStrength.STRONG,
                "confidence": 0.75,
                "description": "威廉指标超买 - 强烈卖出信号"
            }
        }
    
    def analyze_indicators(self, indicator_results: Dict[str, IndicatorResult], 
                          current_price: Optional[float] = None) -> List[TradingSignal]:
        """
        分析技术指标并生成交易信号
        
        Args:
            indicator_results: 技术指标计算结果
            current_price: 当前价格（可选）
        
        Returns:
            List[TradingSignal]: 交易信号列表
        """
        with Timer("分析技术指标生成信号"):
            signals = []
            
            # 分析每个指标的最新信号
            for indicator_name, result in indicator_results.items():
                if result.signals is None or result.signals.empty:
                    continue
                
                latest_signal = result.signals.iloc[-1]
                if pd.isna(latest_signal) or latest_signal == "na":
                    continue
                
                # 根据指标信号类型生成交易信号
                indicator_signals = self._generate_signals_from_indicator(
                    indicator_name, latest_signal, result, current_price
                )
                signals.extend(indicator_signals)
            
            # 合并和过滤信号
            merged_signals = self._merge_signals(signals)
            
            logger.info(f"信号生成完成: 共{len(merged_signals)}个有效信号")
            return merged_signals
    
    def _generate_signals_from_indicator(self, indicator_name: str, 
                                        signal_value: str,
                                        indicator_result: IndicatorResult,
                                        current_price: Optional[float]) -> List[TradingSignal]:
        """从单个指标信号生成交易信号"""
        signals = []
        
        # MACD信号
        if indicator_name == "macd":
            if signal_value == "golden_cross":
                rule = self.signal_rules["macd_golden_cross"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
            elif signal_value == "death_cross":
                rule = self.signal_rules["macd_death_cross"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
        
        # RSI信号
        elif indicator_name.startswith("rsi"):
            if signal_value == "oversold":
                rule = self.signal_rules["rsi_oversold"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
            elif signal_value == "overbought":
                rule = self.signal_rules["rsi_overbought"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
        
        # KDJ信号
        elif indicator_name == "kdj":
            if signal_value == "golden_cross":
                rule = self.signal_rules["kdj_golden_cross"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
            elif signal_value == "death_cross":
                rule = self.signal_rules["kdj_death_cross"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
        
        # 布林带信号
        elif indicator_name == "bollinger":
            if signal_value == "upper_breakout":
                rule = self.signal_rules["bollinger_upper_breakout"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
            elif signal_value == "lower_breakout":
                rule = self.signal_rules["bollinger_lower_breakout"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
        
        # CCI信号
        elif indicator_name == "cci":
            if signal_value == "overbought":
                rule = self.signal_rules["cci_overbought"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
            elif signal_value == "oversold":
                rule = self.signal_rules["cci_oversold"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
        
        # 威廉指标信号
        elif indicator_name == "williams_r":
            if signal_value == "oversold":
                rule = self.signal_rules["williams_oversold"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
            elif signal_value == "overbought":
                rule = self.signal_rules["williams_overbought"]
                signals.append(TradingSignal(
                    signal_type=rule["type"],
                    strength=rule["strength"],
                    confidence=rule["confidence"],
                    indicators=[indicator_name],
                    reasons=[rule["description"]],
                    timestamp=datetime.now(),
                    price=current_price
                ))
        
        return signals
    
    def _merge_signals(self, signals: List[TradingSignal]) -> List[TradingSignal]:
        """合并相同类型的信号"""
        if not signals:
            return []
        
        # 按信号类型分组
        signal_groups = {}
        for signal in signals:
            key = (signal.signal_type, signal.strength)
            if key not in signal_groups:
                signal_groups[key] = []
            signal_groups[key].append(signal)
        
        # 合并每组信号
        merged = []
        for (signal_type, strength), group_signals in signal_groups.items():
            if len(group_signals) == 1:
                merged.append(group_signals[0])
            else:
                # 合并多个相同类型的信号
                merged_signal = self._merge_signal_group(group_signals)
                merged.append(merged_signal)
        
        # 按置信度排序
        merged.sort(key=lambda x: x.confidence, reverse=True)
        
        return merged
    
    def _merge_signal_group(self, signals: List[TradingSignal]) -> TradingSignal:
        """合并一组相同类型的信号"""
        # 使用第一个信号作为基础
        base_signal = signals[0]
        
        # 合并指标和原因
        all_indicators = []
        all_reasons = []
        total_confidence = 0
        
        for signal in signals:
            all_indicators.extend(signal.indicators)
            all_reasons.extend(signal.reasons)
            total_confidence += signal.confidence
        
        # 去重
        all_indicators = list(set(all_indicators))
        all_reasons = list(set(all_reasons))
        
        # 计算平均置信度（加权）
        avg_confidence = total_confidence / len(signals)
        
        # 如果有多个信号支持，提高信号强度
        if len(signals) >= 3:
            strength = SignalStrength.STRONG
            avg_confidence = min(avg_confidence * 1.2, 0.95)  # 提高置信度
        elif len(signals) >= 2:
            strength = SignalStrength.MODERATE
            avg_confidence = min(avg_confidence * 1.1, 0.9)   # 稍微提高置信度
        else:
            strength = base_signal.strength
        
        return TradingSignal(
            signal_type=base_signal.signal_type,
            strength=strength,
            confidence=avg_confidence,
            indicators=all_indicators,
            reasons=all_reasons,
            timestamp=datetime.now(),
            price=base_signal.price
        )
    
    def generate_final_recommendation(self, signals: List[TradingSignal]) -> Dict[str, Any]:
        """
        生成最终交易建议
        
        Args:
            signals: 交易信号列表
        
        Returns:
            Dict[str, Any]: 最终建议
        """
        with Timer("生成最终交易建议"):
            if not signals:
                return {
                    "recommendation": "HOLD",
                    "confidence": 0.5,
                    "reason": "无明确交易信号",
                    "signals": []
                }
            
            # 统计信号类型
            buy_signals = [s for s in signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]]
            sell_signals = [s for s in signals if s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]]
            
            # 计算加权置信度
            buy_confidence = sum(s.confidence for s in buy_signals) / max(len(buy_signals), 1)
            sell_confidence = sum(s.confidence for s in sell_signals) / max(len(sell_signals), 1)
            
            # 生成建议
            if buy_signals and not sell_signals:
                recommendation = "BUY"
                confidence = buy_confidence
                reason = f"有{len(buy_signals)}个买入信号支持"
            elif sell_signals and not buy_signals:
                recommendation = "SELL"
                confidence = sell_confidence
                reason = f"有{len(sell_signals)}个卖出信号支持"
            elif buy_signals and sell_signals:
                # 买卖信号冲突，选择置信度高的
                if buy_confidence > sell_confidence:
                    recommendation = "BUY"
                    confidence = buy_confidence
                    reason = f"买入信号置信度({buy_confidence:.0%})高于卖出信号({sell_confidence:.0%})"
                elif sell_confidence > buy_confidence:
                    recommendation = "SELL"
                    confidence = sell_confidence
                    reason = f"卖出信号置信度({sell_confidence:.0%})高于买入信号({buy_confidence:.0%})"
                else:
                    recommendation = "HOLD"
                    confidence = 0.5
                    reason = "买卖信号平衡，建议观望"
            else:
                recommendation = "HOLD"
                confidence = 0.5
                reason = "无明确交易方向"
            
            # 转换信号为字典格式
            signal_dicts = [s.to_dict() for s in signals]
            
            return {
                "recommendation": recommendation,
                "confidence": round(confidence, 2),
                "reason": reason,
                "signal_count": len(signals),
                "buy_signals": len(buy_signals),
                "sell_signals": len(sell_signals),
                "signals": signal_dicts,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_signal_report(self, stock_data: pd.DataFrame, 
                              current_price: Optional[float] = None) -> Dict[str, Any]:
        """
        生成完整的信号分析报告
        
        Args:
            stock_data: 股票数据
            current_price: 当前价格
        
        Returns:
            Dict[str, Any]: 完整分析报告
        """
        with Timer("生成完整信号分析报告"):
            # 计算技术指标
            indicator_results = technical_indicators.calculate_all_indicators(stock_data)
            
            # 生成指标报告
            indicator_report = technical_indicators.generate_indicator_report(indicator_results)
            
            # 生成交易信号
            trading_signals = self.analyze_indicators(indicator_results, current_price)
            
            # 生成最终建议
            final_recommendation = self.generate_final_recommendation(trading_signals)
            
            # 组合报告
            report = {
                "analysis_date": datetime.now().isoformat(),
                "data_period": {
                    "start": stock_data.index[0].isoformat() if len(stock_data) > 0 else None,
                    "end": stock_data.index[-1].isoformat() if len(stock_data) > 0 else None,
                    "days": len(stock_data)
                },
                "current_price": current_price,
                "indicator_summary": indicator_report["summary"],
                "trading_signals": {
                    "total": len(trading_signals),
                    "buy": len([s for s in trading_signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]]),
                    "sell": len([s for s in trading_signals if s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]]),
                    "neutral": len([s for s in trading_signals if s.signal_type == SignalType.NEUTRAL]),
                    "signals": [s.to_dict() for s in trading_signals]
                },
                "final_recommendation": final_recommendation,
                "risk_assessment": self._assess_risk(indicator_results, trading_signals)
            }
            
            logger.info(f"信号分析报告生成完成: 建议={final_recommendation['recommendation']}")
            return report
    
    def _assess_risk(self, indicator_results: Dict[str, IndicatorResult], 
                    signals: List[TradingSignal]) -> Dict[str, Any]:
        """风险评估"""
        risk_level = "LOW"
        reasons = []
        
        # 检查波动率
        if "atr" in indicator_results:
            atr_result = indicator_results["atr"]
            if not atr_result.values.empty:
                latest_atr = atr_result.values.iloc[-1]
                if latest_atr > 3.0:  # ATR百分比 > 3%
                    risk_level = "HIGH"
                    reasons.append("高波动率市场")
                elif latest_atr > 1.5:
                    risk_level = "MEDIUM"
                    reasons.append("中等波动率")
        
        # 检查信号冲突
        buy_count = len([s for s in signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]])
        sell_count = len([s for s in signals if s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]])
        
        if buy_count > 0 and sell_count > 0:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            reasons.append("买卖信号冲突")
        
        return {
            "level": risk_level,
            "reasons": reasons,
            "suggestions": self._get_risk_suggestions(risk_level)
        }
    
    def _get_risk_suggestions(self, risk_level: str) -> List[str]:
        """获取风险建议"""
        suggestions = {
            "LOW": [
                "市场波动较低，适合常规交易",
                "可适当增加仓位",
                "止损设置可相对宽松"
            ],
            "MEDIUM": [
                "市场波动中等，注意风险管理",
                "建议控制仓位在50%以下",
                "设置合理的止损点"
            ],
            "HIGH": [
                "市场波动剧烈，高风险",
                "建议轻仓或观望",
                "设置严格的止损，控制亏损",
                "避免追涨杀跌"
            ]
        }
        return suggestions.get(risk_level, ["风险等级未知，请谨慎操作"])

# 全局信号生成器实例
signal_generator = SignalGenerator()

def init_signal_generator():
    """初始化信号生成器"""
    logger.info("信号生成器初始化完成")
    return signal_generator

if __name__ == "__main__":
    # 测试信号生成模块
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    print("=== 信号生成模块测试 ===")
    
    # 初始化
    generator = init_signal_generator()
    
    # 创建测试数据
    dates = pd.date_range(start='2026-01-01', periods=50, freq='D')
    np.random.seed(42)
    
    test_data = pd.DataFrame({
        'date': dates,
        'open': 10 + np.random.randn(50).cumsum() * 0.1,
        'high': 10.5 + np.random.randn(50).cumsum() * 0.1,
        'low': 9.5 + np.random.randn(50).cumsum() * 0.1,
        'close': 10 + np.random.randn(50).cumsum() * 0.1,
        'volume': 1000000 + np.random.randn(50).cumsum() * 10000
    })
    test_data.set_index('date', inplace=True)
    
    print(f"测试数据形状: {test_data.shape}")
    
    # 测试信号生成
    print("\n测试信号生成:")
    current_price = test_data['close'].iloc[-1]
    
    # 计算技术指标
    indicator_results = technical_indicators.calculate_all_indicators(test_data)
    
    # 生成信号
    signals = generator.analyze_indicators(indicator_results, current_price)
    print(f"  生成信号数量: {len(signals)}")
    
    for i, signal in enumerate(signals[:3], 1):  # 显示前3个信号
        print(f"  信号{i}: {signal}")
        print(f"    指标: {', '.join(signal.indicators)}")
        print(f"    原因: {', '.join(signal.reasons)}")
    
    # 测试最终建议
    print("\n测试最终建议:")
    recommendation = generator.generate_final_recommendation(signals)
    print(f"  建议: {recommendation['recommendation']}")
    print(f"  置信度: {recommendation['confidence']:.0%}")
    print(f"  原因: {recommendation['reason']}")
    
    # 测试完整报告
    print("\n测试完整分析报告:")
    report = generator.generate_signal_report(test_data, current_price)
    print(f"  数据周期: {report['data_period']['days']}天")
    print(f"  当前价格: {report['current_price']:.2f}")
    print(f"  指标趋势: {report['indicator_summary']['overall_trend']}")
    print(f"  风险等级: {report['risk_assessment']['level']}")
    print(f"  风险原因: {', '.join(report['risk_assessment']['reasons'])}")
    
    print("\n" + "=" * 40)
