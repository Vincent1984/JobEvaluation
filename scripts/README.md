# 启动脚本说明

本目录包含用于启动和管理岗位JD分析器服务的脚本。

## 脚本列表

### 启动脚本

#### Linux/Mac
- `start_all.sh` - 启动所有服务（API、UI、Agents）
- `stop_all.sh` - 停止所有服务

#### Windows
- `start_all.bat` - 启动所有服务（API、UI、Agents）
- `stop_all.bat` - 停止所有服务

### 管理脚本

- `start_agents.py` - 启动所有MCP Agents
- `health_check.py` - 检查所有服务的健康状态
- `init_db.py` - 初始化数据库

## 使用方法

### 首次启动

#### Linux/Mac

```bash
# 1. 添加执行权限
chmod +x scripts/*.sh

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置API密钥等

# 3. 启动所有服务
./scripts/start_all.sh
```

#### Windows

```cmd
REM 1. 配置环境变量
copy .env.example .env
REM 编辑.env文件，配置API密钥等

REM 2. 启动所有服务
scripts\start_all.bat
```

### 停止服务

#### Linux/Mac
```bash
./scripts/stop_all.sh
```

#### Windows
```cmd
scripts\stop_all.bat
```

### 健康检查

```bash
# Linux/Mac
python3 scripts/health_check.py

# Windows
python scripts\health_check.py
```

### 单独启动Agents

```bash
# Linux/Mac
python3 scripts/start_agents.py

# Windows
python scripts\start_agents.py
```

## 服务端口

- **API服务**: http://localhost:8000
- **UI服务**: http://localhost:8501
- **Redis**: localhost:6379

## 日志文件

所有日志文件位于 `logs/` 目录：

- `logs/agents.log` - Agents日志
- `logs/api.log` - API服务日志
- `logs/ui.log` - UI服务日志

查看实时日志：

```bash
# Linux/Mac
tail -f logs/agents.log
tail -f logs/api.log
tail -f logs/ui.log

# Windows
type logs\agents.log
type logs\api.log
type logs\ui.log
```

## 进程管理

### Linux/Mac

启动脚本会将进程ID保存到以下文件：
- `.agents.pid`
- `.api.pid`
- `.ui.pid`

可以使用这些PID手动管理进程：

```bash
# 查看进程状态
ps -p $(cat .api.pid)

# 手动停止进程
kill $(cat .api.pid)
```

### Windows

使用任务管理器或tasklist命令查看进程：

```cmd
tasklist | findstr python
```

## 故障排查

### 服务无法启动

1. 检查端口是否被占用：
   ```bash
   # Linux/Mac
   lsof -i :8000
   lsof -i :8501
   lsof -i :6379
   
   # Windows
   netstat -ano | findstr :8000
   netstat -ano | findstr :8501
   netstat -ano | findstr :6379
   ```

2. 检查Redis是否运行：
   ```bash
   # Linux/Mac
   redis-cli ping
   
   # Windows
   redis-cli.exe ping
   ```

3. 查看日志文件获取详细错误信息

### Redis连接失败

确保Redis已安装并运行：

```bash
# Linux/Mac
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu

redis-server --daemonize yes

# Windows
# 下载并安装Redis for Windows
# 或使用Docker: docker run -d -p 6379:6379 redis
```

### 数据库错误

重新初始化数据库：

```bash
python scripts/init_db.py
```

### 权限错误（Linux/Mac）

确保脚本有执行权限：

```bash
chmod +x scripts/*.sh
```

## 开发模式

在开发模式下，可以单独启动各个服务：

```bash
# 启动API（带自动重载）
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 启动UI（带自动重载）
streamlit run src/ui/app.py --server.port 8501

# 启动Agents
python scripts/start_agents.py
```

## Docker部署

如果使用Docker，请参考 `DOCKER_README.md`：

```bash
# 使用Docker Compose启动
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 生产环境建议

1. **使用进程管理器**：
   - Linux: systemd, supervisor
   - 推荐使用Docker Compose

2. **配置反向代理**：
   - 使用Nginx或Traefik

3. **启用日志轮转**：
   - 配置logrotate（Linux）

4. **监控服务健康**：
   - 定期运行health_check.py
   - 配置告警

5. **数据备份**：
   - 定期备份data/目录
   - 备份Redis数据

## 环境变量

关键环境变量（在.env文件中配置）：

```env
# LLM配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# 数据库配置
DATABASE_URL=sqlite:///./data/jd_analyzer.db

# API配置
API_HOST=0.0.0.0
API_PORT=8000
```

## 支持

如有问题，请查看：
- 主文档: README.md
- Docker文档: DOCKER_README.md
- API文档: http://localhost:8000/docs
