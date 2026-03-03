#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock 实时数据模块
为现有系统添加实时数据分析能力
"""

import pymysql
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
import threading
import schedule
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class RealtimeDataManager:
    """实时数据管理器"""
    
    def __init__(self, db_config=None):
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': '785091',
            'database': 'instockdb',
            'port': 3306,
            'charset': 'utf8mb4'
        }
        
        # 实时数据API配置
        self.data_sources = {
            'sina': 'http://hq.sinajs.cn/list=',
            'tencent': 'http://qt.gtimg.cn/q=',
            'eastmoney': 'https://push2.eastmoney.com/api/qt/stock/get'
        }
        
        # 缓存实时数据
        self.realtime_cache = {}
        self.cache_timeout = 60  # 缓存超时时间（秒）
        
        print("✅ 实时数据管理器初始化完成")
    
    def connect_db(self):
        """连接数据库"""
        try:
            conn = pymysql.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return None
    
    def get_stock_list(self, limit=100):
        """获取股票列表"""
        try:
            conn = self.connect_db()
            if not conn:
                return []
            
            cursor = conn.cursor()
            query = """
            SELECT DISTINCT code, name, industry 
            FROM cn_stock_selection 
            WHERE date = (SELECT MAX(date) FROM cn_stock_selection)
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            stocks = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return stocks
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return []
    
    def fetch_realtime_from_sina(self, stock_code):
        """从新浪财经获取实时数据"""
        try:
            # 转换股票代码格式
            if stock_code.startswith('6'):
                market_code = f'sh{stock_code}'
            else:
                market_code = f'sz{stock_code}'
            
            url = f"{self.data_sources['sina']}{market_code}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                # 解析新浪数据格式
                content = response.text
                # 格式: var hq_str_sh000001="平安银行,10.88,10.87,10.88,10.91,10.84,10.88,10.89,...";
                if '="' in content:
                    data_str = content.split('="')[1].split('"')[0]
                    data_fields = data_str.split(',')
                    
                    if len(data_fields) >= 32:
                        return {
                            'code': stock_code,
                            'name': data_fields[0],
                            'open': float(data_fields[1]),
                            'pre_close': float(data_fields[2]),
                            'current': float(data_fields[3]),
                            'high': float(data_fields[4]),
                            'low': float(data_fields[5]),
                            'volume': int(data_fields[8]),
                            'amount': float(data_fields[9]),
                            'time': f"{data_fields[30]} {data_fields[31]}",
                            'source': 'sina'
                        }
            
            return None
        except Exception as e:
            print(f"❌ 获取新浪实时数据失败({stock_code}): {e}")
            return None
    
    def fetch_realtime_from_tencent(self, stock_code):
        """从腾讯财经获取实时数据"""
        try:
            # 转换股票代码格式
            if stock_code.startswith('6'):
                market_code = f'sh{stock_code}'
            else:
                market_code = f'sz{stock_code}'
            
            url = f"{self.data_sources['tencent']}{market_code}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                content = response.text
                # 格式: v_sh000001="1~平安银行~000001~10.88~10.87~10.88~...";
                if '="' in content:
                    data_str = content.split('="')[1].split('"')[0]
                    data_fields = data_str.split('~')
                    
                    if len(data_fields) >= 40:
                        return {
                            'code': stock_code,
                            'name': data_fields[1],
                            'current': float(data_fields[3]),
                            'change': float(data_fields[4]) - float(data_fields[3]),
                            'change_percent': (float(data_fields[4]) - float(data_fields[3])) / float(data_fields[3]) * 100,
                            'open': float(data_fields[5]),
                            'pre_close': float(data_fields[4]),
                            'high': float(data_fields[33]),
                            'low': float(data_fields[34]),
                            'volume': int(data_fields[36]),
                            'amount': float(data_fields[37]),
                            'time': data_fields[30],
                            'source': 'tencent'
                        }
            
            return None
        except Exception as e:
            print(f"❌ 获取腾讯实时数据失败({stock_code}): {e}")
            return None
    
    def get_realtime_data(self, stock_code, use_cache=True):
        """获取股票实时数据"""
        cache_key = f"{stock_code}_{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # 检查缓存
        if use_cache and cache_key in self.realtime_cache:
            cached_data = self.realtime_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_timeout:
                return cached_data['data']
        
        # 尝试多个数据源
        data = None
        
        # 先尝试新浪
        data = self.fetch_realtime_from_sina(stock_code)
        
        # 如果新浪失败，尝试腾讯
        if not data:
            data = self.fetch_realtime_from_tencent(stock_code)
        
        # 更新缓存
        if data:
            self.realtime_cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
        
        return data
    
    def batch_get_realtime(self, stock_codes, max_workers=5):
        """批量获取实时数据"""
        results = {}
        
        for code in stock_codes:
            try:
                data = self.get_realtime_data(code)
                if data:
                    results[code] = data
                time.sleep(0.1)  # 避免请求过快
            except Exception as e:
                print(f"❌ 获取{code}实时数据失败: {e}")
        
        return results
    
    def create_realtime_table(self):
        """创建实时数据表"""
        try:
            conn = self.connect_db()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # 创建实时数据表
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS cn_stock_realtime (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                stock_code VARCHAR(10) NOT NULL,
                stock_name VARCHAR(50),
                current_price DECIMAL(10,2),
                change_amount DECIMAL(10,2),
                change_percent DECIMAL(10,2),
                open_price DECIMAL(10,2),
                pre_close DECIMAL(10,2),
                high_price DECIMAL(10,2),
                low_price DECIMAL(10,2),
                volume BIGINT,
                amount DECIMAL(15,2),
                timestamp DATETIME NOT NULL,
                data_source VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_stock_code (stock_code),
                INDEX idx_timestamp (timestamp),
                INDEX idx_stock_timestamp (stock_code, timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            
            print("✅ 实时数据表创建/检查完成")
            
            cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            print(f"❌ 创建实时数据表失败: {e}")
            return False
    
    def save_realtime_data(self, realtime_data):
        """保存实时数据到数据库"""
        try:
            conn = self.connect_db()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            insert_sql = """
            INSERT INTO cn_stock_realtime 
            (stock_code, stock_name, current_price, change_amount, change_percent, 
             open_price, pre_close, high_price, low_price, volume, amount, 
             timestamp, data_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            current_time = datetime.now()
            
            cursor.execute(insert_sql, (
                realtime_data.get('code'),
                realtime_data.get('name'),
                realtime_data.get('current'),
                realtime_data.get('change', 0),
                realtime_data.get('change_percent', 0),
                realtime_data.get('open'),
                realtime_data.get('pre_close'),
                realtime_data.get('high'),
                realtime_data.get('low'),
                realtime_data.get('volume', 0),
                realtime_data.get('amount', 0),
                current_time,
                realtime_data.get('source', 'unknown')
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            print(f"❌ 保存实时数据失败: {e}")
            return False
    
    def get_latest_realtime(self, stock_code, limit=10):
        """获取最新实时数据"""
        try:
            conn = self.connect_db()
            if not conn:
                return []
            
            cursor = conn.cursor()
            
            query = """
            SELECT * FROM cn_stock_realtime 
            WHERE stock_code = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
            """
            
            cursor.execute(query, (stock_code, limit))
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            conn.close()
            
            return results
        except Exception as e:
            print(f"❌ 获取最新实时数据失败: {e}")
            return []
    
    def analyze_realtime_signal(self, stock_code, history_days=5):
        """分析实时信号"""
        try:
            # 获取实时数据
            realtime_data = self.get_realtime_data(stock_code)
            if not realtime_data:
                return None
            
            # 获取历史数据
            conn = self.connect_db()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            # 查询历史数据
            history_query = """
            SELECT date, new_price, change_rate, volume_ratio, net_inflow
            FROM cn_stock_selection 
            WHERE code = %s 
            AND date >= DATE_SUB(%s, INTERVAL %s DAY)
            ORDER BY date DESC
            """
            
            cursor.execute(history_query, (stock_code, datetime.now().date(), history_days))
            history_data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # 分析信号
            signal = {
                'code': stock_code,
                'name': realtime_data.get('name', ''),
                'current_price': realtime_data.get('current', 0),
                'change_percent': realtime_data.get('change_percent', 0),
                'volume': realtime_data.get('volume', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'signals': [],
                'recommendation': '观望',
                'confidence': 0
            }
            
            # 价格突破分析
            if history_data:
                recent_prices = [row[1] for row in history_data[:3] if row[1]]
                if recent_prices:
                    avg_price = sum(recent_prices) / len(recent_prices)
                    if realtime_data.get('current', 0) > avg_price * 1.02:
                        signal['signals'].append('突破近期均价')
                        signal['confidence'] += 20
            
            # 成交量分析
            if realtime_data.get('volume', 0) > 1000000:  # 成交量大于100万
                signal['signals'].append('放量')
                signal['confidence'] += 15
            
            # 涨跌幅分析
            change_percent = realtime_data.get('change_percent', 0)
            if change_percent > 3:
                signal['signals'].append('强势上涨')
                signal['confidence'] += 25
            elif change_percent < -3:
                signal['signals'].append('弱势下跌')
                signal['confidence'] -= 20
            
            # 生成建议
            if signal['confidence'] >= 40:
                signal['recommendation'] = '买入'
            elif signal['confidence'] >= 20:
                signal['recommendation'] = '关注'
            elif signal['confidence'] <= -20:
                signal['recommendation'] = '卖出'
            else:
                signal['recommendation'] = '观望'
            
            return signal
            
        except Exception as e:
            print(f"❌ 分析实时信号失败: {e}")
            return None
    
    def start_realtime_monitor(self, stock_codes, interval=60):
        """启动实时监控"""
        print(f"🚀 启动实时监控，监控{len(stock_codes)}只股票，间隔{interval}秒")
        
        def monitor_task():
            print(f"\n📊 实时监控更新 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            for code in stock_codes:
                try:
                    # 获取实时数据
                    data = self.get_realtime_data(code, use_cache=False)
                    if data:
                        # 保存到数据库
                        self.save_realtime_data(data)
                        
                        # 分析信号
                        signal = self.analyze_realtime_signal(code)
                        if signal and signal['confidence'] >= 30:
                            print(f"  🔔 {code}: {signal['recommendation']} (信心度: {signal['confidence']})")
                    
                    time.sleep(0.5)  # 避免请求过快
                except Exception as e:
                    print(f"  ❌ 监控{code}失败: {e}")
        
        # 立即执行一次
        monitor_task()
        
        # 定时执行
        schedule.every(interval).seconds.do(monitor_task)
        
        print("✅ 实时监控已启动，按Ctrl+C停止")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 实时监控已停止")

class RealtimeAnalyzer:
    """实时分析器"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def generate_realtime_report(self, stock_codes=None):
        """生成实时分析报告"""
        print("="*80)
        print("myStock 实时分析报告")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 如果没有指定股票，获取关注的股票
        if not stock_codes:
            stocks = self.data_manager.get_stock_list(limit=20)
            stock_codes = [stock[0] for stock in stocks]
        
        print(f"\n📊 分析{len(stock_codes)}只股票:")
        
        strong_signals = []
        weak_signals = []
        
        for code in stock_codes:
            try:
                signal = self.data_manager.analyze_realtime_signal(code)
                if signal:
                    if signal['confidence'] >= 30:
                        strong_signals.append(signal)
                    elif signal['confidence'] <= -20:
                        weak_signals.append(signal)
            except Exception as e:
                print(f"  ❌ 分析{code}失败: {e}")
        
        # 输出强烈信号
        if strong_signals:
            print(f"\n🎯 强烈信号 ({len(strong_signals)}只):")
            for signal in sorted(strong_signals, key=lambda x: x['confidence'], reverse=True)[:5]:
                print(f"  🟢 {signal['code']}/{signal['name']}: {signal['current_price']:.2f}元")
                print(f"     涨跌幅: {signal['change_percent']:.2f}%, 信心度: {signal['confidence']}")
                print(f"     信号: {', '.join(signal['signals'])}")
                print(f"     建议: {signal['recommendation']}")
        
        # 输出弱势信号
        if weak_signals:
            print(f"\n⚠️ 弱势信号 ({len(weak_signals)}只):")
            for signal in sorted(weak_signals, key=lambda x: x['confidence'])[:3]:
                print(f"  🔴 {signal['code']}/{signal['name']}: {signal['current_price']:.2f}元")
                print(f"     涨跌幅: {signal['change_percent']:.2f}%, 信心度: {signal['confidence']}")
                print(f"     建议: {signal['recommendation']}")
        
        print(f"\n📈 市场实时状态:")
        print(f"  分析时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"  强烈信号: {len(strong_signals)}只")
        print(f"  弱势信号: {len(weak_signals)}只")
        
        if len(strong_signals) > len(weak_signals) * 2:
            print(f"  🟢 市场情绪: 积极")
        elif len(strong_signals) > len(weak_signals):
            print(f"  🟡 市场情绪: 偏积极")
        elif len(strong_signals) == len(weak_signals):
            print(f"  ⚪ 市场情绪: 中性")
        else:
            print(f"  🔴 市场情绪: 谨慎")
        
        print(f"\n💡 操作建议:")
        if strong_signals:
            print(f"  1. 关注强烈信号股票")
            print(f"  2. 设置合理止损")
            print(f"  3. 控制仓位风险")
        else:
            print(f"  1. 市场信号不明，建议观望")
            print(f"  2. 等待明确方向")
            print(f"  3. 关注资金流向")
        
        print(f"\n⚠️ 风险提示:")
        print(f"  1. 实时数据有延迟，仅供参考")
        print(f"  2. 股市有风险，投资需谨慎")
        print(f"  3. 建议结合其他分析工具")

def main():
    """主函数"""
    print("="*80)
    print("myStock 实时数据分析系统")
    print("="*80)
    
    # 初始化数据管理器
    data_manager = RealtimeDataManager()
    
    # 创建实时数据表
    print("\n1. 检查实时数据表...")
    data_manager.create_realtime_table()
    
    # 获取关注的股票
    print("\n2. 获取关注股票列表...")
    stocks = data_manager.get_stock_list(limit=50)
    
    if not stocks:
        print("❌ 未找到股票数据，请先运行myStock数据更新")
        return
    
    stock_codes = [stock[0] for stock in stocks]
    print(f"✅ 获取到{len(stock_codes)}只股票")
    
    # 创建分析器
    analyzer = RealtimeAnalyzer(data_manager)
    
    # 生成实时报告
    print("\n3. 生成实时分析报告...")
    analyzer.generate_realtime_report(stock_codes[:10])  # 只分析前10只
    
    print("\n4. 测试实时数据获取...")
    test_codes = ['000034', '603949']  # 神州数码和雪龙集团
    for code in test_codes:
        data = data_manager.get_realtime_data(code)
        if data:
            print(f"  ✅ {code}: {data.get('current', 0):.2f}元 ({data.get('change_percent', 0):.2f}%)")
        else:
            print(f"  ❌ {code}: 获取实时数据失败")
    
    print(f"\n🎯 系统优化完成!")
    print(f"   实时数据模块已集成到myStock系统")
    print(f"   支持功能:")
    print(f"     - 实时数据获取（新浪/腾讯）")
    print(f"     - 实时信号分析")
    print(f"     - 实时数据存储")
    print(f"     - 实时监控")
    
    print(f"\n🚀 使用说明:")
    print(f"   1. 运行实时监控: python realtime_module.py --monitor")
    print(f"   2. 生成实时报告: python realtime_module.py --report")
    print(f"   3. 更新实时数据: python realtime_module.py --update")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='myStock实时数据分析系统')
    parser.add_argument('--monitor', action='store_true', help='启动实时监控')
    parser.add_argument('--report', action='store_true', help='生成实时报告')
    parser.add_argument('--update', action='store_true', help='更新实时数据')
    parser.add_argument('--codes', type=str, help='指定股票代码，用逗号分隔')
    
    args = parser.parse_args()
    
    if args.monitor:
        # 启动监控
        data_manager = RealtimeDataManager()
        data_manager.create_realtime_table()
        
        if args.codes:
            stock_codes = args.codes.split(',')
        else:
            stocks = data_manager.get_stock_list(limit=20)
            stock_codes = [stock[0] for stock in stocks]
        
        data_manager.start_realtime_monitor(stock_codes, interval=60)
    elif args.report:
        # 生成报告
        data_manager = RealtimeDataManager()
        analyzer = RealtimeAnalyzer(data_manager)
        
        if args.codes:
            stock_codes = args.codes.split(',')
        else:
            stocks = data_manager.get_stock_list(limit=20)
            stock_codes = [stock[0] for stock in stocks]
        
        analyzer.generate_realtime_report(stock_codes)
    elif args.update:
        # 更新数据
        data_manager = RealtimeDataManager()
        data_manager.create_realtime_table()
        
        if args.codes:
            stock_codes = args.codes.split(',')
        else:
            stocks = data_manager.get_stock_list(limit=50)
            stock_codes = [stock[0] for stock in stocks]
        
        print(f"更新{len(stock_codes)}只股票的实时数据...")
        for code in stock_codes:
            data = data_manager.get_realtime_data(code, use_cache=False)
            if data:
                data_manager.save_realtime_data(data)
                print(f"  ✅ {code}: 更新成功")
            else:
                print(f"  ❌ {code}: 更新失败")
    else:
        # 默认运行主函数
        main()