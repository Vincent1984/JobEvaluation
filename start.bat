@echo off
chcp 65001 >nul
echo ========================================
echo 岗位JD分析器 - 快速启动
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\" (
    echo 📦 正在创建虚拟环境...
    python -m venv venv
    echo ✅ 虚拟环境已创建
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 正在检查依赖...
pip install -q -r requirements.txt

REM 运行启动脚本
python run.py

pause
