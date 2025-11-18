@echo off
echo ========================================
echo 启动 JD 分析器服务
echo ========================================
echo.

echo [1/2] 启动 API 服务 (端口 8000)...
start "JD Analyzer API" cmd /k "python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/2] 启动 UI 服务 (端口 8501)...
start "JD Analyzer UI" cmd /k "streamlit run src/ui/app.py --server.port 8501"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo API 服务: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo UI 服务:  http://localhost:8501
echo.
echo 按任意键退出...
pause >nul
