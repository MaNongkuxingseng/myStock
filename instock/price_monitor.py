#!/usr/bin/env python3
"""
价格监控系统 - 实时监控股票价格并发送提醒
"""

import json
import os
import time
from datetime import datetime
import random

class PriceMonitor:
    """价格监控器"""
    
    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()
        self.alerts_sent = []
        
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
    
    def get_simulated_price(self, code, base_price):
        """获取模拟价格（待替换为真实API）"""
        # 基于时间的波动模拟
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        time_factor = (current_hour * 60 + current_minute) / 1440.0
        
        # 模拟日内波动
        if time_factor < 0.25:  # 早盘
            volatility = 0.02
        elif time_factor < 0.5:  # 午前
            volatility = 0.015
        elif time_factor < 0.75:  # 午后
            volatility = 0.01
        else:  # 尾盘
            volatility = 0.005
        
        # 添加随机波动
        random.seed(hash(f"{code}{current_hour}{current_minute}") % 1000)
        fluctuation = random.uniform(-volatility, volatility)
        
        current_price = base_price * (1 + fluctuation)
        change_percent = fluctuation * 100
        
        return {
            'price': round(current_price, 3),
            'change': round(change_percent, 2),
            'volume': random.randint(50000, 200000) * 100,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def check_price_alerts(self, stock, realtime_data):
        """检查价格警报"""
        alerts = []
        rules = stock['monitor_rules']
        current_price = realtime_data['price']
        change = realtime_data['change']
        
        # 止损警报
        if 'stop_loss' in rules and current_price <= rules['stop_loss']:
            alerts.append({
                'level': 'critical',
                'type': 'stop_loss',
                'message': f"{stock['code']} {stock['name']} 触发止损位 {rules['stop_loss']}元",
                'current_price': current_price,
                'threshold': rules['stop_loss']
            })
        
        # 买入提醒
        if 'buy_alert' in rules and current_price <= rules['buy_alert']:
            alerts.append({
                'level': 'warning',
                'type': 'buy_opportunity',
                'message': f"{stock['code']} {stock['name']} 达到买入价 {rules['buy_alert']}元",
                'current_price': current_price,
                'threshold': rules['buy_alert']
            })
        
        # 卖出提醒
        if 'sell_alert' in rules and current_price >= rules['sell_alert']:
            alerts.append({
                'level': 'warning',
                'type': 'sell_opportunity',
                'message': f"{stock['code']} {stock['name']} 达到目标价 {rules['sell_alert']}元",
                'current_price': current_price,
                'threshold': rules['sell_alert']
            })
        
        # 支撑位提醒
        if 'support' in rules and current_price <= rules['support']:
            alerts.append({
                'level': 'info',
                'type': 'support_test',
                'message': f"{stock['code']} {stock['name']} 测试支撑位 {rules['support']}元",
                'current_price': current_price,
                'threshold': rules['support']
            })
        
        # 阻力位提醒
        if 'resistance' in rules and current_price >= rules['resistance']:
            alerts.append({
                'level': 'info',
                'type': 'resistance_test',
                'message': f"{stock['code']} {stock['name']} 测试阻力位 {rules['resistance']}元",
                'current_price': current_price,
                'threshold': rules['resistance']
            })
        
        # 涨跌幅提醒
        if 'change_threshold' in rules and abs(change) >= rules['change_threshold']:
            direction = "上涨" if change > 0 else "下跌"
            alerts.append({
                'level': 'warning' if abs(change) > 5 else 'info',
                'type': 'price_change',
                'message': f"{stock['code']} {stock['name']} {direction}{abs(change):.1f}%",
                'current_price': current_price,
                'change': change
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
        
        message = f"{emoji} **价格监控警报**\n\n"
        message += f"**股票**: {stock_info['code']} {stock_info['name']}\n"
        message += f"**类型**: {alert['type']}\n"
        message += f"**级别**: {alert['level'].upper()}\n"
        message += f"**消息**: {alert['message']}\n"
        message += f"**现价**: {alert['current_price']}元"
        
        if 'change' in alert:
            message += f" ({alert['change']:+.1f}%)"
        
        message += f"\n**时间**: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"\n---\nmyStock监控系统"
        
        return message
    
    def send_feishu_alert(self, message):
        """发送Feishu警报（模拟）"""
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
    
    def check_all_stocks(self):
        """检查所有监控股票"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 开始价格检查...")
        
        all_alerts = []
        
        for stock in self.config['monitored_stocks']:
            # 获取实时价格
            realtime_data = self.get_simulated_price(
                stock['code'], 
                stock['current_price']
            )
            
            # 检查警报
            alerts = self.check_price_alerts(stock, realtime_data)
            
            if alerts:
                all_alerts.extend(alerts)
                
                # 显示当前状态
                change_symbol = "▲" if realtime_data['change'] > 0 else "▼" if realtime_data['change'] < 0 else "●"
                print(f"  {stock['code']} {stock['name']}: {realtime_data['price']}元 {change_symbol}{abs(realtime_data['change']):.1f}%")
        
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
        
        return len(all_alerts)
    
    def run_continuous_monitoring(self):
        """持续监控"""
        print("="*60)
        print("myStock价格监控系统启动")
        print("="*60)
        
        check_count = 0
        
        try:
            while True:
                check_count += 1
                print(f"\n检查轮次 #{check_count}")
                
                alert_count = self.check_all_stocks()
                
                if alert_count == 0:
                    print("  无警报触发")
                
                # 等待下一次检查
                interval = self.config['notification_settings']['check_interval_minutes']
                print(f"\n等待 {interval} 分钟后再次检查...")
                time.sleep(interval * 60)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
            
            # 生成监控报告
            self.generate_monitoring_report(check_count)
    
    def generate_monitoring_report(self, total_checks):
        """生成监控报告"""
        report = f"📊 **价格监控报告** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        report += f"监控时长: {total_checks} 次检查\n"
        report += f"警报总数: {len(self.alerts_sent)} 条\n"
        
        # 按级别统计
        level_counts = {'critical': 0, 'warning': 0, 'info': 0}
        for alert in self.alerts_sent:
            # 从消息中提取级别
            msg = alert['message']
            if '🔴' in msg:
                level_counts['critical'] += 1
            elif '🟡' in msg:
                level_counts['warning'] += 1
            elif '🟢' in msg:
                level_counts['info'] += 1
        
        report += f"\n警报分布:\n"
        report += f"• 严重警报: {level_counts['critical']} 条\n"
        report += f"• 警告警报: {level_counts['warning']} 条\n"
        report += f"• 信息警报: {level_counts['info']} 条\n"
        
        # 最近警报
        report += f"\n最近警报:\n"
        recent_alerts = self.alerts_sent[-3:] if len(self.alerts_sent) >= 3 else self.alerts_sent
        for alert in recent_alerts:
            time_str = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M')
            # 提取简要信息
            lines = alert['message'].split('\n')
            brief = next((l for l in lines if '消息:' in l), '')
            if brief:
                brief = brief.replace('**消息**: ', '')[:40]
                report += f"• {time_str}: {brief}...\n"
        
        report += f"\n---\nmyStock智能监控系统"
        
        print("\n" + "="*60)
        print("监控报告:")
        print("="*60)
        print(report)
        
        return report

def main():
    """主函数"""
    config_path = os.path.join(os.path.dirname(__file__), "price_monitor_config.json")
    
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        return
    
    monitor = PriceMonitor(config_path)
    
    print("选择操作模式:")
    print("1. 启动持续监控")
    print("2. 执行单次检查")
    print("3. 查看当前配置")
    print("4. 测试警报发送")
    
    try:
        choice = input("请输入选择 (1-4): ").strip()
    except:
        choice = "1"  # 默认选择
    
    if choice == '1':
        monitor.run_continuous_monitoring()
    elif choice == '2':
        monitor.check_all_stocks()
    elif choice == '3':
        print(json.dumps(monitor.config, indent=2, ensure_ascii=False))
    elif choice == '4':
        # 测试警报
        test_alert = {
            'level': 'info',
            'type': 'test',
            'message': '价格监控系统测试正常',
            'current_price': 100.00,
            'change': 0.0
        }
        test_stock = {'code': '000001', 'name': '测试股票'}
        message = monitor.format_alert_message(test_alert, test_stock)
        monitor.send_feishu_alert(message)
    else:
        print("无效选择，启动持续监控")
        monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()