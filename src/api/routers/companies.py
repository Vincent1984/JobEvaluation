"""企业管理API端点"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ...models.schemas import Company, JobCategory
from datetime import datetime
import uuid
from ..storage import company_storage, category_storage

router = APIRouter()


class CreateCompanyRequest(BaseModel):
    """创建企业请求"""
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "科技有限公司"
            }
        }


class UpdateCompanyRequest(BaseModel):
    """更新企业请求"""
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "新科技有限公司"
            }
        }


@router.post("", response_model=Dict[str, Any])
async def create_company(request: CreateCompanyRequest):
    """
    创建企业
    
    - **name**: 企业名称
    """
    try:
        # 生成企业ID
        company_id = f"comp_{uuid.uuid4().hex[:8]}"
        
        # 创建企业对象
        company = Company(
            id=company_id,
            name=request.name,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 存储企业
        company_storage[company_id] = company
        
        return {
            "success": True,
            "message": "企业创建成功",
            "data": company.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def list_companies():
    """
    列出所有企业
    
    返回所有企业的列表，包含企业名称、创建时间等信息
    """
    companies = list(company_storage.values())
    
    return {
        "success": True,
        "data": [c.model_dump() for c in companies],
        "total": len(companies)
    }


@router.get("/{company_id}", response_model=Dict[str, Any])
async def get_company(company_id: str):
    """
    获取企业详情
    
    - **company_id**: 企业ID
    """
    company = company_storage.get(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail=f"企业 {company_id} 不存在")
    
    return {
        "success": True,
        "data": company.model_dump()
    }


@router.put("/{company_id}", response_model=Dict[str, Any])
async def update_company(company_id: str, request: UpdateCompanyRequest):
    """
    更新企业名称
    
    - **company_id**: 企业ID
    - **name**: 新的企业名称
    """
    company = company_storage.get(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail=f"企业 {company_id} 不存在")
    
    # 更新企业名称
    company.name = request.name
    company.updated_at = datetime.now()
    
    return {
        "success": True,
        "message": "企业更新成功",
        "data": company.model_dump()
    }


@router.delete("/{company_id}", response_model=Dict[str, Any])
async def delete_company(company_id: str, confirm: bool = False):
    """
    删除企业（带确认提示）
    
    - **company_id**: 企业ID
    - **confirm**: 确认删除标志（必须为true才能删除）
    
    注意：删除企业将同时删除该企业下的所有职位分类和标签
    """
    company = company_storage.get(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail=f"企业 {company_id} 不存在")
    
    # 检查是否确认删除
    if not confirm:
        # 统计该企业下的分类数量
        company_categories = [
            c for c in category_storage.values()
            if c.company_id == company_id
        ]
        
        return {
            "success": False,
            "message": "需要确认删除操作",
            "warning": f"删除企业将同时删除 {len(company_categories)} 个职位分类及其所有标签",
            "confirm_required": True,
            "data": {
                "company_id": company_id,
                "company_name": company.name,
                "categories_count": len(company_categories)
            }
        }
    
    # 执行删除操作
    # 1. 删除该企业下的所有分类和标签
    # 获取该企业的所有分类
    company_categories = [
        c for c in category_storage.values()
        if c.company_id == company_id
    ]
    
    # 删除所有分类
    for category in company_categories:
        if category.id in category_storage:
            del category_storage[category.id]
    
    # 2. 删除企业
    del company_storage[company_id]
    
    return {
        "success": True,
        "message": f"企业删除成功，已同时删除 {len(company_categories)} 个职位分类"
    }


@router.get("/{company_id}/categories", response_model=Dict[str, Any])
async def list_company_categories(
    company_id: str,
    level: Optional[int] = None
):
    """
    列出企业的分类
    
    - **company_id**: 企业ID
    - **level**: 筛选指定层级（可选）
    """
    company = company_storage.get(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail=f"企业 {company_id} 不存在")
    
    # 获取该企业的所有分类
    company_categories = [
        c for c in category_storage.values()
        if c.company_id == company_id
    ]
    
    # 筛选层级
    if level is not None:
        company_categories = [c for c in company_categories if c.level == level]
    
    return {
        "success": True,
        "data": [c.model_dump() for c in company_categories],
        "total": len(company_categories)
    }


@router.get("/{company_id}/categories/tree", response_model=Dict[str, Any])
async def get_company_category_tree(company_id: str):
    """
    获取企业的分类树（3层级结构）
    
    - **company_id**: 企业ID
    
    返回该企业完整的分类树结构，包含父子关系
    """
    company = company_storage.get(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail=f"企业 {company_id} 不存在")
    
    # 获取该企业的所有分类
    company_categories = {
        c.id: c for c in category_storage.values()
        if c.company_id == company_id
    }
    
    def build_tree(parent_id: Optional[str] = None, level: int = 1) -> List[Dict]:
        """递归构建分类树"""
        children = [
            c for c in company_categories.values()
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
        "data": {
            "company": company.model_dump(),
            "category_tree": tree
        }
    }



@router.post("/{company_id}/categories", response_model=Dict[str, Any])
async def create_company_category(company_id: str, request: Dict[str, Any]):
    """
    为企业创建职位分类
    
    - **company_id**: 企业ID
    - **name**: 分类名称
    - **level**: 分类层级（1-3）
    - **parent_id**: 父级分类ID（二级和三级必填）
    - **description**: 分类描述（可选）
    - **sample_jd_ids**: 样本JD列表（仅第三层级，1-2个）
    """
    company = company_storage.get(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail=f"企业 {company_id} 不存在")
    
    # 生成分类ID
    category_id = f"cat_{uuid.uuid4().hex[:8]}"
    
    # 创建分类对象
    try:
        category = JobCategory(
            id=category_id,
            company_id=company_id,
            name=request.get("name"),
            level=request.get("level"),
            parent_id=request.get("parent_id"),
            description=request.get("description"),
            sample_jd_ids=request.get("sample_jd_ids", []),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 存储分类
        category_storage[category_id] = category
        
        return {
            "success": True,
            "message": "分类创建成功",
            "data": category.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
