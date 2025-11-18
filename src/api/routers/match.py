"""匹配评估相关API端点"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
from ...models.schemas import MatchResult
from ...mcp.simple_client import get_simple_mcp_client
import io

# 获取简化 MCP 客户端（不依赖 Redis）
mcp_client = get_simple_mcp_client()

router = APIRouter()

# 临时存储（MVP版本）- 与questionnaire共享
match_storage: Dict[str, MatchResult] = {}


@router.get("/{match_id}", response_model=Dict[str, Any])
async def get_match_result(match_id: str):
    """
    获取匹配结果
    
    - **match_id**: 匹配结果ID
    """
    match_result = match_storage.get(match_id)
    
    if not match_result:
        raise HTTPException(
            status_code=404,
            detail=f"匹配结果 {match_id} 不存在"
        )
    
    return {
        "success": True,
        "data": match_result.model_dump()
    }


@router.get("/{match_id}/report")
async def download_match_report(match_id: str, format: str = "pdf"):
    """
    下载匹配报告
    
    - **match_id**: 匹配结果ID
    - **format**: 报告格式（pdf/html/json，默认pdf）
    """
    match_result = match_storage.get(match_id)
    
    if not match_result:
        raise HTTPException(
            status_code=404,
            detail=f"匹配结果 {match_id} 不存在"
        )
    
    # 获取JD信息
    jd = await mcp_client.get_jd(match_result.jd_id)
    if not jd:
        raise HTTPException(
            status_code=404,
            detail=f"JD {match_result.jd_id} 不存在"
        )
    
    try:
        if format == "json":
            # JSON格式
            import json
            content = json.dumps({
                "match_result": match_result.model_dump(),
                "jd": jd.model_dump()
            }, ensure_ascii=False, indent=2)
            
            return StreamingResponse(
                io.BytesIO(content.encode('utf-8')),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=match_report_{match_id}.json"
                }
            )
        
        elif format == "html":
            # HTML格式
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>匹配评估报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .score {{ font-size: 48px; font-weight: bold; color: #4CAF50; }}
        .dimension {{ margin: 10px 0; }}
        .list-item {{ margin: 5px 0; padding: 5px; background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>匹配评估报告</h1>
    
    <h2>岗位信息</h2>
    <p><strong>职位标题:</strong> {jd.job_title}</p>
    <p><strong>部门:</strong> {jd.department or '未指定'}</p>
    <p><strong>地点:</strong> {jd.location or '未指定'}</p>
    
    <h2>匹配度评分</h2>
    <div class="score">{match_result.overall_score:.1f}分</div>
    
    <h2>各维度得分</h2>
    {''.join([f'<div class="dimension"><strong>{dim}:</strong> {score:.1f}分</div>' 
              for dim, score in match_result.dimension_scores.items()])}
    
    <h2>优势</h2>
    {''.join([f'<div class="list-item">✓ {strength}</div>' 
              for strength in match_result.strengths])}
    
    <h2>差距</h2>
    {''.join([f'<div class="list-item">✗ {gap}</div>' 
              for gap in match_result.gaps])}
    
    <h2>建议</h2>
    {''.join([f'<div class="list-item">→ {rec}</div>' 
              for rec in match_result.recommendations])}
    
    <p style="margin-top: 50px; color: #999; font-size: 12px;">
        生成时间: {match_result.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</body>
</html>
"""
            
            return StreamingResponse(
                io.BytesIO(html_content.encode('utf-8')),
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename=match_report_{match_id}.html"
                }
            )
        
        elif format == "pdf":
            # PDF格式（简化版，实际应使用reportlab等库）
            # 这里返回HTML，实际生产环境应该转换为PDF
            raise HTTPException(
                status_code=501,
                detail="PDF格式暂未实现，请使用html或json格式"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的格式: {format}，支持的格式: pdf, html, json"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jd/{jd_id}/matches", response_model=Dict[str, Any])
async def list_jd_matches(jd_id: str):
    """
    列出指定JD的所有匹配结果
    
    - **jd_id**: 岗位JD的ID
    """
    # 验证JD是否存在
    jd = await mcp_client.get_jd(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD {jd_id} 不存在")
    
    # 筛选该JD的所有匹配结果
    matches = [
        match for match in match_storage.values()
        if match.jd_id == jd_id
    ]
    
    # 按匹配度排序（从高到低）
    matches.sort(key=lambda x: x.overall_score, reverse=True)
    
    return {
        "success": True,
        "data": [m.model_dump() for m in matches],
        "total": len(matches)
    }


@router.get("", response_model=Dict[str, Any])
async def list_all_matches():
    """
    列出所有匹配结果
    """
    matches = list(match_storage.values())
    
    # 按创建时间排序（最新的在前）
    matches.sort(key=lambda x: x.created_at, reverse=True)
    
    return {
        "success": True,
        "data": [m.model_dump() for m in matches],
        "total": len(matches)
    }
