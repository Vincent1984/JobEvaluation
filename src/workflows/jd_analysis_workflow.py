"""
JD完整分析工作流

实现解析→评估→优化的完整流程，通过MCP协调多个Agent
"""

import uuid
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from src.mcp.server import MCPServer
from src.mcp.context import MCPContext
from src.mcp.message import MCPMessage

logger = logging.getLogger(__name__)


class JDAnalysisWorkflow:
    """JD分析工作流 - 通过MCP协调多个Agent"""
    
    def __init__(self, mcp_server: MCPServer):
        """
        初始化JD分析工作流
        
        Args:
            mcp_server: MCP服务器实例
        """
        self.mcp_server = mcp_server
        self.workflow_name = "jd_analysis"
    
    async def execute_full_analysis(
        self,
        jd_text: str,
        evaluation_model: str = "standard",
        custom_template: Optional[Dict] = None,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """
        执行完整的JD分析流程：解析 → 评估 → 优化
        
        Args:
            jd_text: 岗位JD文本
            evaluation_model: 评估模型类型 (standard/mercer_ipe/factor_comparison)
            custom_template: 自定义解析模板
            timeout: 工作流超时时间（秒）
        
        Returns:
            包含完整分析结果的字典:
            {
                "jd_id": "JD唯一标识",
                "parsed_data": {...},  # 解析结果
                "evaluation": {...},   # 评估结果
                "suggestions": {...},  # 优化建议
                "workflow_id": "工作流ID",
                "status": "completed/failed",
                "execution_time": 123.45
            }
        """
        start_time = time.time()
        workflow_id = str(uuid.uuid4())
        
        logger.info(f"开始JD分析工作流 [workflow_id={workflow_id}]")
        
        try:
            # 1. 创建工作流上下文
            context = await self._create_workflow_context(
                workflow_id=workflow_id,
                jd_text=jd_text,
                evaluation_model=evaluation_model,
                custom_template=custom_template
            )
            
            # 2. 步骤1: 解析JD
            logger.info(f"步骤1: 解析JD [workflow_id={workflow_id}]")
            parse_result = await self._parse_jd(
                context_id=context.context_id,
                jd_text=jd_text,
                custom_template=custom_template,
                timeout=timeout / 3
            )
            
            if not parse_result.get("success"):
                raise Exception(f"JD解析失败: {parse_result.get('error')}")
            
            jd_id = parse_result["jd_id"]
            parsed_data = parse_result["parsed_data"]
            
            # 更新上下文
            context.shared_data["jd_id"] = jd_id
            context.shared_data["parsed_data"] = parsed_data
            context.shared_data["step"] = "evaluation"
            await self.mcp_server.update_context(context)
            
            # 3. 步骤2: 评估质量
            logger.info(f"步骤2: 评估JD质量 [workflow_id={workflow_id}, jd_id={jd_id}]")
            eval_result = await self._evaluate_quality(
                context_id=context.context_id,
                jd_id=jd_id,
                evaluation_model=evaluation_model,
                timeout=timeout / 3
            )
            
            if not eval_result.get("success"):
                raise Exception(f"质量评估失败: {eval_result.get('error')}")
            
            evaluation = eval_result["evaluation"]
            
            # 更新上下文
            context.shared_data["evaluation"] = evaluation
            context.shared_data["step"] = "optimization"
            await self.mcp_server.update_context(context)
            
            # 4. 步骤3: 生成优化建议
            logger.info(f"步骤3: 生成优化建议 [workflow_id={workflow_id}, jd_id={jd_id}]")
            opt_result = await self._generate_suggestions(
                context_id=context.context_id,
                jd_id=jd_id,
                timeout=timeout / 3
            )
            
            if not opt_result.get("success"):
                raise Exception(f"优化建议生成失败: {opt_result.get('error')}")
            
            suggestions = opt_result["suggestions"]
            
            # 5. 汇总结果
            execution_time = time.time() - start_time
            
            result = {
                "jd_id": jd_id,
                "parsed_data": parsed_data,
                "evaluation": evaluation,
                "suggestions": suggestions,
                "workflow_id": workflow_id,
                "status": "completed",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # 更新上下文为完成状态
            context.shared_data["result"] = result
            context.shared_data["step"] = "completed"
            context.shared_data["status"] = "completed"
            await self.mcp_server.update_context(context)
            
            logger.info(
                f"JD分析工作流完成 [workflow_id={workflow_id}, "
                f"jd_id={jd_id}, execution_time={execution_time:.2f}s]"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                f"JD分析工作流失败 [workflow_id={workflow_id}, "
                f"error={error_msg}, execution_time={execution_time:.2f}s]"
            )
            
            # 更新上下文为失败状态
            try:
                context.shared_data["status"] = "failed"
                context.shared_data["error"] = error_msg
                await self.mcp_server.update_context(context)
            except:
                pass
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": error_msg,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _create_workflow_context(
        self,
        workflow_id: str,
        jd_text: str,
        evaluation_model: str,
        custom_template: Optional[Dict]
    ) -> MCPContext:
        """创建工作流上下文"""
        context = MCPContext(
            context_id=workflow_id,
            task_id=workflow_id,
            shared_data={
                "workflow": "jd_analysis",
                "jd_text": jd_text,
                "evaluation_model": evaluation_model,
                "custom_template": custom_template,
                "step": "parsing",
                "status": "running",
                "start_time": time.time()
            },
            metadata={
                "workflow_type": "jd_analysis",
                "created_at": datetime.now().isoformat()
            }
        )
        
        await self.mcp_server.update_context(context)
        logger.debug(f"创建工作流上下文 [context_id={context.context_id}]")
        
        return context
    
    async def _parse_jd(
        self,
        context_id: str,
        jd_text: str,
        custom_template: Optional[Dict],
        timeout: float
    ) -> Dict[str, Any]:
        """
        步骤1: 解析JD
        
        通过MCP向Parser Agent发送解析请求
        """
        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender="workflow",
            receiver="parser",
            message_type="request",
            action="parse_jd",
            payload={
                "jd_text": jd_text,
                "custom_fields": custom_template or {}
            },
            context_id=context_id,
            timestamp=time.time()
        )
        
        try:
            await self.mcp_server.send_message(message)
            response = await self.mcp_server.wait_for_response(
                message.message_id,
                timeout=timeout
            )
            
            return {
                "success": True,
                "jd_id": response.payload.get("jd_id"),
                "parsed_data": response.payload.get("parsed_data")
            }
            
        except TimeoutError:
            logger.error(f"JD解析超时 [context_id={context_id}]")
            return {
                "success": False,
                "error": "JD解析超时"
            }
        except Exception as e:
            logger.error(f"JD解析异常 [context_id={context_id}, error={str(e)}]")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _evaluate_quality(
        self,
        context_id: str,
        jd_id: str,
        evaluation_model: str,
        timeout: float
    ) -> Dict[str, Any]:
        """
        步骤2: 评估JD质量
        
        通过MCP向Evaluator Agent发送评估请求
        """
        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender="workflow",
            receiver="evaluator",
            message_type="request",
            action="evaluate_quality",
            payload={
                "jd_id": jd_id,
                "model_type": evaluation_model
            },
            context_id=context_id,
            timestamp=time.time()
        )
        
        try:
            await self.mcp_server.send_message(message)
            response = await self.mcp_server.wait_for_response(
                message.message_id,
                timeout=timeout
            )
            
            return {
                "success": True,
                "evaluation": response.payload
            }
            
        except TimeoutError:
            logger.error(f"质量评估超时 [context_id={context_id}, jd_id={jd_id}]")
            return {
                "success": False,
                "error": "质量评估超时"
            }
        except Exception as e:
            logger.error(
                f"质量评估异常 [context_id={context_id}, "
                f"jd_id={jd_id}, error={str(e)}]"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_suggestions(
        self,
        context_id: str,
        jd_id: str,
        timeout: float
    ) -> Dict[str, Any]:
        """
        步骤3: 生成优化建议
        
        通过MCP向Optimizer Agent发送优化请求
        """
        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender="workflow",
            receiver="optimizer",
            message_type="request",
            action="generate_suggestions",
            payload={
                "jd_id": jd_id
            },
            context_id=context_id,
            timestamp=time.time()
        )
        
        try:
            await self.mcp_server.send_message(message)
            response = await self.mcp_server.wait_for_response(
                message.message_id,
                timeout=timeout
            )
            
            return {
                "success": True,
                "suggestions": response.payload
            }
            
        except TimeoutError:
            logger.error(f"优化建议生成超时 [context_id={context_id}, jd_id={jd_id}]")
            return {
                "success": False,
                "error": "优化建议生成超时"
            }
        except Exception as e:
            logger.error(
                f"优化建议生成异常 [context_id={context_id}, "
                f"jd_id={jd_id}, error={str(e)}]"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        获取工作流状态
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            工作流状态信息，如果不存在返回None
        """
        context = await self.mcp_server.get_context(workflow_id)
        
        if not context:
            return None
        
        return {
            "workflow_id": workflow_id,
            "status": context.shared_data.get("status", "unknown"),
            "step": context.shared_data.get("step", "unknown"),
            "jd_id": context.shared_data.get("jd_id"),
            "start_time": context.shared_data.get("start_time"),
            "error": context.shared_data.get("error")
        }
