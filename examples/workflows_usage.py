"""
工作流使用示例

演示如何使用JD分析工作流和问卷评估工作流
"""

import asyncio
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_jd_analysis():
    """示例1: JD完整分析工作流"""
    from src.mcp.server import MCPServer
    from src.workflows import JDAnalysisWorkflow
    from src.core.config import get_settings
    import redis.asyncio as redis
    
    logger.info("=" * 60)
    logger.info("示例1: JD完整分析工作流")
    logger.info("=" * 60)
    
    # 初始化Redis和MCP Server
    settings = get_settings()
    redis_client = redis.from_url(settings.redis_url)
    mcp_server = MCPServer(redis_client)
    
    # 创建工作流实例
    workflow = JDAnalysisWorkflow(mcp_server)
    
    # 准备JD文本
    jd_text = """
    职位名称：Python后端工程师
    
    岗位职责：
    1. 负责公司核心业务系统的后端开发和维护
    2. 参与系统架构设计和技术方案制定
    3. 编写高质量、可维护的代码
    4. 优化系统性能，提升用户体验
    
    任职要求：
    1. 本科及以上学历，计算机相关专业
    2. 3年以上Python开发经验
    3. 熟悉Django或FastAPI框架
    4. 熟悉MySQL、Redis等数据库
    5. 具有良好的团队协作能力
    """
    
    try:
        # 执行完整分析
        logger.info("开始执行JD分析...")
        result = await workflow.execute_full_analysis(
            jd_text=jd_text,
            evaluation_model="standard",
            timeout=300.0
        )
        
        if result["status"] == "completed":
            logger.info(f"✓ 分析完成！")
            logger.info(f"  - JD ID: {result['jd_id']}")
            logger.info(f"  - 工作流ID: {result['workflow_id']}")
            logger.info(f"  - 执行时间: {result['execution_time']:.2f}秒")
            
            # 显示解析结果
            parsed = result['parsed_data']
            logger.info(f"\n解析结果:")
            logger.info(f"  - 职位标题: {parsed.get('job_title', 'N/A')}")
            logger.info(f"  - 部门: {parsed.get('department', 'N/A')}")
            logger.info(f"  - 职责数量: {len(parsed.get('responsibilities', []))}")
            logger.info(f"  - 必备技能: {len(parsed.get('required_skills', []))}")
            
            # 显示评估结果
            evaluation = result['evaluation']
            quality_score = evaluation.get('quality_score', {})
            logger.info(f"\n质量评估:")
            logger.info(f"  - 综合分数: {quality_score.get('overall_score', 0):.1f}/100")
            logger.info(f"  - 完整性: {quality_score.get('completeness', 0):.1f}/100")
            logger.info(f"  - 清晰度: {quality_score.get('clarity', 0):.1f}/100")
            logger.info(f"  - 专业性: {quality_score.get('professionalism', 0):.1f}/100")
            
            # 显示优化建议
            suggestions = result['suggestions']
            logger.info(f"\n优化建议:")
            for idx, suggestion in enumerate(suggestions.get('recommendations', [])[:3], 1):
                logger.info(f"  {idx}. {suggestion}")
        else:
            logger.error(f"✗ 分析失败: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"执行异常: {str(e)}", exc_info=True)
    
    finally:
        await redis_client.close()


async def example_questionnaire_generation():
    """示例2: 生成评估问卷"""
    from src.mcp.server import MCPServer
    from src.workflows import QuestionnaireWorkflow
    from src.core.config import get_settings
    import redis.asyncio as redis
    
    logger.info("\n" + "=" * 60)
    logger.info("示例2: 生成评估问卷")
    logger.info("=" * 60)
    
    # 初始化
    settings = get_settings()
    redis_client = redis.from_url(settings.redis_url)
    mcp_server = MCPServer(redis_client)
    
    # 创建工作流实例
    workflow = QuestionnaireWorkflow(mcp_server)
    
    try:
        # 生成问卷（假设已有JD ID）
        jd_id = "jd_example_123"
        
        logger.info(f"为JD {jd_id} 生成问卷...")
        result = await workflow.generate_questionnaire(
            jd_id=jd_id,
            evaluation_model="mercer_ipe",
            timeout=120.0
        )
        
        if result["status"] == "completed":
            logger.info(f"✓ 问卷生成完成！")
            logger.info(f"  - 问卷ID: {result['questionnaire_id']}")
            logger.info(f"  - 工作流ID: {result['workflow_id']}")
            logger.info(f"  - 执行时间: {result['execution_time']:.2f}秒")
            
            # 显示问卷信息
            questionnaire = result['questionnaire']
            logger.info(f"\n问卷信息:")
            logger.info(f"  - 标题: {questionnaire.get('title', 'N/A')}")
            logger.info(f"  - 题目数量: {len(questionnaire.get('questions', []))}")
            logger.info(f"  - 评估模型: {questionnaire.get('evaluation_model', 'N/A')}")
            
            # 显示前3个题目
            questions = questionnaire.get('questions', [])
            if questions:
                logger.info(f"\n前3个题目:")
                for idx, q in enumerate(questions[:3], 1):
                    logger.info(f"  {idx}. {q.get('question_text', 'N/A')}")
                    logger.info(f"     类型: {q.get('question_type', 'N/A')}")
                    logger.info(f"     维度: {q.get('dimension', 'N/A')}")
        else:
            logger.error(f"✗ 问卷生成失败: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"执行异常: {str(e)}", exc_info=True)
    
    finally:
        await redis_client.close()


async def example_single_candidate_evaluation():
    """示例3: 评估单个候选人"""
    from src.mcp.server import MCPServer
    from src.workflows import QuestionnaireWorkflow
    from src.core.config import get_settings
    import redis.asyncio as redis
    
    logger.info("\n" + "=" * 60)
    logger.info("示例3: 评估单个候选人")
    logger.info("=" * 60)
    
    # 初始化
    settings = get_settings()
    redis_client = redis.from_url(settings.redis_url)
    mcp_server = MCPServer(redis_client)
    
    # 创建工作流实例
    workflow = QuestionnaireWorkflow(mcp_server)
    
    try:
        # 准备数据
        jd_id = "jd_example_123"
        questionnaire_id = "quest_example_456"
        
        # 候选人回答
        responses = {
            "q1": "5年",  # 工作年限
            "q2": ["Python", "Django", "FastAPI", "MySQL"],  # 技能
            "q3": 8,  # 自评分数（1-10）
            "q4": "有丰富的后端开发经验，参与过多个大型项目..."  # 开放题
        }
        
        logger.info(f"评估候选人: 张三")
        result = await workflow.evaluate_match(
            jd_id=jd_id,
            questionnaire_id=questionnaire_id,
            responses=responses,
            respondent_name="张三",
            timeout=120.0
        )
        
        if result["status"] == "completed":
            logger.info(f"✓ 评估完成！")
            logger.info(f"  - 匹配ID: {result['match_id']}")
            logger.info(f"  - 执行时间: {result['execution_time']:.2f}秒")
            
            # 显示匹配结果
            match_result = result['match_result']
            logger.info(f"\n匹配结果:")
            logger.info(f"  - 综合匹配度: {match_result.get('overall_score', 0):.1f}/100")
            
            # 维度得分
            dimension_scores = match_result.get('dimension_scores', {})
            if dimension_scores:
                logger.info(f"\n各维度得分:")
                for dimension, score in dimension_scores.items():
                    logger.info(f"  - {dimension}: {score:.1f}/100")
            
            # 优势
            strengths = match_result.get('strengths', [])
            if strengths:
                logger.info(f"\n优势:")
                for idx, strength in enumerate(strengths[:3], 1):
                    logger.info(f"  {idx}. {strength}")
            
            # 差距
            gaps = match_result.get('gaps', [])
            if gaps:
                logger.info(f"\n差距:")
                for idx, gap in enumerate(gaps[:3], 1):
                    logger.info(f"  {idx}. {gap}")
        else:
            logger.error(f"✗ 评估失败: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"执行异常: {str(e)}", exc_info=True)
    
    finally:
        await redis_client.close()


async def example_batch_candidate_evaluation():
    """示例4: 批量评估候选人"""
    from src.mcp.server import MCPServer
    from src.workflows import QuestionnaireWorkflow
    from src.core.config import get_settings
    import redis.asyncio as redis
    
    logger.info("\n" + "=" * 60)
    logger.info("示例4: 批量评估候选人")
    logger.info("=" * 60)
    
    # 初始化
    settings = get_settings()
    redis_client = redis.from_url(settings.redis_url)
    mcp_server = MCPServer(redis_client)
    
    # 创建工作流实例
    workflow = QuestionnaireWorkflow(mcp_server)
    
    try:
        # 准备数据
        jd_id = "jd_example_123"
        questionnaire_id = "quest_example_456"
        
        # 多个候选人的回答
        candidate_responses = [
            {
                "respondent_name": "张三",
                "responses": {
                    "q1": "5年",
                    "q2": ["Python", "Django", "FastAPI"],
                    "q3": 8
                }
            },
            {
                "respondent_name": "李四",
                "responses": {
                    "q1": "3年",
                    "q2": ["Python", "Flask"],
                    "q3": 7
                }
            },
            {
                "respondent_name": "王五",
                "responses": {
                    "q1": "7年",
                    "q2": ["Python", "Django", "FastAPI", "Redis"],
                    "q3": 9
                }
            },
            {
                "respondent_name": "赵六",
                "responses": {
                    "q1": "2年",
                    "q2": ["Python"],
                    "q3": 6
                }
            }
        ]
        
        logger.info(f"批量评估 {len(candidate_responses)} 个候选人...")
        result = await workflow.batch_evaluate_candidates(
            jd_id=jd_id,
            questionnaire_id=questionnaire_id,
            candidate_responses=candidate_responses,
            timeout=300.0
        )
        
        if result["status"] == "completed":
            logger.info(f"✓ 批量评估完成！")
            logger.info(f"  - 批量ID: {result['batch_id']}")
            logger.info(f"  - 总计: {result['total']}")
            logger.info(f"  - 成功: {result['successful']}")
            logger.info(f"  - 失败: {result['failed']}")
            logger.info(f"  - 执行时间: {result['execution_time']:.2f}秒")
            
            # 按匹配度排序
            results = result['results']
            sorted_results = sorted(
                results,
                key=lambda x: x['match_result']['overall_score'],
                reverse=True
            )
            
            logger.info(f"\n候选人排名（按匹配度）:")
            for idx, candidate in enumerate(sorted_results, 1):
                name = candidate['respondent_name']
                score = candidate['match_result']['overall_score']
                logger.info(f"  {idx}. {name}: {score:.1f}/100")
            
            # 显示失败的候选人
            if result['failed_candidates']:
                logger.info(f"\n失败的候选人:")
                for candidate in result['failed_candidates']:
                    logger.info(f"  - {candidate['respondent_name']}: {candidate['error']}")
        else:
            logger.error(f"✗ 批量评估失败: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"执行异常: {str(e)}", exc_info=True)
    
    finally:
        await redis_client.close()


async def example_workflow_status_tracking():
    """示例5: 工作流状态追踪"""
    from src.mcp.server import MCPServer
    from src.workflows import JDAnalysisWorkflow, QuestionnaireWorkflow
    from src.core.config import get_settings
    import redis.asyncio as redis
    
    logger.info("\n" + "=" * 60)
    logger.info("示例5: 工作流状态追踪")
    logger.info("=" * 60)
    
    # 初始化
    settings = get_settings()
    redis_client = redis.from_url(settings.redis_url)
    mcp_server = MCPServer(redis_client)
    
    # 创建工作流实例
    jd_workflow = JDAnalysisWorkflow(mcp_server)
    quest_workflow = QuestionnaireWorkflow(mcp_server)
    
    try:
        # 假设有一个正在运行的工作流
        workflow_id = "workflow_example_789"
        
        # 查询JD分析工作流状态
        logger.info(f"查询工作流状态: {workflow_id}")
        status = await jd_workflow.get_workflow_status(workflow_id)
        
        if status:
            logger.info(f"✓ 工作流状态:")
            logger.info(f"  - 工作流ID: {status['workflow_id']}")
            logger.info(f"  - 状态: {status['status']}")
            logger.info(f"  - 当前步骤: {status['step']}")
            logger.info(f"  - JD ID: {status.get('jd_id', 'N/A')}")
            
            if status.get('error'):
                logger.info(f"  - 错误: {status['error']}")
        else:
            logger.info(f"工作流不存在或已过期")
        
        # 查询批量评估状态
        batch_id = "batch_example_101"
        logger.info(f"\n查询批量评估状态: {batch_id}")
        status = await quest_workflow.get_workflow_status(batch_id)
        
        if status and status.get('workflow_type') == 'batch_evaluation':
            logger.info(f"✓ 批量评估状态:")
            logger.info(f"  - 批量ID: {status['workflow_id']}")
            logger.info(f"  - 状态: {status['status']}")
            logger.info(f"  - 总计: {status['total_candidates']}")
            logger.info(f"  - 已处理: {status['processed_candidates']}")
            logger.info(f"  - 成功: {status['successful_candidates']}")
            logger.info(f"  - 失败: {status['failed_candidates']}")
            
            # 计算进度
            if status['total_candidates'] > 0:
                progress = (status['processed_candidates'] / status['total_candidates']) * 100
                logger.info(f"  - 进度: {progress:.1f}%")
    
    except Exception as e:
        logger.error(f"执行异常: {str(e)}", exc_info=True)
    
    finally:
        await redis_client.close()


async def main():
    """运行所有示例"""
    logger.info("工作流使用示例")
    logger.info("=" * 60)
    
    # 运行示例（根据需要注释/取消注释）
    
    # 示例1: JD完整分析
    await example_jd_analysis()
    
    # 示例2: 生成问卷
    # await example_questionnaire_generation()
    
    # 示例3: 评估单个候选人
    # await example_single_candidate_evaluation()
    
    # 示例4: 批量评估候选人
    # await example_batch_candidate_evaluation()
    
    # 示例5: 工作流状态追踪
    # await example_workflow_status_tracking()
    
    logger.info("\n" + "=" * 60)
    logger.info("所有示例执行完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
