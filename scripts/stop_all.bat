@echo off
REM 停止所有服务的便捷脚本（Windows）

echo ==========================================
echo 岗位JD分析器 - 停止所有服务
echo ==========================================

REM 停止Python进程
echo 停止Agents...
taskkill /F /FI "WINDOWTITLE eq start_agents.py*" >nul 2>&1
taskkill /F /FI "COMMANDLINE eq *start_agents.py*" >nul 2>&1

echo 停止API服务...
taskkill /F /FI "COMMANDLINE eq *uvicorn*src.api.main:app*" >nul 2>&1

echo 停止UI服务...
taskkill /F /FI "COMMANDLINE eq *streamlit*src\ui\app.py*" >nul 2>&1

REM 额外清理
for /f "tokens=2" %%a in ('tasklist ^| findstr /i "python"') do (
    tasklist /FI "PID eq %%a" /V | findstr /i "start_agents uvicorn streamlit" >nul
    if not errorlevel 1 (
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo 所有服务已停止
echo ==========================================

pause
