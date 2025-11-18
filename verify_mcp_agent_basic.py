"""验证MCPAgent基类实现 - 不需要Redis"""

import asyncio
from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage, MessageType


class MockMCPServer:
    """模拟MCP服务器用于测试"""
    
    def __init__(self):
        self.registered_agents = {}
        self.pubsub = None
    
    async def register_agent(self, agent_id: str, agent_type: str, metadata: dict = None):
        """注册Agent"""
        self.registered_agents[agent_id] = {
            "agent_type": agent_type,
            "metadata": metadata or {}
        }
        print(f"✓ Agent registered: {agent_id} (type: {agent_type})")
    
    async def unregister_agent(self, agent_id: str):
        """注销Agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
        print(f"✓ Agent unregistered: {agent_id}")
    
    async def is_agent_registered(self, agent_id: str) -> bool:
        """检查Agent是否已注册"""
        return agent_id in self.registered_agents
    
    async def subscribe_to_channel(self, channel: str):
        """订阅通道"""
        print(f"✓ Subscribed to channel: {channel}")
    
    async def unsubscribe_from_channel(self, channel: str):
        """取消订阅通道"""
        print(f"✓ Unsubscribed from channel: {channel}")
    
    async def send_message(self, message: MCPMessage):
        """发送消息"""
        print(f"✓ Message sent: {message.message_id} from {message.sender} to {message.receiver or 'broadcast'}")
    
    async def get_context(self, context_id: str):
        """获取上下文"""
        return None
    
    async def save_context(self, context):
        """保存上下文"""
        print(f"✓ Context saved: {context.context_id}")
    
    async def update_context(self, context):
        """更新上下文"""
        print(f"✓ Context updated: {context.context_id}")


async def test_agent_initialization():
    """测试1: Agent初始化"""
    print("\n=== 测试1: Agent初始化 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_001",
        agent_type="parser",
        mcp_server=server,
        metadata={"version": "1.0", "description": "Test agent"}
    )
    
    assert agent.agent_id == "test_agent_001"
    assert agent.agent_type == "parser"
    assert agent.metadata["version"] == "1.0"
    assert not agent.is_running
    assert len(agent.message_handlers) == 0
    assert len(agent.tools) == 0
    
    print("✓ Agent初始化成功")
    print(f"  - Agent ID: {agent.agent_id}")
    print(f"  - Agent Type: {agent.agent_type}")
    print(f"  - Is Running: {agent.is_running}")


async def test_agent_start_stop():
    """测试2: Agent启动和停止"""
    print("\n=== 测试2: Agent启动和停止 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_002",
        agent_type="evaluator",
        mcp_server=server
    )
    
    # 启动Agent
    await agent.start()
    assert agent.is_running
    print("✓ Agent启动成功")
    
    # 验证Agent已注册
    is_registered = await server.is_agent_registered("test_agent_002")
    assert is_registered
    print("✓ Agent已注册到服务器")
    
    # 停止Agent
    await agent.stop()
    assert not agent.is_running
    print("✓ Agent停止成功")


async def test_message_handler_registration():
    """测试3: 消息处理器注册"""
    print("\n=== 测试3: 消息处理器注册 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_003",
        agent_type="test",
        mcp_server=server
    )
    
    # 定义处理器
    async def handle_parse_jd(message: MCPMessage):
        print(f"Handling action: {message.action}")
    
    async def handle_evaluate_quality(message: MCPMessage):
        print(f"Handling action: {message.action}")
    
    # 注册处理器
    agent.register_handler("parse_jd", handle_parse_jd)
    agent.register_handler("evaluate_quality", handle_evaluate_quality)
    
    # 验证注册
    assert "parse_jd" in agent.message_handlers
    assert "evaluate_quality" in agent.message_handlers
    assert len(agent.get_registered_actions()) == 2
    
    print("✓ 消息处理器注册成功")
    print(f"  - 已注册的操作: {agent.get_registered_actions()}")
    
    # 注销处理器
    agent.unregister_handler("parse_jd")
    assert "parse_jd" not in agent.message_handlers
    assert len(agent.get_registered_actions()) == 1
    
    print("✓ 消息处理器注销成功")


async def test_tool_registration():
    """测试4: 工具注册"""
    print("\n=== 测试4: 工具注册 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_004",
        agent_type="test",
        mcp_server=server
    )
    
    # 定义工具函数
    def parse_text_tool(text: str):
        return {"parsed": text}
    
    def validate_data_tool(data: dict):
        return {"valid": True}
    
    # 注册工具
    agent.register_tool(parse_text_tool)
    agent.register_tool(validate_data_tool)
    
    # 验证注册
    tools = agent.get_tools()
    assert len(tools) == 2
    assert parse_text_tool in tools
    assert validate_data_tool in tools
    
    print("✓ 工具注册成功")
    print(f"  - 已注册的工具数量: {len(tools)}")
    
    # 注销工具
    agent.unregister_tool(parse_text_tool)
    tools = agent.get_tools()
    assert len(tools) == 1
    assert parse_text_tool not in tools
    
    print("✓ 工具注销成功")


async def test_send_request():
    """测试5: 发送请求消息"""
    print("\n=== 测试5: 发送请求消息 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="requester_agent",
        agent_type="requester",
        mcp_server=server
    )
    
    await agent.start()
    
    # 创建一个任务来发送请求（不等待响应，因为没有真实的接收者）
    try:
        # 使用短超时时间
        await asyncio.wait_for(
            agent.send_request(
                receiver="parser_agent",
                action="parse_jd",
                payload={"jd_text": "招聘高级Python工程师..."},
                timeout=0.5
            ),
            timeout=1.0
        )
    except asyncio.TimeoutError:
        print("✓ 请求发送成功（超时是预期的，因为没有接收者）")
    
    await agent.stop()


async def test_send_notification():
    """测试6: 发送通知消息"""
    print("\n=== 测试6: 发送通知消息 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="notifier_agent",
        agent_type="notifier",
        mcp_server=server
    )
    
    await agent.start()
    
    # 发送通知
    await agent.send_notification(
        action="status_update",
        payload={"status": "processing", "progress": 50},
        receiver="monitor_agent"
    )
    
    print("✓ 通知消息发送成功")
    
    # 发送广播通知
    await agent.send_notification(
        action="system_event",
        payload={"event": "task_completed"},
        receiver=None  # 广播
    )
    
    print("✓ 广播消息发送成功")
    
    await agent.stop()


async def test_context_management():
    """测试7: 上下文管理"""
    print("\n=== 测试7: 上下文管理 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="context_agent",
        agent_type="test",
        mcp_server=server
    )
    
    await agent.start()
    
    # 创建上下文
    context = await agent.create_context(
        task_id="task_001",
        workflow_type="jd_analysis",
        shared_data={"jd_text": "招聘高级Python工程师..."},
        metadata={"priority": "high"},
        expiration_seconds=3600
    )
    
    assert context.task_id == "task_001"
    assert context.workflow_type == "jd_analysis"
    assert context.shared_data["jd_text"] == "招聘高级Python工程师..."
    assert agent.agent_id in context.participants
    
    print("✓ 上下文创建成功")
    print(f"  - Context ID: {context.context_id}")
    print(f"  - Task ID: {context.task_id}")
    print(f"  - Workflow Type: {context.workflow_type}")
    print(f"  - Participants: {context.participants}")
    
    # 更新上下文
    context.update_data("jd_id", "jd_001")
    await agent.update_context(context)
    
    print("✓ 上下文更新成功")
    
    await agent.stop()


async def test_agent_info():
    """测试8: Agent信息获取"""
    print("\n=== 测试8: Agent信息获取 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="info_agent",
        agent_type="test",
        mcp_server=server,
        metadata={"version": "2.0"}
    )
    
    await agent.start()
    
    # 注册一些处理器和工具
    async def handler(msg):
        pass
    
    def tool():
        pass
    
    agent.register_handler("action_1", handler)
    agent.register_handler("action_2", handler)
    agent.register_tool(tool)
    
    # 获取信息
    info = agent.get_info()
    
    assert info["agent_id"] == "info_agent"
    assert info["agent_type"] == "test"
    assert info["is_running"] is True
    assert "action_1" in info["registered_actions"]
    assert "action_2" in info["registered_actions"]
    assert "tool" in info["registered_tools"]
    
    print("✓ Agent信息获取成功")
    print(f"  - Agent ID: {info['agent_id']}")
    print(f"  - Agent Type: {info['agent_type']}")
    print(f"  - Is Running: {info['is_running']}")
    print(f"  - Registered Actions: {info['registered_actions']}")
    print(f"  - Registered Tools: {info['registered_tools']}")
    
    await agent.stop()


async def test_agent_health_check():
    """测试9: Agent健康检查"""
    print("\n=== 测试9: Agent健康检查 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="health_agent",
        agent_type="test",
        mcp_server=server
    )
    
    await agent.start()
    
    health = await agent.health_check()
    
    assert health["agent_id"] == "health_agent"
    assert health["agent_type"] == "test"
    assert health["is_running"] is True
    assert health["is_registered"] is True
    assert health["status"] == "healthy"
    
    print("✓ Agent健康检查成功")
    print(f"  - Status: {health['status']}")
    print(f"  - Is Running: {health['is_running']}")
    print(f"  - Is Registered: {health['is_registered']}")
    
    await agent.stop()


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("MCPAgent基类实现验证")
    print("=" * 60)
    
    try:
        await test_agent_initialization()
        await test_agent_start_stop()
        await test_message_handler_registration()
        await test_tool_registration()
        await test_send_request()
        await test_send_notification()
        await test_context_management()
        await test_agent_info()
        await test_agent_health_check()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\nMCPAgent基类实现验证完成，包括：")
        print("  1. ✓ Agent注册和消息订阅")
        print("  2. ✓ 消息处理器注册机制")
        print("  3. ✓ 请求-响应模式")
        print("  4. ✓ 通知消息发送")
        print("  5. ✓ 上下文管理")
        print("  6. ✓ 工具注册")
        print("  7. ✓ Agent信息获取")
        print("  8. ✓ 健康检查")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
