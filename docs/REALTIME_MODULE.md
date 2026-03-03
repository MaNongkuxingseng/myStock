# myStock 实时数据模块文档

## 概述

实时数据模块为myStock系统添加了实时数据分析能力，支持：
- 实时股票数据获取（新浪、腾讯数据源）
- 实时信号分析
- 实时数据存储
- 实时监控
- Web API接口

## 安装和集成

### 1. 自动集成
运行集成脚本：
```bash
cd myStock
python integrate_realtime.py
```

### 2. 手动集成
1. 将`realtime_module.py`复制到`instock/realtime/`目录
2. 创建`instock/realtime/__init__.py`
3. 更新`instock/__init__.py`

## 核心类

### RealtimeDataManager
实时数据管理器，负责数据获取和存储。

```python
from instock.realtime import RealtimeDataManager

# 初始化
data_manager = RealtimeDataManager()

# 创建实时数据表
data_manager.create_realtime_table()

# 获取实时数据
data = data_manager.get_realtime_data('000034')

# 批量获取
batch_data = data_manager.batch_get_realtime(['000034', '603949'])

# 保存数据
data_manager.save_realtime_data(data)

# 获取历史数据
history = data_manager.get_latest_realtime('000034', limit=10)
```

### RealtimeAnalyzer
实时分析器，负责信号分析和报告生成。

```python
from instock.realtime import RealtimeAnalyzer

# 初始化
analyzer = RealtimeAnalyzer(data_manager)

# 分析单只股票信号
signal = data_manager.analyze_realtime_signal('000034')

# 生成实时报告
analyzer.generate_realtime_report(['000034', '603949'])
```

## 使用示例

### 基本使用
```python
# 参见 examples/realtime_basic.py
```

### 实时监控
```python
# 参见 examples/realtime_monitor.py
```

### 命令行使用
```bash
# 生成实时报告
python realtime_module.py --report

# 启动实时监控
python realtime_module.py --monitor

# 更新实时数据
python realtime_module.py --update --codes=000034,603949
```

## Web API

### 启动API服务
```bash
cd myStock/instock/web
python realtime_api.py
```

### API接口

1. **获取实时数据**
   ```
   GET /api/realtime/data?code=000034&action=data
   ```

2. **获取实时信号**
   ```
   GET /api/realtime/data?code=000034&action=signal
   ```

3. **获取历史数据**
   ```
   GET /api/realtime/data?code=000034&action=history&limit=10
   ```

4. **生成实时报告**
   ```
   GET /api/realtime/report?limit=20
   ```

## 数据源

### 支持的数据源
1. **新浪财经** (`sina`)
   - 地址: `http://hq.sinajs.cn/list=`
   - 格式: `sh000001` 或 `sz000001`

2. **腾讯财经** (`tencent`)
   - 地址: `http://qt.gtimg.cn/q=`
   - 格式: `sh000001` 或 `sz000001`

### 数据缓存
- 默认缓存时间: 60秒
- 避免频繁请求API

## 数据库表

### cn_stock_realtime 表结构
```sql
CREATE TABLE cn_stock_realtime (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50),
    current_price DECIMAL(10,2),
    change_amount DECIMAL(10,2),
    change_percent DECIMAL(10,2),
    open_price DECIMAL(10,2),
    pre_close DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    volume BIGINT,
    amount DECIMAL(15,2),
    timestamp DATETIME NOT NULL,
    data_source VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 信号分析规则

### 信号类型
1. **突破近期均价** (+20分)
   - 当前价 > 3日均价 * 1.02

2. **放量** (+15分)
   - 成交量 > 100万

3. **强势上涨** (+25分)
   - 涨幅 > 3%

4. **弱势下跌** (-20分)
   - 跌幅 < -3%

### 建议等级
- **买入**: 信心度 ≥ 40
- **关注**: 信心度 ≥ 20
- **观望**: 信心度 -20 ~ 20
- **卖出**: 信心度 ≤ -20

## 故障排除

### 常见问题

1. **获取数据失败**
   - 检查网络连接
   - 检查数据源是否可用
   - 检查股票代码格式

2. **数据库连接失败**
   - 检查数据库配置
   - 检查MySQL服务状态
   - 检查用户权限

3. **API服务无法启动**
   - 检查端口是否被占用
   - 检查Python依赖
   - 检查文件权限

### 日志查看
```bash
# 查看实时模块日志
tail -f instock/log/realtime.log
```

## 性能优化

### 建议配置
1. **缓存策略**: 适当调整缓存时间
2. **批量处理**: 使用批量获取接口
3. **异步处理**: 考虑使用异步IO
4. **数据库索引**: 确保关键字段有索引

### 监控建议
1. **监控频率**: 根据需求调整
2. **股票数量**: 控制监控的股票数量
3. **错误处理**: 添加适当的错误处理

## 更新日志

### v1.0.0 (2026-03-02)
- 初始版本发布
- 支持新浪、腾讯数据源
- 实时信号分析
- Web API接口
- 实时监控功能

## 联系方式

如有问题或建议，请联系系统管理员。
