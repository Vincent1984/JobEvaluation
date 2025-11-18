# 岗位JD分析器 - Docker镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/uploads

# 暴露端口
# 8000: FastAPI
# 8501: Streamlit
EXPOSE 8000 8501

# 默认命令（可被docker-compose覆盖）
CMD ["python", "run.py"]
