#!/usr/bin/env python3
"""
9时间点消息推送调度系统
"""

import os
import json
import time
import schedule
from datetime import datetime, timedelta
import threading
import sys

class NinePointScheduler:
    """9时间点调度系统"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 9个时间点配置
        self.time_points = [
            {'time': '09:00', 'name': '早盘准备', 'type': 'morning'},
            {'time': '09:30', 'name': '开盘分析', 'type': 'opening'},
            {'time': '10:00', 'name': '盘中跟踪1', 'type': 'tracking'},
            {'time': '11:00', 'name': '盘中跟踪2', 'type': 'tracking'},
            {'time': '11:30', 'name': '午盘总结', 'type': 'midday'},
            {'time': '13:00', 'name': '午盘开盘', 'type': 'afternoon'},
            {'time': '14:00', 'name': '盘中跟踪3', 'type': 'tracking'},
            {'time': '14:30', 'name': '尾盘分析', 'type': 'late'},
            {'time': '15:00', 'name': '收盘总结', 'type': 'closing'}
        ]
        
        # 持仓股
        self.holdings = [
            {'code': '600118', 'name': '中国卫星'},
            {'code': '600157', 'name': '永泰能源'},
            {'code': '000731', 'name': '四川美丰'}
        ]
        
        # 日志目录
        self.log_dir = os.path.join(self.base_dir, 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 状态文件
        self.status_file = os.path.join(self.log_dir, 'scheduler_status.json')
        
        print("=" * 70)
        print("9时间点消息推送调度系统")
        print(f"初始化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    def log_message(self, level, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # 打印到控制台
        print(log_entry)
        
        # 写入日志文件
        log_file = os.path.join(self.log_dir, f"scheduler_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def save_status(self, time_point, status, details=None):
        """保存状态"""
        status_data = {
            'last_execution': datetime.now().isoformat(),
            'time_point': time_point,
            'status': status,
            'details': details or {}
        }
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
    
    def execute_time_point(self, tp_config):
        """执行单个时间点任务"""
        time_str = tp_config['time']
        name = tp_config['name']
        
        self.log_message('INFO', f"开始执行 {time_str} {name} 任务")
        
        try:
            # 1. 数据获取
            self.log_message('INFO', '步骤1: 获取实时数据')
            data = self.fetch_realtime_data()
            
            # 2. 数据分析
            self.log_message('INFO', '步骤2: 分析数据')
            analysis = self.analyze_data(data)
            
            # 3. 生成报告
            self.log_message('INFO', '步骤3: 生成报告')
            report = self.generate_report(tp_config, data, analysis)
            
            # 4. 保存文件
            self.log_message('INFO', '步骤4: 保存文件')
            files = self.save_files(tp_config, data, analysis, report)
            
            # 5. Git提交
            self.log_message('INFO', '步骤5: Git提交')
            git_success = self.git_commit(tp_config, files)
            
            # 6. 生成追溯报告
            self.log_message('INFO', '步骤6: 生成追溯报告')
            trace_report = self.generate_trace_report(tp_config, files, git_success)
            
            # 保存状态
            self.save_status(time_str, 'success', {
                'files_generated': files,
                'git_success': git_success,
                'trace_report': trace_report
            })
            
            self.log_message('SUCCESS', f"{time_str} {name} 任务执行完成")
            return True
            
        except Exception as e:
            self.log_message('ERROR', f"任务执行失败: {str(e)}")
            self.save_status(time_str, 'failed', {'error': str(e)})
            return False
    
    def fetch_realtime_data(self):
        """获取实时数据（简化版）"""
        import requests
        
        data = {}
        for stock in self.holdings:
            code = stock['code']
            try:
                # 腾讯财经API
                if code.startswith('6'):
                    market_code = f"sh{code}"
                else:
                    market_code = f"sz{code}"
                
                url = f"http://qt.gtimg.cn/q={market_code}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    text = response.text.strip()
                    if '=' in text:
                        data_part = text.split('=')[1].strip('"')
                        fields = data_part.split('~')
                        
                        if len(fields) >= 40:
                            data[code] = {
                                'name': stock['name'],
                                'price': float(fields[3]) if fields[3] else 0,
                                'pre_close': float(fields[4]) if fields[4] else 0,
                                'open': float(fields[5]) if fields[5] else 0,
                                'high': float(fields[33]) if len(fields) > 33 and fields[33] else 0,
                                'low': float(fields[34]) if len(fields) > 34 and fields[34] else 0,
                                'volume': int(fields[6]) if fields[6] else 0,
                                'time': fields[30] if len(fields) > 30 else ''
                            }
            except:
                pass
        
        return data
    
    def analyze_data(self, data):
        """分析数据"""
        analysis = {}
        
        for code, stock_data in data.items():
            if stock_data:
                price = stock_data['price']
                pre_close = stock_data['pre_close']
                
                if pre_close > 0:
                    change_pct = (price - pre_close) / pre_close * 100
                    
                    # 生成信号
                    signals = []
                    if change_pct > 3:
                        signals.append('强势上涨')
                    elif change_pct < -3:
                        signals.append('大幅下跌')
                    
                    if stock_data['volume'] > 1000000:
                        signals.append('放量')
                    
                    # 操作建议
                    if change_pct > 5:
                        recommendation = "强势上涨，持有或加仓"
                    elif change_pct > 0:
                        recommendation = "温和上涨，持有观察"
                    elif change_pct > -3:
                        recommendation = "震荡整理，观望"
                    elif change_pct > -6:
                        recommendation = "小幅下跌，谨慎持有"
                    else:
                        recommendation = "大幅下跌，建议减仓"
                    
                    analysis[code] = {
                        'change_pct': change_pct,
                        'signals': signals,
                        'recommendation': recommendation
                    }
        
        return analysis
    
    def generate_report(self, tp_config, data, analysis):
        """生成报告"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""{tp_config['name']}分析报告
时间: {timestamp}
时间点: {tp_config['time']}
========================================

市场概况:
"""
        
        for code, stock_data in data.items():
            if code in analysis:
                anal = analysis[code]
                report += f"""
{stock_data['name']} ({code}):
• 当前价: {stock_data['price']:.2f}元
• 涨跌幅: {anal['change_pct']:+.2f}%
• 成交量: {stock_data['volume']:,}手
• 信号: {', '.join(anal['signals']) if anal['signals'] else '无'}
• 建议: {anal['recommendation']}
"""
        
        report += f"""
========================================
生成时间: {timestamp}
"""
        
        return report
    
    def save_files(self, tp_config, data, analysis, report):
        """保存文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        date_str = datetime.now().strftime('%Y%m%d')
        
        # 创建日期目录
        date_dirs = {
            'reports': os.path.join(self.base_dir, 'reports', date_str),
            'data': os.path.join(self.base_dir, 'data', date_str),
            'analysis': os.path.join(self.base_dir, 'analysis', date_str)
        }
        
        for dir_path in date_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        files = []
        
        # 1. 保存数据文件
        data_file = os.path.join(date_dirs['data'], f"data_{tp_config['time'].replace(':', '')}_{timestamp}.json")
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'time_point': tp_config['time'],
                'fetch_time': datetime.now().isoformat(),
                'data': data,
                'analysis': analysis
            }, f, ensure_ascii=False, indent=2)
        files.append(data_file)
        
        # 2. 保存报告文件
        report_file = os.path.join(date_dirs['reports'], f"report_{tp_config['time'].replace(':', '')}_{timestamp}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        files.append(report_file)
        
        # 3. 保存分析文件
        analysis_file = os.path.join(date_dirs['analysis'], f"analysis_{tp_config['time'].replace(':', '')}_{timestamp}.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        files.append(analysis_file)
        
        return files
    
    def git_commit(self, tp_config, files):
        """Git提交"""
        try:
            import subprocess
            
            # 切换到项目目录
            os.chdir(self.base_dir)
            
            # 添加文件
            for file in files:
                rel_path = os.path.relpath(file, self.base_dir)
                subprocess.run(['git', 'add', rel_path], check=True)
            
            # 提交
            commit_msg = f"feat: {tp_config['time']} {tp_config['name']}报告 - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # 尝试推送
            try:
                subprocess.run(['git', 'push'], check=True)
            except:
                pass  # 推送失败不影响
            
            return True
            
        except Exception as e:
            self.log_message('WARNING', f"Git提交失败: {str(e)}")
            return False
    
    def generate_trace_report(self, tp_config, files, git_success):
        """生成追溯报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        trace_report = {
            'workflow_id': f"workflow_{timestamp}",
            'time_point': tp_config['time'],
            'execution_time': datetime.now().isoformat(),
            'files_generated': [os.path.basename(f) for f in files],
            'git_success': git_success,
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform
            }
        }
        
        trace_file = os.path.join(self.log_dir, f"trace_{tp_config['time'].replace(':', '')}_{timestamp}.json")
        with open(trace_file, 'w', encoding='utf-8') as f:
            json.dump(trace_report, f, ensure_ascii=False, indent=2)
        
        return trace_file
    
    def setup_schedule(self):
        """设置调度"""
        self.log_message('INFO', '设置9时间点调度')
        
        for tp in self.time_points:
            schedule.every().day.at(tp['time']).do(
                lambda tp=tp: self.execute_time_point(tp)
            )
            self.log_message('INFO', f"已调度: {tp['time']} - {tp['name']}")
    
    def run(self):
        """运行调度器"""
        self.log_message('INFO', '启动调度器')
        
        # 设置调度
        self.setup_schedule()
        
        # 立即执行当前时间点（如果已过时间）
        current_time = datetime.now().strftime('%H:%M')
        for tp in self.time_points:
            if tp['time'] <= current_time:
                self.log_message('INFO', f"立即执行已过时间点: {tp['time']}")
                self.execute_time_point(tp)
        
        self.log_message('INFO', '调度器运行中，按Ctrl+C停止')
        
        # 运行调度
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.log_message('INFO', '调度器已停止')
    
    def test_workflow(self):
        """测试工作流程"""
        self.log_message('INFO', '开始测试工作流程')
        
        # 测试当前时间点
        test_tp = {'time': 'TEST', 'name': '测试任务', 'type': 'test'}
        
        success = self.execute_time_point(test_tp)
        
        if success:
            self.log_message('SUCCESS', '工作流程测试成功')
        else:
            self.log_message('ERROR', '工作流程测试失败')
        
        return success

def main():
    """主函数"""
    scheduler = NinePointScheduler()
    
    print("\n选择操作:")
    print("1. 测试工作流程")
    print("2. 启动调度器")
    print("3. 查看状态")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == '1':
        scheduler.test_workflow()
    elif choice == '2':
        scheduler.run()
    elif choice == '3':
        if os.path.exists(scheduler.status_file):
            with open(scheduler.status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            print(f"最后执行: {status.get('last_execution')}")
            print(f"时间点: {status.get('time_point')}")
            print(f"状态: {status.get('status')}")
        else:
            print("无状态信息")
    else:
        print("无效选择")

if __name__ == "__main__":
    main()