# 重启 API 服务器指南

## 为什么需要重启？

我们修复了 API 代码中的问题，但 API 服务器还在运行旧代码。需要重启服务器以加载新代码。

## 修复内容

### 文件: `src/mcp/simple_client.py`

**问题**: `analyze_jd` 方法返回的 `EvaluationResult` 对象缺少必需字段

**修复**:
1. ✅ 添加了 `overall_score` 字段
2. ✅ 添加了 `company_value` 字段  
3. ✅ 添加了 `is_core_position` 字段
4. ✅ 添加了 `dimension_contributions` 字段
5. ✅ 正确映射 `dimension_scores` 到 `QualityScore` 字段

## 重启步骤

### 方法 1: 使用 Ctrl+C 重启（推荐）

1. **找到运行 API 的终端窗口**

2. **停止 API 服务**:
   - 按 `Ctrl+C` 停止服务器

3. **重新启动 API**:
   ```bash
   python -m src.api.main
   ```

4. **等待启动完成**:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

### 方法 2: 使用任务管理器（Windows）

1. **打开任务管理器**:
   - 按 `Ctrl+Shift+Esc`

2. **找到 Python 进程**:
   - 在"详细信息"标签页中找到 `python.exe`
   - 查看命令行参数，找到运行 API 的进程

3. **结束进程**:
   - 右键点击 → 结束任务

4. **重新启动 API**:
   ```bash
   python -m src.api.main
   ```

### 方法 3: 使用 PowerShell 命令

```powershell
# 1. 找到占用 8000 端口的进程
$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($process) {
    # 2. 停止进程
    Stop-Process -Id $process -Force
    Write-Host "API 服务已停止"
} else {
    Write-Host "未找到运行在 8000 端口的进程"
}

# 3. 等待 2 秒
Start-Sleep -Seconds 2

# 4. 重新启动 API
python -m src.api.main
```

## 验证修复

### 1. 检查 API 状态

```bash
python check_api.py
```

预期输出:
```
✅ API 服务正常运行
```

### 2. 测试 /jd/analyze 端点

**PowerShell**:
```powershell
$body = @{
    jd_text = "职位：高级Python工程师`n职责：负责后端开发"
    model_type = "standard"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/jd/analyze" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**预期响应**:
```json
{
  "success": true,
  "data": {
    "jd": {
      "id": "jd_xxx",
      "job_title": "高级Python工程师",
      ...
    },
    "evaluation": {
      "id": "eval_xxx",
      "jd_id": "jd_xxx",
      "model_type": "standard",
      "overall_score": 85.0,  // ✅ 现在有这个字段了
      "company_value": "中价值",  // ✅ 现在有这个字段了
      "is_core_position": false,  // ✅ 现在有这个字段了
      "quality_score": {
        "overall_score": 85.0,
        "completeness": 90.0,
        "clarity": 80.0,
        "professionalism": 85.0,
        "issues": []
      },
      ...
    }
  }
}
```

### 3. 测试 UI

1. **启动 UI** (如果还没启动):
   ```bash
   streamlit run src/ui/app.py
   ```

2. **测试 JD 解析**:
   - 进入"📝 JD解析（第一步）"
   - 输入 JD 文本
   - 点击"解析并保存"
   - ✅ 应该成功，不再出现 500 错误

3. **查看结果**:
   - 应该能看到解析结果
   - 应该能看到质量评分
   - 应该能看到优化建议

## 常见问题

### Q1: 重启后还是 500 错误？

**检查步骤**:
1. 确认 API 服务器已完全重启
2. 检查 API 日志中的错误信息
3. 确认修改的文件已保存
4. 尝试清除 Python 缓存:
   ```bash
   # 删除 __pycache__ 目录
   Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
   
   # 删除 .pyc 文件
   Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
   ```

### Q2: 找不到 API 进程？

**解决方案**:
```powershell
# 查找所有 Python 进程
Get-Process python | Format-Table Id, ProcessName, StartTime

# 或者查找占用 8000 端口的进程
netstat -ano | findstr :8000
```

### Q3: 端口被占用？

**解决方案**:
```powershell
# 找到占用端口的进程 ID
netstat -ano | findstr :8000

# 结束进程（替换 <PID> 为实际进程 ID）
taskkill /PID <PID> /F
```

## 自动重启（可选）

如果您使用 `--reload` 参数启动 API，代码修改后会自动重启：

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

但有时自动重启可能不会加载所有更改，建议手动重启。

## 下一步

重启 API 后：

1. ✅ 运行 `python check_api.py` 验证状态
2. ✅ 测试 `/jd/analyze` 端点
3. ✅ 在 UI 中测试 JD 解析功能
4. ✅ 确认不再出现 500 错误

## 相关文档

- `API_500_ERROR_FIX.md` - 问题分析和修复说明
- `START_API_SERVICE.md` - API 服务启动指南
- `check_api.py` - API 状态检查脚本

## 更新日期

2025-01-XX
