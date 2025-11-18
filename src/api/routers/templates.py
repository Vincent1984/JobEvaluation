"""模板管理API端点"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from ...models.schemas import CustomTemplate
from datetime import datetime
import uuid

router = APIRouter()

# 临时存储（MVP版本）
template_storage: Dict[str, CustomTemplate] = {}


class CreateTemplateRequest(BaseModel):
    """创建模板请求"""
    name: str
    template_type: str
    config: Dict[str, Any]


class UpdateTemplateRequest(BaseModel):
    """更新模板请求"""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


@router.post("", response_model=Dict[str, Any])
async def create_template(request: CreateTemplateRequest):
    """
    创建模板
    
    - **name**: 模板名称
    - **template_type**: 模板类型（parsing/evaluation/questionnaire）
    - **config**: 模板配置（JSON对象）
    
    示例配置：
    - parsing模板: {"custom_fields": ["技术栈", "团队规模", "汇报关系"]}
    - evaluation模板: {"dimensions": ["完整性", "清晰度"], "weights": {"完整性": 0.6, "清晰度": 0.4}}
    - questionnaire模板: {"question_count": 10, "include_dimensions": ["技能", "经验"]}
    """
    # 验证模板类型
    valid_types = ["parsing", "evaluation", "questionnaire"]
    if request.template_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的模板类型: {request.template_type}，支持的类型: {', '.join(valid_types)}"
        )
    
    try:
        # 生成模板ID
        template_id = f"tmpl_{uuid.uuid4().hex[:8]}"
        
        # 创建模板对象
        template = CustomTemplate(
            id=template_id,
            name=request.name,
            template_type=request.template_type,
            config=request.config,
            created_at=datetime.now()
        )
        
        # 存储模板
        template_storage[template_id] = template
        
        return {
            "success": True,
            "message": "模板创建成功",
            "data": template.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def list_templates(template_type: Optional[str] = None):
    """
    列出模板
    
    - **template_type**: 筛选指定类型的模板（可选）
    """
    templates = list(template_storage.values())
    
    # 筛选
    if template_type:
        templates = [t for t in templates if t.template_type == template_type]
    
    # 按创建时间排序（最新的在前）
    templates.sort(key=lambda x: x.created_at, reverse=True)
    
    return {
        "success": True,
        "data": [t.model_dump() for t in templates],
        "total": len(templates)
    }


@router.get("/{template_id}", response_model=Dict[str, Any])
async def get_template(template_id: str):
    """
    获取模板详情
    
    - **template_id**: 模板ID
    """
    template = template_storage.get(template_id)
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"模板 {template_id} 不存在"
        )
    
    return {
        "success": True,
        "data": template.model_dump()
    }


@router.put("/{template_id}", response_model=Dict[str, Any])
async def update_template(template_id: str, request: UpdateTemplateRequest):
    """
    更新模板
    
    - **template_id**: 模板ID
    - **name**: 新的模板名称（可选）
    - **config**: 新的模板配置（可选）
    """
    template = template_storage.get(template_id)
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"模板 {template_id} 不存在"
        )
    
    # 更新字段
    if request.name is not None:
        template.name = request.name
    
    if request.config is not None:
        template.config = request.config
    
    return {
        "success": True,
        "message": "模板更新成功",
        "data": template.model_dump()
    }


@router.delete("/{template_id}", response_model=Dict[str, Any])
async def delete_template(template_id: str):
    """
    删除模板
    
    - **template_id**: 模板ID
    """
    template = template_storage.get(template_id)
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"模板 {template_id} 不存在"
        )
    
    # 删除模板
    del template_storage[template_id]
    
    return {
        "success": True,
        "message": "模板删除成功"
    }


# 预置一些默认模板
def init_default_templates():
    """初始化默认模板"""
    default_templates = [
        CustomTemplate(
            id="tmpl_default_parsing",
            name="标准解析模板",
            template_type="parsing",
            config={
                "custom_fields": [
                    "job_title",
                    "department",
                    "location",
                    "responsibilities",
                    "required_skills",
                    "preferred_skills",
                    "qualifications"
                ]
            },
            created_at=datetime.now()
        ),
        CustomTemplate(
            id="tmpl_tech_parsing",
            name="技术岗位解析模板",
            template_type="parsing",
            config={
                "custom_fields": [
                    "job_title",
                    "department",
                    "location",
                    "responsibilities",
                    "required_skills",
                    "preferred_skills",
                    "qualifications",
                    "tech_stack",
                    "team_size",
                    "reporting_to"
                ]
            },
            created_at=datetime.now()
        ),
        CustomTemplate(
            id="tmpl_standard_eval",
            name="标准评估模板",
            template_type="evaluation",
            config={
                "dimensions": ["completeness", "clarity", "professionalism"],
                "weights": {
                    "completeness": 0.33,
                    "clarity": 0.33,
                    "professionalism": 0.34
                }
            },
            created_at=datetime.now()
        ),
        CustomTemplate(
            id="tmpl_mercer_ipe",
            name="美世国际职位评估法模板",
            template_type="evaluation",
            config={
                "model": "mercer_ipe",
                "dimensions": ["影响力", "沟通", "创新", "知识技能"],
                "weights": {
                    "影响力": 0.35,
                    "沟通": 0.25,
                    "创新": 0.20,
                    "知识技能": 0.20
                },
                "description": "美世国际职位评估法（Mercer IPE）是一种国际标准的岗位评估方法，从影响力、沟通、创新和知识技能四个维度评估岗位价值",
                "适用场景": ["职位价值评估", "薪酬体系设计", "组织架构优化", "岗位等级划分"]
            },
            created_at=datetime.now()
        ),
        CustomTemplate(
            id="tmpl_factor_comparison",
            name="因素比较法模板",
            template_type="evaluation",
            config={
                "model": "factor_comparison",
                "dimensions": ["技能要求", "责任程度", "努力程度", "工作条件"],
                "weights": {
                    "技能要求": 0.30,
                    "责任程度": 0.30,
                    "努力程度": 0.20,
                    "工作条件": 0.20
                },
                "description": "因素比较法是一种基于补偿性因素的岗位评估方法，适合薪酬设计和职位分级",
                "适用场景": ["薪酬设计", "职位分级", "内部公平性分析", "市场对标"]
            },
            created_at=datetime.now()
        )
    ]
    
    for template in default_templates:
        if template.id not in template_storage:
            template_storage[template.id] = template


# 初始化默认模板
init_default_templates()
