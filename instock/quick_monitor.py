#!/usr/bin/env python3
"""
快速监控 - 单次检查并推送提醒
"""

import sys
import os
sys.path.append('D:\\python_libs')

import json
from datetime import datetime
from real_time_data import RealTimeDataFetcher

def send_feishu_alert(message):
    """发送Feishu警报"""
    print("="*60)
    print("发送Feishu警报:")
    print("="*60)
    print(message)
    print("="*60)
    return True

def quick_monitor():
    """快速监控检查"""
    config_path = os.path.join(os.path.dirname(__file__), "price_monitor_config.json")
    
    if not os.path.exists(config_path):
        print("配置文件不存在")
        return
    
    # 加载配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("myStock真实行情监控系统启动")
    print("="*50)
    print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"监控股票: {len(config['monitored_stocks'])}只")
    print("="*50)
    
    # 初始化数据获取器
    fetcher = RealTimeDataFetcher()
    
    # 获取大盘数据
    print("\n大盘指数:")
    market_data = fetcher.get_market_index()
    
    market_report = []
    for name, data in market_data.items():
        if 'error' not in data:
            change = data['change_percent']
            if change > 0:
                status = "上涨"
                emoji = "[涨]"
            elif change < 0:
                status = "下跌"
                emoji = "[跌]"
            else:
                status = "平盘"
                emoji = "[平]"
            
            print(f"  {name}: {data['price']} ({change:+.2f}%) {status}")
            market_report.append(f"{name}: {data['price']} ({change:+.2f}%)")
    
    # 检查股票
    print("\n持仓监控:")
    alerts = []
    
    for stock in config['monitored_stocks']:
        code = stock['code']
        name = stock['name']
        rules = stock['monitor_rules']
        
        # 获取真实价格
        data = fetcher.get_stock_data(code, fallback=True)
        
        if data and 'error' not in data:
            current_price = data['price']
            change = data['change_percent']
            
            # 显示状态
            if change > 0:
                trend = "上涨"
                symbol = "[涨]"
            elif change < 0:
                trend = "下跌"
                symbol = "[跌]"
            else:
                trend = "平盘"
                symbol = "[平]"
            
            print(f"  {code} {name}: {current_price}元 ({change:+.2f}%) {trend}")
            
            # 检查警报
            # 止损检查
            if 'stop_loss' in rules and current_price <= rules['stop_loss']:
                alerts.append({
                    'level': 'critical',
                    'stock': f"{code} {name}",
                    'message': f"触发止损位 {rules['stop_loss']}元",
                    'price': current_price,
                    'change': change
                })
            
            # 买入机会检查
            if 'buy_alert' in rules and current_price <= rules['buy_alert']:
                alerts.append({
                    'level': 'warning',
                    'stock': f"{code} {name}",
                    'message': f"达到买入价 {rules['buy_alert']}元",
                    'price': current_price,
                    'change': change
                })
            
            # 目标价检查
            if 'sell_alert' in rules and current_price >= rules['sell_alert']:
                alerts.append({
                    'level': 'warning',
                    'stock': f"{code} {name}",
                    'message': f"达到目标价 {rules['sell_alert']}元",
                    'price': current_price,
                    'change': change
                })
            
            # 涨跌幅检查
            if 'change_threshold' in rules and abs(change) >= rules['change_threshold']:
                alerts.append({
                    'level': 'info',
                    'stock': f"{code} {name}",
                    'message': f"涨跌幅 {abs(change):.1f}% 超过阈值",
                    'price': current_price,
                    'change': change
                })
                
        else:
            print(f"  {code} {name}: 获取失败")
    
    # 发送警报
    if alerts:
        print(f"\n发现 {len(alerts)} 个警报:")
        
        # 按级别排序
        level_order = {'critical': 3, 'warning': 2, 'info': 1}
        alerts.sort(key=lambda x: level_order.get(x['level'], 0), reverse=True)
        
        # 发送最重要的警报
        alert = alerts[0]
        
        # 构建消息
        if alert['level'] == 'critical':
            level_text = "严重警报"
            emoji = "[紧急]"
        elif alert['level'] == 'warning':
            level_text = "警告警报"
            emoji = "[警告]"
        else:
            level_text = "信息警报"
            emoji = "[信息]"
        
        message = f"{emoji} myStock监控警报\n\n"
        message += f"股票: {alert['stock']}\n"
        message += f"级别: {level_text}\n"
        message += f"消息: {alert['message']}\n"
        message += f"现价: {alert['price']}元"
        
        if alert['change'] > 0:
            message += f" (上涨{alert['change']:.1f}%)"
        elif alert['change'] < 0:
            message += f" (下跌{abs(alert['change']):.1f}%)"
        
        message += f"\n时间: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"数据源: 新浪财经实时API\n\n"
        
        if alert['level'] == 'critical':
            message += "建议: 立即检查持仓\n"
        elif alert['level'] == 'warning':
            message += "建议: 考虑相应操作\n"
        
        message += "---\nmyStock真实行情监控系统"
        
        # 发送警报
        send_feishu_alert(message)
        
        # 显示其他警报
        if len(alerts) > 1:
            print(f"\n其他警报 ({len(alerts)-1}个):")
            for other_alert in alerts[1:3]:  # 显示最多2个其他警报
                print(f"  • {other_alert['stock']}: {other_alert['message']}")
    else:
        # 如果没有警报，发送状态报告
        message = f"[状态] myStock监控报告\n\n"
        message += f"时间: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"大盘: {' | '.join(market_report[:2])}\n\n"
        
        message += "持仓状态:\n"
        for stock in config['monitored_stocks']:
            code = stock['code']
            name = stock['name']
            data = fetcher.get_stock_data(code, fallback=True)
            
            if data and 'error' not in data:
                change = data['change_percent']
                if change > 0:
                    trend = "上涨"
                elif change < 0:
                    trend = "下跌"
                else:
                    trend = "平盘"
                
                message += f"{code} {name}: {data['price']}元 ({change:+.1f}%) {trend}\n"
        
        message += f"\n监控结果: 无警报触发\n"
        message += f"检查时间: {datetime.now().strftime('%H:%M:%S')}\n"
        message += "---\nmyStock真实行情监控系统"
        
        send_feishu_alert(message)
    
    print("\n" + "="*50)
    print("监控检查完成")
    print("="*50)

if __name__ == "__main__":
    quick_monitor()