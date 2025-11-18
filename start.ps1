# 简化的启动脚本
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "岗位JD分析器 - 启动服务" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "检查 Python 环境..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Python" -ForegroundColor Red
    exit 1
}

# 创建目录
Write-Host "创建必要的目录..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path data, logs, uploads | Out-Null

# 检查 .env
if (-not (Test-Path .env)) {
    Write-Host "创建 .env 文件..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "请在新的终端窗口中运行以下命令：" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Write-Host "1. 启动 API 服务：" -ForegroundColor Cyan
Write-Host "   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""

Write-Host "2. 启动 UI 服务：" -ForegroundColor Cyan
Write-Host "   python -m streamlit run src/ui/app.py --server.port 8501" -ForegroundColor White
Write-Host ""

Write-Host "============================================================" -ForegroundColor Green
Write-Host "访问地址：" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  - Streamlit UI: http://localhost:8501" -ForegroundColor Yellow
Write-Host "  - API 文档: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  - API 健康检查: http://localhost:8000/health" -ForegroundColor Yellow
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
Read-Host
