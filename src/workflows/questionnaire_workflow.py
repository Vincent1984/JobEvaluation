"""
问卷生成与匹配评估工作流

实现问卷生成→回答收集→匹配计算的流程，支持批量候选人评估
"""

import uuid
import time
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

from src.mcp.server import MCPServer
from src.mcp.context import MCPContext
from src.mcp.message import MCPMessage

logger = logging.getLogger(__name__)


class QuestionnaireWorkflow:
    """问卷生成与匹配评估工作流"""
    
    def __init__(self, mcp_server: MCPServer):
        """
        初始化问卷工作流
        
        Args:
            mcp_server: MCP服务器实例
        """
        self.mcp_server = mcp_server
        self.workflow_name = "questionnaire"
    
    async def generate_questionnaire(
        self,
        jd_id: str,
        evaluation_model: str = "standard",
        custom_config: Optional[Dict] = None,
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        生成评估问卷
        
        Args:
            jd_id: 岗位JD ID
            evaluation_model: 评估模型类型 (standard/mercer_ipe/factor_comparison)
            custom_config: 自定义问卷配置
            timeout: 超时时间（秒）
        
        Returns:
            包含问卷信息的字典:
            {
                "questionnaire_id": "问卷ID",
                "questionnaire": {...},  # 问卷详情
                "workflow_id": "工作流ID",
                "status": "completed/failed",
                "execution_time": 12.34
            }
        """
        start_time = time.time()
        workflow_id = str(uuid.uuid4())
        
        logger.info(
            f"开始问卷生成工作流 [workflow_id={workflow_id}, jd_id={jd_id}]"
        )
        
        try:
            # 1. 创建工作流上下文
            context = await self._create_workflow_context(
                workflow_id=workflow_id,
                jd_id=jd_id,
                evaluation_model=evaluation_model,
                custom_config=custom_config,
                workflow_type="questionnaire_generation"
            )
            
            # 2. 生成问卷
            logger.info(f"生成问卷 [workflow_id={workflow_id}, jd_id={jd_id}]")
            result = await self._generate_questionnaire_internal(
                context_id=context.context_id,
                jd_id=jd_id,
                evaluation_model=evaluation_model,
                custom_config=custom_config,
                timeout=timeout
            )
            
            if not result.get("success"):
                raise Exception(f"问卷生成失败: {result.get('error')}")
            
            execution_time = time.time() - start_time
            
            response = {
                "questionnaire_id": result["questionnaire_id"],
                "questionnaire": result["questionnaire"],
                "workflow_id": workflow_id,
                "status": "completed",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # 更新上下文
            context.shared_data["result"] = response
            context.shared_data["status"] = "completed"
            await self.mcp_server.update_context(context)
            
            logger.info(
                f"问卷生成完成 [workflow_id={workflow_id}, "
                f"questionnaire_id={result['questionnaire_id']}, "
                f"execution_time={execution_time:.2f}s]"
            )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                f"问卷生成失败 [workflow_id={workflow_id}, "
                f"error={error_msg}, execution_time={execution_time:.2f}s]"
            )
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": error_msg,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def evaluate_match(
        self,
        jd_id: str,
        questionnaire_id: str,
        responses: Dict[str, Any],
        respondent_name: Optional[str] = None,
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        评估单个候选人的匹配度
        
        Args:
            jd_id: 岗位JD ID
            questionnaire_id: 问卷ID
            responses: 问卷回答 {question_id: answer}
            respondent_name: 被评估人姓名
            timeout: 超时时间（秒）
        
        Returns:
            包含匹配结果的字典:
            {
                "match_id": "匹配结果ID",
                "match_result": {...},  # 匹配详情
                "workflow_id": "工作流ID",
                "status": "completed/failed",
                "execution_time": 12.34
            }
        """
        start_time = time.time()
        workflow_id = str(uuid.uuid4())
        
        logger.info(
            f"开始匹配评估工作流 [workflow_id={workflow_id}, "
            f"jd_id={jd_id}, questionnaire_id={questionnaire_id}]"
        )
        
        try:
            # 1. 创建工作流上下文
            context = await self._create_workflow_context(
                workflow_id=workflow_id,
                jd_id=jd_id,
                questionnaire_id=questionnaire_id,
                responses=responses,
                respondent_name=respondent_name,
                workflow_type="match_evaluation"
            )
            
            # 2. 评估匹配度
            logger.info(
                f"评估匹配度 [workflow_id={workflow_id}, "
                f"jd_id={jd_id}, questionnaire_id={questionnaire_id}]"
            )
            result = await self._evaluate_match_internal(
                context_id=context.context_id,
                jd_id=jd_id,
                questionnaire_id=questionnaire_id,
                responses=responses,
                respondent_name=respondent_name,
                timeout=timeout
            )
            
            if not result.get("success"):
                raise Exception(f"匹配评估失败: {result.get('error')}")
            
            execution_time = time.time() - start_time
            
            response = {
                "match_id": result["match_id"],
                "match_result": result["match_result"],
                "workflow_id": workflow_id,
                "status": "completed",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # 更新上下文
            context.shared_data["result"] = response
            context.shared_data["status"] = "completed"
            await self.mcp_server.update_context(context)
            
            logger.info(
                f"匹配评估完成 [workflow_id={workflow_id}, "
                f"match_id={result['match_id']}, "
                f"execution_time={execution_time:.2f}s]"
            )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                f"匹配评估失败 [workflow_id={workflow_id}, "
                f"error={error_msg}, execution_time={execution_time:.2f}s]"
            )
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": error_msg,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def batch_evaluate_candidates(
        self,
        jd_id: str,
        questionnaire_id: str,
        candidate_responses: List[Dict[str, Any]],
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """
        批量评估多个候选人
        
        Args:
            jd_id: 岗位JD ID
            questionnaire_id: 问卷ID
            candidate_responses: 候选人回答列表
                [
                    {
                        "respondent_name": "张三",
                        "responses": {question_id: answer}
                    },
                    ...
                ]
            timeout: 总超时时间（秒）
        
        Returns:
            包含批量评估结果的字典:
            {
                "batch_id": "批量任务ID",
                "total": 10,
                "successful": 9,
                "failed": 1,
                "results": [...],  # 成功的匹配结果
                "failed_candidates": [...],  # 失败的候选人
                "workflow_id": "工作流ID",
                "status": "completed",
                "execution_time": 123.45
            }
        """
        start_time = time.time()
        workflow_id = str(uuid.uuid4())
        batch_id = workflow_id
        
        logger.info(
            f"开始批量候选人评估 [workflow_id={workflow_id}, "
            f"jd_id={jd_id}, questionnaire_id={questionnaire_id}, "
            f"total_candidates={len(candidate_responses)}]"
        )
        
        try:
            # 1. 创建批量工作流上下文
            context = await self._create_batch_workflow_context(
                workflow_id=workflow_id,
                jd_id=jd_id,
                questionnaire_id=questionnaire_id,
                total_candidates=len(candidate_responses)
            )
            
            # 2. 批量处理候选人
            results = []
            failed_candidates = []
            per_candidate_timeout = timeout / len(candidate_responses) if candidate_responses else timeout
            
            for idx, candidate_data in enumerate(candidate_responses, 1):
                respondent_name = candidate_data.get("respondent_name", f"候选人{idx}")
                responses = candidate_data.get("responses", {})
                
                logger.info(
                    f"评估候选人 {idx}/{len(candidate_responses)} "
                    f"[workflow_id={workflow_id}, name={respondent_name}]"
                )
                
                try:
                    # 评估单个候选人
                    match_result = await self._evaluate_match_internal(
                        context_id=context.context_id,
                        jd_id=jd_id,
                        questionnaire_id=questionnaire_id,
                        responses=responses,
                        respondent_name=respondent_name,
                        timeout=per_candidate_timeout
                    )
                    
                    if match_result.get("success"):
                        results.append({
                            "respondent_name": respondent_name,
                            "match_id": match_result["match_id"],
                            "match_result": match_result["match_result"],
                            "status": "success"
                        })
                        
                        # 更新上下文
                        context.shared_data["successful_candidates"] += 1
                    else:
                        failed_candidates.append({
                            "respondent_name": respondent_name,
                            "error": match_result.get("error", "未知错误"),
                            "status": "failed"
                        })
                        
                        context.shared_data["failed_candidates"] += 1
                
                except Exception as e:
                    error_msg = str(e)
                    logger.error(
                        f"候选人评估异常 [workflow_id={workflow_id}, "
                        f"name={respondent_name}, error={error_msg}]"
                    )
                    
                    failed_candidates.append({
                        "respondent_name": respondent_name,
                        "error": error_msg,
                        "status": "failed"
                    })
                    
                    context.shared_data["failed_candidates"] += 1
                
                # 更新进度
                context.shared_data["processed_candidates"] = idx
                await self.mcp_server.update_context(context)
            
            execution_time = time.time() - start_time
            
            # 3. 汇总结果
            response = {
                "batch_id": batch_id,
                "total": len(candidate_responses),
                "successful": len(results),
                "failed": len(failed_candidates),
                "results": results,
                "failed_candidates": failed_candidates,
                "workflow_id": workflow_id,
                "status": "completed",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # 更新上下文为完成状态
            context.shared_data["result"] = response
            context.shared_data["status"] = "completed"
            await self.mcp_server.update_context(context)
            
            logger.info(
                f"批量候选人评估完成 [workflow_id={workflow_id}, "
                f"total={len(candidate_responses)}, successful={len(results)}, "
                f"failed={len(failed_candidates)}, execution_time={execution_time:.2f}s]"
            )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                f"批量候选人评估失败 [workflow_id={workflow_id}, "
                f"error={error_msg}, execution_time={execution_time:.2f}s]"
            )
            
            return {
                "batch_id": batch_id,
                "workflow_id": workflow_id,
                "status": "failed",
                "error": error_msg,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _create_workflow_context(
        self,
        workflow_id: str,
        workflow_type: str,
        **kwargs
    ) -> MCPContext:
        """创建工作流上下文"""
        context = MCPContext(
            context_id=workflow_id,
            task_id=workflow_id,
            shared_data={
                "workflow": "questionnaire",
                "workflow_type": workflow_type,
                "status": "running",
                "start_time": time.time(),
                **kwargs
            },
            metadata={
                "workflow_type": workflow_type,
                "created_at": datetime.now().isoformat()
            }
        )
        
        await self.mcp_server.update_context(context)
        logger.debug(f"创建工作流上下文 [context_id={context.context_id}]")
        
        return context
    
    async def _create_batch_workflow_context(
        self,
        workflow_id: str,
        jd_id: str,
        questionnaire_id: str,
        total_candidates: int
    ) -> MCPContext:
        """创建批量评估工作流上下文"""
        context = MCPContext(
            context_id=workflow_id,
            task_id=workflow_id,
            shared_data={
                "workflow": "questionnaire",
                "workflow_type": "batch_evaluation",
                "jd_id": jd_id,
                "questionnaire_id": questionnaire_id,
                "total_candidates": total_candidates,
                "processed_candidates": 0,
                "successful_candidates": 0,
                "failed_candidates": 0,
                "status": "running",
                "start_time": time.time()
            },
            metadata={
                "workflow_type": "batch_evaluation",
                "created_at": datetime.now().isoformat()
            }
        )
        
        await self.mcp_server.update_context(context)
        logger.debug(
            f"创建批量评估上下文 [context_id={context.context_id}, "
            f"total_candidates={total_candidates}]"
        )
        
        return context
    
    async def _generate_questionnaire_internal(
        self,
        context_id: str,
        jd_id: str,
        evaluation_model: str,
        custom_config: Optional[Dict],
        timeout: float
    ) -> Dict[str, Any]:
        """
        内部方法: 生成问卷
        
        通过MCP向Questionnaire Agent发送生成请求
        """
        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender="workflow",
            receiver="questionnaire",
            message_type="request",
            action="generate_questionnaire",
            payload={
                "jd_id": jd_id,
                "evaluation_model": evaluation_model,
                "custom_config": custom_config or {}
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
                "questionnaire_id": response.payload.get("questionnaire_id"),
                "questionnaire": response.payload.get("questionnaire")
            }
            
        except TimeoutError:
            logger.error(f"问卷生成超时 [context_id={context_id}, jd_id={jd_id}]")
            return {
                "success": False,
                "error": "问卷生成超时"
            }
        except Exception as e:
            logger.error(
                f"问卷生成异常 [context_id={context_id}, "
                f"jd_id={jd_id}, error={str(e)}]"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _evaluate_match_internal(
        self,
        context_id: str,
        jd_id: str,
        questionnaire_id: str,
        responses: Dict[str, Any],
        respondent_name: Optional[str],
        timeout: float
    ) -> Dict[str, Any]:
        """
        内部方法: 评估匹配度
        
        通过MCP向Matcher Agent发送评估请求
        """
        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender="workflow",
            receiver="matcher",
            message_type="request",
            action="evaluate_match",
            payload={
                "jd_id": jd_id,
                "questionnaire_id": questionnaire_id,
                "responses": responses,
                "respondent_name": respondent_name
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
                "match_id": response.payload.get("match_id"),
                "match_result": response.payload.get("match_result")
            }
            
        except TimeoutError:
            logger.error(
                f"匹配评估超时 [context_id={context_id}, "
                f"jd_id={jd_id}, questionnaire_id={questionnaire_id}]"
            )
            return {
                "success": False,
                "error": "匹配评估超时"
            }
        except Exception as e:
            logger.error(
                f"匹配评估异常 [context_id={context_id}, "
                f"jd_id={jd_id}, questionnaire_id={questionnaire_id}, error={str(e)}]"
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
        
        workflow_type = context.shared_data.get("workflow_type", "unknown")
        
        status_info = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "status": context.shared_data.get("status", "unknown"),
            "start_time": context.shared_data.get("start_time"),
            "error": context.shared_data.get("error")
        }
        
        # 批量评估的额外信息
        if workflow_type == "batch_evaluation":
            status_info.update({
                "total_candidates": context.shared_data.get("total_candidates", 0),
                "processed_candidates": context.shared_data.get("processed_candidates", 0),
                "successful_candidates": context.shared_data.get("successful_candidates", 0),
                "failed_candidates": context.shared_data.get("failed_candidates", 0)
            })
        
        return status_info
    
    async def get_batch_results(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        获取批量评估结果
        
        Args:
            batch_id: 批量任务ID
        
        Returns:
            批量评估结果，如果不存在返回None
        """
        context = await self.mcp_server.get_context(batch_id)
        
        if not context:
            return None
        
        return context.shared_data.get("result")
