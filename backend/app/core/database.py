"""
PostgreSQL 数据库连接管理
"""

import asyncio
from typing import AsyncGenerator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from .config import settings

# 异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

# 同步数据库引擎（用于Alembic迁移）
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300
)

# 会话工厂
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# ORM基类
Base = declarative_base()

# 元数据
metadata = MetaData()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库事务回滚: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库连接
    """
    try:
        # 测试数据库连接
        async with async_engine.begin() as conn:
            # 创建所有表（开发环境）
            if settings.is_development():
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ 数据库表创建成功")
        
        logger.info(f"✅ 数据库连接成功: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
        
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise


async def close_db() -> None:
    """
    关闭数据库连接
    """
    try:
        await async_engine.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭数据库连接失败: {e}")


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = async_engine
        self.session_factory = AsyncSessionLocal
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            async with self.session_factory() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    async def get_connection_info(self) -> dict:
        """获取数据库连接信息"""
        try:
            async with self.session_factory() as session:
                result = await session.execute("""
                    SELECT 
                        version() as version,
                        current_database() as database,
                        current_user as user,
                        inet_server_addr() as host,
                        inet_server_port() as port
                """)
                row = result.fetchone()
                return {
                    "version": row.version,
                    "database": row.database,
                    "user": row.user,
                    "host": row.host,
                    "port": row.port,
                    "status": "connected"
                }
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def execute_raw_sql(self, sql: str, params: dict = None) -> list:
        """执行原生SQL"""
        try:
            async with self.session_factory() as session:
                if params:
                    result = await session.execute(sql, params)
                else:
                    result = await session.execute(sql)
                return result.fetchall()
        except Exception as e:
            logger.error(f"执行SQL失败: {e}")
            raise


# 全局数据库管理器实例
db_manager = DatabaseManager() 