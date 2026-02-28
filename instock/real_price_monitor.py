#!/usr/bin/env python3
"""
真实价格监控系统 - 使用真实行情API
"""

import sys
import os
# 添加自定义库路径
sys.path.append('D:\\python_libs')

import json
import time
from datetime import datetime
from real_time_data import RealTimeDataFetcher

class RealPriceMonitor:
    """真实价格监控器"""
    
    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()
        self.fetcher = RealTimeDataFetcher()
        self.alerts_sent = []
        self.last_check_time = None
        
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"配置加载成功，监控{len(self.config['monitored_stocks'])}只股票")
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config = {
                'monitored_stocks': [],
                'notification_settings': {
                    'feishu_group': 'oc_b99df765824c2e59b3fabf287e8d14a2',
                    'check_interval_minutes': 5
                }
            }
    
    def get_real_time_price(self, code):
        """获取真实实时价格"""
        try:
            data = self.fetcher.get_stock_data(code, fallback=True)
            
            if data and 'error' not in data:
                return {
                    'code': code,
                    'price': data.get('price', 0),
                    'change': data.get('change_percent', 0),
                    'volume': data.get('volume', 0),
                    'time': data.get('time', datetime.now().strftime('%H:%M:%S')),
                    'source': data.get('source', 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
            else:
                return {
                    'code': code,
                    'price': 0,
                    'change': 0,
                    'error': data.get('error', '获取失败') if data else '未知错误',
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
                
        except Exception as e:
            return {
                'code': code,
                'price': 0,
                'change': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def check_price_alerts(self, stock, realtime_data):
        """检查价格警报"""
        if not realtime_data['success']:
            return []
        
        alerts = []
        rules = stock['monitor_rules']
        current_price = realtime_data['price']
        change = realtime_data['change']
        
        # 更新配置中的当前价格
        stock['current_price'] = current_price
        
        # 止损警报
        if 'stop_loss' in rules and current_price <= rules['stop_loss']:
            alerts.append({
                'level': 'critical',
                'type': 'stop_loss',
                'message': f"{stock['code']} {stock['name']} 触发止损位 {rules['stop_loss']}元",
                'current_price': current_price,
                'threshold': rules['stop_loss'],
                'change': change
            })
        
        # 买入提醒
        if 'buy_alert' in rules and current_price <= rules['buy_alert']:
            alerts.append({
                'level': 'warning',
                'type': 'buy_opportunity',
                'message': f"{stock['code']} {stock['name']} 达到买入价 {rules['buy_alert']}元",
                'current_price': current_price,
                'threshold': rules['buy_alert'],
                'change': change
            })
        
        # 卖出提醒
        if 'sell_alert' in rules and current_price >= rules['sell_alert']:
            alerts.append({
                'level': 'warning',
                'type': 'sell_opportunity',
                'message': f"{stock['code']} {stock['name']} 达到目标价 {rules['sell_alert']}元",
                'current_price': current_price,
                'threshold': rules['sell_alert'],
                'change': change
            })
        
        # 支撑位提醒
        if 'support' in rules and current_price <= rules['support']:
            alerts.append({
                'level': 'info',
                'type': 'support_test',
                'message': f"{stock['code']} {stock['name']} 测试支撑位 {rules['support']}元",
                'current_price': current_price,
                'threshold': rules['support'],
                'change': change
            })
        
        # 阻力位提醒
        if 'resistance' in rules and current_price >= rules['resistance']:
            alerts.append({
                'level': 'info',
                'type': 'resistance_test',
                'message': f"{stock['code']} {stock['name']} 测试阻力位 {rules['resistance']}元",
                'current_price': current_price,
                'threshold': rules['resistance'],
                'change': change
            })
        
        # 涨跌幅提醒
        if 'change_threshold' in rules and abs(change) >= rules['change_threshold']:
            direction = "上涨" if change > 0 else "下跌"
            alerts.append({
                'level': 'warning' if abs(change) > 5 else 'info',
                'type': 'price_change',
                'message': f"{stock['code']} {stock['name']} {direction}{abs(change):.1f}%",
                'current_price': current_price,
                'change': change,
                'threshold': rules['change_threshold']
            })
        
        return alerts
    
    def format_alert_message(self, alert, stock_info):
        """格式化警报消息"""
        level_emojis = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🟢'
        }
        
        emoji = level_emojis.get(alert['level'], '⚪')
        
        message = f"{emoji} **真实行情监控警报**\n\n"
        message += f"**股票**: {stock_info['code']} {stock_info['name']}\n"
        message += f"**类型**: {alert['type']}\n"
        message += f"**级别**: {alert['level'].upper()}\n"
        message += f"**消息**: {alert['message']}\n"
        message += f"**现价**: {alert['current_price']}元"
        
        if 'change' in alert:
            change_emoji = "📈" if alert['change'] > 0 else "📉" if alert['change'] < 0 else "➡️"
            message += f" {change_emoji} ({alert['change']:+.1f}%)"
        
        message += f"\n**时间**: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"**数据源**: 新浪财经实时API\n"
        
        if alert['level'] == 'critical':
            message += f"\n⚠️ **紧急操作建议**: 立即检查持仓\n"
        elif alert['level'] == 'warning':
            message += f"\n💡 **操作建议**: 考虑相应操作\n"
        
        message += f"\n---\nmyStock真实行情监控系统"
        
        return message
    
    def send_feishu_alert(self, message):
        """发送Feishu警报"""
        # 这里应该调用Feishu API
        # 暂时打印到控制台并记录
        
        print(f"\n发送Feishu警报:")
        print("="*50)
        print(message)
        print("="*50)
        
        # 记录已发送的警报
        self.alerts_sent.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'sent': True
        })
        
        return True
    
    def update_config_prices(self):
        """更新配置中的价格数据"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            updated = False
            for stock in config['monitored_stocks']:
                code = stock['code']
                realtime_data = self.get_real_time_price(code)
                
                if realtime_data['success']:
                    old_price = stock.get('current_price', 0)
                    new_price = realtime_data['price']
                    
                    if old_price != new_price:
                        stock['current_price'] = new_price
                        updated = True
            
            if updated:
                config['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                print("配置价格已更新")
            
            return updated
            
        except Exception as e:
            print(f"更新配置价格失败: {e}")
            return False
    
    def check_all_stocks(self):
        """检查所有监控股票"""
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{current_time}] 开始真实行情检查...")
        
        all_alerts = []
        market_data = self.fetcher.get_market_index()
        
        # 显示大盘情况
        print("大盘指数:")
        for name, data in market_data.items():
            if 'error' not in data:
                change_emoji = "🟢" if data['change_percent'] > 0 else "🔴" if data['change_percent'] < 0 else "🟡"
                print(f"  {change_emoji} {name}: {data['price']} ({data['change_percent']:+.2f}%)")
        
        print("\n股票监控:")
        for stock in self.config['monitored_stocks']:
            # 获取真实价格
            realtime_data = self.get_real_time_price(stock['code'])
            
            if realtime_data['success']:
                # 检查警报
                alerts = self.check_price_alerts(stock, realtime_data)
                
                if alerts:
                    all_alerts.extend(alerts)
                
                # 显示当前状态
                change_symbol = "▲" if realtime_data['change'] > 0 else "▼" if realtime_data['change'] < 0 else "●"
                print(f"  {stock['code']} {stock['name']}: {realtime_data['price']}元 {change_symbol}{abs(realtime_data['change']):.1f}%")
            else:
                print(f"  ❌ {stock['code']} {stock['name']}: 获取失败 - {realtime_data.get('error', '未知错误')}")
        
        # 发送警报
        if all_alerts:
            # 按级别排序：critical > warning > info
            level_order = {'critical': 3, 'warning': 2, 'info': 1}
            all_alerts.sort(key=lambda x: level_order.get(x['level'], 0), reverse=True)
            
            # 发送最重要的3个警报
            for alert in all_alerts[:3]:
                stock_info = next(
                    (s for s in self.config['monitored_stocks'] 
                     if s['code'] == alert.get('code', '')),
                    {}
                )
                
                message = self.format_alert_message(alert, stock_info)
                self.send_feishu_alert(message)
        
        self.last_check_time = datetime.now()
        return len(all_alerts)
    
    def generate_daily_report(self):
        """生成日报"""
        report = f"📊 **myStock真实行情日报** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # 获取市场数据
        market_data = self.fetcher.get_market_index()
        
        report += "🌐 **大盘概览**\n"
        for name, data in market_data.items():
            if 'error' not in data:
                change_emoji = "🟢" if data['change_percent'] > 0 else "🔴" if data['change_percent'] < 0 else "🟡"
                report += f"{change_emoji} {name}: {data['price']} ({data['change_percent']:+.2f}%)\n"
        
        report += f"\n📈 **持仓监控**\n"
        
        for stock in self.config['monitored_stocks']:
            realtime_data = self.get_real_time_price(stock['code'])
            
            if realtime_data['success']:
                change_emoji = "🟢" if realtime_data['change'] > 0 else "🔴" if realtime_data['change'] < 0 else "🟡"
                report += f"{change_emoji} {stock['code']} {stock['name']}: {realtime_data['price']}元 ({realtime_data['change']:+.1f}%)\n"
        
        report += f"\n🔔 **今日警报统计**\n"
        report += f"• 总检查次数: {len(self.alerts_sent)}\n"
        report += f"• 最后检查: {self.last_check_time.strftime('%H:%M:%S') if self.last_check_time else '未检查'}\n"
        
        report += f"\n---\nmyStock真实行情监控系统\n"
        report += f"数据源: 新浪财经实时API\n"
        report += f"下次报告: 收盘后16:20\n"
        
        return report
    
    def run_continuous_monitoring(self):
        """持续监控"""
        print("="*60)
        print("myStock真实行情监控系统启动")
        print("="*60)
        print("数据源: 新浪财经实时API")
        print(f"监控股票: {len(self.config['monitored_stocks'])}只")
        print(f"检查频率: {self.config['notification_settings']['check_interval_minutes']}分钟")
        print("="*60)
        
        check_count = 0
        
        try:
            while True:
                check_count += 1
                print(f"\n检查轮次 #{check_count}")
                
                # 更新配置价格
                self.update_config_prices()
                
                # 检查所有股票
                alert_count = self.check_all_stocks()
                
                if alert_count == 0:
                    print("  无警报触发")
                
                # 等待下一次检查
                interval = self.config['notification_settings']['check_interval_minutes']
                print(f"\n等待 {interval} 分钟后再次检查...")
                time.sleep(interval * 60)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
            
            # 生成最终报告
            report = self.generate_daily_report()
            print("\n" + "="*60)
            print("今日监控报告:")
            print("="*60)
            print(report)

def main():
    """主函数"""
    config_path = os.path.join(os.path.dirname(__file__), "price_monitor_config.json")
    
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        return
    
    monitor = RealPriceMonitor(config_path)
    
    print("选择操作模式:")
    print("1. 启动持续监控")
    print("2. 执行单次检查")
    print("3. 生成日报")
    print("4. 测试API连接")
    
    try:
        choice = input("请输入选择 (1-4): ").strip()
    except:
        choice = "1"  # 默认选择
    
    if choice == '1':
        monitor.run_continuous_monitoring()
    elif choice == '2':
        monitor.check_all_stocks()
    elif choice == '3':
        report = monitor.generate_daily_report()
        print(report)
    elif choice == '4':
        # 测试API连接
        from real_time_data import test_real_time_data
        test_real_time_data()
    else:
        print("无效选择，启动持续监控")
        monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()