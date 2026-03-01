"""
myStock 1.1版本 - 推送调度模块
负责管理9个时间点的推送调度和执行
"""

import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from ..utils.helpers import Timer, is_trading_day, format_time

logger = logging.getLogger("mystock.push.scheduler")

class PushTimePoint(Enum):
    """推送时间点枚举"""
    MORNING_ANALYSIS = "09:00"      # 早盘分析
    OPENING_MONITOR = "09:30"       # 开盘监控
    MARKET_OBSERVATION = "10:00"    # 市场观察
    PRE_NOON_SUMMARY = "11:00"      # 午前总结
    AFTERNOON_ANALYSIS = "13:00"    # 午后分析
    INTRA_MONITOR = "14:00"         # 盘中监控
    LATE_SESSION_OBSERVATION = "14:30"  # 尾盘观察
    CLOSING_SUMMARY = "15:00"       # 收盘总结
    EVENING_REVIEW = "20:00"        # 晚间复盘

class PushStatus(Enum):
    """推送状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    SUCCESS = "success"      # 执行成功
    FAILED = "failed"        # 执行失败
    SKIPPED = "skipped"      # 跳过（非交易日等）
    DISABLED = "disabled"    # 已禁用

class PushTask:
    """推送任务"""
    
    def __init__(self, 
                 time_point: PushTimePoint,
                 name: str,
                 handler: Callable,
                 enabled: bool = True,
                 require_trading_day: bool = True):
        self.time_point = time_point
        self.name = name
        self.handler = handler
        self.enabled = enabled
        self.require_trading_day = require_trading_day
        self.last_run = None
        self.last_status = PushStatus.PENDING
        self.last_result = None
        self.error_message = None
        
    def should_run(self) -> bool:
        """判断任务是否应该执行"""
        if not self.enabled:
            logger.debug(f"任务已禁用: {self.name}")
            return False
        
        if self.require_trading_day and not is_trading_day():
            logger.debug(f"非交易日，跳过任务: {self.name}")
            return False
        
        return True
    
    def execute(self) -> Dict[str, Any]:
        """执行任务"""
        if not self.should_run():
            self.last_status = PushStatus.SKIPPED
            return {"status": "skipped", "reason": "任务禁用或非交易日"}
        
        self.last_status = PushStatus.RUNNING
        self.last_run = datetime.now()
        self.error_message = None
        
        try:
            with Timer(f"推送任务执行: {self.name}"):
                result = self.handler()
                self.last_result = result
                self.last_status = PushStatus.SUCCESS
                logger.info(f"推送任务执行成功: {self.name}")
                return {"status": "success", "result": result}
                
        except Exception as e:
            self.last_status = PushStatus.FAILED
            self.error_message = str(e)
            logger.error(f"推送任务执行失败: {self.name} - 错误: {e}")
            return {"status": "failed", "error": str(e)}
    
    def get_info(self) -> Dict[str, Any]:
        """获取任务信息"""
        return {
            "time_point": self.time_point.value,
            "name": self.name,
            "enabled": self.enabled,
            "require_trading_day": self.require_trading_day,
            "last_run": format_time(self.last_run.timestamp()) if self.last_run else None,
            "last_status": self.last_status.value,
            "last_result": self.last_result if self.last_result else None,
            "error_message": self.error_message
        }

class PushScheduler:
    """推送调度器"""
    
    def __init__(self):
        self.tasks: Dict[PushTimePoint, PushTask] = {}
        self.scheduler_thread = None
        self.running = False
        self.history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        
        logger.info("推送调度器初始化完成")
    
    def register_task(self, task: PushTask):
        """注册推送任务"""
        if task.time_point in self.tasks:
            logger.warning(f"时间点 {task.time_point.value} 已存在任务，将被覆盖")
        
        self.tasks[task.time_point] = task
        logger.info(f"注册推送任务: {task.name} - 时间点: {task.time_point.value}")
    
    def register_default_tasks(self):
        """注册默认的9个时间点任务"""
        default_tasks = [
            PushTask(
                time_point=PushTimePoint.MORNING_ANALYSIS,
                name="早盘分析",
                handler=self._generate_morning_analysis,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.OPENING_MONITOR,
                name="开盘监控",
                handler=self._generate_opening_monitor,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.MARKET_OBSERVATION,
                name="市场观察",
                handler=self._generate_market_observation,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.PRE_NOON_SUMMARY,
                name="午前总结",
                handler=self._generate_pre_noon_summary,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.AFTERNOON_ANALYSIS,
                name="午后分析",
                handler=self._generate_afternoon_analysis,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.INTRA_MONITOR,
                name="盘中监控",
                handler=self._generate_intra_monitor,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.LATE_SESSION_OBSERVATION,
                name="尾盘观察",
                handler=self._generate_late_session_observation,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.CLOSING_SUMMARY,
                name="收盘总结",
                handler=self._generate_closing_summary,
                enabled=True,
                require_trading_day=True
            ),
            PushTask(
                time_point=PushTimePoint.EVENING_REVIEW,
                name="晚间复盘",
                handler=self._generate_evening_review,
                enabled=True,
                require_trading_day=False  # 晚间复盘在非交易日也可执行
            )
        ]
        
        for task in default_tasks:
            self.register_task(task)
        
        logger.info(f"已注册 {len(default_tasks)} 个默认推送任务")
    
    def _schedule_task(self, task: PushTask):
        """调度单个任务"""
        def job():
            result = task.execute()
            self._record_history(task, result)
        
        # 使用schedule库调度任务
        schedule.every().day.at(task.time_point.value).do(job)
        logger.debug(f"已调度任务: {task.name} - 时间: {task.time_point.value}")
    
    def _record_history(self, task: PushTask, result: Dict[str, Any]):
        """记录执行历史"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_name": task.name,
            "time_point": task.time_point.value,
            "status": result.get("status"),
            "result": result.get("result"),
            "error": result.get("error")
        }
        
        self.history.append(history_entry)
        
        # 限制历史记录大小
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
        
        logger.debug(f"记录推送历史: {task.name} - 状态: {result.get('status')}")
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return
        
        # 注册默认任务（如果尚未注册）
        if not self.tasks:
            self.register_default_tasks()
        
        # 调度所有任务
        for task in self.tasks.values():
            self._schedule_task(task)
        
        # 启动调度线程
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("推送调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if not self.running:
            logger.warning("调度器未在运行")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("推送调度器已停止")
    
    def _run_scheduler(self):
        """调度器运行循环"""
        logger.info("调度器线程开始运行")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                logger.error(f"调度器运行异常: {e}")
                time.sleep(5)  # 异常后等待5秒
        
        logger.info("调度器线程结束运行")
    
    def trigger_manual_push(self, time_point: PushTimePoint) -> Dict[str, Any]:
        """手动触发推送"""
        if time_point not in self.tasks:
            return {"status": "error", "message": f"未找到时间点 {time_point.value} 的任务"}
        
        task = self.tasks[time_point]
        logger.info(f"手动触发推送: {task.name}")
        
        result = task.execute()
        self._record_history(task, result)
        
        return result
    
    def get_next_push_time(self) -> Optional[datetime]:
        """获取下一个推送时间"""
        next_run = None
        
        for task in self.tasks.values():
            if not task.enabled:
                continue
            
            # 这里简化处理，实际应该计算每个任务的下次运行时间
            # schedule库没有直接获取下次运行时间的API
            pass
        
        return next_run
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        enabled_tasks = sum(1 for task in self.tasks.values() if task.enabled)
        disabled_tasks = len(self.tasks) - enabled_tasks
        
        # 统计历史状态
        status_counts = {}
        for entry in self.history[-24:]:  # 最近24条记录
            status = entry.get("status")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "enabled_tasks": enabled_tasks,
            "disabled_tasks": disabled_tasks,
            "history_count": len(self.history),
            "recent_status": status_counts,
            "tasks": {tp.value: task.get_info() for tp, task in self.tasks.items()}
        }
    
    # 以下是默认的任务处理函数（占位符，实际由其他模块实现）
    def _generate_morning_analysis(self):
        """生成早盘分析"""
        return {"content": "早盘分析内容", "type": "morning_analysis"}
    
    def _generate_opening_monitor(self):
        """生成开盘监控"""
        return {"content": "开盘监控内容", "type": "opening_monitor"}
    
    def _generate_market_observation(self):
        """生成市场观察"""
        return {"content": "市场观察内容", "type": "market_observation"}
    
    def _generate_pre_noon_summary(self):
        """生成午前总结"""
        return {"content": "午前总结内容", "type": "pre_noon_summary"}
    
    def _generate_afternoon_analysis(self):
        """生成午后分析"""
        return {"content": "午后分析内容", "type": "afternoon_analysis"}
    
    def _generate_intra_monitor(self):
        """生成盘中监控"""
        return {"content": "盘中监控内容", "type": "intra_monitor"}
    
    def _generate_late_session_observation(self):
        """生成尾盘观察"""
        return {"content": "尾盘观察内容", "type": "late_session_observation"}
    
    def _generate_closing_summary(self):
        """生成收盘总结"""
        return {"content": "收盘总结内容", "type": "closing_summary"}
    
    def _generate_evening_review(self):
        """生成晚间复盘"""
        return {"content": "晚间复盘内容", "type": "evening_review"}

# 全局推送调度器实例
push_scheduler = PushScheduler()

def init_push_scheduler():
    """初始化推送调度器"""
    push_scheduler.register_default_tasks()
    logger.info("推送调度器初始化完成")
    return push_scheduler

if __name__ == "__main__":
    # 测试推送调度模块
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    print("=== 推送调度模块测试 ===")
    
    # 初始化
    scheduler = init_push_scheduler()
    
    # 测试任务注册
    print(f"已注册任务数量: {len(scheduler.tasks)}")
    for time_point, task in scheduler.tasks.items():
        print(f"  {time_point.value}: {task.name} - 启用: {task.enabled}")
    
    # 测试状态获取
    status = scheduler.get_status()
    print(f"\n调度器状态:")
    print(f"  运行中: {status['running']}")
    print(f"  总任务数: {status['total_tasks']}")
    print(f"  启用任务: {status['enabled_tasks']}")
    print(f"  禁用任务: {status['disabled_tasks']}")
    
    # 测试手动触发（模拟）
    print("\n测试手动触发推送:")
    test_time_point = PushTimePoint.MORNING_ANALYSIS
    result = scheduler.trigger_manual_push(test_time_point)
    print(f"  手动触发 {test_time_point.value}: {result['status']}")
    
    # 测试任务信息
    print("\n任务详细信息:")
    for time_point, task in scheduler.tasks.items():
        info = task.get_info()
        print(f"  {info['name']}:")
        print(f"    时间点: {info['time_point']}")
        print(f"    状态: {info['last_status']}")
        print(f"    最后运行: {info['last_run']}")
    
    # 测试交易日判断
    print(f"\n当前是否为交易日: {is_trading_day()}")
    
    print("\n" + "=" * 40)