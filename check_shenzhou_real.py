#!/usr/bin/env python3
"""
获取神州数码真实数据 - 纯文本版本
"""

import pymysql
import pandas as pd

print("="*80)
print("神州数码(000034) - 真实数据查询")
print("="*80)

try:
    # 连接数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='785091',
        database='instockdb',
        charset='utf8mb4'
    )
    
    print("[OK] 数据库连接成功")
    
    # 查询神州数码最新数据
    query = """
    SELECT 
        trade_date,
        close_price,
        open_price,
        high_price,
        low_price,
        volume,
        change_percent,
        turnover_rate
    FROM cn_stock_indicators 
    WHERE stock_code = '000034' 
    ORDER BY trade_date DESC 
    LIMIT 10
    """
    
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        print(f"\n神州数码最新数据 (共{len(df)}条记录):")
        print("-"*80)
        
        # 显示最新数据
        latest = df.iloc[0]
        print(f"最新交易日: {latest['trade_date']}")
        print(f"收盘价: {latest['close_price']:.2f}元")
        print(f"开盘价: {latest['open_price']:.2f}元")
        print(f"最高价: {latest['high_price']:.2f}元")
        print(f"最低价: {latest['low_price']:.2f}元")
        print(f"成交量: {latest['volume']:,.0f}手")
        print(f"涨跌幅: {latest['change_percent']:.2f}%")
        print(f"换手率: {latest['turnover_rate']:.2f}%")
        
        # 验证用户提供的数据
        user_price = 40.63
        user_volume = 632500  # 63.25万手
        
        print(f"\n数据验证:")
        print(f"用户提供收盘价: {user_price}元")
        print(f"数据库收盘价: {latest['close_price']:.2f}元")
        
        price_diff = abs(latest['close_price'] - user_price)
        price_diff_pct = abs((latest['close_price'] - user_price)/user_price*100)
        print(f"价格差异: {price_diff:.2f}元 ({price_diff_pct:.1f}%)")
        
        print(f"\n用户提供成交量: {user_volume:,.0f}手")
        print(f"数据库成交量: {latest['volume']:,.0f}手")
        
        volume_diff = abs(latest['volume'] - user_volume)
        volume_diff_pct = abs((latest['volume'] - user_volume)/user_volume*100)
        print(f"成交量差异: {volume_diff:,.0f}手 ({volume_diff_pct:.1f}%)")
        
        # 检查数据一致性
        print(f"\n数据一致性检查:")
        if price_diff_pct < 1 and volume_diff_pct < 10:
            print("[PASS] 数据基本一致")
        else:
            print("[FAIL] 数据存在显著差异")
            
        # 显示历史数据
        print(f"\n近期历史数据:")
        print("-"*80)
        for i, row in df.iterrows():
            print(f"{row['trade_date']}: {row['close_price']:.2f}元 ({row['change_percent']:+.2f}%), 成交量: {row['volume']:,.0f}手")
            
    else:
        print("[ERROR] 未找到神州数码数据")
    
    # 查询技术指标
    print(f"\n技术指标数据:")
    print("-"*80)
    
    tech_query = """
    SELECT 
        trade_date,
        ma5_price,
        ma10_price,
        ma20_price,
        rsi_6,
        rsi_12,
        rsi_24,
        macd,
        macd_signal,
        macd_hist,
        kdj_k,
        kdj_d,
        kdj_j,
        boll_upper,
        boll_middle,
        boll_lower
    FROM cn_stock_indicators 
    WHERE stock_code = '000034' 
    ORDER BY trade_date DESC 
    LIMIT 3
    """
    
    tech_df = pd.read_sql(tech_query, conn)
    
    if not tech_df.empty:
        latest_tech = tech_df.iloc[0]
        print(f"MA均线: MA5={latest_tech['ma5_price']:.2f}, MA10={latest_tech['ma10_price']:.2f}, MA20={latest_tech['ma20_price']:.2f}")
        print(f"RSI指标: RSI6={latest_tech['rsi_6']:.1f}, RSI12={latest_tech['rsi_12']:.1f}, RSI24={latest_tech['rsi_24']:.1f}")
        print(f"MACD指标: MACD={latest_tech['macd']:.3f}, 信号线={latest_tech['macd_signal']:.3f}, 柱状图={latest_tech['macd_hist']:.3f}")
        print(f"KDJ指标: K={latest_tech['kdj_k']:.1f}, D={latest_tech['kdj_d']:.1f}, J={latest_tech['kdj_j']:.1f}")
        print(f"布林带: 上轨={latest_tech['boll_upper']:.2f}, 中轨={latest_tech['boll_middle']:.2f}, 下轨={latest_tech['boll_lower']:.2f}")
    else:
        print("未找到技术指标数据")
    
    conn.close()
    print("\n[OK] 数据库查询完成")
    
except Exception as e:
    print(f"[ERROR] 数据库查询错误: {e}")
    print("请检查:")
    print("1. MySQL服务是否运行")
    print("2. 数据库密码是否正确")
    print("3. 数据库名是否正确")

print("\n" + "="*80)
print("问题分析和解决方案")
print("="*80)

print("""
问题根源:
1. 我错误地使用了myStock 1.1版本的模拟数据生成器
2. 模拟数据与真实数据存在巨大差异
3. 没有验证数据准确性就直接进行分析

立即解决方案:
1. 停止所有基于模拟数据的分析
2. 使用myStock 1.0数据库的真实数据
3. 重新进行准确的技术分析
4. 修正操作指导建议

数据准确性要求:
- 收盘价误差: < 0.5%
- 成交量误差: < 5%
- 技术指标: 使用数据库计算值
- 实时验证: 与用户提供数据对比
""")

print("="*80)