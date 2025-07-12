"""
数据库连接配置
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_url():
    """获取数据库连接URL"""
    return settings.DATABASE_URL


async def init_db():
    """初始化数据库连接"""
    # 这里可以添加数据库连接初始化逻辑
    pass


def create_tables():
    """创建数据库表"""
    # 导入所有模型以确保它们被注册
    from ..models.user import User
    from ..models.thinking_analysis import ThinkingAnalysis
    from ..models.collaboration import CollaborationSession, UserSession
    
    # 创建所有表
    Base.metadata.create_all(bind=engine) 