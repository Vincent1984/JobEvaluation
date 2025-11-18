"""测试MCP消息协议实现"""

from src.mcp import MCPMessage, MessageType, MCPContext
from src.mcp.message import (
    create_request_message,
    create_notification_message,
    create_event_message
)
from src.mcp.context import create_context
import json


def test_mcp_message_creation():
    """测试消息创建"""
    print("测试1: 创建请求消息...")
    
    message = MCPMessage(
        sender="parser_agent",
        receiver="data_manager_agent",
        message_type=MessageType.REQUEST,
        action="save_jd",
        payload={"jd_id": "jd_001", "job_title": "Python工程师"},
        context_id="ctx_001"
    )
    
    assert message.sender == "parser_agent"
    assert message.receiver == "data_manager_agent"
    assert message.message_type == MessageType.REQUEST
    assert message.action == "save_jd"
    assert message.is_request()
    assert not message.is_broadcast()
    
    print("✓ 消息创建成功")
    print(f"  消息ID: {message.message_id}")
    print(f"  发送者: {message.sender}")
    print(f"  接收者: {message.receiver}")
    print(f"  操作: {message.action}")


def test_message_serialization():
    """测试消息序列化和反序列化"""
    print("\n测试2: 消息序列化...")
    
    original = create_request_message(
        sender="agent_a",
        receiver="agent_b",
        action="test_action",
        payload={"key": "value"},
        context_id="ctx_test"
    )
    
    # 序列化为JSON
    json_str = original.to_json()
    print(f"  JSON长度: {len(json_str)} 字符")
    
    # 反序列化
    restored = MCPMessage.from_json(json_str)
    
    assert restored.sender == original.sender
    assert restored.receiver == original.receiver
    assert restored.action == original.action
    assert restored.payload == original.payload
    
    print("✓ 序列化/反序列化成功")


def test_response_creation():
    """测试响应消息创建"""
    print("\n测试3: 创建响应消息...")
    
    request = create_request_message(
        sender="agent_a",
        receiver="agent_b",
        action="get_data",
        payload={"id": "123"}
    )
    
    response = request.create_response(
        payload={"data": "result"},
        sender="agent_b"
    )
    
    assert response.sender == "agent_b"
    assert response.receiver == "agent_a"
    assert response.message_type == MessageType.RESPONSE
    assert response.correlation_id == request.message_id
    assert response.is_response()
    
    print("✓ 响应消息创建成功")
    print(f"  原请求ID: {request.message_id}")
    print(f"  响应关联ID: {response.correlation_id}")


def test_broadcast_message():
    """测试广播消息"""
    print("\n测试4: 创建广播消息...")
    
    event = create_event_message(
        sender="coordinator",
        action="task_completed",
        payload={"task_id": "task_001"}
    )
    
    assert event.receiver is None
    assert event.is_broadcast()
    assert event.is_event()
    
    print("✓ 广播消息创建成功")


def test_mcp_context_creation():
    """测试上下文创建"""
    print("\n测试5: 创建MCP上下文...")
    
    context = MCPContext(
        task_id="task_001",
        workflow_type="jd_analysis",
        shared_data={"jd_text": "招聘Python工程师"},
        metadata={"priority": "high"}
    )
    
    assert context.task_id == "task_001"
    assert context.workflow_type == "jd_analysis"
    assert context.is_active()
    assert not context.is_completed()
    
    print("✓ 上下文创建成功")
    print(f"  上下文ID: {context.context_id}")
    print(f"  任务ID: {context.task_id}")
    print(f"  工作流类型: {context.workflow_type}")


def test_context_data_operations():
    """测试上下文数据操作"""
    print("\n测试6: 上下文数据操作...")
    
    context = create_context(
        task_id="task_002",
        workflow_type="test"
    )
    
    # 更新数据
    context.update_data("step1", "completed")
    context.update_data("jd_id", "jd_001")
    
    assert context.get_data("step1") == "completed"
    assert context.has_data("jd_id")
    assert not context.has_data("nonexistent")
    
    # 移除数据
    context.remove_data("step1")
    assert not context.has_data("step1")
    
    print("✓ 数据操作成功")


def test_context_participants():
    """测试上下文参与者管理"""
    print("\n测试7: 参与者管理...")
    
    context = create_context(task_id="task_003")
    
    # 添加参与者
    context.add_participant("parser_agent")
    context.add_participant("evaluator_agent")
    context.add_participant("parser_agent")  # 重复添加
    
    assert len(context.participants) == 2
    assert context.is_participant("parser_agent")
    assert context.is_participant("evaluator_agent")
    assert not context.is_participant("unknown_agent")
    
    # 移除参与者
    context.remove_participant("parser_agent")
    assert not context.is_participant("parser_agent")
    
    print("✓ 参与者管理成功")


def test_context_status():
    """测试上下文状态管理"""
    print("\n测试8: 状态管理...")
    
    context = create_context(task_id="task_004")
    
    assert context.is_active()
    
    context.update_status("completed")
    assert context.is_completed()
    assert not context.is_active()
    
    context.update_status("failed")
    assert context.is_failed()
    
    print("✓ 状态管理成功")


def test_context_serialization():
    """测试上下文序列化"""
    print("\n测试9: 上下文序列化...")
    
    original = create_context(
        task_id="task_005",
        workflow_type="jd_analysis",
        shared_data={"key": "value"},
        metadata={"creator": "test"}
    )
    
    # 序列化
    json_str = original.to_json()
    
    # 反序列化
    restored = MCPContext.from_json(json_str)
    
    assert restored.task_id == original.task_id
    assert restored.workflow_type == original.workflow_type
    assert restored.shared_data == original.shared_data
    assert restored.metadata == original.metadata
    
    print("✓ 上下文序列化成功")


def test_context_expiration():
    """测试上下文过期"""
    print("\n测试10: 上下文过期...")
    
    context = create_context(
        task_id="task_006",
        expiration_seconds=3600  # 1小时
    )
    
    assert context.expires_at is not None
    assert not context.is_expired()
    
    # 设置为已过期
    context.expires_at = 0
    assert context.is_expired()
    
    print("✓ 过期管理成功")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("MCP消息协议测试")
    print("=" * 60)
    
    try:
        test_mcp_message_creation()
        test_message_serialization()
        test_response_creation()
        test_broadcast_message()
        test_mcp_context_creation()
        test_context_data_operations()
        test_context_participants()
        test_context_status()
        test_context_serialization()
        test_context_expiration()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        raise


if __name__ == "__main__":
    main()
