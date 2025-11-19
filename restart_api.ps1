# API 服务器重启脚本

Write-Host "="*70 -ForegroundColor Cyan
Write-Host "API 服务器重启脚本" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

# 1. 查找占用 8000 端口的进程
Write-Host "`n[1/4] 查找 API 进程..." -ForegroundColor Yellow

$connection = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($connection) {
    $processId = $connection.OwningProcess
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    
    if ($process) {
        Write-Host "  找到进程: $($process.ProcessName) (PID: $processId)" -ForegroundColor Green
        
        # 2. 停止进程
        Write-Host "`n[2/4] 停止 API 服务..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $processId -Force
            Write-Host "  ✅ API 服务已停止" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ 停止失败: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ⚠️ 进程已不存在" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ℹ️ 未找到运行在 8000 端口的进程" -ForegroundColor Cyan
}

# 3. 等待端口释放
Write-Host "`n[3/4] 等待端口释放..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# 清除 Python 缓存（可选）
Write-Host "  清除 Python 缓存..." -ForegroundColor Gray
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# 4. 重新启动 API
Write-Host "`n[4/4] 启动 API 服务..." -ForegroundColor Yellow
Write-Host "  命令: python -m src.api.main" -ForegroundColor Gray
Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "API 服务正在启动..." -ForegroundColor Green
Write-Host "按 Ctrl+C 可以停止服务" -ForegroundColor Yellow
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""

# 启动 API（前台运行）
python -m src.api.main
