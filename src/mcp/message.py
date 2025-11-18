"""MCP消息协议 - 消息格式定义"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid
import json


class MessageType(str, Enum):
    """消息类型枚举"""
    REQUEST = "request"  # 请求消息（需要响应）
    RESPONSE = "response"  # 响应消息
    NOTIFICATION = "notification"  # 通知消息（不需要响应）
    EVENT = "event"  # 事件消息（广播）


class MCPMessage(BaseModel):
    """
    MCP标准消息格式
    
    用于Agent间的标准化通讯，支持请求-响应模式和事件通知模式
    """
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="消息唯一标识符"
    )
    sender: str = Field(description="发送者Agent ID")
    receiver: Optional[str] = Field(
        None,
        description="接收者Agent ID，None表示广播消息"
    )
    message_type: MessageType = Field(description="消息类型")
    action: str = Field(description="操作类型/动作名称")
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="消息负载数据"
    )
    context_id: Optional[str] = Field(
        None,
        description="关联的上下文ID，用于跟踪相关消息"
    )
    correlation_id: Optional[str] = Field(
        None,
        description="关联的请求消息ID，用于响应消息匹配请求"
    )
    timestamp: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        description="消息时间戳"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="消息元数据（如优先级、过期时间等）"
    )
    
    def to_json(self) -> str:
        """序列化为JSON字符串"""
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """从JSON字符串反序列化"""
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """从字典创建消息"""
        return cls.model_validate(data)
    
    def create_response(
        self,
        payload: Dict[str, Any],
        sender: str
    ) -> 'MCPMessage':
        """
        创建响应消息
        
        Args:
            payload: 响应数据
            sender: 响应者Agent ID
            
        Returns:
            响应消息对象
        """
        return MCPMessage(
            sender=sender,
            receiver=self.sender,  # 响应给原发送者
            message_type=MessageType.RESPONSE,
            action=f"{self.action}_response",
            payload=payload,
            context_id=self.context_id,
            correlation_id=self.message_id,  # 关联原请求
            metadata=self.metadata
        )
    
    def is_request(self) -> bool:
        """判断是否为请求消息"""
        return self.message_type == MessageType.REQUEST
    
    def is_response(self) -> bool:
        """判断是否为响应消息"""
        return self.message_type == MessageType.RESPONSE
    
    def is_notification(self) -> bool:
        """判断是否为通知消息"""
        return self.message_type == MessageType.NOTIFICATION
    
    def is_event(self) -> bool:
        """判断是否为事件消息"""
        return self.message_type == MessageType.EVENT
    
    def is_broadcast(self) -> bool:
        """判断是否为广播消息"""
        return self.receiver is None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_123e4567-e89b-12d3-a456-426614174000",
                "sender": "parser_agent",
                "receiver": "data_manager_agent",
                "message_type": "request",
                "action": "save_jd",
                "payload": {
                    "jd_id": "jd_001",
                    "job_title": "高级Python工程师",
                    "raw_text": "招聘高级Python工程师..."
                },
                "context_id": "ctx_001",
                "correlation_id": None,
                "timestamp": 1704067200.0,
                "metadata": {
                    "priority": "high",
                    "timeout": 30
                }
            }
        }


def create_request_message(
    sender: str,
    receiver: str,
    action: str,
    payload: Dict[str, Any],
    context_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MCPMessage:
    """
    创建请求消息的便捷函数
    
    Args:
        sender: 发送者Agent ID
        receiver: 接收者Agent ID
        action: 操作类型
        payload: 消息数据
        context_id: 上下文ID（可选）
        metadata: 元数据（可选）
        
    Returns:
        请求消息对象
    """
    return MCPMessage(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.REQUEST,
        action=action,
        payload=payload,
        context_id=context_id,
        metadata=metadata or {}
    )


def create_notification_message(
    sender: str,
    action: str,
    payload: Dict[str, Any],
    context_id: Optional[str] = None,
    receiver: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MCPMessage:
    """
    创建通知消息的便捷函数
    
    Args:
        sender: 发送者Agent ID
        action: 操作类型
        payload: 消息数据
        context_id: 上下文ID（可选）
        receiver: 接收者Agent ID（可选，None表示广播）
        metadata: 元数据（可选）
        
    Returns:
        通知消息对象
    """
    return MCPMessage(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.NOTIFICATION,
        action=action,
        payload=payload,
        context_id=context_id,
        metadata=metadata or {}
    )


def create_event_message(
    sender: str,
    action: str,
    payload: Dict[str, Any],
    context_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MCPMessage:
    """
    创建事件消息的便捷函数（广播）
    
    Args:
        sender: 发送者Agent ID
        action: 事件类型
        payload: 事件数据
        context_id: 上下文ID（可选）
        metadata: 元数据（可选）
        
    Returns:
        事件消息对象
    """
    return MCPMessage(
        sender=sender,
        receiver=None,  # 事件消息总是广播
        message_type=MessageType.EVENT,
        action=action,
        payload=payload,
        context_id=context_id,
        metadata=metadata or {}
    )
