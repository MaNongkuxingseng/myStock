#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试myStock实时API访问
"""

import urllib.request
import json
import sys

def test_api(endpoint, description):
    """测试API端点"""
    print(f"\n测试: {description}")
    print(f"URL: {endpoint}")
    
    try:
        response = urllib.request.urlopen(endpoint)
        data = json.loads(response.read().decode('utf-8'))
        
        if data.get('success', False):
            print("✅ 测试成功")
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
        else:
            print("⚠️ 测试返回失败")
            print(f"错误信息: {data.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    base_url = "http://localhost:9999"
    
    print("="*80)
    print("myStock实时API访问测试")
    print(f"基础URL: {base_url}")
    print("="*80)
    
    # 测试首页
    print("\n1. 测试首页...")
    try:
        response = urllib.request.urlopen(base_url + "/")
        content = response.read().decode('utf-8')
        if "myStock 实时数据API" in content:
            print("✅ 首页访问成功")
        else:
            print("⚠️ 首页内容异常")
    except Exception as e:
        print(f"❌ 首页访问失败: {e}")
    
    # 测试股票数据API
    test_cases = [
        (f"{base_url}/api/stock?code=000034&action=data", "神州数码实时数据"),
        (f"{base_url}/api/stock?code=603949&action=data", "雪龙集团实时数据"),
        (f"{base_url}/api/stock?code=000001&action=data", "平安银行实时数据"),
        (f"{base_url}/api/stock?action=market", "市场概况数据"),
    ]
    
    for url, desc in test_cases:
        test_api(url, desc)
    
    # 总结
    print("\n" + "="*80)
    print("测试完成!")
    print("="*80)
    
    print("\n📊 访问地址汇总:")
    print(f"1. 首页: {base_url}/")
    print(f"2. 神州数码: {base_url}/api/stock?code=000034&action=data")
    print(f"3. 雪龙集团: {base_url}/api/stock?code=603949&action=data")
    print(f"4. 市场概况: {base_url}/api/stock?action=market")
    
    print("\n💡 使用建议:")
    print("1. 在浏览器中打开首页查看完整API文档")
    print("2. 使用Python requests库或curl命令访问API")
    print("3. 实时数据基于数据库最新信息")
    print("4. 服务运行在端口9999，确保防火墙允许访问")

if __name__ == "__main__":
    main()