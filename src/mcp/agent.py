"""MCP Agent基类 - 所有Agent的基础实现"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import uuid

from .message import MCPMessage, MessageType, create_request_message, create_notification_message
from .context import MCPContext
from .server import MCPServer

logger = logging.getLogger(__name__)


class MCPAgent:
    """
    MCP Agent基类
    
    所有Agent的基础类，提供：
    - Agent注册和消息订阅
    - 消息处理器注册机制
    - 请求-响应模式
    - 上下文管理
    - 工具注册
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        mcp_server: MCPServer,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化Agent
        
        Args:
            agent_id: Agent唯一标识符
            agent_type: Agent类型（如：parser, evaluator, optimizer等）
            mcp_server: MCP服务器实例
            metadata: Agent元数据（可选）
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.mcp_server = mcp_server
        self.metadata = metadata or {}
        
        # 消息处理器注册表
        self.message_handlers: Dict[str, Callable[[MCPMessage], Any]] = {}
        
        # 工具注册表
        self.tools: List[Callable] = []
        
        # 运行状态
        self.is_running = False
        self._listener_task: Optional[asyncio.Task] = None
        
        # 响应等待队列（用于请求-响应模式）
        self._pending_responses: Dict[str, asyncio.Future] = {}
        
        # 订阅的通道
        self._subscribed_channels: List[str] = []
        
        logger.info(
            f"Agent initialized: {agent_id} (type: {agent_type})"
        )
    
    # ==================== Agent生命周期管理 ====================
    
    async def start(self) -> None:
        """启动Agent"""
        if self.is_running:
            logger.warning(f"Agent {self.agent_id} is already running")
            return
        
        # 注册到MCP服务器
        await self.mcp_server.register_agent(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            metadata=self.metadata
        )
        
        # 订阅消息
        await self._subscribe_to_messages()
        
        # 启动消息监听器
        self._listener_task = asyncio.create_task(self._listen_to_messages())
        
        self.is_running = True
        
        logger.info(f"Agent started: {self.agent_id}")
    
    async def stop(self) -> None:
        """停止Agent"""
        if not self.is_running:
            logger.warning(f"Agent {self.agent_id} is not running")
            return
        
        self.is_running = False
        
        # 停止消息监听器
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
        
        # 取消订阅
        await self._unsubscribe_from_messages()
        
        # 从MCP服务器注销
        await self.mcp_server.unregister_agent(self.agent_id)
        
        # 取消所有待处理的响应
        for future in self._pending_responses.values():
            if not future.done():
                future.cancel()
        self._pending_responses.clear()
        
        logger.info(f"Agent stopped: {self.agent_id}")
    
    # ==================== 消息订阅 ====================
    
    async def _subscribe_to_messages(self) -> None:
        """订阅消息通道（内部方法）"""
        # 订阅Agent专属通道
        agent_channel = f"mcp:agent:{self.agent_id}"
        await self.mcp_server.subscribe_to_channel(agent_channel)
        self._subscribed_channels.append(agent_channel)
        
        # 订阅广播通道
        broadcast_channel = "mcp:broadcast"
        await self.mcp_server.subscribe_to_channel(broadcast_channel)
        self._subscribed_channels.append(broadcast_channel)
        
        logger.debug(f"Agent {self.agent_id} subscribed to channels")
    
    async def _unsubscribe_from_messages(self) -> None:
        """取消订阅消息通道（内部方法）"""
        for channel in self._subscribed_channels:
            await self.mcp_server.unsubscribe_from_channel(channel)
        
        self._subscribed_channels.clear()
        
        logger.debug(f"Agent {self.agent_id} unsubscribed from channels")
    
    async def _listen_to_messages(self) -> None:
        """监听消息（内部方法）"""
        if not self.mcp_server.pubsub:
            logger.warning(f"Agent {self.agent_id}: PubSub not initialized, skipping message listener")
            return
        
        logger.info(f"Agent {self.agent_id} started listening to messages")
        
        try:
            async for message in self.mcp_server.pubsub.listen():
                if not self.is_running:
                    break
                
                if message["type"] == "message":
                    await self._handle_message(message["data"])
        
        except asyncio.CancelledError:
            logger.info(f"Agent {self.agent_id} message listener cancelled")
            raise
        
        except Exception as e:
            logger.error(f"Agent {self.agent_id} error in message listener: {e}")
    
    async def _handle_message(self, message_data: str) -> None:
        """
        处理接收到的消息（内部方法）
        
        Args:
            message_data: 消息JSON字符串
        """
        try:
            message = MCPMessage.from_json(message_data)
            
            # 忽略自己发送的消息
            if message.sender == self.agent_id:
                return
            
            # 如果是响应消息，处理待处理的响应
            if message.is_response() and message.correlation_id:
                await self._handle_response(message)
                return
            
            # 调用注册的消息处理器
            handler = self.message_handlers.get(message.action)
            if handler:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(
                        f"Agent {self.agent_id} error handling message "
                        f"{message.message_id} (action: {message.action}): {e}"
                    )
            else:
                logger.debug(
                    f"Agent {self.agent_id} no handler for action: {message.action}"
                )
        
        except Exception as e:
            logger.error(f"Agent {self.agent_id} error processing message: {e}")
    
    async def _handle_response(self, message: MCPMessage) -> None:
        """
        处理响应消息（内部方法）
        
        Args:
            message: 响应消息
        """
        correlation_id = message.correlation_id
        
        if correlation_id in self._pending_responses:
            future = self._pending_responses[correlation_id]
            if not future.done():
                future.set_result(message)
            del self._pending_responses[correlation_id]
            
            logger.debug(
                f"Agent {self.agent_id} received response for request {correlation_id}"
            )
    
    # ==================== 消息处理器注册 ====================
    
    def register_handler(
        self,
        action: str,
        handler: Callable[[MCPMessage], Any]
    ) -> None:
        """
        注册消息处理器
        
        Args:
            action: 操作类型
            handler: 处理函数（接收MCPMessage参数）
        """
        self.message_handlers[action] = handler
        logger.debug(f"Agent {self.agent_id} registered handler for action: {action}")
    
    def unregister_handler(self, action: str) -> None:
        """
        注销消息处理器
        
        Args:
            action: 操作类型
        """
        if action in self.message_handlers:
            del self.message_handlers[action]
            logger.debug(
                f"Agent {self.agent_id} unregistered handler for action: {action}"
            )
    
    def get_registered_actions(self) -> List[str]:
        """
        获取已注册的操作类型列表
        
        Returns:
            操作类型列表
        """
        return list(self.message_handlers.keys())
    
    # ==================== 请求-响应模式 ====================
    
    async def send_request(
        self,
        receiver: str,
        action: str,
        payload: Dict[str, Any],
        context_id: Optional[str] = None,
        timeout: float = 30.0
    ) -> MCPMessage:
        """
        发送请求并等待响应
        
        Args:
            receiver: 接收者Agent ID
            action: 操作类型
            payload: 请求数据
            context_id: 上下文ID（可选）
            timeout: 超时时间（秒）
            
        Returns:
            响应消息
            
        Raises:
            asyncio.TimeoutError: 如果超时未收到响应
        """
        # 创建请求消息
        message = create_request_message(
            sender=self.agent_id,
            receiver=receiver,
            action=action,
            payload=payload,
            context_id=context_id
        )
        
        # 创建响应Future
        response_future = asyncio.Future()
        self._pending_responses[message.message_id] = response_future
        
        # 发送消息
        await self.mcp_server.send_message(message)
        
        logger.debug(
            f"Agent {self.agent_id} sent request {message.message_id} "
            f"to {receiver} (action: {action})"
        )
        
        try:
            # 等待响应
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        
        except asyncio.TimeoutError:
            # 清理待处理的响应
            if message.message_id in self._pending_responses:
                del self._pending_responses[message.message_id]
            
            logger.error(
                f"Agent {self.agent_id} request {message.message_id} "
                f"to {receiver} timed out after {timeout}s"
            )
            raise
    
    async def send_response(
        self,
        request_message: MCPMessage,
        payload: Dict[str, Any]
    ) -> None:
        """
        发送响应消息
        
        Args:
            request_message: 原始请求消息
            payload: 响应数据
        """
        # 创建响应消息
        response = request_message.create_response(
            payload=payload,
            sender=self.agent_id
        )
        
        # 发送响应
        await self.mcp_server.send_message(response)
        
        logger.debug(
            f"Agent {self.agent_id} sent response to {request_message.sender} "
            f"for request {request_message.message_id}"
        )
    
    # ==================== 通知消息 ====================
    
    async def send_notification(
        self,
        action: str,
        payload: Dict[str, Any],
        context_id: Optional[str] = None,
        receiver: Optional[str] = None
    ) -> None:
        """
        发送通知消息（不需要响应）
        
        Args:
            action: 操作类型
            payload: 通知数据
            context_id: 上下文ID（可选）
            receiver: 接收者Agent ID（可选，None表示广播）
        """
        # 创建通知消息
        message = create_notification_message(
            sender=self.agent_id,
            action=action,
            payload=payload,
            context_id=context_id,
            receiver=receiver
        )
        
        # 发送消息
        await self.mcp_server.send_message(message)
        
        logger.debug(
            f"Agent {self.agent_id} sent notification "
            f"to {receiver or 'broadcast'} (action: {action})"
        )
    
    # ==================== 上下文管理 ====================
    
    async def get_context(self, context_id: str) -> Optional[MCPContext]:
        """
        获取上下文
        
        Args:
            context_id: 上下文ID
            
        Returns:
            上下文对象，如果不存在则返回None
        """
        return await self.mcp_server.get_context(context_id)
    
    async def update_context(self, context: MCPContext) -> None:
        """
        更新上下文
        
        Args:
            context: 上下文对象
        """
        # 添加自己为参与者
        context.add_participant(self.agent_id)
        
        # 更新到服务器
        await self.mcp_server.update_context(context)
    
    async def create_context(
        self,
        task_id: str,
        workflow_type: str = "general",
        shared_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expiration_seconds: Optional[int] = None
    ) -> MCPContext:
        """
        创建新上下文
        
        Args:
            task_id: 任务ID
            workflow_type: 工作流类型
            shared_data: 初始共享数据（可选）
            metadata: 元数据（可选）
            expiration_seconds: 过期时间（秒，可选）
            
        Returns:
            上下文对象
        """
        from .context import create_context
        
        context = create_context(
            task_id=task_id,
            workflow_type=workflow_type,
            shared_data=shared_data,
            metadata=metadata,
            expiration_seconds=expiration_seconds
        )
        
        # 添加自己为参与者
        context.add_participant(self.agent_id)
        
        # 保存到服务器
        await self.mcp_server.save_context(context)
        
        logger.debug(f"Agent {self.agent_id} created context: {context.context_id}")
        
        return context
    
    # ==================== 工具管理 ====================
    
    def register_tool(self, tool: Callable) -> None:
        """
        注册工具
        
        Args:
            tool: 工具函数
        """
        self.tools.append(tool)
        logger.debug(
            f"Agent {self.agent_id} registered tool: {tool.__name__}"
        )
    
    def unregister_tool(self, tool: Callable) -> None:
        """
        注销工具
        
        Args:
            tool: 工具函数
        """
        if tool in self.tools:
            self.tools.remove(tool)
            logger.debug(
                f"Agent {self.agent_id} unregistered tool: {tool.__name__}"
            )
    
    def get_tools(self) -> List[Callable]:
        """
        获取已注册的工具列表
        
        Returns:
            工具函数列表
        """
        return self.tools.copy()
    
    # ==================== 工具方法 ====================
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取Agent信息
        
        Returns:
            Agent信息字典
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "metadata": self.metadata,
            "is_running": self.is_running,
            "registered_actions": self.get_registered_actions(),
            "registered_tools": [tool.__name__ for tool in self.tools],
            "pending_responses": len(self._pending_responses)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        is_registered = await self.mcp_server.is_agent_registered(self.agent_id)
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "is_running": self.is_running,
            "is_registered": is_registered,
            "subscribed_channels": len(self._subscribed_channels),
            "pending_responses": len(self._pending_responses),
            "status": "healthy" if (self.is_running and is_registered) else "unhealthy"
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"MCPAgent(agent_id='{self.agent_id}', "
            f"agent_type='{self.agent_type}', "
            f"is_running={self.is_running})"
        )


# ==================== 便捷函数 ====================

async def create_agent(
    agent_id: str,
    agent_type: str,
    mcp_server: MCPServer,
    metadata: Optional[Dict[str, Any]] = None,
    auto_start: bool = True
) -> MCPAgent:
    """
    创建并启动Agent的便捷函数
    
    Args:
        agent_id: Agent唯一标识符
        agent_type: Agent类型
        mcp_server: MCP服务器实例
        metadata: Agent元数据（可选）
        auto_start: 是否自动启动Agent
        
    Returns:
        Agent实例
    """
    agent = MCPAgent(
        agent_id=agent_id,
        agent_type=agent_type,
        mcp_server=mcp_server,
        metadata=metadata
    )
    
    if auto_start:
        await agent.start()
    
    return agent
