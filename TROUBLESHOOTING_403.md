# 故障排除：403 错误

## 问题描述

在 UI 中上传岗位附件或使用某些功能时出现：
```
AxiosError: Request failed with status code 403
```

或

```
❌ API请求失败: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded
```

## 原因分析

### 主要原因：API 服务未启动

UI 中的某些功能需要调用 API 服务：
- ✅ JD 分析（文本输入）- 不需要 API
- ✅ JD 分析（文件上传）- 不需要 API
- ✅ 批量上传 - 不需要 API
- ❌ 职位分类管理 - **需要 API**
- ❌ 问卷管理 - **需要 API**
- ❌ 匹配结果 - **需要 API**
- ❌ 模板管理 - **需要 API**

## 解决方案

### 方案 1：使用启动脚本（推荐）

双击运行 `start_services.bat`，会自动启动两个服务：
- API 服务（端口 8000）
- UI 服务（端口 8501）

### 方案 2：手动启动服务

#### 步骤 1：启动 API 服务

打开第一个命令行窗口：
```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

等待看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 步骤 2：启动 UI 服务

打开第二个命令行窗口：
```bash
streamlit run src/ui/app.py --server.port 8501
```

等待看到：
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 方案 3：仅使用不需要 API 的功能

如果不想启动 API 服务，可以只使用以下功能：
- ✅ JD 分析（文本输入或文件上传）
- ✅ 批量上传
- ✅ 历史记录

避免使用：
- ❌ 职位分类管理
- ❌ 问卷管理
- ❌ 匹配结果
- ❌ 模板管理

## 验证服务状态

### 检查 API 服务

在浏览器中访问：
```
http://localhost:8000/health
```

应该看到：
```json
{"status": "healthy"}
```

### 检查 API 文档

访问：
```
http://localhost:8000/docs
```

应该看到 Swagger API 文档界面。

### 检查 UI 服务

访问：
```
http://localhost:8501
```

应该看到 JD 分析器界面。

## 常见错误

### 错误 1：端口被占用

```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**解决方案**：
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程（替换 PID）
taskkill /PID <进程ID> /F
```

### 错误 2：模块未找到

```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案**：
```bash
pip install -r requirements.txt
```

### 错误 3：CORS 错误

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解决方案**：
- 确保 API 服务正在运行
- 检查 `src/api/__init__.py` 中的 CORS 配置
- 当前配置允许所有来源（`allow_origins=["*"]`）

## 功能对照表

| 功能 | 需要 API | 说明 |
|------|---------|------|
| JD 分析（文本） | ❌ | 直接使用 Simple MCP Client |
| JD 分析（文件） | ❌ | 本地解析文件 |
| 批量上传 | ❌ | 本地处理 |
| 职位分类管理 | ✅ | 需要 API 存储数据 |
| 问卷管理 | ✅ | 需要 API 存储数据 |
| 匹配结果 | ✅ | 需要 API 存储数据 |
| 模板管理 | ✅ | 需要 API 存储数据 |
| 历史记录 | ❌ | 使用 session_state |

## 架构说明

### 当前架构（MVP）

```
┌─────────────────────────────────────┐
│         Streamlit UI                │
│  - JD 分析（Simple MCP Client）     │
│  - 批量上传（Simple MCP Client）    │
│  - 历史记录（session_state）        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         FastAPI                     │
│  - 职位分类管理                      │
│  - 问卷管理                          │
│  - 匹配结果                          │
│  - 模板管理                          │
└─────────────────────────────────────┘
```

### 为什么这样设计？

1. **核心功能优先**：JD 分析是核心功能，不依赖 API 可以独立运行
2. **简化部署**：MVP 阶段可以只启动 UI，快速验证核心功能
3. **渐进增强**：需要数据持久化的功能通过 API 实现

## 推荐使用方式

### 开发/测试阶段

只启动 UI 服务，使用核心功能：
```bash
streamlit run src/ui/app.py --server.port 8501
```

### 完整功能使用

启动两个服务：
```bash
# 方式 1：使用启动脚本
start_services.bat

# 方式 2：手动启动
# 终端 1
python -m uvicorn src.api.main:app --reload --port 8000

# 终端 2
streamlit run src/ui/app.py --server.port 8501
```

## 总结

403 错误通常是因为 API 服务未启动。根据你的需求：

- **只需要 JD 分析**：只启动 UI 即可
- **需要完整功能**：启动 API + UI

使用 `start_services.bat` 可以一键启动所有服务！

---

**文档版本**: 1.0  
**最后更新**: 2024年
