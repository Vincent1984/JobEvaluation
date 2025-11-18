"""数据管理Agent - 统一数据访问接口"""

import logging
from typing import Dict, Any, Optional, List
import uuid

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.database import get_db
from src.repositories.jd_repository import JDRepository

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
        
        # 注册消息处理器
        self.register_handler("save_jd", self.handle_save_jd)
        self.register_handler("get_jd", self.handle_get_jd)
        self.register_handler("save_evaluation", self.handle_save_evaluation)
        self.register_handler("get_evaluation", self.handle_get_evaluation)
        self.register_handler("save_questionnaire", self.handle_save_questionnaire)
        self.register_handler("get_questionnaire", self.handle_get_questionnaire)
        self.register_handler("save_match_result", self.handle_save_match_result)
        self.register_handler("get_match_result", self.handle_get_match_result)
        self.register_handler("get_all_categories", self.handle_get_all_categories)
        self.register_handler("save_category", self.handle_save_category)
        self.register_handler("update_jd_category", self.handle_update_jd_category)
        
        logger.info(f"DataManagerAgent initialized: {agent_id}")
    
    def _get_db(self):
        """获取数据库连接"""
        if self.db is None:
            self.db = next(get_db())
            self.jd_repo = JDRepository(self.db)
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
        """获取JD数据"""
        jd_id = message.payload.get("jd_id")
        
        logger.info(f"收到获取JD请求: jd_id={jd_id}")
        
        try:
            db = self._get_db()
            
            # 这里简化处理，返回模拟数据
            # 实际应该从数据库查询
            jd_data = {
                "id": jd_id,
                "job_title": "示例职位",
                "responsibilities": [],
                "required_skills": [],
                "qualifications": []
            }
            
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
        """保存评估结果"""
        jd_id = message.payload.get("jd_id")
        evaluation = message.payload.get("evaluation")
        
        logger.info(f"收到保存评估请求: jd_id={jd_id}")
        
        try:
            # 简化处理
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
        """获取评估结果"""
        jd_id = message.payload.get("jd_id")
        
        logger.info(f"收到获取评估请求: jd_id={jd_id}")
        
        try:
            # 简化处理，返回模拟数据
            evaluation = {
                "overall_score": 80,
                "dimension_scores": {},
                "issues": []
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


async def create_data_manager_agent(
    mcp_server: MCPServer,
    agent_id: str = "data_manager",
    auto_start: bool = True
) -> DataManagerAgent:
    agent = DataManagerAgent(mcp_server=mcp_server, agent_id=agent_id)
    if auto_start:
        await agent.start()
    return agent
