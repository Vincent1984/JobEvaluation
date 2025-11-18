# Docker 部署指南

## 概述

本文档说明如何使用Docker和Docker Compose部署岗位JD分析器系统。

## 系统架构

系统包含以下服务：

- **Redis**: 消息队列和缓存服务（端口6379）
- **API**: FastAPI后端服务（端口8000）
- **UI**: Streamlit前端服务（端口8501）
- **Agents**: 后台Agent服务（可选）

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存
- 至少5GB可用磁盘空间

## 快速开始

### 1. 环境配置

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑`.env`文件，配置必要的环境变量：

```env
# LLM配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379

# 数据库配置
DATABASE_URL=sqlite:///./data/jd_analyzer.db

# API配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 2. 构建和启动服务

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问服务

- **Streamlit UI**: http://localhost:8501
- **FastAPI文档**: http://localhost:8000/docs
- **API健康检查**: http://localhost:8000/health

### 4. 初始化数据库

首次启动时，需要初始化数据库：

```bash
docker-compose exec api python scripts/init_db.py
```

## 服务管理

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d api
docker-compose up -d ui
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart api
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f ui
```

## 数据持久化

系统使用Docker卷来持久化数据：

- `redis_data`: Redis数据
- `./data`: SQLite数据库和应用数据
- `./uploads`: 上传的文件

## 健康检查

所有服务都配置了健康检查：

```bash
# 检查服务健康状态
docker-compose ps

# 手动检查API健康
curl http://localhost:8000/health

# 手动检查UI健康
curl http://localhost:8501/_stcore/health
```

## 开发模式

在开发模式下，代码更改会自动重新加载：

```bash
# 使用开发配置启动
docker-compose up -d

# 代码挂载为卷，修改会自动生效
```

## 生产部署

### 1. 优化配置

编辑`docker-compose.yml`，移除开发相关配置：

```yaml
# 移除 --reload 标志
command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 添加资源限制
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### 2. 使用环境变量文件

```bash
# 使用生产环境变量
docker-compose --env-file .env.production up -d
```

### 3. 配置反向代理

使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs api

# 检查端口占用
netstat -an | grep 8000
netstat -an | grep 8501
netstat -an | grep 6379
```

### Redis连接失败

```bash
# 检查Redis服务状态
docker-compose ps redis

# 测试Redis连接
docker-compose exec redis redis-cli ping
```

### 数据库错误

```bash
# 重新初始化数据库
docker-compose exec api python scripts/init_db.py

# 检查数据库文件权限
ls -la data/
```

### 内存不足

```bash
# 查看容器资源使用
docker stats

# 增加Docker内存限制
# 在Docker Desktop设置中调整
```

## 备份和恢复

### 备份数据

```bash
# 备份数据库
docker-compose exec api tar -czf /tmp/backup.tar.gz /app/data
docker cp jd-analyzer-api:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# 备份Redis数据
docker-compose exec redis redis-cli SAVE
docker cp jd-analyzer-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

### 恢复数据

```bash
# 停止服务
docker-compose down

# 恢复数据库
tar -xzf backup-20240101.tar.gz -C ./data

# 恢复Redis数据
cp redis-backup-20240101.rdb ./redis_data/dump.rdb

# 重启服务
docker-compose up -d
```

## 更新和升级

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d

# 清理旧镜像
docker image prune -f
```

## 监控和日志

### 日志管理

```bash
# 限制日志大小（在docker-compose.yml中配置）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 性能监控

```bash
# 实时监控资源使用
docker stats

# 查看容器详情
docker-compose exec api ps aux
```

## 安全建议

1. **不要在生产环境中使用默认密钥**
2. **限制容器网络访问**
3. **定期更新基础镜像**
4. **使用非root用户运行容器**
5. **启用Docker内容信任**
6. **定期备份数据**

## 常见问题

### Q: 如何更改服务端口？

A: 编辑`docker-compose.yml`中的端口映射：

```yaml
ports:
  - "8080:8000"  # 将API端口改为8080
```

### Q: 如何扩展Agent服务？

A: 使用Docker Compose的scale功能：

```bash
docker-compose up -d --scale agents=3
```

### Q: 如何使用外部Redis？

A: 修改环境变量，指向外部Redis：

```env
REDIS_HOST=external-redis.example.com
REDIS_PORT=6379
```

然后移除docker-compose.yml中的redis服务。

## 支持

如有问题，请查看：
- 项目文档: README.md
- API文档: http://localhost:8000/docs
- 问题追踪: GitHub Issues
