"""
思维分析服务层
"""

import time
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from ..core.config import settings
from ..models.thinking_analysis import ThinkingAnalysis, AnalysisType, ThinkingStyle, AnalysisFeedback
from ..models.user import User
from ..ai_models.model_manager import ModelManager
from ..core.redis_client import cache_manager
from ..services.user_service import user_service


class ThinkingAnalysisService:
    """思维分析服务类"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    async def analyze_thinking_pattern(
        self,
        db: AsyncSession,
        user_id: int,
        input_text: str,
        input_image: Optional[bytes] = None,
        analysis_type: str = "comprehensive",
        save_result: bool = True,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析思维模式
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            input_text: 输入文本
            input_image: 输入图像（可选）
            analysis_type: 分析类型
            save_result: 是否保存结果
            session_id: 会话ID（可选）
        
        Returns:
            分析结果字典
        """
        try:
            start_time = time.time()
            
            # 构建输入数据
            input_data = {"text": input_text}
            if input_image:
                input_data["image"] = input_image
            
            # 执行AI分析
            if not self.model_manager.initialized:
                raise Exception("AI模型管理器未初始化")
            
            analysis_results = await self.model_manager.analyze_thinking_pattern(input_data)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 提取分析结果
            thinking_summary = analysis_results.get("thinking_summary", {})
            individual_analyses = analysis_results.get("individual_analyses", {})
            
            # 转换思维风格枚举
            dominant_style = thinking_summary.get("dominant_thinking_style", "平衡思维")
            style_enum = self._convert_to_style_enum(dominant_style)
            
            # 计算置信度分数
            confidence_score = self._calculate_confidence_score(thinking_summary)
            
            # 准备保存的数据
            analysis_data = {
                "user_id": user_id,
                "session_id": session_id,
                "input_text": input_text,
                "analysis_type": AnalysisType(analysis_type),
                "dominant_thinking_style": style_enum,
                "thinking_scores": thinking_summary.get("thinking_scores", {}),
                "balance_index": thinking_summary.get("balance_index", 0.5),
                "visual_analysis": individual_analyses.get("visual_thinking"),
                "logical_analysis": individual_analyses.get("logical_thinking"),
                "creative_analysis": individual_analyses.get("creative_thinking"),
                "confidence_score": confidence_score,
                "processing_time": processing_time,
                "model_version": "1.0.0",
                "metadata": {
                    "input_length": len(input_text),
                    "has_image": input_image is not None,
                    "analysis_timestamp": settings.get_current_time()
                }
            }
            
            # 保存到数据库
            analysis_record = None
            if save_result:
                analysis_record = await self._save_analysis_result(db, analysis_data)
                
                # 更新用户思维统计
                if analysis_record:
                    await user_service.update_user_thinking_stats(
                        db, user_id, analysis_results
                    )
            
            # 准备返回结果
            result = {
                "success": True,
                "analysis_id": analysis_record.id if analysis_record else None,
                "thinking_summary": thinking_summary,
                "individual_analyses": individual_analyses,
                "processing_time": processing_time,
                "confidence_score": confidence_score,
                "timestamp": settings.get_current_time()
            }
            
            # 缓存结果
            cache_key = f"thinking_analysis:{hash(input_text)}:{user_id}"
            await cache_manager.set(cache_key, result, ttl=3600)
            
            logger.info(f"思维分析完成: user_id={user_id}, type={analysis_type}, time={processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"思维分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": settings.get_current_time()
            }
    
    async def get_analysis_history(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取用户分析历史"""
        try:
            # 构建查询
            query = select(ThinkingAnalysis).where(ThinkingAnalysis.user_id == user_id)
            
            if analysis_type:
                query = query.where(ThinkingAnalysis.analysis_type == AnalysisType(analysis_type))
            
            # 添加排序和分页
            query = query.order_by(ThinkingAnalysis.created_at.desc()).offset(offset).limit(limit)
            
            # 执行查询
            result = await db.execute(query)
            analyses = result.scalars().all()
            
            # 获取总数
            count_query = select(func.count(ThinkingAnalysis.id)).where(ThinkingAnalysis.user_id == user_id)
            if analysis_type:
                count_query = count_query.where(ThinkingAnalysis.analysis_type == AnalysisType(analysis_type))
            
            total_result = await db.execute(count_query)
            total_count = total_result.scalar()
            
            return {
                "success": True,
                "analyses": [analysis.to_summary() for analysis in analyses],
                "total_count": total_count,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + len(analyses) < total_count
                }
            }
            
        except Exception as e:
            logger.error(f"获取分析历史失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "analyses": [],
                "total_count": 0
            }
    
    async def get_analysis_detail(
        self,
        db: AsyncSession,
        analysis_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取分析详情"""
        try:
            result = await db.execute(
                select(ThinkingAnalysis)
                .where(ThinkingAnalysis.id == analysis_id)
                .where(ThinkingAnalysis.user_id == user_id)
            )
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                return None
            
            return {
                "success": True,
                "analysis": analysis.to_dict()
            }
            
        except Exception as e:
            logger.error(f"获取分析详情失败: {e}")
            return None
    
    async def generate_creative_ideas(
        self,
        db: AsyncSession,
        user_id: int,
        prompt: str,
        num_ideas: int = 3,
        creativity_level: float = 0.8,
        save_result: bool = True
    ) -> Dict[str, Any]:
        """生成创意想法"""
        try:
            start_time = time.time()
            
            # 使用创造思维模型生成想法
            if not self.model_manager.initialized:
                raise Exception("AI模型管理器未初始化")
            
            creative_result = await self.model_manager.creative_model.generate_creative_ideas(
                prompt, num_ideas, creativity_level
            )
            
            processing_time = time.time() - start_time
            
            # 保存结果（如果需要）
            if save_result:
                analysis_data = {
                    "user_id": user_id,
                    "input_text": prompt,
                    "analysis_type": AnalysisType.CREATIVE,
                    "dominant_thinking_style": ThinkingStyle.CREATIVE,
                    "creative_analysis": creative_result,
                    "processing_time": processing_time,
                    "model_version": "1.0.0",
                    "metadata": {
                        "prompt_length": len(prompt),
                        "num_ideas": num_ideas,
                        "creativity_level": creativity_level
                    }
                }
                
                await self._save_analysis_result(db, analysis_data)
            
            result = {
                "success": True,
                "prompt": prompt,
                "generated_ideas": creative_result.get("generated_ideas", []),
                "creativity_metrics": {
                    "average_creativity_score": creative_result.get("creativity_level", 0),
                    "idea_diversity": len(creative_result.get("generated_ideas", [])),
                    "processing_time": processing_time
                },
                "timestamp": settings.get_current_time()
            }
            
            # 缓存结果
            cache_key = f"creative_ideas:{hash(prompt)}:{num_ideas}:{user_id}"
            await cache_manager.set(cache_key, result, ttl=1800)
            
            logger.info(f"创意生成完成: user_id={user_id}, ideas={num_ideas}, time={processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"创意生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": settings.get_current_time()
            }
    
    async def submit_feedback(
        self,
        db: AsyncSession,
        analysis_id: int,
        user_id: int,
        rating: int,
        feedback_text: Optional[str] = None,
        is_accurate: Optional[int] = None,
        suggestions: Optional[str] = None
    ) -> bool:
        """提交分析反馈"""
        try:
            # 验证分析记录存在
            analysis_result = await db.execute(
                select(ThinkingAnalysis)
                .where(ThinkingAnalysis.id == analysis_id)
                .where(ThinkingAnalysis.user_id == user_id)
            )
            analysis = analysis_result.scalar_one_or_none()
            
            if not analysis:
                return False
            
            # 创建反馈记录
            feedback = AnalysisFeedback(
                analysis_id=analysis_id,
                user_id=user_id,
                rating=rating,
                feedback_text=feedback_text,
                is_accurate=is_accurate,
                suggestions=suggestions
            )
            
            db.add(feedback)
            await db.commit()
            
            logger.info(f"反馈提交成功: analysis_id={analysis_id}, rating={rating}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"提交反馈失败: {e}")
            return False
    
    async def get_user_thinking_statistics(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """获取用户思维统计"""
        try:
            # 从缓存获取
            cache_key = f"thinking_stats:{user_id}"
            cached_stats = await cache_manager.get(cache_key)
            if cached_stats:
                return cached_stats
            
            # 获取用户基本信息
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "用户不存在"}
            
            # 获取分析统计
            analysis_stats = await db.execute(
                select(
                    func.count(ThinkingAnalysis.id).label("total_analyses"),
                    func.avg(ThinkingAnalysis.confidence_score).label("avg_confidence"),
                    func.avg(ThinkingAnalysis.balance_index).label("avg_balance"),
                    func.avg(ThinkingAnalysis.processing_time).label("avg_processing_time")
                ).where(ThinkingAnalysis.user_id == user_id)
            )
            stats = analysis_stats.first()
            
            # 获取思维风格分布
            style_stats = await db.execute(
                select(
                    ThinkingAnalysis.dominant_thinking_style,
                    func.count(ThinkingAnalysis.id).label("count")
                )
                .where(ThinkingAnalysis.user_id == user_id)
                .group_by(ThinkingAnalysis.dominant_thinking_style)
            )
            style_distribution = {
                style.value if style else "未知": count 
                for style, count in style_stats.fetchall()
            }
            
            # 计算改进趋势（简化版）
            recent_analyses = await db.execute(
                select(ThinkingAnalysis.balance_index)
                .where(ThinkingAnalysis.user_id == user_id)
                .order_by(ThinkingAnalysis.created_at.desc())
                .limit(10)
            )
            recent_scores = [score for score in recent_analyses.scalars() if score is not None]
            
            improvement_trend = "stable"
            if len(recent_scores) >= 5:
                first_half = sum(recent_scores[:len(recent_scores)//2]) / (len(recent_scores)//2)
                second_half = sum(recent_scores[len(recent_scores)//2:]) / (len(recent_scores) - len(recent_scores)//2)
                if second_half > first_half + 0.1:
                    improvement_trend = "improving"
                elif second_half < first_half - 0.1:
                    improvement_trend = "declining"
            
            result = {
                "success": True,
                "user_id": user_id,
                "statistics": {
                    "total_analyses": stats.total_analyses or 0,
                    "avg_confidence": round(float(stats.avg_confidence or 0), 2),
                    "avg_balance_index": round(float(stats.avg_balance or 0), 2),
                    "avg_processing_time": round(float(stats.avg_processing_time or 0), 2),
                    "style_distribution": style_distribution,
                    "improvement_trend": improvement_trend,
                    "user_thinking_stats": user.thinking_stats or {}
                },
                "insights": self._generate_insights(stats, style_distribution, improvement_trend)
            }
            
            # 缓存结果
            await cache_manager.set(cache_key, result, ttl=1800)
            
            return result
            
        except Exception as e:
            logger.error(f"获取思维统计失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _save_analysis_result(
        self,
        db: AsyncSession,
        analysis_data: Dict[str, Any]
    ) -> Optional[ThinkingAnalysis]:
        """保存分析结果到数据库"""
        try:
            analysis = ThinkingAnalysis(**analysis_data)
            db.add(analysis)
            await db.commit()
            await db.refresh(analysis)
            
            logger.info(f"保存分析结果成功: {analysis.id}")
            return analysis
            
        except Exception as e:
            await db.rollback()
            logger.error(f"保存分析结果失败: {e}")
            return None
    
    def _convert_to_style_enum(self, style_str: str) -> ThinkingStyle:
        """转换思维风格字符串为枚举"""
        style_mapping = {
            "形象思维": ThinkingStyle.VISUAL,
            "逻辑思维": ThinkingStyle.LOGICAL,
            "创造思维": ThinkingStyle.CREATIVE,
            "平衡思维": ThinkingStyle.BALANCED
        }
        return style_mapping.get(style_str, ThinkingStyle.BALANCED)
    
    def _calculate_confidence_score(self, thinking_summary: Dict[str, Any]) -> float:
        """计算分析置信度分数"""
        try:
            scores = thinking_summary.get("thinking_scores", {})
            if not scores:
                return 0.5
            
            # 基于分数的一致性和平衡性计算置信度
            values = list(scores.values())
            max_score = max(values)
            score_variance = sum((x - sum(values)/len(values))**2 for x in values) / len(values)
            
            # 主导分数越高，方差越小，置信度越高
            confidence = (max_score + (1 - score_variance)) / 2
            return round(min(max(confidence, 0.0), 1.0), 2)
            
        except Exception:
            return 0.5
    
    def _generate_insights(
        self,
        stats: Any,
        style_distribution: Dict[str, int],
        improvement_trend: str
    ) -> List[str]:
        """生成思维洞察"""
        insights = []
        
        # 分析总数洞察
        total = stats.total_analyses or 0
        if total > 50:
            insights.append("您是一个非常活跃的思维探索者！")
        elif total > 20:
            insights.append("您在思维分析方面已经积累了不错的经验")
        elif total > 0:
            insights.append("继续保持思维分析的习惯，会有更多收获")
        
        # 主导风格洞察
        if style_distribution:
            dominant = max(style_distribution, key=style_distribution.get)
            insights.append(f"您的主导思维风格是{dominant}")
        
        # 平衡性洞察
        avg_balance = stats.avg_balance or 0
        if avg_balance > 0.8:
            insights.append("您拥有非常平衡的思维模式")
        elif avg_balance > 0.6:
            insights.append("您的思维模式相对平衡")
        
        # 改进趋势洞察
        if improvement_trend == "improving":
            insights.append("您的思维能力正在持续提升！")
        elif improvement_trend == "declining":
            insights.append("建议多做一些思维训练来保持状态")
        
        return insights


# 思维分析服务实例需要在应用启动时初始化
def create_thinking_service(model_manager: ModelManager) -> ThinkingAnalysisService:
    """创建思维分析服务实例"""
    return ThinkingAnalysisService(model_manager) 