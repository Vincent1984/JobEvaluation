"""配置管理"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # DeepSeek-R1 LLM配置
    OPENAI_API_KEY: str = "sk-748d2d1b25074781b311c75b0c8c10ad"
    OPENAI_BASE_URL: str = "https://api.deepseek.com/v1"
    LLM_MODEL: str = "deepseek-chat"  # DeepSeek-R1推理模型
    
    # LLM高级配置
    LLM_MAX_RETRIES: int = 3  # 最大重试次数
    LLM_TIMEOUT: float = 60.0  # 请求超时时间（秒）
    LLM_ENABLE_CACHE: bool = True  # 是否启用缓存
    LLM_MAX_CONCURRENT: int = 5  # 批量调用最大并发数
    LLM_DEFAULT_TEMPERATURE: float = 0.7  # 默认温度参数
    LLM_DEFAULT_MAX_TOKENS: int = 4000  # 默认最大token数
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/jd_analyzer.db"
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Streamlit配置
    STREAMLIT_PORT: int = 8501
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
