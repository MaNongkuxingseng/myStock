#!/usr/bin/env python3
"""
测试实时数据API可用性
"""

import requests
import time
from datetime import datetime

def test_api(url, name):
    """测试单个API"""
    print(f"\n测试 {name} API...")
    print(f"URL: {url}")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        elapsed = time.time() - start_time
        
        print(f"响应时间: {elapsed:.2f}秒")
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)} 字节")
        
        if response.status_code == 200:
            if len(response.text) > 100:
                print(f"✅ {name} API 可用")
                # 显示前200字符
                preview = response.text[:200].replace('\n', ' ')
                print(f"数据预览: {preview}...")
                return True
            else:
                print(f"⚠️  {name} API 响应内容过短")
                return False
        elif response.status_code == 403:
            print(f"❌ {name} API 访问被拒绝 (403)")
            return False
        else:
            print(f"❌ {name} API 错误: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ {name} API 连接超时")
        return False
    except Exception as e:
        print(f"❌ {name} API 异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("实时数据API可用性测试")
    print(f"测试时间: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # 测试的API列表
    apis = [
        {
            'name': '腾讯财经-上证指数',
            'url': 'http://qt.gtimg.cn/q=sh000001'
        },
        {
            'name': '腾讯财经-深证成指', 
            'url': 'http://qt.gtimg.cn/q=sz399001'
        },
        {
            'name': '东方财富-个股',
            'url': 'http://push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f43,f57,f58,f169,f170'
        },
        {
            'name': '新浪财经-上证指数',
            'url': 'http://hq.sinajs.cn/list=sh000001'
        }
    ]
    
    results = []
    
    for api in apis:
        success = test_api(api['url'], api['name'])
        results.append({
            'name': api['name'],
            'url': api['url'],
            'success': success,
            'time': datetime.now().strftime('%H:%M:%S')
        })
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("API测试结果汇总")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"测试总数: {total}")
    print(f"成功数: {successful}")
    print(f"失败数: {total - successful}")
    print(f"成功率: {successful/total*100:.1f}%")
    
    print("\n详细结果:")
    for result in results:
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"{status} - {result['name']}")
    
    # 建议
    print("\n" + "=" * 60)
    print("建议解决方案")
    print("=" * 60)
    
    if successful > 0:
        print("✅ 有可用的数据源，可以立即使用")
        
        # 推荐最佳数据源
        working_apis = [r for r in results if r['success']]
        if working_apis:
            best_api = working_apis[0]
            print(f"推荐使用: {best_api['name']}")
            print(f"API地址: {best_api['url']}")
            
            # 立即创建使用该API的数据获取脚本
            create_data_fetcher(best_api)
    else:
        print("❌ 所有API都不可用")
        print("应急方案:")
        print("1. 使用昨日收盘数据作为基准")
        print("2. 手动输入实时价格")
        print("3. 使用模拟数据进行测试")
        print("4. 检查网络连接和防火墙设置")
    
    return results

def create_data_fetcher(api_info):
    """创建数据获取脚本"""
    script = f'''#!/usr/bin/env python3
"""
实时数据获取脚本
使用 {api_info['name']}
"""

import requests
import json
from datetime import datetime

def get_realtime_data(stock_codes):
    """获取实时数据"""
    results = {{}}
    
    for code in stock_codes:
        try:
            # 根据代码构造URL
            if api_info['name'].startswith('腾讯财经'):
                # 腾讯格式: sh000001, sz000002
                if code.startswith('6'):
                    market_code = f"sh{code}"
                else:
                    market_code = f"sz{code}"
                
                url = f"http://qt.gtimg.cn/q={{market_code}}"
                
            elif api_info['name'].startswith('东方财富'):
                # 东方财富格式: 1.000001 (沪市), 0.000002 (深市)
                if code.startswith('6'):
                    secid = f"1.{{code}}"
                else:
                    secid = f"0.{{code}}"
                
                url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={{secid}}&fields=f43,f57,f58,f169,f170"
            
            elif api_info['name'].startswith('新浪财经'):
                # 新浪格式: sh000001, sz000002
                if code.startswith('6'):
                    market_code = f"sh{code}"
                else:
                    market_code = f"sz{code}"
                
                url = f"http://hq.sinajs.cn/list={{market_code}}"
            
            # 发送请求
            response = requests.get(url, timeout=5, headers={{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }})
            
            if response.status_code == 200:
                data = parse_response(response.text, api_info['name'])
                if data:
                    results[code] = {{
                        'code': code,
                        'success': True,
                        'data': data,
                        'timestamp': datetime.now().isoformat()
                    }}
                else:
                    results[code] = {{
                        'code': code,
                        'success': False,
                        'error': '数据解析失败',
                        'timestamp': datetime.now().isoformat()
                    }}
            else:
                results[code] = {{
                    'code': code,
                    'success': False,
                    'error': f'HTTP {{response.status_code}}',
                    'timestamp': datetime.now().isoformat()
                }}
                
        except Exception as e:
            results[code] = {{
                'code': code,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }}
    
    return results

def parse_response(text, api_name):
    """解析API响应"""
    try:
        if '腾讯财经' in api_name:
            # 腾讯格式: v_sh000001="上证指数,3200.12,..."
            if '=' in text:
                data_part = text.split('=')[1].strip('"')
                fields = data_part.split(',')
                
                if len(fields) >= 32:
                    return {{
                        'name': fields[0],
                        'open': float(fields[1]) if fields[1] else 0,
                        'pre_close': float(fields[2]) if fields[2] else 0,
                        'price': float(fields[3]) if fields[3] else 0,
                        'high': float(fields[4]) if fields[4] else 0,
                        'low': float(fields[5]) if fields[5] else 0,
                        'volume': int(fields[6]) if fields[6] else 0,
                        'amount': float(fields[7]) if fields[7] else 0,
                        'time': fields[30] if len(fields) > 30 else ''
                    }}
        
        elif '东方财富' in api_name:
            # 东方财富JSON格式
            data = json.loads(text)
            if data.get('rc') == 0 and 'data' in data:
                d = data['data']
                return {{
                    'name': d.get('f58', ''),
                    'price': d.get('f43', 0) / 100,  # 价格需要除以100
                    'change': d.get('f170', 0) / 100,
                    'change_percent': d.get('f169', 0) / 100,
                    'volume': d.get('f57', 0)
                }}
        
        elif '新浪财经' in api_name:
            # 新浪格式: var hq_str_sh000001="上证指数,3200.12,...";
            if '="' in text:
                data_part = text.split('="')[1].rstrip('";')
                fields = data_part.split(',')
                
                if len(fields) >= 6:
                    return {{
                        'name': fields[0],
                        'open': float(fields[1]) if fields[1] else 0,
                        'pre_close': float(fields[2]) if fields[2] else 0,
                        'price': float(fields[3]) if fields[3] else 0,
                        'high': float(fields[4]) if fields[4] else 0,
                        'low': float(fields[5]) if fields[5] else 0
                    }}
    
    except Exception as e:
        print(f"解析错误: {{e}}")
    
    return None

if __name__ == "__main__":
    # 测试持仓股
    holdings = ['600118', '600157', '000731']
    print("获取持仓股实时数据...")
    results = get_realtime_data(holdings)
    
    print(f"\\n获取结果:")
    for code, result in results.items():
        if result['success']:
            data = result['data']
            print(f"✅ {{code}}: {{data.get('name', 'N/A')}}")
            print(f"   当前价: {{data.get('price', 'N/A')}}")
            if 'change_percent' in data:
                print(f"   涨跌幅: {{data.get('change_percent', 'N/A')}}%")
            print(f"   时间: {{result['timestamp']}}")
        else:
            print(f"❌ {{code}}: {{result.get('error', '未知错误')}}")
'''
    
    filename = "realtime_data_fetcher.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(script)
    
    print(f"✅ 已创建实时数据获取脚本: {filename}")
    print("立即运行测试...")

if __name__ == "__main__":
    results = main()