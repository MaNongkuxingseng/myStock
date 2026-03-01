"""
myStock 1.1版本 - 配置文件
版本: 1.1.0
创建时间: 2026-03-01
"""

import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "src" / "config"

# 确保目录存在
for directory in [DATA_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# 数据库配置
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",  # 实际使用时需要配置
    "database": "mystock",
    "charset": "utf8mb4",
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 3600
}

# 推送系统配置
PUSH_SYSTEM_CONFIG = {
    "time_points": {
        "09:00": {"name": "早盘分析", "enabled": True},
        "09:30": {"name": "开盘监控", "enabled": True},
        "10:00": {"name": "市场观察", "enabled": True},
        "11:00": {"name": "午前总结", "enabled": True},
        "13:00": {"name": "午后分析", "enabled": True},
        "14:00": {"name": "盘中监控", "enabled": True},
        "14:30": {"name": "尾盘观察", "enabled": True},
        "15:00": {"name": "收盘总结", "enabled": True},
        "20:00": {"name": "晚间复盘", "enabled": True}
    },
    "content_types": ["market", "signals", "risk", "suggestions", "status"],
    "fallback_enabled": True,
    "holiday_skip": True
}

# 数据分析配置
ANALYSIS_CONFIG = {
    "indicators": {
        "macd": {"fast": 12, "slow": 26, "signal": 9},
        "rsi": {"periods": [6, 12, 24]},
        "kdj": {"n": 9, "m1": 3, "m2": 3},
        "bollinger": {"period": 20, "std_dev": 2},
        "cci": {"period": 20},
        "atr": {"period": 14},
        "williams": {"period": 14}
    },
    "time_frames": ["daily", "60min", "15min", "weekly"],
    "risk_levels": {
        "low": 0.3,
        "medium": 0.6,
        "high": 0.8
    }
}

# 性能配置
PERFORMANCE_CONFIG = {
    "cache_enabled": True,
    "cache_ttl": 300,  # 5分钟
    "query_timeout": 30,
    "max_concurrent_tasks": 5,
    "log_level": "INFO"
}

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "mystock.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "standard",
            "level": "DEBUG"
        }
    },
    "loggers": {
        "mystock": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

# API配置
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "workers": 4,
    "cors_enabled": True
}

# 环境检测
def check_environment():
    """检查开发环境"""
    requirements = {
        "Python版本": "3.8+",
        "MySQL服务": "运行中",
        "Git": "已配置",
        "工作目录": "正确"
    }
    
    status = {}
    
    # 检查Python版本
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    status["Python"] = f"{python_version} ✅" if sys.version_info >= (3, 8) else f"{python_version} ❌"
    
    # 检查目录
    status["工作目录"] = f"{BASE_DIR} ✅" if BASE_DIR.exists() else "❌"
    
    # 检查配置文件
    config_file = CONFIG_DIR / "settings.py"
    status["配置文件"] = "存在 ✅" if config_file.exists() else "缺失 ❌"
    
    return status

if __name__ == "__main__":
    print("=== myStock 1.1版本环境检查 ===")
    env_status = check_environment()
    for key, value in env_status.items():
        print(f"{key}: {value}")
    print("=" * 40)