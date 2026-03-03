#!/usr/bin/env python3
"""
修复后的实时数据获取
"""

import requests
from datetime import datetime

def get_tencent_realtime_fixed(code):
    """从腾讯财经获取实时数据（修复版本）"""
    # 构造代码
    if code.startswith('6'):
        market_code = f"sh{code}"
    else:
        market_code = f"sz{code}"
    
    url = f"http://qt.gtimg.cn/q={market_code}"
    
    try:
        response = requests.get(url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        
        if response.status_code == 200:
            text = response.text.strip()
            print(f"原始响应: {text[:100]}...")
            
            # 解析新格式: v_sh000001="1~上证指数~000001~4186.02~..."
            if '=' in text:
                data_part = text.split('=')[1].strip('"')
                fields = data_part.split('~')
                
                print(f"字段数: {len(fields)}")
                print(f"字段示例: {fields[:10]}")
                
                if len(fields) >= 40:
                    # 根据观察的字段位置
                    return {
                        'code': code,
                        'market_code': market_code,
                        'name': fields[1] if len(fields) > 1 else '',
                        'price': float(fields[3]) if len(fields) > 3 and fields[3] else 0,
                        'pre_close': float(fields[4]) if len(fields) > 4 and fields[4] else 0,
                        'open': float(fields[5]) if len(fields) > 5 and fields[5] else 0,
                        'high': float(fields[33]) if len(fields) > 33 and fields[33] else 0,
                        'low': float(fields[34]) if len(fields) > 34 and fields[34] else 0,
                        'volume': int(fields[6]) if len(fields) > 6 and fields[6] else 0,
                        'amount': float(fields[37]) if len(fields) > 37 and fields[37] else 0,
                        'time': fields[30] if len(fields) > 30 else '',
                        'status': '交易中' if len(fields) > 32 and fields[32] == '1' else '已收盘',
                        'success': True,
                        'raw_fields': fields[:20]  # 保存前20个字段用于调试
                    }
                else:
                    print(f"字段不足: 需要至少40个，实际{len(fields)}个")
        
        return {'code': code, 'success': False, 'error': '解析失败', 'raw': text[:100]}
        
    except Exception as e:
        return {'code': code, 'success': False, 'error': str(e)}

def main():
    print("="*60)
    print("修复版实时数据获取")
    print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    
    # 先测试上证指数
    print("\n测试上证指数 (sh000001)...")
    test_data = get_tencent_realtime_fixed('000001')
    if test_data.get('success'):
        print(f"✅ 测试成功!")
        print(f"  名称: {test_data.get('name')}")
        print(f"  当前价: {test_data.get('price')}")
        print(f"  昨收: {test_data.get('pre_close')}")
        print(f"  涨跌: {test_data.get('price', 0) - test_data.get('pre_close', 0):.2f}")
        print(f"  涨跌幅: {(test_data.get('price', 0) - test_data.get('pre_close', 0)) / test_data.get('pre_close', 1) * 100:.2f}%")
        print(f"  时间: {test_data.get('time')}")
    else:
        print(f"❌ 测试失败: {test_data.get('error')}")
    
    # 持仓股
    print("\n" + "="*60)
    print("获取持仓股实时数据")
    print("="*60)
    
    holdings = ['600118', '600157', '000731']
    
    results = []
    for code in holdings:
        print(f"\n获取 {code}...")
        data = get_tencent_realtime_fixed(code)
        
        if data.get('success'):
            print(f"✅ 成功获取!")
            print(f"  名称: {data.get('name')}")
            print(f"  当前价: {data.get('price')}")
            print(f"  昨收: {data.get('pre_close')}")
            
            if data['price'] > 0 and data['pre_close'] > 0:
                change = data['price'] - data['pre_close']
                change_pct = change / data['pre_close'] * 100
                print(f"  涨跌: {change:.2f}")
                print(f"  涨跌幅: {change_pct:.2f}%")
            
            print(f"  开盘价: {data.get('open')}")
            print(f"  最高价: {data.get('high')}")
            print(f"  最低价: {data.get('low')}")
            
            vol = data.get('volume', 0)
            if vol > 0:
                print(f"  成交量: {vol:,} 手")
            
            print(f"  时间: {data.get('time')}")
            print(f"  状态: {data.get('status')}")
        else:
            print(f"❌ 获取失败: {data.get('error')}")
            if 'raw' in data:
                print(f"  原始数据: {data['raw']}")
        
        results.append(data)
    
    # 汇总
    print("\n" + "="*60)
    print("实时数据汇总")
    print("="*60)
    
    successful = sum(1 for r in results if r.get('success'))
    print(f"成功获取: {successful}/{len(results)} 只股票")
    
    if successful > 0:
        print("\n立即生成10:00消息内容...")
        
        # 生成简要分析
        analysis = []
        for data in results:
            if data.get('success'):
                stock_info = f"{data.get('name', data['code'])} ({data['code']}): "
                stock_info += f"现价{data.get('price')}元, "
                
                if data['price'] > 0 and data['pre_close'] > 0:
                    change_pct = (data['price'] - data['pre_close']) / data['pre_close'] * 100
                    stock_info += f"{'↑' if change_pct > 0 else '↓'}{abs(change_pct):.2f}%"
                
                analysis.append(stock_info)
        
        print("\n实时股价:")
        for info in analysis:
            print(f"  • {info}")
    
    # 保存结果
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"realtime_fixed_{timestamp}.json"
    
    save_data = {
        'timestamp': datetime.now().isoformat(),
        'success_count': successful,
        'total_count': len(results),
        'results': results
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到: {filename}")
    
    return results

if __name__ == "__main__":
    results = main()