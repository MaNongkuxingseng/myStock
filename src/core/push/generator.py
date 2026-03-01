"""
myStock 1.1版本 - 内容生成模块
基于分析结果生成各时间点的推送内容
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..utils.helpers import Timer, format_time, format_number
from ..analysis.indicators import technical_indicators
from ..analysis.signals import signal_generator, TradingSignal

logger = logging.getLogger("mystock.push.generator")

@dataclass
class PushContent:
    """推送内容"""
    title: str
    content: str
    summary: str
    signals: List[Dict[str, Any]]
    recommendation: str
    confidence: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "signals": self.signals,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }

class ContentGenerator:
    """内容生成器"""
    
    def __init__(self):
        logger.info("内容生成器初始化完成")
    
    def generate_morning_analysis(self, stock_data: pd.DataFrame, 
                                 current_price: float) -> PushContent:
        """生成早盘分析内容"""
        with Timer("生成早盘分析内容"):
            # 生成分析报告
            report = signal_generator.generate_signal_report(stock_data, current_price)
            
            # 提取关键信息
            recommendation = report["final_recommendation"]["recommendation"]
            confidence = report["final_recommendation"]["confidence"]
            signals = report["trading_signals"]["signals"]
            
            # 生成标题
            if recommendation == "BUY":
                title = f"📈 早盘看涨 | {confidence:.0%}置信度"
            elif recommendation == "SELL":
                title = f"📉 早盘看跌 | {confidence:.0%}置信度"
            else:
                title = f"⚖️ 早盘震荡 | 建议观望"
            
            # 生成内容
            content = self._format_morning_content(report, current_price)
            
            # 生成摘要
            summary = self._generate_summary(report, "早盘")
            
            return PushContent(
                title=title,
                content=content,
                summary=summary,
                signals=signals,
                recommendation=recommendation,
                confidence=confidence,
                timestamp=datetime.now()
            )
    
    def generate_opening_monitor(self, stock_data: pd.DataFrame,
                                current_price: float) -> PushContent:
        """生成开盘监控内容"""
        with Timer("生成开盘监控内容"):
            report = signal_generator.generate_signal_report(stock_data, current_price)
            recommendation = report["final_recommendation"]["recommendation"]
            confidence = report["final_recommendation"]["confidence"]
            
            title = f"🔍 开盘监控 | {recommendation}信号"
            content = self._format_opening_content(report, current_price)
            summary = self._generate_summary(report, "开盘")
            
            return PushContent(
                title=title,
                content=content,
                summary=summary,
                signals=report["trading_signals"]["signals"],
                recommendation=recommendation,
                confidence=confidence,
                timestamp=datetime.now()
            )
    
    def generate_market_observation(self, stock_data: pd.DataFrame,
                                   current_price: float) -> PushContent:
        """生成市场观察内容"""
        with Timer("生成市场观察内容"):
            report = signal_generator.generate_signal_report(stock_data, current_price)
            recommendation = report["final_recommendation"]["recommendation"]
            
            title = f"👀 市场观察 | {recommendation}趋势"
            content = self._format_market_content(report, current_price)
            summary = self._generate_summary(report, "市场")
            
            return PushContent(
                title=title,
                content=content,
                summary=summary,
                signals=report["trading_signals"]["signals"],
                recommendation=recommendation,
                confidence=report["final_recommendation"]["confidence"],
                timestamp=datetime.now()
            )
    
    def generate_closing_summary(self, stock_data: pd.DataFrame,
                                current_price: float) -> PushContent:
        """生成收盘总结内容"""
        with Timer("生成收盘总结内容"):
            report = signal_generator.generate_signal_report(stock_data, current_price)
            recommendation = report["final_recommendation"]["recommendation"]
            
            # 计算当日涨跌幅
            if len(stock_data) >= 2:
                prev_close = stock_data['close'].iloc[-2]
                change = ((current_price - prev_close) / prev_close) * 100
                change_str = f"{change:+.2f}%"
            else:
                change_str = "N/A"
            
            title = f"📊 收盘总结 | {change_str} | {recommendation}"
            content = self._format_closing_content(report, current_price, change_str)
            summary = self._generate_summary(report, "收盘")
            
            return PushContent(
                title=title,
                content=content,
                summary=summary,
                signals=report["trading_signals"]["signals"],
                recommendation=recommendation,
                confidence=report["final_recommendation"]["confidence"],
                timestamp=datetime.now()
            )
    
    def generate_evening_review(self, stock_data: pd.DataFrame,
                               current_price: float) -> PushContent:
        """生成晚间复盘内容"""
        with Timer("生成晚间复盘内容"):
            report = signal_generator.generate_signal_report(stock_data, current_price)
            recommendation = report["final_recommendation"]["recommendation"]
            
            title = f"🌙 晚间复盘 | 明日展望: {recommendation}"
            content = self._format_evening_content(report, current_price)
            summary = self._generate_summary(report, "晚间")
            
            return PushContent(
                title=title,
                content=content,
                summary=summary,
                signals=report["trading_signals"]["signals"],
                recommendation=recommendation,
                confidence=report["final_recommendation"]["confidence"],
                timestamp=datetime.now()
            )
    
    def _format_morning_content(self, report: Dict[str, Any], 
                               current_price: float) -> str:
        """格式化早盘分析内容"""
        lines = []
        
        # 标题行
        lines.append(f"⏰ **早盘分析** {format_time()}")
        lines.append("=" * 40)
        
        # 价格信息
        lines.append(f"📈 **当前价格**: {current_price:.2f}")
        
        # 建议和置信度
        rec = report["final_recommendation"]
        lines.append(f"🎯 **操作建议**: {rec['recommendation']} ({rec['confidence']:.0%}置信度)")
        lines.append(f"📝 **建议理由**: {rec['reason']}")
        
        # 信号统计
        signals = report["trading_signals"]
        lines.append(f"📊 **信号统计**: 买入{signals['buy']}个 | 卖出{signals['sell']}个 | 中性{signals['neutral']}个")
        
        # 风险提示
        risk = report["risk_assessment"]
        lines.append(f"⚠️ **风险等级**: {risk['level']}")
        if risk['reasons']:
            lines.append(f"📋 **风险原因**: {', '.join(risk['reasons'])}")
        
        # 关键指标
        lines.append("\n🔑 **关键指标**:")
        indicator_summary = report["indicator_summary"]
        lines.append(f"   • 整体趋势: {indicator_summary['overall_trend']}")
        lines.append(f"   • 买入信号: {indicator_summary['buy_signals']}个")
        lines.append(f"   • 卖出信号: {indicator_summary['sell_signals']}个")
        
        # 操作建议
        lines.append("\n💡 **操作建议**:")
        if rec['recommendation'] == "BUY":
            lines.append("   1. 可考虑分批建仓")
            lines.append("   2. 设置止损位: 当前价-2%")
            lines.append("   3. 目标价位: 当前价+5%")
        elif rec['recommendation'] == "SELL":
            lines.append("   1. 考虑减仓或离场")
            lines.append("   2. 反弹是卖出机会")
            lines.append("   3. 等待更好入场点")
        else:
            lines.append("   1. 建议观望为主")
            lines.append("   2. 等待明确信号")
            lines.append("   3. 控制仓位风险")
        
        # 关注要点
        lines.append("\n👁️ **关注要点**:")
        lines.append("   1. 开盘后30分钟走势")
        lines.append("   2. 成交量变化")
        lines.append("   3. 关键支撑阻力位")
        
        return "\n".join(lines)
    
    def _format_opening_content(self, report: Dict[str, Any],
                               current_price: float) -> str:
        """格式化开盘监控内容"""
        lines = []
        
        lines.append(f"🔍 **开盘监控** {format_time()}")
        lines.append("=" * 40)
        
        lines.append(f"💰 **当前价格**: {current_price:.2f}")
        
        rec = report["final_recommendation"]
        lines.append(f"📢 **实时建议**: {rec['recommendation']}")
        
        # 重点关注信号
        signals = report["trading_signals"]["signals"]
        if signals:
            lines.append("\n🚨 **重点关注信号**:")
            for i, signal in enumerate(signals[:3], 1):  # 显示前3个重要信号
                lines.append(f"   {i}. {signal['signal'].upper()} - {signal['strength']}信号")
                if signal.get('reasons'):
                    lines.append(f"     原因: {signal['reasons'][0]}")
        
        # 实时观察
        lines.append("\n👀 **实时观察**:")
        lines.append("   1. 开盘价与昨日收盘对比")
        lines.append("   2. 前30分钟成交量")
        lines.append("   3. 主要技术指标变化")
        
        return "\n".join(lines)
    
    def _format_market_content(self, report: Dict[str, Any],
                              current_price: float) -> str:
        """格式化市场观察内容"""
        lines = []
        
        lines.append(f"👀 **市场观察** {format_time()}")
        lines.append("=" * 40)
        
        lines.append(f"📊 **当前状态**: {report['indicator_summary']['overall_trend']}")
        lines.append(f"🎯 **操作方向**: {report['final_recommendation']['recommendation']}")
        
        # 市场情绪
        buy_signals = report['trading_signals']['buy']
        sell_signals = report['trading_signals']['sell']
        total_signals = buy_signals + sell_signals
        
        if total_signals > 0:
            buy_ratio = buy_signals / total_signals
            if buy_ratio > 0.7:
                sentiment = "极度乐观"
            elif buy_ratio > 0.6:
                sentiment = "乐观"
            elif buy_ratio > 0.4:
                sentiment = "中性"
            elif buy_ratio > 0.3:
                sentiment = "谨慎"
            else:
                sentiment = "悲观"
            
            lines.append(f"😊 **市场情绪**: {sentiment} (买入:{buy_signals}/卖出:{sell_signals})")
        
        # 关键指标状态
        lines.append("\n📈 **指标状态**:")
        indicator_summary = report["indicator_summary"]
        
        strong_indicators = indicator_summary.get("strong_indicators", [])
        if strong_indicators:
            lines.append(f"   • 强势指标: {', '.join(strong_indicators[:3])}")
        
        weak_indicators = indicator_summary.get("weak_indicators", [])
        if weak_indicators:
            lines.append(f"   • 弱势指标: {', '.join(weak_indicators[:3])}")
        
        # 操作建议
        lines.append("\n💼 **操作策略**:")
        risk_level = report["risk_assessment"]["level"]
        if risk_level == "HIGH":
            lines.append("   高风险市场，建议:")
            lines.append("   • 严格控制仓位")
            lines.append("   • 设置严格止损")
            lines.append("   • 避免追涨杀跌")
        elif risk_level == "MEDIUM":
            lines.append("   中等风险市场，建议:")
            lines.append("   • 适度参与")
            lines.append("   • 分批建仓")
            lines.append("   • 关注关键点位")
        else:
            lines.append("   低风险市场，建议:")
            lines.append("   • 可适当增加仓位")
            lines.append("   • 关注趋势延续")
            lines.append("   • 把握回调机会")
        
        return "\n".join(lines)
    
    def _format_closing_content(self, report: Dict[str, Any],
                               current_price: float,
                               change_str: str) -> str:
        """格式化收盘总结内容"""
        lines = []
        
        lines.append(f"📊 **收盘总结** {format_time()}")
        lines.append("=" * 40)
        
        lines.append(f"💰 **收盘价格**: {current_price:.2f}")
        lines.append(f"📈 **今日涨跌**: {change_str}")
        
        # 全天表现总结
        rec = report["final_recommendation"]
        lines.append(f"🎯 **全天建议**: {rec['recommendation']} ({rec['confidence']:.0%})")
        
        # 信号变化
        signals = report["trading_signals"]
        lines.append(f"📢 **信号变化**: 买入{signals['buy']}↑ 卖出{signals['sell']}↓")
        
        # 技术面总结
        lines.append("\n🔧 **技术面总结**:")
        trend = report["indicator_summary"]["overall_trend"]
        if "bull" in trend:
            lines.append("   • 技术面偏多")
            lines.append("   • 多数指标向好")
            lines.append("   • 趋势有望延续")
        elif "bear" in trend:
            lines.append("   • 技术面偏空")
            lines.append("   • 调整压力较大")
            lines.append("   • 谨慎对待反弹")
        else:
            lines.append("   • 技术面中性")
            lines.append("   • 多空力量均衡")
            lines.append("   • 等待方向选择")
        
        # 明日展望
        lines.append("\n🔮 **明日展望**:")
        risk = report["risk_assessment"]
        if risk["level"] == "HIGH":
            lines.append("   明日预计波动较大")
            lines.append("   建议控制风险为主")
            lines.append("   等待市场企稳")
        elif rec["recommendation"] == "BUY":
            lines.append("   明日有望延续涨势")
            lines.append("   关注开盘表现")
            lines.append("   把握回调买入机会")
        elif rec["recommendation"] == "SELL":
            lines.append("   明日可能继续调整")
            lines.append("   反弹是减仓机会")
            lines.append("   等待更好买点")
        else:
            lines.append("   明日可能维持震荡")
            lines.append("   高抛低吸操作")
            lines.append("   等待突破信号")
        
        # 关键点位
        lines.append("\n📍 **关键点位**:")
        lines.append("   • 支撑位: 关注今日低点")
        lines.append("   • 阻力位: 关注今日高点")
        lines.append("   • 突破位: 等待明确方向")
        
        return "\n".join(lines)
    
    def _format_evening_content(self, report: Dict[str, Any],
                               current_price: float) -> str:
        """格式化晚间复盘内容"""
        lines = []
        
        lines.append(f"🌙 **晚间复盘** {format_time()}")
        lines.append("=" * 40)
        
        lines.append("📅 **全天回顾**:")
        lines.append("   回顾今日市场表现")
        lines.append("   分析技术指标变化")
        lines.append("   总结交易信号演变")
        
        # 技术分析
        lines.append("\n🔍 **技术分析**:")
        indicator_summary = report["indicator_summary"]
        lines.append(f"   • 整体趋势: {indicator_summary['overall_trend']}")
        lines.append(f"   • 多空对比: 买入{indicator_summary['buy_signals']}:卖出{indicator_summary['sell_signals']}")
        
        # 信号有效性评估
        lines.append("\n📊 **信号评估**:")
        signals = report["trading_signals"]["signals"]
        if signals:
            strong_signals = [s for s in signals if s.get('strength') == 'strong']
            if strong_signals:
                lines.append(f"   • 强信号数量: {len(strong_signals)}个")
                for signal in strong_signals[:2]:
                    lines.append(f"     - {signal['signal']}: {signal.get('reasons', [''])[0]}")
        
        # 风险提示
        lines.append("\n⚠️ **风险提示**:")
        risk = report["risk_assessment"]
        lines.append(f"   • 风险等级: {risk['level']}")
        for suggestion in risk['suggestions'][:2]:
            lines.append(f"   • {suggestion}")
        
        # 明日策略
        lines.append("\n🎯 **明日策略**:")
        rec = report["final_recommendation"]
        if rec["recommendation"] == "BUY":
            lines.append("   1. 关注早盘表现，择机入场")
            lines.append("   2. 设置合理止损，控制风险")
            lines.append("   3. 目标看向阻力位突破")
        elif rec["recommendation"] == "SELL":
            lines.append("   1. 反弹是减仓机会")
            lines.append("   2. 等待更好买点出现")
            lines.append("   3. 控制仓位，保持谨慎")
        else:
            lines.append("   1. 观望为主，等待信号")
            lines.append("   2. 小仓位试盘")
            lines.append("   3. 关注突破方向")
        
        # 学习总结
        lines.append("\n📚 **学习总结**:")
        lines.append("   1. 回顾今日交易决策")
        lines.append("   2. 分析指标有效性")
        lines.append("   3. 优化明日交易计划")
        
        return "\n".join(lines)
    
    def _generate_summary(self, report: Dict[str, Any], time_point: str) -> str:
        """生成内容摘要"""
        rec = report["final_recommendation"]
        risk = report["risk_assessment"]
        
        summary = f"{time_point}分析: {rec['recommendation']}建议"
        summary += f", {rec['confidence']:.0%}置信度"
        summary += f", 风险等级: {risk['level']}"
        
        signals = report["trading_signals"]
        if signals['buy'] > 0 or signals['sell'] > 0:
            summary += f", 信号: 买{signals['buy']}/卖{signals['sell']}"
        
        return summary
    
    def generate_by_time_point(self, time_point: str, 
                              stock_data: pd.DataFrame,
                              current_price: float) -> PushContent:
        """根据时间点生成内容"""
        time_point_handlers = {
            "09:00": self.generate_morning_analysis,
            "09:30": self.generate_opening_monitor,
            "10:00": self.generate_market_observation,
            "11:00": self.generate_market_observation,  # 复用市场观察
            "13:00": self.generate_market_observation,  # 复用市场观察
            "14:00": self.generate_market_observation,  # 复用市场观察
            "14:30": self.generate_market_observation,  # 复用市场观察
            "15:00": self.generate_closing_summary,
            "20:00": self.generate_evening_review
        }
        
        handler = time_point_handlers.get(time_point)
        if not handler:
            logger.warning(f"未知时间点: {time_point}，使用默认处理")
            handler = self.generate_market_observation
        
        return handler(stock_data, current_price)

# 全局内容生成器实例
content_generator = ContentGenerator()

def init_content_generator():
    """初始化内容生成器"""
    logger.info("内容生成器初始化完成")
    return content_generator

if __name__ == "__main__":
    # 测试内容生成模块
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    print("=== 内容生成模块测试 ===")
    
    # 初始化
    generator = init_content_generator()
    
    # 创建测试数据
    dates = pd.date_range(start='2026-01-01', periods=30, freq='D')
    np.random.seed(42)
    
    test_data = pd.DataFrame({
        'date': dates,
        'open': 10 + np.random.randn(30).cumsum() * 0.1,
        'high': 10.5 + np.random.randn(30).cumsum() * 0.1,
        'low': 9.5 + np.random.randn(30).cumsum() * 0.1,
        'close': 10 + np.random.randn(30).cumsum() * 0.1,
        'volume': 1000000 + np.random.randn(30).cumsum() * 10000
    })
    test_data.set_index('date', inplace=True)
    
    current_price = test_data['close'].iloc[-1]
    
    # 测试各时间点内容生成
    print("\n测试各时间点内容生成:")
    
    time_points = ["09:00", "09:30", "15:00", "20:00"]
    for time_point in time_points:
        print(f"\n{time_point} 内容生成:")
        try:
            content = generator.generate_by_time_point(time_point, test_data, current_price)
            print(f"  标题: {content.title}")
            print(f"  建议: {content.recommendation} ({content.confidence:.0%})")
            print(f"  摘要: {content.summary}")
            print(f"  信号数: {len(content.signals)}")
            
            # 显示部分内容
            content_lines = content.content.split('\n')
            print(f"  内容预览:")
            for line in content_lines[:5]:
                print(f"    {line}")
            if len(content_lines) > 5:
                print(f"    ... (共{len(content_lines)}行)")
                
        except Exception as e:
            print(f"  生成失败: {e}")
    
    print("\n" + "=" * 40)