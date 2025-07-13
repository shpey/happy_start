"""
数据分析服务
提供全面的用户行为分析、思维模式洞察和系统使用统计
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
import pandas as pd
import numpy as np
from collections import defaultdict
import logging

from ..models.thinking_analysis import ThinkingAnalysis
from ..models.user import User
from ..models.collaboration import CollaborationSession, CollaborationEvent
from ..core.database import get_db

logger = logging.getLogger(__name__)


class AnalyticsService:
    """数据分析服务"""
    
    def __init__(self, db: Session):
        self.db = db
        
    # ==================== 用户行为分析 ====================
    
    async def get_user_behavior_analytics(
        self, 
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取用户行为分析
        
        Args:
            user_id: 用户ID，None表示全局统计
            days: 分析天数
            
        Returns:
            用户行为分析数据
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 基础查询条件
            base_query = self.db.query(ThinkingAnalysis).filter(
                ThinkingAnalysis.created_at >= start_date
            )
            
            if user_id:
                base_query = base_query.filter(ThinkingAnalysis.user_id == user_id)
            
            analyses = base_query.all()
            
            # 计算活跃度指标
            activity_metrics = self._calculate_activity_metrics(analyses, days)
            
            # 使用模式分析
            usage_patterns = self._analyze_usage_patterns(analyses)
            
            # 时间分布分析
            time_distribution = self._analyze_time_distribution(analyses)
            
            # 功能使用统计
            feature_usage = self._analyze_feature_usage(analyses)
            
            # 趋势分析
            trends = self._calculate_trends(analyses, days)
            
            return {
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "activity_metrics": activity_metrics,
                "usage_patterns": usage_patterns,
                "time_distribution": time_distribution,
                "feature_usage": feature_usage,
                "trends": trends,
                "total_users": len(set(a.user_id for a in analyses)) if not user_id else 1,
                "total_analyses": len(analyses)
            }
            
        except Exception as e:
            logger.error(f"用户行为分析失败: {e}")
            raise
    
    def _calculate_activity_metrics(self, analyses: List[ThinkingAnalysis], days: int) -> Dict[str, Any]:
        """计算活跃度指标"""
        if not analyses:
            return {
                "daily_average": 0,
                "weekly_average": 0,
                "peak_hour": None,
                "active_days": 0,
                "retention_rate": 0
            }
        
        # 按日期分组
        daily_counts = defaultdict(int)
        hourly_counts = defaultdict(int)
        user_activity = defaultdict(set)
        
        for analysis in analyses:
            date_key = analysis.created_at.date()
            hour_key = analysis.created_at.hour
            user_id = analysis.user_id
            
            daily_counts[date_key] += 1
            hourly_counts[hour_key] += 1
            user_activity[user_id].add(date_key)
        
        # 计算指标
        daily_average = sum(daily_counts.values()) / max(len(daily_counts), 1)
        weekly_average = daily_average * 7
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
        active_days = len(daily_counts)
        
        # 用户留存率计算
        total_users = len(user_activity)
        if total_users > 0:
            # 计算最近7天活跃用户占比
            recent_date = datetime.utcnow().date() - timedelta(days=7)
            recent_active_users = sum(
                1 for dates in user_activity.values() 
                if any(d >= recent_date for d in dates)
            )
            retention_rate = (recent_active_users / total_users) * 100
        else:
            retention_rate = 0
        
        return {
            "daily_average": round(daily_average, 2),
            "weekly_average": round(weekly_average, 2),
            "peak_hour": peak_hour,
            "active_days": active_days,
            "retention_rate": round(retention_rate, 2)
        }
    
    def _analyze_usage_patterns(self, analyses: List[ThinkingAnalysis]) -> Dict[str, Any]:
        """分析使用模式"""
        if not analyses:
            return {"session_patterns": [], "behavior_clusters": []}
        
        # 用户会话模式分析
        user_sessions = defaultdict(list)
        for analysis in analyses:
            user_sessions[analysis.user_id].append(analysis.created_at)
        
        session_patterns = []
        for user_id, timestamps in user_sessions.items():
            timestamps.sort()
            
            # 计算会话间隔
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # 小时
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                session_patterns.append({
                    "user_id": user_id,
                    "total_sessions": len(timestamps),
                    "avg_interval_hours": round(avg_interval, 2),
                    "pattern_type": self._classify_usage_pattern(avg_interval, len(timestamps))
                })
        
        # 行为聚类分析
        behavior_clusters = self._cluster_user_behaviors(analyses)
        
        return {
            "session_patterns": session_patterns,
            "behavior_clusters": behavior_clusters
        }
    
    def _classify_usage_pattern(self, avg_interval: float, session_count: int) -> str:
        """分类使用模式"""
        if avg_interval < 2 and session_count > 10:
            return "重度用户"
        elif avg_interval < 24 and session_count > 5:
            return "活跃用户"
        elif avg_interval < 72:
            return "常规用户"
        else:
            return "偶尔用户"
    
    def _cluster_user_behaviors(self, analyses: List[ThinkingAnalysis]) -> List[Dict[str, Any]]:
        """用户行为聚类"""
        user_features = defaultdict(lambda: {
            "total_analyses": 0,
            "avg_processing_time": 0,
            "analysis_types": defaultdict(int),
            "confidence_scores": [],
            "complexity_scores": []
        })
        
        # 提取用户特征
        for analysis in analyses:
            user_id = analysis.user_id
            features = user_features[user_id]
            
            features["total_analyses"] += 1
            features["avg_processing_time"] += analysis.processing_time or 0
            features["analysis_types"][analysis.analysis_type] += 1
            features["confidence_scores"].append(analysis.confidence_score or 0)
            
            # 从结果中提取复杂度信息
            if analysis.results and isinstance(analysis.results, dict):
                complexity = analysis.results.get("complexity_score", 50)
                features["complexity_scores"].append(complexity)
        
        # 计算平均值和分类
        clusters = []
        for user_id, features in user_features.items():
            if features["total_analyses"] > 0:
                features["avg_processing_time"] /= features["total_analyses"]
                
                avg_confidence = np.mean(features["confidence_scores"]) if features["confidence_scores"] else 0
                avg_complexity = np.mean(features["complexity_scores"]) if features["complexity_scores"] else 50
                
                # 分类用户类型
                user_type = self._classify_user_type(
                    features["total_analyses"],
                    avg_confidence,
                    avg_complexity,
                    features["avg_processing_time"]
                )
                
                clusters.append({
                    "user_id": user_id,
                    "user_type": user_type,
                    "total_analyses": features["total_analyses"],
                    "avg_confidence": round(avg_confidence, 2),
                    "avg_complexity": round(avg_complexity, 2),
                    "avg_processing_time": round(features["avg_processing_time"], 2),
                    "preferred_types": dict(features["analysis_types"])
                })
        
        return clusters
    
    def _classify_user_type(self, total_analyses: int, avg_confidence: float, 
                           avg_complexity: float, avg_processing_time: float) -> str:
        """分类用户类型"""
        if total_analyses >= 50 and avg_confidence >= 80:
            return "专家用户"
        elif total_analyses >= 20 and avg_complexity >= 70:
            return "高级用户"
        elif total_analyses >= 10:
            return "活跃用户"
        else:
            return "新手用户"
    
    def _analyze_time_distribution(self, analyses: List[ThinkingAnalysis]) -> Dict[str, Any]:
        """分析时间分布"""
        if not analyses:
            return {"hourly": {}, "daily": {}, "weekly": {}}
        
        hourly_dist = defaultdict(int)
        daily_dist = defaultdict(int)
        weekly_dist = defaultdict(int)
        
        for analysis in analyses:
            dt = analysis.created_at
            hourly_dist[dt.hour] += 1
            daily_dist[dt.date().isoformat()] += 1
            weekly_dist[dt.weekday()] += 1  # 0=Monday, 6=Sunday
        
        # 转换周几为中文
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekly_named = {weekday_names[k]: v for k, v in weekly_dist.items()}
        
        return {
            "hourly": dict(hourly_dist),
            "daily": dict(daily_dist),
            "weekly": weekly_named
        }
    
    def _analyze_feature_usage(self, analyses: List[ThinkingAnalysis]) -> Dict[str, Any]:
        """分析功能使用情况"""
        if not analyses:
            return {"analysis_types": {}, "feature_adoption": {}}
        
        # 分析类型使用统计
        type_usage = defaultdict(int)
        feature_usage = defaultdict(int)
        
        for analysis in analyses:
            type_usage[analysis.analysis_type] += 1
            
            # 从结果中提取使用的功能
            if analysis.results and isinstance(analysis.results, dict):
                if "features_used" in analysis.results:
                    for feature in analysis.results["features_used"]:
                        feature_usage[feature] += 1
                
                # 根据分析类型推断功能使用
                if analysis.analysis_type == "comprehensive":
                    feature_usage["三层思维分析"] += 1
                elif analysis.analysis_type == "creative":
                    feature_usage["创造性思维"] += 1
                elif analysis.analysis_type == "logical":
                    feature_usage["逻辑推理"] += 1
        
        # 计算功能采用率
        total_analyses = len(analyses)
        feature_adoption = {
            feature: {
                "count": count,
                "adoption_rate": round((count / total_analyses) * 100, 2)
            }
            for feature, count in feature_usage.items()
        }
        
        return {
            "analysis_types": dict(type_usage),
            "feature_adoption": feature_adoption
        }
    
    def _calculate_trends(self, analyses: List[ThinkingAnalysis], days: int) -> Dict[str, Any]:
        """计算趋势分析"""
        if not analyses or len(analyses) < 2:
            return {"growth_rate": 0, "trend_direction": "stable", "predictions": []}
        
        # 按日期聚合数据
        daily_data = defaultdict(int)
        for analysis in analyses:
            date_key = analysis.created_at.date()
            daily_data[date_key] += 1
        
        # 转换为时间序列
        dates = sorted(daily_data.keys())
        values = [daily_data[date] for date in dates]
        
        if len(values) < 2:
            return {"growth_rate": 0, "trend_direction": "stable", "predictions": []}
        
        # 计算增长率
        recent_avg = np.mean(values[-7:]) if len(values) >= 7 else np.mean(values[-len(values)//2:])
        early_avg = np.mean(values[:7]) if len(values) >= 7 else np.mean(values[:len(values)//2])
        
        growth_rate = ((recent_avg - early_avg) / max(early_avg, 1)) * 100 if early_avg > 0 else 0
        
        # 趋势方向
        if growth_rate > 10:
            trend_direction = "上升"
        elif growth_rate < -10:
            trend_direction = "下降"
        else:
            trend_direction = "稳定"
        
        # 简单预测（线性趋势）
        predictions = self._generate_predictions(values, 7)  # 预测未来7天
        
        return {
            "growth_rate": round(growth_rate, 2),
            "trend_direction": trend_direction,
            "predictions": predictions
        }
    
    def _generate_predictions(self, values: List[int], forecast_days: int) -> List[Dict[str, Any]]:
        """生成预测数据"""
        if len(values) < 3:
            return []
        
        # 简单线性回归预测
        x = np.arange(len(values))
        y = np.array(values)
        
        # 计算趋势线
        z = np.polyfit(x, y, 1)
        trend_line = np.poly1d(z)
        
        # 生成预测
        predictions = []
        base_date = datetime.utcnow().date()
        
        for i in range(1, forecast_days + 1):
            future_x = len(values) + i - 1
            predicted_value = max(0, int(trend_line(future_x)))
            future_date = base_date + timedelta(days=i)
            
            predictions.append({
                "date": future_date.isoformat(),
                "predicted_value": predicted_value,
                "confidence": max(0.5, 1.0 - (i * 0.1))  # 随时间递减的置信度
            })
        
        return predictions
    
    # ==================== 思维模式洞察 ====================
    
    async def get_thinking_pattern_insights(
        self, 
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取思维模式洞察
        
        Args:
            user_id: 用户ID，None表示全局统计
            days: 分析天数
            
        Returns:
            思维模式洞察数据
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 基础查询
            base_query = self.db.query(ThinkingAnalysis).filter(
                ThinkingAnalysis.created_at >= start_date
            )
            
            if user_id:
                base_query = base_query.filter(ThinkingAnalysis.user_id == user_id)
            
            analyses = base_query.all()
            
            # 思维类型分布分析
            thinking_distribution = self._analyze_thinking_distribution(analyses)
            
            # 思维能力评估
            cognitive_assessment = self._assess_cognitive_abilities(analyses)
            
            # 思维模式演进
            pattern_evolution = self._analyze_pattern_evolution(analyses)
            
            # 个性化建议
            recommendations = self._generate_recommendations(analyses, user_id)
            
            # 对比分析
            comparative_analysis = await self._get_comparative_analysis(analyses, user_id)
            
            return {
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "thinking_distribution": thinking_distribution,
                "cognitive_assessment": cognitive_assessment,
                "pattern_evolution": pattern_evolution,
                "recommendations": recommendations,
                "comparative_analysis": comparative_analysis,
                "total_analyses": len(analyses)
            }
            
        except Exception as e:
            logger.error(f"思维模式洞察分析失败: {e}")
            raise
    
    def _analyze_thinking_distribution(self, analyses: List[ThinkingAnalysis]) -> Dict[str, Any]:
        """分析思维类型分布"""
        if not analyses:
            return {"types": {}, "styles": {}, "complexity_levels": {}}
        
        # 思维类型分布
        type_dist = defaultdict(int)
        style_scores = defaultdict(list)
        complexity_levels = defaultdict(int)
        
        for analysis in analyses:
            type_dist[analysis.analysis_type] += 1
            
            # 从thinking_summary中提取思维风格分数
            if analysis.thinking_summary and isinstance(analysis.thinking_summary, dict):
                thinking_scores = analysis.thinking_summary.get("thinking_scores", {})
                for style, score in thinking_scores.items():
                    style_scores[style].append(score)
            
            # 复杂度分析
            if analysis.results and isinstance(analysis.results, dict):
                complexity = analysis.results.get("complexity_score", 50)
                if complexity >= 80:
                    complexity_levels["高复杂度"] += 1
                elif complexity >= 60:
                    complexity_levels["中复杂度"] += 1
                else:
                    complexity_levels["低复杂度"] += 1
        
        # 计算平均思维风格分数
        avg_style_scores = {}
        for style, scores in style_scores.items():
            avg_style_scores[style] = round(np.mean(scores), 2) if scores else 0
        
        return {
            "types": dict(type_dist),
            "styles": avg_style_scores,
            "complexity_levels": dict(complexity_levels)
        }
    
    def _assess_cognitive_abilities(self, analyses: List[ThinkingAnalysis]) -> Dict[str, Any]:
        """评估认知能力"""
        if not analyses:
            return {"overall_score": 0, "abilities": {}, "strengths": [], "weaknesses": []}
        
        # 收集各项能力指标
        abilities = {
            "逻辑推理": [],
            "创造思维": [],
            "批判思维": [],
            "系统思维": [],
            "直觉思维": []
        }
        
        confidence_scores = []
        processing_times = []
        
        for analysis in analyses:
            confidence_scores.append(analysis.confidence_score or 0)
            processing_times.append(analysis.processing_time or 0)
            
            # 从分析结果中提取能力评分
            if analysis.thinking_summary and isinstance(analysis.thinking_summary, dict):
                thinking_scores = analysis.thinking_summary.get("thinking_scores", {})
                
                # 映射到认知能力
                if "logical_thinking" in thinking_scores:
                    abilities["逻辑推理"].append(thinking_scores["logical_thinking"])
                if "creative_thinking" in thinking_scores:
                    abilities["创造思维"].append(thinking_scores["creative_thinking"])
                if "visual_thinking" in thinking_scores:
                    abilities["直觉思维"].append(thinking_scores["visual_thinking"])
                
                # 根据分析类型推断其他能力
                if analysis.analysis_type == "logical":
                    abilities["批判思维"].append(analysis.confidence_score or 70)
                elif analysis.analysis_type == "comprehensive":
                    abilities["系统思维"].append(analysis.confidence_score or 75)
        
        # 计算平均能力分数
        ability_scores = {}
        for ability, scores in abilities.items():
            ability_scores[ability] = round(np.mean(scores), 2) if scores else 0
        
        # 总体评分
        overall_score = round(np.mean(list(ability_scores.values())), 2) if ability_scores else 0
        
        # 识别优势和劣势
        sorted_abilities = sorted(ability_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [ability for ability, score in sorted_abilities[:2] if score >= 70]
        weaknesses = [ability for ability, score in sorted_abilities[-2:] if score < 60]
        
        return {
            "overall_score": overall_score,
            "abilities": ability_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "avg_confidence": round(np.mean(confidence_scores), 2) if confidence_scores else 0,
            "avg_processing_time": round(np.mean(processing_times), 2) if processing_times else 0
        }
    
    def _analyze_pattern_evolution(self, analyses: List[ThinkingAnalysis]) -> Dict[str, Any]:
        """分析思维模式演进"""
        if len(analyses) < 5:
            return {"evolution_trend": "数据不足", "milestones": [], "improvement_rate": 0}
        
        # 按时间排序
        sorted_analyses = sorted(analyses, key=lambda x: x.created_at)
        
        # 划分时期
        total_count = len(sorted_analyses)
        period_size = max(5, total_count // 4)  # 至少5个样本为一个时期
        
        periods = []
        for i in range(0, total_count, period_size):
            period_analyses = sorted_analyses[i:i + period_size]
            if len(period_analyses) >= 3:  # 至少3个样本才分析
                periods.append(period_analyses)
        
        if len(periods) < 2:
            return {"evolution_trend": "时间跨度不足", "milestones": [], "improvement_rate": 0}
        
        # 分析各时期的指标
        period_metrics = []
        for period in periods:
            confidence_scores = [a.confidence_score or 0 for a in period]
            processing_times = [a.processing_time or 0 for a in period]
            
            avg_confidence = np.mean(confidence_scores)
            avg_processing_time = np.mean(processing_times)
            
            period_metrics.append({
                "avg_confidence": avg_confidence,
                "avg_processing_time": avg_processing_time,
                "analysis_count": len(period),
                "start_date": period[0].created_at.isoformat(),
                "end_date": period[-1].created_at.isoformat()
            })
        
        # 计算改进率
        first_confidence = period_metrics[0]["avg_confidence"]
        last_confidence = period_metrics[-1]["avg_confidence"]
        improvement_rate = ((last_confidence - first_confidence) / max(first_confidence, 1)) * 100
        
        # 确定演进趋势
        if improvement_rate > 15:
            evolution_trend = "显著提升"
        elif improvement_rate > 5:
            evolution_trend = "稳步提升"
        elif improvement_rate > -5:
            evolution_trend = "基本稳定"
        else:
            evolution_trend = "有所下降"
        
        # 识别里程碑
        milestones = self._identify_milestones(sorted_analyses)
        
        return {
            "evolution_trend": evolution_trend,
            "improvement_rate": round(improvement_rate, 2),
            "period_metrics": period_metrics,
            "milestones": milestones
        }
    
    def _identify_milestones(self, analyses: List[ThinkingAnalysis]) -> List[Dict[str, Any]]:
        """识别重要里程碑"""
        milestones = []
        
        # 首次分析
        if analyses:
            milestones.append({
                "type": "首次分析",
                "date": analyses[0].created_at.isoformat(),
                "description": "开始使用智能思维分析系统"
            })
        
        # 高置信度分析
        high_confidence_analyses = [a for a in analyses if (a.confidence_score or 0) >= 90]
        if high_confidence_analyses:
            milestones.append({
                "type": "高质量分析",
                "date": high_confidence_analyses[0].created_at.isoformat(),
                "description": f"首次达到{high_confidence_analyses[0].confidence_score}%置信度"
            })
        
        # 分析数量里程碑
        analysis_milestones = [10, 50, 100, 200]
        for milestone in analysis_milestones:
            if len(analyses) >= milestone:
                milestone_analysis = analyses[milestone - 1]
                milestones.append({
                    "type": f"{milestone}次分析",
                    "date": milestone_analysis.created_at.isoformat(),
                    "description": f"累计完成{milestone}次思维分析"
                })
        
        return milestones[-5:]  # 返回最近5个里程碑
    
    def _generate_recommendations(self, analyses: List[ThinkingAnalysis], user_id: Optional[int]) -> List[Dict[str, Any]]:
        """生成个性化建议"""
        if not analyses:
            return [{"type": "开始使用", "content": "开始进行思维分析，探索您的思维模式", "priority": "high"}]
        
        recommendations = []
        
        # 基于能力评估的建议
        cognitive_assessment = self._assess_cognitive_abilities(analyses)
        abilities = cognitive_assessment["abilities"]
        
        # 针对薄弱环节的建议
        for ability, score in abilities.items():
            if score < 60:
                recommendations.append({
                    "type": "能力提升",
                    "content": f"建议多练习{ability}相关的分析，当前得分：{score}",
                    "priority": "high",
                    "target_ability": ability
                })
        
        # 基于使用模式的建议
        type_usage = defaultdict(int)
        for analysis in analyses:
            type_usage[analysis.analysis_type] += 1
        
        total_analyses = len(analyses)
        if total_analyses >= 10:
            # 分析类型多样性建议
            unique_types = len(type_usage)
            if unique_types < 3:
                recommendations.append({
                    "type": "功能探索",
                    "content": "尝试使用不同类型的思维分析，丰富您的思维维度",
                    "priority": "medium"
                })
            
            # 频率建议
            recent_analyses = [a for a in analyses if (datetime.utcnow() - a.created_at).days <= 7]
            if len(recent_analyses) < 3:
                recommendations.append({
                    "type": "使用频率",
                    "content": "建议增加使用频率，保持思维训练的连续性",
                    "priority": "medium"
                })
        
        # 基于处理时间的建议
        processing_times = [a.processing_time or 0 for a in analyses if a.processing_time]
        if processing_times:
            avg_time = np.mean(processing_times)
            if avg_time > 300:  # 5分钟
                recommendations.append({
                    "type": "效率提升",
                    "content": "可以尝试更简洁的输入，提高分析效率",
                    "priority": "low"
                })
        
        # 成就激励
        if total_analyses >= 50:
            recommendations.append({
                "type": "成就认可",
                "content": f"恭喜！您已完成{total_analyses}次分析，展现了持续学习的精神",
                "priority": "positive"
            })
        
        return recommendations[:5]  # 返回最多5个建议
    
    async def _get_comparative_analysis(self, analyses: List[ThinkingAnalysis], user_id: Optional[int]) -> Dict[str, Any]:
        """获取对比分析"""
        if not user_id or not analyses:
            return {"user_percentile": None, "comparison_metrics": {}}
        
        try:
            # 获取全局统计数据进行对比
            all_users_query = self.db.query(ThinkingAnalysis).filter(
                ThinkingAnalysis.created_at >= datetime.utcnow() - timedelta(days=30)
            )
            all_analyses = all_users_query.all()
            
            if not all_analyses:
                return {"user_percentile": None, "comparison_metrics": {}}
            
            # 用户指标
            user_confidence = np.mean([a.confidence_score or 0 for a in analyses])
            user_analysis_count = len(analyses)
            
            # 全局指标
            all_confidences = [a.confidence_score or 0 for a in all_analyses]
            all_user_counts = defaultdict(int)
            for a in all_analyses:
                all_user_counts[a.user_id] += 1
            
            # 计算百分位
            confidence_percentile = (np.sum(np.array(all_confidences) <= user_confidence) / len(all_confidences)) * 100
            count_percentile = (np.sum(np.array(list(all_user_counts.values())) <= user_analysis_count) / len(all_user_counts)) * 100
            
            return {
                "user_percentile": {
                    "confidence": round(confidence_percentile, 1),
                    "activity": round(count_percentile, 1)
                },
                "comparison_metrics": {
                    "user_avg_confidence": round(user_confidence, 2),
                    "global_avg_confidence": round(np.mean(all_confidences), 2),
                    "user_analysis_count": user_analysis_count,
                    "global_avg_count": round(np.mean(list(all_user_counts.values())), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"对比分析失败: {e}")
            return {"user_percentile": None, "comparison_metrics": {}}
    
    # ==================== 系统使用统计 ====================
    
    async def get_system_usage_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取系统使用统计"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 用户统计
            user_stats = await self._get_user_statistics(start_date, end_date)
            
            # 分析统计
            analysis_stats = await self._get_analysis_statistics(start_date, end_date)
            
            # 协作统计
            collaboration_stats = await self._get_collaboration_statistics(start_date, end_date)
            
            # 性能统计
            performance_stats = await self._get_performance_statistics(start_date, end_date)
            
            # 增长趋势
            growth_trends = await self._get_growth_trends(start_date, end_date)
            
            return {
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "user_statistics": user_stats,
                "analysis_statistics": analysis_stats,
                "collaboration_statistics": collaboration_stats,
                "performance_statistics": performance_stats,
                "growth_trends": growth_trends
            }
            
        except Exception as e:
            logger.error(f"系统使用统计失败: {e}")
            raise
    
    async def _get_user_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取用户统计"""
        # 总用户数
        total_users = self.db.query(User).count()
        
        # 新注册用户
        new_users = self.db.query(User).filter(
            User.created_at >= start_date
        ).count()
        
        # 活跃用户
        active_users = self.db.query(ThinkingAnalysis.user_id).filter(
            ThinkingAnalysis.created_at >= start_date
        ).distinct().count()
        
        # 用户留存
        retention_rate = (active_users / max(total_users, 1)) * 100
        
        return {
            "total_users": total_users,
            "new_users": new_users,
            "active_users": active_users,
            "retention_rate": round(retention_rate, 2)
        }
    
    async def _get_analysis_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取分析统计"""
        analyses = self.db.query(ThinkingAnalysis).filter(
            ThinkingAnalysis.created_at >= start_date
        ).all()
        
        total_analyses = len(analyses)
        
        # 分析类型分布
        type_distribution = defaultdict(int)
        confidence_scores = []
        processing_times = []
        
        for analysis in analyses:
            type_distribution[analysis.analysis_type] += 1
            confidence_scores.append(analysis.confidence_score or 0)
            processing_times.append(analysis.processing_time or 0)
        
        return {
            "total_analyses": total_analyses,
            "type_distribution": dict(type_distribution),
            "avg_confidence": round(np.mean(confidence_scores), 2) if confidence_scores else 0,
            "avg_processing_time": round(np.mean(processing_times), 2) if processing_times else 0
        }
    
    async def _get_collaboration_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取协作统计"""
        try:
            sessions = self.db.query(CollaborationSession).filter(
                CollaborationSession.created_at >= start_date
            ).all()
            
            events = self.db.query(CollaborationEvent).filter(
                CollaborationEvent.created_at >= start_date
            ).all()
            
            return {
                "total_sessions": len(sessions),
                "total_events": len(events),
                "avg_session_duration": 0,  # 需要根据实际数据计算
                "active_collaborators": len(set(e.user_id for e in events if e.user_id))
            }
        except Exception:
            # 如果协作表不存在，返回默认值
            return {
                "total_sessions": 0,
                "total_events": 0,
                "avg_session_duration": 0,
                "active_collaborators": 0
            }
    
    async def _get_performance_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取性能统计"""
        # 这里可以集成实际的性能监控数据
        return {
            "avg_response_time": 250,  # 毫秒
            "error_rate": 0.5,  # 百分比
            "uptime": 99.9,  # 百分比
            "concurrent_users": 50  # 当前并发用户数
        }
    
    async def _get_growth_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取增长趋势"""
        # 按天统计
        daily_stats = defaultdict(lambda: {"users": 0, "analyses": 0})
        
        # 用户注册趋势
        users = self.db.query(User).filter(User.created_at >= start_date).all()
        for user in users:
            date_key = user.created_at.date().isoformat()
            daily_stats[date_key]["users"] += 1
        
        # 分析趋势
        analyses = self.db.query(ThinkingAnalysis).filter(
            ThinkingAnalysis.created_at >= start_date
        ).all()
        for analysis in analyses:
            date_key = analysis.created_at.date().isoformat()
            daily_stats[date_key]["analyses"] += 1
        
        # 转换为列表格式
        trend_data = []
        current_date = start_date.date()
        end_date_date = end_date.date()
        
        while current_date <= end_date_date:
            date_str = current_date.isoformat()
            trend_data.append({
                "date": date_str,
                "new_users": daily_stats[date_str]["users"],
                "new_analyses": daily_stats[date_str]["analyses"]
            })
            current_date += timedelta(days=1)
        
        return {
            "daily_trends": trend_data
        } 