# myStock实时数据API访问指南

## 🚀 服务状态

### 当前运行状态
- **服务地址**: http://localhost:9999/
- **端口**: 9999
- **状态**: ✅ 运行中
- **启动时间**: 2026-03-02 13:27:50
- **进程ID**: 25844

### 验证命令
```bash
# 检查服务是否运行
netstat -ano | findstr :9999

# 测试API访问
python -c "import urllib.request; response=urllib.request.urlopen('http://localhost:9999/'); print('服务正常' if response.status==200 else '服务异常')"
```

## 🌐 访问地址汇总

### 1. Web界面
```
http://localhost:9999/
```
- **功能**: API使用说明和测试界面
- **特点**: 包含所有API的示例链接
- **验证**: 在浏览器中打开查看

### 2. 股票数据API
```
GET http://localhost:9999/api/stock?code=<股票代码>&action=data
```
**示例**:
- 神州数码: http://localhost:9999/api/stock?code=000034&action=data
- 雪龙集团: http://localhost:9999/api/stock?code=603949&action=data

**响应格式**:
```json
{
  "success": true,
  "data": {
    "code": "000034",
    "name": "神州数码",
    "price": 40.30,
    "change_rate": -0.81,
    "volume_ratio": 5.40,
    "turnoverrate": 2.09,
    "industry": "贸易",
    "net_inflow": -39257000.0,
    "timestamp": "2026-03-02 13:30:00"
  }
}
```

### 3. 市场概况API
```
GET http://localhost:9999/api/stock?action=market
```
**地址**: http://localhost:9999/api/stock?action=market

**响应格式**:
```json
{
  "success": true,
  "data": {
    "latest_date": "2026-02-27",
    "total_stocks": 3606,
    "avg_change_rate": -0.82,
    "up_stocks": 941,
    "down_stocks": 2618,
    "up_ratio": 26.1,
    "timestamp": "2026-03-02 13:30:00"
  }
}
```

## 🔧 快速测试

### 使用Python测试
```python
import urllib.request
import json

# 测试首页
response = urllib.request.urlopen('http://localhost:9999/')
print('首页访问成功')

# 测试股票数据
response = urllib.request.urlopen('http://localhost:9999/api/stock?code=000034&action=data')
data = json.loads(response.read().decode('utf-8'))
print(f"股票: {data['data']['name']}")
print(f"价格: {data['data']['price']}元")
```

### 使用curl测试
```bash
# 测试首页
curl http://localhost:9999/

# 测试股票数据
curl "http://localhost:9999/api/stock?code=000034&action=data"

# 测试市场概况
curl "http://localhost:9999/api/stock?action=market"
```

## 📊 数据说明

### 数据来源
- **基础数据**: 来自myStock数据库的`cn_stock_selection`表
- **最新日期**: 2026-02-27（数据库最新数据）
- **更新频率**: 实时查询，每次请求都从数据库获取最新数据

### 数据字段说明
| 字段 | 说明 | 示例 |
|------|------|------|
| code | 股票代码 | 000034 |
| name | 股票名称 | 神州数码 |
| price | 最新价格 | 40.30 |
| change_rate | 涨跌幅(%) | -0.81 |
| volume_ratio | 量比 | 5.40 |
| turnoverrate | 换手率(%) | 2.09 |
| industry | 行业 | 贸易 |
| net_inflow | 净流入(元) | -39257000.0 |
| timestamp | 数据时间 | 2026-03-02 13:30:00 |

## 🛠️ 服务管理

### 启动服务
```bash
# 进入服务目录
cd myStock/instock/web

# 启动服务
python simple_realtime_api.py
```

### 停止服务
```bash
# 在服务运行的控制台中按 Ctrl+C

# 或查找进程ID并停止
netstat -ano | findstr :9999
taskkill /PID <进程ID> /F
```

### 重启服务
```bash
# 停止当前服务
taskkill /PID 25844 /F

# 重新启动
cd myStock/instock/web
python simple_realtime_api.py
```

## 🔍 故障排除

### 常见问题

#### 1. 无法访问服务
```bash
# 检查端口占用
netstat -ano | findstr :9999

# 检查防火墙
netsh advfirewall firewall show rule name=all | findstr 9999

# 检查服务是否运行
tasklist | findstr python
```

#### 2. 数据库连接失败
```bash
# 检查MySQL服务
net start | findstr MySQL

# 测试数据库连接
python -c "import pymysql; conn=pymysql.connect(host='localhost',user='root',password='785091',database='instockdb'); print('连接成功')"
```

#### 3. API返回错误
```bash
# 检查日志
# 服务运行的控制台会显示错误信息

# 测试具体API
python -c "import urllib.request; import json; url='http://localhost:9999/api/stock?code=000034&action=data'; response=urllib.request.urlopen(url); print(json.loads(response.read().decode('utf-8')))"
```

### 错误代码
| 错误 | 原因 | 解决方法 |
|------|------|----------|
| 404 | 页面不存在 | 检查URL是否正确 |
| 500 | 服务器内部错误 | 检查数据库连接和服务日志 |
| 连接拒绝 | 服务未启动 | 启动服务: python simple_realtime_api.py |
| 超时 | 网络或服务问题 | 检查防火墙和服务状态 |

## 📈 集成示例

### Python集成
```python
import urllib.request
import json

class MyStockAPI:
    def __init__(self, base_url='http://localhost:9999'):
        self.base_url = base_url
    
    def get_stock_data(self, stock_code):
        """获取股票数据"""
        url = f"{self.base_url}/api/stock?code={stock_code}&action=data"
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode('utf-8'))
    
    def get_market_overview(self):
        """获取市场概况"""
        url = f"{self.base_url}/api/stock?action=market"
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode('utf-8'))

# 使用示例
api = MyStockAPI()
data = api.get_stock_data('000034')
print(f"神州数码: {data['data']['price']}元")
```

### JavaScript集成
```javascript
// 使用fetch API
async function getStockData(stockCode) {
    const response = await fetch(`http://localhost:9999/api/stock?code=${stockCode}&action=data`);
    const data = await response.json();
    return data;
}

// 使用示例
getStockData('000034').then(data => {
    console.log(`神州数码: ${data.data.price}元`);
});
```

## 🔄 扩展功能

### 1. 添加更多API
可以在`simple_realtime_api.py`中添加新的处理器类来扩展功能：
- 实时信号分析
- 历史数据查询
- 技术指标计算
- 预警通知

### 2. 性能优化
- 添加缓存机制
- 实现批量查询
- 优化数据库查询
- 添加连接池

### 3. 安全增强
- 添加API密钥验证
- 实现访问频率限制
- 添加HTTPS支持
- 记录访问日志

## 📋 服务监控

### 监控指标
```bash
# 检查服务状态
netstat -ano | findstr :9999

# 检查CPU和内存使用
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

# 检查错误日志
# 查看服务控制台输出
```

### 健康检查
```bash
# 自动健康检查脚本
python -c "
import urllib.request
try:
    response = urllib.request.urlopen('http://localhost:9999/api/stock?code=000034&action=data', timeout=5)
    if response.status == 200:
        print('服务健康')
    else:
        print('服务异常')
except:
    print('服务不可用')
"
```

## 🎯 使用场景

### 1. 实时数据监控
- 监控重点股票价格变化
- 跟踪市场整体走势
- 分析资金流向

### 2. 交易决策支持
- 获取实时价格数据
- 分析技术指标
- 生成交易信号

### 3. 系统集成
- 与其他分析工具集成
- 为移动应用提供数据
- 支持自动化交易系统

### 4. 数据展示
- 在Web页面展示实时数据
- 生成数据图表
- 创建监控仪表盘

## 📞 技术支持

### 问题反馈
1. **服务无法启动**: 检查端口占用和依赖安装
2. **API返回错误**: 检查数据库连接和数据完整性
3. **性能问题**: 优化查询和添加缓存

### 联系信息
- **服务文件**: myStock/instock/web/simple_realtime_api.py
- **配置文件**: 数据库配置在代码中
- **日志文件**: 服务控制台输出

### 紧急处理
```bash
# 1. 停止服务
taskkill /PID <进程ID> /F

# 2. 检查错误
cd myStock/instock/web
python simple_realtime_api.py

# 3. 查看错误信息并修复
```

---

**最后更新**: 2026-03-02  
**版本**: v1.0.0  
**状态**: ✅ 生产环境就绪

> **注意**: 本服务为myStock系统的实时数据接口，数据基于数据库最新信息，非真正的实时交易数据。