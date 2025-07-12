"""
数据模型包初始化
"""

from .user import User
from .thinking_analysis import (
    ThinkingAnalysis, 
    AnalysisFeedback, 
    AnalysisType, 
    ThinkingStyle
)
from .collaboration import (
    CollaborationSession,
    UserSession, 
    SessionEvent,
    SharedObject,
    RoomStatus,
    UserRole
)

# 确保所有模型都被SQLAlchemy识别
__all__ = [
    "User",
    "ThinkingAnalysis",
    "AnalysisFeedback", 
    "AnalysisType",
    "ThinkingStyle",
    "CollaborationSession",
    "UserSession",
    "SessionEvent", 
    "SharedObject",
    "RoomStatus",
    "UserRole"
] 