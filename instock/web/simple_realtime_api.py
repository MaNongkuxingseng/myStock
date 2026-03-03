#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单实时数据API服务
启动在 http://localhost:9999/
"""

import tornado.web
import tornado.ioloop
import json
from datetime import datetime
import pymysql

class SimpleRealtimeAPI:
    """简单实时API"""
    
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
    
    def get_stock_data(self, stock_code):
        """获取股票数据"""
        try:
            conn = self.connect_db()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            query = f"""
            SELECT 
                code, name, new_price, change_rate, volume_ratio, turnoverrate,
                industry, net_inflow
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
                    'price': float(data[2]),
                    'change_rate': float(data[3]),
                    'volume_ratio': float(data[4]),
                    'turnoverrate': float(data[5]),
                    'industry': data[6],
                    'net_inflow': float(data[7]) if data[7] else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return None
    
    def get_market_overview(self):
        """获取市场概况"""
        try:
            conn = self.connect_db()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            # 获取最新日期
            cursor.execute("SELECT MAX(date) FROM cn_stock_selection")
            latest_date = cursor.fetchone()[0]
            
            # 获取市场数据
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
            data = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if data:
                return {
                    'latest_date': str(latest_date),
                    'total_stocks': data[0],
                    'avg_change_rate': float(data[1]),
                    'up_stocks': data[2],
                    'down_stocks': data[3],
                    'up_ratio': data[2]/data[0]*100 if data[0] > 0 else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"获取市场概况失败: {e}")
            return None

class StockDataHandler(tornado.web.RequestHandler):
    """股票数据处理器"""
    
    def initialize(self):
        self.api = SimpleRealtimeAPI()
    
    def get(self):
        """处理GET请求"""
        stock_code = self.get_argument('code', '')
        action = self.get_argument('action', 'data')
        
        if action == 'data':
            if not stock_code:
                self.write({'error': '请提供股票代码参数: ?code=000034'})
                return
            
            data = self.api.get_stock_data(stock_code)
            if data:
                self.write({
                    'success': True,
                    'data': data
                })
            else:
                self.write({
                    'success': False,
                    'error': f'未找到股票 {stock_code} 的数据'
                })
        
        elif action == 'market':
            data = self.api.get_market_overview()
            if data:
                self.write({
                    'success': True,
                    'data': data
                })
            else:
                self.write({
                    'success': False,
                    'error': '获取市场数据失败'
                })
        
        else:
            self.write({
                'error': '不支持的操作类型',
                'supported_actions': ['data', 'market']
            })

class HomeHandler(tornado.web.RequestHandler):
    """首页处理器"""
    
    def get(self):
        """显示API使用说明"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>myStock 实时数据API</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                code { background: #eee; padding: 2px 5px; border-radius: 3px; }
                .success { color: green; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>myStock 实时数据API</h1>
            <p>服务已启动，当前时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            
            <h2>API端点</h2>
            
            <div class="endpoint">
                <h3>1. 获取股票数据</h3>
                <p><code>GET /api/stock?code=000034&action=data</code></p>
                <p>参数: <code>code</code> - 股票代码 (如: 000034)</p>
                <p>示例: <a href="/api/stock?code=000034&action=data" target="_blank">/api/stock?code=000034&action=data</a></p>
            </div>
            
            <div class="endpoint">
                <h3>2. 获取市场概况</h3>
                <p><code>GET /api/stock?action=market</code></p>
                <p>示例: <a href="/api/stock?action=market" target="_blank">/api/stock?action=market</a></p>
            </div>
            
            <div class="endpoint">
                <h3>3. 测试股票</h3>
                <ul>
                    <li><a href="/api/stock?code=000034&action=data" target="_blank">神州数码 (000034)</a></li>
                    <li><a href="/api/stock?code=603949&action=data" target="_blank">雪龙集团 (603949)</a></li>
                    <li><a href="/api/stock?code=000001&action=data" target="_blank">平安银行 (000001)</a></li>
                </ul>
            </div>
            
            <h2>响应格式</h2>
            <pre>
{
    "success": true,
    "data": {
        "code": "000034",
        "name": "神州数码",
        "price": 40.30,
        "change_rate": -0.81,
        "volume_ratio": 5.40,
        "timestamp": "2026-03-02 11:00:00"
    }
}
            </pre>
            
            <h2>状态</h2>
            <p class="success">✅ 服务运行正常</p>
            <p>端口: 9999</p>
            <p>启动时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </body>
        </html>
        """
        self.write(html)

def make_app():
    """创建Tornado应用"""
    return tornado.web.Application([
        (r"/", HomeHandler),
        (r"/api/stock", StockDataHandler),
    ])

def main():
    """主函数"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("="*80)
    print("myStock 实时数据API服务")
    print("启动在: http://localhost:9999/")
    print("="*80)
    
    # 创建应用
    app = make_app()
    
    # 启动服务
    try:
        app.listen(9999)
        print("[成功] 服务启动成功!")
        print("\n[接口] 可用接口:")
        print("  1. 首页: http://localhost:9999/")
        print("  2. 股票数据: http://localhost:9999/api/stock?code=000034&action=data")
        print("  3. 市场概况: http://localhost:9999/api/stock?action=market")
        print("\n[测试] 测试链接:")
        print("  - 神州数码: http://localhost:9999/api/stock?code=000034&action=data")
        print("  - 雪龙集团: http://localhost:9999/api/stock?code=603949&action=data")
        print("  - 市场概况: http://localhost:9999/api/stock?action=market")
        print("\n[操作] 按 Ctrl+C 停止服务")
        
        # 启动事件循环
        tornado.ioloop.IOLoop.current().start()
        
    except Exception as e:
        print(f"[错误] 服务启动失败: {e}")
        print("可能的原因:")
        print("  1. 端口9999已被占用")
        print("  2. 数据库连接失败")
        print("  3. 依赖库未安装")
        print("\n解决方法:")
        print("  1. 检查端口: netstat -ano | findstr :9999")
        print("  2. 检查数据库: python -c \"import pymysql; print('pymysql已安装')\"")
        print("  3. 安装依赖: pip install tornado pymysql")

if __name__ == "__main__":
    main()