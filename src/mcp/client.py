"""MCP Client - 简化的 Agent 调用接口

为 API 和 UI 层提供简单的 Agent 调用方法
"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from .server import MCPServer
from .message import MCPMessage
from .context import create_context
from ..models.schemas import (
    JobDescription,
    EvaluationResult,
    QualityScore,
    EvaluationModel
)


class MCPClient:
    """MCP 客户端 - 简化 Agent 调用"""
    
    def __init__(self, mcp_server: Optional[MCPServer] = None):
        """初始化 MCP 客户端
        
        Args:
            mcp_server: MCP 服务器实例（如果为 None，会自动创建）
        """
        self.mcp_server = mcp_server
        self._initialized = False
    
    async def _ensure_initialized(self):
        """确保 MCP Server 已初始化"""
        if not self._initialized:
            if not self.mcp_server:
                self.mcp_server = MCPServer()
            
            # 启动必要的 Agents
            await self._start_agents()
            self._initialized = True
    
    async def _start_agents(self):
        """启动必要的 Agents"""
        from ..agents.parser_agent import ParserAgent
        from ..agents.evaluator_agent import EvaluatorAgent
        from ..agents.data_manager_agent import DataManagerAgent
        from ..core.llm_client import deepseek_client
        
        # 先连接并启动 MCP Server
        try:
            await self.mcp_server.connect()
            await self.mcp_server.start()
        except Exception as e:
            # 如果 Redis 连接失败，记录警告但继续（开发模式）
            import logging
            logging.warning(f"MCP Server connection failed: {e}. Running in standalone mode.")
        
        # 创建并启动 Agents
        parser = ParserAgent(
            mcp_server=self.mcp_server,
            llm_client=deepseek_client,
            agent_id="parser"
        )
        
        evaluator = EvaluatorAgent(
            mcp_server=self.mcp_server,
            llm_client=deepseek_client,
            agent_id="evaluator"
        )
        
        data_manager = DataManagerAgent(
            mcp_server=self.mcp_server,
            agent_id="data_manager"
        )
        
        # 启动 Agents
        await parser.start()
        await evaluator.start()
        await data_manager.start()
    
    async def _call_agent(
        self,
        receiver: str,
        action: str,
        payload: Dict[str, Any],
        timeout: float = 60.0
    ) -> MCPMessage:
        """调用 Agent 的通用方法
        
        Args:
            receiver: 接收者 Agent ID
            action: 动作名称
            payload: 消息负载
            timeout: 超时时间
            
        Returns:
            Agent 的响应消息
        """
        await self._ensure_initialized()
        
        # 创建上下文
        context = create_context(
            task_id=str(uuid.uuid4()),
            workflow_type="mcp_client",
            metadata={"client": "mcp_client"}
        )
        
        # 发送请求
        response = await self.mcp_server.send_request(
            sender="mcp_client",
            receiver=receiver,
            action=action,
            payload=payload,
            context_id=context.context_id,
            timeout=timeout
        )
        
        return response
    
    async def parse_jd(self, jd_text: str) -> JobDescription:
        """解析 JD 文本
        
        Args:
            jd_text: JD 文本
            
        Returns:
            JobDescription 对象
            
        Raises:
            Exception: 解析失败
        """
        # 调用 ParserAgent
        response = await self._call_agent(
            receiver="parser",
            action="parse_jd",
            payload={"jd_text": jd_text}
        )
        
        # 检查响应
        if not response.payload.get("success", True):
            error = response.payload.get("error", "解析失败")
            raise Exception(f"JD 解析失败: {error}")
        
        # 构建 JobDescription 对象
        parsed_data = response.payload.get("parsed_data", {})
        jd_id = response.payload.get("jd_id")
        
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
            created_at=datetime.fromisoformat(parsed_data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(parsed_data.get("updated_at", datetime.now().isoformat()))
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
            
        Raises:
            Exception: 评估失败
        """
        # 调用 EvaluatorAgent
        response = await self._call_agent(
            receiver="evaluator",
            action="evaluate_quality",
            payload={
                "jd_id": jd_id,
                "model_type": model_type.value
            }
        )
        
        # 检查响应
        if not response.payload.get("success", True):
            error = response.payload.get("error", "评估失败")
            raise Exception(f"JD 评估失败: {error}")
        
        # 构建 EvaluationResult 对象
        eval_data = response.payload.get("evaluation", {})
        quality_data = eval_data.get("quality_score", {})
        
        quality_score = QualityScore(
            overall_score=quality_data.get("overall_score", 0.0),
            completeness=quality_data.get("completeness", 0.0),
            clarity=quality_data.get("clarity", 0.0),
            professionalism=quality_data.get("professionalism", 0.0),
            issues=quality_data.get("issues", [])
        )
        
        eval_id = eval_data.get("id", f"eval_{uuid.uuid4().hex[:8]}")
        
        evaluation = EvaluationResult(
            id=eval_id,
            jd_id=jd_id,
            model_type=model_type,
            quality_score=quality_score,
            recommendations=eval_data.get("recommendations", []),
            created_at=datetime.fromisoformat(eval_data.get("created_at", datetime.now().isoformat()))
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
            model_type: 评估模型类型
            
        Returns:
            包含 jd 和 evaluation 的字典
        """
        # 1. 解析 JD
        jd = await self.parse_jd(jd_text)
        
        # 2. 评估质量
        evaluation = await self.evaluate_jd(jd.id, model_type)
        
        return {
            "jd": jd,
            "evaluation": evaluation
        }
    
    async def get_jd(self, jd_id: str) -> Optional[JobDescription]:
        """获取 JD
        
        Args:
            jd_id: JD ID
            
        Returns:
            JobDescription 对象或 None
        """
        try:
            response = await self._call_agent(
                receiver="data_manager",
                action="get_jd",
                payload={"jd_id": jd_id}
            )
            
            if response.payload.get("success"):
                jd_data = response.payload.get("jd")
                if jd_data:
                    return JobDescription(**jd_data)
        except Exception:
            pass
        
        return None
    
    async def shutdown(self):
        """关闭客户端，停止所有 Agents"""
        if self.mcp_server and self._initialized:
            # 停止所有 Agents
            for agent in self.mcp_server.agents.values():
                await agent.stop()


# 全局客户端实例（单例模式）
_mcp_client_instance: Optional[MCPClient] = None


def get_mcp_client(mcp_server: Optional[MCPServer] = None) -> MCPClient:
    """获取 MCP 客户端实例（单例模式）
    
    Args:
        mcp_server: MCP 服务器实例（可选）
        
    Returns:
        MCPClient 实例
    """
    global _mcp_client_instance
    
    if _mcp_client_instance is None:
        _mcp_client_instance = MCPClient(mcp_server)
    
    return _mcp_client_instance
