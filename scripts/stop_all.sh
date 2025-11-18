#!/bin/bash
# 停止所有服务的便捷脚本（Linux/Mac）

echo "=========================================="
echo "岗位JD分析器 - 停止所有服务"
echo "=========================================="

# 从PID文件读取并停止服务
if [ -f .agents.pid ]; then
    AGENTS_PID=$(cat .agents.pid)
    echo "停止Agents (PID: $AGENTS_PID)..."
    kill $AGENTS_PID 2>/dev/null || echo "Agents已停止或未运行"
    rm .agents.pid
fi

if [ -f .api.pid ]; then
    API_PID=$(cat .api.pid)
    echo "停止API服务 (PID: $API_PID)..."
    kill $API_PID 2>/dev/null || echo "API服务已停止或未运行"
    rm .api.pid
fi

if [ -f .ui.pid ]; then
    UI_PID=$(cat .ui.pid)
    echo "停止UI服务 (PID: $UI_PID)..."
    kill $UI_PID 2>/dev/null || echo "UI服务已停止或未运行"
    rm .ui.pid
fi

# 额外清理：查找并停止相关进程
echo "清理残留进程..."
pkill -f "start_agents.py" 2>/dev/null
pkill -f "uvicorn src.api.main:app" 2>/dev/null
pkill -f "streamlit run src/ui/app.py" 2>/dev/null

echo ""
echo "所有服务已停止"
echo "=========================================="
