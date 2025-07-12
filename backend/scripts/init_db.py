#!/usr/bin/env python3
"""
数据库初始化脚本
创建表结构并插入初始数据
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from loguru import logger

from app.core.config import settings
from app.core.database import Base
from app.models import *  # 导入所有模型
from app.services.user_service import user_service


async def create_tables():
    """创建数据库表"""
    try:
        logger.info("开始创建数据库表...")
        
        # 创建异步引擎
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True,
            future=True
        )
        
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ 数据库表创建成功")
        return engine
        
    except Exception as e:
        logger.error(f"❌ 创建数据库表失败: {e}")
        raise


async def create_initial_data(engine):
    """创建初始数据"""
    try:
        logger.info("开始创建初始数据...")
        
        # 创建异步会话
        AsyncSessionLocal = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            # 创建管理员用户
            admin_user = await user_service.create_user(
                db=session,
                username="admin",
                email="admin@intelligentthinking.com",
                password="admin123",
                full_name="系统管理员"
            )
            
            if admin_user:
                # 设置为高级用户
                admin_user.is_premium = True
                admin_user.is_verified = True
                await session.commit()
                logger.info(f"✅ 创建管理员用户成功: {admin_user.username}")
            
            # 创建示例用户
            demo_users = [
                {
                    "username": "demo_user",
                    "email": "demo@example.com",
                    "password": "demo123",
                    "full_name": "演示用户"
                },
                {
                    "username": "test_visual",
                    "email": "visual@example.com", 
                    "password": "test123",
                    "full_name": "视觉思维测试用户"
                },
                {
                    "username": "test_logical",
                    "email": "logical@example.com",
                    "password": "test123", 
                    "full_name": "逻辑思维测试用户"
                },
                {
                    "username": "test_creative",
                    "email": "creative@example.com",
                    "password": "test123",
                    "full_name": "创造思维测试用户"
                }
            ]
            
            for user_data in demo_users:
                try:
                    demo_user = await user_service.create_user(
                        db=session,
                        **user_data
                    )
                    if demo_user:
                        logger.info(f"✅ 创建演示用户成功: {demo_user.username}")
                except Exception as e:
                    logger.warning(f"⚠️ 创建用户失败 {user_data['username']}: {e}")
            
            # 创建示例协作会话
            from app.models.collaboration import CollaborationSession, RoomStatus
            
            demo_sessions = [
                {
                    "room_id": "demo_room_001",
                    "name": "思维探索演示房间",
                    "description": "这是一个用于演示三层思维模型的协作空间",
                    "creator_id": admin_user.id if admin_user else 1,
                    "is_public": True,
                    "max_users": 10,
                    "status": RoomStatus.ACTIVE
                },
                {
                    "room_id": "creative_lab_001", 
                    "name": "创意实验室",
                    "description": "专注于创造思维训练的协作空间",
                    "creator_id": admin_user.id if admin_user else 1,
                    "is_public": True,
                    "max_users": 8,
                    "status": RoomStatus.ACTIVE
                },
                {
                    "room_id": "logic_gym_001",
                    "name": "逻辑健身房", 
                    "description": "逻辑思维训练和推理练习空间",
                    "creator_id": admin_user.id if admin_user else 1,
                    "is_public": True,
                    "max_users": 6,
                    "status": RoomStatus.ACTIVE
                }
            ]
            
            for session_data in demo_sessions:
                try:
                    demo_session = CollaborationSession(**session_data)
                    session.add(demo_session)
                    await session.commit()
                    await session.refresh(demo_session)
                    logger.info(f"✅ 创建协作会话成功: {demo_session.name}")
                except Exception as e:
                    logger.warning(f"⚠️ 创建协作会话失败: {e}")
                    await session.rollback()
            
        logger.info("✅ 初始数据创建完成")
        
    except Exception as e:
        logger.error(f"❌ 创建初始数据失败: {e}")
        raise


async def verify_database():
    """验证数据库连接和表结构"""
    try:
        logger.info("开始验证数据库...")
        
        engine = create_async_engine(settings.DATABASE_URL)
        
        async with engine.begin() as conn:
            # 检查表是否存在
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            result = await conn.execute(tables_query)
            tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"✅ 数据库验证成功，共找到 {len(tables)} 个表:")
            for table in tables:
                logger.info(f"  - {table}")
            
            # 检查用户数量
            user_count_query = text("SELECT COUNT(*) FROM users;")
            result = await conn.execute(user_count_query)
            user_count = result.scalar()
            logger.info(f"✅ 用户表中有 {user_count} 个用户")
            
            # 检查协作会话数量
            session_count_query = text("SELECT COUNT(*) FROM collaboration_sessions;")
            result = await conn.execute(session_count_query)
            session_count = result.scalar()
            logger.info(f"✅ 协作会话表中有 {session_count} 个会话")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库验证失败: {e}")
        return False


async def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    try:
        logger.warning("⚠️ 开始重置数据库（将删除所有数据）...")
        
        engine = create_async_engine(settings.DATABASE_URL)
        
        async with engine.begin() as conn:
            # 删除所有表
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("✅ 已删除所有表")
            
            # 重新创建表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 已重新创建所有表")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ 重置数据库失败: {e}")
        return False


async def main():
    """主函数"""
    logger.info("🚀 智能思维数据库初始化工具")
    logger.info(f"数据库URL: {settings.DATABASE_URL}")
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "reset":
                logger.warning("执行数据库重置...")
                if await reset_database():
                    logger.info("✅ 数据库重置完成")
                return
            elif command == "verify":
                logger.info("执行数据库验证...")
                if await verify_database():
                    logger.info("✅ 数据库验证完成")
                return
            elif command == "help":
                print("""
使用方法:
  python init_db.py          # 创建表和初始数据
  python init_db.py reset    # 重置数据库
  python init_db.py verify   # 验证数据库
  python init_db.py help     # 显示帮助
                """)
                return
        
        # 默认操作：创建表和初始数据
        engine = await create_tables()
        await create_initial_data(engine)
        await engine.dispose()
        
        # 验证结果
        if await verify_database():
            logger.info("🎉 数据库初始化完成！")
            logger.info("现在可以启动应用程序了：")
            logger.info("  后端: cd backend && python main.py")
            logger.info("  前端: cd frontend && npm start")
        else:
            logger.error("❌ 数据库初始化验证失败")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("🛑 用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 初始化过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    # 运行主函数
    asyncio.run(main()) 