#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取真实股票价格 - 接入新浪财经API
"""

import requests
import json
import datetime
import time

def get_sina_stock_price(stock_code):
    """从新浪财经获取股票实时价格"""
    try:
        # 构造新浪财经代码
        if stock_code.startswith('6'):
            sina_code = f'sh{stock_code}'
        else:
            sina_code = f'sz{stock_code}'
        
        url = f'http://hq.sinajs.cn/list={sina_code}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 解析数据
            data = response.text
            if '="' in data:
                content = data.split('="')[1].split('";')[0]
                fields = content.split(',')
                
                if len(fields) >= 30:
                    return {
                        'code': stock_code,
                        'name': fields[0],
                        'open': float(fields[1]),
                        'yesterday_close': float(fields[2]),
                        'current': float(fields[3]),
                        'high': float(fields[4]),
                        'low': float(fields[5]),
                        'volume': int(fields[8]),
                        'amount': float(fields[9]),
                        'time': f'{fields[30]} {fields[31]}',
                        'source': 'sina'
                    }
        
        return None
        
    except Exception as e:
        print(f"获取{stock_code}失败: {e}")
        return None

def get_tencent_stock_price(stock_code):
    """从腾讯财经获取股票价格（备用）"""
    try:
        url = f'http://qt.gtimg.cn/q={stock_code}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.text
            if '="' in data:
                content = data.split('="')[1].split('";')[0]
                fields = content.split('~')
                
                if len(fields) >= 40:
                    return {
                        'code': stock_code,
                        'name': fields[1],
                        'current': float(fields[3]),
                        'yesterday_close': float(fields[4]),
                        'open': float(fields[5]),
                        'high': float(fields[33]),
                        'low': float(fields[34]),
                        'volume': int(fields[36]),
                        'amount': float(fields[37]),
                        'time': fields[30],
                        'source': 'tencent'
                    }
        
        return None
        
    except Exception as e:
        print(f"腾讯获取{stock_code}失败: {e}")
        return None

def get_stock_price(stock_code):
    """获取股票价格，优先新浪，失败则用腾讯"""
    price_data = get_sina_stock_price(stock_code)
    
    if not price_data:
        print(f"新浪获取{stock_code}失败，尝试腾讯...")
        price_data = get_tencent_stock_price(stock_code)
    
    return price_data

def main():
    """主函数"""
    print("=" * 60)
    print("获取真实股票价格 - 2026年2月27日收盘价")
    print("=" * 60)
    
    # 需要获取价格的股票
    stocks = ['603949', '600343', '002312']
    
    real_prices = {}
    
    for stock_code in stocks:
        print(f"\n获取 {stock_code} 价格...")
        price_data = get_stock_price(stock_code)
        
        if price_data:
            real_prices[stock_code] = price_data
            
            # 显示价格信息
            change = ((price_data['current'] - price_data['yesterday_close']) / 
                     price_data['yesterday_close'] * 100)
            
            print(f"✅ {price_data['code']} {price_data['name']}")
            print(f"   当前价: {price_data['current']:.2f}元")
            print(f"   开盘价: {price_data['open']:.2f}元")
            print(f"   昨收价: {price_data['yesterday_close']:.2f}元")
            print(f"   最高价: {price_data['high']:.2f}元")
            print(f"   最低价: {price_data['low']:.2f}元")
            print(f"   涨跌幅: {change:+.2f}%")
            print(f"   成交量: {price_data['volume']:,}手")
            print(f"   成交额: {price_data['amount']:,.2f}万元")
            print(f"   更新时间: {price_data['time']}")
            print(f"   数据源: {price_data['source']}")
        else:
            print(f"❌ {stock_code}: 无法获取价格数据")
    
    print("\n" + "=" * 60)
    print("价格获取完成")
    print(f"获取时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 保存价格数据
    if real_prices:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_prices_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(real_prices, f, ensure_ascii=False, indent=2)
        
        print(f"\n价格数据已保存: {filename}")
        
        # 返回价格字典供其他脚本使用
        return real_prices
    else:
        print("\n⚠️ 警告: 未获取到任何价格数据")
        return None

if __name__ == "__main__":
    main()