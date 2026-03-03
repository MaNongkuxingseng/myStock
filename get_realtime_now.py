#!/usr/bin/env python3
"""
立即获取实时数据 - 简化版本
"""

import requests
from datetime import datetime

def get_tencent_realtime(code):
    """从腾讯财经获取实时数据"""
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
            # 解析腾讯格式
            text = response.text
            if '=' in text:
                data_part = text.split('=')[1].strip('"')
                fields = data_part.split(',')
                
                if len(fields) >= 32:
                    return {
                        'code': code,
                        'name': fields[0],
                        'open': float(fields[1]) if fields[1] else 0,
                        'pre_close': float(fields[2]) if fields[2] else 0,
                        'price': float(fields[3]) if fields[3] else 0,
                        'high': float(fields[4]) if fields[4] else 0,
                        'low': float(fields[5]) if fields[5] else 0,
                        'volume': int(fields[6]) if fields[6] else 0,
                        'amount': float(fields[7]) if fields[7] else 0,
                        'buy1': float(fields[9]) if fields[9] else 0,
                        'sell1': float(fields[19]) if fields[19] else 0,
                        'time': fields[30] if len(fields) > 30 else '',
                        'status': fields[32] if len(fields) > 32 else '',
                        'success': True
                    }
        
        return {'code': code, 'success': False, 'error': '解析失败'}
        
    except Exception as e:
        return {'code': code, 'success': False, 'error': str(e)}

def main():
    print("立即获取实时数据...")
    print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
    
    # 持仓股
    holdings = ['600118', '600157', '000731']
    
    results = []
    for code in holdings:
        print(f"\n获取 {code}...")
        data = get_tencent_realtime(code)
        
        if data.get('success'):
            print(f"[成功] {data.get('name', 'N/A')}")
            print(f"  当前价: {data.get('price', 'N/A')}")
            print(f"  涨跌: {data.get('price', 0) - data.get('pre_close', 0):.2f}")
            print(f"  开盘价: {data.get('open', 'N/A')}")
            print(f"  最高价: {data.get('high', 'N/A')}")
            print(f"  最低价: {data.get('low', 'N/A')}")
            print(f"  成交量: {data.get('volume', 'N/A')}")
            print(f"  时间: {data.get('time', 'N/A')}")
            print(f"  状态: {data.get('status', 'N/A')}")
        else:
            print(f"[失败] {data.get('error', '未知错误')}")
        
        results.append(data)
    
    # 生成简要报告
    print("\n" + "="*60)
    print("实时数据汇总")
    print("="*60)
    
    successful = sum(1 for r in results if r.get('success'))
    print(f"成功获取: {successful}/{len(results)} 只股票")
    
    # 保存结果
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"realtime_data_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到: realtime_data_{timestamp}.json")
    
    return results

if __name__ == "__main__":
    results = main()