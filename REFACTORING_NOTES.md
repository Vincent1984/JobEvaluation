# 重构说明：移除 Services 模块

## 重构日期
2024年（根据当前日期）

## 重构原因

根据设计文档（`.kiro/specs/jd-analyzer/design.md`），本项目采用 **MCP (Model Context Protocol) Agentic 架构**，所有业务逻辑应该由 Agents 处理，而不是传统的 Services 层。

`services` 模块的存在违背了架构设计原则，造成了架构不一致性。

## 重构内容

### 1. 创建 MCP Client (`src/mcp/client.py`)

创建了一个简化的 MCP 客户端，为 API 和 UI 层提供便捷的 Agent 调用接口：

```python
from src.mcp.client import get_mcp_client

mcp_client = get_mcp_client()

# 解析 JD
jd = await mcp_client.parse_jd(jd_text)

# 评估 JD
evaluation = await mcp_client.evaluate_jd(jd_id, model_type)

# 完整分析
result = await mcp_client.analyze_jd(jd_text, model_type)
```

### 2. 更新 API 路由

所有 API 路由文件已更新，移除对 `jd_service` 的依赖：

- `src/api/routers/jd.py` ✅
- `src/api/routers/batch.py` ✅
- `src/api/routers/questionnaire.py` ✅
- `src/api/routers/match.py` ✅

**变更示例：**

```python
# 之前
from ...services.jd_service import jd_service
result = await jd_service.analyze_jd(jd_text, model_type)

# 之后
from ...mcp.client import get_mcp_client
mcp_client = get_mcp_client()
result = await mcp_client.analyze_jd(jd_text, model_type)
```

### 3. 更新 UI 层

`src/ui/app.py` 已更新，移除对 `jd_service` 的依赖：

```python
# 之前
from src.services.jd_service import jd_service
result = run_async(jd_service.analyze_jd(jd_text, model_type))

# 之后
from src.mcp.client import get_mcp_client
mcp_client = get_mcp_client()
result = run_async(mcp_client.analyze_jd(jd_text, model_type))
```

### 4. 删除 Services 模块

以下文件已被删除：
- `src/services/jd_service.py`
- `src/services/README.md`
- `src/services/__init__.py`
- `src/services/` 目录

## 架构对比

### 重构前（不符合设计）

```
UI/API → JDService → LLM
         ↓
         临时存储（内存）
```

### 重构后（符合设计）

```
UI/API → MCP Client → MCP Server → Agents
                                    ↓
                                    DataManagerAgent → Database
```

## 优势

1. **架构一致性**：完全符合设计文档中的 MCP Agentic 架构
2. **职责清晰**：
   - API/UI 层：接收请求、展示结果
   - MCP Client：简化 Agent 调用
   - Agents：处理所有业务逻辑
   - DataManagerAgent：数据持久化
3. **可扩展性**：新增功能只需添加新的 Agent
4. **可维护性**：消除了架构不一致性

## 迁移指南

如果你的代码中还在使用 `jd_service`，请按以下步骤迁移：

### 步骤 1：更新导入

```python
# 旧代码
from src.services.jd_service import jd_service

# 新代码
from src.mcp.client import get_mcp_client
mcp_client = get_mcp_client()
```

### 步骤 2：更新方法调用

所有方法调用保持不变，只需将 `jd_service` 替换为 `mcp_client`：

```python
# 解析 JD
jd = await mcp_client.parse_jd(jd_text)

# 评估 JD
evaluation = await mcp_client.evaluate_jd(jd_id, model_type)

# 完整分析
result = await mcp_client.analyze_jd(jd_text, model_type)

# 获取 JD
jd = await mcp_client.get_jd(jd_id)
```

### 步骤 3：测试

确保所有功能正常工作：
- JD 解析
- JD 评估
- 批量上传
- 问卷生成
- 匹配评估

## 注意事项

1. **异步调用**：所有 MCP Client 方法都是异步的，必须使用 `await`
2. **初始化**：MCP Client 会自动初始化 MCP Server 和必要的 Agents
3. **单例模式**：`get_mcp_client()` 返回全局单例，避免重复初始化

## 相关文档

- 设计文档：`.kiro/specs/jd-analyzer/design.md`
- 架构不一致性说明：`ARCHITECTURE_INCONSISTENCY.md`
- MCP 协议说明：`src/mcp/README.md`

## 后续工作

- [ ] 更新测试文件，移除对 `jd_service` 的依赖
- [ ] 完善 MCP Client 的错误处理
- [ ] 添加 MCP Client 的单元测试
- [ ] 更新项目文档

## 总结

通过这次重构，我们成功地：
1. 移除了不符合架构设计的 Services 层
2. 统一了所有业务逻辑到 Agents
3. 简化了 API 和 UI 层的代码
4. 提高了代码的可维护性和可扩展性

现在整个项目完全符合 MCP Agentic 架构设计！
