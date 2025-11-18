"""测试MCP Server实现"""

import asyncio
import sys
from src.mcp import MCPServer, create_mcp_server
from src.mcp.message import create_request_message, create_notification_message
from src.mcp.context import create_context


async def test_mcp_server():
    """测试MCP Server基本功能"""
    
    print("=" * 60)
    print("测试 MCP Server 实现")
    print("=" * 60)
    
    # 测试1: 创建和连接服务器
    print("\n[测试1] 创建和连接MCP服务器...")
    try:
        server = MCPServer(
            redis_host="localhost",
            redis_port=6379,
            redis_db=0
        )
        await server.connect()
        print("✓ 成功连接到Redis")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print("\n提示: 请确保Redis服务器正在运行")
        print("  - Windows: 下载并运行Redis")
        print("  - Linux/Mac: sudo service redis-server start")
        return
    
    # 测试2: 启动服务器
    print("\n[测试2] 启动MCP服务器...")
    try:
        await server.start()
        print("✓ MCP服务器已启动")
    except Exception as e:
        print(f"✗ 启动失败: {e}")
        await server.disconnect()
        return
    
    # 测试3: 注册Agent
    print("\n[测试3] 注册Agent...")
    try:
        await server.register_agent(
            agent_id="test_parser",
            agent_type="parser",
            metadata={"version": "1.0"}
        )
        await server.register_agent(
            agent_id="test_evaluator",
            agent_type="evaluator",
            metadata={"version": "1.0"}
        )
        print("✓ 成功注册2个Agent")
        
        # 验证注册
        is_registered = await server.is_agent_registered("test_parser")
        print(f"✓ test_parser 注册状态: {is_registered}")
        
        agents = await server.get_registered_agents()
        print(f"✓ 已注册的Agent数量: {len(agents)}")
        print(f"  Agent列表: {list(agents)}")
    except Exception as e:
        print(f"✗ 注册失败: {e}")
    
    # 测试4: 上下文管理
    print("\n[测试4] 上下文管理...")
    try:
        # 创建上下文
        context = create_context(
            task_id="test_task_001",
            workflow_type="jd_analysis",
            shared_data={"jd_text": "测试职位描述"},
            metadata={"priority": "high"},
            expiration_seconds=3600
        )
        print(f"✓ 创建上下文: {context.context_id}")
        
        # 保存上下文
        await server.save_context(context)
        print("✓ 上下文已保存到Redis")
        
        # 获取上下文
        retrieved_context = await server.get_context(context.context_id)
        if retrieved_context:
            print(f"✓ 成功获取上下文: {retrieved_context.context_id}")
            print(f"  任务ID: {retrieved_context.task_id}")
            print(f"  工作流类型: {retrieved_context.workflow_type}")
            print(f"  共享数据: {retrieved_context.shared_data}")
        else:
            print("✗ 获取上下文失败")
        
        # 更新上下文
        context.update_data("step1", "completed")
        context.add_participant("test_parser")
        await server.update_context(context)
        print("✓ 上下文已更新")
        
        # 再次获取验证更新
        updated_context = await server.get_context(context.context_id)
        if updated_context:
            print(f"✓ 验证更新: step1 = {updated_context.get_data('step1')}")
            print(f"  参与者: {updated_context.participants}")
        
        # 列出所有上下文
        context_ids = await server.list_contexts()
        print(f"✓ 当前上下文数量: {len(context_ids)}")
        
    except Exception as e:
        print(f"✗ 上下文管理失败: {e}")
    
    # 测试5: 消息发送
    print("\n[测试5] 消息发送...")
    try:
        # 创建请求消息
        request_msg = create_request_message(
            sender="test_coordinator",
            receiver="test_parser",
            action="parse_jd",
            payload={"jd_text": "测试职位描述"},
            context_id=context.context_id
        )
        print(f"✓ 创建请求消息: {request_msg.message_id}")
        
        # 发送消息
        await server.send_message(request_msg)
        print("✓ 消息已发送")
        
        # 创建广播消息
        broadcast_msg = create_notification_message(
            sender="test_coordinator",
            action="task_started",
            payload={"task_id": "test_task_001"}
        )
        print(f"✓ 创建广播消息: {broadcast_msg.message_id}")
        
        # 发送广播
        await server.send_message(broadcast_msg)
        print("✓ 广播消息已发送")
        
    except Exception as e:
        print(f"✗ 消息发送失败: {e}")
    
    # 测试6: 健康检查
    print("\n[测试6] 健康检查...")
    try:
        health = await server.health_check()
        print(f"✓ 服务器状态: {health['status']}")
        print(f"  Redis连接: {health['redis_connected']}")
        print(f"  运行状态: {health['is_running']}")
        print(f"  注册Agent数: {health['registered_agents']}")
        print(f"  活动上下文数: {health['active_contexts']}")
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
    
    # 测试7: 统计信息
    print("\n[测试7] 获取统计信息...")
    try:
        stats = await server.get_stats()
        if "error" not in stats:
            print(f"✓ Redis版本: {stats.get('redis_version')}")
            print(f"  已注册Agent: {stats.get('registered_agents')}")
            print(f"  活动上下文: {stats.get('active_contexts')}")
            print(f"  Agent列表: {stats.get('agent_ids')}")
        else:
            print(f"✗ 获取统计失败: {stats['error']}")
    except Exception as e:
        print(f"✗ 获取统计失败: {e}")
    
    # 测试8: 清理
    print("\n[测试8] 清理资源...")
    try:
        # 删除上下文
        await server.delete_context(context.context_id)
        print("✓ 上下文已删除")
        
        # 注销Agent
        await server.unregister_agent("test_parser")
        await server.unregister_agent("test_evaluator")
        print("✓ Agent已注销")
        
        # 停止服务器
        await server.stop()
        print("✓ MCP服务器已停止")
        
    except Exception as e:
        print(f"✗ 清理失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


async def test_convenience_function():
    """测试便捷函数"""
    
    print("\n" + "=" * 60)
    print("测试便捷函数 create_mcp_server")
    print("=" * 60)
    
    try:
        # 使用便捷函数创建服务器
        server = await create_mcp_server(
            redis_host="localhost",
            redis_port=6379,
            redis_db=0,
            auto_start=True
        )
        print("✓ 使用便捷函数成功创建并启动服务器")
        
        # 验证服务器状态
        health = await server.health_check()
        print(f"✓ 服务器状态: {health['status']}")
        
        # 停止服务器
        await server.stop()
        print("✓ 服务器已停止")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        print("\n提示: 请确保Redis服务器正在运行")


if __name__ == "__main__":
    print("\nMCP Server 测试脚本")
    print("=" * 60)
    
    # 运行测试
    asyncio.run(test_mcp_server())
    
    # 测试便捷函数
    asyncio.run(test_convenience_function())
    
    print("\n所有测试完成!")
