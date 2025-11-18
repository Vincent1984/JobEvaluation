@echo off
REM 启动所有服务的便捷脚本（Windows）

echo ==========================================
echo 岗位JD分析器 - 启动所有服务
echo ==========================================

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    exit /b 1
)

REM 创建必要的目录
echo 创建必要的目录...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist uploads mkdir uploads

REM 检查环境变量文件
if not exist .env (
    echo 警告: 未找到.env文件
    if exist .env.example (
        copy .env.example .env
        echo 已从.env.example创建.env文件，请检查配置
    )
)

REM 初始化数据库
echo 初始化数据库...
python scripts\init_db.py

REM 启动Redis（需要手动启动或使用Docker）
echo 请确保Redis已启动...

REM 启动Agents（后台运行）
echo 启动Agents...
start /B python scripts\start_agents.py > logs\agents.log 2>&1

REM 等待Agents启动
timeout /t 3 /nobreak >nul

REM 启动API服务（后台运行）
echo 启动API服务...
start /B python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs\api.log 2>&1

REM 等待API启动
timeout /t 3 /nobreak >nul

REM 启动UI服务（后台运行）
echo 启动UI服务...
start /B python -m streamlit run src\ui\app.py --server.port 8501 --server.address 0.0.0.0 > logs\ui.log 2>&1

REM 等待服务启动
timeout /t 5 /nobreak >nul

REM 健康检查
echo.
echo 执行健康检查...
python scripts\health_check.py

echo.
echo ==========================================
echo 所有服务已启动！
echo ==========================================
echo.
echo 访问地址：
echo   - Streamlit UI: http://localhost:8501
echo   - API文档: http://localhost:8000/docs
echo   - API健康检查: http://localhost:8000/health
echo.
echo 查看日志：
echo   - type logs\agents.log
echo   - type logs\api.log
echo   - type logs\ui.log
echo.
echo 停止服务：
echo   - scripts\stop_all.bat
echo ==========================================

pause
