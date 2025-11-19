"""职位分类管理API端点"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ...models.schemas import JobCategory, CategoryTag
from datetime import datetime
import uuid
from ..storage import category_storage, tag_storage

router = APIRouter()


class CreateCategoryRequest(BaseModel):
    """创建分类请求"""
    company_id: str
    name: str
    level: int
    parent_id: Optional[str] = None
    description: Optional[str] = None
    sample_jd_ids: List[str] = []


class UpdateCategoryRequest(BaseModel):
    """更新分类请求"""
    name: Optional[str] = None
    description: Optional[str] = None


class UpdateSamplesRequest(BaseModel):
    """更新样本JD请求"""
    sample_jd_ids: List[str]


@router.post("", response_model=Dict[str, Any])
async def create_category(request: CreateCategoryRequest):
    """
    创建职位分类（支持添加样本JD）
    
    - **company_id**: 所属企业ID
    - **name**: 分类名称
    - **level**: 分类层级（1-3）
    - **parent_id**: 父级分类ID（二级和三级必填）
    - **description**: 分类描述（可选）
    - **sample_jd_ids**: 样本JD列表（仅第三层级，1-2个）
    """
    try:
        # 验证企业是否存在
        from . import companies
        if request.company_id not in companies.company_storage:
            raise HTTPException(
                status_code=404,
                detail=f"企业 {request.company_id} 不存在"
            )
        
        # 生成分类ID
        category_id = f"cat_{uuid.uuid4().hex[:8]}"
        
        # 创建分类对象（会自动验证规则）
        category = JobCategory(
            id=category_id,
            company_id=request.company_id,
            name=request.name,
            level=request.level,
            parent_id=request.parent_id,
            description=request.description,
            sample_jd_ids=request.sample_jd_ids,
            created_at=datetime.now()
        )
        
        # 验证父级分类是否存在
        if category.parent_id:
            parent = category_storage.get(category.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=404,
                    detail=f"父级分类 {category.parent_id} 不存在"
                )
            
            # 验证父级层级是否正确
            if parent.level != category.level - 1:
                raise HTTPException(
                    status_code=400,
                    detail=f"父级分类层级不匹配：期望 {category.level - 1}，实际 {parent.level}"
                )
        
        # 存储分类
        category_storage[category_id] = category
        
        return {
            "success": True,
            "message": "分类创建成功",
            "data": category.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def list_categories(
    level: Optional[int] = None,
    parent_id: Optional[str] = None
):
    """
    列出职位分类
    
    - **level**: 筛选指定层级（可选）
    - **parent_id**: 筛选指定父级的子分类（可选）
    """
    categories = list(category_storage.values())
    
    # 筛选
    if level is not None:
        categories = [c for c in categories if c.level == level]
    
    if parent_id is not None:
        categories = [c for c in categories if c.parent_id == parent_id]
    
    return {
        "success": True,
        "data": [c.model_dump() for c in categories],
        "total": len(categories)
    }


@router.get("/tree", response_model=Dict[str, Any])
async def get_category_tree():
    """
    获取分类树（3层级结构）
    
    返回完整的分类树结构，包含父子关系
    """
    def build_tree(parent_id: Optional[str] = None, level: int = 1) -> List[Dict]:
        """递归构建分类树"""
        children = [
            c for c in category_storage.values()
            if c.parent_id == parent_id and c.level == level
        ]
        
        tree = []
        for category in children:
            node = category.model_dump()
            
            # 递归获取子分类
            if level < 3:
                node["children"] = build_tree(category.id, level + 1)
            else:
                node["children"] = []
            
            tree.append(node)
        
        return tree
    
    tree = build_tree(parent_id=None, level=1)
    
    return {
        "success": True,
        "data": tree
    }


@router.get("/{category_id}", response_model=Dict[str, Any])
async def get_category(category_id: str):
    """
    获取分类详情
    
    - **category_id**: 分类ID
    """
    category = category_storage.get(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail=f"分类 {category_id} 不存在")
    
    return {
        "success": True,
        "data": category.model_dump()
    }


@router.put("/{category_id}", response_model=Dict[str, Any])
async def update_category(category_id: str, request: UpdateCategoryRequest):
    """
    更新分类
    
    - **category_id**: 分类ID
    - **name**: 新的分类名称（可选）
    - **description**: 新的分类描述（可选）
    """
    category = category_storage.get(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail=f"分类 {category_id} 不存在")
    
    # 更新字段
    if request.name is not None:
        category.name = request.name
    if request.description is not None:
        category.description = request.description
    
    return {
        "success": True,
        "message": "分类更新成功",
        "data": category.model_dump()
    }


@router.put("/{category_id}/samples", response_model=Dict[str, Any])
async def update_category_samples(category_id: str, request: UpdateSamplesRequest):
    """
    更新样本JD
    
    - **category_id**: 分类ID（必须是第三层级）
    - **sample_jd_ids**: 样本JD ID列表（1-2个）
    """
    category = category_storage.get(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail=f"分类 {category_id} 不存在")
    
    # 验证是否为第三层级
    if category.level != 3:
        raise HTTPException(
            status_code=400,
            detail="只有第三层级分类才能添加样本JD"
        )
    
    # 验证样本数量
    if len(request.sample_jd_ids) > 2:
        raise HTTPException(
            status_code=400,
            detail="样本JD数量不能超过2个"
        )
    
    # 更新样本JD
    category.sample_jd_ids = request.sample_jd_ids
    
    return {
        "success": True,
        "message": "样本JD更新成功",
        "data": category.model_dump()
    }


@router.delete("/{category_id}", response_model=Dict[str, Any])
async def delete_category(category_id: str):
    """
    删除分类
    
    - **category_id**: 分类ID
    
    注意：如果该分类有子分类，将无法删除
    """
    category = category_storage.get(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail=f"分类 {category_id} 不存在")
    
    # 检查是否有子分类
    children = [c for c in category_storage.values() if c.parent_id == category_id]
    if children:
        raise HTTPException(
            status_code=400,
            detail=f"无法删除分类：存在 {len(children)} 个子分类"
        )
    
    # 删除分类
    del category_storage[category_id]
    
    return {
        "success": True,
        "message": "分类删除成功"
    }


# ==================== 分类标签管理端点 ====================

class CreateTagRequest(BaseModel):
    """创建标签请求"""
    name: str
    tag_type: str
    description: str


@router.post("/{category_id}/tags", response_model=Dict[str, Any])
async def create_category_tag(category_id: str, request: CreateTagRequest):
    """
    为第三层级分类添加标签
    
    - **category_id**: 分类ID（必须是第三层级）
    - **name**: 标签名称
    - **tag_type**: 标签类型（战略重要性、业务价值、技能稀缺性、市场竞争度、发展潜力、风险等级）
    - **description**: 标签描述和对评估的影响说明
    """
    try:
        # 验证分类是否存在
        category = category_storage.get(category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"分类 {category_id} 不存在"
            )
        
        # 验证是否为第三层级
        if category.level != 3:
            raise HTTPException(
                status_code=400,
                detail="只有第三层级分类才能添加标签"
            )
        
        # 验证标签类型
        valid_tag_types = [
            "战略重要性", "业务价值", "技能稀缺性", 
            "市场竞争度", "发展潜力", "风险等级"
        ]
        if request.tag_type not in valid_tag_types:
            raise HTTPException(
                status_code=400,
                detail=f"无效的标签类型。有效类型: {', '.join(valid_tag_types)}"
            )
        
        # 生成标签ID
        tag_id = f"tag_{uuid.uuid4().hex[:8]}"
        
        # 创建标签对象
        tag = CategoryTag(
            id=tag_id,
            category_id=category_id,
            name=request.name,
            tag_type=request.tag_type,
            description=request.description,
            created_at=datetime.now()
        )
        
        # 存储标签
        tag_storage[tag_id] = tag
        
        # 更新分类的标签列表
        category.tags.append(tag)
        
        return {
            "success": True,
            "message": "标签创建成功",
            "data": tag.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category_id}/tags", response_model=Dict[str, Any])
async def get_category_tags(category_id: str):
    """
    获取分类的所有标签
    
    - **category_id**: 分类ID
    """
    # 验证分类是否存在
    category = category_storage.get(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"分类 {category_id} 不存在"
        )
    
    # 获取该分类的所有标签
    tags = [tag for tag in tag_storage.values() if tag.category_id == category_id]
    
    return {
        "success": True,
        "data": [tag.model_dump() for tag in tags],
        "total": len(tags)
    }
