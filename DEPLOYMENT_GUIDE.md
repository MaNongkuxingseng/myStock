# myStock系统部署指南

## 📋 系统概述

本系统包含三个核心模块：
1. **myStock集成分析系统** - 结合myStock技术指标的持仓分析
2. **任务管理bot系统** - 独立的任务跟踪和管理bot
3. **早上9点定时推送系统** - 自动化的定时报告推送

## 🚀 快速开始

### 1. 环境检查
```bash
# 检查Python环境
cd G:\openclaw\workspace\_system\agent-home\myStock\instock
python -c "import sys; sys.path.append('D:\\python_libs'); import pymysql; print('环境正常')"

# 检查数据库连接
python -c "
import sys
sys.path.append('D:\\\\python_libs')
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='785091', database='instockdb', port=3306, charset='utf8mb4')
print('数据库连接正常')
conn.close()
"
```

### 2. 更新持仓数据
编辑文件：`instock\monitor\mystock_integrated_analysis.py`
```python
# 第15-35行，更新为你的实际持仓
self.holdings = [
    {
        'code': '你的股票代码',
        'name': '股票名称',
        'quantity': 持仓数量,
        'cost_price': 成本价,
        'portfolio': '组合名称'
    },
    # ... 更多持仓
]
```

### 3. 测试myStock分析
```bash
cd G:\openclaw\workspace\_system\agent-home\myStock\instock
python monitor\mystock_integrated_analysis.py
```

### 4. 测试任务管理
```bash
cd G:\openclaw\workspace\_system\agent-home\myStock\instock
python task_manager\task_management_system.py
```

### 5. 测试定时推送
```bash
cd G:\openclaw\workspace\_system\agent-home\myStock\instock
python scheduler\morning_9am_scheduler.py
# 选择选项1：立即执行一次测试
```

## ⏰ 早上9点定时推送配置

### Windows任务计划配置

#### 方法1：使用批处理文件
创建 `G:\openclaw\workspace\_system\agent-home\myStock\run_9am_task.bat`：
```batch
@echo off
chcp 65001 >nul
echo myStock早上9点定时任务
echo.

cd /d "G:\openclaw\workspace\_system\agent-home\myStock\instock"
python scheduler\morning_9am_scheduler.py --run-once

echo.
echo 任务执行完成
pause
```

#### 方法2：Windows任务计划配置步骤
1. 打开"任务计划程序"
2. 创建基本任务
3. 名称: `myStock早上9点分析`
4. 触发器: 每天，09:00
5. 操作: 启动程序
   - 程序: `python.exe`
   - 参数: `scheduler\morning_9am_scheduler.py --run-once`
   - 起始于: `G:\openclaw\workspace\_system\agent-home\myStock\instock`
6. 条件: 取消"只有在计算机使用交流电源时才启动此任务"
7. 设置: 选中"如果过了计划开始时间，立即启动任务"

### 测试定时任务
```bash
# 手动测试
python scheduler\morning_9am_scheduler.py --run-once

# 查看日志
type logs\scheduler_2026-02-27.log
```

## 🤖 任务管理bot部署

### 1. 创建新Feishu群组
1. 在Feishu中创建新群组，命名为"myStock任务管理"
2. 获取群组ID（类似 `oc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
3. 更新配置文件

### 2. 更新群组配置
编辑 `instock\scheduler\morning_9am_scheduler.py`：
```python
self.groups = {
    'analysis': 'oc_b99df765824c2e59b3fabf287e8d14a2',  # 当前分析群组
    'management': '你的新群组ID'  # 新管理群组
}
```

### 3. 任务管理功能
- **每日报告**: 早上9点推送任务概览
- **任务提醒**: 截止日期前自动提醒
- **进度更新**: 实时更新任务状态
- **复盘机制**: 每周任务复盘

### 4. 添加新任务
```python
from task_manager.task_management_system import TaskManager

manager = TaskManager()
new_task = {
    "title": "任务标题",
    "description": "任务描述",
    "category": "development",  # analysis/monitoring/development/maintenance/communication/review
    "priority": "high",  # critical/high/medium/low
    "assignee": "负责人",
    "due_date": "2026-02-28",
    "notes": "备注信息"
}

task_id = manager.add_task(new_task)
print(f"新任务ID: {task_id}")
```

## 📊 myStock指标分析集成

### 已集成的技术指标
1. **MACD** - 趋势指标
2. **KDJ** - 超买超卖指标
3. **布林带** - 波动性指标
4. **RSI** - 相对强弱指标
5. **成交量分析** - 量价关系

### 分析逻辑
1. 从myStock数据库获取股票数据
2. 计算各项技术指标
3. 综合评分（0-100分）
4. 生成交易建议
5. 风险预警

### 自定义分析规则
编辑 `instock\monitor\mystock_integrated_analysis.py`：
```python
# 技术指标权重
self.indicator_weights = {
    'macd': 0.25,      # 调整权重
    'kdj': 0.20,
    'boll': 0.15,
    'rsi': 0.15,
    'volume': 0.10,
    'trend': 0.15
}

# 预警阈值
PROFIT_ALERT_THRESHOLD = 10    # 盈亏超过10%预警
PRICE_CHANGE_THRESHOLD = 7     # 价格涨跌幅超过7%预警
CONCENTRATION_THRESHOLD = 30   # 单股权重超过30%预警
```

## 📱 消息推送配置

### 当前推送配置
- **分析群组**: `oc_b99df765824c2e59b3fabf287e8d14a2`
- **推送时间**: 每天09:00
- **消息类型**: 
  - myStock持仓分析报告
  - 技术指标分析
  - 操作建议
  - 风险预警

### 消息格式示例
```
⏰ myStock早盘分析报告 2026-02-27 09:00

📈 组合概览
• 持仓数量: 3只
• 总市值: 119,750元
• 总盈亏: +7,250元 (+6.4%)

🔍 技术分析摘要
📈 000001 平安银行
当前价: 13.75 | 盈亏: +10.0%
技术评分: 🟢 78/100 | 权重: 57.4%
技术信号: MACD金叉向上, KDJ超卖
操作建议: 🔴 技术面看好，建议继续持有
```

### 测试消息推送
```bash
# 生成测试消息
python scheduler\morning_9am_scheduler.py --test-message

# 查看生成的消息文件
dir logs\messages\
```

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MySQL服务
net start mysql

# 测试连接
python -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='root', password='785091', database='instockdb')
    print('连接成功')
except Exception as e:
    print(f'连接失败: {e}')
"
```

#### 2. myStock指标计算失败
```bash
# 检查数据表
python -c "
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='785091', database='instockdb')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM cn_stock_selection')
print(f'股票数据记录: {cursor.fetchone()[0]}')
conn.close()
"
```

#### 3. 定时任务不执行
```bash
# 检查任务计划
schtasks /query /tn "myStock早上9点分析"

# 手动测试
python scheduler\morning_9am_scheduler.py --run-once

# 查看日志
type logs\scheduler_*.log | more
```

#### 4. 消息发送失败
```bash
# 检查群组ID配置
python -c "
from scheduler.morning_9am_scheduler import Morning9AMScheduler
scheduler = Morning9AMScheduler()
print(f'分析群组: {scheduler.groups[\"analysis\"]}')
print(f'管理群组: {scheduler.groups[\"management\"]}')
"
```

### 日志文件位置
- **调度器日志**: `instock\scheduler\logs\scheduler_YYYY-MM-DD.log`
- **消息文件**: `instock\scheduler\logs\messages\`
- **执行结果**: `instock\scheduler\logs\execution_YYYY-MM-DD_HHMM.json`

## 📈 监控和维护

### 日常检查
1. **早上9点后**：检查消息是否正常推送
2. **查看日志**：确认任务执行状态
3. **验证数据**：检查分析结果的准确性
4. **更新任务**：维护任务管理系统的任务状态

### 性能监控
```bash
# 查看最近执行情况
dir instock\scheduler\logs\execution_*.json

# 分析执行成功率
python -c "
import json, os, glob
files = glob.glob('instock/scheduler/logs/execution_*.json')
success_count = 0
for f in files[-7:]:  # 最近7天
    try:
        with open(f, 'r') as fp:
            data = json.load(fp)
            if data.get('mystock_analysis', {}).get('success'):
                success_count += 1
    except:
        pass
print(f'最近7天执行成功率: {success_count}/{len(files)}')
"
```

### 数据备份
```bash
# 备份任务数据
copy instock\task_manager\tasks.json instock\task_manager\backup\tasks_$(date +%Y%m%d).json

# 备份配置
copy instock\scheduler\morning_9am_scheduler.py instock\scheduler\backup\
```

## 🚀 扩展计划

### 短期计划（1-2周）
1. ✅ 集成myStock指标计算
2. ✅ 建立早上9点定时推送
3. ⏳ 创建任务管理bot
4. ⏳ 配置新管理群组
5. ⏳ 优化消息格式

### 中期计划（1个月）
1. 实现Feishu API自动推送
2. 添加更多技术指标
3. 实现持仓自动同步
4. 添加移动端通知
5. 优化分析算法

### 长期计划（3个月）
1. 对接券商API
2. 实现自动化交易
3. 添加AI分析模块
4. 多账户管理
5. 高级风险控制

## 📞 支持与反馈

### 问题报告
1. 查看日志文件定位问题
2. 在Feishu群组中反馈
3. 提供错误截图和日志

### 功能请求
1. 在任务管理系统中创建功能请求任务
2. 描述具体需求和场景
3. 指定优先级和截止日期

### 联系方式
- **当前群组**: `oc_b99df765824c2e59b3fabf287e8d14a2`
- **管理群组**: 待创建
- **系统路径**: `G:\openclaw\workspace\_system\agent-home\myStock`

---

**最后更新**: 2026-02-27  
**版本**: 1.0.0  
**状态**: ✅ 可部署运行