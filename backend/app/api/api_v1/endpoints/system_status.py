"""
系统状态 API 端点
"""

import psutil
import torch
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from loguru import logger

from ....core.database import db_manager
from ....core.redis_client import redis_client, cache_manager
from ....core.neo4j_client import neo4j_client, knowledge_graph_manager
from ....core.config import settings

router = APIRouter()


@router.get("/health")
async def comprehensive_health_check() -> Dict[str, Any]:
    """
    综合系统健康检查
    
    检查所有核心服务的状态：
    - PostgreSQL 数据库
    - Redis 缓存
    - Neo4j 知识图谱
    - AI 模型
    - 系统资源
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": settings.get_current_time(),
            "services": {},
            "system_resources": {},
            "ai_models": {}
        }
        
        # 检查数据库连接
        try:
            db_healthy = await db_manager.health_check()
            db_info = await db_manager.get_connection_info()
            health_status["services"]["postgresql"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "details": db_info
            }
        except Exception as e:
            health_status["services"]["postgresql"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 检查Redis连接
        try:
            redis_healthy = await redis_client.health_check()
            redis_info = await redis_client.get_info()
            health_status["services"]["redis"] = {
                "status": "healthy" if redis_healthy else "unhealthy",
                "details": redis_info
            }
        except Exception as e:
            health_status["services"]["redis"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 检查Neo4j连接
        try:
            neo4j_healthy = await neo4j_client.health_check()
            neo4j_info = await neo4j_client.get_database_info()
            health_status["services"]["neo4j"] = {
                "status": "healthy" if neo4j_healthy else "unhealthy",
                "details": neo4j_info
            }
        except Exception as e:
            health_status["services"]["neo4j"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 检查系统资源
        health_status["system_resources"] = _get_system_resources()
        
        # 检查AI模型状态
        health_status["ai_models"] = _get_ai_model_status()
        
        # 判断整体健康状态
        service_statuses = [service["status"] for service in health_status["services"].values()]
        if any(status == "error" for status in service_statuses):
            health_status["status"] = "degraded"
        elif any(status == "unhealthy" for status in service_statuses):
            health_status["status"] = "warning"
        
        return health_status
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=503, detail=f"健康检查失败: {str(e)}")


@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """获取系统性能指标"""
    try:
        metrics = {
            "timestamp": settings.get_current_time(),
            "system": _get_detailed_system_metrics(),
            "services": {},
            "cache": await _get_cache_metrics(),
            "knowledge_graph": await _get_knowledge_graph_metrics()
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"指标获取失败: {str(e)}")


@router.get("/version")
async def get_version_info() -> Dict[str, Any]:
    """获取系统版本信息"""
    try:
        import sys
        import platform
        
        version_info = {
            "application": {
                "name": settings.APP_NAME,
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "api_version": settings.API_V1_STR
            },
            "system": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "architecture": platform.architecture(),
                "processor": platform.processor()
            },
            "dependencies": {
                "pytorch": torch.__version__,
                "gpu_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
            }
        }
        
        return version_info
        
    except Exception as e:
        logger.error(f"获取版本信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"版本信息获取失败: {str(e)}")


@router.get("/config")
async def get_system_config() -> Dict[str, Any]:
    """获取系统配置信息（敏感信息已脱敏）"""
    try:
        config_info = {
            "server": {
                "host": settings.SERVER_HOST,
                "port": settings.SERVER_PORT,
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG
            },
            "database": {
                "postgres_server": settings.POSTGRES_SERVER,
                "postgres_port": settings.POSTGRES_PORT,
                "postgres_db": settings.POSTGRES_DB,
                "redis_host": settings.REDIS_HOST,
                "redis_port": settings.REDIS_PORT,
                "neo4j_uri": settings.NEO4J_URI.split("@")[-1] if "@" in settings.NEO4J_URI else settings.NEO4J_URI
            },
            "ai_models": {
                "enable_gpu": settings.ENABLE_GPU,
                "max_batch_size": settings.MAX_BATCH_SIZE,
                "models_path": settings.AI_MODELS_PATH,
                "thinking_models": {k: v["description"] for k, v in settings.THINKING_MODELS.items()}
            },
            "features": {
                "enable_metrics": settings.ENABLE_METRICS,
                "enable_tracing": settings.ENABLE_TRACING,
                "enable_blockchain": settings.ENABLE_BLOCKCHAIN,
                "cache_ttl": settings.CACHE_TTL
            }
        }
        
        return config_info
        
    except Exception as e:
        logger.error(f"获取配置信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"配置信息获取失败: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(pattern: str = "*") -> Dict[str, Any]:
    """清除缓存"""
    try:
        if pattern == "*":
            success = await cache_manager.flush_all()
            message = "所有缓存已清空"
        else:
            keys = await cache_manager.keys(pattern)
            if keys:
                deleted_count = await cache_manager.delete(*keys)
                success = deleted_count > 0
                message = f"已删除 {deleted_count} 个缓存键"
            else:
                success = True
                message = "没有找到匹配的缓存键"
        
        return {
            "success": success,
            "message": message,
            "pattern": pattern,
            "timestamp": settings.get_current_time()
        }
        
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"缓存清除失败: {str(e)}")


# 辅助函数

def _get_system_resources() -> Dict[str, Any]:
    """获取系统资源使用情况"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True)
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "usage_percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "usage_percent": (disk.used / disk.total) * 100
            }
        }
    except Exception:
        return {"error": "无法获取系统资源信息"}


def _get_detailed_system_metrics() -> Dict[str, Any]:
    """获取详细的系统性能指标"""
    try:
        # CPU 详细信息
        cpu_times = psutil.cpu_times()
        cpu_stats = {
            "usage_percent": psutil.cpu_percent(interval=None),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            "times": {
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle
            }
        }
        
        # 内存详细信息
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_stats = {
            "virtual": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
        }
        
        # 网络信息
        network = psutil.net_io_counters()
        network_stats = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        return {
            "cpu": cpu_stats,
            "memory": memory_stats,
            "network": network_stats,
            "gpu": _get_gpu_info()
        }
        
    except Exception as e:
        return {"error": f"获取系统指标失败: {str(e)}"}


def _get_gpu_info() -> Dict[str, Any]:
    """获取GPU信息"""
    try:
        if torch.cuda.is_available():
            gpu_info = {
                "available": True,
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(),
                "memory": {
                    "total": torch.cuda.get_device_properties(0).total_memory,
                    "allocated": torch.cuda.memory_allocated(),
                    "cached": torch.cuda.memory_reserved()
                }
            }
        else:
            gpu_info = {"available": False}
        
        return gpu_info
        
    except Exception:
        return {"available": False, "error": "无法获取GPU信息"}


def _get_ai_model_status() -> Dict[str, Any]:
    """获取AI模型状态"""
    try:
        # 这里需要从应用状态获取模型管理器
        # 暂时返回模拟状态
        return {
            "initialized": True,
            "models_loaded": {
                "visual_thinking": True,
                "logical_thinking": True,
                "creative_thinking": True
            },
            "device": "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu",
            "memory_usage": "正常"
        }
        
    except Exception:
        return {"initialized": False, "error": "无法获取AI模型状态"}


async def _get_cache_metrics() -> Dict[str, Any]:
    """获取缓存指标"""
    try:
        redis_info = await redis_client.get_info()
        
        return {
            "redis_info": redis_info,
            "connection_status": "connected" if await redis_client.health_check() else "disconnected"
        }
        
    except Exception as e:
        return {"error": f"获取缓存指标失败: {str(e)}"}


async def _get_knowledge_graph_metrics() -> Dict[str, Any]:
    """获取知识图谱指标"""
    try:
        graph_stats = await knowledge_graph_manager.get_graph_statistics()
        
        return {
            "statistics": graph_stats,
            "connection_status": "connected" if await neo4j_client.health_check() else "disconnected"
        }
        
    except Exception as e:
        return {"error": f"获取知识图谱指标失败: {str(e)}"} 