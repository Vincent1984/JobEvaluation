"""Simple MCP Client - 不依赖 Redis 的简化版本

用于开发环境，直接调用 Agents 而不通过 MCP Server
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.schemas import (
    JobDescription,
    EvaluationResult,
    QualityScore,
    EvaluationModel
)


class SimpleMCPClient:
    """简化的 MCP 客户端 - 直接调用 Agents"""
    
    def __init__(self):
        """初始化简化客户端"""
        self._parser_agent = None
        self._evaluator_agent = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """确保 Agents 已初始化"""
        if not self._initialized:
            from ..agents.parser_agent import ParserAgent
            from ..agents.evaluator_agent import EvaluatorAgent
            from ..core.llm_client import deepseek_client
            
            # 创建 Agents（不需要 MCP Server）
            self._parser_agent = ParserAgent(
                mcp_server=None,  # 不使用 MCP Server
                llm_client=deepseek_client,
                agent_id="parser"
            )
            
            self._evaluator_agent = EvaluatorAgent(
                mcp_server=None,  # 不使用 MCP Server
                llm_client=deepseek_client,
                agent_id="evaluator"
            )
            
            self._initialized = True
    
    async def parse_jd(self, jd_text: str) -> JobDescription:
        """解析 JD 文本
        
        Args:
            jd_text: JD 文本
            
        Returns:
            JobDescription 对象
        """
        await self._ensure_initialized()
        
        # 直接调用 Parser Agent 的解析方法（传入空的 custom_fields）
        parsed_data = await self._parser_agent._parse_jd_with_llm(jd_text, {})
        
        # 生成 JD ID
        jd_id = f"jd_{uuid.uuid4().hex[:8]}"
        
        # 构建 JobDescription 对象
        jd = JobDescription(
            id=jd_id,
            job_title=parsed_data.get("job_title", "未知职位"),
            department=parsed_data.get("department"),
            location=parsed_data.get("location"),
            responsibilities=parsed_data.get("responsibilities", []),
            required_skills=parsed_data.get("required_skills", []),
            preferred_skills=parsed_data.get("preferred_skills", []),
            qualifications=parsed_data.get("qualifications", []),
            raw_text=jd_text,
            category_level1_id=parsed_data.get("category_level1_id"),
            category_level2_id=parsed_data.get("category_level2_id"),
            category_level3_id=parsed_data.get("category_level3_id"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return jd
    
    async def evaluate_jd(
        self,
        jd_id: str,
        model_type: EvaluationModel = EvaluationModel.STANDARD
    ) -> EvaluationResult:
        """评估 JD 质量
        
        Args:
            jd_id: JD ID
            model_type: 评估模型类型
            
        Returns:
            EvaluationResult 对象
        """
        await self._ensure_initialized()
        
        # 注意：这里需要 JD 数据，但简化版本中我们没有存储
        # 实际使用时需要传入 JD 对象或从某处获取
        # 这里返回一个模拟的评估结果
        
        eval_id = f"eval_{uuid.uuid4().hex[:8]}"
        
        quality_score = QualityScore(
            overall_score=85.0,
            completeness=90.0,
            clarity=80.0,
            professionalism=85.0,
            issues=[]
        )
        
        evaluation = EvaluationResult(
            id=eval_id,
            jd_id=jd_id,
            model_type=model_type,
            quality_score=quality_score,
            recommendations=["建议添加更多职责描述", "建议明确薪资范围"],
            created_at=datetime.now()
        )
        
        return evaluation
    
    async def analyze_jd(
        self,
        jd_text: str,
        model_type: EvaluationModel = EvaluationModel.STANDARD
    ) -> Dict[str, Any]:
        """完整分析 JD（解析 + 评估）
        
        Args:
            jd_text: JD 文本
            model_type: 评估模型类型（可以是 EvaluationModel 枚举或字符串）
            
        Returns:
            包含 jd 和 evaluation 的字典
        """
        # 1. 解析 JD
        jd = await self.parse_jd(jd_text)
        
        # 2. 评估质量（使用实际的评估逻辑）
        await self._ensure_initialized()
        
        # 构建 JD 数据用于评估
        jd_data = {
            "job_title": jd.job_title,
            "department": jd.department,
            "location": jd.location,
            "responsibilities": jd.responsibilities,
            "required_skills": jd.required_skills,
            "preferred_skills": jd.preferred_skills,
            "qualifications": jd.qualifications,
            "raw_text": jd.raw_text
        }
        
        # 处理 model_type（可能是枚举或字符串）
        if isinstance(model_type, str):
            model_type_str = model_type
        else:
            model_type_str = model_type.value
        
        # 选择评估模型
        model = self._evaluator_agent.evaluation_models.get(model_type_str)
        if not model:
            model = self._evaluator_agent.evaluation_models["standard"]
        
        # 调用评估模型的 evaluate 方法
        eval_result = await model.evaluate(jd_data, self._evaluator_agent.llm)
        
        # 构建 EvaluationResult 对象
        eval_id = f"eval_{uuid.uuid4().hex[:8]}"
        
        quality_score = QualityScore(
            overall_score=eval_result.get("overall_score", 0.0),
            completeness=eval_result.get("completeness", 0.0),
            clarity=eval_result.get("clarity", 0.0),
            professionalism=eval_result.get("professionalism", 0.0),
            issues=eval_result.get("issues", [])
        )
        
        # 确保 model_type 是 EvaluationModel 枚举
        if isinstance(model_type, str):
            # 从字符串转换为枚举
            model_type_enum = EvaluationModel(model_type)
        else:
            model_type_enum = model_type
        
        evaluation = EvaluationResult(
            id=eval_id,
            jd_id=jd.id,
            model_type=model_type_enum,
            quality_score=quality_score,
            recommendations=eval_result.get("recommendations", []),
            created_at=datetime.now()
        )
        
        return {
            "jd": jd,
            "evaluation": evaluation
        }
    
    async def get_jd(self, jd_id: str) -> Optional[JobDescription]:
        """获取 JD
        
        注意：简化版本不支持持久化存储
        
        Args:
            jd_id: JD ID
            
        Returns:
            None（简化版本不支持）
        """
        return None
    
    async def shutdown(self):
        """关闭客户端"""
        pass


# 全局客户端实例（单例模式）
_simple_mcp_client_instance: Optional[SimpleMCPClient] = None


def get_simple_mcp_client() -> SimpleMCPClient:
    """获取简化 MCP 客户端实例（单例模式）
    
    Returns:
        SimpleMCPClient 实例
    """
    global _simple_mcp_client_instance
    
    if _simple_mcp_client_instance is None:
        _simple_mcp_client_instance = SimpleMCPClient()
    
    return _simple_mcp_client_instance
