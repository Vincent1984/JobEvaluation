"""MCP Server - Agent通讯中枢（基于Redis）"""

import asyncio
import json
import logging
from typing import Dict, Optional, Callable, Any, Set
from datetime import datetime

import redis.asyncio as redis
from redis.asyncio.client import PubSub

from .message import MCPMessage, MessageType
from .context import MCPContext

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP服务器 - Agent通讯中枢
    
    基于Redis实现消息发布订阅和上下文存储，
    提供Agent注册、消息路由和上下文管理功能
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None
    ):
        """
        初始化MCP服务器
        
        Args:
            redis_host: Redis主机地址
            redis_port: Redis端口
            redis_db: Redis数据库编号
            redis_password: Redis密码（可选）
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password
        
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[PubSub] = None
        
        # Agent注册表
        self.agents: Dict[str, Dict[str, Any]] = {}
        
        # 消息处理器
        self.message_handlers: Dict[str, Callable] = {}
        
        # 运行状态
        self.is_running = False
        self._listener_task: Optional[asyncio.Task] = None
        
        logger.info(
            f"MCP Server initialized with Redis at {redis_host}:{redis_port}/{redis_db}"
        )
    
    async def connect(self) -> None:
        """连接到Redis服务器"""
        try:
            self.redis_client = await redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                encoding="utf-8"
            )
            
            # 测试连接
            await self.redis_client.ping()
            
            logger.info("Successfully connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self.pubsub:
            await self.pubsub.close()
            self.pubsub = None
        
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        
        logger.info("Disconnected from Redis")
    
    async def start(self) -> None:
        """启动MCP服务器"""
        if self.is_running:
            logger.warning("MCP Server is already running")
            return
        
        if not self.redis_client:
            await self.connect()
        
        self.is_running = True
        
        # 启动消息监听器
        self._listener_task = asyncio.create_task(self._listen_to_messages())
        
        logger.info("MCP Server started")
    
    async def stop(self) -> None:
        """停止MCP服务器"""
        if not self.is_running:
            logger.warning("MCP Server is not running")
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
        
        await self.disconnect()
        
        logger.info("MCP Server stopped")
    
    async def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        注册Agent
        
        Args:
            agent_id: Agent唯一标识符
            agent_type: Agent类型
            metadata: Agent元数据（可选）
        """
        agent_info = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "metadata": metadata or {},
            "registered_at": datetime.now().timestamp()
        }
        
        self.agents[agent_id] = agent_info
        
        # 在Redis中记录注册的Agent（如果已连接）
        if self.redis_client:
            try:
                await self.redis_client.sadd("mcp:agents", agent_id)
                await self.redis_client.hset(
                    f"mcp:agent:{agent_id}:info",
                    mapping={
                        "agent_type": agent_type,
                        "metadata": json.dumps(metadata or {}),
                        "registered_at": str(agent_info["registered_at"])
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to register agent in Redis: {e}")
        
        logger.info(f"Agent registered: {agent_id} (type: {agent_type})")
    
    async def unregister_agent(self, agent_id: str) -> None:
        """
        注销Agent
        
        Args:
            agent_id: Agent唯一标识符
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
        
        # 从Redis中移除Agent记录（如果已连接）
        if self.redis_client:
            try:
                await self.redis_client.srem("mcp:agents", agent_id)
                await self.redis_client.delete(f"mcp:agent:{agent_id}:info")
            except Exception as e:
                logger.warning(f"Failed to unregister agent from Redis: {e}")
        
        logger.info(f"Agent unregistered: {agent_id}")
    
    async def get_registered_agents(self) -> Set[str]:
        """
        获取所有已注册的Agent ID
        
        Returns:
            Agent ID集合
        """
        if not self.redis_client:
            # 如果没有 Redis，返回本地注册的 Agents
            return set(self.agents.keys())
        
        try:
            agents = await self.redis_client.smembers("mcp:agents")
            return agents if agents else set()
        except Exception as e:
            logger.warning(f"Failed to get agents from Redis: {e}")
            return set(self.agents.keys())
    
    async def is_agent_registered(self, agent_id: str) -> bool:
        """
        检查Agent是否已注册
        
        Args:
            agent_id: Agent唯一标识符
            
        Returns:
            是否已注册
        """
        # 先检查本地注册表
        if agent_id in self.agents:
            return True
        
        # 如果有 Redis，再检查 Redis
        if self.redis_client:
            try:
                return await self.redis_client.sismember("mcp:agents", agent_id)
            except Exception as e:
                logger.warning(f"Failed to check agent in Redis: {e}")
        
        return False
    
    async def send_message(self, message: MCPMessage) -> None:
        """
        发送消息
        
        Args:
            message: MCP消息对象
        """
        if not self.redis_client:
            raise RuntimeError("MCP Server is not connected to Redis")
        
        # 确定消息通道
        if message.receiver:
            # 点对点消息
            channel = f"mcp:agent:{message.receiver}"
        else:
            # 广播消息
            channel = "mcp:broadcast"
        
        # 发布消息
        message_json = message.to_json()
        await self.redis_client.publish(channel, message_json)
        
        logger.debug(
            f"Message sent: {message.message_id} "
            f"from {message.sender} to {message.receiver or 'broadcast'} "
            f"(action: {message.action})"
        )
    
    async def subscribe_to_channel(self, channel: str) -> None:
        """
        订阅消息通道
        
        Args:
            channel: 通道名称
        """
        if not self.pubsub:
            self.pubsub = self.redis_client.pubsub()
        
        await self.pubsub.subscribe(channel)
        logger.info(f"Subscribed to channel: {channel}")
    
    async def unsubscribe_from_channel(self, channel: str) -> None:
        """
        取消订阅消息通道
        
        Args:
            channel: 通道名称
        """
        if self.pubsub:
            await self.pubsub.unsubscribe(channel)
            logger.info(f"Unsubscribed from channel: {channel}")
    
    async def _listen_to_messages(self) -> None:
        """监听消息（内部方法）"""
        if not self.pubsub:
            self.pubsub = self.redis_client.pubsub()
        
        # 订阅广播通道
        await self.pubsub.subscribe("mcp:broadcast")
        
        logger.info("Started listening to messages")
        
        try:
            async for message in self.pubsub.listen():
                if not self.is_running:
                    break
                
                if message["type"] == "message":
                    await self._handle_message(message["data"])
        
        except asyncio.CancelledError:
            logger.info("Message listener cancelled")
            raise
        
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
    
    async def _handle_message(self, message_data: str) -> None:
        """
        处理接收到的消息（内部方法）
        
        Args:
            message_data: 消息JSON字符串
        """
        try:
            message = MCPMessage.from_json(message_data)
            
            # 调用注册的消息处理器
            handler = self.message_handlers.get(message.action)
            if handler:
                await handler(message)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def register_message_handler(
        self,
        action: str,
        handler: Callable[[MCPMessage], Any]
    ) -> None:
        """
        注册消息处理器
        
        Args:
            action: 操作类型
            handler: 处理函数
        """
        self.message_handlers[action] = handler
        logger.info(f"Message handler registered for action: {action}")
    
    def unregister_message_handler(self, action: str) -> None:
        """
        注销消息处理器
        
        Args:
            action: 操作类型
        """
        if action in self.message_handlers:
            del self.message_handlers[action]
            logger.info(f"Message handler unregistered for action: {action}")
    
    # ==================== 上下文管理 ====================
    
    async def save_context(self, context: MCPContext) -> None:
        """
        保存上下文到Redis
        
        Args:
            context: MCP上下文对象
        """
        if not self.redis_client:
            raise RuntimeError("MCP Server is not connected to Redis")
        
        context_key = f"mcp:context:{context.context_id}"
        context_json = context.to_json()
        
        # 保存上下文，设置过期时间
        if context.expires_at:
            ttl = int(context.expires_at - datetime.now().timestamp())
            if ttl > 0:
                await self.redis_client.setex(context_key, ttl, context_json)
            else:
                # 已过期，不保存
                logger.warning(f"Context {context.context_id} is already expired")
                return
        else:
            # 默认1小时过期
            await self.redis_client.setex(context_key, 3600, context_json)
        
        logger.debug(f"Context saved: {context.context_id}")
    
    async def get_context(self, context_id: str) -> Optional[MCPContext]:
        """
        从Redis获取上下文
        
        Args:
            context_id: 上下文ID
            
        Returns:
            上下文对象，如果不存在则返回None
        """
        if not self.redis_client:
            raise RuntimeError("MCP Server is not connected to Redis")
        
        context_key = f"mcp:context:{context_id}"
        context_json = await self.redis_client.get(context_key)
        
        if context_json:
            context = MCPContext.from_json(context_json)
            logger.debug(f"Context retrieved: {context_id}")
            return context
        
        logger.debug(f"Context not found: {context_id}")
        return None
    
    async def update_context(self, context: MCPContext) -> None:
        """
        更新上下文
        
        Args:
            context: MCP上下文对象
        """
        # 更新时间戳
        context.updated_at = datetime.now().timestamp()
        
        # 保存到Redis
        await self.save_context(context)
        
        logger.debug(f"Context updated: {context.context_id}")
    
    async def delete_context(self, context_id: str) -> None:
        """
        删除上下文
        
        Args:
            context_id: 上下文ID
        """
        if not self.redis_client:
            raise RuntimeError("MCP Server is not connected to Redis")
        
        context_key = f"mcp:context:{context_id}"
        await self.redis_client.delete(context_key)
        
        logger.debug(f"Context deleted: {context_id}")
    
    async def list_contexts(self, pattern: str = "*") -> list[str]:
        """
        列出所有上下文ID
        
        Args:
            pattern: 匹配模式（默认为所有）
            
        Returns:
            上下文ID列表
        """
        if not self.redis_client:
            raise RuntimeError("MCP Server is not connected to Redis")
        
        keys = []
        async for key in self.redis_client.scan_iter(f"mcp:context:{pattern}"):
            # 提取context_id
            context_id = key.replace("mcp:context:", "")
            keys.append(context_id)
        
        return keys
    
    async def cleanup_expired_contexts(self) -> int:
        """
        清理已过期的上下文
        
        Returns:
            清理的上下文数量
        """
        if not self.redis_client:
            raise RuntimeError("MCP Server is not connected to Redis")
        
        cleaned_count = 0
        
        async for key in self.redis_client.scan_iter("mcp:context:*"):
            context_json = await self.redis_client.get(key)
            if context_json:
                try:
                    context = MCPContext.from_json(context_json)
                    if context.is_expired():
                        await self.redis_client.delete(key)
                        cleaned_count += 1
                        logger.debug(f"Expired context cleaned: {context.context_id}")
                except Exception as e:
                    logger.error(f"Error checking context expiration: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned {cleaned_count} expired contexts")
        
        return cleaned_count
    
    # ==================== 工具方法 ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        try:
            if not self.redis_client:
                return {
                    "status": "unhealthy",
                    "redis_connected": False,
                    "is_running": self.is_running
                }
            
            # 测试Redis连接
            await self.redis_client.ping()
            
            # 获取注册的Agent数量
            agent_count = await self.redis_client.scard("mcp:agents")
            
            # 获取上下文数量
            context_count = 0
            async for _ in self.redis_client.scan_iter("mcp:context:*"):
                context_count += 1
            
            return {
                "status": "healthy",
                "redis_connected": True,
                "is_running": self.is_running,
                "registered_agents": agent_count,
                "active_contexts": context_count
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "redis_connected": False,
                "is_running": self.is_running,
                "error": str(e)
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取服务器统计信息
        
        Returns:
            统计信息
        """
        if not self.redis_client:
            return {"error": "Not connected to Redis"}
        
        try:
            # 获取Redis信息
            redis_info = await self.redis_client.info()
            
            # 获取注册的Agent
            agents = await self.get_registered_agents()
            
            # 获取上下文列表
            contexts = await self.list_contexts()
            
            return {
                "redis_version": redis_info.get("redis_version"),
                "redis_uptime_seconds": redis_info.get("uptime_in_seconds"),
                "redis_connected_clients": redis_info.get("connected_clients"),
                "registered_agents": len(agents),
                "agent_ids": list(agents),
                "active_contexts": len(contexts),
                "is_running": self.is_running
            }
        
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


# ==================== 便捷函数 ====================

async def create_mcp_server(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
    redis_password: Optional[str] = None,
    auto_start: bool = True
) -> MCPServer:
    """
    创建并启动MCP服务器的便捷函数
    
    Args:
        redis_host: Redis主机地址
        redis_port: Redis端口
        redis_db: Redis数据库编号
        redis_password: Redis密码（可选）
        auto_start: 是否自动启动服务器
        
    Returns:
        MCP服务器实例
    """
    server = MCPServer(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_db=redis_db,
        redis_password=redis_password
    )
    
    if auto_start:
        await server.start()
    
    return server
