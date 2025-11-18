"""FastAPI应用主入口"""

import uvicorn
from . import app
from ..core.config import settings


def start_api_server():
    """启动FastAPI服务器"""
    uvicorn.run(
        "src.api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    start_api_server()
