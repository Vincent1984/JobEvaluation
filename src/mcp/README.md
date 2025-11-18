# MCP消息协议使用指南

## 概述

MCP (Model Context Protocol) 是Agent间通讯的标准协议，提供了消息传递和上下文共享的机制。

## 核心组件

### 1. MCPMessage - 消息协议

用于Agent之间的标准化通讯。

#### 消息类型

- `REQUEST`: 请求消息（需要响应）
- `RESPONSE`: 响应消息
- `NOTIFICATION`: 通知消息（不需要响应）
- `EVENT`: 事件消息（广播）

#### 基本使用

```python
from src.mcp import MCPMessage, MessageType
from src.mcp.message import create_request_message

# 创建请求消息
message = create_request_message(
    sender="parser_agent",
    receiver="data_manager_agent",
    action="save_jd",
    payload={"jd_id": "jd_001", "job_title": "Python工程师"},
    context_id="ctx_001"
)

# 创建响应消息
response = message.create_response(
    payload={"success": True, "jd_id": "jd_001"},
    sender="data_manager_agent"
)

# 序列化和反序列化
json_str = message.to_json()
restored_message = MCPMessage.from_json(json_str)
```

#### 便捷函数

```python
from src.mcp.message import (
    create_request_message,
    create_notification_message,
    create_event_message
)

# 创建请求
request = create_request_message(
    sender="agent_a",
    receiver="agent_b",
    action="get_data",
    payload={"id": "123"}
)

# 创建通知
notification = create_notification_message(
    sender="agent_a",
    action="progress_update",
    payload={"progress": 50}
)

# 创建事件（广播）
event = create_event_message(
    sender="coordinator",
    action="task_completed",
    payload={"task_id": "task_001"}
)
```

### 2. MCPContext - 共享上下文

用于在多个Agent之间共享任务相关的数据和状态。

#### 基本使用

```python
from src.mcp import MCPContext
from src.mcp.context import create_context

# 创建上下文
context = create_context(
    task_id="task_001",
    workflow_type="jd_analysis",
    shared_data={"jd_text": "招聘Python工程师"},
    metadata={"priority": "high"},
    expiration_seconds=3600  # 1小时后过期
)

# 数据操作
context.update_data("step1", "completed")
context.update_data("jd_id", "jd_001")

value = context.get_data("step1")  # "completed"
has_key = context.has_data("jd_id")  # True

context.remove_data("step1")

# 参与者管理
context.add_participant("parser_agent")
context.add_participant("evaluator_agent")

is_participant = context.is_participant("parser_agent")  # True

context.remove_participant("parser_agent")

# 状态管理
context.update_status("completed")
is_completed = context.is_completed()  # True

# 序列化
json_str = context.to_json()
restored_context = MCPContext.from_json(json_str)
```

## 工作流示例

### Agent间请求-响应模式

```python
# Agent A 发送请求
request = create_request_message(
    sender="parser_agent",
    receiver="data_manager_agent",
    action="save_jd",
    payload={
        "jd_id": "jd_001",
        "job_title": "Python工程师",
        "raw_text": "招聘Python工程师..."
    },
    context_id="ctx_001"
)

# Agent B 处理请求并响应
response = request.create_response(
    payload={"success": True, "jd_id": "jd_001"},
    sender="data_manager_agent"
)
```

### 使用共享上下文的工作流

```python
# 1. 创建工作流上下文
context = create_context(
    task_id="analyze_jd_001",
    workflow_type="jd_analysis",
    shared_data={"jd_text": "招聘Python工程师..."}
)

# 2. Parser Agent 解析JD
context.add_participant("parser_agent")
context.update_data("parsed_data", {
    "job_title": "Python工程师",
    "department": "技术部"
})
context.update_data("jd_id", "jd_001")

# 3. Evaluator Agent 评估质量
context.add_participant("evaluator_agent")
jd_id = context.get_data("jd_id")
# ... 执行评估 ...
context.update_data("evaluation_result", {
    "overall_score": 85.0,
    "issues": []
})

# 4. 完成工作流
context.update_status("completed")
```

### 3. MCPServer - MCP服务器

基于Redis实现的Agent通讯中枢，提供消息发布订阅和上下文存储功能。

#### 基本使用

```python
from src.mcp import MCPServer, create_mcp_server

# 方式1: 使用便捷函数创建并启动
server = await create_mcp_server(
    redis_host="localhost",
    redis_port=6379,
    redis_db=0,
    auto_start=True
)

# 方式2: 手动创建和启动
server = MCPServer(
    redis_host="localhost",
    redis_port=6379,
    redis_db=0
)
await server.connect()
await server.start()

# 停止服务器
await server.stop()
```

#### Agent注册

```python
# 注册Agent
await server.register_agent(
    agent_id="parser_agent",
    agent_type="parser",
    metadata={"version": "1.0", "capabilities": ["parse_jd", "classify_job"]}
)

# 检查Agent是否已注册
is_registered = await server.is_agent_registered("parser_agent")

# 获取所有已注册的Agent
agents = await server.get_registered_agents()

# 注销Agent
await server.unregister_agent("parser_agent")
```

#### 消息发送

```python
from src.mcp.message import create_request_message

# 创建消息
message = create_request_message(
    sender="coordinator",
    receiver="parser_agent",
    action="parse_jd",
    payload={"jd_text": "招聘Python工程师..."}
)

# 发送消息
await server.send_message(message)

# 发送广播消息（receiver=None）
broadcast_message = create_notification_message(
    sender="coordinator",
    action="task_completed",
    payload={"task_id": "task_001"}
)
await server.send_message(broadcast_message)
```

#### 消息订阅

```python
# 订阅特定Agent的消息通道
await server.subscribe_to_channel("mcp:agent:parser_agent")

# 订阅广播通道
await server.subscribe_to_channel("mcp:broadcast")

# 注册消息处理器
async def handle_parse_request(message: MCPMessage):
    print(f"Received parse request: {message.payload}")
    # 处理消息...

server.register_message_handler("parse_jd", handle_parse_request)

# 取消订阅
await server.unsubscribe_from_channel("mcp:agent:parser_agent")
```

#### 上下文管理

```python
from src.mcp.context import create_context

# 创建上下文
context = create_context(
    task_id="task_001",
    workflow_type="jd_analysis",
    shared_data={"jd_text": "招聘Python工程师..."},
    expiration_seconds=3600
)

# 保存上下文
await server.save_context(context)

# 获取上下文
retrieved_context = await server.get_context(context.context_id)

# 更新上下文
context.update_data("step1", "completed")
await server.update_context(context)

# 删除上下文
await server.delete_context(context.context_id)

# 列出所有上下文
context_ids = await server.list_contexts()

# 清理过期上下文
cleaned_count = await server.cleanup_expired_contexts()
```

#### 健康检查和统计

```python
# 健康检查
health = await server.health_check()
print(health)
# {
#     "status": "healthy",
#     "redis_connected": True,
#     "is_running": True,
#     "registered_agents": 5,
#     "active_contexts": 10
# }

# 获取统计信息
stats = await server.get_stats()
print(stats)
# {
#     "redis_version": "7.0.0",
#     "redis_uptime_seconds": 12345,
#     "registered_agents": 5,
#     "agent_ids": ["parser_agent", "evaluator_agent", ...],
#     "active_contexts": 10,
#     "is_running": True
# }
```

## 完整工作流示例

### 使用MCP Server的Agent通讯

```python
from src.mcp import MCPServer, create_mcp_server
from src.mcp.message import create_request_message
from src.mcp.context import create_context

# 1. 启动MCP服务器
server = await create_mcp_server()

# 2. 注册Agents
await server.register_agent("coordinator", "coordinator")
await server.register_agent("parser_agent", "parser")
await server.register_agent("data_manager", "data_manager")

# 3. 创建工作流上下文
context = create_context(
    task_id="analyze_jd_001",
    workflow_type="jd_analysis",
    shared_data={"jd_text": "招聘Python工程师..."}
)
await server.save_context(context)

# 4. Coordinator发送解析请求
parse_request = create_request_message(
    sender="coordinator",
    receiver="parser_agent",
    action="parse_jd",
    payload={"jd_text": "招聘Python工程师..."},
    context_id=context.context_id
)
await server.send_message(parse_request)

# 5. Parser处理后更新上下文
context.update_data("parsed_data", {
    "job_title": "Python工程师",
    "department": "技术部"
})
context.update_data("jd_id", "jd_001")
await server.update_context(context)

# 6. Parser发送保存请求给Data Manager
save_request = create_request_message(
    sender="parser_agent",
    receiver="data_manager",
    action="save_jd",
    payload={"jd_id": "jd_001", "parsed_data": {...}},
    context_id=context.context_id
)
await server.send_message(save_request)

# 7. 完成后清理
context.update_status("completed")
await server.update_context(context)
```

## 最佳实践

1. **使用context_id关联消息**: 在同一工作流中的所有消息应使用相同的context_id
2. **设置合理的过期时间**: 为长时间运行的任务设置适当的过期时间
3. **及时更新状态**: 在工作流的关键节点更新上下文状态
4. **记录参与者**: 使用add_participant跟踪参与工作流的所有Agent
5. **使用元数据**: 在metadata中存储优先级、创建者等信息
6. **定期清理**: 定期调用cleanup_expired_contexts清理过期上下文
7. **健康监控**: 定期调用health_check监控服务器状态
8. **优雅关闭**: 应用退出时调用server.stop()优雅关闭服务器

## 消息字段说明

### MCPMessage字段

- `message_id`: 消息唯一标识符（自动生成）
- `sender`: 发送者Agent ID
- `receiver`: 接收者Agent ID（None表示广播）
- `message_type`: 消息类型（REQUEST/RESPONSE/NOTIFICATION/EVENT）
- `action`: 操作类型/动作名称
- `payload`: 消息负载数据
- `context_id`: 关联的上下文ID
- `correlation_id`: 关联的请求消息ID（用于响应）
- `timestamp`: 消息时间戳
- `metadata`: 消息元数据

### MCPContext字段

- `context_id`: 上下文唯一标识符（自动生成）
- `task_id`: 关联的任务ID
- `workflow_type`: 工作流类型
- `shared_data`: Agent间共享的数据
- `metadata`: 上下文元数据
- `status`: 上下文状态（active/completed/failed/cancelled）
- `created_at`: 创建时间戳
- `updated_at`: 最后更新时间戳
- `expires_at`: 过期时间戳
- `participants`: 参与的Agent ID列表
