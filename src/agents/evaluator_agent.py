"""质量评估Agent - 评估JD质量"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.llm_client import DeepSeekR1Client

logger = logging.getLogger(__name__)


class EvaluationModelBase:
    """评估模型基类"""
    
    def __init__(self):
        self.dimensions = []
        self.weights = {}
    
    async def evaluate(self, jd_data: Dict, llm_client: DeepSeekR1Client) -> Dict:
        """执行评估"""
        raise NotImplementedError


class StandardEvaluationModel(EvaluationModelBase):
    """标准评估模型"""
    
    def __init__(self):
        super().__init__()
        self.dimensions = ["完整性", "清晰度", "专业性"]
        self.weights = {
            "完整性": 0.4,
            "清晰度": 0.3,
            "专业性": 0.3
        }
    
    async def evaluate(self, jd_data: Dict, llm_client: DeepSeekR1Client) -> Dict:
        """基于标准模型评估"""
        prompt = f"""作为HR专家，请评估以下岗位JD的质量。

岗位信息：
职位名称: {jd_data.get('job_title', '未知')}
职责: {json.dumps(jd_data.get('responsibilities', []), ensure_ascii=False)}
必备技能: {json.dumps(jd_data.get('required_skills', []), ensure_ascii=False)}
任职资格: {json.dumps(jd_data.get('qualifications', []), ensure_ascii=False)}

请从以下三个维度评估（每个维度0-100分）：
1. 完整性：JD是否包含所有必要信息（职责、技能、资格等）
2. 清晰度：描述是否清晰明确，易于理解
3. 专业性：语言是否专业，是否符合行业标准

返回JSON格式：
{{
    "dimension_scores": {{"完整性": 85, "清晰度": 75, "专业性": 80}},
    "overall_score": 80,
    "analysis": "详细分析...",
    "issues": [
        {{"type": "缺失信息", "severity": "high", "description": "缺少薪资范围"}},
        {{"type": "描述模糊", "severity": "medium", "description": "职责描述不够具体"}}
    ]
}}
"""
        
        result = await llm_client.generate_json(prompt, temperature=0.3)
        
        # 应用权重计算总分
        weighted_score = sum(
            result["dimension_scores"][dim] * self.weights[dim]
            for dim in self.dimensions
        )
        result["weighted_score"] = weighted_score
        
        return result


class MercerIPEModel(EvaluationModelBase):
    """美世国际职位评估法"""
    
    def __init__(self):
        super().__init__()
        self.dimensions = ["影响力", "沟通", "创新", "知识技能"]
        self.weights = {
            "影响力": 0.35,
            "沟通": 0.25,
            "创新": 0.20,
            "知识技能": 0.20
        }
    
    async def evaluate(self, jd_data: Dict, llm_client: DeepSeekR1Client) -> Dict:
        """基于美世法评估"""
        prompt = f"""作为HR专家，请使用美世国际职位评估法（Mercer IPE）评估以下岗位。

岗位信息：
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

请从以下四个维度评估（每个维度0-100分）：
1. 影响力（Impact）：岗位对组织的影响范围和程度
2. 沟通（Communication）：岗位所需的沟通复杂度和频率
3. 创新（Innovation）：岗位所需的创新和问题解决能力
4. 知识技能（Knowledge & Skills）：岗位所需的专业知识和技能水平

返回JSON格式：
{{
    "dimension_scores": {{"影响力": 85, "沟通": 75, "创新": 70, "知识技能": 80}},
    "overall_score": 78,
    "analysis": "详细分析...",
    "issues": ["问题1", "问题2"]
}}
"""
        
        result = await llm_client.generate_json(prompt, temperature=0.3)
        
        # 应用权重计算总分
        weighted_score = sum(
            result["dimension_scores"][dim] * self.weights[dim]
            for dim in self.dimensions
        )
        result["weighted_score"] = weighted_score
        
        return result


class FactorComparisonModel(EvaluationModelBase):
    """因素比较法"""
    
    def __init__(self):
        super().__init__()
        self.dimensions = ["技能要求", "责任程度", "努力程度", "工作条件"]
        self.weights = {
            "技能要求": 0.30,
            "责任程度": 0.30,
            "努力程度": 0.20,
            "工作条件": 0.20
        }
    
    async def evaluate(self, jd_data: Dict, llm_client: DeepSeekR1Client) -> Dict:
        """基于因素比较法评估"""
        prompt = f"""作为HR专家，请使用因素比较法评估以下岗位。

岗位信息：
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

请从以下四个因素评估（每个因素0-100分）：
1. 技能要求：岗位所需的技能水平和复杂度
2. 责任程度：岗位承担的责任大小和重要性
3. 努力程度：岗位所需的体力和脑力努力
4. 工作条件：工作环境和条件的优劣

返回JSON格式：
{{
    "dimension_scores": {{"技能要求": 85, "责任程度": 75, "努力程度": 70, "工作条件": 80}},
    "overall_score": 78,
    "analysis": "详细分析...",
    "issues": ["问题1", "问题2"]
}}
"""
        
        result = await llm_client.generate_json(prompt, temperature=0.3)
        
        # 应用权重计算总分
        weighted_score = sum(
            result["dimension_scores"][dim] * self.weights[dim]
            for dim in self.dimensions
        )
        result["weighted_score"] = weighted_score
        
        return result


class EvaluatorAgent(MCPAgent):
    """质量评估Agent
    
    职责：
    - 评估JD质量
    - 应用专业评估模型（美世法、因素法）
    - 识别质量问题
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        llm_client: DeepSeekR1Client,
        agent_id: str = "evaluator",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """初始化质量评估Agent
        
        Args:
            mcp_server: MCP服务器实例
            llm_client: LLM客户端
            agent_id: Agent ID
            metadata: 元数据
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="evaluator",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        self.llm = llm_client
        
        # 评估模型注册表
        self.evaluation_models = {
            "standard": StandardEvaluationModel(),
            "mercer_ipe": MercerIPEModel(),
            "factor_comparison": FactorComparisonModel()
        }
        
        # 注册消息处理器
        self.register_handler("evaluate_quality", self.handle_evaluate_quality)
        
        logger.info(f"EvaluatorAgent initialized: {agent_id}")
    
    async def handle_evaluate_quality(self, message: MCPMessage) -> None:
        """处理质量评估请求
        
        Args:
            message: MCP消息，payload包含:
                - jd_id: JD ID
                - model_type: 评估模型类型（可选，默认standard）
        """
        jd_id = message.payload.get("jd_id")
        model_type = message.payload.get("model_type", "standard")
        
        logger.info(f"收到质量评估请求: jd_id={jd_id}, model={model_type}")
        
        try:
            # 从数据Agent获取JD数据
            jd_response = await self.send_request(
                receiver="data_manager",
                action="get_jd",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            if not jd_response.payload.get("success", True):
                raise Exception(f"获取JD失败: {jd_response.payload.get('error', '未知错误')}")
            
            jd_data = jd_response.payload["jd"]
            
            # 选择评估模型
            model = self.evaluation_models.get(model_type)
            if not model:
                logger.warning(f"未知的评估模型: {model_type}, 使用标准模型")
                model = self.evaluation_models["standard"]
            
            # 执行评估
            evaluation_result = await model.evaluate(jd_data, self.llm)
            
            # 添加元数据
            evaluation_result["jd_id"] = jd_id
            evaluation_result["model_type"] = model_type
            evaluation_result["evaluated_at"] = datetime.now().isoformat()
            
            # 保存评估结果
            save_response = await self.send_request(
                receiver="data_manager",
                action="save_evaluation",
                payload={
                    "jd_id": jd_id,
                    "evaluation": evaluation_result
                },
                context_id=message.context_id,
                timeout=30.0
            )
            
            if not save_response.payload.get("success", True):
                logger.warning(f"保存评估结果失败: {save_response.payload.get('error', '未知错误')}")
            
            logger.info(f"质量评估完成: jd_id={jd_id}, score={evaluation_result.get('overall_score')}")
            
            # 返回结果
            await self.send_response(message, {
                "success": True,
                "quality_score": {
                    "overall_score": evaluation_result.get("overall_score", 0),
                    "dimension_scores": evaluation_result.get("dimension_scores", {}),
                    "weighted_score": evaluation_result.get("weighted_score", 0)
                },
                "evaluation": evaluation_result
            })
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })


# 便捷函数
async def create_evaluator_agent(
    mcp_server: MCPServer,
    llm_client: DeepSeekR1Client,
    agent_id: str = "evaluator",
    auto_start: bool = True
) -> EvaluatorAgent:
    """创建并启动质量评估Agent
    
    Args:
        mcp_server: MCP服务器实例
        llm_client: LLM客户端
        agent_id: Agent ID
        auto_start: 是否自动启动
        
    Returns:
        EvaluatorAgent实例
    """
    agent = EvaluatorAgent(
        mcp_server=mcp_server,
        llm_client=llm_client,
        agent_id=agent_id
    )
    
    if auto_start:
        await agent.start()
    
    return agent
