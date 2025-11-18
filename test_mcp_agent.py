"""测试MCP Agent基类实现"""

import asyncio
import pytest
from src.mcp import MCPServer, MCPAgent, MCPMessage, MessageType


@pytest.fixture
async def mcp_server():
    """创建MCP服务器fixture"""
    server = MCPServer(
        redis_host="localhost",
        redis_port=6379,
        redis_db=0
    )
    await server.start()
    yield server
    await server.stop()


@pytest.fixture
async def test_agent(mcp_server):
    """创建测试Agent fixture"""
    agent = MCPAgent(
        agent_id="test_agent",
        agent_type="test",
        mcp_server=mcp_server,
        metadata={"version": "1.0"}
    )
    await agent.start()
    yield agent
    await agent.stop()


@pytest.mark.asyncio
async def test_agent_initialization():
    """测试Agent初始化"""
    server = MCPServer()
    await server.connect()
    
    agent = MCPAgent(
        agent_id="agent_001",
        agent_type="parser",
        mcp_server=server,
        metadata={"version": "1.0", "description": "Test agent"}
    )
    
    assert agent.agent_id == "agent_001"
    assert agent.agent_type == "parser"
    assert agent.metadata["version"] == "1.0"
    assert not agent.is_running
    assert len(agent.message_handlers) == 0
    assert len(agent.tools) == 0
    
    await server.disconnect()


@pytest.mark.asyncio
async def test_agent_start_stop(mcp_server):
    """测试Agent启动和停止"""
    agent = MCPAgent(
        agent_id="agent_002",
        agent_type="evaluator",
        mcp_server=mcp_server
    )
    
    # 启动Agent
    await agent.start()
    assert agent.is_running
    
    # 验证Agent已注册
    is_registered = await mcp_server.is_agent_registered("agent_002")
    assert is_registered
    
    # 停止Agent
    await agent.stop()
    assert not agent.is_running
    
    # 验证Agent已注销
    is_registered = await mcp_server.is_agent_registered("agent_002")
    assert not is_registered


@pytest.mark.asyncio
async def test_message_handler_registration(test_agent):
    """测试消息处理器注册"""
    
    # 定义处理器
    async def handle_test_action(message: MCPMessage):
        print(f"Handling action: {message.action}")
    
    # 注册处理器
    test_agent.register_handler("test_action", handle_test_action)
    
    # 验证注册
    assert "test_action" in test_agent.message_handlers
    assert len(test_agent.get_registered_actions()) == 1
    
    # 注销处理器
    test_agent.unregister_handler("test_action")
    assert "test_action" not in test_agent.message_handlers
    assert len(test_agent.get_registered_actions()) == 0


@pytest.mark.asyncio
async def test_request_response_pattern(mcp_server):
    """测试请求-响应模式"""
    
    # 创建两个Agent
    agent_a = MCPAgent(
        agent_id="agent_a",
        agent_type="requester",
        mcp_server=mcp_server
    )
    
    agent_b = MCPAgent(
        agent_id="agent_b",
        agent_type="responder",
        mcp_server=mcp_server
    )
    
    await agent_a.start()
    await agent_b.start()
    
    # 为agent_b注册处理器
    async def handle_request(message: MCPMessage):
        # 发送响应
        await agent_b.send_response(
            request_message=message,
            payload={"result": "success", "data": "processed"}
        )
    
    agent_b.register_handler("process_data", handle_request)
    
    # agent_a发送请求
    response = await agent_a.send_request(
        receiver="agent_b",
        action="process_data",
        payload={"input": "test data"},
        timeout=5.0
    )
    
    # 验证响应
    assert response.is_response()
    assert response.sender == "agent_b"
    assert response.receiver == "agent_a"
    assert response.payload["result"] == "success"
    assert response.payload["data"] == "processed"
    
    await agent_a.stop()
    await agent_b.stop()


@pytest.mark.asyncio
async def test_notification_message(mcp_server):
    """测试通知消息"""
    
    # 创建两个Agent
    sender = MCPAgent(
        agent_id="sender_agent",
        agent_type="sender",
        mcp_server=mcp_server
    )
    
    receiver = MCPAgent(
        agent_id="receiver_agent",
        agent_type="receiver",
        mcp_server=mcp_server
    )
    
    await sender.start()
    await receiver.start()
    
    # 用于验证的标志
    notification_received = asyncio.Event()
    received_payload = {}
    
    # 为receiver注册处理器
    async def handle_notification(message: MCPMessage):
        nonlocal received_payload
        received_payload = message.payload
        notification_received.set()
    
    receiver.register_handler("status_update", handle_notification)
    
    # 发送通知
    await sender.send_notification(
        action="status_update",
        payload={"status": "processing", "progress": 50},
        receiver="receiver_agent"
    )
    
    # 等待通知被接收
    await asyncio.wait_for(notification_received.wait(), timeout=5.0)
    
    # 验证接收到的数据
    assert received_payload["status"] == "processing"
    assert received_payload["progress"] == 50
    
    await sender.stop()
    await receiver.stop()


@pytest.mark.asyncio
async def test_broadcast_message(mcp_server):
    """测试广播消息"""
    
    # 创建一个发送者和多个接收者
    sender = MCPAgent(
        agent_id="broadcaster",
        agent_type="sender",
        mcp_server=mcp_server
    )
    
    receiver1 = MCPAgent(
        agent_id="receiver_1",
        agent_type="receiver",
        mcp_server=mcp_server
    )
    
    receiver2 = MCPAgent(
        agent_id="receiver_2",
        agent_type="receiver",
        mcp_server=mcp_server
    )
    
    await sender.start()
    await receiver1.start()
    await receiver2.start()
    
    # 用于验证的标志
    receiver1_event = asyncio.Event()
    receiver2_event = asyncio.Event()
    
    # 为接收者注册处理器
    async def handle_broadcast_1(message: MCPMessage):
        receiver1_event.set()
    
    async def handle_broadcast_2(message: MCPMessage):
        receiver2_event.set()
    
    receiver1.register_handler("broadcast_event", handle_broadcast_1)
    receiver2.register_handler("broadcast_event", handle_broadcast_2)
    
    # 发送广播消息
    await sender.send_notification(
        action="broadcast_event",
        payload={"message": "Hello everyone!"},
        receiver=None  # 广播
    )
    
    # 等待两个接收者都收到消息
    await asyncio.wait_for(receiver1_event.wait(), timeout=5.0)
    await asyncio.wait_for(receiver2_event.wait(), timeout=5.0)
    
    await sender.stop()
    await receiver1.stop()
    await receiver2.stop()


@pytest.mark.asyncio
async def test_context_management(mcp_server):
    """测试上下文管理"""
    
    agent = MCPAgent(
        agent_id="context_agent",
        agent_type="test",
        mcp_server=mcp_server
    )
    
    await agent.start()
    
    # 创建上下文
    context = await agent.create_context(
        task_id="task_001",
        workflow_type="test_workflow",
        shared_data={"key": "value"},
        metadata={"priority": "high"},
        expiration_seconds=3600
    )
    
    assert context.task_id == "task_001"
    assert context.workflow_type == "test_workflow"
    assert context.shared_data["key"] == "value"
    assert agent.agent_id in context.participants
    
    # 获取上下文
    retrieved_context = await agent.get_context(context.context_id)
    assert retrieved_context is not None
    assert retrieved_context.context_id == context.context_id
    
    # 更新上下文
    context.update_data("new_key", "new_value")
    await agent.update_context(context)
    
    # 验证更新
    updated_context = await agent.get_context(context.context_id)
    assert updated_context.get_data("new_key") == "new_value"
    
    await agent.stop()


@pytest.mark.asyncio
async def test_tool_registration(test_agent):
    """测试工具注册"""
    
    # 定义工具函数
    def tool_1():
        return "tool_1_result"
    
    def tool_2():
        return "tool_2_result"
    
    # 注册工具
    test_agent.register_tool(tool_1)
    test_agent.register_tool(tool_2)
    
    # 验证注册
    tools = test_agent.get_tools()
    assert len(tools) == 2
    assert tool_1 in tools
    assert tool_2 in tools
    
    # 注销工具
    test_agent.unregister_tool(tool_1)
    tools = test_agent.get_tools()
    assert len(tools) == 1
    assert tool_1 not in tools
    assert tool_2 in tools


@pytest.mark.asyncio
async def test_agent_info(test_agent):
    """测试Agent信息获取"""
    
    # 注册一些处理器和工具
    async def handler(msg):
        pass
    
    def tool():
        pass
    
    test_agent.register_handler("action_1", handler)
    test_agent.register_tool(tool)
    
    # 获取信息
    info = test_agent.get_info()
    
    assert info["agent_id"] == "test_agent"
    assert info["agent_type"] == "test"
    assert info["is_running"] is True
    assert "action_1" in info["registered_actions"]
    assert "tool" in info["registered_tools"]


@pytest.mark.asyncio
async def test_agent_health_check(test_agent):
    """测试Agent健康检查"""
    
    health = await test_agent.health_check()
    
    assert health["agent_id"] == "test_agent"
    assert health["agent_type"] == "test"
    assert health["is_running"] is True
    assert health["is_registered"] is True
    assert health["status"] == "healthy"


@pytest.mark.asyncio
async def test_request_timeout(mcp_server):
    """测试请求超时"""
    
    agent = MCPAgent(
        agent_id="timeout_agent",
        agent_type="test",
        mcp_server=mcp_server
    )
    
    await agent.start()
    
    # 发送请求到不存在的Agent（应该超时）
    with pytest.raises(asyncio.TimeoutError):
        await agent.send_request(
            receiver="non_existent_agent",
            action="test_action",
            payload={},
            timeout=1.0
        )
    
    await agent.stop()


@pytest.mark.asyncio
async def test_multiple_handlers(mcp_server):
    """测试多个处理器"""
    
    agent = MCPAgent(
        agent_id="multi_handler_agent",
        agent_type="test",
        mcp_server=mcp_server
    )
    
    await agent.start()
    
    # 注册多个处理器
    handler_calls = []
    
    async def handler_1(message: MCPMessage):
        handler_calls.append("handler_1")
    
    async def handler_2(message: MCPMessage):
        handler_calls.append("handler_2")
    
    async def handler_3(message: MCPMessage):
        handler_calls.append("handler_3")
    
    agent.register_handler("action_1", handler_1)
    agent.register_handler("action_2", handler_2)
    agent.register_handler("action_3", handler_3)
    
    # 验证所有处理器都已注册
    actions = agent.get_registered_actions()
    assert len(actions) == 3
    assert "action_1" in actions
    assert "action_2" in actions
    assert "action_3" in actions
    
    await agent.stop()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
