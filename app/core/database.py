from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.base_model import Base
from app.core.config import settings

# 创建数据库引擎和会话工厂
engine = create_async_engine(settings.database_url, **settings.engine_options)

SessionFactory = async_sessionmaker(
    engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)


# 数据库依赖注入
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


# 用于临时使用的创建数据库表的函数
# 请在生产环境中使用 Alembic 进行数据库迁移
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
