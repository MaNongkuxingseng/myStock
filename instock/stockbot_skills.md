# StockBot Agent Skills 配置文件

## 📋 技能概述

StockBot是一个专业的股票监控和分析Agent，集成了实时行情、技术分析、风险管理和智能推送功能。

## 🎯 核心技能

### 1. 实时价格监控
- **功能**: 监控多只股票实时价格
- **数据源**: 新浪财经API + 腾讯财经备用
- **频率**: 可配置（默认5分钟）
- **输出**: 价格更新、涨跌幅计算

### 2. 技术指标分析
- **趋势指标**: MA, EMA, MACD, 布林带
- **动量指标**: RSI, KDJ, WR, CCI
- **成交量指标**: OBV, 量比, MFI
- **波动率指标**: ATR, 布林带宽度

### 3. 智能警报系统
- **警报级别**: 严重(🔴)、警告(🟡)、信息(🟢)
- **触发条件**: 止损、止盈、关键点位、涨跌幅
- **推送渠道**: Feishu群组
- **格式**: 结构化消息 + 操作建议

### 4. 投资组合分析
- **持仓分析**: 市值、盈亏、权重
- **风险评估**: 集中度、波动性、市场风险
- **优化建议**: 减仓、加仓、调仓建议
- **绩效评估**: 收益率、夏普比率、最大回撤

### 5. 市场情绪分析
- **大盘监控**: 主要指数涨跌
- **板块分析**: 行业轮动
- **资金流向**: 主力资金、北向资金
- **情绪指标**: 恐慌指数、多空比

## 🔧 技能配置

### 配置文件: `price_monitor_config.json`
```json
{
  "version": "1.1",
  "monitored_stocks": [
    {
      "code": "603949",
      "name": "雪龙集团",
      "current_price": 19.39,
      "monitor_rules": {
        "buy_alert": 19.0,
        "sell_alert": 20.6,
        "stop_loss": 18.5,
        "support": 18.8,
        "resistance": 20.0,
        "change_threshold": 3.0
      }
    }
  ],
  "notification_settings": {
    "feishu_group": "oc_b99df765824c2e59b3fabf287e8d14a2",
    "check_interval_minutes": 5
  }
}
```

### 技术指标配置
```python
# 在technical_indicators.py中配置
indicators_config = {
    'trend_indicators': ['MA', 'EMA', 'MACD', 'BOLL'],
    'momentum_indicators': ['RSI', 'KDJ', 'WR', 'CCI'],
    'volume_indicators': ['OBV', 'VOLRATIO', 'MFI'],
    'volatility_indicators': ['ATR', 'BBWIDTH']
}
```

## 🚀 使用方式

### 启动StockBot
```bash
# 进入目录
cd G:\openclaw\workspace\_system\agent-home\myStock\instock

# 启动StockBot Agent
python stockbot_agent.py

# 选择模式:
# 1. 单次分析并推送
# 2. 持续监控
# 3. 测试技术指标
# 4. 查看系统状态
```

### 定时任务配置
```bash
# Windows任务计划
# 每天09:00执行分析
python stockbot_agent.py --mode single

# 每5分钟持续监控
python stockbot_agent.py --mode continuous
```

### API调用示例
```python
from stockbot_agent import StockBotAgent

# 初始化Agent
agent = StockBotAgent()

# 单次分析
report = agent.run_single_analysis()

# 获取技术分析
technicals = agent.analyze_stock_technicals('603949')

# 检查警报
alerts = agent.check_price_alerts()

# 分析投资组合
portfolio = agent.analyze_portfolio()
```

## 📊 输出格式

### Feishu消息格式
```
📊 StockBot分析报告 2026-02-27 13:15:00

🌐 市场概览
🟢 上证指数: 4128.90 (-0.43%)
🔴 深证成指: 14375.25 (-0.89%)

📈 股票分析
🟢 603949 雪龙集团: 19.35元 (-1.28%)
   技术评分: 65/100 | 趋势: weak_bearish | 建议: hold

💰 投资组合
总市值: 107,455元
总盈亏: -2,294元
风险等级: medium

🚨 警报列表
🔴 600537 亿晶光电涨跌幅9.2%超过阈值

💡 操作建议
🔴 雪龙集团仓位过重(52.3%)，建议减仓
🟡 亿晶光电大幅上涨，考虑部分获利了结

---
StockBot Agent v1.0 | 数据源: 新浪财经实时API
```

### 数据结构
```python
{
  "timestamp": "2026-02-27T13:15:00",
  "market_overview": {
    "indices": {...},
    "sentiment": "bearish",
    "trend": "sideways"
  },
  "stock_analysis": [
    {
      "code": "603949",
      "name": "雪龙集团",
      "current_price": 19.35,
      "change": -1.28,
      "technicals": {
        "trend": {...},
        "momentum": {...},
        "summary": {
          "technical_score": 65,
          "trend_strength": "weak_bearish",
          "recommendation": "hold"
        }
      }
    }
  ],
  "alerts": [...],
  "recommendations": [...]
}
```

## 🔄 技能扩展

### 添加新指标
1. 在`technical_indicators.py`中添加计算方法
2. 在`analyze_stock_technicals`中集成
3. 更新配置和报告格式

### 添加新数据源
1. 在`real_time_data.py`中添加API接口
2. 实现数据解析方法
3. 更新`get_stock_data`方法支持新源

### 添加新警报类型
1. 在`check_single_stock_alerts`中添加检查逻辑
2. 定义警报级别和消息格式
3. 更新报告生成逻辑

## 📈 性能优化

### 缓存策略
- 价格数据: 30秒缓存
- 技术指标: 按需计算
- 历史数据: 本地存储

### 并发处理
- 多股票并行获取
- 异步API调用
- 批量数据处理

### 错误处理
- API失败自动重试
- 备用数据源切换
- 优雅降级机制

## 🛠️ 维护指南

### 日常维护
1. 检查API连接状态
2. 更新监控规则
3. 清理历史数据
4. 备份配置文件

### 故障排除
```bash
# 测试API连接
python real_time_data.py

# 测试技术指标
python technical_indicators.py

# 检查配置
python -c "import json; print(json.load(open('price_monitor_config.json')))"
```

### 日志管理
- 分析日志: `logs/analysis_*.log`
- 警报日志: `logs/alerts_*.log`
- 错误日志: `logs/errors_*.log`

## 🔗 依赖关系

### Python库
```txt
requests>=2.25.0
numpy>=1.20.0
pandas>=1.3.0 (可选，用于高级分析)
```

### 数据源
- 新浪财经: http://hq.sinajs.cn/
- 腾讯财经: http://qt.gtimg.cn/
- 东方财富: http://push2.eastmoney.com/

### 推送渠道
- Feishu: 当前群组 `oc_b99df765824c2e59b3fabf287e8d14a2`
- 可扩展: 微信、Telegram、Email

## 📝 版本历史

### v1.0 (2026-02-27)
- ✅ 基础价格监控
- ✅ 技术指标分析
- ✅ 智能警报系统
- ✅ Feishu消息推送
- ✅ 投资组合分析

### v1.1 (计划)
- ⚙️ 更多技术指标
- ⚙️ 历史数据分析
- ⚙️ 多时间框架
- ⚙️ 机器学习预测

### v2.0 (规划)
- 🤖 AI智能建议
- 🤖 自动化交易
- 🤖 多账户管理
- 🤖 Web管理界面

## 💡 最佳实践

### 监控规则设置
1. 止损位: 成本价-7%
2. 止盈位: 成本价+10-15%
3. 买入提醒: 支撑位附近
4. 涨跌幅阈值: 3-5%

### 风险控制
1. 单股仓位 < 30%
2. 总仓位 < 80%
3. 止损严格执行
4. 定期复盘调整

### 系统优化
1. 定时清理日志
2. 定期更新配置
3. 监控系统资源
4. 备份重要数据

---

**StockBot将持续优化和扩展，为您的投资决策提供专业支持。**