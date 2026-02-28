#!/usr/bin/env python3
"""
任务管理系统 - 独立的bot
用于任务跟踪、执行情况更新、复盘提醒
推送到新的群组专门用于分析管理
"""

import sys
import os
import json
from datetime import datetime, timedelta
from enum import Enum

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('D:\\python_libs')

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 待开始
    IN_PROGRESS = "in_progress"  # 进行中
    BLOCKED = "blocked"      # 阻塞
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = "critical"    # 关键
    HIGH = "high"           # 高
    MEDIUM = "medium"       # 中
    LOW = "low"             # 低

class TaskCategory(Enum):
    """任务类别"""
    ANALYSIS = "analysis"    # 分析任务
    MONITORING = "monitoring" # 监控任务
    DEVELOPMENT = "development" # 开发任务
    MAINTENANCE = "maintenance" # 维护任务
    COMMUNICATION = "communication" # 沟通任务
    REVIEW = "review"        # 复盘任务

class TaskManager:
    """任务管理器"""
    
    def __init__(self, db_path=None):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.current_time = datetime.now().strftime('%H:%M:%S')
        
        # 任务存储路径
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = os.path.join(os.path.dirname(__file__), "tasks.json")
        
        # 初始化任务数据库
        self.tasks = self.load_tasks()
        
        # 新群组配置（用于分析管理）
        self.management_group_id = "oc_new_analysis_management_group"  # 需要创建新群组
        self.current_group_id = "oc_b99df765824c2e59b3fabf287e8d14a2"  # 当前群组
    
    def load_tasks(self):
        """加载任务"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.get_default_tasks()
        else:
            return self.get_default_tasks()
    
    def save_tasks(self):
        """保存任务"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def get_default_tasks(self):
        """获取默认任务列表"""
        return {
            "tasks": [
                {
                    "id": "TASK-001",
                    "title": "myStock持仓分析系统开发",
                    "description": "开发集成myStock指标计算的持仓分析系统",
                    "category": TaskCategory.DEVELOPMENT.value,
                    "priority": TaskPriority.HIGH.value,
                    "status": TaskStatus.COMPLETED.value,
                    "assignee": "valenbot",
                    "created_at": self.today,
                    "due_date": self.today,
                    "progress": 100,
                    "dependencies": [],
                    "notes": "已完成基础框架，需要集成myStock指标计算",
                    "updates": [
                        {
                            "timestamp": f"{self.today} 05:00",
                            "content": "任务创建",
                            "author": "system"
                        }
                    ]
                },
                {
                    "id": "TASK-002",
                    "title": "早上9点定时推送配置",
                    "description": "配置每天早上9点自动推送分析报告",
                    "category": TaskCategory.MONITORING.value,
                    "priority": TaskPriority.CRITICAL.value,
                    "status": TaskStatus.IN_PROGRESS.value,
                    "assignee": "valenbot",
                    "created_at": self.today,
                    "due_date": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    "progress": 70,
                    "dependencies": ["TASK-001"],
                    "notes": "需要配置Windows任务计划",
                    "updates": [
                        {
                            "timestamp": f"{self.today} 05:15",
                            "content": "开始配置定时任务",
                            "author": "valenbot"
                        }
                    ]
                },
                {
                    "id": "TASK-003",
                    "title": "任务管理bot开发",
                    "description": "开发独立的bot用于任务跟踪管理",
                    "category": TaskCategory.DEVELOPMENT.value,
                    "priority": TaskPriority.HIGH.value,
                    "status": TaskStatus.IN_PROGRESS.value,
                    "assignee": "valenbot",
                    "created_at": self.today,
                    "due_date": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    "progress": 60,
                    "dependencies": [],
                    "notes": "当前正在开发中",
                    "updates": [
                        {
                            "timestamp": f"{self.today} 05:20",
                            "content": "开始开发任务管理模块",
                            "author": "valenbot"
                        }
                    ]
                },
                {
                    "id": "TASK-004",
                    "title": "新群组创建与配置",
                    "description": "创建专门用于分析管理的新群组",
                    "category": TaskCategory.COMMUNICATION.value,
                    "priority": TaskPriority.MEDIUM.value,
                    "status": TaskStatus.PENDING.value,
                    "assignee": "valen",
                    "created_at": self.today,
                    "due_date": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                    "progress": 0,
                    "dependencies": ["TASK-003"],
                    "notes": "需要手动创建Feishu群组",
                    "updates": []
                },
                {
                    "id": "TASK-005",
                    "title": "myStock数据源验证",
                    "description": "验证myStock数据库连接和数据质量",
                    "category": TaskCategory.MAINTENANCE.value,
                    "priority": TaskPriority.MEDIUM.value,
                    "status": TaskStatus.IN_PROGRESS.value,
                    "assignee": "valenbot",
                    "created_at": self.today,
                    "due_date": self.today,
                    "progress": 80,
                    "dependencies": [],
                    "notes": "数据库连接正常，需要验证指标计算",
                    "updates": [
                        {
                            "timestamp": f"{self.today} 05:10",
                            "content": "数据库连接测试通过",
                            "author": "valenbot"
                        }
                    ]
                },
                {
                    "id": "TASK-006",
                    "title": "每周复盘机制建立",
                    "description": "建立每周任务复盘和总结机制",
                    "category": TaskCategory.REVIEW.value,
                    "priority": TaskPriority.MEDIUM.value,
                    "status": TaskStatus.PENDING.value,
                    "assignee": "valenbot",
                    "created_at": self.today,
                    "due_date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                    "progress": 0,
                    "dependencies": ["TASK-003", "TASK-004"],
                    "notes": "需要设计复盘模板和流程",
                    "updates": []
                }
            ],
            "last_updated": f"{self.today} {self.current_time}",
            "version": "1.0.0"
        }
    
    def add_task(self, task_data):
        """添加新任务"""
        task_id = f"TASK-{len(self.tasks['tasks']) + 1:03d}"
        
        task = {
            "id": task_id,
            "title": task_data.get("title", "未命名任务"),
            "description": task_data.get("description", ""),
            "category": task_data.get("category", TaskCategory.ANALYSIS.value),
            "priority": task_data.get("priority", TaskPriority.MEDIUM.value),
            "status": task_data.get("status", TaskStatus.PENDING.value),
            "assignee": task_data.get("assignee", "未分配"),
            "created_at": self.today,
            "due_date": task_data.get("due_date", self.today),
            "progress": task_data.get("progress", 0),
            "dependencies": task_data.get("dependencies", []),
            "notes": task_data.get("notes", ""),
            "updates": [
                {
                    "timestamp": f"{self.today} {self.current_time}",
                    "content": "任务创建",
                    "author": task_data.get("author", "system")
                }
            ]
        }
        
        self.tasks['tasks'].append(task)
        self.tasks['last_updated'] = f"{self.today} {self.current_time}"
        self.save_tasks()
        
        return task_id
    
    def update_task(self, task_id, updates):
        """更新任务"""
        for task in self.tasks['tasks']:
            if task['id'] == task_id:
                # 更新任务字段
                for key, value in updates.items():
                    if key not in ['id', 'created_at', 'updates']:
                        task[key] = value
                
                # 添加更新记录
                task['updates'].append({
                    "timestamp": f"{self.today} {self.current_time}",
                    "content": updates.get("update_note", "任务更新"),
                    "author": updates.get("author", "system")
                })
                
                self.tasks['last_updated'] = f"{self.today} {self.current_time}"
                self.save_tasks()
                return True
        
        return False
    
    def get_task_summary(self):
        """获取任务摘要"""
        total = len(self.tasks['tasks'])
        completed = sum(1 for t in self.tasks['tasks'] if t['status'] == TaskStatus.COMPLETED.value)
        in_progress = sum(1 for t in self.tasks['tasks'] if t['status'] == TaskStatus.IN_PROGRESS.value)
        pending = sum(1 for t in self.tasks['tasks'] if t['status'] == TaskStatus.PENDING.value)
        blocked = sum(1 for t in self.tasks['tasks'] if t['status'] == TaskStatus.BLOCKED.value)
        
        # 计算总体进度
        total_progress = sum(t['progress'] for t in self.tasks['tasks']) / total if total > 0 else 0
        
        # 按优先级统计
        critical = sum(1 for t in self.tasks['tasks'] if t['priority'] == TaskPriority.CRITICAL.value)
        high = sum(1 for t in self.tasks['tasks'] if t['priority'] == TaskPriority.HIGH.value)
        
        # 即将到期的任务
        today = datetime.now().date()
        overdue = 0
        due_soon = 0
        
        for task in self.tasks['tasks']:
            if task['status'] not in [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]:
                try:
                    due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                    days_until_due = (due_date - today).days
                    
                    if days_until_due < 0:
                        overdue += 1
                    elif days_until_due <= 2:
                        due_soon += 1
                except:
                    pass
        
        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "blocked": blocked,
            "overall_progress": round(total_progress, 1),
            "critical_tasks": critical,
            "high_priority_tasks": high,
            "overdue_tasks": overdue,
            "due_soon_tasks": due_soon,
            "last_updated": self.tasks['last_updated']
        }
    
    def generate_daily_report(self):
        """生成每日任务报告"""
        summary = self.get_task_summary()
        
        report = f"""📋 **任务管理日报** {self.today}

📊 **任务概览**
• 总任务数: {summary['total_tasks']}
• 已完成: {summary['completed']}
• 进行中: {summary['in_progress']}
• 待开始: {summary['pending']}
• 已阻塞: {summary['blocked']}
• 总体进度: {summary['overall_progress']}%

⚠️ **重点关注**
• 关键任务: {summary['critical_tasks']}个
• 高优先级: {summary['high_priority_tasks']}个
• 已逾期: {summary['overdue_tasks']}个
• 即将到期: {summary['due_soon_tasks']}个

🚀 **今日进展**
"""
        
        # 今日有更新的任务
        today_updates = []
        for task in self.tasks['tasks']:
            if task['updates']:
                latest_update = task['updates'][-1]
                if latest_update['timestamp'].startswith(self.today):
                    today_updates.append({
                        'task': task['title'],
                        'update': latest_update['content'],
                        'progress': task['progress']
                    })
        
        if today_updates:
            for update in today_updates[:5]:  # 最多显示5个
                report += f"• {update['task']}: {update['update']} (进度: {update['progress']}%)\n"
        else:
            report += "• 今日暂无任务更新\n"
        
        # 高优先级任务列表
        report += f"\n🔴 **高优先级任务**\n"
        high_priority = [t for t in self.tasks['tasks'] if t['priority'] in [TaskPriority.CRITICAL.value, TaskPriority.HIGH.value] 
                        and t['status'] != TaskStatus.COMPLETED.value]
        
        if high_priority:
            for task in high_priority[:3]:  # 最多显示3个
                status_emoji = "🟢" if task['status'] == TaskStatus.COMPLETED.value else \
                              "🟡" if task['status'] == TaskStatus.IN_PROGRESS.value else \
                              "🔴" if task['status'] == TaskStatus.BLOCKED.value else "⚪"
                
                report += f"{status_emoji} {task['title']}\n"
                report += f"  进度: {task['progress']}% | 负责人: {task['assignee']} | 截止: {task['due_date']}\n"
        else:
            report += "• 暂无高优先级任务\n"
        
        # 阻塞任务
        blocked_tasks = [t for t in self.tasks['tasks'] if t['status'] == TaskStatus.BLOCKED.value]
        if blocked_tasks:
            report += f"\n🚧 **阻塞任务**\n"
            for task in blocked_tasks[:2]:  # 最多显示2个
                report += f"• {task['title']}: {task.get('notes', '需要解决阻塞问题')}\n"
        
        # 下一步行动
        report += f"""
📅 **下一步行动**
1. 处理高优先级任务
2. 解决阻塞问题
3. 更新任务进度
4. 准备明日计划

🔄 **系统状态**
• 任务数据库: ✅ 正常
• 自动提醒: ⚙️ 配置中
• 群组推送: 📱 准备就绪

---
**任务管理系统 | 每日报告**
报告时间: {self.today} {self.current_time}
下次报告: 明日 09:00
"""
        
        return report
    
    def generate_reminder_message(self, task):
        """生成任务提醒消息"""
        due_date = task['due_date']
        today = datetime.now().date()
        
        try:
            due = datetime.strptime(due_date, '%Y-%m-%d').date()
            days_left = (due - today).days
            
            if days_left < 0:
                urgency = "🔴 已逾期"
            elif days_left == 0:
                urgency = "🟡 今日截止"
            elif days_left <= 2:
                urgency = "🟡 即将截止"
            else:
                urgency = "🟢 进行中"
        except:
            urgency = "⚪ 未设置截止日期"
        
        message = f"""⏰ **任务提醒** {task['id']}

📝 **任务信息**
• 标题: {task['title']}
• 负责人: {task['assignee']}
• 截止日期: {due_date} ({urgency})
• 当前进度: {task['progress']}%
• 状态: {task['status']}

📋 **任务描述**
{task['description']}

💡 **最新进展**
"""
        
        if task['updates']:
            latest = task['updates'][-1]
            message += f"{latest['content']} ({latest['timestamp']})\n"
        else:
            message += "暂无更新记录\n"
        
        if task.get('notes'):
            message += f"\n📌 **备注**\n{task['notes']}\n"
        
        message += f"""
---
请及时更新任务进度，确保按时完成。
"""
        
        return message
    
    def check_and_send_reminders(self):
        """检查并发送提醒"""
        today = datetime.now().date()
        reminders = []
        
        for task in self.tasks['tasks']:
            if task['status'] in [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]:
                continue
            
            try:
                due_date