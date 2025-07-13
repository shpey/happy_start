"""
数据分析API端点
提供用户行为分析、思维模式洞察和系统使用统计的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ....core.database import get_db
from ....core.security import get_current_user, get_current_active_user
from ....services.analytics_service import AnalyticsService
from ....models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/user-behavior")
async def get_user_behavior_analytics(
    days: int = Query(30, ge=1, le=365, description="分析时间范围（天）"),
    user_id: Optional[int] = Query(None, description="用户ID，为空表示当前用户"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户行为分析
    
    - **days**: 分析时间范围（1-365天）
    - **user_id**: 指定用户ID（管理员功能，普通用户只能查看自己的数据）
    
    Returns:
        - activity_metrics: 活跃度指标
        - usage_patterns: 使用模式分析
        - time_distribution: 时间分布
        - feature_usage: 功能使用统计
        - trends: 趋势分析
    """
    try:
        # 权限检查：普通用户只能查看自己的数据
        target_user_id = user_id
        if user_id and user_id != current_user.id:
            # 检查是否为管理员
            if not getattr(current_user, 'is_admin', False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问其他用户的数据"
                )
        elif not user_id:
            target_user_id = current_user.id
        
        # 创建分析服务
        analytics_service = AnalyticsService(db)
        
        # 获取用户行为分析
        behavior_analytics = await analytics_service.get_user_behavior_analytics(
            user_id=target_user_id,
            days=days
        )
        
        return {
            "success": True,
            "message": "用户行为分析获取成功",
            "data": behavior_analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户行为分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/thinking-patterns")
async def get_thinking_pattern_insights(
    days: int = Query(30, ge=1, le=365, description="分析时间范围（天）"),
    user_id: Optional[int] = Query(None, description="用户ID，为空表示当前用户"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取思维模式洞察
    
    - **days**: 分析时间范围（1-365天）
    - **user_id**: 指定用户ID（管理员功能）
    
    Returns:
        - thinking_distribution: 思维类型分布
        - cognitive_assessment: 认知能力评估
        - pattern_evolution: 思维模式演进
        - recommendations: 个性化建议
        - comparative_analysis: 对比分析
    """
    try:
        # 权限检查
        target_user_id = user_id
        if user_id and user_id != current_user.id:
            if not getattr(current_user, 'is_admin', False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问其他用户的数据"
                )
        elif not user_id:
            target_user_id = current_user.id
        
        # 创建分析服务
        analytics_service = AnalyticsService(db)
        
        # 获取思维模式洞察
        pattern_insights = await analytics_service.get_thinking_pattern_insights(
            user_id=target_user_id,
            days=days
        )
        
        return {
            "success": True,
            "message": "思维模式洞察获取成功",
            "data": pattern_insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"思维模式洞察分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/system-usage")
async def get_system_usage_statistics(
    days: int = Query(30, ge=1, le=365, description="统计时间范围（天）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取系统使用统计（管理员功能）
    
    - **days**: 统计时间范围（1-365天）
    
    Returns:
        - user_statistics: 用户统计
        - analysis_statistics: 分析统计
        - collaboration_statistics: 协作统计
        - performance_statistics: 性能统计
        - growth_trends: 增长趋势
    """
    try:
        # 管理员权限检查
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限才能查看系统统计"
            )
        
        # 创建分析服务
        analytics_service = AnalyticsService(db)
        
        # 获取系统使用统计
        system_stats = await analytics_service.get_system_usage_statistics(days=days)
        
        return {
            "success": True,
            "message": "系统使用统计获取成功",
            "data": system_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"系统使用统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"统计失败: {str(e)}"
        )


@router.get("/dashboard-summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取仪表板摘要数据
    
    提供用户个人仪表板所需的关键指标摘要
    
    Returns:
        - personal_stats: 个人统计
        - recent_activity: 最近活动
        - recommendations: 推荐建议
        - quick_insights: 快速洞察
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # 获取用户最近30天的行为分析
        behavior_analytics = await analytics_service.get_user_behavior_analytics(
            user_id=current_user.id,
            days=30
        )
        
        # 获取思维模式洞察
        pattern_insights = await analytics_service.get_thinking_pattern_insights(
            user_id=current_user.id,
            days=30
        )
        
        # 构建仪表板摘要
        dashboard_summary = {
            "personal_stats": {
                "total_analyses": behavior_analytics.get("total_analyses", 0),
                "active_days": behavior_analytics["activity_metrics"]["active_days"],
                "daily_average": behavior_analytics["activity_metrics"]["daily_average"],
                "overall_score": pattern_insights["cognitive_assessment"]["overall_score"],
                "dominant_thinking_style": _get_dominant_style(pattern_insights["thinking_distribution"]["styles"])
            },
            "recent_activity": {
                "time_distribution": behavior_analytics["time_distribution"],
                "feature_usage": behavior_analytics["feature_usage"],
                "trends": behavior_analytics["trends"]
            },
            "recommendations": pattern_insights["recommendations"][:3],  # 前3个建议
            "quick_insights": {
                "strengths": pattern_insights["cognitive_assessment"]["strengths"],
                "weaknesses": pattern_insights["cognitive_assessment"]["weaknesses"],
                "evolution_trend": pattern_insights["pattern_evolution"]["evolution_trend"],
                "improvement_rate": pattern_insights["pattern_evolution"]["improvement_rate"]
            }
        }
        
        return {
            "success": True,
            "message": "仪表板摘要获取成功",
            "data": dashboard_summary
        }
        
    except Exception as e:
        logger.error(f"仪表板摘要获取失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败: {str(e)}"
        )


@router.get("/comparative-analysis")
async def get_comparative_analysis(
    metric: str = Query("confidence", description="对比指标（confidence, activity, growth）"),
    period: str = Query("monthly", description="时间周期（weekly, monthly, quarterly）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取对比分析数据
    
    - **metric**: 对比指标
        - confidence: 置信度对比
        - activity: 活跃度对比
        - growth: 成长速度对比
    - **period**: 时间周期
        - weekly: 最近7天对比
        - monthly: 最近30天对比
        - quarterly: 最近90天对比
    
    Returns:
        - user_metrics: 用户指标
        - peer_comparison: 同期用户对比
        - percentile_rank: 百分位排名
        - improvement_suggestions: 改进建议
    """
    try:
        # 根据周期确定天数
        period_days = {
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90
        }
        
        days = period_days.get(period, 30)
        
        analytics_service = AnalyticsService(db)
        
        # 获取用户数据
        user_behavior = await analytics_service.get_user_behavior_analytics(
            user_id=current_user.id,
            days=days
        )
        
        user_patterns = await analytics_service.get_thinking_pattern_insights(
            user_id=current_user.id,
            days=days
        )
        
        # 获取全局对比数据
        global_behavior = await analytics_service.get_user_behavior_analytics(
            user_id=None,  # 全局统计
            days=days
        )
        
        # 构建对比分析
        comparative_data = {
            "user_metrics": _extract_metric_value(user_behavior, user_patterns, metric),
            "global_average": _extract_metric_value(global_behavior, None, metric),
            "percentile_rank": user_patterns["comparative_analysis"].get("user_percentile", {}),
            "improvement_suggestions": _generate_improvement_suggestions(
                user_behavior, user_patterns, metric
            )
        }
        
        return {
            "success": True,
            "message": "对比分析获取成功",
            "data": comparative_data
        }
        
    except Exception as e:
        logger.error(f"对比分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/export-report")
async def export_analytics_report(
    format: str = Query("json", description="导出格式（json, csv, pdf）"),
    include_charts: bool = Query(False, description="是否包含图表数据"),
    days: int = Query(30, ge=1, le=365, description="报告时间范围"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    导出分析报告
    
    - **format**: 导出格式（json, csv, pdf）
    - **include_charts**: 是否包含图表数据
    - **days**: 报告时间范围
    
    Returns:
        - report_data: 报告数据
        - download_url: 下载链接（如果生成了文件）
        - metadata: 报告元数据
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # 获取完整分析数据
        behavior_analytics = await analytics_service.get_user_behavior_analytics(
            user_id=current_user.id,
            days=days
        )
        
        pattern_insights = await analytics_service.get_thinking_pattern_insights(
            user_id=current_user.id,
            days=days
        )
        
        # 构建报告数据
        report_data = {
            "user_info": {
                "user_id": current_user.id,
                "username": getattr(current_user, 'username', '未知用户'),
                "report_generated_at": datetime.utcnow().isoformat()
            },
            "analysis_period": behavior_analytics["period"],
            "behavior_analytics": behavior_analytics,
            "pattern_insights": pattern_insights
        }
        
        if include_charts:
            # 添加图表数据
            report_data["chart_data"] = _generate_chart_data(behavior_analytics, pattern_insights)
        
        # 根据格式处理报告
        if format == "json":
            return {
                "success": True,
                "message": "报告生成成功",
                "data": report_data,
                "metadata": {
                    "format": "json",
                    "size": len(str(report_data)),
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
        else:
            # 对于其他格式，先返回JSON，后续可以实现文件生成
            return {
                "success": True,
                "message": f"{format.upper()}格式报告功能正在开发中，暂时返回JSON格式",
                "data": report_data,
                "metadata": {
                    "format": format,
                    "status": "development",
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
        
    except Exception as e:
        logger.error(f"报告导出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


# ==================== 辅助函数 ====================

def _get_dominant_style(styles: Dict[str, float]) -> str:
    """获取主导思维风格"""
    if not styles:
        return "未知"
    
    return max(styles.items(), key=lambda x: x[1])[0] if styles else "未知"


def _extract_metric_value(behavior_data: Dict[str, Any], pattern_data: Optional[Dict[str, Any]], metric: str) -> Dict[str, Any]:
    """提取指定指标的值"""
    if metric == "confidence":
        return {
            "current_value": pattern_data["cognitive_assessment"]["avg_confidence"] if pattern_data else 0,
            "metric_type": "置信度",
            "unit": "%"
        }
    elif metric == "activity":
        return {
            "current_value": behavior_data["activity_metrics"]["daily_average"],
            "metric_type": "日均活跃度",
            "unit": "次/天"
        }
    elif metric == "growth":
        return {
            "current_value": behavior_data["trends"]["growth_rate"],
            "metric_type": "成长率",
            "unit": "%"
        }
    else:
        return {
            "current_value": 0,
            "metric_type": "未知指标",
            "unit": ""
        }


def _generate_improvement_suggestions(
    behavior_data: Dict[str, Any], 
    pattern_data: Dict[str, Any], 
    metric: str
) -> List[Dict[str, Any]]:
    """生成改进建议"""
    suggestions = []
    
    if metric == "confidence":
        avg_confidence = pattern_data["cognitive_assessment"]["avg_confidence"]
        if avg_confidence < 70:
            suggestions.append({
                "type": "置信度提升",
                "content": "建议多进行基础练习，逐步提高分析质量",
                "priority": "high"
            })
    
    elif metric == "activity":
        daily_avg = behavior_data["activity_metrics"]["daily_average"]
        if daily_avg < 1:
            suggestions.append({
                "type": "活跃度提升",
                "content": "建议增加使用频率，每天至少进行一次思维分析",
                "priority": "medium"
            })
    
    elif metric == "growth":
        growth_rate = behavior_data["trends"]["growth_rate"]
        if growth_rate < 0:
            suggestions.append({
                "type": "成长速度",
                "content": "尝试不同类型的分析，突破当前瓶颈",
                "priority": "high"
            })
    
    return suggestions


def _generate_chart_data(behavior_analytics: Dict[str, Any], pattern_insights: Dict[str, Any]) -> Dict[str, Any]:
    """生成图表数据"""
    return {
        "time_series": {
            "daily_activity": behavior_analytics["time_distribution"]["daily"],
            "hourly_distribution": behavior_analytics["time_distribution"]["hourly"]
        },
        "distributions": {
            "thinking_types": pattern_insights["thinking_distribution"]["types"],
            "analysis_types": behavior_analytics["feature_usage"]["analysis_types"]
        },
        "radar_chart": {
            "cognitive_abilities": pattern_insights["cognitive_assessment"]["abilities"]
        },
        "trend_lines": {
            "growth_trend": behavior_analytics["trends"]["predictions"]
        }
    } 