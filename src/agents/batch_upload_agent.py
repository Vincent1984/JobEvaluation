"""批量上传Agent - 处理批量文件上传和解析（优化版）"""

import logging
from typing import Dict, Any, List, Optional
import uuid
import asyncio

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.mcp.context import MCPContext, create_context
from src.utils.file_parser import FileParser, FileParserService
from src.core.performance import monitor_performance, batch_processor

logger = logging.getLogger(__name__)


class FileParserService:
    """文件解析服务 - 支持多种格式"""
    
    SUPPORTED_FORMATS = {
        '.txt': 'parse_txt',
        '.pdf': 'parse_pdf',
        '.docx': 'parse_docx',
        '.doc': 'parse_doc'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_BATCH_SIZE = 20  # 最多20个文件
    MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 总计100MB
    
    def __init__(self):
        self.parser = FileParser()
    
    def validate_file(self, file_size: int, filename: str) -> tuple[bool, str]:
        """验证单个文件
        
        Args:
            file_size: 文件大小（字节）
            filename: 文件名
            
        Returns:
            (是否有效, 错误信息)
        """
        from pathlib import Path
        
        # 检查文件大小
        if file_size > self.MAX_FILE_SIZE:
            return False, f"文件大小超过限制({self.MAX_FILE_SIZE / 1024 / 1024}MB)"
        
        # 检查文件格式
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            return False, f"不支持的文件格式: {file_ext}。支持的格式: {', '.join(self.SUPPORTED_FORMATS.keys())}"
        
        return True, "验证通过"
    
    def validate_batch(self, files: List[tuple]) -> tuple[bool, str]:
        """验证批量上传
        
        Args:
            files: 文件列表 [(size, filename), ...]
            
        Returns:
            (是否有效, 错误信息)
        """
        # 检查文件数量
        if len(files) > self.MAX_BATCH_SIZE:
            return False, f"文件数量超过限制({self.MAX_BATCH_SIZE}个)"
        
        # 检查总大小
        total_size = sum(size for size, _ in files)
        if total_size > self.MAX_TOTAL_SIZE:
            return False, f"总文件大小超过限制({self.MAX_TOTAL_SIZE / 1024 / 1024}MB)"
        
        return True, "验证通过"
    
    def parse_file(self, file_content: bytes, filename: str) -> str:
        """解析文件
        
        Args:
            file_content: 文件内容
            filename: 文件名
            
        Returns:
            解析后的文本
        """
        return self.parser.parse_file(file_content, filename)


class BatchUploadAgent(MCPAgent):
    """批量上传处理Agent
    
    职责：
    - 验证文件格式、大小、数量
    - 批量文件处理循环
    - 进度通知机制（via MCP）
    - 与Parser Agent和Evaluator Agent的协调
    - 批量处理上下文管理
    - 结果汇总和错误处理
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        agent_id: str = "batch_uploader",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """初始化批量上传Agent
        
        Args:
            mcp_server: MCP服务器实例
            agent_id: Agent ID
            metadata: 元数据
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="batch_uploader",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        self.file_parser = FileParserService()
        
        # 注册消息处理器
        self.register_handler("batch_upload", self.handle_batch_upload)
        self.register_handler("parse_file", self.handle_parse_file)
        
        logger.info(f"BatchUploadAgent initialized: {agent_id}")
    
    async def handle_batch_upload(self, message: MCPMessage) -> None:
        """处理批量上传请求
        
        Args:
            message: MCP消息，payload包含:
                - files: 文件列表 [{"filename": str, "content": bytes, "size": int}, ...]
        """
        files = message.payload.get("files", [])
        context_id = message.context_id or str(uuid.uuid4())
        
        logger.info(f"收到批量上传请求: {len(files)}个文件, context_id={context_id}")
        
        # 验证批量上传
        is_valid, error_msg = self.file_parser.validate_batch(
            [(f["size"], f["filename"]) for f in files]
        )
        
        if not is_valid:
            logger.warning(f"批量上传验证失败: {error_msg}")
            await self.send_response(message, {
                "success": False,
                "error": error_msg
            })
            return
        
        # 创建批量处理上下文
        context = create_context(
            task_id=message.message_id,
            workflow_type="batch_upload",
            shared_data={
                "total_files": len(files),
                "processed_files": 0,
                "successful_files": 0,
                "failed_files": []
            },
            metadata={"workflow": "batch_upload"},
            expiration_seconds=3600  # 1小时过期
        )
        context.context_id = context_id
        await self.update_context(context)
        
        # 批量处理文件（优化版：并行解析 + 批量处理）
        results = []
        
        # 步骤1：并行解析所有文件
        logger.info(f"开始并行解析 {len(files)} 个文件...")
        parse_tasks = [
            (file_info["content"], file_info["filename"])
            for file_info in files
        ]
        
        parsed_files = await FileParserService.parse_files_parallel(
            parse_tasks,
            max_concurrent=4
        )
        
        # 步骤2：批量处理解析成功的文件
        async def process_single_file(file_info: Dict, parsed_result: Dict, idx: int):
            """处理单个文件"""
            try:
                # 发送进度通知
                await self.send_notification(
                    action="upload_progress",
                    payload={
                        "context_id": context_id,
                        "current": idx + 1,
                        "total": len(files),
                        "filename": file_info["filename"],
                        "status": "processing"
                    },
                    context_id=context_id
                )
                
                if not parsed_result["success"]:
                    raise Exception(parsed_result.get("error", "文件解析失败"))
                
                jd_text = parsed_result["text"]
                
                # 请求Parser Agent解析JD
                parse_response = await self.send_request(
                    receiver="parser",
                    action="parse_jd",
                    payload={"jd_text": jd_text},
                    context_id=context_id,
                    timeout=60.0
                )
                
                if not parse_response.payload.get("success", True):
                    raise Exception(parse_response.payload.get("error", "解析失败"))
                
                jd_id = parse_response.payload["jd_id"]
                parsed_data = parse_response.payload["parsed_data"]
                
                # 请求Evaluator Agent评估质量
                eval_response = await self.send_request(
                    receiver="evaluator",
                    action="evaluate_quality",
                    payload={"jd_id": jd_id},
                    context_id=context_id,
                    timeout=60.0
                )
                
                if not eval_response.payload.get("success", True):
                    logger.warning(f"评估失败: {eval_response.payload.get('error', '未知错误')}")
                    quality_score = 0
                else:
                    quality_score = eval_response.payload.get("quality_score", {}).get("overall_score", 0)
                
                return {
                    "filename": file_info["filename"],
                    "status": "success",
                    "jd_id": jd_id,
                    "jd_title": parsed_data.get("job_title", "未知职位"),
                    "quality_score": quality_score
                }
                
            except Exception as e:
                logger.error(f"文件处理失败: {file_info['filename']}, 错误: {e}")
                return {
                    "filename": file_info["filename"],
                    "status": "failed",
                    "error": str(e)
                }
        
        # 使用批量处理器并发处理
        logger.info(f"开始批量处理 {len(files)} 个文件...")
        
        process_tasks = []
        for idx, (file_info, parsed_result) in enumerate(zip(files, parsed_files)):
            process_tasks.append(
                process_single_file(file_info, parsed_result, idx)
            )
        
        # 并发执行（限制并发数为5）
        semaphore = asyncio.Semaphore(5)
        
        async def process_with_semaphore(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(
            *[process_with_semaphore(task) for task in process_tasks],
            return_exceptions=True
        )
        
        # 统计结果
        for result in results:
            if isinstance(result, Exception):
                context.shared_data["failed_files"].append({
                    "filename": "unknown",
                    "error": str(result)
                })
            elif result["status"] == "success":
                context.shared_data["successful_files"] += 1
            else:
                context.shared_data["failed_files"].append({
                    "filename": result["filename"],
                    "error": result.get("error", "未知错误")
                })
            
            context.shared_data["processed_files"] += 1
        
        await self.update_context(context)
        
        # 发送完成通知
        await self.send_notification(
            action="upload_complete",
            payload={
                "context_id": context_id,
                "total": len(files),
                "successful": context.shared_data["successful_files"],
                "failed": len(context.shared_data["failed_files"])
            },
            context_id=context_id
        )
        
        # 返回批量处理结果
        await self.send_response(message, {
            "success": True,
            "total": len(files),
            "successful": context.shared_data["successful_files"],
            "failed": len(context.shared_data["failed_files"]),
            "results": results,
            "failed_files": context.shared_data["failed_files"],
            "context_id": context_id
        })
        
        logger.info(
            f"批量上传完成: 总计{len(files)}个文件, "
            f"成功{context.shared_data['successful_files']}个, "
            f"失败{len(context.shared_data['failed_files'])}个"
        )
    
    async def handle_parse_file(self, message: MCPMessage) -> None:
        """处理单个文件解析请求
        
        Args:
            message: MCP消息，payload包含:
                - file_content: 文件内容（bytes）
                - filename: 文件名
        """
        file_content = message.payload.get("file_content")
        filename = message.payload.get("filename")
        
        logger.info(f"收到文件解析请求: {filename}")
        
        try:
            # 验证文件
            is_valid, error_msg = self.file_parser.validate_file(
                len(file_content), filename
            )
            
            if not is_valid:
                logger.warning(f"文件验证失败: {error_msg}")
                await self.send_response(message, {
                    "success": False,
                    "error": error_msg
                })
                return
            
            # 解析文件
            jd_text = self.file_parser.parse_file(file_content, filename)
            
            logger.info(f"文件解析成功: {filename}, 文本长度={len(jd_text)}")
            
            await self.send_response(message, {
                "success": True,
                "jd_text": jd_text,
                "filename": filename
            })
            
        except Exception as e:
            logger.error(f"文件解析失败: {filename}, 错误: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e),
                "filename": filename
            })


# 便捷函数
async def create_batch_upload_agent(
    mcp_server: MCPServer,
    agent_id: str = "batch_uploader",
    auto_start: bool = True
) -> BatchUploadAgent:
    """创建并启动批量上传Agent
    
    Args:
        mcp_server: MCP服务器实例
        agent_id: Agent ID
        auto_start: 是否自动启动
        
    Returns:
        BatchUploadAgent实例
    """
    agent = BatchUploadAgent(mcp_server=mcp_server, agent_id=agent_id)
    
    if auto_start:
        await agent.start()
    
    return agent
