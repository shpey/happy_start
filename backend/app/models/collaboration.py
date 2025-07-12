"""
协作相关数据模型
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class RoomStatus(enum.Enum):
    """房间状态枚举"""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class UserRole(enum.Enum):
    """用户角色枚举"""
    CREATOR = "creator"
    MODERATOR = "moderator"
    PARTICIPANT = "participant"
    OBSERVER = "observer"


class CollaborationSession(Base):
    """协作会话模型"""
    
    __tablename__ = "collaboration_sessions"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 会话配置
    max_users = Column(Integer, default=10)
    is_public = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    allow_anonymous = Column(Boolean, default=False)
    
    # 状态信息
    status = Column(Enum(RoomStatus), default=RoomStatus.ACTIVE)
    current_users_count = Column(Integer, default=0)
    
    # 创建者信息
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 会话设置
    settings = Column(JSON, default={
        "enable_voice": True,
        "enable_video": False,
        "enable_screen_share": True,
        "enable_3d_space": True,
        "thinking_mode": "collaborative",
        "auto_save": True
    })
    
    # 3D空间配置
    space_config = Column(JSON, default={
        "environment": "default",
        "lighting": "natural",
        "background_music": None,
        "spatial_audio": True,
        "max_objects": 100
    })
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    
    # 关系
    creator = relationship("User", back_populates="collaboration_sessions")
    user_sessions = relationship("UserSession", back_populates="collaboration_session")
    session_events = relationship("SessionEvent", back_populates="session")
    shared_objects = relationship("SharedObject", back_populates="session")
    
    def __repr__(self):
        return f"<CollaborationSession(id={self.id}, room_id='{self.room_id}', name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "name": self.name,
            "description": self.description,
            "max_users": self.max_users,
            "is_public": self.is_public,
            "requires_approval": self.requires_approval,
            "allow_anonymous": self.allow_anonymous,
            "status": self.status.value if self.status else None,
            "current_users_count": self.current_users_count,
            "creator_id": self.creator_id,
            "settings": self.settings,
            "space_config": self.space_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }
    
    def to_summary(self):
        """返回会话摘要"""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "name": self.name,
            "description": self.description,
            "current_users_count": self.current_users_count,
            "max_users": self.max_users,
            "status": self.status.value if self.status else None,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserSession(Base):
    """用户会话模型"""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    collaboration_session_id = Column(Integer, ForeignKey("collaboration_sessions.id"), nullable=False)
    
    # 会话信息
    session_token = Column(String(255), unique=True, index=True)
    socket_id = Column(String(100), index=True)  # WebSocket连接ID
    
    # 用户状态
    role = Column(Enum(UserRole), default=UserRole.PARTICIPANT)
    is_online = Column(Boolean, default=True)
    is_speaking = Column(Boolean, default=False)
    is_sharing_screen = Column(Boolean, default=False)
    
    # 位置信息（3D空间中的位置）
    position = Column(JSON, default={"x": 0, "y": 0, "z": 0})
    rotation = Column(JSON, default={"x": 0, "y": 0, "z": 0})
    
    # 用户偏好
    audio_enabled = Column(Boolean, default=True)
    video_enabled = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    
    # 时间戳
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    
    # 关系
    user = relationship("User", back_populates="user_sessions")
    collaboration_session = relationship("CollaborationSession", back_populates="user_sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, session_id={self.collaboration_session_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "collaboration_session_id": self.collaboration_session_id,
            "session_token": self.session_token,
            "socket_id": self.socket_id,
            "role": self.role.value if self.role else None,
            "is_online": self.is_online,
            "is_speaking": self.is_speaking,
            "is_sharing_screen": self.is_sharing_screen,
            "position": self.position,
            "rotation": self.rotation,
            "audio_enabled": self.audio_enabled,
            "video_enabled": self.video_enabled,
            "notifications_enabled": self.notifications_enabled,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None
        }


class SessionEvent(Base):
    """会话事件模型"""
    
    __tablename__ = "session_events"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("collaboration_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))  # 可能是系统事件，所以可为空
    
    # 事件信息
    event_type = Column(String(50), nullable=False)  # join, leave, message, object_create, etc.
    event_data = Column(JSON)  # 事件具体数据
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    session = relationship("CollaborationSession", back_populates="session_events")
    user = relationship("User")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SharedObject(Base):
    """共享对象模型"""
    
    __tablename__ = "shared_objects"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("collaboration_sessions.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 对象信息
    object_type = Column(String(50), nullable=False)  # text, image, 3d_model, thinking_map, etc.
    object_name = Column(String(200))
    object_data = Column(JSON)  # 对象具体数据
    
    # 3D空间位置
    position = Column(JSON, default={"x": 0, "y": 0, "z": 0})
    rotation = Column(JSON, default={"x": 0, "y": 0, "z": 0})
    scale = Column(JSON, default={"x": 1, "y": 1, "z": 1})
    
    # 对象状态
    is_visible = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    # 权限设置
    permissions = Column(JSON, default={
        "view": "all",  # all, creator, moderators
        "edit": "creator",  # all, creator, moderators
        "delete": "creator"
    })
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    session = relationship("CollaborationSession", back_populates="shared_objects")
    creator = relationship("User")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "creator_id": self.creator_id,
            "object_type": self.object_type,
            "object_name": self.object_name,
            "object_data": self.object_data,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "is_visible": self.is_visible,
            "is_locked": self.is_locked,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 