"""优化建议Agent - 生成JD优化建议"""

import logging
import json
from typing import Dict, Any, Optional

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.llm_client import DeepSeekR1Client

logger = logging.getLogger(__name__)


class OptimizerAgent(MCPAgent):
    """优化建议Agent
    
    职责：
    - 基于评估结果生成优化建议
    - 提供JD改写示例
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        llm_client: DeepSeekR1Client,
        agent_id: str = "optimizer",
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type="optimizer",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        self.llm = llm_client
        self.register_handler("generate_suggestions", self.handle_generate_suggestions)
        
        logger.info(f"OptimizerAgent initialized: {agent_id}")
    
    async def handle_generate_suggestions(self, message: MCPMessage) -> None:
        """处理优化建议生成请求"""
        jd_id = message.payload.get("jd_id")
        
        logger.info(f"收到优化建议请求: jd_id={jd_id}")
        
        try:
            # 获取JD数据和评估结果
            jd_response = await self.send_request(
                receiver="data_manager",
                action="get_jd",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            eval_response = await self.send_request(
                receiver="data_manager",
                action="get_evaluation",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            jd_data = jd_response.payload.get("jd", {})
            evaluation = eval_response.payload.get("evaluation", {})
            
            # 生成优化建议
            suggestions = await self._generate_suggestions(jd_data, evaluation)
            
            logger.info(f"优化建议生成完成: jd_id={jd_id}, 建议数={len(suggestions.get('suggestions', []))}")
            
            await self.send_response(message, {
                "success": True,
                "suggestions": suggestions
            })
            
        except Exception as e:
            logger.error(f"优化建议生成失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def _generate_suggestions(self, jd_data: Dict, evaluation: Dict) -> Dict:
        """生成优化建议"""
        prompt = f"""作为HR专家，请为以下岗位JD提供优化建议。

岗位信息：
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

评估结果：
总分: {evaluation.get('overall_score', 0)}
问题: {json.dumps(evaluation.get('issues', []), ensure_ascii=False)}

请提供：
1. 具体的优化建议（按优先级排序）
2. 每条建议的改写示例
3. 缺失信息的补充建议

返回JSON格式：
{{
    "suggestions": [
        {{
            "priority": "high",
            "category": "职责描述",
            "issue": "职责描述过于笼统",
            "suggestion": "具体建议...",
            "example": "改写示例..."
        }}
    ],
    "missing_info": ["薪资范围", "福利待遇"],
    "overall_recommendation": "总体建议..."
}}
"""
        
        result = await self.llm.generate_json(prompt, temperature=0.5)
        return result


async def create_optimizer_agent(
    mcp_server: MCPServer,
    llm_client: DeepSeekR1Client,
    agent_id: str = "optimizer",
    auto_start: bool = True
) -> OptimizerAgent:
    agent = OptimizerAgent(mcp_server=mcp_server, llm_client=llm_client, agent_id=agent_id)
    if auto_start:
        await agent.start()
    return agent
