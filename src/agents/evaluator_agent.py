"""质量评估Agent - 评估JD质量"""

import logging
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.llm_client import DeepSeekR1Client
from src.models.schemas import CategoryTag, DimensionContribution, ManualModification

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


class ComprehensiveEvaluator:
    """综合评估器 - 整合JD内容、评估模板、分类标签三个维度"""
    
    def __init__(self, llm_client: DeepSeekR1Client):
        """初始化综合评估器
        
        Args:
            llm_client: LLM客户端
        """
        self.llm = llm_client
    
    async def comprehensive_evaluate(
        self,
        jd_data: Dict,
        evaluation_model: EvaluationModelBase,
        category_tags: List[CategoryTag]
    ) -> Dict:
        """执行综合评估
        
        Args:
            jd_data: JD数据
            evaluation_model: 评估模型
            category_tags: 分类标签列表
            
        Returns:
            综合评估结果
        """
        # 1. 基础评估（基于JD内容和评估模板）
        base_evaluation = await evaluation_model.evaluate(jd_data, self.llm)
        
        # 2. 分析分类标签的影响
        tag_analysis = await self._analyze_category_tags(category_tags, jd_data)
        
        # 3. 整合三个维度
        integrated_result = await self._integrate_dimensions(
            jd_data,
            base_evaluation,
            tag_analysis,
            evaluation_model
        )
        
        # 4. 判断企业价值
        company_value = await self._determine_company_value(
            base_evaluation,
            tag_analysis,
            jd_data
        )
        
        # 5. 判断是否核心岗位
        is_core_position = await self._determine_core_position(
            tag_analysis,
            base_evaluation,
            jd_data
        )
        
        # 6. 计算维度贡献度
        dimension_contributions = self._calculate_dimension_contributions(
            base_evaluation,
            tag_analysis
        )
        
        # 7. 组装最终结果
        result = {
            **base_evaluation,
            "company_value": company_value,
            "is_core_position": is_core_position,
            "dimension_contributions": dimension_contributions,
            "tag_analysis": tag_analysis,
            "integrated_analysis": integrated_result
        }
        
        return result
    
    async def _analyze_category_tags(
        self,
        category_tags: List[CategoryTag],
        jd_data: Dict
    ) -> Dict:
        """分析分类标签对评估的影响
        
        Args:
            category_tags: 分类标签列表
            jd_data: JD数据
            
        Returns:
            标签分析结果
        """
        if not category_tags:
            return {
                "has_tags": False,
                "strategic_importance": "未知",
                "business_value": "未知",
                "skill_scarcity": "未知",
                "market_competition": "未知",
                "development_potential": "未知",
                "risk_level": "未知",
                "impact_summary": "无分类标签信息"
            }
        
        # 构建标签分析prompt
        tags_info = [
            {
                "name": tag.name,
                "type": tag.tag_type,
                "description": tag.description
            }
            for tag in category_tags
        ]
        
        prompt = f"""作为HR专家，请分析以下分类标签对岗位评估的影响。

岗位信息：
职位名称: {jd_data.get('job_title', '未知')}

分类标签：
{json.dumps(tags_info, ensure_ascii=False, indent=2)}

请分析这些标签对岗位评估的影响，并返回JSON格式：
{{
    "has_tags": true,
    "strategic_importance": "高/中/低",
    "business_value": "高/中/低",
    "skill_scarcity": "高/中/低",
    "market_competition": "高/中/低",
    "development_potential": "高/中/低",
    "risk_level": "高/中/低",
    "impact_summary": "标签对评估的整体影响说明",
    "value_adjustment": 5,  # 对企业价值评级的调整分数（-10到+10）
    "core_position_indicator": 0.8  # 核心岗位指标（0-1，越高越可能是核心岗位）
}}
"""
        
        try:
            analysis = await self.llm.generate_json(prompt, temperature=0.3)
            analysis["has_tags"] = True
            return analysis
        except Exception as e:
            logger.error(f"标签分析失败: {e}")
            return {
                "has_tags": True,
                "strategic_importance": "未知",
                "business_value": "未知",
                "skill_scarcity": "未知",
                "market_competition": "未知",
                "development_potential": "未知",
                "risk_level": "未知",
                "impact_summary": f"标签分析失败: {str(e)}",
                "value_adjustment": 0,
                "core_position_indicator": 0.5
            }
    
    async def _integrate_dimensions(
        self,
        jd_data: Dict,
        base_evaluation: Dict,
        tag_analysis: Dict,
        evaluation_model: EvaluationModelBase
    ) -> Dict:
        """整合JD内容、评估模板、分类标签三个维度
        
        Args:
            jd_data: JD数据
            base_evaluation: 基础评估结果
            tag_analysis: 标签分析结果
            evaluation_model: 评估模型
            
        Returns:
            整合后的分析结果
        """
        prompt = f"""作为HR专家，请整合以下三个维度的信息，给出综合评估分析。

**维度1：JD内容**
职位名称: {jd_data.get('job_title', '未知')}
职责: {json.dumps(jd_data.get('responsibilities', []), ensure_ascii=False)}
必备技能: {json.dumps(jd_data.get('required_skills', []), ensure_ascii=False)}

**维度2：评估模板（{type(evaluation_model).__name__}）**
评估维度: {json.dumps(evaluation_model.dimensions, ensure_ascii=False)}
维度得分: {json.dumps(base_evaluation.get('dimension_scores', {}), ensure_ascii=False)}
基础分数: {base_evaluation.get('overall_score', 0)}

**维度3：分类标签**
{json.dumps(tag_analysis, ensure_ascii=False, indent=2)}

请综合分析这三个维度，返回JSON格式：
{{
    "integrated_score": 85,  # 综合后的最终分数（0-100）
    "dimension_synergy": "三个维度的协同分析",
    "key_insights": ["关键洞察1", "关键洞察2"],
    "conflicts": ["维度间的冲突或不一致"],
    "recommendations": ["基于三维度的综合建议"]
}}
"""
        
        try:
            result = await self.llm.generate_json(prompt, temperature=0.3)
            return result
        except Exception as e:
            logger.error(f"维度整合失败: {e}")
            return {
                "integrated_score": base_evaluation.get('overall_score', 0),
                "dimension_synergy": f"维度整合失败: {str(e)}",
                "key_insights": [],
                "conflicts": [],
                "recommendations": []
            }
    
    async def _determine_company_value(
        self,
        base_evaluation: Dict,
        tag_analysis: Dict,
        jd_data: Dict
    ) -> str:
        """判断企业价值：高价值/中价值/低价值
        
        Args:
            base_evaluation: 基础评估结果
            tag_analysis: 标签分析结果
            jd_data: JD数据
            
        Returns:
            企业价值评级
        """
        # 基础分数
        base_score = base_evaluation.get('overall_score', 0)
        
        # 标签调整
        value_adjustment = tag_analysis.get('value_adjustment', 0)
        
        # 业务价值和战略重要性
        business_value = tag_analysis.get('business_value', '未知')
        strategic_importance = tag_analysis.get('strategic_importance', '未知')
        
        # 综合判断
        adjusted_score = base_score + value_adjustment
        
        # 判断逻辑
        if adjusted_score >= 85 or business_value == "高" or strategic_importance == "高":
            return "高价值"
        elif adjusted_score >= 70 or business_value == "中" or strategic_importance == "中":
            return "中价值"
        else:
            return "低价值"
    
    async def _determine_core_position(
        self,
        tag_analysis: Dict,
        base_evaluation: Dict,
        jd_data: Dict
    ) -> bool:
        """判断是否核心岗位
        
        Args:
            tag_analysis: 标签分析结果
            base_evaluation: 基础评估结果
            jd_data: JD数据
            
        Returns:
            是否核心岗位
        """
        # 核心岗位指标（来自标签分析）
        core_indicator = tag_analysis.get('core_position_indicator', 0.5)
        
        # 战略重要性
        strategic_importance = tag_analysis.get('strategic_importance', '未知')
        
        # 技能稀缺性
        skill_scarcity = tag_analysis.get('skill_scarcity', '未知')
        
        # 市场竞争度
        market_competition = tag_analysis.get('market_competition', '未知')
        
        # 基础分数
        base_score = base_evaluation.get('overall_score', 0)
        
        # 判断逻辑
        is_core = False
        
        # 条件1：核心岗位指标高
        if core_indicator >= 0.7:
            is_core = True
        
        # 条件2：战略重要性高或技能稀缺性高
        if strategic_importance == "高" or skill_scarcity == "高":
            is_core = True
        
        # 条件3：综合分数高且市场竞争度高
        if base_score >= 85 and market_competition == "高":
            is_core = True
        
        return is_core
    
    def _calculate_dimension_contributions(
        self,
        base_evaluation: Dict,
        tag_analysis: Dict
    ) -> Dict:
        """计算三个维度的贡献度百分比
        
        Args:
            base_evaluation: 基础评估结果
            tag_analysis: 标签分析结果
            
        Returns:
            维度贡献度
        """
        # 默认权重
        jd_content_weight = 40.0
        evaluation_template_weight = 30.0
        category_tags_weight = 30.0
        
        # 如果没有标签，调整权重
        if not tag_analysis.get('has_tags', False):
            jd_content_weight = 60.0
            evaluation_template_weight = 40.0
            category_tags_weight = 0.0
        
        return {
            "jd_content": jd_content_weight,
            "evaluation_template": evaluation_template_weight,
            "category_tags": category_tags_weight
        }


class EvaluatorAgent(MCPAgent):
    """质量评估Agent
    
    职责：
    - 评估JD质量
    - 应用专业评估模型（美世法、因素法）
    - 识别质量问题
    - 支持综合评估（整合JD内容、评估模板、分类标签）
    - 支持手动修改评估结果
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
        
        # 综合评估器
        self.comprehensive_evaluator = ComprehensiveEvaluator(llm_client)
        
        # 注册消息处理器
        self.register_handler("evaluate_quality", self.handle_evaluate_quality)
        self.register_handler("update_evaluation", self.handle_update_evaluation)
        
        logger.info(f"EvaluatorAgent initialized: {agent_id}")
    
    async def handle_evaluate_quality(self, message: MCPMessage) -> None:
        """处理质量评估请求（综合评估）
        
        Args:
            message: MCP消息，payload包含:
                - jd_id: JD ID
                - model_type: 评估模型类型（可选，默认standard）
                - category_level3_id: 第三层级分类ID（可选）
        """
        jd_id = message.payload.get("jd_id")
        model_type = message.payload.get("model_type", "standard")
        category_level3_id = message.payload.get("category_level3_id")
        
        logger.info(f"收到质量评估请求: jd_id={jd_id}, model={model_type}, category={category_level3_id}")
        
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
            
            # 获取分类标签（如果有第三层级分类）
            category_tags = []
            if category_level3_id or jd_data.get("category_level3_id"):
                category_id = category_level3_id or jd_data.get("category_level3_id")
                try:
                    tags_response = await self.send_request(
                        receiver="data_manager",
                        action="get_category_tags",
                        payload={"category_id": category_id},
                        context_id=message.context_id,
                        timeout=30.0
                    )
                    
                    if tags_response.payload.get("success", True):
                        tags_data = tags_response.payload.get("tags", [])
                        # 转换为CategoryTag对象
                        category_tags = [
                            CategoryTag(**tag) if isinstance(tag, dict) else tag
                            for tag in tags_data
                        ]
                        logger.info(f"获取到 {len(category_tags)} 个分类标签")
                except Exception as e:
                    logger.warning(f"获取分类标签失败: {e}")
            
            # 选择评估模型
            model = self.evaluation_models.get(model_type)
            if not model:
                logger.warning(f"未知的评估模型: {model_type}, 使用标准模型")
                model = self.evaluation_models["standard"]
            
            # 执行综合评估（整合三个维度）
            evaluation_result = await self.comprehensive_evaluator.comprehensive_evaluate(
                jd_data,
                model,
                category_tags
            )
            
            # 添加元数据
            evaluation_result["jd_id"] = jd_id
            evaluation_result["model_type"] = model_type
            evaluation_result["evaluated_at"] = datetime.now().isoformat()
            evaluation_result["is_manually_modified"] = False
            evaluation_result["manual_modifications"] = []
            
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
            
            logger.info(f"综合评估完成: jd_id={jd_id}, score={evaluation_result.get('overall_score')}, "
                       f"value={evaluation_result.get('company_value')}, "
                       f"core={evaluation_result.get('is_core_position')}")
            
            # 返回结果
            await self.send_response(message, {
                "success": True,
                "quality_score": {
                    "overall_score": evaluation_result.get("overall_score", 0),
                    "dimension_scores": evaluation_result.get("dimension_scores", {}),
                    "weighted_score": evaluation_result.get("weighted_score", 0)
                },
                "company_value": evaluation_result.get("company_value", "中价值"),
                "is_core_position": evaluation_result.get("is_core_position", False),
                "dimension_contributions": evaluation_result.get("dimension_contributions", {}),
                "evaluation": evaluation_result
            })
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}", exc_info=True)
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })


    async def handle_update_evaluation(self, message: MCPMessage) -> None:
        """处理手动修改评估结果的请求
        
        Args:
            message: MCP消息，payload包含:
                - jd_id: JD ID
                - modifications: 修改的字段和新值 (Dict[str, Any])
                - reason: 修改原因 (str)
        """
        jd_id = message.payload.get("jd_id")
        modifications = message.payload.get("modifications", {})
        reason = message.payload.get("reason", "")
        
        logger.info(f"收到手动修改评估结果请求: jd_id={jd_id}, modifications={list(modifications.keys())}")
        
        try:
            # 获取现有评估结果
            eval_response = await self.send_request(
                receiver="data_manager",
                action="get_evaluation",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            if not eval_response.payload.get("success", True):
                raise Exception(f"获取评估结果失败: {eval_response.payload.get('error', '未知错误')}")
            
            evaluation = eval_response.payload.get("evaluation", {})
            
            if not evaluation:
                raise Exception(f"未找到JD {jd_id} 的评估结果")
            
            # 记录修改历史
            modification_record = {
                "timestamp": datetime.now().isoformat(),
                "modified_fields": {},
                "original_values": {},
                "reason": reason
            }
            
            # 应用修改并记录原始值
            for field, new_value in modifications.items():
                if field in evaluation:
                    modification_record["original_values"][field] = evaluation[field]
                    modification_record["modified_fields"][field] = new_value
                    evaluation[field] = new_value
                    logger.info(f"修改字段 {field}: {evaluation[field]} -> {new_value}")
                else:
                    logger.warning(f"字段 {field} 不存在于评估结果中，跳过")
            
            # 标记为手动修改
            evaluation["is_manually_modified"] = True
            
            # 添加修改记录到历史
            if "manual_modifications" not in evaluation:
                evaluation["manual_modifications"] = []
            evaluation["manual_modifications"].append(modification_record)
            
            # 更新时间戳
            evaluation["updated_at"] = datetime.now().isoformat()
            
            # 保存更新后的评估结果
            save_response = await self.send_request(
                receiver="data_manager",
                action="save_evaluation",
                payload={
                    "jd_id": jd_id,
                    "evaluation": evaluation
                },
                context_id=message.context_id,
                timeout=30.0
            )
            
            if not save_response.payload.get("success", True):
                logger.warning(f"保存更新后的评估结果失败: {save_response.payload.get('error', '未知错误')}")
            
            logger.info(f"评估结果手动修改完成: jd_id={jd_id}, 修改了 {len(modifications)} 个字段")
            
            # 返回结果
            await self.send_response(message, {
                "success": True,
                "evaluation": evaluation,
                "modification_record": modification_record
            })
            
        except Exception as e:
            logger.error(f"手动修改评估结果失败: {e}", exc_info=True)
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
