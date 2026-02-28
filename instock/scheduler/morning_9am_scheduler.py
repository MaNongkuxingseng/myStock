#!/usr/bin/env python3
"""
早上9点定时推送系统
集成myStock指标分析 + 任务管理报告
"""

import sys
import os
import json
from datetime import datetime, timedelta
import schedule
import time

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('D:\\python_libs')

class Morning9AMScheduler:
    """早上9点定时推送系统"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.current_time = datetime.now().strftime('%H:%M')
        
        # 群组配置
        self.groups = {
            'analysis': 'oc_b99df765824c2e59b3fabf287e8d14a2',  # 当前分析群组
            'management': 'oc_new_analysis_management_group'    # 新管理群组（待创建）
        }
        
        # 日志文件
        self.log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, f"scheduler_{self.today}.log")
    
    def log_message(self, level, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        print(log_entry.strip())
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def run_mystock_analysis(self):
        """运行myStock分析"""
        try:
            self.log_message("INFO", "开始运行myStock持仓分析...")
            
            # 导入分析模块
            from monitor.mystock_integrated_analysis import MystockIntegratedAnalyzer
            
            analyzer = MystockIntegratedAnalyzer()
            analysis = analyzer.run_analysis()
            
            # 生成9点报告
            report = analyzer.generate_9am_report(analysis)
            
            self.log_message("INFO", f"myStock分析完成，生成报告长度: {len(report)} 字符")
            
            return {
                'success': True,
                'report': report,
                'analysis': analysis
            }
            
        except Exception as e:
            self.log_message("ERROR", f"myStock分析失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 生成错误报告
            error_report = f"""⚠️ **myStock早盘分析报告** {self.today} 09:00

❌ **分析失败**
错误信息: {str(e)}

📱 **系统状态**
• 分析时间: 09:00
• 分析状态: ❌ 失败
• 错误类型: 系统异常

🔧 **故障排查**
1. 检查myStock数据库连接
2. 验证指标计算模块
3. 检查持仓数据配置

🔄 **备用方案**
• 使用昨日缓存数据
• 手动运行分析脚本
• 检查系统日志

---
**myStock智能分析系统 | 错误报告**
报告时间: {self.today} 09:00
"""
            
            return {
                'success': False,
                'report': error_report,
                'error': str(e)
            }
    
    def run_task_management_report(self):
        """运行任务管理报告"""
        try:
            self.log_message("INFO", "开始生成任务管理报告...")
            
            # 导入任务管理模块
            from task_manager.task_management_system import TaskManager
            
            manager = TaskManager()
            report = manager.generate_daily_report()
            
            self.log_message("INFO", f"任务管理报告生成完成，长度: {len(report)} 字符")
            
            return {
                'success': True,
                'report': report,
                'summary': manager.get_task_summary()
            }
            
        except Exception as e:
            self.log_message("ERROR", f"任务管理报告生成失败: {e}")
            
            error_report = f"""📋 **任务管理日报** {self.today}

❌ **报告生成失败**
错误信息: {str(e)}

📊 **系统状态**
• 报告时间: 09:00
• 生成状态: ❌ 失败
• 错误类型: 任务管理异常

🔧 **故障排查**
1. 检查任务数据库
2. 验证任务管理模块
3. 检查文件权限

---
**任务管理系统 | 错误报告**
报告时间: {self.today} 09:00
"""
            
            return {
                'success': False,
                'report': error_report,
                'error': str(e)
            }
    
    def send_to_feishu(self, message, group_type='analysis'):
        """发送消息到Feishu（模拟）"""
        try:
            group_id = self.groups.get(group_type, self.groups['analysis'])
            
            self.log_message("INFO", f"准备发送消息到Feishu群组: {group_id}")
            self.log_message("INFO", f"消息类型: {group_type}, 长度: {len(message)}")
            
            # 这里应该是实际的Feishu API调用
            # 暂时模拟发送
            print("\n" + "="*70)
            print(f"Feishu消息发送到群组: {group_id}")
            print("="*70)
            print(message[:500] + "..." if len(message) > 500 else message)
            print("="*70)
            
            # 保存消息到文件（用于测试）
            message_dir = os.path.join(self.log_dir, "messages")
            os.makedirs(message_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            message_file = os.path.join(message_dir, f"{group_type}_{timestamp}.md")
            
            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            self.log_message("INFO", f"消息已保存到: {message_file}")
            
            return {
                'success': True,
                'message_file': message_file,
                'group_id': group_id
            }
            
        except Exception as e:
            self.log_message("ERROR", f"Feishu消息发送失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def morning_9am_routine(self):
        """早上9点例行任务"""
        self.log_message("INFO", "="*60)
        self.log_message("INFO", "开始执行早上9点定时推送任务")
        self.log_message("INFO", "="*60)
        
        results = {
            'timestamp': f"{self.today} 09:00",
            'mystock_analysis': None,
            'task_management': None,
            'messages_sent': []
        }
        
        # 1. 运行myStock分析
        self.log_message("INFO", "步骤1: 运行myStock持仓分析")
        mystock_result = self.run_mystock_analysis()
        results['mystock_analysis'] = mystock_result
        
        if mystock_result['success']:
            # 发送到分析群组
            send_result = self.send_to_feishu(
                mystock_result['report'], 
                group_type='analysis'
            )
            results['messages_sent'].append({
                'type': 'mystock_analysis',
                'success': send_result['success'],
                'group': 'analysis'
            })
        
        # 2. 运行任务管理报告
        self.log_message("INFO", "步骤2: 生成任务管理报告")
        task_result = self.run_task_management_report()
        results['task_management'] = task_result
        
        if task_result['success']:
            # 发送到管理群组（如果已创建）
            send_result = self.send_to_feishu(
                task_result['report'],
                group_type='management'
            )
            results['messages_sent'].append({
                'type': 'task_management',
                'success': send_result['success'],
                'group': 'management'
            })
        
        # 3. 生成执行摘要
        self.log_message("INFO", "步骤3: 生成执行摘要")
        summary = self.generate_execution_summary(results)
        
        # 保存执行结果
        results_file = os.path.join(self.log_dir, f"execution_{self.today}_0900.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        self.log_message("INFO", f"执行结果已保存到: {results_file}")
        self.log_message("INFO", "早上9点定时推送任务执行完成")
        self.log_message("INFO", "="*60)
        
        return results
    
    def generate_execution_summary(self, results):
        """生成执行摘要"""
        mystock_success = results['mystock_analysis']['success'] if results['mystock_analysis'] else False
        task_success = results['task_management']['success'] if results['task_management'] else False
        
        messages_sent = len([m for m in results['messages_sent'] if m['success']])
        total_messages = len(results['messages_sent'])
        
        summary = f"""📊 **早上9点定时任务执行摘要** {self.today}

⏰ **执行时间**
• 计划时间: 09:00
• 实际时间: {self.current_time}
• 执行状态: {'✅ 完成' if mystock_success or task_success else '❌ 失败'}

📈 **任务执行情况**
• myStock分析: {'✅ 成功' if mystock_success else '❌ 失败'}
• 任务管理报告: {'✅ 成功' if task_success else '❌ 失败'}
• 消息发送: {messages_sent}/{total_messages} 成功

📋 **详细结果**
"""
        
        if results['mystock_analysis']:
            status = '✅' if results['mystock_analysis']['success'] else '❌'
            summary += f"{status} myStock分析: {results['mystock_analysis'].get('report', '')[:100]}...\n"
        
        if results['task_management']:
            status = '✅' if results['task_management']['success'] else '❌'
            summary += f"{status} 任务管理: {results['task_management'].get('report', '')[:100]}...\n"
        
        # 消息发送情况
        summary += f"\n📱 **消息发送情况**\n"
        for msg in results['messages_sent']:
            status = '✅' if msg['success'] else '❌'
            summary += f"{status} {msg['type']} -> {msg['group']}群组\n"
        
        summary += f"""
🔄 **下次执行**
• 下次分析: 明日 09:00
• 下次报告: 今日 16:20 (收盘总结)

🔧 **系统状态**
• 调度器: ✅ 运行中
• 分析模块: {'✅ 正常' if mystock_success else '❌ 异常'}
• 任务管理: {'✅ 正常' if task_success else '❌ 异常'}
• 消息推送: ⚙️ 测试中

---
**早上9点定时推送系统 | 执行摘要**
生成时间: {self.today} {self.current_time}
"""
        
        self.log_message("INFO", f"执行摘要生成完成")
        return summary
    
    def setup_schedule(self):
        """设置定时任务"""
        self.log_message("INFO", "设置定时任务调度...")
        
        # 每天早上9点执行
        schedule.every().day.at("09:00").do(self.morning_9am_routine)
        
        # 测试任务（每分钟执行一次，用于测试）
        schedule.every(1).minutes.do(self.test_routine)
        
        self.log_message("INFO", "定时任务设置完成")
        self.log_message("INFO", "已安排: 每天09:00执行myStock分析和任务报告")
    
    def test_routine(self):
        """测试任务"""
        self.log_message("DEBUG", "测试任务执行中...")
        return {"status": "test_ok", "time": self.current_time}
    
    def run_scheduler(self):
        """运行调度器"""
        self.log_message("INFO", "启动早上9点定时推送调度器")
        self.log_message("INFO", f"当前时间: {self.today} {self.current_time}")
        
        # 设置定时任务
        self.setup_schedule()
        
        # 立即执行一次测试
        self.log_message("INFO", "执行初始测试...")
        test_result = self.test_routine()
        self.log_message("INFO", f"测试结果: {test_result}")
        
        # 如果当前时间是9点附近，立即执行一次
        current_hour = datetime.now().hour
        if current_hour == 9:
            self.log_message("INFO", "当前时间为9点，立即执行例行任务")
            self.morning_9am_routine()
        
        self.log_message("INFO", "调度器开始运行，等待定时任务...")
        self.log_message("INFO", "按 Ctrl+C 停止")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            self.log_message("INFO", "调度器已停止")
        except Exception as e:
            self.log_message("ERROR", f"调度器运行错误: {e}")
    
    def run_once(self):
        """立即执行一次"""
        self.log_message("INFO", "立即执行早上9点任务...")
        return self.morning_9am_routine()

def main():
    """主函数"""
    print("="*70)
    print("早上9点定时推送系统")
    print("="*70)
    
    scheduler = Morning9AMScheduler()
    
    print("\n系统功能:")
    print("1. 每天早上9点自动推送myStock持仓分析")
    print("2. 集成myStock技术指标计算")
    print("3. 生成任务管理日报")
    print("4. 支持多群组推送")
    print("5. 完整的日志和错误处理")
    
    print("\n群组配置:")
    print(f"• 分析群组: {scheduler.groups['analysis']}")
    print(f"• 管理群组: {scheduler.groups['management']} (待创建)")
    
    print("\n执行选项:")
    print("1. 立即执行一次测试")
    print("2. 启动定时调度器")
    print("3. 查看系统状态")
    
    try:
        choice = input("\n请选择 (1-3, 默认1): ").strip() or "1"
        
        if choice == "1":
            print("\n执行一次测试任务...")
            result = scheduler.run_once()
            print(f"\n测试完成!")
            
            # 显示摘要
            if result.get('mystock_analysis', {}).get('success'):
                print("✅ myStock分析: 成功")
            else:
                print("❌ myStock分析: 失败")
            
            if result.get('task_management', {}).get('success'):
                print("✅ 任务管理报告: 成功")
            else:
                print("❌ 任务管理报告: 失败")
            
            print(f"\n详细结果保存在: {scheduler.log_file}")
            
        elif choice == "2":
            print("\n启动定时调度器...")
            scheduler.run_scheduler()
            
        elif choice == "3":
            print("\n系统状态:")
            print(f"• 当前时间: {scheduler.today} {scheduler.current_time}")
            print(f"• 日志文件: {scheduler.log_file}")
            print(f"• 分析群组: {scheduler.groups['analysis']}")
            print(f"• 下次执行: 明天 09:00")
            
        else:
            print("无效选择")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()