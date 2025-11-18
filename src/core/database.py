"""数据库连接和会话管理"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .config import settings
from ..models.database import Base


# 创建异步引擎（优化连接池配置）
# 注意：SQLite不支持连接池参数，仅在使用PostgreSQL/MySQL时启用
if "sqlite" in settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,  # 设置为True可以看到SQL语句
        future=True,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,  # 设置为True可以看到SQL语句
        future=True,
        pool_size=20,  # 连接池大小
        max_overflow=10,  # 最大溢出连接数
        pool_pre_ping=True,  # 连接前ping检查
        pool_recycle=3600,  # 连接回收时间（秒）
    )

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,  # 禁用自动flush提升性能
)


async def init_db():
    """初始化数据库（创建所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """删除所有表（谨慎使用）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@asynccontextmanager
async def get_db():
    """获取数据库会话（上下文管理器）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """获取数据库会话（用于依赖注入）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
