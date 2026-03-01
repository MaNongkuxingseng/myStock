"""
myStock 1.1版本 - 工具函数模块
提供通用的辅助函数和工具
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# 设置日志
logger = logging.getLogger("mystock.utils")

class Timer:
    """性能计时器"""
    
    def __init__(self, name: str = "任务"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"开始执行: {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        if exc_type is None:
            logger.info(f"完成执行: {self.name} - 耗时: {elapsed:.2f}秒")
        else:
            logger.error(f"执行失败: {self.name} - 耗时: {elapsed:.2f}秒 - 错误: {exc_val}")
    
    @property
    def elapsed(self) -> float:
        """获取耗时"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time

def format_time(timestamp: Optional[float] = None, 
                fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间"""
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime(fmt)

def parse_time(time_str: str, 
               fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析时间字符串"""
    return datetime.strptime(time_str, fmt)

def is_trading_day(date: Optional[datetime] = None) -> bool:
    """
    判断是否为交易日
    注意：这里需要接入实际的交易日历API
    """
    if date is None:
        date = datetime.now()
    
    # 周末不是交易日
    if date.weekday() >= 5:  # 5=周六, 6=周日
        return False
    
    # 这里可以添加节假日判断
    # 实际使用时需要接入交易日历API
    
    return True

def get_next_trading_time(current_time: Optional[datetime] = None) -> datetime:
    """获取下一个交易时间"""
    if current_time is None:
        current_time = datetime.now()
    
    # 如果是交易日且在交易时间内
    if is_trading_day(current_time):
        hour = current_time.hour
        if hour < 9:
            # 早于9点，返回9点
            return current_time.replace(hour=9, minute=0, second=0, microsecond=0)
        elif hour < 15 or (hour == 15 and current_time.minute < 30):
            # 在交易时间内，返回当前时间
            return current_time
        else:
            # 超过15:30，返回下一个交易日的9点
            pass
    
    # 寻找下一个交易日
    next_day = current_time + timedelta(days=1)
    while not is_trading_day(next_day):
        next_day += timedelta(days=1)
    
    return next_day.replace(hour=9, minute=0, second=0, microsecond=0)

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """安全地解析JSON字符串"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(data: Any, indent: int = 2, default: Any = None) -> str:
    """安全地序列化为JSON字符串"""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=default)
    except (TypeError, ValueError):
        return "{}"

def format_number(value: float, precision: int = 2) -> str:
    """格式化数字"""
    if value is None:
        return "N/A"
    
    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.{precision}f}B"
    elif abs(value) >= 1_000_000:
        return f"{value/1_000_000:.{precision}f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.{precision}f}K"
    else:
        return f"{value:.{precision}f}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """计算百分比变化"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def validate_stock_code(code: str) -> bool:
    """验证股票代码格式"""
    if not code or not isinstance(code, str):
        return False
    
    # 移除可能的空格和特殊字符
    code = code.strip().upper()
    
    # 检查长度
    if len(code) != 6:
        return False
    
    # 检查是否全数字
    if not code.isdigit():
        return False
    
    # 检查交易所代码
    exchange = code[:2]
    if exchange not in ["00", "30", "60", "68", "83", "87", "88", "89"]:
        return False
    
    return True

def get_file_size(file_path: Union[str, Path]) -> str:
    """获取文件大小（人类可读格式）"""
    path = Path(file_path)
    if not path.exists():
        return "文件不存在"
    
    size = path.stat().st_size
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def create_backup(file_path: Union[str, Path], 
                  backup_dir: Optional[Union[str, Path]] = None) -> bool:
    """创建文件备份"""
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"文件不存在，无法备份: {file_path}")
            return False
        
        if backup_dir is None:
            backup_dir = path.parent / "backups"
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"{path.stem}_{timestamp}{path.suffix}"
        
        import shutil
        shutil.copy2(path, backup_file)
        
        logger.info(f"文件备份成功: {file_path} -> {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"文件备份失败: {file_path} - 错误: {e}")
        return False

if __name__ == "__main__":
    # 测试工具函数
    print("=== 工具函数测试 ===")
    
    # 测试计时器
    with Timer("测试任务"):
        time.sleep(0.1)
    
    # 测试时间格式化
    print(f"当前时间: {format_time()}")
    
    # 测试数字格式化
    print(f"数字格式化: {format_number(1234567.89)}")
    
    # 测试百分比计算
    print(f"百分比变化: {calculate_percentage_change(100, 120):.2f}%")
    
    # 测试股票代码验证
    test_codes = ["000001", "600000", "123456", "ABC123", ""]
    for code in test_codes:
        valid = validate_stock_code(code)
        print(f"股票代码 {code}: {'有效' if valid else '无效'}")
    
    print("=" * 40)