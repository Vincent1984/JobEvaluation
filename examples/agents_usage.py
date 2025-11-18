"""Agent使用示例"""

import asyncio
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
    """启动所有Agent"""
    print("=" * 60)
    print("启动JD分析器Agent系统")
    print("=" * 60)
    
    # 1. 创建MCP服务器
    print("\n[1/3] 创建MCP服务器...")
    mcp_server = await create_mcp_server(
        redis_host="localhost",
        redis_port=6379,
        redis_db=0,
        auto_start=True
    )
    print("✓ MCP服务器已启动")
    
    # 2. 创建LLM客户端
    print("\n[2/3] 创建LLM客户端...")
    llm_client = DeepSeekR1Client()
    print("✓ LLM客户端已创建")
    
    # 3. 创建并启动所有Agent
    print("\n[3/3] 启动所有Agent...")
    agents = []
    
    # 数据管理Agent（不需要LLM）
    print("  - 启动DataManagerAgent...")
    data_manager = await create_data_manager_agent(mcp_server)
    agents.append(data_manager)
    
    # 需要LLM的Agent
    print("  - 启动ParserAgent...")
    parser = await create_parser_agent(mcp_server, llm_client)
    agents.append(parser)
    
    print("  - 启动EvaluatorAgent...")
    evaluator = await create_evaluator_agent(mcp_server, llm_client)
    agents.append(evaluator)
    
    print("  - 启动OptimizerAgent...")
    optimizer = await create_optimizer_agent(mcp_server, llm_client)
    agents.append(optimizer)
    
    print("  - 启动QuestionnaireAgent...")
    questionnaire = await create_questionnaire_agent(mcp_server, llm_client)
    agents.append(questionnaire)
    
    print("  - 启动MatcherAgent...")
    matcher = await create_matcher_agent(mcp_server, llm_client)
    agents.append(matcher)
    
    # 批量上传Agent（不需要LLM）
    print("  - 启动BatchUploadAgent...")
    batch_uploader = await create_batch_upload_agent(mcp_server)
    agents.append(batch_uploader)
    
    # 协调Agent（不需要LLM）
    print("  - 启动CoordinatorAgent...")
    coordinator = await create_coordinator_agent(mcp_server)
    agents.append(coordinator)
    
    # 报告生成Agent（不需要LLM）
    print("  - 启动ReportAgent...")
    reporter = await create_report_agent(mcp_server)
    agents.append(reporter)
    
    print(f"\n✓ 所有Agent已启动: {len(agents)}个")
    
    # 4. 显示Agent状态
    print("\n" + "=" * 60)
    print("Agent状态")
    print("=" * 60)
    for agent in agents:
        health = await agent.health_check()
        status = "✓" if health["status"] == "healthy" else "✗"
        print(f"{status} {agent.agent_id:20s} - {agent.agent_type:15s} - {health['status']}")
    
    return mcp_server, agents


async def example_jd_analysis(mcp_server):
    """示例：JD分析工作流"""
    print("\n" + "=" * 60)
    print("示例：JD分析工作流")
    print("=" * 60)
    
    from src.mcp.message import create_request_message
    
    # 示例JD文本
    jd_text = """
    职位名称：高级Python工程师
    
    岗位职责：
    1. 负责后端服务的设计和开发
    2. 参与系统架构设计和技术选型
    3. 编写高质量、可维护的代码
    4. 参与代码审查和技术分享
    
    任职要求：
    1. 本科及以上学历，计算机相关专业
    2. 3年以上Python开发经验
    3. 熟悉Django或Flask框架
    4. 熟悉MySQL、Redis等数据库
    5. 具有良好的团队协作能力
    """
    
    print("\n发送JD分析请求...")
    print(f"JD文本长度: {len(jd_text)}字符")
    
    # 创建请求消息
    message = create_request_message(
        sender="example_script",
        receiver="coordinator",
        action="analyze_jd",
        payload={
            "jd_text": jd_text,
            "evaluation_model": "standard"
        }
    )
    
    # 发送消息
    await mcp_server.send_message(message)
    
    print("✓ 请求已发送")
    print("\n注意：这是一个异步示例，实际应用中需要等待响应")
    print("完整的请求-响应流程需要通过Agent的send_request方法实现")


async def example_batch_upload(mcp_server):
    """示例：批量上传工作流"""
    print("\n" + "=" * 60)
    print("示例：批量上传工作流")
    print("=" * 60)
    
    print("\n批量上传功能支持：")
    print("  - 文件格式：TXT, PDF, DOCX, DOC")
    print("  - 单文件最大：10MB")
    print("  - 批量最多：20个文件")
    print("  - 总大小最多：100MB")
    
    print("\n使用方法：")
    print("  1. 准备JD文件（支持的格式）")
    print("  2. 通过API上传文件")
    print("  3. BatchUploadAgent自动处理")
    print("  4. 返回批量处理结果")


async def cleanup_agents(mcp_server, agents):
    """清理Agent"""
    print("\n" + "=" * 60)
    print("清理Agent")
    print("=" * 60)
    
    for agent in agents:
        print(f"停止 {agent.agent_id}...")
        await agent.stop()
    
    print("\n停止MCP服务器...")
    await mcp_server.stop()
    
    print("✓ 所有Agent已停止")


async def main():
    """主函数"""
    try:
        # 启动所有Agent
        mcp_server, agents = await start_all_agents()
        
        # 运行示例
        await example_jd_analysis(mcp_server)
        await example_batch_upload(mcp_server)
        
        # 等待一段时间（实际应用中Agent会持续运行）
        print("\n" + "=" * 60)
        print("Agent系统正在运行...")
        print("按Ctrl+C停止")
        print("=" * 60)
        
        # 保持运行
        await asyncio.sleep(10)
        
    except KeyboardInterrupt:
        print("\n\n收到停止信号...")
    
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        if 'mcp_server' in locals() and 'agents' in locals():
            await cleanup_agents(mcp_server, agents)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              JD分析器 - Agent系统示例                         ║
║                                                              ║
║  本示例演示如何启动和使用所有Agent                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
