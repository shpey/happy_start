#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

from app.core.config import settings
from app.core.database import Base, get_db_url
from app.core.security import security_manager
from app.models.user import User
from app.models.thinking_analysis import ThinkingAnalysis
from app.models.collaboration import CollaborationSession, UserSession


def create_database():
    """创建数据库表"""
    try:
        # 创建数据库引擎
        engine = create_engine(get_db_url(), echo=True)
        
        # 删除所有表（仅在开发环境）
        if settings.ENVIRONMENT == "development":
            logger.warning("开发环境：删除所有现有表")
            Base.metadata.drop_all(bind=engine)
        
        # 创建所有表
        logger.info("创建数据库表...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ 数据库表创建成功")
        return engine
        
    except Exception as e:
        logger.error(f"❌ 数据库表创建失败: {e}")
        raise


def create_seed_data(engine):
    """创建种子数据"""
    try:
        # 创建会话
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=security_manager.hash_password("Admin123!"),
            full_name="系统管理员",
            bio="智能思维分析平台管理员",
            is_active=True,
            is_verified=True,
            is_premium=True,
            thinking_stats={
                "total_analyses": 0,
                "dominant_style": None,
                "average_scores": {},
                "improvement_trend": "stable"
            }
        )
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=security_manager.hash_password("Test123!"),
            full_name="测试用户",
            bio="这是一个测试用户账户",
            is_active=True,
            is_verified=True,
            is_premium=False,
            thinking_stats={
                "total_analyses": 5,
                "dominant_style": "逻辑思维",
                "average_scores": {
                    "逻辑思维": 0.85,
                    "创造思维": 0.72,
                    "形象思维": 0.68
                },
                "improvement_trend": "improving"
            }
        )
        
        # 创建演示用户
        demo_user = User(
            username="demouser",
            email="demo@example.com",
            hashed_password=security_manager.hash_password("Demo123!"),
            full_name="演示用户",
            bio="用于演示的用户账户",
            is_active=True,
            is_verified=False,
            is_premium=False,
            thinking_stats={
                "total_analyses": 12,
                "dominant_style": "创造思维",
                "average_scores": {
                    "创造思维": 0.88,
                    "形象思维": 0.75,
                    "逻辑思维": 0.69
                },
                "improvement_trend": "stable"
            }
        )
        
        # 添加用户到数据库
        session.add(admin_user)
        session.add(test_user)
        session.add(demo_user)
        session.commit()
        
        logger.info("✅ 种子数据创建成功")
        logger.info("管理员账户: admin / Admin123!")
        logger.info("测试账户: testuser / Test123!")
        logger.info("演示账户: demouser / Demo123!")
        
        session.close()
        
    except Exception as e:
        logger.error(f"❌ 种子数据创建失败: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        raise


def create_demo_thinking_analyses(engine):
    """创建演示思维分析数据"""
    try:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 获取测试用户
        test_user = session.query(User).filter(User.username == "testuser").first()
        demo_user = session.query(User).filter(User.username == "demouser").first()
        
        if not test_user or not demo_user:
            logger.warning("找不到测试用户，跳过演示数据创建")
            return
        
        # 创建演示思维分析记录
        demo_analyses = [
            ThinkingAnalysis(
                user_id=test_user.id,
                input_text="人工智能的发展会对人类社会产生什么影响？",
                analysis_type="comprehensive",
                results={
                    "visual_thinking": {
                        "score": 0.72,
                        "concepts": ["技术革命", "社会变革", "人机协作"],
                        "associations": ["工业革命", "信息时代", "未来社会"]
                    },
                    "logical_thinking": {
                        "score": 0.85,
                        "reasoning_steps": [
                            "分析AI技术现状",
                            "评估影响领域",
                            "预测发展趋势",
                            "制定应对策略"
                        ],
                        "conclusions": ["需要政策引导", "教育体系改革", "道德伦理考量"]
                    },
                    "creative_thinking": {
                        "score": 0.68,
                        "innovations": ["人机融合工作模式", "AI辅助创作", "智能社会治理"],
                        "possibilities": ["新兴职业", "生活方式转变", "认知能力增强"]
                    }
                },
                thinking_summary={
                    "dominant_thinking_style": "逻辑思维",
                    "thinking_scores": {
                        "逻辑思维": 0.85,
                        "形象思维": 0.72,
                        "创造思维": 0.68
                    },
                    "balance_index": 0.75,
                    "insights": [
                        "您在逻辑分析方面表现突出",
                        "建议加强创造性思维训练",
                        "可以尝试更多跨领域思考"
                    ]
                }
            ),
            ThinkingAnalysis(
                user_id=demo_user.id,
                input_text="如何设计一个理想的城市？",
                analysis_type="comprehensive",
                results={
                    "visual_thinking": {
                        "score": 0.88,
                        "concepts": ["绿色空间", "智能交通", "和谐社区"],
                        "associations": ["生态城市", "智慧城市", "宜居环境"]
                    },
                    "logical_thinking": {
                        "score": 0.71,
                        "reasoning_steps": [
                            "确定城市功能定位",
                            "规划空间布局",
                            "设计交通系统",
                            "配置公共服务"
                        ],
                        "conclusions": ["可持续发展", "以人为本", "技术与自然平衡"]
                    },
                    "creative_thinking": {
                        "score": 0.92,
                        "innovations": ["垂直花园", "地下空间利用", "社区共享中心"],
                        "possibilities": ["漂浮城市", "地下城市", "天空城市"]
                    }
                },
                thinking_summary={
                    "dominant_thinking_style": "创造思维",
                    "thinking_scores": {
                        "创造思维": 0.92,
                        "形象思维": 0.88,
                        "逻辑思维": 0.71
                    },
                    "balance_index": 0.84,
                    "insights": [
                        "您具有出色的创造力和想象力",
                        "建议加强逻辑推理能力",
                        "可以将创意与实际结合"
                    ]
                }
            )
        ]
        
        for analysis in demo_analyses:
            session.add(analysis)
        
        session.commit()
        session.close()
        
        logger.info("✅ 演示思维分析数据创建成功")
        
    except Exception as e:
        logger.error(f"❌ 演示数据创建失败: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        raise


def create_demo_collaboration_sessions(engine):
    """创建演示协作会话数据"""
    try:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 获取用户
        admin_user = session.query(User).filter(User.username == "admin").first()
        test_user = session.query(User).filter(User.username == "testuser").first()
        demo_user = session.query(User).filter(User.username == "demouser").first()
        
        if not all([admin_user, test_user, demo_user]):
            logger.warning("找不到所有用户，跳过协作会话创建")
            return
        
        # 创建演示协作会话
        demo_session = CollaborationSession(
            creator_id=admin_user.id,
            title="AI与未来社会讨论会",
            description="探讨人工智能技术对未来社会的影响和机遇",
            session_type="discussion",
            is_active=True,
            max_participants=10,
            settings={
                "allow_anonymous": False,
                "enable_voice": True,
                "enable_video": False,
                "recording_enabled": False
            }
        )
        
        session.add(demo_session)
        session.commit()
        
        # 创建用户会话
        user_sessions = [
            UserSession(
                user_id=admin_user.id,
                session_id=demo_session.id,
                role="host",
                is_active=True
            ),
            UserSession(
                user_id=test_user.id,
                session_id=demo_session.id,
                role="participant",
                is_active=True
            ),
            UserSession(
                user_id=demo_user.id,
                session_id=demo_session.id,
                role="participant",
                is_active=False
            )
        ]
        
        for user_session in user_sessions:
            session.add(user_session)
        
        session.commit()
        session.close()
        
        logger.info("✅ 演示协作会话数据创建成功")
        
    except Exception as e:
        logger.error(f"❌ 协作会话数据创建失败: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        raise


def main():
    """主函数"""
    logger.info("🚀 开始初始化数据库...")
    
    try:
        # 创建数据库表
        engine = create_database()
        
        # 创建种子数据
        create_seed_data(engine)
        
        # 创建演示数据
        create_demo_thinking_analyses(engine)
        create_demo_collaboration_sessions(engine)
        
        logger.info("🎉 数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"💥 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 