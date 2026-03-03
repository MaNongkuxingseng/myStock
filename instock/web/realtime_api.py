#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据Web API
为myStock系统提供实时数据接口
"""

import tornado.web
import tornado.ioloop
import json
from datetime import datetime

# 添加项目路径
import sys
import os
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

from instock.realtime import RealtimeDataManager, RealtimeAnalyzer

class RealtimeDataHandler(tornado.web.RequestHandler):
    """实时数据处理器"""
    
    def initialize(self):
        self.data_manager = RealtimeDataManager()
        self.analyzer = RealtimeAnalyzer(self.data_manager)
    
    def get(self):
        """获取实时数据"""
        stock_code = self.get_argument('code', '')
        action = self.get_argument('action', 'data')
        
        if not stock_code:
            self.write({'error': '股票代码不能为空'})
            return
        
        try:
            if action == 'data':
                # 获取实时数据
                data = self.data_manager.get_realtime_data(stock_code)
                if data:
                    self.write({
                        'success': True,
                        'data': data,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    self.write({'success': False, 'error': '获取数据失败'})
            
            elif action == 'signal':
                # 获取实时信号
                signal = self.data_manager.analyze_realtime_signal(stock_code)
                if signal:
                    self.write({
                        'success': True,
                        'signal': signal,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    self.write({'success': False, 'error': '分析信号失败'})
            
            elif action == 'history':
                # 获取历史实时数据
                limit = int(self.get_argument('limit', '10'))
                history = self.data_manager.get_latest_realtime(stock_code, limit)
                self.write({
                    'success': True,
                    'history': history,
                    'count': len(history)
                })
            
            else:
                self.write({'error': '不支持的操作类型'})
                
        except Exception as e:
            self.write({'error': str(e)})

class RealtimeReportHandler(tornado.web.RequestHandler):
    """实时报告处理器"""
    
    def initialize(self):
        self.data_manager = RealtimeDataManager()
        self.analyzer = RealtimeAnalyzer(self.data_manager)
    
    def get(self):
        """生成实时报告"""
        limit = int(self.get_argument('limit', '20'))
        
        try:
            # 获取股票列表
            stocks = self.data_manager.get_stock_list(limit=limit)
            stock_codes = [stock[0] for stock in stocks]
            
            # 这里可以调用analyzer生成报告
            # 简化版本：只返回股票列表和基本信息
            result = {
                'success': True,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'stocks': [],
                'total': len(stock_codes)
            }
            
            for code in stock_codes[:10]:  # 只处理前10只
                data = self.data_manager.get_realtime_data(code)
                if data:
                    result['stocks'].append({
                        'code': code,
                        'price': data.get('current', 0),
                        'change': data.get('change_percent', 0),
                        'volume': data.get('volume', 0)
                    })
            
            self.write(result)
            
        except Exception as e:
            self.write({'error': str(e)})

def make_app():
    """创建Tornado应用"""
    return tornado.web.Application([
        (r"/api/realtime/data", RealtimeDataHandler),
        (r"/api/realtime/report", RealtimeReportHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9999)
    print("实时数据API服务启动，端口: 9999")
    print("接口地址:")
    print("  GET /api/realtime/data?code=000034&action=data")
    print("  GET /api/realtime/data?code=000034&action=signal")
    print("  GET /api/realtime/data?code=000034&action=history&limit=10")
    print("  GET /api/realtime/report?limit=20")
    tornado.ioloop.IOLoop.current().start()
