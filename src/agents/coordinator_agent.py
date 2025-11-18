"""协调Agent - 任务编排和Agent协作"""

import logging
import uuid
from typing import Dict, Any, Optional

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.mcp.context import create_context

logger = logging.getLogger(__name__)


class CoordinatorAgent(MCPAgent):
    """协调Agent
    
    职责：
    - 任务分解和分配
    - 工作流编排
    - Agent间协作协调
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        agent_id: str = "coordinator",
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type="coordinator",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        # 注册消息处理器
        self.register_handler("analyze_jd", self.handle_analyze_jd)
        self.register_handler("generate_questionnaire", self.handle_generate_questionnaire)
        self.register_handler("evaluate_match", self.handle_evaluate_match)
        
        logger.info(f"CoordinatorAgent initialized: {agent_id}")
    
    async def handle_analyze_jd(self, message: MCPMessage) -> None:
        """处理JD分析请求（完整工作流）
        
        工作流：解析 -> 评估 -> 优化建议
        """
        jd_text = message.payload.get("jd_text")
        evaluation_model = message.payload.get("evaluation_model", "standard")
        custom_template = message.payload.get("custom_template")
        
        context_id = message.context_id or str(uuid.uuid4())
        
        logger.info(f"收到JD分析请求, context_id={context_id}")
        
        try:
            # 创建工作流上下文
            context = create_context(
                task_id=message.message_id,
                workflow_type="jd_analysis",
                shared_data={
                    "jd_text": jd_text,
                    "evaluation_model": evaluation_model,
                    "custom_template": custom_template
                },
                metadata={"workflow": "full_jd_analysis"},
                expiration_seconds=3600
            )
            context.context_id = context_id
            await self.update_context(context)
            
            # 1. 请求Parser Agent解析JD
            logger.info(f"步骤1: 解析JD, context_id={context_id}")
            parse_response = await self.send_request(
                receiver="parser",
                action="parse_jd",
                payload={
                    "jd_text": jd_text,
                    "custom_fields": custom_template or {}
                },
                context_id=context_id,
                timeout=90.0
            )
            
            if not parse_response.payload.get("success", True):
                raise Exception(f"JD解析失败: {parse_response.payload.get('error', '未知错误')}")
            
            jd_id = parse_response.payload["jd_id"]
            parsed_data = parse_response.payload["parsed_data"]
            
            # 更新上下文
            context.update_data("jd_id", jd_id)
            context.update_data("parsed_data", parsed_data)
            await self.update_context(context)
            
            # 2. 请求Evaluator Agent评估质量
            logger.info(f"步骤2: 评估质量, jd_id={jd_id}")
            eval_response = await self.send_request(
                receiver="evaluator",
                action="evaluate_quality",
                payload={
                    "jd_id": jd_id,
                    "model_type": evaluation_model
                },
                context_id=context_id,
                timeout=90.0
            )
            
            if not eval_response.payload.get("success", True):
                logger.warning(f"质量评估失败: {eval_response.payload.get('error', '未知错误')}")
                evaluation = {}
            else:
                evaluation = eval_response.payload.get("evaluation", {})
            
            # 更新上下文
            context.update_data("evaluation", evaluation)
            await self.update_context(context)
            
            # 3. 请求Optimizer Agent生成优化建议
            logger.info(f"步骤3: 生成优化建议, jd_id={jd_id}")
            opt_response = await self.send_request(
                receiver="optimizer",
                action="generate_suggestions",
                payload={"jd_id": jd_id},
                context_id=context_id,
                timeout=90.0
            )
            
            if not opt_response.payload.get("success", True):
                logger.warning(f"优化建议生成失败: {opt_response.payload.get('error', '未知错误')}")
                suggestions = {}
            else:
                suggestions = opt_response.payload.get("suggestions", {})
            
            # 更新上下文
            context.update_data("suggestions", suggestions)
            context.update_status("completed")
            await self.update_context(context)
            
            # 4. 汇总结果
            result = {
                "jd_id": jd_id,
                "jd": parsed_data,
                "evaluation": evaluation,
                "suggestions": suggestions,
                "context_id": context_id
            }
            
            logger.info(f"JD分析完成: jd_id={jd_id}, score={evaluation.get('overall_score', 0)}")
            
            # 5. 返回响应
            await self.send_response(message, {
                "success": True,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"JD分析失败: {e}")
            
            # 更新上下文状态
            try:
                context = await self.get_context(context_id)
                if context:
                    context.update_status("failed")
                    context.update_data("error", str(e))
                    await self.update_context(context)
            except:
                pass
            
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_generate_questionnaire(self, message: MCPMessage) -> None:
        """处理问卷生成请求"""
        jd_id = message.payload.get("jd_id")
        evaluation_model = message.payload.get("evaluation_model", "standard")
        
        logger.info(f"收到问卷生成请求: jd_id={jd_id}")
        
        try:
            # 直接转发给问卷生成Agent
            response = await self.send_request(
                receiver="questionnaire",
                action="generate_questionnaire",
                payload={
                    "jd_id": jd_id,
                    "evaluation_model": evaluation_model
                },
                context_id=message.context_id,
                timeout=90.0
            )
            
            await self.send_response(message, response.payload)
            
        except Exception as e:
            logger.error(f"问卷生成失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_evaluate_match(self, message: MCPMessage) -> None:
        """处理匹配评估请求"""
        jd_id = message.payload.get("jd_id")
        questionnaire_id = message.payload.get("questionnaire_id")
        responses = message.payload.get("responses", {})
        
        logger.info(f"收到匹配评估请求: jd_id={jd_id}")
        
        try:
            # 直接转发给匹配评估Agent
            response = await self.send_request(
                receiver="matcher",
                action="evaluate_match",
                payload={
                    "jd_id": jd_id,
                    "questionnaire_id": questionnaire_id,
                    "responses": responses
                },
                context_id=message.context_id,
                timeout=90.0
            )
            
            await self.send_response(message, response.payload)
            
        except Exception as e:
            logger.error(f"匹配评估失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })


async def create_coordinator_agent(
    mcp_server: MCPServer,
    agent_id: str = "coordinator",
    auto_start: bool = True
) -> CoordinatorAgent:
    agent = CoordinatorAgent(mcp_server=mcp_server, agent_id=agent_id)
    if auto_start:
        await agent.start()
    return agent
