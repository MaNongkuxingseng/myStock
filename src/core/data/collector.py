"""
myStock 1.1版本 - 数据采集模块
负责从各种数据源采集股票数据
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

import requests
import pandas as pd
from ..utils.helpers import Timer, validate_stock_code

logger = logging.getLogger("mystock.collector")

class DataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def fetch_stock_data(self, stock_code: str, 
                        start_date: str, 
                        end_date: str) -> Optional[pd.DataFrame]:
        """获取股票历史数据"""
        pass
    
    @abstractmethod
    def fetch_realtime_data(self, stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """获取股票实时数据"""
        pass
    
    @abstractmethod
    def fetch_market_data(self) -> Dict[str, Any]:
        """获取市场整体数据"""
        pass

class MockDataSource(DataSource):
    """模拟数据源（用于开发和测试）"""
    
    def __init__(self):
        self._cache = {}
        logger.info("初始化模拟数据源")
    
    def fetch_stock_data(self, stock_code: str, 
                        start_date: str, 
                        end_date: str) -> Optional[pd.DataFrame]:
        """模拟获取股票历史数据"""
        if not validate_stock_code(stock_code):
            logger.error(f"无效的股票代码: {stock_code}")
            return None
        
        with Timer(f"模拟获取历史数据: {stock_code}"):
            # 生成模拟数据
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            data = {
                'date': dates,
                'open': [10.0 + i * 0.1 for i in range(len(dates))],
                'high': [10.5 + i * 0.1 for i in range(len(dates))],
                'low': [9.5 + i * 0.1 for i in range(len(dates))],
                'close': [10.2 + i * 0.1 for i in range(len(dates))],
                'volume': [1000000 + i * 10000 for i in range(len(dates))],
                'amount': [10000000 + i * 100000 for i in range(len(dates))]
            }
            
            df = pd.DataFrame(data)
            df['stock_code'] = stock_code
            df['data_source'] = 'mock'
            
            logger.info(f"模拟历史数据生成完成: {stock_code} - 数据量: {len(df)}行")
            return df
    
    def fetch_realtime_data(self, stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """模拟获取股票实时数据"""
        with Timer(f"模拟获取实时数据: {len(stock_codes)}只股票"):
            result = {}
            
            for code in stock_codes:
                if not validate_stock_code(code):
                    logger.warning(f"跳过无效股票代码: {code}")
                    continue
                
                # 生成模拟实时数据
                result[code] = {
                    'name': f"股票{code}",
                    'current_price': 10.0 + hash(code) % 100 / 10,  # 模拟价格
                    'change': (hash(code) % 20 - 10) / 10,  # 模拟涨跌
                    'change_percent': (hash(code) % 20 - 10) / 100,  # 模拟涨跌幅
                    'volume': 1000000 + hash(code) % 1000000,
                    'amount': 10000000 + hash(code) % 10000000,
                    'high': 10.5 + hash(code) % 100 / 10,
                    'low': 9.5 + hash(code) % 100 / 10,
                    'open': 10.0 + hash(code) % 100 / 10,
                    'prev_close': 10.0 + hash(code) % 100 / 10,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            logger.info(f"模拟实时数据生成完成: {len(result)}只股票")
            return result
    
    def fetch_market_data(self) -> Dict[str, Any]:
        """模拟获取市场数据"""
        with Timer("模拟获取市场数据"):
            market_data = {
                'shanghai_index': {
                    'current': 3000 + hash('sh') % 100,
                    'change': (hash('sh') % 20 - 10),
                    'change_percent': (hash('sh') % 20 - 10) / 100,
                    'volume': 1000000000 + hash('sh') % 1000000000,
                    'amount': 10000000000 + hash('sh') % 10000000000
                },
                'shenzhen_index': {
                    'current': 10000 + hash('sz') % 1000,
                    'change': (hash('sz') % 50 - 25),
                    'change_percent': (hash('sz') % 50 - 25) / 100,
                    'volume': 800000000 + hash('sz') % 800000000,
                    'amount': 8000000000 + hash('sz') % 8000000000
                },
                'chinese_index': {
                    'current': 2000 + hash('cy') % 100,
                    'change': (hash('cy') % 30 - 15),
                    'change_percent': (hash('cy') % 30 - 15) / 100,
                    'volume': 500000000 + hash('cy') % 500000000,
                    'amount': 5000000000 + hash('cy') % 5000000000
                },
                'total_stocks': 5000,
                'rising_stocks': 2500 + hash('rise') % 1000,
                'falling_stocks': 1500 + hash('fall') % 1000,
                'unchanged_stocks': 1000,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info("模拟市场数据生成完成")
            return market_data

class DataCollector:
    """数据采集器"""
    
    def __init__(self, data_source: Optional[DataSource] = None):
        self.data_source = data_source or MockDataSource()
        self._cache = {}
        self._cache_ttl = 300  # 5分钟缓存
        logger.info("数据采集器初始化完成")
    
    def get_stock_history(self, stock_code: str, 
                         days: int = 30,
                         use_cache: bool = True) -> Optional[pd.DataFrame]:
        """获取股票历史数据"""
        cache_key = f"history_{stock_code}_{days}"
        
        # 检查缓存
        if use_cache and cache_key in self._cache:
            cache_data, cache_time = self._cache[cache_key]
            if time.time() - cache_time < self._cache_ttl:
                logger.debug(f"使用缓存数据: {stock_code} ({days}天)")
                return cache_data
        
        # 计算日期范围
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 获取数据
        with Timer(f"采集股票历史数据: {stock_code}"):
            data = self.data_source.fetch_stock_data(stock_code, start_date, end_date)
            
            if data is not None:
                # 更新缓存
                self._cache[cache_key] = (data, time.time())
                logger.info(f"股票历史数据采集完成: {stock_code} - 数据量: {len(data)}行")
            else:
                logger.warning(f"股票历史数据采集失败: {stock_code}")
            
            return data
    
    def get_realtime_quotes(self, stock_codes: List[str],
                           use_cache: bool = True) -> Dict[str, Dict[str, Any]]:
        """获取实时行情"""
        cache_key = f"realtime_{hash(tuple(sorted(stock_codes)))}"
        
        # 检查缓存
        if use_cache and cache_key in self._cache:
            cache_data, cache_time = self._cache[cache_key]
            if time.time() - cache_time < 60:  # 实时数据缓存1分钟
                logger.debug(f"使用缓存实时数据: {len(stock_codes)}只股票")
                return cache_data
        
        # 获取数据
        with Timer(f"采集实时行情: {len(stock_codes)}只股票"):
            data = self.data_source.fetch_realtime_data(stock_codes)
            
            if data:
                # 更新缓存
                self._cache[cache_key] = (data, time.time())
                logger.info(f"实时行情采集完成: {len(data)}只股票")
            else:
                logger.warning("实时行情采集失败")
            
            return data or {}
    
    def get_market_overview(self, use_cache: bool = True) -> Dict[str, Any]:
        """获取市场概览"""
        cache_key = "market_overview"
        
        # 检查缓存
        if use_cache and cache_key in self._cache:
            cache_data, cache_time = self._cache[cache_key]
            if time.time() - cache_time < 60:  # 市场数据缓存1分钟
                logger.debug("使用缓存市场数据")
                return cache_data
        
        # 获取数据
        with Timer("采集市场概览数据"):
            data = self.data_source.fetch_market_data()
            
            if data:
                # 更新缓存
                self._cache[cache_key] = (data, time.time())
                logger.info("市场概览数据采集完成")
            else:
                logger.warning("市场概览数据采集失败")
            
            return data or {}
    
    def get_watchlist_data(self, watchlist: List[str]) -> Dict[str, Any]:
        """获取自选股数据"""
        with Timer(f"采集自选股数据: {len(watchlist)}只股票"):
            # 获取实时行情
            realtime_data = self.get_realtime_quotes(watchlist)
            
            # 获取市场数据
            market_data = self.get_market_overview()
            
            # 组合结果
            result = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'stock_count': len(watchlist),
                'valid_stocks': len(realtime_data),
                'stocks': realtime_data,
                'market': market_data,
                'summary': {
                    'total_change': sum(data.get('change', 0) for data in realtime_data.values()),
                    'avg_change_percent': sum(data.get('change_percent', 0) for data in realtime_data.values()) / len(realtime_data) if realtime_data else 0,
                    'rising_count': sum(1 for data in realtime_data.values() if data.get('change', 0) > 0),
                    'falling_count': sum(1 for data in realtime_data.values() if data.get('change', 0) < 0)
                }
            }
            
            logger.info(f"自选股数据采集完成: {len(realtime_data)}只有效股票")
            return result
    
    def clear_cache(self):
        """清空缓存"""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"缓存已清空，原缓存条目: {cache_size}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        now = time.time()
        cache_info = {
            'total_entries': len(self._cache),
            'expired_entries': 0,
            'memory_usage': 0,  # 简化版本，实际可以计算内存使用
            'entries': []
        }
        
        for key, (data, cache_time) in self._cache.items():
            age = now - cache_time
            is_expired = age > self._cache_ttl
            
            cache_info['entries'].append({
                'key': key[:50] + '...' if len(key) > 50 else key,
                'age_seconds': round(age, 2),
                'expired': is_expired,
                'data_type': type(data).__name__
            })
            
            if is_expired:
                cache_info['expired_entries'] += 1
        
        return cache_info

# 全局数据采集器实例
data_collector = DataCollector()

def init_data_collector(data_source: Optional[DataSource] = None):
    """初始化数据采集器"""
    global data_collector
    data_collector = DataCollector(data_source)
    logger.info("数据采集器初始化完成")
    return data_collector

if __name__ == "__main__":
    # 测试数据采集模块
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    print("=== 数据采集模块测试 ===")
    
    # 初始化
    collector = init_data_collector()
    
    # 测试股票代码验证
    test_codes = ["000001", "600000", "123456"]
    print(f"股票代码验证测试: {test_codes}")
    for code in test_codes:
        valid = validate_stock_code(code)
        print(f"  {code}: {'有效' if valid else '无效'}")
    
    # 测试获取历史数据
    print("\n测试获取历史数据...")
    history_data = collector.get_stock_history("000001", days=5)
    if history_data is not None:
        print(f"历史数据获取成功，数据形状: {history_data.shape}")
        print(f"列名: {list(history_data.columns)}")
        print(f"前3行数据:")
        print(history_data.head(3).to_string())
    else:
        print("历史数据获取失败")
    
    # 测试获取实时数据
    print("\n测试获取实时数据...")
    realtime_data = collector.get_realtime_quotes(["000001", "600000"])
    print(f"实时数据获取成功，股票数量: {len(realtime_data)}")
    for code, data in realtime_data.items():
        print(f"  {code}: 价格={data.get('current_price')}, 涨跌={data.get('change')}")
    
    # 测试获取市场数据
    print("\n测试获取市场数据...")
    market_data = collector.get_market_overview()
    print(f"市场数据获取成功")
    print(f"  上证指数: {market_data.get('shanghai_index', {}).get('current')}")
    print(f"  深证成指: {market_data.get('shenzhen_index', {}).get('current')}")
    print(f"  创业板指: {market_data.get('chinese_index', {}).get('current')}")
    
    # 测试缓存信息
    print("\n测试缓存信息...")
    cache_info = collector.get_cache_info()
    print(f"缓存条目总数: {cache_info['total_entries']}")
    print(f"过期条目数: {cache_info['expired_entries']}")
    
    print("\n" + "=" * 40)