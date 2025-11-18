"""问卷相关API端点"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...models.schemas import (
    Questionnaire,
    QuestionnaireResponse,
    EvaluationModel
)
from ...mcp.simple_client import get_simple_mcp_client
from datetime import datetime
import uuid

# 获取简化 MCP 客户端（不依赖 Redis）
mcp_client = get_simple_mcp_client()

router = APIRouter()

# 临时存储（MVP版本）
questionnaire_storage: Dict[str, Questionnaire] = {}
response_storage: Dict[str, QuestionnaireResponse] = {}


class GenerateQuestionnaireRequest(BaseModel):
    """生成问卷请求"""
    jd_id: str
    evaluation_model: EvaluationModel = EvaluationModel.STANDARD
    title: Optional[str] = None
    description: Optional[str] = None


class SubmitQuestionnaireRequest(BaseModel):
    """提交问卷请求"""
    respondent_name: Optional[str] = None
    answers: Dict[str, Any]


@router.post("/generate", response_model=Dict[str, Any])
async def generate_questionnaire(request: GenerateQuestionnaireRequest):
    """
    生成问卷
    
    - **jd_id**: 岗位JD的ID
    - **evaluation_model**: 评估模型类型（standard/mercer_ipe/factor_comparison）
    - **title**: 问卷标题（可选，默认根据JD生成）
    - **description**: 问卷描述（可选）
    """
    # 验证JD是否存在
    jd = await mcp_client.get_jd(request.jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD {request.jd_id} 不存在")
    
    try:
        # 生成问卷ID
        questionnaire_id = f"quest_{uuid.uuid4().hex[:8]}"
        
        # 使用LLM生成问卷题目
        from ...core.llm_client import llm_client
        
        prompt = f"""
请为以下岗位生成评估问卷。

职位信息：
- 职位标题: {jd.job_title}
- 职责: {', '.join(jd.responsibilities)}
- 必备技能: {', '.join(jd.required_skills)}
- 任职资格: {', '.join(jd.qualifications)}

评估模型: {request.evaluation_model.value}

请生成5-10个问题，涵盖技能、经验、行为等维度。

返回JSON格式：
```json
{{
    "questions": [
        {{
            "id": "q_001",
            "question_text": "您有多少年相关工作经验？",
            "question_type": "single_choice",
            "options": ["1年以下", "1-3年", "3-5年", "5年以上"],
            "dimension": "经验评估",
            "weight": 1.0
        }}
    ]
}}
```

问题类型可选：single_choice（单选）、multiple_choice（多选）、scale（量表）、open_ended（开放题）
"""
        
        result = await llm_client.generate_json(prompt)
        
        # 创建问卷对象
        from ...models.schemas import Question
        
        questions = [
            Question(**q) for q in result.get("questions", [])
        ]
        
        # 生成标题和描述
        title = request.title or f"{jd.job_title} - 评估问卷"
        description = request.description or f"请如实填写以下问题，以评估您与 {jd.job_title} 岗位的匹配度"
        
        # 生成分享链接
        share_link = f"http://localhost:8501/questionnaire/{questionnaire_id}"
        
        questionnaire = Questionnaire(
            id=questionnaire_id,
            jd_id=request.jd_id,
            title=title,
            description=description,
            questions=questions,
            evaluation_model=request.evaluation_model,
            created_at=datetime.now(),
            share_link=share_link
        )
        
        # 存储问卷
        questionnaire_storage[questionnaire_id] = questionnaire
        
        return {
            "success": True,
            "message": "问卷生成成功",
            "data": questionnaire.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{questionnaire_id}", response_model=Dict[str, Any])
async def get_questionnaire(questionnaire_id: str):
    """
    获取问卷
    
    - **questionnaire_id**: 问卷ID
    """
    questionnaire = questionnaire_storage.get(questionnaire_id)
    
    if not questionnaire:
        raise HTTPException(
            status_code=404,
            detail=f"问卷 {questionnaire_id} 不存在"
        )
    
    return {
        "success": True,
        "data": questionnaire.model_dump()
    }


@router.post("/{questionnaire_id}/submit", response_model=Dict[str, Any])
async def submit_questionnaire(
    questionnaire_id: str,
    request: SubmitQuestionnaireRequest
):
    """
    提交问卷
    
    - **questionnaire_id**: 问卷ID
    - **respondent_name**: 填写人姓名（可选）
    - **answers**: 答案字典（question_id -> answer）
    """
    # 验证问卷是否存在
    questionnaire = questionnaire_storage.get(questionnaire_id)
    if not questionnaire:
        raise HTTPException(
            status_code=404,
            detail=f"问卷 {questionnaire_id} 不存在"
        )
    
    # 验证答案完整性
    question_ids = {q.id for q in questionnaire.questions}
    answer_ids = set(request.answers.keys())
    
    missing_questions = question_ids - answer_ids
    if missing_questions:
        raise HTTPException(
            status_code=400,
            detail=f"缺少以下问题的答案: {', '.join(missing_questions)}"
        )
    
    try:
        # 生成回答ID
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        
        # 创建回答对象
        response = QuestionnaireResponse(
            id=response_id,
            questionnaire_id=questionnaire_id,
            respondent_name=request.respondent_name,
            answers=request.answers,
            submitted_at=datetime.now()
        )
        
        # 存储回答
        response_storage[response_id] = response
        
        # 自动触发匹配评估
        from ...core.llm_client import llm_client
        
        # 获取JD信息
        jd = await mcp_client.get_jd(questionnaire.jd_id)
        
        # 使用LLM进行匹配评估
        prompt = f"""
请根据问卷回答评估候选人与岗位的匹配度。

岗位信息：
- 职位标题: {jd.job_title}
- 必备技能: {', '.join(jd.required_skills)}
- 任职资格: {', '.join(jd.qualifications)}

问卷回答：
{request.answers}

请评估以下维度的匹配度（0-100分）：
- 技能匹配
- 经验匹配
- 资质匹配

返回JSON格式：
```json
{{
    "overall_score": 85.0,
    "dimension_scores": {{
        "技能匹配": 90.0,
        "经验匹配": 80.0,
        "资质匹配": 85.0
    }},
    "strengths": ["Python经验丰富", "有大型项目经验"],
    "gaps": ["缺少K8s经验"],
    "recommendations": ["建议学习容器化技术"]
}}
```
"""
        
        match_data = await llm_client.generate_json(prompt)
        
        # 创建匹配结果
        from ...models.schemas import MatchResult
        
        match_id = f"match_{uuid.uuid4().hex[:8]}"
        match_result = MatchResult(
            id=match_id,
            jd_id=questionnaire.jd_id,
            response_id=response_id,
            overall_score=match_data.get("overall_score", 0.0),
            dimension_scores=match_data.get("dimension_scores", {}),
            strengths=match_data.get("strengths", []),
            gaps=match_data.get("gaps", []),
            recommendations=match_data.get("recommendations", []),
            created_at=datetime.now()
        )
        
        # 存储匹配结果（需要导入match router的存储）
        from .match import match_storage
        match_storage[match_id] = match_result
        
        return {
            "success": True,
            "message": "问卷提交成功",
            "data": {
                "response": response.model_dump(),
                "match_result": match_result.model_dump()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def list_questionnaires(jd_id: Optional[str] = None):
    """
    列出问卷
    
    - **jd_id**: 筛选指定JD的问卷（可选）
    """
    questionnaires = list(questionnaire_storage.values())
    
    if jd_id:
        questionnaires = [q for q in questionnaires if q.jd_id == jd_id]
    
    return {
        "success": True,
        "data": [q.model_dump() for q in questionnaires],
        "total": len(questionnaires)
    }
