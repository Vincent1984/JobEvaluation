"""验证MCPAgent基类实现 - 不需要Redis"""

import asyncio
from src.mcp.agent import MCPAgent
from src.mcp.message import MCPMessage, MessageType, create_request_message


class MockMCPServer:
    """模拟MCP服务器用于测试"""
    
    def __init__(self):
        self.registered_agents = {}
        self.pubsub = None
    
    async def register_agent(self, agent_id: str, agent_type: str, metadata: dict):
        """注册Agent"""
        self.registered_agents[agent_id] = {
            "agent_type": agent_type,
            "metadata": metadata
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


async def test_agent_initialization():
    """测试1: Agent初始化"""
    print("\n=== 测试1: Agent初始化 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_001",
        agent_type="parser",
        mcp_server=server,
        metadata={"version": "1.0", "description": "Test parser agent"}
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
    print(f"  - Metadata: {agent.metadata}")
    print(f"  - Is Running: {agent.is_running}")


async def test_agent_registration():
    """测试2: Agent注册和消息订阅"""
    print("\n=== 测试2: Agent注册和消息订阅 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_002",
        agent_type="evaluator",
        mcp_server=server
    )
    
    # 启动Agent（会触发注册和订阅）
    await agent.start()
    
    assert agent.is_running
    assert await server.is_agent_registered("test_agent_002")
    
    print("✓ Agent注册和订阅成功")
    print(f"  - Agent运行状态: {agent.is_running}")
    print(f"  - 已订阅通道数: {len(agent._subscribed_channels)}")
    
    # 停止Agent
    await agent.stop()
    
    assert not agent.is_running
    assert not await server.is_agent_registered("test_agent_002")
    
    print("✓ Agent注销成功")


async def test_message_handler_registration():
    """测试3: 消息处理器注册机制"""
    print("\n=== 测试3: 消息处理器注册机制 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_003",
        agent_type="test",
        mcp_server=server
    )
    
    # 定义处理器
    async def handle_parse_jd(message: MCPMessage):
        print(f"  处理消息: {message.action}")
    
    async def handle_evaluate_quality(message: MCPMessage):
        print(f"  处理消息: {message.action}")
    
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
    print(f"  - 剩余操作: {agent.get_registered_actions()}")


async def test_request_response_pattern():
    """测试4: 请求-响应模式"""
    print("\n=== 测试4: 请求-响应模式 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_004",
        agent_type="test",
        mcp_server=server
    )
    
    await agent.start()
    
    # 测试发送请求
    request_task = asyncio.create_task(
        agent.send_request(
            receiver="data_manager",
            action="save_jd",
            payload={"jd_id": "jd_001", "title": "Python工程师"},
            timeout=2.0
        )
    )
    
    # 等待一小段时间让请求被发送
    await asyncio.sleep(0.1)
    
    # 验证请求已发送
    assert len(agent._pending_responses) == 1
    print("✓ 请求已发送")
    print(f"  - 待处理响应数: {len(agent._pending_responses)}")
    
    # 取消请求任务（因为没有真实的响应者）
    request_task.cancel()
    try:
        await request_task
    except asyncio.CancelledError:
        pass
    
    await agent.stop()
    
    print("✓ 请求-响应模式测试完成")


async def test_notification_sending():
    """测试5: 发送通知消息"""
    print("\n=== 测试5: 发送通知消息 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_005",
        agent_type="test",
        mcp_server=server
    )
    
    await agent.start()
    
    # 发送点对点通知
    await agent.send_notification(
        action="status_update",
        payload={"status": "processing", "progress": 50},
        receiver="coordinator"
    )
    
    print("✓ 点对点通知已发送")
    
    # 发送广播通知
    await agent.send_notification(
        action="system_event",
        payload={"event": "task_completed"},
        receiver=None  # 广播
    )
    
    print("✓ 广播通知已发送")
    
    await agent.stop()


async def test_tool_registration():
    """测试6: 工具注册"""
    print("\n=== 测试6: 工具注册 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_006",
        agent_type="test",
        mcp_server=server
    )
    
    # 定义工具函数
    def parse_text(text: str):
        return {"parsed": text}
    
    def validate_data(data: dict):
        return True
    
    # 注册工具
    agent.register_tool(parse_text)
    agent.register_tool(validate_data)
    
    # 验证注册
    tools = agent.get_tools()
    assert len(tools) == 2
    assert parse_text in tools
    assert validate_data in tools
    
    print("✓ 工具注册成功")
    print(f"  - 已注册工具数: {len(tools)}")
    print(f"  - 工具名称: {[tool.__name__ for tool in tools]}")
    
    # 注销工具
    agent.unregister_tool(parse_text)
    tools = agent.get_tools()
    assert len(tools) == 1
    assert parse_text not in tools
    
    print("✓ 工具注销成功")


async def test_agent_info():
    """测试7: Agent信息获取"""
    print("\n=== 测试7: Agent信息获取 ===")
    
    server = MockMCPServer()
    
    agent = MCPAgent(
        agent_id="test_agent_007",
        agent_type="parser",
        mcp_server=server,
        metadata={"version": "2.0"}
    )
    
    await agent.start()
    
    # 注册一些处理器和工具
    async def handler(msg):
        pass
    
    def tool():
        pass
    
    agent.register_handler("test_action", handler)
    agent.register_tool(tool)
    
    # 获取信息
    info = agent.get_info()
    
    assert info["agent_id"] == "test_agent_007"
    assert info["agent_type"] == "parser"
    assert info["is_running"] is True
    assert "test_action" in info["registered_actions"]
    assert "tool" in info["registered_tools"]
    
    print("✓ Agent信息获取成功")
    print(f"  - Agent ID: {info['agent_id']}")
    print(f"  - Agent Type: {info['agent_type']}")
    print(f"  - 运行状态: {info['is_running']}")
    print(f"  - 已注册操作: {info['registered_actions']}")
    print(f"  - 已注册工具: {info['registered_tools']}")
    
    await agent.stop()


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("MCPAgent基类实现验证")
    print("=" * 60)
    
    try:
        await test_agent_initialization()
        await test_agent_registration()
        await test_message_handler_registration()
        await test_request_response_pattern()
        await test_notification_sending()
        await test_tool_registration()
        await test_agent_info()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n实现的功能:")
        print("  1. ✓ Agent注册和消息订阅")
        print("  2. ✓ 消息处理器注册机制")
        print("  3. ✓ 请求-响应模式")
        print("  4. ✓ 通知消息发送")
        print("  5. ✓ 工具注册管理")
        print("  6. ✓ Agent信息查询")
        print("  7. ✓ 生命周期管理（启动/停止）")
        print("\n任务3.3已完成！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
