@echo off
chcp 65001 >nul
echo === myStock系统检查工具 ===
echo.

REM 检查虚拟环境
if exist ".venv-mystock\Scripts\python.exe" (
    echo [OK] 虚拟环境存在
    set VENV_PYTHON=.venv-mystock\Scripts\python.exe
) else (
    echo [ERROR] 虚拟环境不存在
    echo 请运行: python -m venv .venv-mystock
    pause
    exit /b 1
)

REM 检查依赖
echo.
echo 检查Python依赖...
%VENV_PYTHON% -c "import pandas; print('[OK] pandas:', pandas.__version__)"
if errorlevel 1 (
    echo [ERROR] pandas未安装
    echo 正在安装依赖...
    %VENV_PYTHON% -m pip install -r requirements.txt
)

%VENV_PYTHON% -c "import numpy; print('[OK] numpy:', numpy.__version__)"
%VENV_PYTHON% -c "import pymysql; print('[OK] pymysql:', pymysql.__version__)"
%VENV_PYTHON% -c "import talib; print('[OK] talib: OK')"

REM 检查数据库
echo.
echo 检查数据库连接...
%VENV_PYTHON% -c "
import sys
sys.path.append('.')
from instock.lib import database
print('[INFO] 数据库配置:', database.db_host, ':', database.db_port, '/', database.db_database)
import pymysql
try:
    conn = pymysql.connect(
        host=database.db_host,
        user=database.db_user,
        password=database.db_password,
        database=database.db_database,
        port=database.db_port,
        charset=database.db_charset
    )
    print('[OK] 数据库连接成功')
    conn.close()
except Exception as e:
    print('[ERROR] 数据库连接失败:', e)
"

REM 检查配置文件
echo.
echo 检查配置文件...
if exist "instock\config\eastmoney_cookie.txt" (
    echo [INFO] 东方财富Cookie文件存在
) else (
    echo [WARNING] 东方财富Cookie文件不存在
)

if exist "instock\config\proxy.txt" (
    echo [INFO] 代理配置文件存在
) else (
    echo [WARNING] 代理配置文件不存在
)

echo.
echo === 检查完成 ===
pause