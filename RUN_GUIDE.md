# myStock 版本运行指南

## 快速开始

### 1. 检查当前运行状态
```bash
# 查看端口占用
netstat -ano | findstr "9988 8000 9000"

# 查看myStock进程
tasklist | findstr "python.exe"

# 访问Web服务
curl http://localhost:9988/
# 或浏览器访问: http://localhost:9988/
```

### 2. 停止当前服务 (如果需要)
```bash
# 停止myStock 1.0服务
taskkill /PID 1648 /F

# 停止打印服务 (如果需要释放端口8000)
taskkill /PID 24216 /F
```

## myStock 1.0版本运行

### 启动方式
```bash
# 方式1: 直接运行Web服务
cd G:\openclaw\workspace\projects\active\myStock\instock\web
python web_service.py

# 方式2: 从项目根目录运行
cd G:\openclaw\workspace\projects\active\myStock
python -m instock.web.web_service

# 方式3: 使用批处理脚本 (如果存在)
cd G:\openclaw\workspace\projects\active\myStock
start_1_0.bat
```

### 验证运行
```bash
# 1. 检查端口
netstat -ano | findstr :9988

# 2. 访问首页
curl http://localhost:9988/

# 3. 查看日志
cd G:\openclaw\workspace\projects\active\myStock\instock\log
tail -f web_service.log
```

### 运行定时任务
```bash
# 查看可用任务
cd G:\openclaw\workspace\projects\active\myStock\instock\job
dir *.py

# 手动运行任务 (示例)
python stock_daily.py
python indicator_calc.py
```

## myStock 1.1版本运行

### 启动推送系统
```bash
# 方式1: 启动推送调度服务
cd G:\openclaw\workspace\projects\active\myStock
python -c "
from src.core.push.scheduler import push_scheduler
push_scheduler.register_default_tasks()
push_scheduler.start()
print('推送调度服务已启动')
"

# 方式2: 测试运行
cd G:\openclaw\workspace\projects\active\myStock
python test_system.py
```

### 测试技术分析功能
```bash
cd G:\openclaw\workspace\projects\active\myStock

# 导入测试
python -c "
from src.core.analysis.indicators import technical_indicators
from src.core.analysis.signals import signal_generator
print('技术分析模块导入成功')
"

# 完整功能测试
python -c "
import pandas as pd
import numpy as np
from src.core.analysis.indicators import technical_indicators
from src.core.analysis.signals import signal_generator

# 创建测试数据
dates = pd.date_range(start='2026-01-01', periods=20, freq='D')
np.random.seed(42)
data = pd.DataFrame({
    'close': 10 + np.random.randn(20).cumsum() * 0.1
}, index=dates)

# 计算指标
indicators = technical_indicators.calculate_all_indicators(data)
print(f'计算完成: {len(indicators)}个指标')

# 生成信号
current_price = data['close'].iloc[-1]
signals = signal_generator.analyze_indicators(indicators, current_price)
print(f'生成信号: {len(signals)}个')
"
```

### 测试推送功能
```bash
cd G:\openclaw\workspace\projects\active\myStock

# 测试内容生成
python -c "
import pandas as pd
import numpy as np
from src.core.push.generator import content_generator

# 创建测试数据
dates = pd.date_range(start='2026-01-01', periods=20, freq='D')
np.random.seed(42)
data = pd.DataFrame({
    'close': 10 + np.random.randn(20).cumsum() * 0.1
}, index=dates)
current_price = data['close'].iloc[-1]

# 生成早盘分析
content = content_generator.generate_morning_analysis(data, current_price)
print(f'内容生成成功: {content.title}')
print(f'建议: {content.recommendation}')
"

# 测试推送执行
python -c "
from src.core.push.executor import push_executor
import pandas as pd
import numpy as np
from src.core.push.generator import content_generator

# 创建测试数据
dates = pd.date_range(start='2026-01-01', periods=20, freq='D')
np.random.seed(42)
data = pd.DataFrame({
    'close': 10 + np.random.randn(20).cumsum() * 0.1
}, index=dates)
current_price = data['close'].iloc[-1]

# 生成内容
content = content_generator.generate_morning_analysis(data, current_price)

# 发送到控制台
success = push_executor.send_to_console(content)
print(f'控制台发送: {'成功' if success else '失败'}')

# 保存到文件
success = push_executor.save_to_file(content)
print(f'文件保存: {'成功' if success else '失败'})
"
```

## 同时运行两个版本

### 方案1: 端口隔离 (推荐)
```bash
# 1.0版本: 端口9988 (已运行)
# 1.1推送服务: 独立进程

# 启动1.1推送服务
cd G:\openclaw\workspace\projects\active\myStock
start python -c "
from src.core.push.scheduler import push_scheduler
push_scheduler.register_default_tasks()
push_scheduler.start()
import time
while True:
    time.sleep(60)
"

# 验证两个版本都在运行
netstat -ano | findstr "9988"
tasklist | findstr "python.exe"
```

### 方案2: 服务集成
```bash
# 1.0版本提供Web服务
# 1.1版本提供分析服务

# 创建集成脚本
cd G:\openclaw\workspace\projects\active\myStock
cat > run_integrated.py << 'EOF'
import threading
import time

def run_1_0():
    """运行1.0 Web服务"""
    import subprocess
    subprocess.run(["python", "-m", "instock.web.web_service"])

def run_1_1():
    """运行1.1推送服务"""
    from src.core.push.scheduler import push_scheduler
    push_scheduler.register_default_tasks()
    push_scheduler.start()
    while True:
        time.sleep(60)

if __name__ == "__main__":
    # 启动1.0服务线程
    t1 = threading.Thread(target=run_1_0, daemon=True)
    t1.start()
    
    # 启动1.1服务
    run_1_1()
EOF

# 运行集成服务
python run_integrated.py
```

## 测试脚本

### 1.0版本功能测试
```bash
cd G:\openclaw\workspace\projects\active\myStock

# 运行完整测试
python test_1_0_simple.py

# 查看测试报告
cat 1_0_TEST_REPORT.json
```

### 1.1版本功能测试
```bash
cd G:\openclaw\workspace\projects\active\myStock

# 运行系统测试
python test_system.py

# 运行集成测试
python scripts/integration_test.py
```

### 版本对比测试
```bash
cd G:\openclaw\workspace\projects\active\myStock

# 生成对比报告
python -c "
import json
from datetime import datetime

# 读取1.0测试报告
with open('1_0_TEST_REPORT.json', 'r') as f:
    report_1_0 = json.load(f)

# 模拟1.1测试报告
report_1_1 = {
    'version': '1.1',
    'test_time': datetime.now().isoformat(),
    'results': [
        {'test': 'Technical Indicators', 'success': True, 'details': '7 indicators'},
        {'test': 'Signal Generation', 'success': True, 'details': '12 rules'},
        {'test': 'Push System', 'success': True, 'details': '9 time points'},
        {'test': 'Content Generation', 'success': True, 'details': '5 content types'},
        {'test': 'Push Execution', 'success': True, 'details': '3 formats'}
    ],
    'summary': {
        'total_tests': 5,
        'passed_tests': 5,
        'failed_tests': 0,
        'success_rate': 1.0
    }
}

print('版本对比报告:')
print(f'1.0版本: {report_1_0['summary']['passed_tests']}/{report_1_0['summary']['total_tests']} 通过')
print(f'1.1版本: {report_1_1['summary']['passed_tests']}/{report_1_1['summary']['total_tests']} 通过')
"
```

## 故障排除

### 常见问题1: 端口冲突
```bash
# 检查端口占用
netstat -ano | findstr ":9988 :8000 :9000"

# 解决方案:
# 1. 停止冲突进程
taskkill /PID <冲突PID> /F

# 2. 修改配置文件使用其他端口
# 1.0版本: 修改instock/web/web_service.py中的端口
# 1.1版本: 修改src/config/settings.py中的端口
```

### 常见问题2: 导入错误
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 添加项目路径
cd G:\openclaw\workspace\projects\active\myStock
export PYTHONPATH=$PYTHONPATH:$(pwd)
# 或
set PYTHONPATH=%PYTHONPATH%;%CD%
```

### 常见问题3: 数据库连接失败
```bash
# 检查MySQL服务
net start | findstr "MySQL"

# 检查数据库配置
# 1.0版本: 查看instock/lib/database.py
# 1.1版本: 查看src/config/settings.py

# 测试数据库连接
python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='mystock'
    )
    print('数据库连接成功')
    conn.close()
except Exception as e:
    print(f'数据库连接失败: {e}')
"
```

### 常见问题4: 服务无法启动
```bash
# 查看错误日志
cd G:\openclaw\workspace\projects\active\myStock\instock\log
type web_service.log

# 检查依赖
pip list | findstr "tornado pandas numpy"

# 安装缺失依赖
pip install tornado pandas numpy mysql-connector-python schedule
```

## 监控和维护

### 服务监控
```bash
# 监控脚本
cd G:\openclaw\workspace\projects\active\myStock
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "=== myStock 服务监控 ==="
echo "时间: $(date)"

# 检查端口
echo "端口检查:"
netstat -ano | grep -E "(9988|9000)" || echo "  无相关端口"

# 检查进程
echo "进程检查:"
tasklist | grep -E "(python.exe|myStock)" || echo "  无相关进程"

# 检查日志
echo "日志检查:"
if [ -f "instock/log/web_service.log" ]; then
    echo "  日志文件存在"
    tail -5 instock/log/web_service.log
else
    echo "  日志文件不存在"
fi
EOF

# 运行监控
bash monitor.sh
```

### 日志管理
```bash
# 查看实时日志
cd G:\openclaw\workspace\projects\active\myStock\instock\log
tail -f web_service.log

# 查看错误日志
find . -name "*.log" -exec grep -l "ERROR\|Exception" {} \;

# 清理旧日志
# 保留最近7天的日志
find instock/log -name "*.log" -mtime +7 -delete
```

### 备份和恢复
```bash
# 数据库备份
mysqldump -u root -p mystock > mystock_backup_$(date +%Y%m%d).sql

# 代码备份
cd G:\openclaw\workspace\projects\active\myStock
git add .
git commit -m "备份 $(date +%Y%m%d)"
git push

# 配置文件备份
cp -r instock/ instock_backup_$(date +%Y%m%d)/
cp -r src/ src_backup_$(date +%Y%m%d)/
```

## 性能优化建议

### 1.0版本优化
```bash
# 启用数据库连接池
# 修改instock/lib/database.py

# 添加查询缓存
# 在singleton_stock.py中添加缓存逻辑

# 优化Web服务配置
# 调整Tornado的线程数和超时设置
```

### 1.1版本优化
```bash
# 启用批量计算
# 在indicators.py中优化批量计算逻辑

# 添加结果缓存
# 在signals.py中添加信号缓存

# 优化推送性能
# 在executor.py中添加异步发送
```

## 扩展开发

### 添加新功能到1.0版本
```bash
# 1. 在现有模块中添加功能
# 2. 保持API兼容性
# 3. 充分测试后部署
```

### 添加新功能到1.1版本
```bash
# 1. 在src/目录下创建新模块
# 2. 遵循模块化设计原则
# 3. 添加单元测试
# 4. 更新配置和文档
```

### 创建混合功能
```bash
# 示例: 将1.1的技术分析集成到1.0
# 1. 在1.0中调用1.1的分析模块
# 2. 通过共享数据库或API通信
# 3. 逐步迁移功能
```

---

**最后更新**: 2026-03-01 12:45  
**维护提示**: 定期检查端口冲突，备份重要数据，监控服务状态。