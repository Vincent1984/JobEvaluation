# Simple MCP Client 说明

## 问题背景

在重构过程中，我们遇到了 Redis 连接问题：
```
AttributeError: 'NoneType' object has no attribute 'sadd'
```

这是因为 MCP Server 需要 Redis 连接才能正常工作，但在开发环境中可能没有安装或启动 Redis。

## 解决方案

创建了 `SimpleMCPClient` (`src/mcp/simple_client.py`)，这是一个不依赖 Redis 的简化版本：

### 特点

1. **无需 Redis**：直接调用 Agents，不通过 MCP Server
2. **快速启动**：无需额外的基础设施
3. **开发友好**：适合本地开发和测试
4. **功能完整**：支持所有核心功能（解析、评估、分析）

### 架构对比

#### 完整版（需要 Redis）
```
UI/API → MCP Client → MCP Server (Redis) → Agents → Database
```

#### 简化版（无需 Redis）
```
UI/API → Simple MCP Client → Agents (直接调用)
```

## 使用方法

### 在 API 中使用

```python
from ...mcp.simple_client import get_simple_mcp_client

# 获取简化客户端
mcp_client = get_simple_mcp_client()

# 使用方法与完整版相同
result = await mcp_client.analyze_jd(jd_text, model_type)
```

### 在 UI 中使用

```python
from src.mcp.simple_client import get_simple_mcp_client

# 获取简化客户端
mcp_client = get_simple_mcp_client()

# 使用方法与完整版相同
result = run_async(mcp_client.analyze_jd(jd_text, model_type))
```

## 功能支持

### ✅ 支持的功能

- ✅ JD 解析 (`parse_jd`)
- ✅ JD 评估 (`evaluate_jd`)
- ✅ 完整分析 (`analyze_jd`)
- ✅ 所有评估模型（标准、美世法、因素比较法）

### ⚠️ 限制

- ⚠️ 不支持数据持久化（`get_jd` 返回 None）
- ⚠️ 不支持 Agent 间通信（直接调用）
- ⚠️ 不支持批量处理的进度跟踪
- ⚠️ 不支持分布式部署

## 何时使用

### 使用 Simple MCP Client（当前默认）

- ✅ 本地开发环境
- ✅ 快速原型验证
- ✅ 单机部署
- ✅ 不需要数据持久化
- ✅ 没有 Redis 环境

### 使用完整 MCP Client

- ✅ 生产环境
- ✅ 需要数据持久化
- ✅ 需要 Agent 间协作
- ✅ 分布式部署
- ✅ 有 Redis 环境

## 切换到完整版

如果你有 Redis 环境，想使用完整的 MCP 架构：

### 1. 安装并启动 Redis

```bash
# Windows (使用 WSL 或 Docker)
docker run -d -p 6379:6379 redis:latest

# Linux/Mac
redis-server
```

### 2. 更新代码

将所有文件中的：
```python
from ...mcp.simple_client import get_simple_mcp_client
mcp_client = get_simple_mcp_client()
```

替换为：
```python
from ...mcp.client import get_mcp_client
mcp_client = get_mcp_client()
```

### 3. 重启服务

```bash
# 重启 API
python -m uvicorn src.api.main:app --reload

# 重启 UI
streamlit run src/ui/app.py
```

## 实现细节

### SimpleMCPClient 类

```python
class SimpleMCPClient:
    """简化的 MCP 客户端"""
    
    async def parse_jd(self, jd_text: str) -> JobDescription:
        """直接调用 Parser Agent"""
        parsed_data = await self._parser_agent._parse_jd_with_llm(jd_text)
        # 构建 JobDescription 对象
        return jd
    
    async def analyze_jd(self, jd_text: str, model_type: EvaluationModel) -> Dict:
        """解析 + 评估"""
        jd = await self.parse_jd(jd_text)
        
        # 直接调用评估模型
        model = self._evaluator_agent.evaluation_models.get(model_type.value)
        eval_result = await model.evaluate(jd_data, self._evaluator_agent.llm)
        
        return {"jd": jd, "evaluation": evaluation}
```

### 优势

1. **简单**：无需配置 Redis
2. **快速**：减少了网络通信开销
3. **可靠**：减少了依赖项
4. **易调试**：直接调用，更容易追踪问题

### 劣势

1. **无持久化**：数据不会保存
2. **无协作**：Agents 不能相互通信
3. **无扩展**：不支持分布式部署

## 未来计划

### 短期（MVP）

- ✅ 使用 Simple MCP Client
- ✅ 完成核心功能开发
- ✅ 本地测试验证

### 中期（生产准备）

- [ ] 安装 Redis
- [ ] 切换到完整 MCP Client
- [ ] 添加数据持久化
- [ ] 完善 Agent 间协作

### 长期（扩展）

- [ ] 分布式部署
- [ ] 负载均衡
- [ ] 高可用性
- [ ] 监控和日志

## 故障排除

### 问题：仍然出现 Redis 错误

**解决方案**：确保所有文件都使用 `simple_client`：

```bash
# 检查是否还有文件使用旧的 client
grep -r "from.*mcp.client import" src/
```

### 问题：Agent 初始化失败

**解决方案**：检查 LLM 配置：

```bash
# 确保 .env 文件中有正确的 API Key
cat .env | grep DEEPSEEK_API_KEY
```

### 问题：解析或评估失败

**解决方案**：查看日志：

```bash
# 查看 Streamlit 日志
# 在浏览器控制台或终端查看错误信息
```

## 总结

Simple MCP Client 是一个实用的解决方案，让我们能够在没有 Redis 的情况下继续开发。它保持了与完整版相同的 API 接口，使得将来切换到完整版变得非常简单。

对于 MVP 阶段，这个简化版本完全够用！🎉

---

**创建日期**：2024年  
**作者**：Kiro AI Assistant
