"""JD分析相关API端点"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ...models.schemas import (
    JobDescription,
    EvaluationResult,
    EvaluationModel
)
from ...mcp.simple_client import get_simple_mcp_client
from ...utils.file_parser import file_parser

# 获取简化 MCP 客户端（不依赖 Redis）
mcp_client = get_simple_mcp_client()

router = APIRouter()


class JDAnalyzeRequest(BaseModel):
    """JD分析请求"""
    jd_text: str
    model_type: EvaluationModel = EvaluationModel.STANDARD
    custom_fields: Optional[Dict[str, Any]] = None


class JDParseRequest(BaseModel):
    """JD解析请求"""
    jd_text: str
    custom_fields: Optional[Dict[str, Any]] = None


class UpdateCategoryRequest(BaseModel):
    """更新分类请求"""
    category_level1_id: Optional[str] = None
    category_level2_id: Optional[str] = None
    category_level3_id: Optional[str] = None


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_jd(request: JDAnalyzeRequest):
    """
    完整JD分析（解析+评估）
    
    - **jd_text**: 岗位JD文本
    - **model_type**: 评估模型类型（standard/mercer_ipe/factor_comparison）
    - **custom_fields**: 自定义字段配置（可选）
    """
    try:
        result = await mcp_client.analyze_jd(
            jd_text=request.jd_text,
            model_type=request.model_type
        )
        
        return {
            "success": True,
            "data": {
                "jd": result["jd"].model_dump(),
                "evaluation": result["evaluation"].model_dump()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse", response_model=Dict[str, Any])
async def parse_jd(request: JDParseRequest):
    """
    仅解析JD（不进行评估）
    
    - **jd_text**: 岗位JD文本
    - **custom_fields**: 自定义字段配置（可选）
    """
    try:
        jd = await mcp_client.parse_jd(jd_text=request.jd_text)
        
        return {
            "success": True,
            "data": jd.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{jd_id}", response_model=Dict[str, Any])
async def get_jd(jd_id: str):
    """
    获取JD详情
    
    - **jd_id**: JD的唯一标识符
    """
    jd = await mcp_client.get_jd(jd_id)
    
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD {jd_id} 不存在")
    
    return {
        "success": True,
        "data": jd.model_dump()
    }


@router.get("/{jd_id}/evaluation", response_model=Dict[str, Any])
async def get_jd_evaluation(jd_id: str):
    """
    获取JD的评估结果
    
    - **jd_id**: JD的唯一标识符
    """
    # 查找该JD的评估结果
    jd = await mcp_client.get_jd(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD {jd_id} 不存在")
    
    # 通过 DataManagerAgent 获取评估结果
    try:
        from ...mcp.client import get_mcp_client
        client = get_mcp_client()
        response = await client._call_agent(
            receiver="data_manager",
            action="get_evaluation",
            payload={"jd_id": jd_id}
        )
        
        if not response.payload.get("success") or not response.payload.get("evaluation"):
            raise HTTPException(status_code=404, detail=f"JD {jd_id} 的评估结果不存在")
        
        latest_evaluation = EvaluationResult(**response.payload["evaluation"])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"JD {jd_id} 的评估结果不存在")
    
    return {
        "success": True,
        "data": latest_evaluation.model_dump()
    }


@router.put("/{jd_id}/category", response_model=Dict[str, Any])
async def update_jd_category(jd_id: str, request: UpdateCategoryRequest):
    """
    手动更新JD分类
    
    - **jd_id**: JD的唯一标识符
    - **category_level1_id**: 一级分类ID（可选）
    - **category_level2_id**: 二级分类ID（可选）
    - **category_level3_id**: 三级分类ID（可选）
    """
    jd = await mcp_client.get_jd(jd_id)
    
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD {jd_id} 不存在")
    
    # 通过 DataManagerAgent 更新分类
    try:
        from ...mcp.client import get_mcp_client
        client = get_mcp_client()
        response = await client._call_agent(
            receiver="data_manager",
            action="update_jd_category",
            payload={
                "jd_id": jd_id,
                "category_level1_id": request.category_level1_id,
                "category_level2_id": request.category_level2_id,
                "category_level3_id": request.category_level3_id
            }
        )
        
        if not response.payload.get("success"):
            raise HTTPException(status_code=500, detail="更新分类失败")
        
        # 重新获取更新后的 JD
        jd = await mcp_client.get_jd(jd_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "success": True,
        "message": "分类更新成功",
        "data": jd.model_dump()
    }


@router.put("/{jd_id}/evaluation", response_model=Dict[str, Any])
async def update_jd_evaluation(jd_id: str, request: Dict[str, Any]):
    """
    手动修改JD评估结果
    
    - **jd_id**: JD的唯一标识符
    - **modifications**: 要修改的字段（overall_score, company_value, is_core_position）
    - **reason**: 修改原因（可选）
    
    支持修改的字段：
    - overall_score: 综合质量分数（0-100）
    - company_value: 企业价值评级（高价值/中价值/低价值）
    - is_core_position: 是否核心岗位（true/false）
    """
    try:
        # 验证JD是否存在
        jd = await mcp_client.get_jd(jd_id)
        if not jd:
            raise HTTPException(status_code=404, detail=f"JD {jd_id} 不存在")
        
        # 提取修改字段和原因
        modifications = {}
        reason = request.get("reason", "")
        
        # 支持的字段
        allowed_fields = ["overall_score", "company_value", "is_core_position"]
        
        for field in allowed_fields:
            if field in request:
                modifications[field] = request[field]
        
        if not modifications:
            raise HTTPException(
                status_code=400, 
                detail=f"请提供要修改的字段。支持的字段: {', '.join(allowed_fields)}"
            )
        
        # 验证字段值
        if "overall_score" in modifications:
            score = modifications["overall_score"]
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                raise HTTPException(
                    status_code=400,
                    detail="overall_score 必须是0-100之间的数字"
                )
        
        if "company_value" in modifications:
            value = modifications["company_value"]
            if value not in ["高价值", "中价值", "低价值"]:
                raise HTTPException(
                    status_code=400,
                    detail="company_value 必须是：高价值、中价值或低价值"
                )
        
        if "is_core_position" in modifications:
            if not isinstance(modifications["is_core_position"], bool):
                raise HTTPException(
                    status_code=400,
                    detail="is_core_position 必须是布尔值"
                )
        
        # 通过 EvaluatorAgent 更新评估结果
        from ...mcp.client import get_mcp_client
        client = get_mcp_client()
        response = await client._call_agent(
            receiver="evaluator",
            action="update_evaluation",
            payload={
                "jd_id": jd_id,
                "modifications": modifications,
                "reason": reason
            }
        )
        
        if not response.payload.get("success"):
            raise HTTPException(status_code=500, detail="更新评估结果失败")
        
        updated_evaluation = EvaluationResult(**response.payload["evaluation"])
        
        return {
            "success": True,
            "message": "评估结果已更新",
            "data": updated_evaluation.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=Dict[str, Any])
async def upload_jd_file(
    file: UploadFile = File(...),
    model_type: EvaluationModel = EvaluationModel.STANDARD
):
    """
    单个文件上传并分析
    
    - **file**: JD文件（支持TXT、PDF、DOCX格式）
    - **model_type**: 评估模型类型
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 验证文件
        is_valid, error_msg = file_parser.validate_file(
            file_size=len(file_content),
            filename=file.filename
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 解析文件
        jd_text = file_parser.parse_file(file_content, file.filename)
        
        # 分析JD
        result = await mcp_client.analyze_jd(
            jd_text=jd_text,
            model_type=model_type
        )
        
        return {
            "success": True,
            "message": f"文件 {file.filename} 分析完成",
            "data": {
                "jd": result["jd"].model_dump(),
                "evaluation": result["evaluation"].model_dump()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
