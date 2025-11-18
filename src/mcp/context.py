"""MCP上下文协议 - 共享上下文定义"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json


class MCPContext(BaseModel):
    """
    MCP共享上下文
    
    用于在多个Agent之间共享任务相关的数据和状态，
    支持工作流跟踪和数据传递
    """
    context_id: str = Field(
        default_factory=lambda: f"ctx_{uuid.uuid4()}",
        description="上下文唯一标识符"
    )
    task_id: str = Field(description="关联的任务ID")
    workflow_type: str = Field(
        default="general",
        description="工作流类型（如：jd_analysis, questionnaire_generation等）"
    )
    shared_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Agent间共享的数据"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="上下文元数据（如创建者、优先级等）"
    )
    status: str = Field(
        default="active",
        description="上下文状态（active, completed, failed, cancelled）"
    )
    created_at: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        description="创建时间戳"
    )
    updated_at: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        description="最后更新时间戳"
    )
    expires_at: Optional[float] = Field(
        None,
        description="过期时间戳（可选）"
    )
    participants: List[str] = Field(
        default_factory=list,
        description="参与的Agent ID列表"
    )
    
    def to_json(self) -> str:
        """序列化为JSON字符串"""
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPContext':
        """从JSON字符串反序列化"""
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPContext':
        """从字典创建上下文"""
        return cls.model_validate(data)
    
    def update_data(self, key: str, value: Any) -> None:
        """
        更新共享数据
        
        Args:
            key: 数据键
            value: 数据值
        """
        self.shared_data[key] = value
        self.updated_at = datetime.now().timestamp()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """
        获取共享数据
        
        Args:
            key: 数据键
            default: 默认值
            
        Returns:
            数据值
        """
        return self.shared_data.get(key, default)
    
    def has_data(self, key: str) -> bool:
        """
        检查是否存在指定的共享数据
        
        Args:
            key: 数据键
            
        Returns:
            是否存在
        """
        return key in self.shared_data
    
    def remove_data(self, key: str) -> None:
        """
        移除共享数据
        
        Args:
            key: 数据键
        """
        if key in self.shared_data:
            del self.shared_data[key]
            self.updated_at = datetime.now().timestamp()
    
    def add_participant(self, agent_id: str) -> None:
        """
        添加参与者
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self.participants:
            self.participants.append(agent_id)
            self.updated_at = datetime.now().timestamp()
    
    def remove_participant(self, agent_id: str) -> None:
        """
        移除参与者
        
        Args:
            agent_id: Agent ID
        """
        if agent_id in self.participants:
            self.participants.remove(agent_id)
            self.updated_at = datetime.now().timestamp()
    
    def is_participant(self, agent_id: str) -> bool:
        """
        检查是否为参与者
        
        Args:
            agent_id: Agent ID
            
        Returns:
            是否为参与者
        """
        return agent_id in self.participants
    
    def update_status(self, status: str) -> None:
        """
        更新上下文状态
        
        Args:
            status: 新状态（active, completed, failed, cancelled）
        """
        valid_statuses = ["active", "completed", "failed", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        self.status = status
        self.updated_at = datetime.now().timestamp()
    
    def is_active(self) -> bool:
        """判断上下文是否处于活动状态"""
        return self.status == "active"
    
    def is_completed(self) -> bool:
        """判断上下文是否已完成"""
        return self.status == "completed"
    
    def is_failed(self) -> bool:
        """判断上下文是否失败"""
        return self.status == "failed"
    
    def is_cancelled(self) -> bool:
        """判断上下文是否已取消"""
        return self.status == "cancelled"
    
    def is_expired(self) -> bool:
        """
        判断上下文是否已过期
        
        Returns:
            是否过期
        """
        if self.expires_at is None:
            return False
        return datetime.now().timestamp() > self.expires_at
    
    def set_expiration(self, seconds: int) -> None:
        """
        设置过期时间
        
        Args:
            seconds: 从现在开始的秒数
        """
        self.expires_at = datetime.now().timestamp() + seconds
        self.updated_at = datetime.now().timestamp()
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        更新元数据
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        self.metadata[key] = value
        self.updated_at = datetime.now().timestamp()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        获取元数据
        
        Args:
            key: 元数据键
            default: 默认值
            
        Returns:
            元数据值
        """
        return self.metadata.get(key, default)
    
    class Config:
        json_schema_extra = {
            "example": {
                "context_id": "ctx_123e4567-e89b-12d3-a456-426614174000",
                "task_id": "task_001",
                "workflow_type": "jd_analysis",
                "shared_data": {
                    "jd_text": "招聘高级Python工程师...",
                    "jd_id": "jd_001",
                    "parsed_data": {
                        "job_title": "高级Python工程师",
                        "department": "技术部"
                    }
                },
                "metadata": {
                    "creator": "coordinator_agent",
                    "priority": "high",
                    "user_id": "user_001"
                },
                "status": "active",
                "created_at": 1704067200.0,
                "updated_at": 1704067200.0,
                "expires_at": 1704070800.0,
                "participants": [
                    "coordinator_agent",
                    "parser_agent",
                    "evaluator_agent",
                    "data_manager_agent"
                ]
            }
        }


def create_context(
    task_id: str,
    workflow_type: str = "general",
    shared_data: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    expiration_seconds: Optional[int] = None
) -> MCPContext:
    """
    创建MCP上下文的便捷函数
    
    Args:
        task_id: 任务ID
        workflow_type: 工作流类型
        shared_data: 初始共享数据（可选）
        metadata: 元数据（可选）
        expiration_seconds: 过期时间（秒，可选）
        
    Returns:
        上下文对象
    """
    context = MCPContext(
        task_id=task_id,
        workflow_type=workflow_type,
        shared_data=shared_data or {},
        metadata=metadata or {}
    )
    
    if expiration_seconds is not None:
        context.set_expiration(expiration_seconds)
    
    return context
