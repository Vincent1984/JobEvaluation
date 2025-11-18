# Agents模块

本模块实现了JD分析器的所有专门化Agent，基于MCP（Model Context Protocol）进行通讯和协作。

## Agent架构

系统采用多Agent协作架构，每个Agent是一个自主的智能实体，通过MCP协议进行通讯。

### Agent列表

1. **BatchUploadAgent** - 批量上传处理Agent
2. **ParserAgent** - JD解析Agent
3. **EvaluatorAgent** - 质量评估Agent
4. **OptimizerAgent** - 优化建议Agent
5. **QuestionnaireAgent** - 问卷生成Agent
6. **MatcherAgent** - 匹配评估Agent
7. **DataManagerAgent** - 数据管理Agent
8. **CoordinatorAgent** - 协调Agent
9. **ReportAgent** - 报告生成Agent

## Agent详细说明

### 1. BatchUploadAgent

**职责：**
- 验证文件格式、大小、数量
- 批量文件处理循环
- 进度通知机制（via MCP）
- 与Parser Agent和Evaluator Agent的协调
- 批量处理上下文管理
- 结果汇总和错误处理

**支持的文件格式：**
- TXT（UTF-8, GBK, GB2312等编码）
- PDF
- DOCX
- DOC（可选）

**限制：**
- 单个文件最大10MB
- 批量上传最多20个文件
- 总大小最多100MB

**消息处理器：**
- `batch_upload`: 处理批量上传请求
- `parse_file`: 处理单个文件解析请求

### 2. ParserAgent

**职责：**
- 解析JD文本，提取结构化信息
- 应用自定义字段提取
- 职位自动分类（基于3层级分类体系）
- 获取样本JD并用于分类参考
- 构建分类Prompt（包含样本JD参考）
- 与DataManagerAgent通讯

**提取的字段：**
- job_title: 职位名称
- department: 部门
- location: 工作地点
- responsibilities: 职责列表
- required_skills: 必备技能列表
- preferred_skills: 优选技能列表
- qualifications: 任职资格列表
- custom_fields: 自定义字段

**消息处理器：**
- `parse_jd`: 处理JD解析请求
- `classify_job`: 处理职位分类请求

### 3. EvaluatorAgent

**职责：**
- 评估JD质量
- 应用专业评估模型（美世法、因素法）
- 识别质量问题

**支持的评估模型：**
1. **标准评估模型（standard）**
   - 完整性（40%）
   - 清晰度（30%）
   - 专业性（30%）

2. **美世国际职位评估法（mercer_ipe）**
   - 影响力（35%）
   - 沟通（25%）
   - 创新（20%）
   - 知识技能（20%）

3. **因素比较法（factor_comparison）**
   - 技能要求（30%）
   - 责任程度（30%）
   - 努力程度（20%）
   - 工作条件（20%）

**消息处理器：**
- `evaluate_quality`: 处理质量评估请求

### 4. OptimizerAgent

**职责：**
- 基于评估结果生成优化建议
- 提供JD改写示例

**生成的建议包括：**
- 具体的优化建议（按优先级排序）
- 每条建议的改写示例
- 缺失信息的补充建议

**消息处理器：**
- `generate_suggestions`: 处理优化建议生成请求

### 5. QuestionnaireAgent

**职责：**
- 基于JD生成评估问卷
- 适配不同评估模型
- 生成多种问题类型

**支持的问题类型：**
- single_choice: 单选题
- multiple_choice: 多选题
- scale: 量表题（1-5分）
- open_ended: 开放题

**消息处理器：**
- `generate_questionnaire`: 处理问卷生成请求

### 6. MatcherAgent

**职责：**
- 解析问卷回答
- 计算多维度匹配度
- 生成优势和差距分析

**评估维度：**
- 技能匹配
- 经验匹配
- 资质匹配

**消息处理器：**
- `evaluate_match`: 处理匹配评估请求

### 7. DataManagerAgent

**职责：**
- 数据库CRUD操作
- 统一数据访问接口
- 职位分类的CRUD操作（包含样本JD管理）
- 获取分类树
- 更新JD分类
- 样本JD数量验证（第三层级最多2个）

**消息处理器：**
- `save_jd`: 保存JD数据
- `get_jd`: 获取JD数据
- `save_evaluation`: 保存评估结果
- `get_evaluation`: 获取评估结果
- `save_questionnaire`: 保存问卷
- `get_questionnaire`: 获取问卷
- `save_match_result`: 保存匹配结果
- `get_match_result`: 获取匹配结果
- `get_all_categories`: 获取所有职位分类
- `save_category`: 保存职位分类
- `update_jd_category`: 更新JD的分类

### 8. CoordinatorAgent

**职责：**
- 任务分解和分配
- 工作流编排
- Agent间协作协调

**支持的工作流：**
1. **JD分析工作流（analyze_jd）**
   - 步骤1: Parser Agent解析JD
   - 步骤2: Evaluator Agent评估质量
   - 步骤3: Optimizer Agent生成优化建议

2. **问卷生成工作流（generate_questionnaire）**
   - 转发给Questionnaire Agent

3. **匹配评估工作流（evaluate_match）**
   - 转发给Matcher Agent

**消息处理器：**
- `analyze_jd`: 处理JD分析请求（完整工作流）
- `generate_questionnaire`: 处理问卷生成请求
- `evaluate_match`: 处理匹配评估请求

### 9. ReportAgent

**职责：**
- 汇总报告数据
- 生成PDF报告
- 生成可视化图表

**支持的报告类型：**
1. **JD分析报告**
   - 执行摘要
   - JD详情
   - 质量评估
   - 可视化图表

2. **匹配度报告**
   - 匹配度概览
   - 优势分析
   - 能力差距
   - 发展建议
   - 可视化图表

**消息处理器：**
- `generate_report`: 处理JD分析报告生成请求
- `generate_match_report`: 处理匹配报告生成请求

## 使用示例

### 启动所有Agent

```python
import asyncio
from src.mcp.server import create_mcp_server
from src.core.llm_client import DeepSeekR1Client
from src.agents import (
    create_batch_upload_agent,
    create_parser_agent,
    create_evaluator_agent,
    create_optimizer_agent,
    create_questionnaire_agent,
    create_matcher_agent,
    create_data_manager_agent,
    create_coordinator_agent,
    create_report_agent
)

async def start_all_agents():
    # 创建MCP服务器
    mcp_server = await create_mcp_server(
        redis_host="localhost",
        redis_port=6379,
        auto_start=True
    )
    
    # 创建LLM客户端
    llm_client = DeepSeekR1Client()
    
    # 创建并启动所有Agent
    agents = []
    
    # 数据管理Agent（不需要LLM）
    data_manager = await create_data_manager_agent(mcp_server)
    agents.append(data_manager)
    
    # 需要LLM的Agent
    parser = await create_parser_agent(mcp_server, llm_client)
    evaluator = await create_evaluator_agent(mcp_server, llm_client)
    optimizer = await create_optimizer_agent(mcp_server, llm_client)
    questionnaire = await create_questionnaire_agent(mcp_server, llm_client)
    matcher = await create_matcher_agent(mcp_server, llm_client)
    agents.extend([parser, evaluator, optimizer, questionnaire, matcher])
    
    # 批量上传Agent（不需要LLM）
    batch_uploader = await create_batch_upload_agent(mcp_server)
    agents.append(batch_uploader)
    
    # 协调Agent（不需要LLM）
    coordinator = await create_coordinator_agent(mcp_server)
    agents.append(coordinator)
    
    # 报告生成Agent（不需要LLM）
    reporter = await create_report_agent(mcp_server)
    agents.append(reporter)
    
    print(f"所有Agent已启动: {len(agents)}个")
    
    return mcp_server, agents

# 运行
if __name__ == "__main__":
    asyncio.run(start_all_agents())
```

### 通过Coordinator执行JD分析

```python
async def analyze_jd_example():
    # 假设已经启动了所有Agent
    
    # 通过Coordinator Agent发送分析请求
    from src.mcp.message import create_request_message
    
    message = create_request_message(
        sender="api",
        receiver="coordinator",
        action="analyze_jd",
        payload={
            "jd_text": "招聘高级Python工程师...",
            "evaluation_model": "standard"
        }
    )
    
    # 发送消息并等待响应
    await mcp_server.send_message(message)
```

## Agent通讯流程

### JD分析完整流程

```
API/UI
  ↓ (analyze_jd)
CoordinatorAgent
  ↓ (parse_jd)
ParserAgent
  ↓ (save_jd)
DataManagerAgent
  ↓ (返回jd_id)
ParserAgent
  ↓ (返回解析结果)
CoordinatorAgent
  ↓ (evaluate_quality)
EvaluatorAgent
  ↓ (get_jd)
DataManagerAgent
  ↓ (返回JD数据)
EvaluatorAgent
  ↓ (save_evaluation)
DataManagerAgent
  ↓ (返回评估结果)
EvaluatorAgent
  ↓ (返回评估结果)
CoordinatorAgent
  ↓ (generate_suggestions)
OptimizerAgent
  ↓ (get_jd, get_evaluation)
DataManagerAgent
  ↓ (返回数据)
OptimizerAgent
  ↓ (返回优化建议)
CoordinatorAgent
  ↓ (返回完整结果)
API/UI
```

### 批量上传流程

```
API/UI
  ↓ (batch_upload)
BatchUploadAgent
  ↓ (循环处理每个文件)
  ├─ (parse_jd)
  │  ParserAgent
  │    ↓ (save_jd)
  │    DataManagerAgent
  │    ↓ (返回jd_id)
  │  ParserAgent
  │  ↓ (返回解析结果)
  ├─ (evaluate_quality)
  │  EvaluatorAgent
  │    ↓ (get_jd, save_evaluation)
  │    DataManagerAgent
  │  EvaluatorAgent
  │  ↓ (返回评估结果)
  └─ (汇总结果)
BatchUploadAgent
  ↓ (返回批量处理结果)
API/UI
```

## 注意事项

1. **Agent启动顺序**：建议先启动DataManagerAgent，再启动其他Agent
2. **超时设置**：Agent间通讯默认超时30秒，复杂操作（如LLM调用）可设置更长超时
3. **错误处理**：所有Agent都实现了完善的错误处理，失败时会返回详细错误信息
4. **上下文管理**：使用MCP Context跟踪工作流状态，支持断点续传
5. **并发控制**：批量处理时注意控制并发数，避免过载

## 扩展开发

### 添加新Agent

1. 继承`MCPAgent`基类
2. 实现`__init__`方法，注册消息处理器
3. 实现消息处理方法
4. 在`__init__.py`中导出
5. 创建便捷函数`create_xxx_agent`

示例：

```python
from src.mcp.agent import MCPAgent

class MyCustomAgent(MCPAgent):
    def __init__(self, mcp_server, agent_id="my_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="my_custom",
            mcp_server=mcp_server
        )
        
        self.register_handler("my_action", self.handle_my_action)
    
    async def handle_my_action(self, message):
        # 处理逻辑
        await self.send_response(message, {
            "success": True,
            "result": "..."
        })
```

## 测试

每个Agent都应该有对应的单元测试，测试文件位于项目根目录的`test_*.py`文件中。

运行测试：

```bash
pytest test_agents.py -v
```

## 性能优化

1. **LLM缓存**：所有Agent使用的LLM客户端都启用了缓存，相同请求会直接返回缓存结果
2. **批量处理**：BatchUploadAgent支持并发处理多个文件
3. **异步通讯**：所有Agent间通讯都是异步的，不会阻塞
4. **上下文过期**：MCP Context会自动过期清理，避免内存泄漏

## 监控和日志

所有Agent都使用Python标准logging模块记录日志，日志级别可通过环境变量配置：

```bash
export LOG_LEVEL=INFO
```

日志格式：

```
2024-01-01 12:00:00 INFO [ParserAgent] 收到JD解析请求, 文本长度=1234
2024-01-01 12:00:05 INFO [ParserAgent] JD解析成功: jd_id=xxx, 职位=高级Python工程师
```

## 故障排查

### Agent无法启动

1. 检查Redis是否运行：`redis-cli ping`
2. 检查MCP服务器是否启动
3. 查看日志输出

### Agent通讯超时

1. 检查网络连接
2. 增加超时时间
3. 检查目标Agent是否正常运行

### LLM调用失败

1. 检查API密钥配置
2. 检查网络连接
3. 查看LLM客户端日志

## 相关文档

- [MCP协议文档](../mcp/README.md)
- [LLM客户端文档](../core/README_DEEPSEEK.md)
- [数据库设计文档](../../docs/database_schema.md)
