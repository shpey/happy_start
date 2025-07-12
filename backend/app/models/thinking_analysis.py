"""
思维分析记录数据模型
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class AnalysisType(enum.Enum):
    """分析类型枚举"""
    COMPREHENSIVE = "comprehensive"
    VISUAL = "visual"
    LOGICAL = "logical"  
    CREATIVE = "creative"


class ThinkingStyle(enum.Enum):
    """思维风格枚举"""
    VISUAL = "形象思维"
    LOGICAL = "逻辑思维"
    CREATIVE = "创造思维"
    BALANCED = "平衡思维"


class ThinkingAnalysis(Base):
    """思维分析记录模型"""
    
    __tablename__ = "thinking_analyses"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), index=True)  # 可选的会话ID
    
    # 分析内容
    input_text = Column(Text, nullable=False)
    input_image_url = Column(String(500))  # 可选的图像输入
    analysis_type = Column(Enum(AnalysisType), default=AnalysisType.COMPREHENSIVE)
    
    # 分析结果
    dominant_thinking_style = Column(Enum(ThinkingStyle))
    thinking_scores = Column(JSON)  # 各种思维类型的分数
    balance_index = Column(Float)  # 思维平衡指数
    
    # 详细分析结果
    visual_analysis = Column(JSON)  # 形象思维分析结果
    logical_analysis = Column(JSON)  # 逻辑思维分析结果
    creative_analysis = Column(JSON)  # 创造思维分析结果
    
    # 分析质量指标
    confidence_score = Column(Float)  # 分析置信度
    processing_time = Column(Float)  # 处理时间（秒）
    model_version = Column(String(50))  # 使用的模型版本
    
    # 元数据
    metadata = Column(JSON, default={})  # 额外的分析元数据
    tags = Column(JSON, default=[])  # 标签
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="thinking_analyses")
    feedback_records = relationship("AnalysisFeedback", back_populates="analysis")
    
    def __repr__(self):
        return f"<ThinkingAnalysis(id={self.id}, user_id={self.user_id}, style='{self.dominant_thinking_style}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "input_text": self.input_text,
            "input_image_url": self.input_image_url,
            "analysis_type": self.analysis_type.value if self.analysis_type else None,
            "dominant_thinking_style": self.dominant_thinking_style.value if self.dominant_thinking_style else None,
            "thinking_scores": self.thinking_scores,
            "balance_index": self.balance_index,
            "visual_analysis": self.visual_analysis,
            "logical_analysis": self.logical_analysis,
            "creative_analysis": self.creative_analysis,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time,
            "model_version": self.model_version,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_summary(self):
        """返回分析摘要"""
        return {
            "id": self.id,
            "analysis_type": self.analysis_type.value if self.analysis_type else None,
            "dominant_thinking_style": self.dominant_thinking_style.value if self.dominant_thinking_style else None,
            "balance_index": self.balance_index,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tags": self.tags
        }


class AnalysisFeedback(Base):
    """分析反馈模型"""
    
    __tablename__ = "analysis_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("thinking_analyses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 反馈内容
    rating = Column(Integer)  # 1-5分评分
    feedback_text = Column(Text)
    is_accurate = Column(Integer)  # 准确性：1准确，0不准确，-1不确定
    suggestions = Column(Text)  # 改进建议
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    analysis = relationship("ThinkingAnalysis", back_populates="feedback_records")
    user = relationship("User")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "feedback_text": self.feedback_text,
            "is_accurate": self.is_accurate,
            "suggestions": self.suggestions,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 