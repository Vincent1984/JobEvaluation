# 项目启动指南

## 快速启动

### 方式1：使用启动脚本（推荐）

**Windows:**
```bash
scripts\start_all.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start_all.sh
./scripts/start_all.sh
```

### 方式2：手动启动各服务

#### 1. 初始化数据库
```bash
python scripts/init_db.py
# 选择选项 1 (初始化数据库)
```

#### 2. 启动 API 服务（新终端窗口）
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 启动 Streamlit UI（新终端窗口）
```bash
python -m streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0
```

#### 4. （可选）启动 Redis
如果需要使用 Redis 缓存：
```bash
# Windows: 下载并安装 Redis for Windows
# Linux/Mac:
redis-server
```

## 访问地址

启动成功后，可以通过以下地址访问：

- **Streamlit UI**: http://localhost:8501
- **API 文档**: http://localhost:8000/docs
- **API 健康检查**: http://localhost:8000/health

## 服务说明

### 1. API 服务 (FastAPI)
- 端口: 8000
- 提供 RESTful API 接口
- 自动生成 API 文档（Swagger UI）

### 2. UI 服务 (Streamlit)
- 端口: 8501
- 提供 Web 界面
- 支持 JD 上传、分析、匹配等功能

### 3. Redis（可选）
- 端口: 6379
- 用于 LLM 响应缓存
- 如果未启动，系统会使用内存缓存

## 环境配置

确保 `.env` 文件已正确配置：

```env
# DeepSeek API 配置
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-reasoner

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/jd_analyzer.db

# Redis 配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## 停止服务

### 使用脚本停止
```bash
# Windows
scripts\stop_all.bat

# Linux/Mac
./scripts/stop_all.sh
```

### 手动停止
在各个终端窗口按 `Ctrl+C`

## 故障排查

### 问题1：端口被占用
```bash
# Windows - 查找占用端口的进程
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# 杀死进程
taskkill /PID <进程ID> /F
```

### 问题2：Redis 连接失败
- 检查 Redis 是否已启动
- 或者在 `.env` 中禁用 Redis，使用内存缓存

### 问题3：数据库错误
```bash
# 重新初始化数据库
python scripts/init_db.py
# 选择选项 2 (重置数据库)
```

### 问题4：API 无法访问
- 检查防火墙设置
- 确认 8000 端口未被占用
- 查看日志: `logs/api.log`

### 问题5：UI 无法访问
- 检查 8501 端口未被占用
- 查看日志: `logs/ui.log`

## 开发模式

### 启用热重载
API 服务已默认启用 `--reload` 参数，代码修改后会自动重启。

### 查看日志
```bash
# Windows
type logs\api.log
type logs\ui.log

# Linux/Mac
tail -f logs/api.log
tail -f logs/ui.log
```

### 调试模式
在 `.env` 中设置：
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 性能优化

系统已实现以下性能优化（任务 11.4）：

1. **LLM 调用优化**
   - 请求去重
   - 并发控制
   - 智能缓存

2. **数据库优化**
   - 连接池配置
   - 批量操作
   - 查询缓存

3. **文件处理优化**
   - 并行解析
   - 异步处理

4. **缓存策略**
   - 多级缓存
   - 缓存预热

详见：`docs/PERFORMANCE_OPTIMIZATION.md`

## 生产部署

### 使用 Docker
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Gunicorn（生产环境）
```bash
# 安装 Gunicorn
pip install gunicorn

# 启动 API
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 健康检查

```bash
# 运行健康检查脚本
python scripts/health_check.py

# 或访问 API 健康检查端点
curl http://localhost:8000/health
```

## 下一步

1. 配置 DeepSeek API 密钥
2. 上传 JD 文件进行测试
3. 查看 API 文档了解更多功能
4. 阅读用户手册：`QUICKSTART.md`

## 技术支持

如遇问题，请查看：
- 项目文档：`README.md`
- API 文档：http://localhost:8000/docs
- 性能优化文档：`docs/PERFORMANCE_OPTIMIZATION.md`
