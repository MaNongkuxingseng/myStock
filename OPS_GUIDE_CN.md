# myStock 一键启动说明（Windows 本机版）

## 1. 已准备好的脚本
位置：`myStock/instock/bin/`

- `run_job_local.bat`：执行每日数据作业（支持传日期参数）
- `run_web_local.bat`：启动 Web 服务（默认 9988）
- `run_all_local.bat`：一键同时拉起作业窗口 + Web 窗口

这些脚本已内置：
- Python 解释器：`..\.venv-mystock\Scripts\python.exe`
- MySQL 连接环境变量：
  - `db_host=127.0.0.1`
  - `db_user=root`
  - `db_password=785091`
  - `db_database=instockdb`

## 2. 推荐启动方式

### 方式 A：一键启动（最省事）
双击：

`myStock\instock\bin\run_all_local.bat`

### 方式 B：分别启动
1) 先跑作业：

`myStock\instock\bin\run_job_local.bat`

2) 再开网页：

`myStock\instock\bin\run_web_local.bat`

## 3. 常用命令（作业）
脚本支持透传参数：

- 当前交易日：
  - `run_job_local.bat`
- 指定单日：
  - `run_job_local.bat 2026-02-26`
- 指定多日：
  - `run_job_local.bat 2026-02-25,2026-02-26`
- 指定区间：
  - `run_job_local.bat 2026-02-01 2026-02-26`

## 4. 访问方式
Web 启动成功后访问：

- `http://127.0.0.1:9988`

## 5. 故障排查
1) 提示找不到 venv python：
- 检查 `.venv-mystock` 是否在 `workspace` 根目录

2) MySQL 连接失败：
- 确认 MySQL 服务已启动
- 核对 root 密码是否仍为 `785091`

3) 页面打不开：
- 确认 `run_web_local.bat` 窗口未退出
- 查看日志：`myStock/instock/log/stock_web.log`

4) 作业异常：
- 查看日志：`myStock/instock/log/stock_execute_job.log`

## 6. 建议（后续优化）
- 将数据库密码改为专用业务账户（非 root）
- 环境变量迁移到 `.env` 或系统级配置，避免明文密码
- Python 建议切换到 3.11（项目兼容性更稳）
