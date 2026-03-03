#!/usr/bin/env python3
"""
测试API连接
检查实时数据API的可访问性
"""

import requests
import json
from datetime import datetime

def test_api_connection():
    """测试API连接"""
    print("=" * 60)
    print("API连接测试")
    print("=" * 60)
    
    # 常见的股票数据API端点
    test_endpoints = [
        {
            "name": "新浪财经实时数据",
            "url": "http://hq.sinajs.cn/list=sh000001",
            "method": "GET"
        },
        {
            "name": "腾讯财经实时数据",
            "url": "http://qt.gtimg.cn/q=sh000001",
            "method": "GET"
        },
        {
            "name": "东方财富实时数据",
            "url": "http://push2.eastmoney.com/api/qt/stock/get?secid=1.000001",
            "method": "GET"
        }
    ]
    
    results = []
    
    for endpoint in test_endpoints:
        print(f"\n测试: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        
        try:
            response = requests.get(
                endpoint['url'],
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            status = response.status_code
            content_length = len(response.content)
            
            print(f"状态码: {status}")
            print(f"内容长度: {content_length} 字节")
            
            if status == 200:
                if content_length > 0:
                    print("[OK] 连接成功，有数据返回")
                    success = True
                else:
                    print("[WARN] 连接成功，但无数据返回")
                    success = False
            elif status == 403:
                print("[ERROR] 访问被拒绝 (403 Forbidden)")
                success = False
            elif status == 404:
                print("[ERROR] 页面不存在 (404 Not Found)")
                success = False
            else:
                print(f"[ERROR] 连接失败，状态码: {status}")
                success = False
                
        except requests.exceptions.Timeout:
            print("[ERROR] 连接超时")
            success = False
        except requests.exceptions.ConnectionError:
            print("[ERROR] 连接错误")
            success = False
        except Exception as e:
            print(f"[ERROR] 未知错误: {str(e)}")
            success = False
        
        results.append({
            "name": endpoint['name'],
            "url": endpoint['url'],
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("API连接测试报告")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    
    print(f"测试总数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"失败数: {total_tests - successful_tests}")
    print(f"成功率: {successful_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for result in results:
        status = "[OK] 成功" if result['success'] else "[ERROR] 失败"
        print(f"{status} - {result['name']}")
    
    # 保存测试结果
    report = {
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "results": results
    }
    
    with open("api_connection_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: api_connection_test_report.json")
    
    return successful_tests > 0

def check_proxy_settings():
    """检查代理设置"""
    print("\n" + "=" * 60)
    print("代理设置检查")
    print("=" * 60)
    
    try:
        # 检查系统代理设置
        import os
        http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
        
        print(f"HTTP代理: {http_proxy or '未设置'}")
        print(f"HTTPS代理: {https_proxy or '未设置'}")
        
        # 检查requests的代理设置
        session = requests.Session()
        proxies = session.proxies
        print(f"Requests代理设置: {proxies or '无'}")
        
    except Exception as e:
        print(f"检查代理设置时出错: {str(e)}")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n" + "=" * 60)
    print("解决方案建议")
    print("=" * 60)
    
    print("如果API访问失败，可以尝试以下解决方案:")
    print("\n1. 使用代理服务器:")
    print("   ```python")
    print("   proxies = {")
    print("       'http': 'http://your-proxy:port',")
    print("       'https': 'http://your-proxy:port'")
    print("   }")
    print("   response = requests.get(url, proxies=proxies)")
    print("   ```")
    
    print("\n2. 使用备用数据源:")
    print("   - 本地数据库缓存")
    print("   - 第三方数据服务")
    print("   - 文件系统缓存")
    
    print("\n3. 调整请求频率:")
    print("   - 添加请求间隔")
    print("   - 使用随机User-Agent")
    print("   - 实现重试机制")
    
    print("\n4. 使用模拟数据（开发环境）:")
    print("   - 生成模拟数据")
    print("   - 使用历史数据")
    print("   - 离线分析模式")

if __name__ == "__main__":
    print("开始API连接测试...")
    check_proxy_settings()
    has_success = test_api_connection()
    
    if not has_success:
        suggest_solutions()
    
    print("\n测试完成！")