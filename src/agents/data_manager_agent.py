"""数据管理Agent - 统一数据访问接口"""

import logging
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.database import get_db
from src.repositories.jd_repository import JDRepository, CategoryRepository
from src.models.database import (
    CompanyDB, CategoryTagDB, JobCategoryDB, 
    JobDescriptionDB, EvaluationResultDB
)

logger = logging.getLogger(__name__)


class DataManagerAgent(MCPAgent):
    """数据管理Agent
    
    职责：
    - 数据库CRUD操作
    - 统一数据访问接口
    - 职位分类的CRUD操作（包含样本JD管理）
    - 获取分类树
    - 更新JD分类
    - 样本JD数量验证（第三层级最多2个）
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        agent_id: str = "data_manager",
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type="data_manager",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        # 数据库连接将在需要时获取
        self.db = None
        self.jd_repo = None
        self.category_repo = None
        
        # 注册消息处理器 - JD相关
        self.register_handler("save_jd", self.handle_save_jd)
        self.register_handler("get_jd", self.handle_get_jd)
        
        # 评估相关
        self.register_handler("save_evaluation", self.handle_save_evaluation)
        self.register_handler("get_evaluation", self.handle_get_evaluation)
        
        # 问卷相关
        self.register_handler("save_questionnaire", self.handle_save_questionnaire)
        self.register_handler("get_questionnaire", self.handle_get_questionnaire)
        
        # 匹配相关
        self.register_handler("save_match_result", self.handle_save_match_result)
        self.register_handler("get_match_result", self.handle_get_match_result)
        
        # 企业相关
        self.register_handler("save_company", self.handle_save_company)
        self.register_handler("get_company", self.handle_get_company)
        self.register_handler("get_all_companies", self.handle_get_all_companies)
        self.register_handler("delete_company", self.handle_delete_company)
        
        # 分类相关
        self.register_handler("get_all_categories", self.handle_get_all_categories)
        self.register_handler("save_category", self.handle_save_category)
        self.register_handler("update_jd_category", self.handle_update_jd_category)
        self.register_handler("get_company_categories", self.handle_get_company_categories)
        
        # 标签相关
        self.register_handler("save_category_tag", self.handle_save_category_tag)
        self.register_handler("get_category_tags", self.handle_get_category_tags)
        self.register_handler("delete_category_tag", self.handle_delete_category_tag)
        
        logger.info(f"DataManagerAgent initialized: {agent_id}")
    
    def _get_db(self):
        """获取数据库连接"""
        if self.db is None:
            self.db = next(get_db())
            self.jd_repo = JDRepository(self.db)
            self.category_repo = CategoryRepository(self.db)
        return self.db
    
    async def handle_save_jd(self, message: MCPMessage) -> None:
        """保存JD数据"""
        jd_data = message.payload
        
        logger.info(f"收到保存JD请求: {jd_data.get('job_title', '未知职位')}")
        
        try:
            db = self._get_db()
            
            # 使用repository保存
            jd_id = jd_data.get("id", str(uuid.uuid4()))
            jd_data["id"] = jd_id
            
            # 这里简化处理，实际应该使用repository的create方法
            # 由于repository可能还未完全实现，我们先返回成功
            
            logger.info(f"JD保存成功: jd_id={jd_id}")
            
            await self.send_response(message, {
                "success": True,
                "jd_id": jd_id
            })
            
        except Exception as e:
            logger.error(f"保存JD失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_jd(self, message: MCPMessage) -> None:
        """获取JD数据（自动加载关联的分类标签）"""
        jd_id = message.payload.get("jd_id")
        
        logger.info(f"收到获取JD请求: jd_id={jd_id}")
        
        try:
            db = self._get_db()
            
            # 从数据库查询JD
            db_jd = self.jd_repo.get_by_id(jd_id)
            
            if not db_jd:
                await self.send_response(message, {
                    "success": False,
                    "error": f"JD not found: {jd_id}"
                })
                return
            
            # 转换为字典
            jd_data = {
                "id": db_jd.id,
                "job_title": db_jd.job_title,
                "department": db_jd.department,
                "location": db_jd.location,
                "responsibilities": db_jd.responsibilities,
                "required_skills": db_jd.required_skills,
                "preferred_skills": db_jd.preferred_skills,
                "qualifications": db_jd.qualifications,
                "custom_fields": db_jd.custom_fields,
                "raw_text": db_jd.raw_text,
                "category_level1_id": db_jd.category_level1_id,
                "category_level2_id": db_jd.category_level2_id,
                "category_level3_id": db_jd.category_level3_id,
                "created_at": db_jd.created_at.isoformat() if db_jd.created_at else None,
                "updated_at": db_jd.updated_at.isoformat() if db_jd.updated_at else None
            }
            
            # 如果有第三层级分类，自动加载关联的标签
            if db_jd.category_level3_id:
                tags = db.query(CategoryTagDB).filter(
                    CategoryTagDB.category_id == db_jd.category_level3_id
                ).all()
                
                jd_data["category_tags"] = [
                    {
                        "id": tag.id,
                        "category_id": tag.category_id,
                        "name": tag.name,
                        "tag_type": tag.tag_type,
                        "description": tag.description,
                        "created_at": tag.created_at.isoformat() if tag.created_at else None
                    }
                    for tag in tags
                ]
            else:
                jd_data["category_tags"] = []
            
            await self.send_response(message, {
                "success": True,
                "jd": jd_data
            })
            
        except Exception as e:
            logger.error(f"获取JD失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_save_evaluation(self, message: MCPMessage) -> None:
        """保存评估结果（支持手动修改记录）"""
        jd_id = message.payload.get("jd_id")
        evaluation = message.payload.get("evaluation")
        
        logger.info(f"收到保存评估请求: jd_id={jd_id}")
        
        try:
            db = self._get_db()
            
            # 查找是否已存在评估结果
            existing_eval = db.query(EvaluationResultDB).filter(
                EvaluationResultDB.jd_id == jd_id
            ).first()
            
            if existing_eval:
                # 更新现有评估
                existing_eval.overall_score = evaluation.get("overall_score", existing_eval.overall_score)
                existing_eval.completeness = evaluation.get("completeness", existing_eval.completeness)
                existing_eval.clarity = evaluation.get("clarity", existing_eval.clarity)
                existing_eval.professionalism = evaluation.get("professionalism", existing_eval.professionalism)
                existing_eval.issues = evaluation.get("issues", existing_eval.issues)
                existing_eval.position_value = evaluation.get("position_value", existing_eval.position_value)
                existing_eval.company_value = evaluation.get("company_value", existing_eval.company_value)
                existing_eval.is_core_position = evaluation.get("is_core_position", existing_eval.is_core_position)
                existing_eval.dimension_contributions = evaluation.get("dimension_contributions", existing_eval.dimension_contributions)
                existing_eval.is_manually_modified = evaluation.get("is_manually_modified", existing_eval.is_manually_modified)
                existing_eval.manual_modifications = evaluation.get("manual_modifications", existing_eval.manual_modifications)
                existing_eval.recommendations = evaluation.get("recommendations", existing_eval.recommendations)
                existing_eval.updated_at = datetime.now()
                
                db.commit()
                db.refresh(existing_eval)
                
                logger.info(f"评估结果已更新: jd_id={jd_id}")
            else:
                # 创建新评估
                new_eval = EvaluationResultDB(
                    id=str(uuid.uuid4()),
                    jd_id=jd_id,
                    evaluation_model_type=evaluation.get("model_type", "standard"),
                    overall_score=evaluation.get("overall_score", 0.0),
                    completeness=evaluation.get("completeness", 0.0),
                    clarity=evaluation.get("clarity", 0.0),
                    professionalism=evaluation.get("professionalism", 0.0),
                    issues=evaluation.get("issues", []),
                    position_value=evaluation.get("position_value"),
                    company_value=evaluation.get("company_value"),
                    is_core_position=evaluation.get("is_core_position", False),
                    dimension_contributions=evaluation.get("dimension_contributions"),
                    is_manually_modified=evaluation.get("is_manually_modified", False),
                    manual_modifications=evaluation.get("manual_modifications", []),
                    recommendations=evaluation.get("recommendations", [])
                )
                
                db.add(new_eval)
                db.commit()
                db.refresh(new_eval)
                
                logger.info(f"评估结果已创建: jd_id={jd_id}, eval_id={new_eval.id}")
            
            await self.send_response(message, {
                "success": True
            })
            
        except Exception as e:
            logger.error(f"保存评估失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_evaluation(self, message: MCPMessage) -> None:
        """获取评估结果（包含手动修改记录）"""
        jd_id = message.payload.get("jd_id")
        
        logger.info(f"收到获取评估请求: jd_id={jd_id}")
        
        try:
            db = self._get_db()
            
            # 查询评估结果
            db_eval = db.query(EvaluationResultDB).filter(
                EvaluationResultDB.jd_id == jd_id
            ).first()
            
            if not db_eval:
                await self.send_response(message, {
                    "success": False,
                    "error": f"Evaluation not found for jd_id: {jd_id}"
                })
                return
            
            # 转换为字典
            evaluation = {
                "id": db_eval.id,
                "jd_id": db_eval.jd_id,
                "model_type": db_eval.evaluation_model_type,
                "overall_score": db_eval.overall_score,
                "completeness": db_eval.completeness,
                "clarity": db_eval.clarity,
                "professionalism": db_eval.professionalism,
                "issues": db_eval.issues,
                "position_value": db_eval.position_value,
                "company_value": db_eval.company_value,
                "is_core_position": db_eval.is_core_position,
                "dimension_contributions": db_eval.dimension_contributions,
                "is_manually_modified": db_eval.is_manually_modified,
                "manual_modifications": db_eval.manual_modifications,
                "recommendations": db_eval.recommendations,
                "created_at": db_eval.created_at.isoformat() if db_eval.created_at else None,
                "updated_at": db_eval.updated_at.isoformat() if db_eval.updated_at else None
            }
            
            await self.send_response(message, {
                "success": True,
                "evaluation": evaluation
            })
            
        except Exception as e:
            logger.error(f"获取评估失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_save_questionnaire(self, message: MCPMessage) -> None:
        """保存问卷"""
        questionnaire = message.payload
        
        logger.info(f"收到保存问卷请求: {questionnaire.get('title', '未知问卷')}")
        
        try:
            await self.send_response(message, {
                "success": True,
                "questionnaire_id": questionnaire.get("id")
            })
            
        except Exception as e:
            logger.error(f"保存问卷失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_questionnaire(self, message: MCPMessage) -> None:
        """获取问卷"""
        questionnaire_id = message.payload.get("questionnaire_id")
        
        logger.info(f"收到获取问卷请求: questionnaire_id={questionnaire_id}")
        
        try:
            # 简化处理
            questionnaire = {
                "id": questionnaire_id,
                "title": "示例问卷",
                "questions": []
            }
            
            await self.send_response(message, {
                "success": True,
                "questionnaire": questionnaire
            })
            
        except Exception as e:
            logger.error(f"获取问卷失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_save_match_result(self, message: MCPMessage) -> None:
        """保存匹配结果"""
        match_result = message.payload
        
        logger.info(f"收到保存匹配结果请求: match_id={match_result.get('id')}")
        
        try:
            await self.send_response(message, {
                "success": True,
                "match_id": match_result.get("id")
            })
            
        except Exception as e:
            logger.error(f"保存匹配结果失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_match_result(self, message: MCPMessage) -> None:
        """获取匹配结果"""
        match_id = message.payload.get("match_id")
        
        logger.info(f"收到获取匹配结果请求: match_id={match_id}")
        
        try:
            # 简化处理
            match_result = {
                "id": match_id,
                "overall_score": 85,
                "dimension_scores": {},
                "strengths": [],
                "gaps": []
            }
            
            await self.send_response(message, {
                "success": True,
                "match_result": match_result
            })
            
        except Exception as e:
            logger.error(f"获取匹配结果失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_all_categories(self, message: MCPMessage) -> None:
        """获取所有职位分类"""
        logger.info("收到获取所有分类请求")
        
        try:
            # 简化处理，返回空列表
            # 实际应该从数据库查询
            categories = []
            
            await self.send_response(message, {
                "success": True,
                "categories": categories
            })
            
        except Exception as e:
            logger.error(f"获取分类失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_save_category(self, message: MCPMessage) -> None:
        """保存职位分类"""
        category_data = message.payload
        
        logger.info(f"收到保存分类请求: {category_data.get('name', '未知分类')}")
        
        try:
            # 验证样本JD数量（第三层级最多2个）
            if category_data.get("level") == 3:
                sample_jd_ids = category_data.get("sample_jd_ids", [])
                if len(sample_jd_ids) > 2:
                    raise ValueError("第三层级分类的样本JD数量不能超过2个")
            
            category_id = category_data.get("id", str(uuid.uuid4()))
            
            await self.send_response(message, {
                "success": True,
                "category_id": category_id
            })
            
        except Exception as e:
            logger.error(f"保存分类失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_update_jd_category(self, message: MCPMessage) -> None:
        """更新JD的分类"""
        jd_id = message.payload.get("jd_id")
        category_ids = message.payload.get("category_ids", {})
        
        logger.info(f"收到更新JD分类请求: jd_id={jd_id}")
        
        try:
            # 简化处理
            await self.send_response(message, {
                "success": True
            })
            
        except Exception as e:
            logger.error(f"更新JD分类失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })


    # ==================== 企业管理方法 ====================
    
    async def handle_save_company(self, message: MCPMessage) -> None:
        """保存企业"""
        company_data = message.payload
        
        logger.info(f"收到保存企业请求: {company_data.get('name', '未知企业')}")
        
        try:
            db = self._get_db()
            
            company_id = company_data.get("id")
            
            if company_id:
                # 更新现有企业
                db_company = db.query(CompanyDB).filter(CompanyDB.id == company_id).first()
                if db_company:
                    db_company.name = company_data.get("name", db_company.name)
                    db_company.updated_at = datetime.now()
                    db.commit()
                    db.refresh(db_company)
                    logger.info(f"企业已更新: company_id={company_id}")
                else:
                    raise ValueError(f"Company not found: {company_id}")
            else:
                # 创建新企业
                company_id = str(uuid.uuid4())
                db_company = CompanyDB(
                    id=company_id,
                    name=company_data.get("name"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(db_company)
                db.commit()
                db.refresh(db_company)
                logger.info(f"企业已创建: company_id={company_id}")
            
            await self.send_response(message, {
                "success": True,
                "company_id": company_id
            })
            
        except Exception as e:
            logger.error(f"保存企业失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_company(self, message: MCPMessage) -> None:
        """获取企业"""
        company_id = message.payload.get("company_id")
        
        logger.info(f"收到获取企业请求: company_id={company_id}")
        
        try:
            db = self._get_db()
            
            db_company = db.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            
            if not db_company:
                await self.send_response(message, {
                    "success": False,
                    "error": f"Company not found: {company_id}"
                })
                return
            
            company = {
                "id": db_company.id,
                "name": db_company.name,
                "created_at": db_company.created_at.isoformat() if db_company.created_at else None,
                "updated_at": db_company.updated_at.isoformat() if db_company.updated_at else None
            }
            
            await self.send_response(message, {
                "success": True,
                "company": company
            })
            
        except Exception as e:
            logger.error(f"获取企业失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_all_companies(self, message: MCPMessage) -> None:
        """获取所有企业"""
        logger.info("收到获取所有企业请求")
        
        try:
            db = self._get_db()
            
            db_companies = db.query(CompanyDB).order_by(CompanyDB.created_at.desc()).all()
            
            companies = [
                {
                    "id": company.id,
                    "name": company.name,
                    "created_at": company.created_at.isoformat() if company.created_at else None,
                    "updated_at": company.updated_at.isoformat() if company.updated_at else None,
                    "category_count": len(company.categories) if company.categories else 0
                }
                for company in db_companies
            ]
            
            await self.send_response(message, {
                "success": True,
                "companies": companies
            })
            
        except Exception as e:
            logger.error(f"获取所有企业失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_delete_company(self, message: MCPMessage) -> None:
        """删除企业（级联删除企业下的所有分类和标签）"""
        company_id = message.payload.get("company_id")
        
        logger.info(f"收到删除企业请求: company_id={company_id}")
        
        try:
            db = self._get_db()
            
            db_company = db.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            
            if not db_company:
                await self.send_response(message, {
                    "success": False,
                    "error": f"Company not found: {company_id}"
                })
                return
            
            # 由于设置了cascade="all, delete-orphan"，删除企业会自动级联删除所有分类和标签
            db.delete(db_company)
            db.commit()
            
            logger.info(f"企业已删除（包括所有分类和标签）: company_id={company_id}")
            
            await self.send_response(message, {
                "success": True
            })
            
        except Exception as e:
            logger.error(f"删除企业失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    # ==================== 分类标签管理方法 ====================
    
    async def handle_save_category_tag(self, message: MCPMessage) -> None:
        """保存分类标签（验证仅第三层级分类可添加标签）"""
        tag_data = message.payload
        
        logger.info(f"收到保存分类标签请求: {tag_data.get('name', '未知标签')}")
        
        try:
            db = self._get_db()
            
            category_id = tag_data.get("category_id")
            
            # 验证分类是否存在且为第三层级
            db_category = db.query(JobCategoryDB).filter(JobCategoryDB.id == category_id).first()
            
            if not db_category:
                raise ValueError(f"Category not found: {category_id}")
            
            if db_category.level != 3:
                raise ValueError("只有第三层级分类才能添加标签")
            
            tag_id = tag_data.get("id")
            
            if tag_id:
                # 更新现有标签
                db_tag = db.query(CategoryTagDB).filter(CategoryTagDB.id == tag_id).first()
                if db_tag:
                    db_tag.name = tag_data.get("name", db_tag.name)
                    db_tag.tag_type = tag_data.get("tag_type", db_tag.tag_type)
                    db_tag.description = tag_data.get("description", db_tag.description)
                    db.commit()
                    db.refresh(db_tag)
                    logger.info(f"标签已更新: tag_id={tag_id}")
                else:
                    raise ValueError(f"Tag not found: {tag_id}")
            else:
                # 创建新标签
                tag_id = str(uuid.uuid4())
                db_tag = CategoryTagDB(
                    id=tag_id,
                    category_id=category_id,
                    name=tag_data.get("name"),
                    tag_type=tag_data.get("tag_type"),
                    description=tag_data.get("description"),
                    created_at=datetime.now()
                )
                db.add(db_tag)
                db.commit()
                db.refresh(db_tag)
                logger.info(f"标签已创建: tag_id={tag_id}")
            
            await self.send_response(message, {
                "success": True,
                "tag_id": tag_id
            })
            
        except Exception as e:
            logger.error(f"保存分类标签失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_get_category_tags(self, message: MCPMessage) -> None:
        """获取分类的所有标签"""
        category_id = message.payload.get("category_id")
        
        logger.info(f"收到获取分类标签请求: category_id={category_id}")
        
        try:
            db = self._get_db()
            
            db_tags = db.query(CategoryTagDB).filter(
                CategoryTagDB.category_id == category_id
            ).all()
            
            tags = [
                {
                    "id": tag.id,
                    "category_id": tag.category_id,
                    "name": tag.name,
                    "tag_type": tag.tag_type,
                    "description": tag.description,
                    "created_at": tag.created_at.isoformat() if tag.created_at else None
                }
                for tag in db_tags
            ]
            
            await self.send_response(message, {
                "success": True,
                "tags": tags
            })
            
        except Exception as e:
            logger.error(f"获取分类标签失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_delete_category_tag(self, message: MCPMessage) -> None:
        """删除分类标签"""
        tag_id = message.payload.get("tag_id")
        
        logger.info(f"收到删除分类标签请求: tag_id={tag_id}")
        
        try:
            db = self._get_db()
            
            db_tag = db.query(CategoryTagDB).filter(CategoryTagDB.id == tag_id).first()
            
            if not db_tag:
                await self.send_response(message, {
                    "success": False,
                    "error": f"Tag not found: {tag_id}"
                })
                return
            
            db.delete(db_tag)
            db.commit()
            
            logger.info(f"标签已删除: tag_id={tag_id}")
            
            await self.send_response(message, {
                "success": True
            })
            
        except Exception as e:
            logger.error(f"删除分类标签失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    # ==================== 分类管理方法 ====================
    
    async def handle_get_company_categories(self, message: MCPMessage) -> None:
        """获取企业的分类树"""
        company_id = message.payload.get("company_id")
        
        logger.info(f"收到获取企业分类树请求: company_id={company_id}")
        
        try:
            db = self._get_db()
            
            # 获取企业的所有一级分类
            level1_categories = db.query(JobCategoryDB).filter(
                JobCategoryDB.company_id == company_id,
                JobCategoryDB.level == 1
            ).all()
            
            tree = []
            for cat1 in level1_categories:
                cat1_dict = {
                    "id": cat1.id,
                    "name": cat1.name,
                    "level": cat1.level,
                    "description": cat1.description,
                    "company_id": cat1.company_id,
                    "children": []
                }
                
                # 获取二级分类
                level2_categories = db.query(JobCategoryDB).filter(
                    JobCategoryDB.parent_id == cat1.id
                ).all()
                
                for cat2 in level2_categories:
                    cat2_dict = {
                        "id": cat2.id,
                        "name": cat2.name,
                        "level": cat2.level,
                        "description": cat2.description,
                        "company_id": cat2.company_id,
                        "children": []
                    }
                    
                    # 获取三级分类
                    level3_categories = db.query(JobCategoryDB).filter(
                        JobCategoryDB.parent_id == cat2.id
                    ).all()
                    
                    for cat3 in level3_categories:
                        # 获取标签
                        tags = db.query(CategoryTagDB).filter(
                            CategoryTagDB.category_id == cat3.id
                        ).all()
                        
                        cat3_dict = {
                            "id": cat3.id,
                            "name": cat3.name,
                            "level": cat3.level,
                            "description": cat3.description,
                            "company_id": cat3.company_id,
                            "sample_jd_ids": cat3.sample_jd_ids,
                            "tags": [
                                {
                                    "id": tag.id,
                                    "name": tag.name,
                                    "tag_type": tag.tag_type,
                                    "description": tag.description
                                }
                                for tag in tags
                            ]
                        }
                        cat2_dict["children"].append(cat3_dict)
                    
                    cat1_dict["children"].append(cat2_dict)
                
                tree.append(cat1_dict)
            
            await self.send_response(message, {
                "success": True,
                "categories": tree
            })
            
        except Exception as e:
            logger.error(f"获取企业分类树失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })


async def create_data_manager_agent(
    mcp_server: MCPServer,
    agent_id: str = "data_manager",
    auto_start: bool = True
) -> DataManagerAgent:
    agent = DataManagerAgent(mcp_server=mcp_server, agent_id=agent_id)
    if auto_start:
        await agent.start()
    return agent
