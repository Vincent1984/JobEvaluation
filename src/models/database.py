"""SQLAlchemy数据库模型"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class CompanyDB(Base):
    """企业表"""
    __tablename__ = "companies"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    categories = relationship("JobCategoryDB", back_populates="company", cascade="all, delete-orphan")


class CategoryTagDB(Base):
    """分类标签表（仅用于第三层级分类）"""
    __tablename__ = "category_tags"
    
    id = Column(String(50), primary_key=True)
    category_id = Column(String(50), ForeignKey("job_categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    tag_type = Column(String(100), nullable=False)  # 战略重要性、业务价值、技能稀缺性、市场竞争度、发展潜力、风险等级
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    category = relationship("JobCategoryDB", back_populates="tags")
    
    # 索引
    __table_args__ = (
        Index('idx_tags_category', 'category_id'),
    )


class JobCategoryDB(Base):
    """职位分类表（支持3层级）"""
    __tablename__ = "job_categories"
    
    id = Column(String(50), primary_key=True)
    company_id = Column(String(50), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    level = Column(Integer, nullable=False)  # 1=一级, 2=二级, 3=三级
    parent_id = Column(String(50), ForeignKey("job_categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    sample_jd_ids = Column(JSON, default=list)  # 样本JD的ID列表（仅第三层级，1-2个）
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    company = relationship("CompanyDB", back_populates="categories")
    parent = relationship("JobCategoryDB", remote_side=[id], backref="children")
    tags = relationship("CategoryTagDB", back_populates="category", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_categories_company', 'company_id'),
        Index('idx_categories_level', 'level'),
        Index('idx_categories_parent', 'parent_id'),
    )
    

class JobDescriptionDB(Base):
    """岗位JD表"""
    __tablename__ = "job_descriptions"
    
    id = Column(String(50), primary_key=True)
    job_title = Column(String(200), nullable=False)
    department = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    responsibilities = Column(JSON, default=list)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    qualifications = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    raw_text = Column(Text, nullable=False)
    
    # 职位分类（最多3层）
    category_level1_id = Column(String(50), ForeignKey("job_categories.id"), nullable=True)
    category_level2_id = Column(String(50), ForeignKey("job_categories.id"), nullable=True)
    category_level3_id = Column(String(50), ForeignKey("job_categories.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    category_level1 = relationship("JobCategoryDB", foreign_keys=[category_level1_id])
    category_level2 = relationship("JobCategoryDB", foreign_keys=[category_level2_id])
    category_level3 = relationship("JobCategoryDB", foreign_keys=[category_level3_id])


class EvaluationResultDB(Base):
    """评估结果表"""
    __tablename__ = "evaluation_results"
    
    id = Column(String(50), primary_key=True)
    jd_id = Column(String(50), ForeignKey("job_descriptions.id"), nullable=False)
    evaluation_model_type = Column(String(50), nullable=False)  # standard, mercer_ipe, factor_comparison
    
    # 质量评分
    overall_score = Column(Float, nullable=False)
    completeness = Column(Float, nullable=False)
    clarity = Column(Float, nullable=False)
    professionalism = Column(Float, nullable=False)
    issues = Column(JSON, default=list)
    
    # 岗位价值评估（可选）
    position_value = Column(JSON, nullable=True)
    
    # 综合评估字段（新增）
    company_value = Column(String(50), nullable=True)  # 高价值/中价值/低价值
    is_core_position = Column(Boolean, default=False)  # 是否核心岗位
    dimension_contributions = Column(JSON, nullable=True)  # 三个维度的贡献度百分比
    
    # 手动修改支持（新增）
    is_manually_modified = Column(Boolean, default=False)  # 是否手动修改过
    manual_modifications = Column(JSON, default=list)  # 修改历史记录
    
    # 优化建议
    recommendations = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    job_description = relationship("JobDescriptionDB", backref="evaluations")
    
    # 索引
    __table_args__ = (
        Index('idx_evaluation_jd', 'jd_id'),
        Index('idx_evaluation_company_value', 'company_value'),
        Index('idx_evaluation_core_position', 'is_core_position'),
        {'extend_existing': True}
    )


class QuestionnaireDB(Base):
    """问卷表"""
    __tablename__ = "questionnaires"
    
    id = Column(String(50), primary_key=True)
    jd_id = Column(String(50), ForeignKey("job_descriptions.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(JSON, default=list)  # 问题列表
    evaluation_model = Column(String(50), nullable=False)
    share_link = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    job_description = relationship("JobDescriptionDB", backref="questionnaires")


class QuestionnaireResponseDB(Base):
    """问卷回答表"""
    __tablename__ = "questionnaire_responses"
    
    id = Column(String(50), primary_key=True)
    questionnaire_id = Column(String(50), ForeignKey("questionnaires.id"), nullable=False)
    respondent_name = Column(String(200), nullable=True)
    answers = Column(JSON, default=dict)  # question_id -> answer
    submitted_at = Column(DateTime, default=datetime.now)
    
    # 关系
    questionnaire = relationship("QuestionnaireDB", backref="responses")


class MatchResultDB(Base):
    """匹配结果表"""
    __tablename__ = "match_results"
    
    id = Column(String(50), primary_key=True)
    jd_id = Column(String(50), ForeignKey("job_descriptions.id"), nullable=False)
    response_id = Column(String(50), ForeignKey("questionnaire_responses.id"), nullable=False)
    
    overall_score = Column(Float, nullable=False)
    dimension_scores = Column(JSON, default=dict)
    strengths = Column(JSON, default=list)
    gaps = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    job_description = relationship("JobDescriptionDB", backref="match_results")
    response = relationship("QuestionnaireResponseDB", backref="match_results")


class CustomTemplateDB(Base):
    """自定义模板表"""
    __tablename__ = "custom_templates"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    template_type = Column(String(50), nullable=False)  # parsing, evaluation, questionnaire
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.now)
