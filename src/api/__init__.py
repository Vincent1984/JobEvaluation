"""FastAPI应用初始化"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import jd, categories, companies, questionnaire, match, templates, batch, tags

app = FastAPI(
    title="岗位JD分析器API",
    description="基于AI的岗位JD分析、评估和匹配系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(jd.router, prefix="/api/v1/jd", tags=["JD分析"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["职位分类"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["企业管理"])
app.include_router(questionnaire.router, prefix="/api/v1/questionnaire", tags=["问卷管理"])
app.include_router(match.router, prefix="/api/v1/match", tags=["匹配评估"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["模板管理"])
app.include_router(batch.router, prefix="/api/v1/batch", tags=["批量处理"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["标签管理"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "岗位JD分析器API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
