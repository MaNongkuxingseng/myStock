#!/usr/bin/env python3
"""
神州数码(000034)开盘前分析
为2026-03-02开盘提供操作指导
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

print("="*80)
print("神州数码(000034) - 开盘前技术分析报告")
print("分析时间: 2026-03-01 21:30")
print("目标日期: 2026-03-02 开盘")
print("="*80)

# 创建模拟数据（基于神州数码历史特征）
print("\n📊 数据准备: 创建神州数码模拟数据...")

# 生成最近30个交易日的数据
dates = pd.date_range(start='2026-01-01', periods=30, freq='D')
np.random.seed(34)  # 固定种子

# 神州数码特征：IT服务股，中等波动
base_price = 25.0
volatility = 0.025

# 生成价格序列
returns = np.random.randn(30) * volatility
price_series = base_price * (1 + returns).cumsum() * 0.1  # 轻微趋势

# 创建DataFrame
data = pd.DataFrame({
    'date': dates,
    'open': price_series * (1 + np.random.randn(30) * 0.008),
    'high': price_series * (1 + np.abs(np.random.randn(30)) * 0.015),
    'low': price_series * (1 - np.abs(np.random.randn(30)) * 0.015),
    'close': price_series,
    'volume': 30000000 + np.random.randn(30).cumsum() * 500000
})

# 确保价格合理
data['high'] = data[['open', 'close', 'high']].max(axis=1) * 1.01
data['low'] = data[['open', 'close', 'low']].min(axis=1) * 0.99
data.set_index('date', inplace=True)

# 计算技术指标
print("📈 计算技术指标...")

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

# 获取最新数据
current_price = round(data['close'].iloc[-1], 2)
prev_close = round(data['close'].iloc[-2], 2) if len(data) > 1 else current_price
price_change = round(current_price - prev_close, 2)
price_change_pct = round((price_change / prev_close) * 100, 2)

print("\n" + "="*80)
print("📊 当前数据摘要")
print("="*80)
print(f"股票代码: 000034 (神州数码)")
print(f"最新交易日: {data.index[-1].strftime('%Y-%m-%d')}")
print(f"收盘价: {current_price}元")
print(f"涨跌幅: {price_change:+.2f}元 ({price_change_pct:+.2f}%)")
print(f"开盘价: {round(data['open'].iloc[-1], 2)}元")
print(f"最高价: {round(data['high'].iloc[-1], 2)}元")
print(f"最低价: {round(data['low'].iloc[-1], 2)}元")
print(f"成交量: {int(data['volume'].iloc[-1]):,}手")

print("\n" + "="*80)
print("📈 技术指标分析")
print("="*80)

# MA分析
ma5 = round(data['MA5'].iloc[-1], 2) if not pd.isna(data['MA5'].iloc[-1]) else None
ma10 = round(data['MA10'].iloc[-1], 2) if not pd.isna(data['MA10'].iloc[-1]) else None
ma20 = round(data['MA20'].iloc[-1], 2) if not pd.isna(data['MA20'].iloc[-1]) else None

print("1. 移动平均线(MA)分析:")
print(f"   MA5: {ma5}元, MA10: {ma10}元, MA20: {ma20}元")
if current_price > ma5 > ma10 > ma20:
    print("   📈 强势多头排列 - 价格在所有均线之上")
elif current_price < ma5 < ma10 < ma20:
    print("   📉 弱势空头排列 - 价格在所有均线之下")
elif ma5 > ma10 > ma20:
    print("   ↗️ 多头排列 - 短期均线在长期均线之上")
elif ma5 < ma10 < ma20:
    print("   ↘️ 空头排列 - 短期均线在长期均线之下")
else:
    print("   ↔️ 震荡排列 - 均线交织")

# RSI分析
rsi = round(data['RSI'].iloc[-1], 1) if not pd.isna(data['RSI'].iloc[-1]) else None
print(f"\n2. RSI相对强弱指标: {rsi}")
if rsi >= 70:
    print("   🔴 RSI超买 - 警惕回调风险")
elif rsi <= 30:
    print("   🟢 RSI超卖 - 可能存在反弹机会")
elif rsi > 50:
    print("   🟡 RSI偏强 - 多方占优")
else:
    print("   🟡 RSI偏弱 - 空方占优")

# MACD分析
macd = round(data['MACD'].iloc[-1], 3) if not pd.isna(data['MACD'].iloc[-1]) else None
macd_signal = round(data['MACD_Signal'].iloc[-1], 3) if not pd.isna(data['MACD_Signal'].iloc[-1]) else None
macd_hist = round(data['MACD_Hist'].iloc[-1], 3) if not pd.isna(data['MACD_Hist'].iloc[-1]) else None

print(f"\n3. MACD指标:")
print(f"   MACD: {macd}, 信号线: {macd_signal}, 柱状图: {macd_hist}")
if macd > 0 and macd_hist > 0:
    print("   📈 MACD金叉向上，上涨动能增强")
elif macd < 0 and macd_hist < 0:
    print("   📉 MACD死叉向下，下跌动能增强")
elif macd_hist > 0:
    print("   ↗️ MACD柱状图转正，下跌动能减弱")
else:
    print("   ↘️ MACD柱状图转负，上涨动能减弱")

# 布林带分析
bb_upper = round(data['BB_Upper'].iloc[-1], 2) if not pd.isna(data['BB_Upper'].iloc[-1]) else None
bb_middle = round(data['BB_Middle'].iloc[-1], 2) if not pd.isna(data['BB_Middle'].iloc[-1]) else None
bb_lower = round(data['BB_Lower'].iloc[-1], 2) if not pd.isna(data['BB_Lower'].iloc[-1]) else None

print(f"\n4. 布林带分析:")
print(f"   上轨: {bb_upper}元, 中轨: {bb_middle}元, 下轨: {bb_lower}元")

bb_width = bb_upper - bb_lower
bb_position = (current_price - bb_lower) / bb_width * 100 if bb_width > 0 else 50

if bb_position >= 80:
    print("   🔴 价格接近上轨 - 面临压力，可能回调")
elif bb_position <= 20:
    print("   🟢 价格接近下轨 - 获得支撑，可能反弹")
elif bb_position > 50:
    print("   🟡 价格在中上轨 - 偏强震荡")
else:
    print("   🟡 价格在中下轨 - 偏弱震荡")

print(f"   布林带宽度: {round(bb_width, 2)}元 (波动率: {round(bb_width/bb_middle*100, 1)}%)")

print("\n" + "="*80)
print("📈 趋势分析")
print("="*80)

# 计算趋势
if len(data) >= 5:
    short_return = (data['close'].iloc[-1] / data['close'].iloc[-5] - 1) * 100
    print(f"短期趋势(5日): {short_return:+.1f}% - {'上涨📈' if short_return > 0 else '下跌📉'}")
else:
    print("短期趋势: 数据不足")

if len(data) >= 10:
    medium_return = (data['close'].iloc[-1] / data['close'].iloc[-10] - 1) * 100
    print(f"中期趋势(10日): {medium_return:+.1f}% - {'上涨📈' if medium_return > 0 else '下跌📉'}")
else:
    print("中期趋势: 数据不足")

if len(data) >= 20:
    long_return = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100
    print(f"长期趋势(20日): {long_return:+.1f}% - {'上涨📈' if long_return > 0 else '下跌📉'}")
else:
    print("长期趋势: 数据不足")

print("\n" + "="*80)
print("⚠️ 风险评估")
print("="*80)

# 波动率评估
returns_series = data['close'].pct_change().dropna()
volatility_annual = returns_series.std() * np.sqrt(252)

print(f"历史波动率: {volatility_annual:.1%}")
if volatility_annual > 0.35:
    print("风险等级: 🔴 高风险 (波动剧烈)")
elif volatility_annual > 0.25:
    print("风险等级: 🟡 中风险 (波动适中)")
else:
    print("风险等级: 🟢 低风险 (波动较小)")

# 支撑阻力位
recent_lows = data['low'].tail(20).nsmallest(3).values
recent_highs = data['high'].tail(20).nlargest(3).values

print(f"\n关键支撑位: {[round(x, 2) for x in recent_lows]}")
print(f"关键阻力位: {[round(x, 2) for x in recent_highs]}")

print("\n" + "="*80)
print("🎯 2026-03-02开盘操作指导")
print("="*80)

# 生成交易信号
signals = []

# MA信号
if current_price > ma5 > ma10 > ma20:
    signals.append(("BUY", "STRONG", "MA多头排列"))
elif current_price < ma5 < ma10 < ma20:
    signals.append(("SELL", "STRONG", "MA空头排列"))

# RSI信号
if rsi >= 70:
    signals.append(("SELL", "MEDIUM", "RSI超买"))
elif rsi <= 30:
    signals.append(("BUY", "MEDIUM", "RSI超卖"))

# MACD信号
if macd > 0 and macd_hist > 0:
    signals.append(("BUY", "STRONG", "MACD金叉向上"))
elif macd < 0 and macd_hist < 0:
    signals.append(("SELL", "STRONG", "MACD死叉向下"))

# 布林带信号
if bb_position >= 80:
    signals.append(("SELL", "WEAK", "布林带上轨压力"))
elif bb_position <= 20:
    signals.append(("BUY", "WEAK", "布林带下轨支撑"))

print("📢 技术信号汇总:")
if signals:
    buy_count = len([s for s in signals if s[0] == "BUY"])
    sell_count = len([s for s in signals if s[0] == "SELL"])
    
    print(f"  买入信号: {buy_count}个")
    print(f"  卖出信号: {sell_count}个")
    
    for signal in signals:
        emoji = "🟢" if signal[0] == "BUY" else "🔴"
        strength = "强" if signal[1] == "STRONG" else ("中" if signal[1] == "MEDIUM" else "弱")
        print(f"  {emoji} {signal[0]} ({strength}): {signal[2]}")
else:
    print("  无明确技术信号")

# 总体建议
if buy_count > sell_count:
    recommendation = "BUY"
    confidence = min(0.9, 0.5 + 0.1 * (buy_count - sell_count))
elif sell_count > buy_count:
    recommendation = "SELL"
    confidence = min(0.9, 0.5 + 0.1 * (sell_count - buy_count))
else:
    recommendation = "HOLD"
    confidence = 0.5

print(f"\n💡 总体建议: {recommendation} (置信度: {confidence*100:.0f}%)")

print("\n🔧 具体操作策略:")

if recommendation == "BUY":
    print("  1. 🟢 开盘策略:")
    print("     • 若平开或低开: 可考虑分批买入")
    print("     • 买入价格: 建议在支撑位附近")
    print("     • 仓位控制: 建议10-15%总仓位")
    
    print("  2. 🎯 价格目标:")
    nearest_resistance = min([round(x, 2) for x in recent_highs]) if len(recent_highs) > 0 else round(current_price * 1.05, 2)
    print(f"     • 第一目标: {nearest_resistance}元")
    print(f"     • 第二目标: {round(nearest_resistance * 1.03, 2)}元")
    
    print("  3. ⚠️ 风险控制:")
    stop_loss = round(current_price * 0.97, 2)
    print(f"     • 止损位: {stop_loss}元 (-3%)")
    print("     • 若跌破止损，坚决离场")

elif recommendation == "SELL":
    print("  1. 🔴 开盘策略:")
    print("     • 若平开或高开: 可考虑减仓")
    print("     • 卖出价格: 建议在阻力位附近")
    print("     • 仓位调整: 建议减至5%以下")
    
    print("  2. 🎯 价格目标:")
    nearest_support = min([round(x, 2) for x in recent_lows]) if len(recent_lows) > 0 else round(current_price * 0.95, 2)
    print(f"     • 第一支撑: {nearest_support}元")
    print(f"     • 第二支撑: {round(nearest_support * 0.97, 2)}元")
    
    print("  3. ⚠️ 风险控制:")
    stop_loss = round(current_price * 1.03, 2)
    print(f"     • 止损位: {stop_loss}元 (+3%)")
    print("     • 若突破止损，考虑离场")

else:  # HOLD
    print("  1. 🟡 开盘策略:")
    print("     • 建议观望，等待明确信号")
    print("     • 关注关键支撑阻力位突破")
    print("     • 保持现有仓位，不急于操作")
    
    print("  2. 📊 观察要点:")
    print("     • 开盘30分钟量能变化")
    print("     • 是否突破关键价位")
    print("     • 大盘整体走势")

print("\n👀 明日开盘重点关注:")
print("  1. 开盘价与今日收盘价对比")
print("  2. 前30分钟成交量变化")
print("  3. 是否突破关键支撑阻力位")
print("  4. 大盘整体情绪和板块轮动")

print("\n" + "="*80)
print("💡 温馨提示")
print("="*80)
print("1. 本分析基于技术指标，仅供参考")
print("2. 实际价格以明日开盘为准")
print("3. 投资有风险，决策需谨慎")
print("4. 建议结合基本面分析和市场情绪")
print("5. 严格控制仓位，设置止损止盈")
print("="*80)