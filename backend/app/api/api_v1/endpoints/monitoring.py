"""
监控API端点
提供系统健康检查、性能指标和告警信息
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import get_current_user, require_permission, Permission
from ....core.monitoring import (
    performance_monitor, health_checker, metrics_collector,
    PerformanceMetric, HealthCheckResult, Alert, ServiceStatus, AlertLevel
)

router = APIRouter()


class SystemHealthResponse(BaseModel):
    """系统健康响应"""
    overall_status: ServiceStatus
    timestamp: datetime
    services: Dict[str, Dict[str, Any]]
    uptime_seconds: float


class PerformanceMetricsResponse(BaseModel):
    """性能指标响应"""
    current: Optional[Dict[str, Any]]
    history: List[Dict[str, Any]]
    summary: Dict[str, Any]


class AlertResponse(BaseModel):
    """告警响应"""
    active_alerts: List[Dict[str, Any]]
    resolved_alerts: List[Dict[str, Any]]
    alert_summary: Dict[str, Any]


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    request: Request,
    include_details: bool = True
) -> SystemHealthResponse:
    """
    获取系统健康状态
    
    - **include_details**: 是否包含详细信息
    """
    # 运行所有健康检查
    health_results = health_checker.run_all_checks()
    overall_status = health_checker.get_overall_health()
    
    # 计算系统运行时间
    uptime = performance_monitor.start_time
    uptime_seconds = datetime.utcnow().timestamp() - uptime
    
    # 构建服务状态信息
    services = {}
    for name, result in health_results.items():
        service_info = {
            "status": result.status.value,
            "response_time": result.response_time,
            "last_check": result.timestamp.isoformat()
        }
        
        if include_details:
            service_info.update({
                "details": result.details,
                "errors": result.errors
            })
        
        services[name] = service_info
    
    return SystemHealthResponse(
        overall_status=overall_status,
        timestamp=datetime.utcnow(),
        services=services,
        uptime_seconds=uptime_seconds
    )


@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    request: Request,
    hours: int = 1,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> PerformanceMetricsResponse:
    """
    获取性能指标
    
    - **hours**: 历史数据时间范围（小时）
    """
    # 获取当前指标
    current_metric = performance_monitor.get_current_metrics()
    current_data = None
    if current_metric:
        current_data = {
            "timestamp": current_metric.timestamp.isoformat(),
            "cpu_percent": current_metric.cpu_percent,
            "memory_percent": current_metric.memory_percent,
            "memory_used_mb": current_metric.memory_used_mb,
            "disk_percent": current_metric.disk_percent,
            "network_bytes_sent": current_metric.network_bytes_sent,
            "network_bytes_recv": current_metric.network_bytes_recv,
            "active_connections": current_metric.active_connections,
            "response_time_avg": current_metric.response_time_avg,
            "requests_per_second": current_metric.requests_per_second,
            "error_rate": current_metric.error_rate
        }
    
    # 获取历史数据
    history_metrics = performance_monitor.get_metrics_history(hours * 60)
    history_data = []
    for metric in history_metrics:
        history_data.append({
            "timestamp": metric.timestamp.isoformat(),
            "cpu_percent": metric.cpu_percent,
            "memory_percent": metric.memory_percent,
            "memory_used_mb": metric.memory_used_mb,
            "disk_percent": metric.disk_percent,
            "response_time_avg": metric.response_time_avg,
            "requests_per_second": metric.requests_per_second,
            "error_rate": metric.error_rate
        })
    
    # 获取自定义指标摘要
    custom_metrics = metrics_collector.get_metrics_summary()
    
    # 计算汇总统计
    summary = {
        "total_requests": performance_monitor.request_count,
        "total_errors": performance_monitor.error_count,
        "uptime_seconds": datetime.utcnow().timestamp() - performance_monitor.start_time,
        "custom_metrics": custom_metrics
    }
    
    if history_data:
        # 计算平均值
        cpu_values = [m["cpu_percent"] for m in history_data]
        memory_values = [m["memory_percent"] for m in history_data]
        response_times = [m["response_time_avg"] for m in history_data]
        
        summary.update({
            "avg_cpu_percent": sum(cpu_values) / len(cpu_values),
            "avg_memory_percent": sum(memory_values) / len(memory_values),
            "avg_response_time": sum(response_times) / len(response_times),
            "max_cpu_percent": max(cpu_values),
            "max_memory_percent": max(memory_values),
            "max_response_time": max(response_times)
        })
    
    return PerformanceMetricsResponse(
        current=current_data,
        history=history_data,
        summary=summary
    )


@router.get("/alerts", response_model=AlertResponse)
async def get_alerts(
    request: Request,
    include_resolved: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AlertResponse:
    """
    获取系统告警信息
    
    - **include_resolved**: 是否包含已解决的告警
    """
    # 获取活跃告警
    active_alerts = performance_monitor.get_active_alerts()
    active_alerts_data = []
    for alert in active_alerts:
        active_alerts_data.append({
            "id": alert.id,
            "level": alert.level.value,
            "title": alert.title,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "service": alert.service,
            "metric": alert.metric,
            "value": alert.value,
            "threshold": alert.threshold
        })
    
    # 获取已解决的告警
    resolved_alerts_data = []
    if include_resolved:
        resolved_alerts = [a for a in performance_monitor.alerts if a.resolved]
        for alert in resolved_alerts[-50:]:  # 最近50个已解决告警
            resolved_alerts_data.append({
                "id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "service": alert.service,
                "metric": alert.metric,
                "value": alert.value,
                "threshold": alert.threshold
            })
    
    # 统计信息
    alert_summary = {
        "active_count": len(active_alerts_data),
        "critical_count": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
        "error_count": len([a for a in active_alerts if a.level == AlertLevel.ERROR]),
        "warning_count": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
        "info_count": len([a for a in active_alerts if a.level == AlertLevel.INFO])
    }
    
    return AlertResponse(
        active_alerts=active_alerts_data,
        resolved_alerts=resolved_alerts_data,
        alert_summary=alert_summary
    )


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    解决告警
    
    - **alert_id**: 告警ID
    """
    performance_monitor.resolve_alert(alert_id)
    
    return {
        "success": True,
        "message": f"告警 {alert_id} 已标记为已解决",
        "resolved_at": datetime.utcnow().isoformat(),
        "resolved_by": current_user.get("username", "unknown")
    }


@router.get("/metrics/custom")
async def get_custom_metrics(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取自定义指标"""
    return metrics_collector.get_metrics_summary()


@router.post("/metrics/custom")
async def record_custom_metric(
    request: Request,
    metric_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    记录自定义指标
    
    - **metric_data**: 指标数据
      - name: 指标名称
      - type: 指标类型 (counter, gauge, histogram)
      - value: 指标值
      - tags: 标签 (可选)
    """
    name = metric_data.get("name")
    metric_type = metric_data.get("type")
    value = metric_data.get("value")
    tags = metric_data.get("tags", {})
    
    if not all([name, metric_type, value is not None]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要的指标参数: name, type, value"
        )
    
    try:
        if metric_type == "counter":
            metrics_collector.increment_counter(name, int(value), tags)
        elif metric_type == "gauge":
            metrics_collector.set_gauge(name, float(value), tags)
        elif metric_type == "histogram":
            metrics_collector.record_histogram(name, float(value), tags)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的指标类型，支持: counter, gauge, histogram"
            )
        
        return {
            "success": True,
            "message": f"指标 {name} 记录成功",
            "metric": {
                "name": name,
                "type": metric_type,
                "value": value,
                "tags": tags
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"指标值格式错误: {str(e)}"
        )


@router.get("/system/info")
async def get_system_info(
    request: Request
) -> Dict[str, Any]:
    """获取系统信息"""
    import platform
    import psutil
    from ....core.config import settings
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "disk_total_gb": psutil.disk_usage('/').total / 1024 / 1024 / 1024
        },
        "application": {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "api_version": settings.API_V1_STR
        },
        "runtime": {
            "uptime_seconds": datetime.utcnow().timestamp() - performance_monitor.start_time,
            "total_requests": performance_monitor.request_count,
            "total_errors": performance_monitor.error_count,
            "current_connections": len(psutil.net_connections()) if hasattr(psutil, 'net_connections') else 0
        }
    }


@router.get("/system/status")
async def get_system_status(
    request: Request
) -> Dict[str, Any]:
    """获取简化的系统状态（公开接口）"""
    health_results = health_checker.run_all_checks()
    overall_status = health_checker.get_overall_health()
    current_metric = performance_monitor.get_current_metrics()
    
    status_data = {
        "status": overall_status.value,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": datetime.utcnow().timestamp() - performance_monitor.start_time,
        "services": len(health_results),
        "healthy_services": len([r for r in health_results.values() if r.status == ServiceStatus.HEALTHY])
    }
    
    if current_metric:
        status_data.update({
            "cpu_percent": current_metric.cpu_percent,
            "memory_percent": current_metric.memory_percent,
            "response_time_avg": current_metric.response_time_avg,
            "requests_per_second": current_metric.requests_per_second
        })
    
    return status_data


@router.post("/system/health-check")
@require_permission(Permission.ADMIN)
async def trigger_health_check(
    request: Request,
    service_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    手动触发健康检查
    
    - **service_name**: 服务名称（可选，不指定则检查所有服务）
    """
    if service_name:
        result = health_checker.run_check(service_name)
        return {
            "service": service_name,
            "status": result.status.value,
            "response_time": result.response_time,
            "details": result.details,
            "errors": result.errors,
            "timestamp": result.timestamp.isoformat()
        }
    else:
        results = health_checker.run_all_checks()
        return {
            "overall_status": health_checker.get_overall_health().value,
            "services": {
                name: {
                    "status": result.status.value,
                    "response_time": result.response_time,
                    "errors": result.errors
                }
                for name, result in results.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        } 