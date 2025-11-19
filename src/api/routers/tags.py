"""分类标签管理API端点"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...models.schemas import CategoryTag
from datetime import datetime

router = APIRouter()


class UpdateTagRequest(BaseModel):
    """更新标签请求"""
    name: Optional[str] = None
    tag_type: Optional[str] = None
    description: Optional[str] = None


@router.put("/{tag_id}", response_model=Dict[str, Any])
async def update_tag(tag_id: str, request: UpdateTagRequest):
    """
    更新标签
    
    - **tag_id**: 标签ID
    - **name**: 新的标签名称（可选）
    - **tag_type**: 新的标签类型（可选）
    - **description**: 新的标签描述（可选）
    """
    # 导入存储（从categories模块）
    from . import categories
    
    # 验证标签是否存在
    tag = categories.tag_storage.get(tag_id)
    if not tag:
        raise HTTPException(
            status_code=404,
            detail=f"标签 {tag_id} 不存在"
        )
    
    # 验证标签类型（如果提供）
    if request.tag_type is not None:
        valid_tag_types = [
            "战略重要性", "业务价值", "技能稀缺性", 
            "市场竞争度", "发展潜力", "风险等级"
        ]
        if request.tag_type not in valid_tag_types:
            raise HTTPException(
                status_code=400,
                detail=f"无效的标签类型。有效类型: {', '.join(valid_tag_types)}"
            )
    
    # 更新字段
    if request.name is not None:
        tag.name = request.name
    if request.tag_type is not None:
        tag.tag_type = request.tag_type
    if request.description is not None:
        tag.description = request.description
    
    # 同时更新分类中的标签引用
    category = categories.category_storage.get(tag.category_id)
    if category:
        for i, cat_tag in enumerate(category.tags):
            if cat_tag.id == tag_id:
                category.tags[i] = tag
                break
    
    return {
        "success": True,
        "message": "标签更新成功",
        "data": tag.model_dump()
    }


@router.delete("/{tag_id}", response_model=Dict[str, Any])
async def delete_tag(tag_id: str):
    """
    删除标签
    
    - **tag_id**: 标签ID
    """
    # 导入存储（从categories模块）
    from . import categories
    
    # 验证标签是否存在
    tag = categories.tag_storage.get(tag_id)
    if not tag:
        raise HTTPException(
            status_code=404,
            detail=f"标签 {tag_id} 不存在"
        )
    
    # 从分类中移除标签引用
    category = categories.category_storage.get(tag.category_id)
    if category:
        category.tags = [t for t in category.tags if t.id != tag_id]
    
    # 删除标签
    del categories.tag_storage[tag_id]
    
    return {
        "success": True,
        "message": "标签删除成功"
    }
