# 启动 API 服务指南

## 当前状态
❌ API 服务未运行（端口 8000 未监听）

## 快速启动

### 方法 1: 使用 Python 模块方式（推荐）

```bash
python -m src.api.main
```

或者在 PowerShell 中：

```powershell
python -m src.api.main
```

### 方法 2: 使用 uvicorn 直接启动

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 方法 3: 使用启动脚本

如果项目中有启动脚本：

```bash
# Windows
start_api.bat

# Linux/Mac
./start_api.sh
```

## 验证 API 服务

### 1. 检查端口是否监听

**PowerShell**:
```powershell
Test-NetConnection -ComputerName localhost -Port 8000
```

**CMD**:
```cmd
netstat -an | findstr :8000
```

### 2. 访问 API 文档

启动成功后，在浏览器中访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 3. 测试 API 端点

```bash
# 使用 curl
curl http://localhost:8000/health

# 使用 PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health
```

## 常见问题

### Q1: 端口 8000 已被占用

**错误信息**:
```
Error: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): 通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

**解决方案**:

1. **查找占用端口的进程**:
   ```powershell
   netstat -ano | findstr :8000
   ```

2. **终止进程**:
   ```powershell
   taskkill /PID <进程ID> /F
   ```

3. **或者使用其他端口**:
   ```bash
   uvicorn src.api.main:app --port 8001
   ```
   
   然后更新 UI 配置：
   ```python
   # src/ui/app.py
   API_BASE_URL = "http://localhost:8001/api/v1"
   ```

### Q2: 找不到模块

**错误信息**:
```
ModuleNotFoundError: No module named 'src'
```

**解决方案**:

1. **确保在项目根目录**:
   ```bash
   cd D:\project\JobEvaluation
   ```

2. **检查 Python 路径**:
   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   ```

3. **设置 PYTHONPATH**:
   ```powershell
   $env:PYTHONPATH = "D:\project\JobEvaluation"
   python -m src.api.main
   ```

### Q3: 缺少依赖包

**错误信息**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案**:

安装依赖：
```bash
pip install -r requirements.txt
```

或者手动安装核心依赖：
```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

### Q4: 数据库连接失败

**错误信息**:
```
Could not connect to database
```

**解决方案**:

1. **检查数据库配置**:
   ```python
   # src/api/config.py 或 .env
   DATABASE_URL = "sqlite:///./jd_analyzer.db"
   ```

2. **初始化数据库**:
   ```bash
   python -m src.database.init_db
   ```

## 同时运行 API 和 UI

### 方法 1: 使用两个终端窗口

**终端 1 - API 服务**:
```bash
python -m src.api.main
```

**终端 2 - Streamlit UI**:
```bash
streamlit run src/ui/app.py
```

### 方法 2: 使用后台进程（PowerShell）

```powershell
# 启动 API（后台）
Start-Process python -ArgumentList "-m", "src.api.main" -WindowStyle Hidden

# 启动 UI（前台）
streamlit run src/ui/app.py
```

### 方法 3: 使用启动脚本

创建 `start_all.bat`:
```batch
@echo off
echo Starting API service...
start "API Service" python -m src.api.main

echo Waiting for API to start...
timeout /t 5 /nobreak

echo Starting Streamlit UI...
streamlit run src/ui/app.py
```

然后运行：
```bash
start_all.bat
```

## 检查 API 服务状态

### 创建检查脚本

创建 `check_api.py`:
```python
import requests
import sys

API_BASE_URL = "http://localhost:8000"

def check_api():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API 服务正常运行")
            print(f"   URL: {API_BASE_URL}")
            return True
        else:
            print(f"⚠️ API 返回状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务")
        print(f"   请确保 API 服务正在运行: {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    success = check_api()
    sys.exit(0 if success else 1)
```

运行检查：
```bash
python check_api.py
```

## API 服务配置

### 环境变量

创建 `.env` 文件：
```env
# API 配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# 数据库配置
DATABASE_URL=sqlite:///./jd_analyzer.db

# LLM 配置
OPENAI_API_KEY=your_api_key_here
DEEPSEEK_API_KEY=your_api_key_here

# 日志配置
LOG_LEVEL=INFO
```

### 配置文件

`src/api/config.py`:
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./jd_analyzer.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 日志和调试

### 查看 API 日志

API 启动后会在控制台输出日志：

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 启用详细日志

```bash
# 设置日志级别为 DEBUG
uvicorn src.api.main:app --log-level debug
```

### 查看请求日志

在 API 代码中添加日志：
```python
import logging

logger = logging.getLogger(__name__)

@app.get("/jd/list")
async def list_jds():
    logger.info("Received request to list JDs")
    # ...
```

## 下一步

1. **启动 API 服务**:
   ```bash
   python -m src.api.main
   ```

2. **验证 API 运行**:
   - 访问 http://localhost:8000/docs
   - 或运行 `python check_api.py`

3. **启动 UI**:
   ```bash
   streamlit run src/ui/app.py
   ```

4. **测试功能**:
   - 解析 JD
   - 评估 JD
   - 管理企业和分类

## 需要帮助？

如果遇到问题：

1. 检查错误日志
2. 确认依赖已安装
3. 验证配置文件
4. 查看相关文档：
   - `API_QUICKSTART.md`
   - `QUICK_TEST_GUIDE.md`
   - `API_ENDPOINT_FIX.md`

## 相关命令速查

```bash
# 启动 API
python -m src.api.main

# 启动 UI
streamlit run src/ui/app.py

# 检查端口
netstat -ano | findstr :8000

# 安装依赖
pip install -r requirements.txt

# 检查 API 状态
python check_api.py

# 查看 API 文档
# 浏览器访问: http://localhost:8000/docs
```
