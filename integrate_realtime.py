#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将实时数据模块集成到现有myStock系统
"""

import os
import sys
import shutil
from datetime import datetime

def integrate_with_instock():
    """集成到instock目录"""
    print("="*80)
    print("myStock实时数据系统集成")
    print("="*80)
    
    # 检查instock目录
    instock_dir = os.path.join(os.path.dirname(__file__), 'instock')
    if not os.path.exists(instock_dir):
        print(f"❌ instock目录不存在: {instock_dir}")
        return False
    
    print(f"✅ 找到instock目录: {instock_dir}")
    
    # 创建实时数据目录
    realtime_dir = os.path.join(instock_dir, 'realtime')
    if not os.path.exists(realtime_dir):
        os.makedirs(realtime_dir)
        print(f"✅ 创建实时数据目录: {realtime_dir}")
    
    # 复制实时模块文件
    source_files = ['realtime_module.py']
    
    for file in source_files:
        source_path = os.path.join(os.path.dirname(__file__), file)
        dest_path = os.path.join(realtime_dir, file)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"✅ 复制文件: {file} -> {dest_path}")
        else:
            print(f"❌ 源文件不存在: {source_path}")
    
    # 创建__init__.py文件
    init_file = os.path.join(realtime_dir, '__init__.py')
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write('''
"""
myStock实时数据模块
"""
from .realtime_module import RealtimeDataManager, RealtimeAnalyzer

__all__ = ['RealtimeDataManager', 'RealtimeAnalyzer']
''')
    print(f"✅ 创建__init__.py文件")
    
    # 修改instock的__init__.py
    instock_init = os.path.join(instock_dir, '__init__.py')
    if os.path.exists(instock_init):
        with open(instock_init, 'a', encoding='utf-8') as f:
            f.write('\n# 实时数据模块\nfrom . import realtime\n')
        print(f"✅ 更新instock __init__.py")
    
    return True

def create_realtime_job():
    """创建实时数据抓取任务"""
    print("\n📋 创建实时数据抓取任务...")
    
    job_dir = os.path.join(os.path.dirname(__file__), 'instock', 'job')
    if not os.path.exists(job_dir):
        print(f"❌ job目录不存在: {job_dir}")
        return False
    
    # 创建实时数据抓取任务
    realtime_job = os.path.join(job_dir, 'realtime_data_daily_job.py')
    
    job_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据抓取任务
每5分钟抓取一次关注的股票实时数据
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

from instock.realtime import RealtimeDataManager

def main():
    """主函数"""
    print("="*80)
    print("实时数据抓取任务")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 初始化数据管理器
    data_manager = RealtimeDataManager()
    
    # 确保实时数据表存在
    data_manager.create_realtime_table()
    
    # 获取关注的股票（前50只）
    stocks = data_manager.get_stock_list(limit=50)
    if not stocks:
        print("❌ 未找到股票数据")
        return
    
    stock_codes = [stock[0] for stock in stocks]
    print(f"✅ 获取到{len(stock_codes)}只关注股票")
    
    # 抓取实时数据
    success_count = 0
    fail_count = 0
    
    for code in stock_codes:
        try:
            data = data_manager.get_realtime_data(code, use_cache=False)
            if data:
                # 保存到数据库
                if data_manager.save_realtime_data(data):
                    success_count += 1
                    print(f"  ✅ {code}: {data.get('current', 0):.2f}元")
                else:
                    fail_count += 1
                    print(f"  ❌ {code}: 保存失败")
            else:
                fail_count += 1
                print(f"  ❌ {code}: 获取数据失败")
            
            # 避免请求过快
            time.sleep(0.2)
            
        except Exception as e:
            fail_count += 1
            print(f"  ❌ {code}: 异常 - {e}")
    
    print(f"\\n📊 抓取结果:")
    print(f"  成功: {success_count}只")
    print(f"  失败: {fail_count}只")
    print(f"  成功率: {success_count/(success_count+fail_count)*100:.1f}%")
    
    print(f"\\n✅ 任务完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
'''
    
    with open(realtime_job, 'w', encoding='utf-8') as f:
        f.write(job_content)
    
    print(f"✅ 创建实时数据抓取任务: {realtime_job}")
    
    return True

def update_execute_daily_job():
    """更新execute_daily_job.py以包含实时任务"""
    print("\n📋 更新每日任务执行脚本...")
    
    execute_job = os.path.join(os.path.dirname(__file__), 'instock', 'job', 'execute_daily_job.py')
    
    if not os.path.exists(execute_job):
        print(f"❌ execute_daily_job.py不存在: {execute_job}")
        return False
    
    # 读取现有内容
    with open(execute_job, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已包含实时任务
    if 'realtime_data_daily_job' in content:
        print("✅ 实时任务已包含在execute_daily_job.py中")
        return True
    
    # 找到导入部分
    import_lines = []
    new_content = []
    in_import_section = False
    
    for line in content.split('\n'):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            in_import_section = True
            import_lines.append(line)
        elif in_import_section and not line.strip().startswith('import ') and not line.strip().startswith('from '):
            # 导入部分结束，添加实时任务导入
            import_lines.append('import realtime_data_daily_job as rdj')
            new_content.extend(import_lines)
            new_content.append(line)
            in_import_section = False
        else:
            new_content.append(line)
    
    # 找到主函数中的任务执行部分
    final_content = []
    for i, line in enumerate(new_content):
        final_content.append(line)
        # 在适当位置添加实时任务
        if 'executor.submit(kdj.main)' in line:
            # 在K线形态任务后添加实时任务
            final_content.append('        # 第X步创建股票实时数据表')
            final_content.append('        executor.submit(rdj.main)')
    
    # 写回文件
    with open(execute_job, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_content))
    
    print("✅ 更新execute_daily_job.py成功")
    return True

def create_realtime_web_api():
    """创建实时数据Web API"""
    print("\n📋 创建实时数据Web API...")
    
    web_dir = os.path.join(os.path.dirname(__file__), 'instock', 'web')
    if not os.path.exists(web_dir):
        print(f"❌ web目录不存在: {web_dir}")
        return False
    
    # 创建实时数据API文件
    realtime_api = os.path.join(web_dir, 'realtime_api.py')
    
    api_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据Web API
为myStock系统提供实时数据接口
"""

import tornado.web
import tornado.ioloop
import json
from datetime import datetime

# 添加项目路径
import sys
import os
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

from instock.realtime import RealtimeDataManager, RealtimeAnalyzer

class RealtimeDataHandler(tornado.web.RequestHandler):
    """实时数据处理器"""
    
    def initialize(self):
        self.data_manager = RealtimeDataManager()
        self.analyzer = RealtimeAnalyzer(self.data_manager)
    
    def get(self):
        """获取实时数据"""
        stock_code = self.get_argument('code', '')
        action = self.get_argument('action', 'data')
        
        if not stock_code:
            self.write({'error': '股票代码不能为空'})
            return
        
        try:
            if action == 'data':
                # 获取实时数据
                data = self.data_manager.get_realtime_data(stock_code)
                if data:
                    self.write({
                        'success': True,
                        'data': data,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    self.write({'success': False, 'error': '获取数据失败'})
            
            elif action == 'signal':
                # 获取实时信号
                signal = self.data_manager.analyze_realtime_signal(stock_code)
                if signal:
                    self.write({
                        'success': True,
                        'signal': signal,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    self.write({'success': False, 'error': '分析信号失败'})
            
            elif action == 'history':
                # 获取历史实时数据
                limit = int(self.get_argument('limit', '10'))
                history = self.data_manager.get_latest_realtime(stock_code, limit)
                self.write({
                    'success': True,
                    'history': history,
                    'count': len(history)
                })
            
            else:
                self.write({'error': '不支持的操作类型'})
                
        except Exception as e:
            self.write({'error': str(e)})

class RealtimeReportHandler(tornado.web.RequestHandler):
    """实时报告处理器"""
    
    def initialize(self):
        self.data_manager = RealtimeDataManager()
        self.analyzer = RealtimeAnalyzer(self.data_manager)
    
    def get(self):
        """生成实时报告"""
        limit = int(self.get_argument('limit', '20'))
        
        try:
            # 获取股票列表
            stocks = self.data_manager.get_stock_list(limit=limit)
            stock_codes = [stock[0] for stock in stocks]
            
            # 这里可以调用analyzer生成报告
            # 简化版本：只返回股票列表和基本信息
            result = {
                'success': True,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'stocks': [],
                'total': len(stock_codes)
            }
            
            for code in stock_codes[:10]:  # 只处理前10只
                data = self.data_manager.get_realtime_data(code)
                if data:
                    result['stocks'].append({
                        'code': code,
                        'price': data.get('current', 0),
                        'change': data.get('change_percent', 0),
                        'volume': data.get('volume', 0)
                    })
            
            self.write(result)
            
        except Exception as e:
            self.write({'error': str(e)})

def make_app():
    """创建Tornado应用"""
    return tornado.web.Application([
        (r"/api/realtime/data", RealtimeDataHandler),
        (r"/api/realtime/report", RealtimeReportHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9999)
    print("实时数据API服务启动，端口: 9999")
    print("接口地址:")
    print("  GET /api/realtime/data?code=000034&action=data")
    print("  GET /api/realtime/data?code=000034&action=signal")
    print("  GET /api/realtime/data?code=000034&action=history&limit=10")
    print("  GET /api/realtime/report?limit=20")
    tornado.ioloop.IOLoop.current().start()
'''
    
    with open(realtime_api, 'w', encoding='utf-8') as f:
        f.write(api_content)
    
    print(f"✅ 创建实时数据Web API: {realtime_api}")
    
    # 更新web_service.py以包含实时API
    web_service = os.path.join(web_dir, 'web_service.py')
    if os.path.exists(web_service):
        with open(web_service, 'r', encoding='utf-8') as f:
            web_content = f.read()
        
        # 检查是否已包含实时API
        if 'realtime_api' not in web_content:
            # 在适当位置添加导入
            lines = web_content.split('\n')
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if 'import' in line and 'tornado' in line and 'web' in line:
                    # 在tornado导入后添加
                    new_lines.append('from . import realtime_api')
            
            with open(web_service, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print("✅ 更新web_service.py成功")
    
    return True

def create_usage_examples():
    """创建使用示例"""
    print("\n📋 创建使用示例...")
    
    examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
    if not os.path.exists(examples_dir):
        os.makedirs(examples_dir)
    
    # 示例1: 基本使用
    example1 = os.path.join(examples_dir, 'realtime_basic.py')
    
    example1_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock实时数据模块 - 基本使用示例
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from instock.realtime import RealtimeDataManager, RealtimeAnalyzer

def main():
    print("="*80)
    print("myStock实时数据模块 - 基本使用示例")
    print("="*80)
    
    # 1. 初始化数据管理器
    data_manager = RealtimeDataManager()
    
    # 2. 创建实时数据表（如果不存在）
    data_manager.create_realtime_table()
    
    # 3. 获取单只股票实时数据
    print("\\n📊 获取单只股票实时数据:")
    stock_code = "000034"  # 神州数码
    realtime_data = data_manager.get_realtime_data(stock_code)
    
    if realtime_data:
        print(f"股票代码: {realtime_data['code']}")
        print(f"股票名称: {realtime_data['name']}")
        print(f"当前价格: {realtime_data['current']:.2f}元")
        print(f"涨跌幅: {realtime_data.get('change_percent', 0):.2f}%")
        print(f"成交量: {realtime_data['volume']:,}")
        print(f"数据来源: {realtime_data['source']}")
        print(f"更新时间: {realtime_data['time']}")
    else:
        print(f"❌ 获取{stock_code}实时数据失败")
    
    # 4. 分析实时信号
    print("\\n📈 分析实时信号:")
    analyzer = RealtimeAnalyzer(data_manager)
    signal = data_manager.analyze_realtime_signal(stock_code)
    
    if signal:
        print(f"股票: {signal['code']}/{signal['name']}")
        print(f"当前价: {signal['current_price']:.2f}元")
        print(f"涨跌幅: {signal['change_percent']:.2f}%")
        print(f"信号: {', '.join(signal['signals'])}")
        print(f"建议: {signal['recommendation']}")
        print(f"信心度: {signal['confidence']}")
    
    # 5. 批量获取实时数据
    print("\\n📊 批量获取实时数据:")
    stock_codes = ["000034", "603949", "000001"]  # 神州数码、雪龙集团、平安银行
    batch_data = data_manager.batch_get_realtime(stock_codes)
    
    print(f"成功获取{len(batch_data)}只股票数据:")
    for code, data in batch_data.items():
        print(f"  {code}: {data['current']:.2f}元 ({data.get('change_percent', 0):.2f}%)")
    
    # 6. 生成实时报告
    print("\\n📋 生成实时报告:")
    analyzer.generate_realtime_report(stock_codes)

if __name__ == "__main__":
    main()
'''
    
    with open(example1, 'w', encoding='utf-8') as f:
        f.write(example1_content)
    
    print(f"✅ 创建基本使用示例: {example1}")
    
    # 示例2: 实时监控
    example2 = os.path.join(examples_dir, 'realtime_monitor.py')
    
    example2_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
myStock实时数据模块 - 实时监控示例
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from instock.realtime import RealtimeDataManager

def simple_monitor(stock_codes, interval=30):
    """简单实时监控"""
    data_manager = RealtimeDataManager()
    
    print(f"🚀 启动实时监控，监控{len(stock_codes)}只股票")
    print(f"监控间隔: {interval}秒")
    print("按Ctrl+C停止监控\\n")
    
    try:
        while True:
            print(f"\\n📊 监控更新 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-"*60)
            
            for code in stock_codes:
                try:
                    data = data_manager.get_realtime_data(code, use_cache=False)
                    if data:
                        current = data.get('current', 0)
                        change = data.get('change_percent', 0)
                        volume = data.get('volume', 0)
                        
                        # 简单信号判断
                        if change > 2:
                            signal = "🟢 强势"
                        elif change > 0:
                            signal = "🟡 上涨"
                        elif change > -2:
                            signal = "⚪ 平稳"
                        else:
                            signal = "🔴 下跌"
                        
                        print(f"{signal} {code}: {current:.2f}元 ({change:+.2f}%) 成交量: {volume:,}")
                        
                        # 保存到数据库
                        data_manager.save_realtime_data(data)
                    
                    time.sleep(0.2)  # 避免请求过快
                    
                except Exception as e:
                    print(f"❌ {code}: 监控失败 - {e}")
            
            print("-"*60)
            print(f"下次更新: {interval}秒后")
            
            # 等待间隔时间
            for i in range(interval):
                time.sleep(1)
                if i % 10 == 0:
                    print(f"  ...等待{interval-i}秒", end='\\r')
            
    except KeyboardInterrupt:
        print("\\n\\n🛑 监控已停止")

def main():
    print("="*80)
    print("myStock实时数据模块 - 实时监控示例")
    print("="*80)
    
    # 初始化数据管理器
    data_manager = RealtimeDataManager()
    
    # 获取关注的股票
    stocks = data_manager.get_stock_list(limit=10)
    if not stocks:
        print("❌ 未找到股票数据")
        return
    
    stock_codes = [stock[0] for stock in stocks]
    print(f"监控股票: {', '.join(stock_codes)}")
    
    # 启动简单监控
    simple_monitor(stock_codes, interval=60)

if __name__ == "__main__":
    main()
'''
    
    with open(example2, 'w', encoding='utf-8') as f:
        f.write(example2_content)
    
    print(f"✅ 创建实时监控示例: {example2}")
    
    return True

def create_documentation():
    """创建文档"""
    print("\n📋 创建文档...")
    
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    # 实时模块文档
    doc_file = os.path.join(docs_dir, 'REALTIME_MODULE.md')
    
    doc_content = '''# myStock 实时数据模块文档

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
'''
    
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"✅ 创建文档: {doc_file}")
    
    return True

def main():
    """主函数"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("="*80)
    print("myStock实时数据系统集成工具")
    print("="*80)
    
    steps = [
        ("集成到instock目录", integrate_with_instock),
        ("创建实时数据抓取任务", create_realtime_job),
        ("更新每日任务执行脚本", update_execute_daily_job),
        ("创建实时数据Web API", create_realtime_web_api),
        ("创建使用示例", create_usage_examples),
        ("创建文档", create_documentation),
    ]
    
    success_count = 0
    fail_count = 0
    
    for step_name, step_func in steps:
        print(f"\n[执行] {step_name}")
        try:
            if step_func():
                print(f"✅ {step_name} - 成功")
                success_count += 1
            else:
                print(f"❌ {step_name} - 失败")
                fail_count += 1
        except Exception as e:
            print(f"❌ {step_name} - 异常: {e}")
            fail_count += 1
    
    print(f"\n" + "="*80)
    print("集成完成!")
    print(f"成功: {success_count}项")
    print(f"失败: {fail_count}项")
    
    if fail_count == 0:
        print("\n🎉 所有集成步骤成功完成!")
        print("\n🚀 下一步:")
        print("1. 测试实时模块: python realtime_module.py")
        print("2. 运行实时监控: python realtime_module.py --monitor")
        print("3. 启动Web API: python instock/web/realtime_api.py")
        print("4. 查看文档: docs/REALTIME_MODULE.md")
    else:
        print(f"\n⚠️ 有{fail_count}项集成失败，请检查错误信息")
    
    print(f"\n📅 集成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()