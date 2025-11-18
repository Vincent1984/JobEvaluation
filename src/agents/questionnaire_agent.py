"""问卷生成Agent - 生成评估问卷"""

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


class QuestionnaireAgent(MCPAgent):
    """问卷生成Agent
    
    职责：
    - 基于JD生成评估问卷
    - 适配不同评估模型
    - 生成多种问题类型（单选、多选、量表、开放）
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        llm_client: DeepSeekR1Client,
        agent_id: str = "questionnaire",
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type="questionnaire",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        self.llm = llm_client
        self.register_handler("generate_questionnaire", self.handle_generate_questionnaire)
        
        logger.info(f"QuestionnaireAgent initialized: {agent_id}")
    
    async def handle_generate_questionnaire(self, message: MCPMessage) -> None:
        """处理问卷生成请求"""
        jd_id = message.payload.get("jd_id")
        evaluation_model = message.payload.get("evaluation_model", "standard")
        
        logger.info(f"收到问卷生成请求: jd_id={jd_id}, model={evaluation_model}")
        
        try:
            # 获取JD数据
            jd_response = await self.send_request(
                receiver="data_manager",
                action="get_jd",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            jd_data = jd_response.payload.get("jd", {})
            
            # 生成问卷
            questionnaire = await self._generate_questionnaire(jd_data, evaluation_model)
            
            # 保存问卷
            questionnaire_id = str(uuid.uuid4())
            questionnaire["id"] = questionnaire_id
            questionnaire["jd_id"] = jd_id
            questionnaire["created_at"] = datetime.now().isoformat()
            
            save_response = await self.send_request(
                receiver="data_manager",
                action="save_questionnaire",
                payload=questionnaire,
                context_id=message.context_id,
                timeout=30.0
            )
            
            logger.info(f"问卷生成完成: questionnaire_id={questionnaire_id}")
            
            await self.send_response(message, {
                "success": True,
                "questionnaire": questionnaire
            })
            
        except Exception as e:
            logger.error(f"问卷生成失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def _generate_questionnaire(self, jd_data: Dict, evaluation_model: str) -> Dict:
        """生成问卷"""
        prompt = f"""作为HR专家，请为以下岗位生成评估问卷。

岗位信息：
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

评估模型：{evaluation_model}

请生成包含以下类型问题的问卷：
1. 单选题（single_choice）：评估具体技能或经验
2. 多选题（multiple_choice）：评估多项能力
3. 量表题（scale）：评估能力水平（1-5分）
4. 开放题（open_ended）：了解详细情况

返回JSON格式：
{{
    "title": "问卷标题",
    "description": "问卷说明",
    "questions": [
        {{
            "id": "q1",
            "question_text": "问题内容",
            "question_type": "single_choice",
            "options": ["选项1", "选项2"],
            "dimension": "技能评估",
            "weight": 1.0
        }}
    ]
}}

要求：
- 生成10-15个问题
- 覆盖岗位的核心要求
- 问题要具体、可量化
"""
        
        result = await self.llm.generate_json(prompt, temperature=0.6)
        result["evaluation_model"] = evaluation_model
        return result


async def create_questionnaire_agent(
    mcp_server: MCPServer,
    llm_client: DeepSeekR1Client,
    agent_id: str = "questionnaire",
    auto_start: bool = True
) -> QuestionnaireAgent:
    agent = QuestionnaireAgent(mcp_server=mcp_server, llm_client=llm_client, agent_id=agent_id)
    if auto_start:
        await agent.start()
    return agent
