"""
用户数据模型
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 个人信息
    full_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    
    # 用户偏好设置
    preferences = Column(JSON, default={})
    
    # 思维统计信息
    thinking_stats = Column(JSON, default={
        "total_analyses": 0,
        "dominant_style": None,
        "average_scores": {},
        "improvement_trend": "stable"
    })
    
    # 关系
    thinking_analyses = relationship("ThinkingAnalysis", back_populates="user")
    collaboration_sessions = relationship("CollaborationSession", back_populates="creator")
    user_sessions = relationship("UserSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "preferences": self.preferences,
            "thinking_stats": self.thinking_stats
        }
    
    def update_thinking_stats(self, analysis_result: dict):
        """更新思维统计信息"""
        if not self.thinking_stats:
            self.thinking_stats = {
                "total_analyses": 0,
                "dominant_style": None,
                "average_scores": {},
                "improvement_trend": "stable"
            }
        
        # 增加分析次数
        self.thinking_stats["total_analyses"] += 1
        
        # 更新主导风格
        if "thinking_summary" in analysis_result:
            summary = analysis_result["thinking_summary"]
            self.thinking_stats["dominant_style"] = summary.get("dominant_thinking_style")
            
            # 更新平均分数
            if "thinking_scores" in summary:
                current_scores = self.thinking_stats.get("average_scores", {})
                new_scores = summary["thinking_scores"]
                
                for style, score in new_scores.items():
                    if style in current_scores:
                        # 计算移动平均
                        current_scores[style] = (current_scores[style] + score) / 2
                    else:
                        current_scores[style] = score
                
                self.thinking_stats["average_scores"] = current_scores 