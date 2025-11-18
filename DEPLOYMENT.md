# 岗位JD分析器 - 部署文档

> 📚 **完整部署指南** - 涵盖本地开发、Docker部署和生产环境配置

## 目录

- [系统要求](#系统要求)
- [安装说明](#安装说明)
- [配置说明](#配置说明)
- [部署方式](#部署方式)
- [使用指南](#使用指南)
- [运维管理](#运维管理)
- [故障排除](#故障排除)
- [安全建议](#安全建议)

---

## 系统要求

### 硬件要求

**最低配置：**
- CPU: 2核心
- 内存: 4GB RAM
- 磁盘: 10GB可用空间
- 网络: 稳定的互联网连接

**推荐配置：**
- CPU: 4核心或更多
- 内存: 8GB RAM或更多
- 磁盘: 20GB可用空间（SSD推荐）
- 网络: 高速互联网连接

### 软件要求

**必需软件：**
- Python 3.11 或更高版本
- pip (Python包管理器)

**可选软件：**
- Docker 20.10+ 和 Docker Compose 2.0+ (用于容器化部署)
- Redis 6.0+ (用于Agent通讯，Docker部署时自动包含)
- Git (用于版本控制)

### 操作系统支持

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, CentOS 8+, Debian 10+)

---

## 安装说明

### 方式1: 快速安装（推荐新手）


#### Windows用户

```bash
# 1. 下载或克隆项目
git clone <repository-url>
cd jd-analyzer

# 2. 运行自动安装脚本
start.bat

# 3. 按提示选择选项1启动UI
```

#### Linux/Mac用户

```bash
# 1. 下载或克隆项目
git clone <repository-url>
cd jd-analyzer

# 2. 添加执行权限并运行
chmod +x start.sh
./start.sh

# 3. 按提示选择选项1启动UI
```

### 方式2: 手动安装（推荐开发者）

#### 步骤1: 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

#### 步骤2: 安装依赖

```bash
# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

#### 步骤3: 验证安装

```bash
# 检查Python版本
python --version  # 应该显示 3.11 或更高

# 检查依赖安装
pip list | grep streamlit
pip list | grep fastapi
```

### 方式3: Docker安装（推荐生产环境）


#### 前置条件

```bash
# 安装Docker和Docker Compose
# Windows/Mac: 下载Docker Desktop
# Linux: 使用包管理器安装

# 验证安装
docker --version
docker-compose --version
```

#### 快速启动

```bash
# 1. 克隆项目
git clone <repository-url>
cd jd-analyzer

# 2. 配置环境变量（见下文）
cp .env.example .env
# 编辑 .env 文件

# 3. 构建并启动服务
docker-compose up -d

# 4. 初始化数据库
docker-compose exec api python scripts/init_db.py

# 5. 查看服务状态
docker-compose ps
```

详细Docker部署说明请参考 [DOCKER_README.md](DOCKER_README.md)

---

## 配置说明

### 环境变量配置

#### 步骤1: 创建配置文件

```bash
# 复制环境变量模板
cp .env.example .env
```

#### 步骤2: 配置LLM服务

**选项A: 使用OpenAI（推荐国际用户）**

```env
# OpenAI配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# 可选：使用GPT-3.5降低成本
# LLM_MODEL=gpt-3.5-turbo
```

**获取OpenAI API密钥：**
1. 访问 https://platform.openai.com/
2. 注册账号并完成验证
3. 充值账户（建议至少$10）
4. 创建API密钥并复制


**选项B: 使用DeepSeek（推荐国内用户）**

```env
# DeepSeek配置
OPENAI_API_KEY=sk-your-deepseek-api-key-here
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# 或使用DeepSeek推理模型（更强大）
# LLM_MODEL=deepseek-reasoner
```

**获取DeepSeek API密钥：**
1. 访问 https://platform.deepseek.com/
2. 注册账号
3. 创建API密钥并复制
4. 充值（可选，有免费额度）

**选项C: 使用其他兼容OpenAI的服务**

```env
# 自定义API配置
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-api-endpoint/v1
LLM_MODEL=your-model-name
```

#### 步骤3: 配置Redis（可选）

```env
# Redis配置（用于Agent通讯）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # 留空表示无密码
REDIS_DB=0

# Docker部署时使用
# REDIS_HOST=redis
```

#### 步骤4: 配置数据库

```env
# SQLite配置（默认）
DATABASE_URL=sqlite:///./data/jd_analyzer.db

# 或使用PostgreSQL（生产环境推荐）
# DATABASE_URL=postgresql://user:password@localhost:5432/jd_analyzer
```

#### 步骤5: 配置API服务

```env
# API服务配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true  # 开发环境设为true，生产环境设为false

# CORS配置
CORS_ORIGINS=["http://localhost:8501", "http://localhost:3000"]
```


#### 步骤6: 配置日志

```env
# 日志配置
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

### 完整配置示例

```env
# ==================== LLM配置 ====================
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000

# ==================== Redis配置 ====================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite:///./data/jd_analyzer.db

# ==================== API配置 ====================
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
CORS_ORIGINS=["*"]

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ==================== 文件上传配置 ====================
MAX_FILE_SIZE=10485760  # 10MB
MAX_BATCH_SIZE=20
MAX_TOTAL_SIZE=104857600  # 100MB
UPLOAD_DIR=./uploads

# ==================== 缓存配置 ====================
ENABLE_CACHE=true
CACHE_TTL=3600  # 1小时
```

---

## 部署方式

### 部署方式1: 本地开发环境

**适用场景：** 开发、测试、个人使用

#### 启动步骤

```bash
# 1. 激活虚拟环境
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 2. 启动Streamlit UI（最简单）
streamlit run src/ui/app.py

# 或使用启动脚本
python run.py
# 选择选项1: 启动Streamlit UI
```


#### 访问应用

- **Streamlit UI**: http://localhost:8501
- 应用会自动在浏览器中打开

#### 停止服务

```bash
# 在终端中按 Ctrl+C
```

### 部署方式2: 完整服务部署

**适用场景：** 团队使用、需要API接口

#### 启动步骤

**方式A: 使用启动脚本（推荐）**

```bash
# Windows
scripts\start_all.bat

# Linux/Mac
chmod +x scripts/start_all.sh
./scripts/start_all.sh
```

**方式B: 手动启动各服务**

```bash
# 终端1: 启动Redis（如果需要Agent功能）
redis-server

# 终端2: 启动FastAPI后端
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 终端3: 启动Agent服务（可选）
python scripts/start_agents.py

# 终端4: 启动Streamlit前端
streamlit run src/ui/app.py
```

#### 访问应用

- **Streamlit UI**: http://localhost:8501
- **FastAPI文档**: http://localhost:8000/docs
- **API健康检查**: http://localhost:8000/health

#### 停止服务

```bash
# Windows
scripts\stop_all.bat

# Linux/Mac
./scripts/stop_all.sh

# 或手动在每个终端按 Ctrl+C
```


### 部署方式3: Docker容器化部署

**适用场景：** 生产环境、云部署、团队协作

#### 启动步骤

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动所有服务
docker-compose up -d

# 3. 初始化数据库
docker-compose exec api python scripts/init_db.py

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

#### 访问应用

- **Streamlit UI**: http://localhost:8501
- **FastAPI文档**: http://localhost:8000/docs
- **Redis**: localhost:6379

#### 服务管理

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

详细说明请参考 [DOCKER_README.md](DOCKER_README.md)

### 部署方式4: 生产环境部署

**适用场景：** 正式上线、高可用需求

#### 架构建议

```
[负载均衡器 Nginx/HAProxy]
         |
    [API服务集群]
         |
    [Redis集群]
         |
    [数据库主从]
```


#### 生产环境配置

**1. 使用生产环境变量**

```bash
# 创建生产环境配置
cp .env.example .env.production

# 编辑生产配置
nano .env.production
```

```env
# 生产环境配置示例
OPENAI_API_KEY=sk-prod-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# 使用PostgreSQL
DATABASE_URL=postgresql://user:password@db-host:5432/jd_analyzer

# Redis集群
REDIS_HOST=redis-cluster.example.com
REDIS_PORT=6379
REDIS_PASSWORD=strong-password

# 生产API配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
LOG_LEVEL=WARNING

# 安全配置
CORS_ORIGINS=["https://your-domain.com"]
```

**2. 配置反向代理（Nginx）**

```nginx
# /etc/nginx/sites-available/jd-analyzer
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Streamlit UI
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # FastAPI
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```


**3. 使用进程管理器（Supervisor）**

```ini
# /etc/supervisor/conf.d/jd-analyzer.conf

[program:jd-analyzer-api]
command=/path/to/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/path/to/jd-analyzer
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/jd-analyzer/api.err.log
stdout_logfile=/var/log/jd-analyzer/api.out.log

[program:jd-analyzer-ui]
command=/path/to/venv/bin/streamlit run src/ui/app.py --server.port 8501
directory=/path/to/jd-analyzer
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/jd-analyzer/ui.err.log
stdout_logfile=/var/log/jd-analyzer/ui.out.log

[program:jd-analyzer-agents]
command=/path/to/venv/bin/python scripts/start_agents.py
directory=/path/to/jd-analyzer
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/jd-analyzer/agents.err.log
stdout_logfile=/var/log/jd-analyzer/agents.out.log
```

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start jd-analyzer-api
sudo supervisorctl start jd-analyzer-ui
sudo supervisorctl start jd-analyzer-agents

# 查看状态
sudo supervisorctl status
```

**4. 使用Systemd服务**

```ini
# /etc/systemd/system/jd-analyzer-api.service
[Unit]
Description=JD Analyzer API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/jd-analyzer
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl enable jd-analyzer-api
sudo systemctl start jd-analyzer-api
sudo systemctl status jd-analyzer-api
```

---

## 使用指南


### 基本使用流程

#### 1. 首次使用

```bash
# 1. 启动应用
streamlit run src/ui/app.py

# 2. 浏览器访问 http://localhost:8501

# 3. 在"JD分析"页面点击"加载示例JD"

# 4. 点击"开始分析"按钮

# 5. 等待10-30秒查看结果
```

#### 2. 分析自己的JD

**方式A: 文本输入**
1. 在"JD分析"页面的文本框中粘贴JD内容
2. 选择评估模型（标准/美世法/因素法）
3. 点击"开始分析"
4. 查看解析结果、质量评分和优化建议

**方式B: 文件上传**
1. 点击"上传JD文件"
2. 选择TXT、PDF或DOCX文件
3. 系统自动解析并分析
4. 查看结果

#### 3. 批量处理JD

1. 进入"批量上传"页面
2. 选择多个JD文件（最多20个）
3. 点击"开始批量处理"
4. 实时查看处理进度
5. 查看批量处理结果汇总

#### 4. 管理职位分类

1. 进入"职位分类管理"页面
2. 创建分类层级（最多3层）
3. 为第三层级添加样本JD（1-2个）
4. 系统自动使用分类进行JD归类

#### 5. 生成评估问卷

1. 选择已分析的JD
2. 进入"问卷管理"页面
3. 点击"生成问卷"
4. 预览和编辑问卷
5. 生成分享链接发送给候选人

#### 6. 查看匹配结果

1. 进入"匹配结果"页面
2. 选择JD查看所有候选人匹配
3. 点击"查看详情"查看完整分析
4. 下载匹配报告（HTML/JSON）


### API使用指南

详细API使用说明请参考：
- [API_QUICKSTART.md](API_QUICKSTART.md) - API快速开始
- [src/api/README.md](src/api/README.md) - API完整文档
- http://localhost:8000/docs - Swagger交互式文档

#### 快速示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 解析JD
response = requests.post(
    f"{BASE_URL}/jd/parse",
    json={"jd_text": "招聘高级Python工程师..."}
)
jd = response.json()

# 2. 生成问卷
response = requests.post(
    f"{BASE_URL}/questionnaire/generate",
    json={
        "jd_id": jd["data"]["id"],
        "evaluation_model": "standard"
    }
)
questionnaire = response.json()

# 3. 批量上传
files = [
    ('files', open('jd1.txt', 'rb')),
    ('files', open('jd2.txt', 'rb'))
]
response = requests.post(
    f"{BASE_URL}/batch/upload",
    files=files,
    data={'model_type': 'standard'}
)
```

### 更多使用指南

- **快速开始**: [GET_STARTED.md](GET_STARTED.md)
- **详细使用**: [USAGE.md](USAGE.md)
- **UI指南**: [UI_QUICKSTART.md](UI_QUICKSTART.md)
- **演示指南**: [DEMO.md](DEMO.md)

---

## 运维管理

### 健康检查

#### 手动检查

```bash
# 检查API健康
curl http://localhost:8000/health

# 检查UI健康
curl http://localhost:8501/_stcore/health

# 检查Redis连接
redis-cli ping
```


#### 自动健康检查脚本

```bash
# 运行健康检查脚本
python scripts/health_check.py
```

#### Docker健康检查

```bash
# 查看容器健康状态
docker-compose ps

# 查看详细健康信息
docker inspect --format='{{.State.Health.Status}}' jd-analyzer-api
```

### 日志管理

#### 查看日志

```bash
# 应用日志
tail -f logs/app.log

# API日志
tail -f logs/api.log

# Agent日志
tail -f logs/agents.log

# Docker日志
docker-compose logs -f [service_name]
```

#### 日志轮转配置

```bash
# /etc/logrotate.d/jd-analyzer
/path/to/jd-analyzer/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
}
```

### 数据备份

#### 备份数据库

```bash
# SQLite备份
cp data/jd_analyzer.db data/jd_analyzer.db.backup.$(date +%Y%m%d)

# PostgreSQL备份
pg_dump -U user -d jd_analyzer > backup_$(date +%Y%m%d).sql
```

#### 备份上传文件

```bash
# 备份上传目录
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

#### Docker数据备份

```bash
# 备份数据卷
docker run --rm -v jd-analyzer_redis_data:/data -v $(pwd):/backup \
    alpine tar czf /backup/redis_backup_$(date +%Y%m%d).tar.gz /data
```


### 数据恢复

```bash
# 恢复SQLite数据库
cp data/jd_analyzer.db.backup.20240101 data/jd_analyzer.db

# 恢复PostgreSQL
psql -U user -d jd_analyzer < backup_20240101.sql

# 恢复上传文件
tar -xzf uploads_backup_20240101.tar.gz
```

### 性能监控

#### 系统资源监控

```bash
# CPU和内存使用
top
htop

# 磁盘使用
df -h

# Docker资源使用
docker stats
```

#### 应用性能监控

```bash
# API响应时间
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# 数据库查询性能
# 在应用日志中查看慢查询
```

### 更新和升级

#### 更新应用代码

```bash
# 1. 备份数据
./backup.sh

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
pip install -r requirements.txt --upgrade

# 4. 重启服务
# 本地部署
python run.py

# Docker部署
docker-compose down
docker-compose build
docker-compose up -d
```

#### 数据库迁移

```bash
# 运行数据库迁移脚本
python scripts/migrate_db.py

# 或重新初始化（会清空数据）
python scripts/init_db.py
```

---

## 故障排除


### 常见问题

#### 问题1: 启动失败

**症状：** 运行启动脚本后报错

**可能原因和解决方案：**

1. **Python版本不符**
```bash
# 检查Python版本
python --version

# 应该显示3.11或更高，否则需要升级Python
```

2. **依赖未安装**
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

3. **虚拟环境未激活**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **端口被占用**
```bash
# Windows查看端口占用
netstat -ano | findstr :8501
netstat -ano | findstr :8000

# Linux/Mac查看端口占用
lsof -i :8501
lsof -i :8000

# 杀死占用进程或更改端口
streamlit run src/ui/app.py --server.port 8502
```

#### 问题2: API调用失败

**症状：** 分析时提示API错误

**可能原因和解决方案：**

1. **API密钥错误**
```bash
# 检查.env文件中的API密钥
cat .env | grep OPENAI_API_KEY

# 确保密钥正确且有效
```

2. **网络连接问题**
```bash
# 测试API连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 或测试DeepSeek
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```


3. **API余额不足**
```bash
# 登录API平台检查余额
# OpenAI: https://platform.openai.com/account/usage
# DeepSeek: https://platform.deepseek.com/usage
```

4. **请求超时**
```env
# 在.env中增加超时时间
LLM_TIMEOUT=120  # 秒
```

#### 问题3: Redis连接失败

**症状：** Agent功能无法使用

**解决方案：**

1. **确保Redis已启动**
```bash
# 启动Redis
redis-server

# 或使用Docker
docker run -d -p 6379:6379 redis:latest

# 测试连接
redis-cli ping
```

2. **检查Redis配置**
```env
# .env文件
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 问题4: 文件上传失败

**症状：** 上传文件时报错

**可能原因和解决方案：**

1. **文件大小超限**
```bash
# 检查文件大小
ls -lh your_file.pdf

# 单个文件不能超过10MB
```

2. **文件格式不支持**
```bash
# 支持的格式：TXT, PDF, DOCX
# 检查文件扩展名
```

3. **文件损坏**
```bash
# 尝试用其他工具打开文件
# 或重新导出文件
```


#### 问题5: Docker部署问题

**症状：** Docker容器无法启动

**解决方案：**

1. **检查Docker服务**
```bash
# 确保Docker正在运行
docker info

# 启动Docker服务
# Windows/Mac: 启动Docker Desktop
# Linux: sudo systemctl start docker
```

2. **查看容器日志**
```bash
# 查看失败原因
docker-compose logs api
docker-compose logs ui
```

3. **重新构建镜像**
```bash
# 清理旧镜像
docker-compose down -v
docker system prune -a

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

#### 问题6: 数据库错误

**症状：** 数据保存或查询失败

**解决方案：**

1. **重新初始化数据库**
```bash
# 备份现有数据
cp data/jd_analyzer.db data/jd_analyzer.db.backup

# 重新初始化
python scripts/init_db.py
```

2. **检查数据库文件权限**
```bash
# Linux/Mac
chmod 644 data/jd_analyzer.db
chown $USER:$USER data/jd_analyzer.db
```

3. **验证数据库结构**
```bash
python scripts/verify_db_schema.py
```

### 调试技巧

#### 启用调试模式

```env
# .env文件
LOG_LEVEL=DEBUG
API_RELOAD=true
```


#### 查看详细错误信息

```bash
# 查看完整日志
tail -f logs/app.log

# 查看Python错误堆栈
python -u src/ui/app.py 2>&1 | tee debug.log
```

#### 测试各组件

```bash
# 测试数据模型
python test_models.py

# 测试API
python test_api_simple.py

# 测试UI
python test_ui.py

# 测试文件解析
python test_file_parser.py

# 测试LLM连接
python test_deepseek_client.py
```

---

## 安全建议

### 1. API密钥安全

**最佳实践：**

- ✅ 使用环境变量存储API密钥
- ✅ 不要将.env文件提交到Git
- ✅ 定期轮换API密钥
- ✅ 为不同环境使用不同的密钥
- ❌ 不要在代码中硬编码密钥
- ❌ 不要在日志中打印密钥

**密钥管理：**

```bash
# 使用密钥管理服务（生产环境）
# AWS Secrets Manager
# Azure Key Vault
# HashiCorp Vault

# 或使用加密的环境变量文件
ansible-vault encrypt .env.production
```

### 2. 网络安全

**防火墙配置：**

```bash
# 只开放必要端口
# 8000 - API (仅内网)
# 8501 - UI (通过Nginx代理)
# 443 - HTTPS

# UFW示例
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp
sudo ufw deny 8501/tcp
```


**HTTPS配置：**

```bash
# 使用Let's Encrypt获取免费SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 访问控制

**API认证（生产环境建议）：**

```python
# 添加API密钥认证
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("API_SECRET_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

**IP白名单：**

```nginx
# Nginx配置
location /api {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://localhost:8000;
}
```

### 4. 数据安全

**数据加密：**

```bash
# 加密敏感数据
# 使用数据库加密
# 加密备份文件

# 示例：加密备份
tar -czf - data/ | openssl enc -aes-256-cbc -e > backup.tar.gz.enc
```

**数据脱敏：**

```python
# 在日志中脱敏敏感信息
def mask_sensitive_data(text):
    # 隐藏邮箱
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                  '***@***.***', text)
    # 隐藏手机号
    text = re.sub(r'\b1[3-9]\d{9}\b', '***********', text)
    return text
```

### 5. 依赖安全

**定期更新依赖：**

```bash
# 检查安全漏洞
pip install safety
safety check

# 更新依赖
pip list --outdated
pip install --upgrade package_name
```


### 6. 容器安全

**Docker安全最佳实践：**

```dockerfile
# 使用非root用户
FROM python:3.11-slim
RUN useradd -m -u 1000 appuser
USER appuser

# 最小化镜像
FROM python:3.11-alpine

# 扫描漏洞
docker scan jd-analyzer:latest
```

### 7. 日志安全

**安全日志配置：**

```python
# 不记录敏感信息
import logging

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # 过滤API密钥
        record.msg = re.sub(r'sk-[a-zA-Z0-9]{48}', 'sk-***', str(record.msg))
        return True

logger.addFilter(SensitiveDataFilter())
```

### 8. 安全检查清单

**部署前检查：**

- [ ] API密钥已配置且安全存储
- [ ] 生产环境使用HTTPS
- [ ] 防火墙规则已配置
- [ ] 数据库访问受限
- [ ] 日志不包含敏感信息
- [ ] 依赖包已更新到安全版本
- [ ] 备份策略已实施
- [ ] 监控和告警已配置
- [ ] 访问控制已启用
- [ ] 容器使用非root用户

---

## 性能优化

### 1. LLM调用优化

**使用缓存：**

```env
# 启用LLM缓存
ENABLE_CACHE=true
CACHE_TTL=3600
```

**选择合适的模型：**

```env
# 快速响应（成本低）
LLM_MODEL=gpt-3.5-turbo

# 高质量（成本高）
LLM_MODEL=gpt-4

# 性价比（国内）
LLM_MODEL=deepseek-chat
```


### 2. 数据库优化

**使用连接池：**

```python
# 配置数据库连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

**添加索引：**

```sql
-- 为常用查询添加索引
CREATE INDEX idx_jd_created_at ON jd_records(created_at);
CREATE INDEX idx_jd_category ON jd_records(category_id);
CREATE INDEX idx_questionnaire_jd ON questionnaires(jd_id);
```

### 3. API性能优化

**启用压缩：**

```python
# FastAPI启用Gzip压缩
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**使用异步处理：**

```python
# 批量处理使用后台任务
from fastapi import BackgroundTasks

@app.post("/batch/upload")
async def batch_upload(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_batch)
    return {"status": "processing"}
```

### 4. 前端优化

**Streamlit性能配置：**

```toml
# .streamlit/config.toml
[server]
maxUploadSize = 100
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```


### 2. 数据库优化

**索引优化：**

```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_jd_created_at ON job_descriptions(created_at);
CREATE INDEX idx_jd_category ON job_descriptions(category_level3_id);
CREATE INDEX idx_questionnaire_jd ON questionnaires(jd_id);
```

**连接池配置：**

```python
# 配置数据库连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
```

### 3. Redis优化

**内存优化：**

```bash
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

**持久化配置：**

```bash
# redis.conf
save 900 1
save 300 10
save 60 10000
```

### 4. API性能优化

**启用压缩：**

```python
# FastAPI配置
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**并发处理：**

```bash
# 使用多个worker
uvicorn src.api.main:app --workers 4 --host 0.0.0.0 --port 8000
```


### 5. 文件处理优化

**异步处理：**

```python
# 批量上传使用异步处理
import asyncio

async def process_files_async(files):
    tasks = [process_file(f) for f in files]
    return await asyncio.gather(*tasks)
```

**流式处理大文件：**

```python
# 分块读取大文件
def read_large_file(file_path, chunk_size=8192):
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            yield chunk
```

### 6. 前端优化

**Streamlit配置：**

```toml
# .streamlit/config.toml
[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
base = "light"
```

---

## 监控和告警

### 1. 应用监控

**Prometheus + Grafana：**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'jd-analyzer'
    static_configs:
      - targets: ['localhost:8000']
```

**自定义指标：**

```python
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'API request duration')
```


---

## 成本估算

### LLM API成本

**OpenAI定价（参考）：**

| 模型 | 输入价格 | 输出价格 | 单次分析成本 |
|------|---------|---------|-------------|
| GPT-4 | $0.03/1K tokens | $0.06/1K tokens | ~$0.05 |
| GPT-3.5-turbo | $0.0015/1K tokens | $0.002/1K tokens | ~$0.01 |

**DeepSeek定价（参考）：**

| 模型 | 输入价格 | 输出价格 | 单次分析成本 |
|------|---------|---------|-------------|
| deepseek-chat | ¥0.001/1K tokens | ¥0.002/1K tokens | ~¥0.01 (~$0.0014) |
| deepseek-reasoner | ¥0.014/1K tokens | ¥0.028/1K tokens | ~¥0.10 (~$0.014) |

**月度成本估算：**

```
假设每天分析100个JD：
- 使用GPT-4: 100 × $0.05 × 30 = $150/月
- 使用GPT-3.5: 100 × $0.01 × 30 = $30/月
- 使用DeepSeek: 100 × $0.0014 × 30 = $4.2/月
```

### 基础设施成本

**云服务器（参考）：**

| 配置 | 阿里云 | AWS | 适用场景 |
|------|--------|-----|---------|
| 2核4GB | ¥100/月 | $20/月 | 小团队（<50人） |
| 4核8GB | ¥200/月 | $40/月 | 中型团队（50-200人） |
| 8核16GB | ¥400/月 | $80/月 | 大型团队（>200人） |

**总成本估算（中型团队）：**

```
- 服务器: ¥200/月
- LLM API (DeepSeek): ¥130/月 (每天300次分析)
- 域名+SSL: ¥10/月
- 备份存储: ¥20/月
---
总计: ¥360/月 (~$50/月)
```

---

## 扩展性建议

### 水平扩展

**API服务扩展：**

```yaml
# docker-compose.yml
services:
  api:
    image: jd-analyzer-api
    deploy:
      replicas: 3
    ports:
      - "8000-8002:8000"
```


### 2. 日志聚合

**ELK Stack（Elasticsearch + Logstash + Kibana）：**

```yaml
# logstash.conf
input {
  file {
    path => "/path/to/logs/*.log"
    type => "jd-analyzer"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "jd-analyzer-%{+YYYY.MM.dd}"
  }
}
```

### 3. 告警配置

**邮件告警：**

```python
# 配置告警
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'alert@example.com'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)
```

**监控脚本：**

```bash
#!/bin/bash
# monitor.sh

# 检查API健康
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "API服务异常" | mail -s "告警：API服务down" admin@example.com
fi

# 检查磁盘空间
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "磁盘使用率: ${DISK_USAGE}%" | mail -s "告警：磁盘空间不足" admin@example.com
fi
```

---

## 扩展和集成

### 1. 水平扩展

**负载均衡配置：**

```nginx
# nginx.conf
upstream api_backend {
    least_conn;
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}

server {
    location /api {
        proxy_pass http://api_backend;
    }
}
```


**负载均衡配置：**

```nginx
upstream api_backend {
    least_conn;
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    location /api {
        proxy_pass http://api_backend;
    }
}
```

### 垂直扩展

**增加资源配置：**

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

### 数据库扩展

**使用PostgreSQL主从复制：**

```yaml
# docker-compose.yml
services:
  postgres-master:
    image: postgres:15
    environment:
      POSTGRES_DB: jd_analyzer
      
  postgres-slave:
    image: postgres:15
    environment:
      POSTGRES_MASTER_HOST: postgres-master
```

---

## 监控和告警

### 应用监控

**使用Prometheus + Grafana：**

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

**Prometheus配置：**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'jd-analyzer-api'
    static_configs:
      - targets: ['api:8000']
```


### 2. 数据库扩展

**PostgreSQL主从复制：**

```bash
# 主库配置
# postgresql.conf
wal_level = replica
max_wal_senders = 3

# 从库配置
# recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=master_ip port=5432 user=replicator'
```

### 3. Redis集群

**Redis Cluster配置：**

```bash
# 创建Redis集群
redis-cli --cluster create \
  192.168.1.10:6379 \
  192.168.1.11:6379 \
  192.168.1.12:6379 \
  --cluster-replicas 1
```

### 4. 第三方集成

**Webhook集成：**

```python
# 分析完成后发送webhook
import requests

def send_webhook(event, data):
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json={
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
```

**Slack通知：**

```python
from slack_sdk import WebClient

def send_slack_notification(message):
    client = WebClient(token=os.getenv("SLACK_TOKEN"))
    client.chat_postMessage(
        channel="#jd-analyzer",
        text=message
    )
```

---

## 附录

### A. 环境变量完整列表

```env
# ==================== LLM配置 ====================
OPENAI_API_KEY=                 # LLM API密钥（必需）
OPENAI_BASE_URL=                # API基础URL（必需）
LLM_MODEL=                      # 模型名称（必需）
LLM_TEMPERATURE=0.7             # 温度参数（可选）
LLM_MAX_TOKENS=4000             # 最大token数（可选）
LLM_TIMEOUT=60                  # 请求超时（秒）（可选）
```


### 日志聚合

**使用ELK Stack：**

```yaml
# docker-compose.yml
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    
  logstash:
    image: logstash:8.11.0
    
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

### 告警配置

**邮件告警示例：**

```python
# 监控脚本
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'alert@example.com'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)

# 检查API健康
response = requests.get('http://localhost:8000/health')
if response.status_code != 200:
    send_alert('API Down', 'API服务无响应')
```

---

## 附录

### A. 环境变量完整列表

```env
# ==================== LLM配置 ====================
OPENAI_API_KEY=                 # LLM API密钥（必需）
OPENAI_BASE_URL=                # LLM API地址（必需）
LLM_MODEL=                      # 使用的模型名称（必需）
LLM_TEMPERATURE=0.7             # 温度参数（可选）
LLM_MAX_TOKENS=4000             # 最大token数（可选）
LLM_TIMEOUT=60                  # 请求超时时间（可选）

# ==================== Redis配置 ====================
REDIS_HOST=localhost            # Redis主机地址
REDIS_PORT=6379                 # Redis端口
REDIS_PASSWORD=                 # Redis密码（可选）
REDIS_DB=0                      # Redis数据库编号

# ==================== 数据库配置 ====================
DATABASE_URL=                   # 数据库连接URL（必需）

# ==================== API配置 ====================
API_HOST=0.0.0.0               # API监听地址
API_PORT=8000                   # API端口
API_RELOAD=false                # 是否自动重载
CORS_ORIGINS=["*"]              # CORS允许的源

# ==================== 日志配置 ====================
LOG_LEVEL=INFO                  # 日志级别
LOG_FILE=logs/app.log           # 日志文件路径
LOG_MAX_SIZE=10485760           # 日志文件最大大小
LOG_BACKUP_COUNT=5              # 日志备份数量

# ==================== 文件上传配置 ====================
MAX_FILE_SIZE=10485760          # 单个文件最大大小（10MB）
MAX_BATCH_SIZE=20               # 批量上传最大文件数
MAX_TOTAL_SIZE=104857600        # 批量上传总大小限制（100MB）
UPLOAD_DIR=./uploads            # 上传文件存储目录

# ==================== 缓存配置 ====================
ENABLE_CACHE=true               # 是否启用缓存
CACHE_TTL=3600                  # 缓存过期时间（秒）
CACHE_MAX_SIZE=1000             # 缓存最大条目数
```


```env
# ==================== Redis配置 ====================
REDIS_HOST=localhost            # Redis主机（可选）
REDIS_PORT=6379                 # Redis端口（可选）
REDIS_PASSWORD=                 # Redis密码（可选）
REDIS_DB=0                      # Redis数据库编号（可选）

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite:///./data/jd_analyzer.db  # 数据库URL（必需）

# ==================== API配置 ====================
API_HOST=0.0.0.0                # API监听地址（可选）
API_PORT=8000                   # API端口（可选）
API_RELOAD=false                # 自动重载（可选）
CORS_ORIGINS=["*"]              # CORS允许的源（可选）

# ==================== 日志配置 ====================
LOG_LEVEL=INFO                  # 日志级别（可选）
LOG_FILE=logs/app.log           # 日志文件路径（可选）
LOG_MAX_SIZE=10485760           # 日志文件最大大小（可选）
LOG_BACKUP_COUNT=5              # 日志备份数量（可选）

# ==================== 文件上传配置 ====================
MAX_FILE_SIZE=10485760          # 单个文件最大大小（可选）
MAX_BATCH_SIZE=20               # 批量上传最大文件数（可选）
MAX_TOTAL_SIZE=104857600        # 批量上传总大小限制（可选）
UPLOAD_DIR=./uploads            # 上传目录（可选）

# ==================== 缓存配置 ====================
ENABLE_CACHE=true               # 启用缓存（可选）
CACHE_TTL=3600                  # 缓存过期时间（秒）（可选）

# ==================== 安全配置 ====================
API_SECRET_KEY=                 # API密钥（生产环境建议）
ALLOWED_IPS=                    # IP白名单（可选）

# ==================== 监控配置 ====================
ENABLE_METRICS=false            # 启用Prometheus指标（可选）
METRICS_PORT=9090               # 指标端口（可选）

# ==================== Webhook配置 ====================
WEBHOOK_URL=                    # Webhook URL（可选）
SLACK_TOKEN=                    # Slack Token（可选）
```


### B. 端口使用说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 8000 | FastAPI | API服务 |
| 8501 | Streamlit | Web UI |
| 6379 | Redis | 消息队列和缓存 |
| 5432 | PostgreSQL | 数据库（可选） |
| 9090 | Prometheus | 监控（可选） |
| 3000 | Grafana | 可视化（可选） |
| 5601 | Kibana | 日志查看（可选） |

### C. 文件目录结构

```
jd-analyzer/
├── .env                        # 环境变量配置
├── .env.example                # 环境变量模板
├── .gitignore                  # Git忽略文件
├── requirements.txt            # Python依赖
├── Dockerfile                  # Docker镜像定义
├── docker-compose.yml          # Docker编排配置
├── README.md                   # 项目说明
├── DEPLOYMENT.md               # 部署文档（本文档）
├── QUICKSTART.md               # 快速开始
├── USAGE.md                    # 使用说明
├── DOCKER_README.md            # Docker部署指南
│
├── src/                        # 源代码目录
│   ├── core/                   # 核心组件
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── llm_client.py       # LLM客户端
│   │   └── llm_cache.py        # LLM缓存
│   ├── models/                 # 数据模型
│   │   ├── schemas.py          # Pydantic模型
│   │   └── database.py         # SQLAlchemy模型
│   ├── repositories/           # 数据访问层
│   ├── services/               # 业务逻辑层
│   ├── agents/                 # Agent实现
│   ├── workflows/              # 工作流
│   ├── mcp/                    # MCP协议
│   ├── api/                    # FastAPI应用
│   │   ├── main.py             # API入口
│   │   └── routers/            # API路由
│   ├── ui/                     # Streamlit应用
│   │   ├── app.py              # UI入口
│   │   └── pages/              # UI页面
│   └── utils/                  # 工具函数
│
├── scripts/                    # 脚本目录
│   ├── init_db.py              # 初始化数据库
│   ├── start_agents.py         # 启动Agent服务
│   ├── start_all.sh            # 启动所有服务（Linux/Mac）
│   ├── start_all.bat           # 启动所有服务（Windows）
│   ├── stop_all.sh             # 停止所有服务（Linux/Mac）
│   ├── stop_all.bat            # 停止所有服务（Windows）
│   └── health_check.py         # 健康检查脚本
│
├── data/                       # 数据存储目录（自动创建）
│   └── jd_analyzer.db          # SQLite数据库
├── uploads/                    # 上传文件目录（自动创建）
├── logs/                       # 日志目录（自动创建）
├── examples/                   # 示例代码
├── tests/                      # 测试文件
└── docs/                       # 文档目录
```


### B. 端口使用说明

| 端口 | 服务 | 说明 | 必需 |
|------|------|------|------|
| 8501 | Streamlit UI | Web界面 | 是 |
| 8000 | FastAPI | API服务 | 否（仅UI模式不需要） |
| 6379 | Redis | 消息队列 | 否（仅Agent模式需要） |
| 5432 | PostgreSQL | 数据库（可选） | 否 |
| 9090 | Prometheus | 监控指标（可选） | 否 |

### C. 目录结构说明

```
jd-analyzer/
├── .kiro/                      # Kiro配置目录
│   └── specs/                  # 规格文档
├── data/                       # 数据存储目录（自动创建）
│   └── jd_analyzer.db          # SQLite数据库
├── logs/                       # 日志目录（自动创建）
│   ├── app.log                 # 应用日志
│   ├── api.log                 # API日志
│   └── agents.log              # Agent日志
├── uploads/                    # 上传文件目录（自动创建）
├── src/                        # 源代码目录
│   ├── agents/                 # Agent实现
│   ├── api/                    # FastAPI后端
│   ├── core/                   # 核心组件
│   ├── mcp/                    # MCP通讯协议
│   ├── models/                 # 数据模型
│   ├── repositories/           # 数据访问层
│   ├── services/               # 业务服务
│   ├── ui/                     # Streamlit前端
│   ├── utils/                  # 工具函数
│   └── workflows/              # 工作流
├── scripts/                    # 脚本目录
│   ├── init_db.py              # 数据库初始化
│   ├── start_agents.py         # 启动Agent
│   ├── health_check.py         # 健康检查
│   ├── start_all.sh            # 启动所有服务（Linux/Mac）
│   ├── start_all.bat           # 启动所有服务（Windows）
│   ├── stop_all.sh             # 停止所有服务（Linux/Mac）
│   └── stop_all.bat            # 停止所有服务（Windows）
├── docs/                       # 文档目录
├── examples/                   # 示例代码
├── tests/                      # 测试文件
├── .env                        # 环境变量（需创建）
├── .env.example                # 环境变量模板
├── requirements.txt            # Python依赖
├── Dockerfile                  # Docker镜像定义
├── docker-compose.yml          # Docker Compose配置
├── run.py                      # 启动脚本
├── start.bat                   # Windows快速启动
├── start.sh                    # Linux/Mac快速启动
└── README.md                   # 项目说明
```


### D. 常用命令速查

**本地开发：**

```bash
# 快速启动
python run.py

# 启动UI
streamlit run src/ui/app.py

# 启动API
uvicorn src.api.main:app --reload

# 运行测试
python test_mvp.py
python test_api_simple.py
```

**Docker部署：**

```bash
# 构建和启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

**数据库管理：**

```bash
# 初始化数据库
python scripts/init_db.py

# 验证数据库结构
python scripts/verify_db_schema.py

# 备份数据库
cp data/jd_analyzer.db data/backup_$(date +%Y%m%d).db
```

**服务管理：**

```bash
# 启动所有服务
./scripts/start_all.sh  # Linux/Mac
scripts\start_all.bat   # Windows

# 停止所有服务
./scripts/stop_all.sh   # Linux/Mac
scripts\stop_all.bat    # Windows

# 健康检查
python scripts/health_check.py
```

### E. 相关文档链接

**项目文档：**
- [README.md](README.md) - 项目概述
- [GET_STARTED.md](GET_STARTED.md) - 3步快速开始
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [USAGE.md](USAGE.md) - 详细使用说明
- [DOCKER_README.md](DOCKER_README.md) - Docker部署指南

**API文档：**
- [API_QUICKSTART.md](API_QUICKSTART.md) - API快速开始
- [src/api/README.md](src/api/README.md) - API完整文档
- http://localhost:8000/docs - Swagger交互式文档

**UI文档：**
- [UI_QUICKSTART.md](UI_QUICKSTART.md) - UI快速开始
- [src/ui/README.md](src/ui/README.md) - UI完整文档

**技术文档：**
- [.kiro/specs/jd-analyzer/requirements.md](.kiro/specs/jd-analyzer/requirements.md) - 需求文档
- [.kiro/specs/jd-analyzer/design.md](.kiro/specs/jd-analyzer/design.md) - 设计文档
- [docs/database_schema.md](docs/database_schema.md) - 数据库设计


### D. 常用命令速查

#### 本地开发

```bash
# 快速启动
python run.py

# 仅启动UI
streamlit run src/ui/app.py

# 启动API
uvicorn src.api.main:app --reload

# 启动所有服务
./scripts/start_all.sh  # Linux/Mac
scripts\start_all.bat   # Windows

# 停止所有服务
./scripts/stop_all.sh   # Linux/Mac
scripts\stop_all.bat    # Windows
```

#### Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker-compose exec api bash
```

#### 数据库管理

```bash
# 初始化数据库
python scripts/init_db.py

# 验证数据库结构
python scripts/verify_db_schema.py

# 备份数据库
cp data/jd_analyzer.db data/backup_$(date +%Y%m%d).db

# 查看数据库
sqlite3 data/jd_analyzer.db
```

#### 测试

```bash
# 运行所有测试
python -m pytest

# 测试API
python test_api_simple.py

# 测试UI
python test_ui.py

# 测试文件解析
python test_file_parser.py

# 健康检查
python scripts/health_check.py
```


### E. 相关文档索引

**快速开始：**
- [GET_STARTED.md](GET_STARTED.md) - 3步快速启动
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速指南
- [WELCOME.md](WELCOME.md) - 欢迎指南

**使用指南：**
- [USAGE.md](USAGE.md) - 完整使用说明
- [DEMO.md](DEMO.md) - 演示指南
- [UI_QUICKSTART.md](UI_QUICKSTART.md) - UI快速指南
- [API_QUICKSTART.md](API_QUICKSTART.md) - API快速指南

**部署文档：**
- [DEPLOYMENT.md](DEPLOYMENT.md) - 本文档
- [DOCKER_README.md](DOCKER_README.md) - Docker部署详解

**技术文档：**
- [README.md](README.md) - 项目概述
- [src/api/README.md](src/api/README.md) - API文档
- [src/ui/README.md](src/ui/README.md) - UI文档
- [src/agents/README.md](src/agents/README.md) - Agent文档
- [docs/database_schema.md](docs/database_schema.md) - 数据库设计

**规格文档：**
- [.kiro/specs/jd-analyzer/requirements.md](.kiro/specs/jd-analyzer/requirements.md) - 需求文档
- [.kiro/specs/jd-analyzer/design.md](.kiro/specs/jd-analyzer/design.md) - 设计文档
- [.kiro/specs/jd-analyzer/tasks.md](.kiro/specs/jd-analyzer/tasks.md) - 任务列表

**项目状态：**
- [STATUS.md](STATUS.md) - 项目状态
- [MVP_SUMMARY.md](MVP_SUMMARY.md) - MVP总结
- [INDEX.md](INDEX.md) - 文档索引

### F. 支持和帮助

**获取帮助：**
1. 查看相关文档（见上方索引）
2. 查看[故障排除](#故障排除)章节
3. 运行健康检查：`python scripts/health_check.py`
4. 查看日志文件：`logs/app.log`
5. 联系开发团队

**报告问题：**
- 提供详细的错误信息
- 包含日志文件
- 说明复现步骤
- 提供环境信息（OS、Python版本等）


**社区资源：**
- 项目仓库：GitHub
- 问题追踪：GitHub Issues
- 讨论区：GitHub Discussions

### G. 版本历史

**v0.1.0 (MVP) - 2024-01**
- ✅ JD解析功能
- ✅ 质量评估（标准/美世法/因素法）
- ✅ 优化建议生成
- ✅ 批量文件上传（TXT/PDF/DOCX）
- ✅ 职位分类管理（3层级）
- ✅ 问卷生成和管理
- ✅ 候选人匹配评估
- ✅ Streamlit UI界面
- ✅ FastAPI后端
- ✅ Docker部署支持

**即将推出：**
- 🔜 报告导出（PDF/Excel）
- 🔜 数据可视化增强
- 🔜 多语言支持
- 🔜 用户权限管理
- 🔜 高级分析功能

### H. 许可证

MIT License

---

## 总结

本文档涵盖了岗位JD分析器的完整部署流程，包括：

✅ **安装说明** - 多种安装方式（快速安装、手动安装、Docker）  
✅ **配置说明** - 详细的环境变量配置和最佳实践  
✅ **部署方式** - 本地开发、完整服务、Docker、生产环境  
✅ **使用指南** - 基本使用流程和API使用示例  
✅ **运维管理** - 健康检查、日志管理、备份恢复、性能监控  
✅ **故障排除** - 常见问题和解决方案  
✅ **安全建议** - API密钥、网络、访问控制、数据安全  
✅ **性能优化** - LLM、数据库、Redis、API优化  
✅ **监控告警** - 应用监控、日志聚合、告警配置  
✅ **扩展集成** - 水平扩展、数据库扩展、第三方集成

**快速开始：**
1. 运行 `start.bat`（Windows）或 `./start.sh`（Linux/Mac）
2. 配置 `.env` 文件中的API密钥
3. 访问 http://localhost:8501
4. 开始使用！

**需要帮助？** 查看 [GET_STARTED.md](GET_STARTED.md) 或 [USAGE.md](USAGE.md)

---

**祝部署顺利！** 🚀

