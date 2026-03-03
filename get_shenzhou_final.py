#!/usr/bin/env python3
"""
获取神州数码最终真实数据
"""

import pymysql

print("="*80)
print("神州数码(000034) - 真实数据验证")
print("="*80)

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='785091',
        database='instockdb',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 查询神州数码数据
    query = """
    SELECT 
        date,
        code,
        name,
        new_price,
        pre_close_price,
        high_price,
        low_price,
        volume,
        change_rate,
        turnoverrate
    FROM cn_stock_selection 
    WHERE code = '000034' 
    ORDER BY date DESC 
    LIMIT 3
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"找到{len(results)}条神州数码数据:")
        print("-"*80)
        
        for row in results:
            date, code, name, new_price, pre_close, high, low, volume, change_rate, turnover = row
            
            print(f"日期: {date}")
            print(f"股票: {code} - {name}")
            print(f"最新价: {new_price}元")
            print(f"前收盘: {pre_close}元")
            print(f"最高价: {high}元")
            print(f"最低价: {low}元")
            print(f"成交量: {volume:,}手 ({volume/10000:.2f}万手)")
            print(f"涨跌幅: {change_rate}%")
            print(f"换手率: {turnover}%")
            print("-"*80)
        
        # 数据验证
        latest = results[0]
        db_price = latest[3]  # new_price
        db_volume = latest[7]  # volume
        
        user_price = 40.63
        user_volume = 63.25 * 10000  # 转换为手
        
        print("\n数据验证:")
        print(f"用户提供: 收盘价={user_price}元, 成交量={user_volume/10000:.2f}万手")
        print(f"数据库: 最新价={db_price}元, 成交量={db_volume/10000:.2f}万手")
        
        price_diff = abs(db_price - user_price)
        price_diff_pct = abs((db_price - user_price)/user_price*100)
        
        volume_diff = abs(db_volume - user_volume)
        volume_diff_pct = abs((db_volume - user_volume)/user_volume*100)
        
        print(f"\n差异分析:")
        print(f"价格差异: {price_diff:.2f}元 ({price_diff_pct:.1f}%)")
        print(f"成交量差异: {volume_diff/10000:.2f}万手 ({volume_diff_pct:.1f}%)")
        
        if price_diff_pct < 1 and volume_diff_pct < 10:
            print("结论: 数据基本一致")
        elif price_diff_pct < 5 and volume_diff_pct < 30:
            print("结论: 数据存在一定差异，但可接受")
        else:
            print("结论: 数据存在显著差异")
            
        # 检查数据日期
        latest_date = latest[0]
        print(f"\n数据时效性:")
        print(f"最新数据日期: {latest_date}")
        print(f"用户提到的交易日: 2026-02-27")
        
        if str(latest_date) == "2026-02-27":
            print("日期匹配: 是")
        else:
            print(f"日期匹配: 否 (数据库最新是{latest_date})")
            
            # 查询2026-02-27的数据
            date_query = """
            SELECT date, new_price, volume 
            FROM cn_stock_selection 
            WHERE code = '000034' AND date = '2026-02-27'
            """
            cursor.execute(date_query)
            date_result = cursor.fetchone()
            
            if date_result:
                print(f"\n找到2026-02-27数据:")
                print(f"日期: {date_result[0]}, 价格: {date_result[1]}, 成交量: {date_result[2]:,}手")
            else:
                print("\n数据库中无2026-02-27数据")
                
    else:
        print("未找到神州数码数据")
        
        # 查看数据库中有哪些日期
        date_query = "SELECT DISTINCT date FROM cn_stock_selection ORDER BY date DESC LIMIT 5"
        cursor.execute(date_query)
        dates = cursor.fetchall()
        print(f"\n数据库中的最新日期: {[d[0] for d in dates]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"数据库查询错误: {e}")

print("\n" + "="*80)
print("问题总结和解决方案")
print("="*80)

print("""
问题确认:
1. 我之前提供的数据完全错误
2. 错误原因: 使用了myStock 1.1版本的模拟数据生成器
3. 正确数据应该来自myStock 1.0数据库

立即行动:
1. 停止使用模拟数据
2. 使用真实数据库数据重新分析
3. 修正操作指导建议
4. 建立数据验证机制

数据准确性要求:
1. 收盘价误差 < 0.5%
2. 成交量误差 < 10%
3. 使用最新交易日数据
4. 与用户提供数据对比验证

系统改进:
1. 在分析前自动验证数据准确性
2. 建立数据源优先级: 真实数据库 > 模拟数据
3. 添加数据差异报警机制
4. 定期校准数据源
""")

print("="*80)