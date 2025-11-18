"""数据模型定义"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class EvaluationModel(str, Enum):
    """评估模型类型"""
    STANDARD = "standard"
    MERCER_IPE = "mercer_ipe"
    FACTOR_COMPARISON = "factor_comparison"


class QuestionType(str, Enum):
    """问题类型"""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    OPEN_ENDED = "open_ended"


class JobCategory(BaseModel):
    """职位分类模型（支持3层级）"""
    id: str
    name: str
    level: int = Field(ge=1, le=3, description="分类层级: 1=一级, 2=二级, 3=三级")
    parent_id: Optional[str] = Field(None, description="父级分类ID")
    description: Optional[str] = None
    sample_jd_ids: List[str] = Field(default_factory=list, description="样本职位JD的ID（仅第三层级，1-2个）")
    created_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode='after')
    def validate_category_rules(self):
        """验证分类规则"""
        # 验证父级ID规则
        if self.level == 1 and self.parent_id is not None:
            raise ValueError('一级分类不能有父级分类')
        elif self.level in [2, 3] and self.parent_id is None:
            raise ValueError(f'第{self.level}级分类必须指定父级分类')
        
        # 验证样本JD规则
        if self.level == 3:
            # 第三层级最多2个样本JD
            if len(self.sample_jd_ids) > 2:
                raise ValueError('第三层级分类的样本JD数量不能超过2个')
        else:
            # 非第三层级不允许有样本JD
            if len(self.sample_jd_ids) > 0:
                raise ValueError('只有第三层级分类才能添加样本JD')
        
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "id": "cat_001",
                "name": "后端工程师",
                "level": 3,
                "parent_id": "cat_parent_001",
                "description": "负责后端系统开发",
                "sample_jd_ids": ["jd_001", "jd_002"],
                "created_at": "2024-01-01T00:00:00"
            }
        }


class JobDescription(BaseModel):
    """岗位JD模型"""
    id: str
    job_title: str
    department: Optional[str] = None
    location: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    raw_text: str
    category_level1_id: Optional[str] = Field(None, description="一级分类ID")
    category_level2_id: Optional[str] = Field(None, description="二级分类ID")
    category_level3_id: Optional[str] = Field(None, description="三级分类ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "jd_001",
                "job_title": "高级Python工程师",
                "department": "技术部",
                "location": "北京",
                "responsibilities": ["开发后端服务", "优化系统性能"],
                "required_skills": ["Python", "FastAPI", "SQL"],
                "preferred_skills": ["Docker", "K8s"],
                "qualifications": ["本科及以上", "3年以上经验"],
                "custom_fields": {},
                "raw_text": "招聘高级Python工程师...",
                "category_level1_id": "cat_tech",
                "category_level2_id": "cat_dev",
                "category_level3_id": "cat_backend"
            }
        }


class QualityScore(BaseModel):
    """质量评分模型"""
    overall_score: float = Field(ge=0, le=100, description="综合质量分数")
    completeness: float = Field(ge=0, le=100, description="完整性分数")
    clarity: float = Field(ge=0, le=100, description="清晰度分数")
    professionalism: float = Field(ge=0, le=100, description="专业性分数")
    issues: List[Dict[str, str]] = Field(default_factory=list, description="质量问题列表")

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 85.0,
                "completeness": 90.0,
                "clarity": 80.0,
                "professionalism": 85.0,
                "issues": [
                    {"type": "clarity", "severity": "medium", "description": "职责描述不够具体"}
                ]
            }
        }


class EvaluationResult(BaseModel):
    """评估结果模型"""
    model_config = {
        "protected_namespaces": (),  # 允许使用model_开头的字段名
        "json_schema_extra": {
            "example": {
                "id": "eval_001",
                "jd_id": "jd_001",
                "model_type": "standard",
                "quality_score": {
                    "overall_score": 85.0,
                    "completeness": 90.0,
                    "clarity": 80.0,
                    "professionalism": 85.0,
                    "issues": []
                },
                "position_value": {"影响力": 85.0, "沟通": 75.0},
                "recommendations": ["建议补充薪资范围", "职责描述可以更具体"]
            }
        }
    }
    
    id: str
    jd_id: str
    model_type: EvaluationModel
    quality_score: QualityScore
    position_value: Optional[Dict[str, float]] = Field(None, description="岗位价值评估")
    recommendations: List[str] = Field(default_factory=list, description="优化建议")
    created_at: datetime = Field(default_factory=datetime.now)


class Question(BaseModel):
    """问卷题目模型"""
    id: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    dimension: str = Field(description="评估维度")
    weight: float = Field(default=1.0, ge=0, le=1)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "q_001",
                "question_text": "您有多少年Python开发经验？",
                "question_type": "single_choice",
                "options": ["1年以下", "1-3年", "3-5年", "5年以上"],
                "dimension": "技能评估",
                "weight": 1.0
            }
        }


class Questionnaire(BaseModel):
    """问卷模型"""
    id: str
    jd_id: str
    title: str
    description: str
    questions: List[Question] = Field(default_factory=list)
    evaluation_model: EvaluationModel
    created_at: datetime = Field(default_factory=datetime.now)
    share_link: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "quest_001",
                "jd_id": "jd_001",
                "title": "高级Python工程师评估问卷",
                "description": "请如实填写以下问题",
                "questions": [],
                "evaluation_model": "standard",
                "share_link": "http://localhost:8501/questionnaire/quest_001"
            }
        }


class QuestionnaireResponse(BaseModel):
    """问卷回答模型"""
    id: str
    questionnaire_id: str
    respondent_name: Optional[str] = None
    answers: Dict[str, Any] = Field(default_factory=dict, description="question_id -> answer")
    submitted_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "resp_001",
                "questionnaire_id": "quest_001",
                "respondent_name": "张三",
                "answers": {"q_001": "3-5年", "q_002": "熟练"},
                "submitted_at": "2024-01-01T00:00:00"
            }
        }


class MatchResult(BaseModel):
    """匹配结果模型"""
    id: str
    jd_id: str
    response_id: str
    overall_score: float = Field(ge=0, le=100, description="综合匹配度分数")
    dimension_scores: Dict[str, float] = Field(default_factory=dict, description="各维度得分")
    strengths: List[str] = Field(default_factory=list, description="优势列表")
    gaps: List[str] = Field(default_factory=list, description="差距列表")
    recommendations: List[str] = Field(default_factory=list, description="建议列表")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "match_001",
                "jd_id": "jd_001",
                "response_id": "resp_001",
                "overall_score": 85.0,
                "dimension_scores": {"技能匹配": 90.0, "经验匹配": 80.0},
                "strengths": ["Python经验丰富", "有大型项目经验"],
                "gaps": ["缺少K8s经验"],
                "recommendations": ["建议学习容器化技术"]
            }
        }


class CustomTemplate(BaseModel):
    """自定义模板模型"""
    id: str
    name: str
    template_type: str = Field(description="模板类型: parsing, evaluation, questionnaire")
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "tmpl_001",
                "name": "技术岗位解析模板",
                "template_type": "parsing",
                "config": {"custom_fields": ["技术栈", "团队规模"]},
                "created_at": "2024-01-01T00:00:00"
            }
        }
