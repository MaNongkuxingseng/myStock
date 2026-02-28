#!/usr/bin/env python3
"""
真实行情数据获取模块
使用新浪财经免费API获取实时股票数据
"""

import sys
import os
# 添加自定义库路径
sys.path.append('D:\\python_libs')

import requests
import json
import time
from datetime import datetime
import re

class RealTimeDataFetcher:
    """真实行情数据获取器"""
    
    def __init__(self):
        # 新浪财经API配置
        self.sina_api = "http://hq.sinajs.cn/list="
        
        # 股票代码映射（新浪格式）
        self.code_mapping = {
            '603949': 'sh603949',  # 上证
            '600343': 'sh600343',  # 上证
            '002312': 'sz002312',  # 深证
            '600537': 'sh600537'   # 上证
        }
        
        # 缓存配置
        self.cache = {}
        self.cache_duration = 30  # 秒
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn'
        }
    
    def get_sina_stock_data(self, code):
        """从新浪财经获取股票数据"""
        sina_code = self.code_mapping.get(code)
        if not sina_code:
            print(f"未找到股票代码映射: {code}")
            return None
        
        # 检查缓存
        cache_key = f"{code}_{datetime.now().strftime('%H%M')}"
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return cached_data
        
        try:
            # 构建请求URL
            url = f"{self.sina_api}{sina_code}"
            
            # 发送请求
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'gbk'  # 新浪使用GBK编码
            
            if response.status_code != 200:
                print(f"请求失败: {response.status_code}")
                return None
            
            # 解析响应数据
            content = response.text
            # 格式: var hq_str_sh603949="雪龙集团,19.390,19.600,...";
            
            # 提取数据部分
            match = re.search(r'="(.*?)"', content)
            if not match:
                print(f"数据格式错误: {content[:100]}")
                return None
            
            data_str = match.group(1)
            data_parts = data_str.split(',')
            
            if len(data_parts) < 3:
                print(f"数据不完整: {data_str}")
                return None
            
            # 解析数据字段
            stock_data = {
                'code': code,
                'name': data_parts[0],
                'open': float(data_parts[1]) if data_parts[1] else 0,
                'pre_close': float(data_parts[2]) if data_parts[2] else 0,
                'price': float(data_parts[3]) if data_parts[3] else 0,
                'high': float(data_parts[4]) if data_parts[4] else 0,
                'low': float(data_parts[5]) if data_parts[5] else 0,
                'volume': int(data_parts[8]) if data_parts[8] else 0,
                'amount': float(data_parts[9]) if data_parts[9] else 0,
                'time': f"{data_parts[30]} {data_parts[31]}" if len(data_parts) > 31 else datetime.now().strftime('%H:%M:%S'),
                'source': 'sina',
                'timestamp': datetime.now().isoformat()
            }
            
            # 计算涨跌幅
            if stock_data['pre_close'] > 0:
                change = stock_data['price'] - stock_data['pre_close']
                change_percent = (change / stock_data['pre_close']) * 100
                stock_data['change'] = round(change, 3)
                stock_data['change_percent'] = round(change_percent, 2)
            else:
                stock_data['change'] = 0
                stock_data['change_percent'] = 0
            
            # 更新缓存
            self.cache[cache_key] = (stock_data, time.time())
            
            return stock_data
            
        except requests.exceptions.Timeout:
            print(f"请求超时: {code}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"网络错误: {e}")
            return None
        except (ValueError, IndexError) as e:
            print(f"数据解析错误: {e}")
            return None
    
    def get_tencent_stock_data(self, code):
        """从腾讯财经获取股票数据（备用）"""
        # 腾讯API格式: http://qt.gtimg.cn/q=sh603949
        tencent_code = f"sh{code}" if code.startswith('6') else f"sz{code}"
        url = f"http://qt.gtimg.cn/q={tencent_code}"
        
        try:
            response = requests.get(url, timeout=5)
            response.encoding = 'gbk'
            
            if response.status_code != 200:
                return None
            
            content = response.text
            # 格式: v_sh603949="1~雪龙集团~603949~19.39~19.60~...";
            
            match = re.search(r'="(.*?)"', content)
            if not match:
                return None
            
            data_str = match.group(1)
            data_parts = data_str.split('~')
            
            if len(data_parts) < 40:
                return None
            
            stock_data = {
                'code': code,
                'name': data_parts[1],
                'price': float(data_parts[3]) if data_parts[3] else 0,
                'change': float(data_parts[4]) if data_parts[4] else 0,
                'change_percent': float(data_parts[5]) if data_parts[5] else 0,
                'volume': int(data_parts[6]) if data_parts[6] else 0,
                'amount': float(data_parts[37]) if data_parts[37] else 0,
                'high': float(data_parts[33]) if data_parts[33] else 0,
                'low': float(data_parts[34]) if data_parts[34] else 0,
                'open': float(data_parts[5]) if data_parts[5] else 0,
                'pre_close': float(data_parts[4]) if data_parts[4] else 0,
                'time': data_parts[30] if data_parts[30] else datetime.now().strftime('%H:%M:%S'),
                'source': 'tencent',
                'timestamp': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            print(f"腾讯API错误: {e}")
            return None
    
    def get_stock_data(self, code, fallback=True):
        """获取股票数据，支持备用数据源"""
        # 优先使用新浪
        data = self.get_sina_stock_data(code)
        
        # 如果新浪失败且启用备用，尝试腾讯
        if not data and fallback:
            data = self.get_tencent_stock_data(code)
        
        return data
    
    def get_multiple_stocks(self, codes):
        """批量获取多只股票数据"""
        results = {}
        
        for code in codes:
            data = self.get_stock_data(code)
            if data:
                results[code] = data
            else:
                results[code] = {
                    'code': code,
                    'error': '获取数据失败',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 避免请求过快
            time.sleep(0.1)
        
        return results
    
    def get_market_index(self):
        """获取大盘指数"""
        indices = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000300': '沪深300'
        }
        
        market_data = {}
        
        for sina_code, name in indices.items():
            try:
                url = f"{self.sina_api}{sina_code}"
                response = requests.get(url, headers=self.headers, timeout=5)
                response.encoding = 'gbk'
                
                if response.status_code == 200:
                    content = response.text
                    match = re.search(r'="(.*?)"', content)
                    if match:
                        data_str = match.group(1)
                        data_parts = data_str.split(',')
                        
                        if len(data_parts) >= 3:
                            price = float(data_parts[1]) if data_parts[1] else 0
                            pre_close = float(data_parts[2]) if data_parts[2] else 0
                            
                            if pre_close > 0:
                                change = price - pre_close
                                change_percent = (change / pre_close) * 100
                            else:
                                change = 0
                                change_percent = 0
                            
                            market_data[name] = {
                                'price': round(price, 2),
                                'change': round(change, 2),
                                'change_percent': round(change_percent, 2),
                                'time': data_parts[30] if len(data_parts) > 30 else datetime.now().strftime('%H:%M:%S')
                            }
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"获取指数{name}失败: {e}")
                market_data[name] = {
                    'price': 0,
                    'change': 0,
                    'change_percent': 0,
                    'error': str(e)
                }
        
        return market_data

def test_real_time_data():
    """测试实时数据获取"""
    fetcher = RealTimeDataFetcher()
    
    print("测试实时行情API接入...")
    print("="*60)
    
    # 测试单只股票
    test_codes = ['603949', '600343', '002312', '600537']
    
    for code in test_codes:
        print(f"\n获取 {code} 数据...")
        data = fetcher.get_stock_data(code)
        
        if data and 'error' not in data:
            print(f"✅ {data.get('name', '')} ({code})")
            print(f"   现价: {data.get('price', 0)}元")
            print(f"   涨跌: {data.get('change', 0):+.2f}元 ({data.get('change_percent', 0):+.2f}%)")
            print(f"   时间: {data.get('time', '')}")
            print(f"   数据源: {data.get('source', '')}")
        else:
            print(f"❌ {code}: 获取失败")
            if data and 'error' in data:
                print(f"   错误: {data['error']}")
    
    # 测试大盘指数
    print(f"\n获取大盘指数...")
    market_data = fetcher.get_market_index()
    
    for name, data in market_data.items():
        if 'error' not in data:
            change_emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "🟡"
            print(f"{change_emoji} {name}: {data['price']} ({data['change_percent']:+.2f}%)")
        else:
            print(f"⚠️  {name}: 获取失败 - {data.get('error', '未知错误')}")
    
    print("\n" + "="*60)
    print("测试完成")
    
    return True

if __name__ == "__main__":
    test_real_time_data()