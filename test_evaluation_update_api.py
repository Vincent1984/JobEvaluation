"""测试评估结果手动修改API端点"""

import asyncio
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, '.')

from src.models.schemas import (
    JobDescription,
    EvaluationResult,
    QualityScore,
    ManualModification,
    DimensionContribution,
    EvaluationModel
)
from src.agents.data_manager_agent import DataManagerAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.llm_client import DeepSeekR1Client


async def test_evaluation_update():
    """测试评估结果手动修改功能"""
    
    print("=" * 60)
    print("测试评估结果手动修改API功能")
    print("=" * 60)
    
    # 1. 初始化MCP Server和Agents
    print("\n1. 初始化MCP Server和Agents...")
    mcp_server = MCPServer()
    await mcp_server.start()
    
    llm_client = DeepSeekR1Client()
    
    data_agent = DataManagerAgent(
        agent_id="data_manager",
        mcp_server=mcp_server,
        db=None
    )
    await data_agent.start()
    
    evaluator_agent = EvaluatorAgent(
        agent_id="evaluator",
        mcp_server=mcp_server,
        llm_client=llm_client
    )
    await evaluator_agent.start()
    
    print("✓ MCP Server和Agents初始化完成")
    
    # 2. 创建测试JD
    print("\n2. 创建测试JD...")
    test_jd = JobDescription(
        id="test_jd_001",
        job_title="高级Python工程师",
        department="技术部",
        location="北京",
        responsibilities=["开发后端服务", "优化系统性能"],
        required_skills=["Python", "FastAPI", "SQL"],
        preferred_skills=["Docker", "K8s"],
        qualifications=["本科及以上", "3年以上经验"],
        raw_text="招聘高级Python工程师...",
        category_level3_id="cat_backend_003"
    )
    
    # 保存JD
    save_jd_msg = MCPMessage(
        message_id="msg_save_jd",
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_jd",
        payload=test_jd.model_dump(),
        timestamp=datetime.now().timestamp()
    )
    
    await mcp_server.route_message(save_jd_msg)
    await asyncio.sleep(0.5)
    
    print(f"✓ 测试JD已创建: {test_jd.job_title}")
    
    # 3. 创建初始评估结果
    print("\n3. 创建初始评估结果...")
    initial_evaluation = EvaluationResult(
        id="eval_001",
        jd_id="test_jd_001",
        model_type=EvaluationModel.STANDARD,
        quality_score=QualityScore(
            overall_score=85.0,
            completeness=90.0,
            clarity=80.0,
            professionalism=85.0,
            issues=[]
        ),
        recommendations=["建议补充薪资范围"],
        overall_score=85.0,
        company_value="中价值",
        is_core_position=False,
        dimension_contributions=DimensionContribution(
            jd_content=40.0,
            evaluation_template=30.0,
            category_tags=30.0
        ),
        is_manually_modified=False,
        manual_modifications=[]
    )
    
    # 保存评估结果
    save_eval_msg = MCPMessage(
        message_id="msg_save_eval",
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_evaluation",
        payload={
            "jd_id": "test_jd_001",
            "evaluation": initial_evaluation.model_dump()
        },
        timestamp=datetime.now().timestamp()
    )
    
    await mcp_server.route_message(save_eval_msg)
    await asyncio.sleep(0.5)
    
    print(f"✓ 初始评估结果已创建:")
    print(f"  - 综合分数: {initial_evaluation.overall_score}")
    print(f"  - 企业价值: {initial_evaluation.company_value}")
    print(f"  - 核心岗位: {initial_evaluation.is_core_position}")
    print(f"  - 手动修改: {initial_evaluation.is_manually_modified}")
    
    # 4. 测试手动修改评估结果
    print("\n4. 测试手动修改评估结果...")
    
    modifications = {
        "overall_score": 92.0,
        "company_value": "高价值",
        "is_core_position": True
    }
    
    update_msg = MCPMessage(
        message_id="msg_update_eval",
        sender="test",
        receiver="evaluator",
        message_type="request",
        action="update_evaluation",
        payload={
            "jd_id": "test_jd_001",
            "modifications": modifications,
            "reason": "根据业务需求和市场情况调整评分"
        },
        timestamp=datetime.now().timestamp()
    )
    
    await mcp_server.route_message(update_msg)
    await asyncio.sleep(1.0)
    
    print("✓ 修改请求已发送")
    
    # 5. 获取更新后的评估结果
    print("\n5. 获取更新后的评估结果...")
    
    get_eval_msg = MCPMessage(
        message_id="msg_get_eval",
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="get_evaluation",
        payload={"jd_id": "test_jd_001"},
        timestamp=datetime.now().timestamp()
    )
    
    await mcp_server.route_message(get_eval_msg)
    await asyncio.sleep(0.5)
    
    # 从响应队列获取结果
    response = await mcp_server.get_response("msg_get_eval", timeout=2.0)
    
    if response and response.payload.get("success"):
        updated_eval = response.payload.get("evaluation")
        
        print("✓ 更新后的评估结果:")
        print(f"  - 综合分数: {updated_eval['overall_score']} (原: 85.0)")
        print(f"  - 企业价值: {updated_eval['company_value']} (原: 中价值)")
        print(f"  - 核心岗位: {updated_eval['is_core_position']} (原: False)")
        print(f"  - 手动修改: {updated_eval['is_manually_modified']}")
        print(f"  - 修改历史记录数: {len(updated_eval.get('manual_modifications', []))}")
        
        # 6. 验证修改历史
        if updated_eval.get('manual_modifications'):
            print("\n6. 修改历史记录:")
            for idx, mod in enumerate(updated_eval['manual_modifications'], 1):
                print(f"\n  修改 #{idx}:")
                print(f"    - 时间: {mod.get('timestamp')}")
                print(f"    - 修改字段: {mod.get('modified_fields')}")
                print(f"    - 原始值: {mod.get('original_values')}")
                print(f"    - 原因: {mod.get('reason')}")
        
        # 7. 验证字段值
        print("\n7. 验证修改结果:")
        assert updated_eval['overall_score'] == 92.0, "综合分数未正确更新"
        assert updated_eval['company_value'] == "高价值", "企业价值未正确更新"
        assert updated_eval['is_core_position'] == True, "核心岗位标识未正确更新"
        assert updated_eval['is_manually_modified'] == True, "手动修改标识未设置"
        assert len(updated_eval.get('manual_modifications', [])) > 0, "修改历史未记录"
        
        print("✓ 所有验证通过!")
        
    else:
        print("✗ 获取更新后的评估结果失败")
        return False
    
    # 8. 测试第二次修改
    print("\n8. 测试第二次修改...")
    
    second_modifications = {
        "overall_score": 95.0
    }
    
    update_msg2 = MCPMessage(
        message_id="msg_update_eval_2",
        sender="test",
        receiver="evaluator",
        message_type="request",
        action="update_evaluation",
        payload={
            "jd_id": "test_jd_001",
            "modifications": second_modifications,
            "reason": "进一步提升评分"
        },
        timestamp=datetime.now().timestamp()
    )
    
    await mcp_server.route_message(update_msg2)
    await asyncio.sleep(1.0)
    
    # 获取最终结果
    get_eval_msg2 = MCPMessage(
        message_id="msg_get_eval_2",
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="get_evaluation",
        payload={"jd_id": "test_jd_001"},
        timestamp=datetime.now().timestamp()
    )
    
    await mcp_server.route_message(get_eval_msg2)
    await asyncio.sleep(0.5)
    
    response2 = await mcp_server.get_response("msg_get_eval_2", timeout=2.0)
    
    if response2 and response2.payload.get("success"):
        final_eval = response2.payload.get("evaluation")
        
        print("✓ 第二次修改后的结果:")
        print(f"  - 综合分数: {final_eval['overall_score']}")
        print(f"  - 修改历史记录数: {len(final_eval.get('manual_modifications', []))}")
        
        assert final_eval['overall_score'] == 95.0, "第二次修改未生效"
        assert len(final_eval.get('manual_modifications', [])) == 2, "应该有2条修改历史"
        
        print("✓ 第二次修改验证通过!")
    
    # 停止服务
    await mcp_server.stop()
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_evaluation_update())
        if result:
            print("\n测试成功完成!")
            sys.exit(0)
        else:
            print("\n测试失败!")
            sys.exit(1)
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
