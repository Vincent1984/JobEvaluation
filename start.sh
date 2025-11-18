#!/bin/bash

echo "========================================"
echo "岗位JD分析器 - 快速启动"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python，请先安装Python 3.11+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 正在创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 正在检查依赖..."
pip install -q -r requirements.txt

# 运行启动脚本
python run.py
