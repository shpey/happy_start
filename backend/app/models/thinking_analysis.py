"""
思维分析数据模型
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ThinkingAnalysis(Base):
    """思维分析模型"""
    
    __tablename__ = "thinking_analyses"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 分析内容
    input_text = Column(Text, nullable=False)
    analysis_type = Column(String(50), default="comprehensive")  # comprehensive, visual, logical, creative
    
    # 分析结果
    results = Column(JSON, nullable=False)
    thinking_summary = Column(JSON, nullable=False)
    
    # 元数据
    processing_time = Column(Integer, default=0)  # 处理时间（毫秒）
    confidence_score = Column(Integer, default=0)  # 置信度分数（0-100）
    
    # 状态信息
    is_public = Column(Boolean, default=False)
    is_favorited = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="thinking_analyses")
    
    def __repr__(self):
        return f"<ThinkingAnalysis(id={self.id}, user_id={self.user_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "input_text": self.input_text,
            "analysis_type": self.analysis_type,
            "results": self.results,
            "thinking_summary": self.thinking_summary,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "is_public": self.is_public,
            "is_favorited": self.is_favorited,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_dominant_thinking_style(self) -> Optional[str]:
        """获取主导思维风格"""
        if not self.thinking_summary or "thinking_scores" not in self.thinking_summary:
            return None
        
        scores = self.thinking_summary["thinking_scores"]
        if not scores:
            return None
        
        return max(scores, key=scores.get)
    
    def get_balance_index(self) -> float:
        """获取思维平衡指数"""
        if not self.thinking_summary or "balance_index" not in self.thinking_summary:
            return 0.0
        
        return self.thinking_summary["balance_index"]
    
    def get_insights(self) -> list:
        """获取洞察建议"""
        if not self.thinking_summary or "insights" not in self.thinking_summary:
            return []
        
        return self.thinking_summary["insights"] 