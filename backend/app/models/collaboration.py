"""
协作会话数据模型
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from ..core.database import Base


class SessionType(str, Enum):
    """会话类型枚举"""
    DISCUSSION = "discussion"
    BRAINSTORM = "brainstorm"
    ANALYSIS = "analysis"
    LEARNING = "learning"
    WORKSHOP = "workshop"


class UserRole(str, Enum):
    """用户角色枚举"""
    HOST = "host"
    MODERATOR = "moderator"
    PARTICIPANT = "participant"
    OBSERVER = "observer"


class CollaborationSession(Base):
    """协作会话模型"""
    
    __tablename__ = "collaboration_sessions"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 会话信息
    title = Column(String(200), nullable=False)
    description = Column(Text)
    session_type = Column(String(50), default=SessionType.DISCUSSION)
    
    # 会话状态
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # 参与者设置
    max_participants = Column(Integer, default=10)
    current_participants = Column(Integer, default=0)
    
    # 会话设置
    settings = Column(JSON, default={})
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    
    # 关系
    creator = relationship("User", back_populates="collaboration_sessions")
    user_sessions = relationship("UserSession", back_populates="session")
    
    def __repr__(self):
        return f"<CollaborationSession(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "title": self.title,
            "description": self.description,
            "session_type": self.session_type,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "is_archived": self.is_archived,
            "max_participants": self.max_participants,
            "current_participants": self.current_participants,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }
    
    def get_duration(self) -> Optional[int]:
        """获取会话持续时间（秒）"""
        if not self.started_at:
            return None
        
        end_time = self.ended_at or datetime.utcnow()
        return int((end_time - self.started_at).total_seconds())
    
    def is_full(self) -> bool:
        """检查会话是否已满"""
        return self.current_participants >= self.max_participants
    
    def can_join(self, user_id: int) -> bool:
        """检查用户是否可以加入会话"""
        if not self.is_active or self.is_archived:
            return False
        
        if self.is_full():
            return False
        
        # 检查用户是否已经在会话中
        for user_session in self.user_sessions:
            if user_session.user_id == user_id and user_session.is_active:
                return False
        
        return True


class UserSession(Base):
    """用户会话模型"""
    
    __tablename__ = "user_sessions"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("collaboration_sessions.id"), nullable=False)
    
    # 会话信息
    role = Column(String(50), default=UserRole.PARTICIPANT)
    is_active = Column(Boolean, default=True)
    
    # 用户状态
    connection_status = Column(String(50), default="connected")  # connected, disconnected, away
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # 用户设置
    settings = Column(JSON, default={})
    
    # 时间戳
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    
    # 关系
    user = relationship("User", back_populates="user_sessions")
    session = relationship("CollaborationSession", back_populates="user_sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, session_id={self.session_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "role": self.role,
            "is_active": self.is_active,
            "connection_status": self.connection_status,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "settings": self.settings,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None
        }
    
    def get_session_duration(self) -> Optional[int]:
        """获取用户在会话中的时间（秒）"""
        if not self.joined_at:
            return None
        
        end_time = self.left_at or datetime.utcnow()
        return int((end_time - self.joined_at).total_seconds())
    
    def update_activity(self):
        """更新用户活动时间"""
        self.last_activity = datetime.utcnow()
    
    def leave_session(self):
        """离开会话"""
        self.is_active = False
        self.left_at = datetime.utcnow()
        self.connection_status = "disconnected" 