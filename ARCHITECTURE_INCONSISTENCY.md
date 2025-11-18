# 架构不一致问题：Services vs Agents

## 问题描述

**你的问题**：为什么 `services` 模块做 JD 解析时，不调用相应的 Agent？

**现状**：
- ✅ 有 `ParserAgent` - 专门负责 JD 解析
- ✅ 有 `EvaluatorAgent` - 专门负责质量评估
- ❌ 但 `JDService` 直接调用 LLM，绕过了 Agents

## 架构对比

### 当前实现（不一致）

```python
# JDService - 直接调用 LLM
class JDService:
    async def parse_jd(self, jd_text: str):
        # ❌ 直接调用 LLM，绕过 ParserAgent
        parsed_data = await llm_client.generate_json(prompt)
        return JobDescription(...)
    
    async def evaluate_jd(self, jd_id: str):
        # ❌ 直接调用 LLM，绕过 EvaluatorAgent
        eval_data = await llm_client.generate_json(prompt)
        return EvaluationResult(...)
```

```python
# ParserAgent - 也在做同样的事情
class ParserAgent:
    async def handle_parse_jd(self, message):
        # ✅ 使用 LLM 解析
        parsed_data = await self._parse_jd_with_llm(jd_text)
        # ✅ 自动分类
        category_ids = await self._classify_job(parsed_data)
        # ✅ 保存到数据库
        await self.send_request("data_manager", "save_jd", ...)
```

### 问题

1. **功能重复** - JDService 和 ParserAgent 都在做 JD 解析
2. **逻辑不一致** - 两个地方的解析逻辑可能不同
3. **维护困难** - 修改解析逻辑需要改两个地方
4. **架构混乱** - 不清楚应该用哪个

## 为什么会这样？

### 历史原因

这是**渐进式开发**导致的：

1. **第一阶段（MVP）**：快速实现
   ```python
   # 最简单的方式 - 直接调用 LLM
   jd_service = JDService()  # 直接用 LLM
   ```

2. **第二阶段（Agent 系统）**：引入 MCP 架构
   ```python
   # 更复杂但更强大 - 使用 Agent
   parser_agent = ParserAgent()  # 通过 MCP 协议
   ```

3. **结果**：两套系统并存，但没有统一

### 设计文档的视角

查看设计文档 `.kiro/specs/jd-analyzer/design.md`：

**设计文档强调的是 Agent 架构**：
- Parser Agent 负责解析
- Evaluator Agent 负责评估
- Data Manager Agent 负责存储

**但实际实现时**：
- 为了快速 MVP，先实现了简单的 Service
- 后来添加了 Agent，但没有重构 Service

## 应该如何改进？

### 方案 1：Service 调用 Agent（推荐）

让 Service 成为 Agent 的**简化接口**：

```python
class JDService:
    """JD分析服务 - Agent 的简化接口"""
    
    def __init__(self, mcp_server: MCPServer):
        self.mcp_server = mcp_server
        self.parser_agent = None
        self.evaluator_agent = None
    
    async def parse_jd(self, jd_text: str) -> JobDescription:
        """解析JD - 调用 ParserAgent"""
        # ✅ 通过 MCP 调用 ParserAgent
        response = await self.mcp_server.send_request(
            sender="jd_service",
            receiver="parser",
            action="parse_jd",
            payload={"jd_text": jd_text}
        )
        
        if not response.payload.get("success"):
            raise Exception(response.payload.get("error"))
        
        return JobDescription(**response.payload["parsed_data"])
    
    async def evaluate_jd(self, jd_id: str) -> EvaluationResult:
        """评估JD - 调用 EvaluatorAgent"""
        # ✅ 通过 MCP 调用 EvaluatorAgent
        response = await self.mcp_server.send_request(
            sender="jd_service",
            receiver="evaluator",
            action="evaluate_quality",
            payload={"jd_id": jd_id}
        )
        
        if not response.payload.get("success"):
            raise Exception(response.payload.get("error"))
        
        return EvaluationResult(**response.payload["evaluation"])
```

**优点**：
- ✅ 统一使用 Agent 的逻辑
- ✅ Service 成为简单的封装层
- ✅ 保持 Agent 架构的完整性
- ✅ UI/API 可以继续使用 Service

**缺点**：
- ⚠️ 需要启动 MCP Server 和 Agents
- ⚠️ 增加了一层调用

### 方案 2：移除 Service，直接用 Agent

完全使用 Agent 架构：

```python
# UI 中直接调用 Agent
async def analyze_jd_ui(jd_text: str):
    # 发送消息给 ParserAgent
    response = await mcp_server.send_request(
        sender="ui",
        receiver="parser",
        action="parse_jd",
        payload={"jd_text": jd_text}
    )
    return response
```

**优点**：
- ✅ 架构清晰，只有一套系统
- ✅ 完全符合设计文档

**缺点**：
- ❌ UI/API 代码变复杂
- ❌ 需要理解 MCP 协议
- ❌ 简单场景也要用复杂的 Agent

### 方案 3：分场景使用（当前状态）

简单场景用 Service，复杂场景用 Agent：

```python
# 简单场景 - 单个 JD 分析
result = await jd_service.analyze_jd(jd_text)

# 复杂场景 - 批量上传（需要多 Agent 协作）
result = await batch_upload_agent.handle_batch_upload(files)
```

**优点**：
- ✅ 灵活，根据场景选择
- ✅ 简单场景不需要 Agent 开销

**缺点**：
- ❌ 架构不统一
- ❌ 逻辑重复
- ❌ 维护困难

## 推荐方案

### 短期（当前 MVP）

**保持现状**，但明确分工：

```
简单场景（单个 JD）:
  UI/API → JDService → LLM
  
复杂场景（批量、协作）:
  UI/API → Agent → MCP → 其他 Agents
```

**理由**：
- MVP 阶段，快速迭代更重要
- 避免过度工程化
- 两套系统各有用途

### 长期（生产环境）

**统一到 Agent 架构**：

1. **重构 JDService**
   ```python
   class JDService:
       """简化的 Agent 接口"""
       async def parse_jd(self, jd_text):
           return await self._call_agent("parser", "parse_jd", ...)
   ```

2. **提供两种接口**
   ```python
   # 简单接口 - 给不熟悉 MCP 的开发者
   result = await jd_service.analyze_jd(jd_text)
   
   # 完整接口 - 给需要高级功能的场景
   result = await parser_agent.handle_parse_jd(message)
   ```

3. **文档说明**
   - 何时用 Service（简单场景）
   - 何时用 Agent（复杂场景）

## 实际影响

### 当前系统中的使用

**使用 JDService 的地方**：
- `src/ui/app.py` - Streamlit UI
- `src/api/routers/jd.py` - API 端点（可能）

**使用 Agent 的地方**：
- `src/agents/batch_upload_agent.py` - 批量上传
- `src/workflows/` - 工作流

### 功能差异

| 功能 | JDService | ParserAgent |
|------|-----------|-------------|
| JD 解析 | ✅ 基本解析 | ✅ 解析 + 自动分类 |
| 质量评估 | ✅ 基本评估 | ✅ 多模型评估 |
| 数据存储 | ❌ 内存存储 | ✅ 数据库存储 |
| 自动分类 | ❌ 不支持 | ✅ 支持 |
| 协作能力 | ❌ 单独工作 | ✅ 多 Agent 协作 |

## 如何选择？

### 使用 JDService 的场景

```python
# ✅ 适合：快速原型、简单分析
result = await jd_service.analyze_jd(jd_text)
```

**适用于**：
- 单个 JD 分析
- 不需要分类
- 不需要持久化
- 快速测试

### 使用 Agent 的场景

```python
# ✅ 适合：生产环境、复杂流程
response = await mcp_server.send_request(
    receiver="parser",
    action="parse_jd",
    payload={"jd_text": jd_text}
)
```

**适用于**：
- 批量处理
- 需要自动分类
- 需要数据库存储
- 多 Agent 协作
- 生产环境

## 总结

### 问题本质

这是**架构演进**过程中的正常现象：
1. MVP 阶段：快速实现（JDService）
2. 完善阶段：引入 Agent 架构
3. 过渡阶段：两套系统并存 ← **我们在这里**
4. 成熟阶段：统一架构

### 当前建议

**对于你的项目**：
1. ✅ **保持现状** - MVP 阶段不需要完美
2. ✅ **明确分工** - 简单用 Service，复杂用 Agent
3. ✅ **文档说明** - 让团队知道何时用哪个
4. ⏰ **计划重构** - 生产环境前统一架构

### 未来改进

当项目稳定后：
1. 重构 JDService 调用 Agent
2. 或者移除 JDService，统一用 Agent
3. 更新文档和示例
4. 迁移现有代码

---

**关键点**：这不是错误，而是**渐进式开发的正常过程**。重要的是：
- 知道为什么会这样
- 知道何时用哪个
- 计划未来的改进

**你的问题很好**，说明你在认真思考架构！👍
