#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock实时数据分析核心模块
"""

import pymysql
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import json

class RealTimeStockAnalyzer:
    """实时股票分析器"""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '785091',
            'database': 'instockdb',
            'charset': 'utf8mb4'
        }
        
    def connect_db(self):
        """连接数据库"""
        try:
            return pymysql.connect(**self.db_config)
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def get_latest_market_data(self):
        """获取最新市场数据"""
        try:
            conn = self.connect_db()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            # 获取最新日期
            cursor.execute("SELECT MAX(date) FROM cn_stock_selection")
            latest_date = cursor.fetchone()[0]
            
            # 获取市场概况
            query = f"""
            SELECT 
                COUNT(*) as total_stocks,
                AVG(change_rate) as avg_change_rate,
                SUM(CASE WHEN change_rate > 0 THEN 1 ELSE 0 END) as up_stocks,
                SUM(CASE WHEN change_rate < 0 THEN 1 ELSE 0 END) as down_stocks
            FROM cn_stock_selection 
            WHERE date = '{latest_date}'
            """
            
            cursor.execute(query)
            market_data = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'latest_date': latest_date,
                'total_stocks': market_data[0],
                'avg_change_rate': market_data[1],
                'up_stocks': market_data[2],
                'down_stocks': market_data[3]
            }
            
        except Exception as e:
            print(f"获取市场数据失败: {e}")
            return None
    
    def get_stock_realtime_data(self, stock_code):
        """获取股票实时数据（模拟）"""
        # 在实际应用中，这里应该调用实时数据API
        # 暂时使用模拟数据
        
        try:
            # 从数据库获取最新数据
            conn = self.connect_db()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            query = f"""
            SELECT 
                code, name, new_price, change_rate, volume_ratio, turnoverrate,
                industry, net_inflow, netinflow_3days,
                changerate_3days, changerate_5days, changerate_10days,
                pe9, pbnewmrq, roe_weight
            FROM cn_stock_selection 
            WHERE code = '{stock_code}'
            AND date = (SELECT MAX(date) FROM cn_stock_selection)
            """
            
            cursor.execute(query)
            data = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if data:
                return {
                    'code': data[0],
                    'name': data[1],
                    'price': data[2],
                    'change_rate': data[3],
                    'volume_ratio': data[4],
                    'turnoverrate': data[5],
                    'industry': data[6],
                    'net_inflow': data[7],
                    'netinflow_3days': data[8],
                    'changerate_3days': data[9],
                    'changerate_5days': data[10],
                    'changerate_10days': data[11],
                    'pe': data[12],
                    'pb': data[13],
                    'roe': data[14],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return None
    
    def analyze_stock_signal(self, stock_code):
        """分析股票信号"""
        data = self.get_stock_realtime_data(stock_code)
        if not data:
            return None
        
        # 计算信号强度
        score = 50  # 基础分
        
        # 涨跌幅评分
        if data['change_rate'] > 3:
            score += 20
        elif data['change_rate'] > 1:
            score += 10
        elif data['change_rate'] < -3:
            score -= 20
        elif data['change_rate'] < -1:
            score -= 10
        
        # 量比评分
        if data['volume_ratio'] > 2:
            score += 15
        elif data['volume_ratio'] > 1.5:
            score += 10
        
        # 资金流向评分
        if data['net_inflow'] > 0:
            score += 10
        if data['netinflow_3days'] > 0:
            score += 5
        
        # 累计涨幅评分
        if data['changerate_3days'] > 5:
            score += 10
        elif data['changerate_3days'] > 2:
            score += 5
        
        # 估值惩罚
        if data['pe'] and data['pe'] > 50:
            score -= 5
        if data['pb'] and data['pb'] > 5:
            score -= 3
        
        # 确定信号级别
        if score >= 70:
            signal = "强烈买入"
            level = "high"
        elif score >= 60:
            signal = "买入"
            level = "medium"
        elif score >= 50:
            signal = "观望"
            level = "neutral"
        elif score >= 40:
            signal = "谨慎"
            level = "caution"
        else:
            signal = "卖出"
            level = "sell"
        
        return {
            'code': data['code'],
            'name': data['name'],
            'price': data['price'],
            'change_rate': data['change_rate'],
            'score': score,
            'signal': signal,
            'level': level,
            'recommendation': self.generate_recommendation(data, score),
            'timestamp': data['timestamp']
        }
    
    def generate_recommendation(self, data, score):
        """生成操作建议"""
        price = data['price']
        
        if score >= 70:
            buy_price = price * 0.99
            stop_loss = price * 0.93
            target_price = price * 1.15
            return f"建议买入价位: {buy_price:.2f}元，止损: {stop_loss:.2f}元，目标: {target_price:.2f}元"
        
        elif score >= 60:
            buy_price = price * 0.97
            stop_loss = price * 0.92
            target_price = price * 1.12
            return f"可考虑在{buy_price:.2f}元附近买入，止损: {stop_loss:.2f}元"
        
        elif score >= 50:
            return "建议观望，等待明确信号"
        
        elif score >= 40:
            return "谨慎操作，控制仓位"
        
        else:
            return "考虑减仓或卖出"
    
    def get_top_signals(self, limit=10):
        """获取顶部信号股票"""
        try:
            conn = self.connect_db()
            if not conn:
                return []
            
            cursor = conn.cursor()
            
            # 获取最新日期
            cursor.execute("SELECT MAX(date) FROM cn_stock_selection")
            latest_date = cursor.fetchone()[0]
            
            # 查询强势股票
            query = f"""
            SELECT 
                code, name, new_price, change_rate, volume_ratio,
                net_inflow, industry
            FROM cn_stock_selection 
            WHERE date = '{latest_date}'
            AND change_rate > 0
            AND volume_ratio > 1.5
            ORDER BY change_rate DESC
            LIMIT {limit}
            """
            
            cursor.execute(query)
            stocks = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            results = []
            for stock in stocks:
                signal = self.analyze_stock_signal(stock[0])
                if signal:
                    results.append(signal)
            
            return results
            
        except Exception as e:
            print(f"获取顶部信号失败: {e}")
            return []
    
    def generate_realtime_report(self):
        """生成实时分析报告"""
        print("="*80)
        print("myStock实时数据分析报告")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 获取市场数据
        market_data = self.get_latest_market_data()
        if not market_data:
            print("无法获取市场数据")
            return
        
        print(f"\n市场概况 (数据日期: {market_data['latest_date']}):")
        print(f"  股票总数: {market_data['total_stocks']}")
        print(f"  平均涨跌幅: {market_data['avg_change_rate']:.2f}%")
        print(f"  上涨股票: {market_data['up_stocks']} ({market_data['up_stocks']/market_data['total_stocks']*100:.1f}%)")
        print(f"  下跌股票: {market_data['down_stocks']} ({market_data['down_stocks']/market_data['total_stocks']*100:.1f}%)")
        
        # 获取顶部信号
        print(f"\n强势信号股票:")
        top_signals = self.get_top_signals(5)
        
        for i, signal in enumerate(top_signals, 1):
            print(f"\n{i}. {signal['code']}/{signal['name']}")
            print(f"   价格: {signal['price']:.2f}元 ({signal['change_rate']:+.2f}%)")
            print(f"   信号: {signal['signal']} (评分: {signal['score']})")
            print(f"   建议: {signal['recommendation']}")
        
        # 分析重点股票
        print(f"\n重点股票分析:")
        focus_stocks = ['000034', '603949']  # 神州数码、雪龙集团
        
        for code in focus_stocks:
            signal = self.analyze_stock_signal(code)
            if signal:
                print(f"\n{signal['code']}/{signal['name']}:")
                print(f"  价格: {signal['price']:.2f}元 ({signal['change_rate']:+.2f}%)")
                print(f"  信号: {signal['signal']} (评分: {signal['score']})")
                print(f"  建议: {signal['recommendation']}")
            else:
                print(f"\n{code}: 无法获取数据")
        
        print(f"\n操作策略:")
        up_ratio = market_data['up_stocks'] / market_data['total_stocks']
        
        if up_ratio > 0.6:
            print("  市场整体强势，可积极操作")
        elif up_ratio > 0.4:
            print("  市场偏强，可选择性操作")
        elif up_ratio > 0.2:
            print("  市场中性，谨慎操作")
        else:
            print("  市场弱势，建议观望")
        
        print(f"\n风险提示:")
        print("  1. 以上分析基于历史数据，仅供参考")
        print("  2. 股市有风险，投资需谨慎")
        print("  3. 建议设置止损，控制仓位")

def main():
    """主函数"""
    analyzer = RealTimeStockAnalyzer()
    analyzer.generate_realtime_report()

if __name__ == "__main__":
    main()