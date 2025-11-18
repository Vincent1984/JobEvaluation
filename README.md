# 岗位JD分析器 (Job Description Analyzer)

> 🎉 **首次使用？** 查看 [WELCOME.md](WELCOME.md) 获取欢迎指南！  
> 📚 **找不到文档？** 查看 [INDEX.md](INDEX.md) 文档索引！

基于Agentic AI架构的智能岗位JD分析系统，支持自动解析、质量评估、优化建议和候选人匹配。

## 功能特性

- 🔍 **JD解析**: 自动提取职位标题、职责、技能要求等结构化信息
- 📊 **质量评估**: 多维度评估JD质量，支持美世法、因素比较法等专业模型
- 💡 **优化建议**: AI生成针对性的改进建议
- 🎯 **候选人匹配**: 智能问卷生成和匹配度评估
- 📁 **职位分类**: 支持3层级自定义分类体系

## 技术架构

- **Agent框架**: 多Agent协作架构
- **通讯协议**: MCP (Model Context Protocol)
- **后端**: FastAPI + Python 3.11+
- **前端**: Streamlit
- **数据库**: SQLite
- **消息队列**: Redis
- **LLM**: OpenAI/DeepSeek

## 快速开始

> 💡 **想立即开始？** 查看 [GET_STARTED.md](GET_STARTED.md) 获取3步快速启动指南！

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，填入你的API密钥
```

### 3. 启动服务

```bash
# 启动Redis (需要先安装Redis)
redis-server

# 启动FastAPI后端
python -m uvicorn src.api.main:app --reload --port 8000

# 启动Streamlit前端
streamlit run src/ui/app.py
```

### 4. 访问应用

- Streamlit UI: http://localhost:8501
- FastAPI文档: http://localhost:8000/docs

## 项目结构

```
jd-analyzer/
├── src/
│   ├── core/            # 核心组件
│   │   ├── config.py    # 配置管理
│   │   └── llm_client.py # LLM客户端
│   ├── models/          # 数据模型
│   │   └── schemas.py   # Pydantic模型定义
│   ├── services/        # 业务服务
│   │   └── jd_service.py # JD分析服务
│   └── ui/              # Streamlit界面
│       └── app.py       # 主应用
├── data/                # 数据存储（自动创建）
├── .env.example         # 环境变量模板
├── .gitignore          # Git忽略文件
├── requirements.txt     # Python依赖
├── run.py              # 启动脚本
├── start.bat           # Windows快速启动
├── start.sh            # Linux/Mac快速启动
├── test_mvp.py         # MVP测试脚本
├── QUICKSTART.md       # 快速开始指南
└── README.md           # 项目说明
```

## 使用指南

### JD分析

1. 在Streamlit界面输入或上传JD文本
2. 选择评估模型（标准/美世法/因素比较法）
3. 点击"分析"按钮
4. 查看解析结果、质量评分和优化建议

### 候选人匹配

1. 选择已分析的JD
2. 生成评估问卷
3. 分享问卷链接给候选人
4. 查看匹配度报告

## 开发指南

### 添加新Agent

```python
from src.core.mcp import MCPAgent

class CustomAgent(MCPAgent):
    def __init__(self, mcp_server, llm_client):
        super().__init__(
            agent_id="custom",
            agent_type="custom",
            mcp_server=mcp_server,
            llm_client=llm_client
        )
        self.register_handler("custom_action", self.handle_custom_action)
    
    async def handle_custom_action(self, message):
        # 实现自定义逻辑
        pass
```

## License

MIT License
