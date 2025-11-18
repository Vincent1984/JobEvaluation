"""匹配评估Agent - 评估候选人匹配度"""

import logging
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.llm_client import DeepSeekR1Client

logger = logging.getLogger(__name__)


class MatcherAgent(MCPAgent):
    """匹配评估Agent
    
    职责：
    - 解析问卷回答
    - 计算多维度匹配度
    - 生成优势和差距分析
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        llm_client: DeepSeekR1Client,
        agent_id: str = "matcher",
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type="matcher",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        self.llm = llm_client
        self.register_handler("evaluate_match", self.handle_evaluate_match)
        
        logger.info(f"MatcherAgent initialized: {agent_id}")
    
    async def handle_evaluate_match(self, message: MCPMessage) -> None:
        """处理匹配评估请求"""
        jd_id = message.payload.get("jd_id")
        questionnaire_id = message.payload.get("questionnaire_id")
        responses = message.payload.get("responses", {})
        
        logger.info(f"收到匹配评估请求: jd_id={jd_id}, questionnaire_id={questionnaire_id}")
        
        try:
            # 获取JD和问卷数据
            jd_response = await self.send_request(
                receiver="data_manager",
                action="get_jd",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            questionnaire_response = await self.send_request(
                receiver="data_manager",
                action="get_questionnaire",
                payload={"questionnaire_id": questionnaire_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            jd_data = jd_response.payload.get("jd", {})
            questionnaire = questionnaire_response.payload.get("questionnaire", {})
            
            # 计算匹配度
            match_result = await self._calculate_match(jd_data, questionnaire, responses)
            
            # 保存匹配结果
            match_id = str(uuid.uuid4())
            match_result["id"] = match_id
            match_result["jd_id"] = jd_id
            match_result["questionnaire_id"] = questionnaire_id
            match_result["created_at"] = datetime.now().isoformat()
            
            save_response = await self.send_request(
                receiver="data_manager",
                action="save_match_result",
                payload=match_result,
                context_id=message.context_id,
                timeout=30.0
            )
            
            logger.info(f"匹配评估完成: match_id={match_id}, score={match_result.get('overall_score')}")
            
            await self.send_response(message, {
                "success": True,
                "match_result": match_result
            })
            
        except Exception as e:
            logger.error(f"匹配评估失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def _calculate_match(self, jd_data: Dict, questionnaire: Dict, responses: Dict) -> Dict:
        """计算匹配度"""
        prompt = f"""作为HR专家，请评估候选人与岗位的匹配度。

岗位要求：
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

问卷问题：
{json.dumps(questionnaire.get('questions', []), ensure_ascii=False, indent=2)}

候选人回答：
{json.dumps(responses, ensure_ascii=False, indent=2)}

请评估：
1. 总体匹配度（0-100分）
2. 各维度匹配度
3. 候选人优势
4. 能力差距
5. 发展建议

返回JSON格式：
{{
    "overall_score": 85,
    "dimension_scores": {{
        "技能匹配": 90,
        "经验匹配": 80,
        "资质匹配": 85
    }},
    "strengths": ["优势1", "优势2"],
    "gaps": ["差距1", "差距2"],
    "recommendations": ["建议1", "建议2"]
}}
"""
        
        result = await self.llm.generate_json(prompt, temperature=0.3)
        return result


async def create_matcher_agent(
    mcp_server: MCPServer,
    llm_client: DeepSeekR1Client,
    agent_id: str = "matcher",
    auto_start: bool = True
) -> MatcherAgent:
    agent = MatcherAgent(mcp_server=mcp_server, llm_client=llm_client, agent_id=agent_id)
    if auto_start:
        await agent.start()
    return agent
