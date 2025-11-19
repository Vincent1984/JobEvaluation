"""测试增强的DataManagerAgent - 企业和标签管理功能"""

import asyncio
import uuid
from datetime import datetime

from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.agents.data_manager_agent import DataManagerAgent
from src.core.database import init_db, get_db


async def test_company_management():
    """测试企业管理功能"""
    print("\n=== 测试企业管理功能 ===")
    
    # 初始化数据库
    init_db()
    
    # 创建MCP Server
    mcp_server = MCPServer()
    await mcp_server.start()
    
    # 创建DataManagerAgent
    agent = DataManagerAgent(mcp_server=mcp_server)
    await agent.start()
    
    # 测试1: 创建企业
    print("\n1. 创建企业...")
    company_data = {
        "name": "测试科技公司"
    }
    
    create_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_company",
        payload=company_data,
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_company(create_msg)
    
    # 等待响应
    await asyncio.sleep(0.5)
    
    # 测试2: 获取所有企业
    print("\n2. 获取所有企业...")
    get_all_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="get_all_companies",
        payload={},
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_get_all_companies(get_all_msg)
    
    await asyncio.sleep(0.5)
    
    print("\n✓ 企业管理功能测试完成")


async def test_category_tag_management():
    """测试分类标签管理功能"""
    print("\n=== 测试分类标签管理功能 ===")
    
    # 初始化数据库
    init_db()
    
    # 创建MCP Server
    mcp_server = MCPServer()
    await mcp_server.start()
    
    # 创建DataManagerAgent
    agent = DataManagerAgent(mcp_server=mcp_server)
    await agent.start()
    
    # 首先创建企业和分类（需要第三层级分类才能添加标签）
    print("\n1. 创建企业...")
    company_id = str(uuid.uuid4())
    company_data = {
        "id": company_id,
        "name": "标签测试公司"
    }
    
    create_company_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_company",
        payload=company_data,
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_company(create_company_msg)
    await asyncio.sleep(0.5)
    
    # 创建第一层级分类
    print("\n2. 创建第一层级分类...")
    cat1_id = str(uuid.uuid4())
    cat1_data = {
        "id": cat1_id,
        "company_id": company_id,
        "name": "技术类",
        "level": 1,
        "description": "技术相关职位"
    }
    
    create_cat1_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_category",
        payload=cat1_data,
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_category(create_cat1_msg)
    await asyncio.sleep(0.5)
    
    # 创建第二层级分类
    print("\n3. 创建第二层级分类...")
    cat2_id = str(uuid.uuid4())
    cat2_data = {
        "id": cat2_id,
        "company_id": company_id,
        "name": "研发",
        "level": 2,
        "parent_id": cat1_id,
        "description": "研发相关职位"
    }
    
    create_cat2_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_category",
        payload=cat2_data,
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_category(create_cat2_msg)
    await asyncio.sleep(0.5)
    
    # 创建第三层级分类
    print("\n4. 创建第三层级分类...")
    cat3_id = str(uuid.uuid4())
    cat3_data = {
        "id": cat3_id,
        "company_id": company_id,
        "name": "后端工程师",
        "level": 3,
        "parent_id": cat2_id,
        "description": "后端开发职位"
    }
    
    create_cat3_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_category",
        payload=cat3_data,
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_category(create_cat3_msg)
    await asyncio.sleep(0.5)
    
    # 测试添加标签到第三层级分类
    print("\n5. 为第三层级分类添加标签...")
    tag_data = {
        "category_id": cat3_id,
        "name": "高战略重要性",
        "tag_type": "战略重要性",
        "description": "该岗位对企业战略目标实现具有重要影响"
    }
    
    create_tag_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_category_tag",
        payload=tag_data,
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_category_tag(create_tag_msg)
    await asyncio.sleep(0.5)
    
    # 测试获取分类标签
    print("\n6. 获取分类的所有标签...")
    get_tags_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="get_category_tags",
        payload={"category_id": cat3_id},
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_get_category_tags(get_tags_msg)
    await asyncio.sleep(0.5)
    
    # 测试获取企业分类树
    print("\n7. 获取企业分类树...")
    get_tree_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="get_company_categories",
        payload={"company_id": company_id},
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_get_company_categories(get_tree_msg)
    await asyncio.sleep(0.5)
    
    print("\n✓ 分类标签管理功能测试完成")


async def test_evaluation_manual_modification():
    """测试评估结果手动修改功能"""
    print("\n=== 测试评估结果手动修改功能 ===")
    
    # 初始化数据库
    init_db()
    
    # 创建MCP Server
    mcp_server = MCPServer()
    await mcp_server.start()
    
    # 创建DataManagerAgent
    agent = DataManagerAgent(mcp_server=mcp_server)
    await agent.start()
    
    # 创建一个JD用于测试
    jd_id = str(uuid.uuid4())
    
    # 测试1: 保存初始评估结果
    print("\n1. 保存初始评估结果...")
    evaluation_data = {
        "model_type": "standard",
        "overall_score": 75.0,
        "completeness": 80.0,
        "clarity": 70.0,
        "professionalism": 75.0,
        "issues": ["职责描述不够清晰"],
        "company_value": "中价值",
        "is_core_position": False,
        "dimension_contributions": {
            "jd_content": 40,
            "evaluation_template": 30,
            "category_tags": 30
        },
        "is_manually_modified": False,
        "manual_modifications": [],
        "recommendations": ["建议补充具体的工作职责"]
    }
    
    save_eval_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_evaluation",
        payload={
            "jd_id": jd_id,
            "evaluation": evaluation_data
        },
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_evaluation(save_eval_msg)
    await asyncio.sleep(0.5)
    
    # 测试2: 获取评估结果
    print("\n2. 获取评估结果...")
    get_eval_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="get_evaluation",
        payload={"jd_id": jd_id},
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_get_evaluation(get_eval_msg)
    await asyncio.sleep(0.5)
    
    # 测试3: 更新评估结果（模拟手动修改）
    print("\n3. 更新评估结果（手动修改）...")
    updated_evaluation = {
        "model_type": "standard",
        "overall_score": 85.0,  # 手动提高分数
        "completeness": 80.0,
        "clarity": 70.0,
        "professionalism": 75.0,
        "issues": ["职责描述不够清晰"],
        "company_value": "高价值",  # 手动修改为高价值
        "is_core_position": True,  # 手动标记为核心岗位
        "dimension_contributions": {
            "jd_content": 40,
            "evaluation_template": 30,
            "category_tags": 30
        },
        "is_manually_modified": True,
        "manual_modifications": [
            {
                "timestamp": datetime.now().timestamp(),
                "modified_fields": {
                    "overall_score": 85.0,
                    "company_value": "高价值",
                    "is_core_position": True
                },
                "reason": "经过人工审核，该岗位对公司战略更重要",
                "original_values": {
                    "overall_score": 75.0,
                    "company_value": "中价值",
                    "is_core_position": False
                }
            }
        ],
        "recommendations": ["建议补充具体的工作职责"]
    }
    
    update_eval_msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="save_evaluation",
        payload={
            "jd_id": jd_id,
            "evaluation": updated_evaluation
        },
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_save_evaluation(update_eval_msg)
    await asyncio.sleep(0.5)
    
    # 测试4: 再次获取评估结果，验证修改已保存
    print("\n4. 验证修改已保存...")
    get_eval_msg2 = MCPMessage(
        message_id=str(uuid.uuid4()),
        sender="test",
        receiver="data_manager",
        message_type="request",
        action="get_evaluation",
        payload={"jd_id": jd_id},
        timestamp=datetime.now().timestamp()
    )
    
    await agent.handle_get_evaluation(get_eval_msg2)
    await asyncio.sleep(0.5)
    
    print("\n✓ 评估结果手动修改功能测试完成")


async def main():
    """运行所有测试"""
    print("开始测试增强的DataManagerAgent功能...")
    
    try:
        await test_company_management()
        await test_category_tag_management()
        await test_evaluation_manual_modification()
        
        print("\n" + "="*50)
        print("所有测试完成！")
        print("="*50)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
