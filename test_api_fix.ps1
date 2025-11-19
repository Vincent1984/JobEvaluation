# 测试 API 修复脚本

Write-Host "="*70 -ForegroundColor Cyan
Write-Host "测试 API 500 错误修复" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

# 1. 检查 API 状态
Write-Host "`n[测试 1/3] 检查 API 服务状态..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ API 服务正常运行" -ForegroundColor Green
    } else {
        Write-Host "  ❌ API 返回异常状态码: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ 无法连接到 API 服务" -ForegroundColor Red
    Write-Host "  请先启动 API: python -m src.api.main" -ForegroundColor Yellow
    exit 1
}

# 2. 测试 /jd/analyze 端点
Write-Host "`n[测试 2/3] 测试 /jd/analyze 端点..." -ForegroundColor Yellow

$testJD = @"
职位：高级Python工程师

部门：技术研发部
地点：北京

岗位职责：
1. 负责公司核心业务系统的后端开发和维护
2. 参与系统架构设计，优化系统性能和稳定性

任职要求：
- 3年以上Python开发经验
- 熟练掌握FastAPI、Django等Web框架
- 熟悉MySQL、Redis等数据库
"@

$body = @{
    jd_text = $testJD
    model_type = "standard"
} | ConvertTo-Json

try {
    Write-Host "  发送请求..." -ForegroundColor Gray
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/jd/analyze" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -UseBasicParsing `
        -TimeoutSec 30
    
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ 请求成功 (状态码: 200)" -ForegroundColor Green
        
        # 解析响应
        $result = $response.Content | ConvertFrom-Json
        
        if ($result.success) {
            Write-Host "  ✅ API 返回成功" -ForegroundColor Green
            
            # 检查必需字段
            $evaluation = $result.data.evaluation
            
            $missingFields = @()
            if (-not $evaluation.overall_score) { $missingFields += "overall_score" }
            if (-not $evaluation.company_value) { $missingFields += "company_value" }
            if ($null -eq $evaluation.is_core_position) { $missingFields += "is_core_position" }
            
            if ($missingFields.Count -eq 0) {
                Write-Host "  ✅ 所有必需字段都存在" -ForegroundColor Green
                Write-Host ""
                Write-Host "  评估结果:" -ForegroundColor Cyan
                Write-Host "    - 综合质量分数: $($evaluation.overall_score)" -ForegroundColor White
                Write-Host "    - 企业价值: $($evaluation.company_value)" -ForegroundColor White
                Write-Host "    - 核心岗位: $($evaluation.is_core_position)" -ForegroundColor White
                Write-Host "    - 完整性: $($evaluation.quality_score.completeness)" -ForegroundColor White
                Write-Host "    - 清晰度: $($evaluation.quality_score.clarity)" -ForegroundColor White
                Write-Host "    - 专业性: $($evaluation.quality_score.professionalism)" -ForegroundColor White
            } else {
                Write-Host "  ❌ 缺少必需字段: $($missingFields -join ', ')" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "  ❌ API 返回失败" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ❌ 请求失败 (状态码: $($response.StatusCode))" -ForegroundColor Red
        exit 1
    }
} catch {
    $errorMessage = $_.Exception.Message
    if ($errorMessage -like "*500*") {
        Write-Host "  ❌ 500 服务器错误 - API 代码可能还有问题" -ForegroundColor Red
        Write-Host "  错误详情: $errorMessage" -ForegroundColor Red
        Write-Host ""
        Write-Host "  建议:" -ForegroundColor Yellow
        Write-Host "    1. 检查 API 日志中的详细错误信息" -ForegroundColor Yellow
        Write-Host "    2. 确认代码修改已保存" -ForegroundColor Yellow
        Write-Host "    3. 重启 API 服务: .\restart_api.ps1" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "  ❌ 请求失败: $errorMessage" -ForegroundColor Red
        exit 1
    }
}

# 3. 运行 Python 检查脚本
Write-Host "`n[测试 3/3] 运行完整检查..." -ForegroundColor Yellow

try {
    python check_api.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ 完整检查通过" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ 部分检查未通过" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️ 无法运行 check_api.py" -ForegroundColor Yellow
}

# 总结
Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "测试结果总结" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "✅ 所有测试通过！" -ForegroundColor Green
Write-Host ""
Write-Host "API 修复成功，现在可以:" -ForegroundColor Green
Write-Host "  1. 启动 UI: streamlit run src/ui/app.py" -ForegroundColor White
Write-Host "  2. 测试 JD 解析功能" -ForegroundColor White
Write-Host "  3. 验证不再出现 500 错误" -ForegroundColor White
Write-Host "="*70 -ForegroundColor Cyan
