"""
系统监控模块
提供性能监控、健康检查、错误追踪等功能
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import contextmanager
import redis
import json

from .config import settings


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ServiceStatus(str, Enum):
    """服务状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class PerformanceMetric:
    """性能指标"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    response_time_avg: float
    requests_per_second: float
    error_rate: float


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    service_name: str
    status: ServiceStatus
    timestamp: datetime
    response_time: float
    details: Dict[str, Any]
    errors: List[str]


@dataclass
class Alert:
    """告警信息"""
    id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    service: str
    metric: str
    value: Any
    threshold: Any
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, window_size: int = 300):  # 5分钟窗口
        self.window_size = window_size
        self.metrics_history = deque(maxlen=window_size)
        self.request_times = deque(maxlen=1000)  # 最近1000个请求
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.last_network_io = psutil.net_io_counters()
        self.alerts = []
        self.lock = threading.Lock()
        
        # 阈值配置
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time_avg": 2.0,  # 2秒
            "error_rate": 0.05  # 5%
        }
        
        # Redis连接（用于集群监控）
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        except Exception:
            self.redis_client = None
    
    def collect_metrics(self) -> PerformanceMetric:
        """收集性能指标"""
        now = datetime.utcnow()
        
        # CPU和内存
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # 网络IO
        network_io = psutil.net_io_counters()
        network_bytes_sent = network_io.bytes_sent - self.last_network_io.bytes_sent
        network_bytes_recv = network_io.bytes_recv - self.last_network_io.bytes_recv
        self.last_network_io = network_io
        
        # 网络连接数
        try:
            connections = len(psutil.net_connections())
        except Exception:
            connections = 0
        
        # 请求性能指标
        with self.lock:
            response_time_avg = (
                sum(self.request_times) / len(self.request_times)
                if self.request_times else 0
            )
            
            uptime = time.time() - self.start_time
            requests_per_second = self.request_count / uptime if uptime > 0 else 0
            error_rate = self.error_count / self.request_count if self.request_count > 0 else 0
        
        metric = PerformanceMetric(
            timestamp=now,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            disk_percent=disk_percent,
            network_bytes_sent=network_bytes_sent,
            network_bytes_recv=network_bytes_recv,
            active_connections=connections,
            response_time_avg=response_time_avg,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )
        
        self.metrics_history.append(metric)
        self.check_thresholds(metric)
        
        # 发送到Redis集群监控
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"metrics:{settings.PROJECT_NAME}",
                    60,  # 1分钟过期
                    json.dumps(asdict(metric), default=str)
                )
            except Exception:
                pass
        
        return metric
    
    def record_request(self, response_time: float, success: bool = True):
        """记录请求"""
        with self.lock:
            self.request_times.append(response_time)
            self.request_count += 1
            if not success:
                self.error_count += 1
    
    def check_thresholds(self, metric: PerformanceMetric):
        """检查阈值并产生告警"""
        checks = [
            ("cpu_percent", metric.cpu_percent, "CPU使用率"),
            ("memory_percent", metric.memory_percent, "内存使用率"),
            ("disk_percent", metric.disk_percent, "磁盘使用率"),
            ("response_time_avg", metric.response_time_avg, "平均响应时间"),
            ("error_rate", metric.error_rate, "错误率")
        ]
        
        for metric_name, value, display_name in checks:
            threshold = self.thresholds.get(metric_name)
            if threshold and value > threshold:
                self.create_alert(
                    level=AlertLevel.WARNING if value < threshold * 1.2 else AlertLevel.ERROR,
                    title=f"{display_name}过高",
                    message=f"{display_name}达到 {value:.2f}，超过阈值 {threshold}",
                    service="system",
                    metric=metric_name,
                    value=value,
                    threshold=threshold
                )
    
    def create_alert(self, level: AlertLevel, title: str, message: str, 
                    service: str, metric: str, value: Any, threshold: Any):
        """创建告警"""
        alert_id = f"{service}_{metric}_{int(time.time())}"
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            timestamp=datetime.utcnow(),
            service=service,
            metric=metric,
            value=value,
            threshold=threshold
        )
        
        self.alerts.append(alert)
        
        # 限制告警数量
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # 记录到日志
        logging.warning(f"ALERT [{level.value.upper()}] {title}: {message}")
    
    def get_current_metrics(self) -> Optional[PerformanceMetric]:
        """获取当前指标"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, minutes: int = 60) -> List[PerformanceMetric]:
        """获取历史指标"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff]
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return [a for a in self.alerts if not a.resolved]
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                break


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks = {}
        self.results_history = defaultdict(lambda: deque(maxlen=100))
    
    def register_check(self, name: str, check_func: callable, interval: int = 60):
        """注册健康检查"""
        self.checks[name] = {
            "func": check_func,
            "interval": interval,
            "last_check": 0
        }
    
    def run_check(self, name: str) -> HealthCheckResult:
        """运行单个健康检查"""
        if name not in self.checks:
            return HealthCheckResult(
                service_name=name,
                status=ServiceStatus.UNKNOWN,
                timestamp=datetime.utcnow(),
                response_time=0,
                details={},
                errors=["未注册的健康检查"]
            )
        
        check = self.checks[name]
        start_time = time.time()
        
        try:
            result = check["func"]()
            response_time = time.time() - start_time
            
            # 确定状态
            if isinstance(result, dict):
                status = ServiceStatus(result.get("status", ServiceStatus.HEALTHY))
                details = result.get("details", {})
                errors = result.get("errors", [])
            else:
                status = ServiceStatus.HEALTHY if result else ServiceStatus.UNHEALTHY
                details = {}
                errors = [] if result else ["健康检查失败"]
            
            health_result = HealthCheckResult(
                service_name=name,
                status=status,
                timestamp=datetime.utcnow(),
                response_time=response_time,
                details=details,
                errors=errors
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            health_result = HealthCheckResult(
                service_name=name,
                status=ServiceStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                response_time=response_time,
                details={},
                errors=[str(e)]
            )
        
        # 更新检查时间
        check["last_check"] = time.time()
        
        # 保存结果
        self.results_history[name].append(health_result)
        
        return health_result
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """运行所有健康检查"""
        results = {}
        current_time = time.time()
        
        for name, check in self.checks.items():
            # 检查是否需要运行
            if current_time - check["last_check"] >= check["interval"]:
                results[name] = self.run_check(name)
            else:
                # 返回最近的结果
                history = self.results_history[name]
                if history:
                    results[name] = history[-1]
        
        return results
    
    def get_overall_health(self) -> ServiceStatus:
        """获取整体健康状态"""
        results = self.run_all_checks()
        
        if not results:
            return ServiceStatus.UNKNOWN
        
        statuses = [result.status for result in results.values()]
        
        if all(s == ServiceStatus.HEALTHY for s in statuses):
            return ServiceStatus.HEALTHY
        elif any(s == ServiceStatus.UNHEALTHY for s in statuses):
            return ServiceStatus.UNHEALTHY
        else:
            return ServiceStatus.DEGRADED


# 全局监控实例
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()


@contextmanager
def monitor_request():
    """请求监控上下文管理器"""
    start_time = time.time()
    success = True
    
    try:
        yield
    except Exception:
        success = False
        raise
    finally:
        response_time = time.time() - start_time
        performance_monitor.record_request(response_time, success)


def register_default_health_checks():
    """注册默认健康检查"""
    
    def check_database():
        """检查数据库连接"""
        try:
            from .database import get_db
            db = next(get_db())
            db.execute("SELECT 1")
            return {"status": ServiceStatus.HEALTHY, "details": {"connection": "ok"}}
        except Exception as e:
            return {"status": ServiceStatus.UNHEALTHY, "errors": [str(e)]}
    
    def check_redis():
        """检查Redis连接"""
        try:
            from .redis_client import redis_client
            redis_client.ping()
            return {"status": ServiceStatus.HEALTHY, "details": {"connection": "ok"}}
        except Exception as e:
            return {"status": ServiceStatus.UNHEALTHY, "errors": [str(e)]}
    
    def check_disk_space():
        """检查磁盘空间"""
        try:
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100
            
            if free_percent < 10:
                status = ServiceStatus.UNHEALTHY
            elif free_percent < 20:
                status = ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.HEALTHY
            
            return {
                "status": status,
                "details": {
                    "free_percent": free_percent,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                    "total_gb": disk.total / 1024 / 1024 / 1024
                }
            }
        except Exception as e:
            return {"status": ServiceStatus.UNHEALTHY, "errors": [str(e)]}
    
    def check_memory():
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = ServiceStatus.UNHEALTHY
            elif memory.percent > 80:
                status = ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.HEALTHY
            
            return {
                "status": status,
                "details": {
                    "percent": memory.percent,
                    "available_gb": memory.available / 1024 / 1024 / 1024,
                    "total_gb": memory.total / 1024 / 1024 / 1024
                }
            }
        except Exception as e:
            return {"status": ServiceStatus.UNHEALTHY, "errors": [str(e)]}
    
    # 注册健康检查
    health_checker.register_check("database", check_database, 30)
    health_checker.register_check("redis", check_redis, 30)
    health_checker.register_check("disk", check_disk_space, 60)
    health_checker.register_check("memory", check_memory, 30)


# 启动时注册默认健康检查
register_default_health_checks()


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.custom_metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """增加计数器"""
        key = self._make_key(name, tags)
        self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """设置仪表值"""
        key = self._make_key(name, tags)
        self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录直方图值"""
        key = self._make_key(name, tags)
        self.histograms[key].append(value)
        
        # 限制直方图大小
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
    
    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """生成指标键"""
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{name},{tag_str}"
        return name
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        summary = {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {}
        }
        
        # 计算直方图统计
        for key, values in self.histograms.items():
            if values:
                summary["histograms"][key] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p50": self._percentile(values, 0.5),
                    "p95": self._percentile(values, 0.95),
                    "p99": self._percentile(values, 0.99)
                }
        
        return summary
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """计算百分位数"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


# 全局指标收集器
metrics_collector = MetricsCollector() 