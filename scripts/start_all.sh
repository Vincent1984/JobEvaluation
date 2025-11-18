#!/bin/bash
# 启动所有服务的便捷脚本（Linux/Mac）

set -e

echo "=========================================="
echo "岗位JD分析器 - 启动所有服务"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查Redis
if ! command -v redis-server &> /dev/null; then
    echo "警告: 未找到Redis，请确保Redis已安装并运行"
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p data logs uploads

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "警告: 未找到.env文件，使用默认配置"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "已从.env.example创建.env文件，请检查配置"
    fi
fi

# 初始化数据库
echo "初始化数据库..."
python3 scripts/init_db.py

# 启动Redis（如果未运行）
if ! pgrep -x "redis-server" > /dev/null; then
    echo "启动Redis..."
    redis-server --daemonize yes
    sleep 2
fi

# 启动Agents（后台运行）
echo "启动Agents..."
python3 scripts/start_agents.py > logs/agents.log 2>&1 &
AGENTS_PID=$!
echo "Agents PID: $AGENTS_PID"

# 等待Agents启动
sleep 3

# 启动API服务（后台运行）
echo "启动API服务..."
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
echo "API PID: $API_PID"

# 等待API启动
sleep 3

# 启动UI服务（后台运行）
echo "启动UI服务..."
python3 -m streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 > logs/ui.log 2>&1 &
UI_PID=$!
echo "UI PID: $UI_PID"

# 等待服务启动
sleep 5

# 健康检查
echo ""
echo "执行健康检查..."
python3 scripts/health_check.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "所有服务已成功启动！"
    echo "=========================================="
    echo ""
    echo "访问地址："
    echo "  - Streamlit UI: http://localhost:8501"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - API健康检查: http://localhost:8000/health"
    echo ""
    echo "进程ID："
    echo "  - Agents: $AGENTS_PID"
    echo "  - API: $API_PID"
    echo "  - UI: $UI_PID"
    echo ""
    echo "查看日志："
    echo "  - tail -f logs/agents.log"
    echo "  - tail -f logs/api.log"
    echo "  - tail -f logs/ui.log"
    echo ""
    echo "停止服务："
    echo "  - ./scripts/stop_all.sh"
    echo "=========================================="
    
    # 保存PID到文件
    echo $AGENTS_PID > .agents.pid
    echo $API_PID > .api.pid
    echo $UI_PID > .ui.pid
else
    echo ""
    echo "警告: 部分服务可能未正常启动，请检查日志"
fi
