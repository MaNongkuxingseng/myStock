# myStock 版本管理指南

## 当前版本状态

### 1. myStock 1.0版本 (稳定版)
- **状态**: 生产环境运行中
- **端口**: 9988
- **进程ID**: 1648 (python.exe)
- **框架**: Tornado Web框架
- **访问地址**: http://localhost:9988/
- **代码位置**: `instock/` 目录

### 2. myStock 1.1版本 (开发版)
- **状态**: 开发完成，待测试
- **分支**: `feature/v1.1-enhancement`
- **代码位置**: `src/` 目录
- **功能**: 增强的推送系统和数据分析

## 端口分配策略

为了避免端口冲突，采用以下端口分配：

| 版本 | 服务类型 | 默认端口 | 备用端口 | 状态 |
|------|----------|----------|----------|------|
| 1.0 | Web服务 | 9988 | 9989 | ✅ 使用中 |
| 1.1 | Web服务 | 9000 | 9001 | ⏳ 可用 |
| 1.1 | API服务 | 8001 | 8002 | ⏳ 可用 |
| 1.0 | 数据库 | 3306 | - | ✅ MySQL默认 |

**注意**: 端口8000已被CLodopPrint32.exe占用，避免使用。

## 版本启动方式

### 1. myStock 1.0版本启动

#### 方式一：直接启动Web服务
```bash
cd G:\openclaw\workspace\projects\active\myStock\instock\web
python web_service.py
```

#### 方式二：通过脚本启动（如果存在）
```bash
cd G:\openclaw\workspace\projects\active\myStock
python -m instock.web.web_service
```

#### 方式三：停止后重新启动
```bash
# 停止当前服务
taskkill /PID 1648 /F

# 重新启动
cd G:\openclaw\workspace\projects\active\myStock\instock\web
python web_service.py
```

### 2. myStock 1.1版本启动

#### 方式一：启动推送调度服务
```bash
cd G:\openclaw\workspace\projects\active\myStock
python -c "from src.core.push.scheduler import push_scheduler; push_scheduler.register_default_tasks(); push_scheduler.start()"
```

#### 方式二：启动Web服务（待开发）
```bash
# 1.1版本Web服务尚未开发，计划端口9000
cd G:\openclaw\workspace\projects\active\myStock
python src/api/server.py  # 待创建
```

#### 方式三：测试运行
```bash
cd G:\openclaw\workspace\projects\active\myStock
python scripts/test_system.py
```

## 服务检测脚本

### 端口检测脚本
```python
import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

# 检测关键端口
ports = {
    9988: "myStock 1.0 Web服务",
    8000: "CLodop打印服务",
    3306: "MySQL数据库",
    9000: "myStock 1.1 Web服务(计划)"
}

for port, service in ports.items():
    if check_port(port):
        print(f"✅ 端口 {port}: {service} 正在运行")
    else:
        print(f"❌ 端口 {port}: {service} 未运行")
```

### 进程检测脚本
```python
import psutil

def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    return proc
        except:
            continue
    return None

# 查找myStock相关进程
myStock_ports = [9988, 9000]
for port in myStock_ports:
    proc = find_process_by_port(port)
    if proc:
        print(f"端口 {port}: PID {proc.info['pid']} - {proc.info['name']}")
```

## 同时运行两个版本的策略

### 方案一：端口隔离（推荐）
```
1.0版本: 端口 9988 (现有)
1.1版本: 端口 9000 (新端口)

访问方式:
- 1.0: http://localhost:9988/
- 1.1: http://localhost:9000/
```

### 方案二：时间隔离
- 白天运行1.0版本服务用户
- 夜间测试1.1版本新功能

### 方案三：容器隔离
- 使用Docker容器分别运行两个版本
- 每个版本有独立的网络命名空间

## 迁移计划

### 阶段一：并行运行
1. 1.0版本继续服务现有用户
2. 1.1版本在测试环境运行
3. 数据双向同步

### 阶段二：功能迁移
1. 逐步将1.1版本功能集成到1.0
2. 用户无感知迁移

### 阶段三：完全切换
1. 所有用户迁移到1.1版本
2. 1.0版本作为备份

## 故障处理

### 端口冲突处理
1. **检测冲突**: 使用端口检测脚本
2. **解决冲突**:
   - 停止冲突服务
   - 修改配置文件使用备用端口
   - 重新启动服务

### 服务异常处理
1. **检查日志**: `instock/log/` 目录
2. **重启服务**: 按上述启动方式重启
3. **回滚版本**: 如有必要回退到稳定版本

## 监控建议

### 基础监控
- 服务端口监听状态
- 进程CPU/内存使用率
- 错误日志监控

### 业务监控
- 1.0版本Web访问量
- 数据分析任务完成情况
- 推送系统运行状态

---

**最后更新**: 2026-03-01 12:35
**维护者**: OpenClaw AI Assistant