"""批量处理API端点"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ...models.schemas import EvaluationModel
from ...mcp.simple_client import get_simple_mcp_client
from ...utils.file_parser import file_parser

# 获取简化 MCP 客户端（不依赖 Redis）
mcp_client = get_simple_mcp_client()
from datetime import datetime
import uuid
import asyncio

router = APIRouter()

# 批量处理状态存储
batch_status_storage: Dict[str, Dict[str, Any]] = {}
batch_results_storage: Dict[str, Dict[str, Any]] = {}


class BatchAnalyzeRequest(BaseModel):
    """批量分析请求"""
    jd_texts: List[str]
    model_type: EvaluationModel = EvaluationModel.STANDARD


class BatchMatchRequest(BaseModel):
    """批量匹配请求"""
    jd_id: str
    candidate_profiles: List[Dict[str, Any]]


@router.post("/upload", response_model=Dict[str, Any])
async def batch_upload_files(
    files: List[UploadFile] = File(...),
    model_type: EvaluationModel = EvaluationModel.STANDARD
):
    """
    批量文件上传（最多20个）
    
    - **files**: JD文件列表（支持TXT、PDF、DOCX格式）
    - **model_type**: 评估模型类型
    
    返回批量处理ID，可用于查询处理状态和结果
    """
    # 验证文件数量
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"文件数量超过限制：最多20个，当前{len(files)}个"
        )
    
    # 生成批量处理ID
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    
    # 初始化状态
    batch_status_storage[batch_id] = {
        "batch_id": batch_id,
        "status": "processing",
        "total_files": len(files),
        "processed_files": 0,
        "successful_files": 0,
        "failed_files": 0,
        "started_at": datetime.now(),
        "completed_at": None
    }
    
    # 异步处理文件
    asyncio.create_task(
        process_batch_upload(batch_id, files, model_type)
    )
    
    return {
        "success": True,
        "message": f"批量上传已启动，共{len(files)}个文件",
        "data": {
            "batch_id": batch_id,
            "total_files": len(files)
        }
    }


async def process_batch_upload(
    batch_id: str,
    files: List[UploadFile],
    model_type: EvaluationModel
):
    """处理批量上传（后台任务）"""
    results = []
    successful = 0
    failed = 0
    
    for idx, file in enumerate(files, 1):
        try:
            # 读取文件内容
            file_content = await file.read()
            
            # 验证文件
            is_valid, error_msg = file_parser.validate_file(
                file_size=len(file_content),
                filename=file.filename
            )
            
            if not is_valid:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": error_msg
                })
                failed += 1
                continue
            
            # 解析文件
            jd_text = file_parser.parse_file(file_content, file.filename)
            
            # 分析JD
            result = await mcp_client.analyze_jd(
                jd_text=jd_text,
                model_type=model_type
            )
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "jd_id": result["jd"].id,
                "job_title": result["jd"].job_title,
                "quality_score": result["evaluation"].quality_score.overall_score
            })
            successful += 1
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
            failed += 1
        
        # 更新进度
        batch_status_storage[batch_id]["processed_files"] = idx
        batch_status_storage[batch_id]["successful_files"] = successful
        batch_status_storage[batch_id]["failed_files"] = failed
    
    # 完成处理
    batch_status_storage[batch_id]["status"] = "completed"
    batch_status_storage[batch_id]["completed_at"] = datetime.now()
    
    # 保存结果
    batch_results_storage[batch_id] = {
        "batch_id": batch_id,
        "results": results,
        "summary": {
            "total": len(files),
            "successful": successful,
            "failed": failed
        }
    }


@router.get("/status/{batch_id}", response_model=Dict[str, Any])
async def get_batch_status(batch_id: str):
    """
    查询批量处理状态
    
    - **batch_id**: 批量处理ID
    """
    status = batch_status_storage.get(batch_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"批量处理 {batch_id} 不存在"
        )
    
    return {
        "success": True,
        "data": status
    }


@router.get("/results/{batch_id}", response_model=Dict[str, Any])
async def get_batch_results(batch_id: str):
    """
    获取批量处理结果
    
    - **batch_id**: 批量处理ID
    """
    results = batch_results_storage.get(batch_id)
    
    if not results:
        # 检查是否还在处理中
        status = batch_status_storage.get(batch_id)
        if status and status["status"] == "processing":
            raise HTTPException(
                status_code=202,
                detail="批量处理仍在进行中，请稍后查询"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"批量处理结果 {batch_id} 不存在"
            )
    
    return {
        "success": True,
        "data": results
    }


@router.post("/analyze", response_model=Dict[str, Any])
async def batch_analyze_jds(request: BatchAnalyzeRequest):
    """
    批量分析JD文本
    
    - **jd_texts**: JD文本列表
    - **model_type**: 评估模型类型
    """
    if len(request.jd_texts) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"JD数量超过限制：最多20个，当前{len(request.jd_texts)}个"
        )
    
    try:
        results = []
        
        # 并发处理（限制并发数）
        semaphore = asyncio.Semaphore(5)  # 最多5个并发
        
        async def analyze_one(jd_text: str):
            async with semaphore:
                return await mcp_client.analyze_jd(
                    jd_text=jd_text,
                    model_type=request.model_type
                )
        
        # 并发执行
        tasks = [analyze_one(jd_text) for jd_text in request.jd_texts]
        analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for idx, result in enumerate(analysis_results):
            if isinstance(result, Exception):
                results.append({
                    "index": idx,
                    "status": "failed",
                    "error": str(result)
                })
            else:
                results.append({
                    "index": idx,
                    "status": "success",
                    "jd_id": result["jd"].id,
                    "job_title": result["jd"].job_title,
                    "quality_score": result["evaluation"].quality_score.overall_score
                })
        
        # 统计
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "failed")
        
        return {
            "success": True,
            "data": {
                "results": results,
                "summary": {
                    "total": len(request.jd_texts),
                    "successful": successful,
                    "failed": failed
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match", response_model=Dict[str, Any])
async def batch_match_candidates(request: BatchMatchRequest):
    """
    批量匹配候选人
    
    - **jd_id**: 岗位JD的ID
    - **candidate_profiles**: 候选人档案列表
    """
    # 验证JD是否存在
    jd = await mcp_client.get_jd(request.jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD {request.jd_id} 不存在")
    
    if len(request.candidate_profiles) > 50:
        raise HTTPException(
            status_code=400,
            detail=f"候选人数量超过限制：最多50个，当前{len(request.candidate_profiles)}个"
        )
    
    try:
        from ...core.llm_client import llm_client
        from ...models.schemas import MatchResult
        
        results = []
        
        # 并发处理
        semaphore = asyncio.Semaphore(5)
        
        async def match_one(profile: Dict[str, Any]):
            async with semaphore:
                prompt = f"""
请评估候选人与岗位的匹配度。

岗位信息：
- 职位标题: {jd.job_title}
- 必备技能: {', '.join(jd.required_skills)}
- 任职资格: {', '.join(jd.qualifications)}

候选人信息：
{profile}

返回JSON格式：
```json
{{
    "overall_score": 85.0,
    "dimension_scores": {{"技能匹配": 90.0, "经验匹配": 80.0}},
    "strengths": ["优势1", "优势2"],
    "gaps": ["差距1"],
    "recommendations": ["建议1"]
}}
```
"""
                
                match_data = await llm_client.generate_json(prompt)
                
                match_id = f"match_{uuid.uuid4().hex[:8]}"
                match_result = MatchResult(
                    id=match_id,
                    jd_id=request.jd_id,
                    response_id=f"profile_{uuid.uuid4().hex[:8]}",
                    overall_score=match_data.get("overall_score", 0.0),
                    dimension_scores=match_data.get("dimension_scores", {}),
                    strengths=match_data.get("strengths", []),
                    gaps=match_data.get("gaps", []),
                    recommendations=match_data.get("recommendations", []),
                    created_at=datetime.now()
                )
                
                # 存储匹配结果
                from .match import match_storage
                match_storage[match_id] = match_result
                
                return match_result
        
        # 并发执行
        tasks = [match_one(profile) for profile in request.candidate_profiles]
        match_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for idx, result in enumerate(match_results):
            if isinstance(result, Exception):
                results.append({
                    "index": idx,
                    "status": "failed",
                    "error": str(result)
                })
            else:
                results.append({
                    "index": idx,
                    "status": "success",
                    "match_id": result.id,
                    "overall_score": result.overall_score
                })
        
        # 按匹配度排序
        successful_results = [r for r in results if r["status"] == "success"]
        successful_results.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "results": results,
                "ranked_results": successful_results,
                "summary": {
                    "total": len(request.candidate_profiles),
                    "successful": len(successful_results),
                    "failed": len(results) - len(successful_results)
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
