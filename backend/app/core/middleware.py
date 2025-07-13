"""
安全中间件模块
"""

import time
import re
import json
from typing import Dict, List, Optional, Set
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import ipaddress
from datetime import datetime, timedelta

from .security import security_manager, SecurityAuditLog


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        
        # 配置参数
        self.rate_limit_requests = kwargs.get("rate_limit_requests", 1000)
        self.rate_limit_window = kwargs.get("rate_limit_window", 3600)  # 1小时
        self.enable_ip_whitelist = kwargs.get("enable_ip_whitelist", False)
        self.ip_whitelist: Set[str] = set(kwargs.get("ip_whitelist", []))
        self.blocked_ips: Set[str] = set()
        self.enable_sql_injection_protection = kwargs.get("enable_sql_injection_protection", True)
        self.enable_xss_protection = kwargs.get("enable_xss_protection", True)
        
        # 请求统计
        self.request_counts: Dict[str, List[float]] = {}
        
        # SQL注入检测模式
        self.sql_injection_patterns = [
            r"(\s*(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+)",
            r"(\s*(or|and)\s+\d+\s*=\s*\d+)",
            r"(\s*(\'|\").*(\-\-|\#))",
            r"(\s*\'.*\s+(or|and)\s+.*\')",
            r"(\s*\"\s*(or|and)\s+.*\")",
            r"(\s*(exec|sp_|xp_)\w+)",
        ]
        
        # XSS检测模式
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
        ]
        
        # 编译正则表达式
        self.compiled_sql_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_injection_patterns]
        self.compiled_xss_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        start_time = time.time()
        client_ip = self.get_client_ip(request)
        
        try:
            # 1. IP白名单检查
            if self.enable_ip_whitelist and not self.check_ip_whitelist(client_ip):
                logger.warning(f"IP {client_ip} not in whitelist")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "访问被拒绝"}
                )
            
            # 2. IP黑名单检查
            if client_ip in self.blocked_ips:
                logger.warning(f"Blocked IP {client_ip} attempted access")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "IP已被封禁"}
                )
            
            # 3. 速率限制检查
            if not self.check_rate_limit(client_ip):
                # 记录速率限制事件
                security_manager.log_security_event(SecurityAuditLog(
                    user_id=None,
                    action="rate_limit_exceeded",
                    resource=str(request.url),
                    ip_address=client_ip,
                    timestamp=datetime.utcnow(),
                    success=False
                ))
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "请求过于频繁，请稍后重试"}
                )
            
            # 4. 安全检查（SQL注入、XSS等）
            security_issues = await self.check_security_issues(request)
            if security_issues:
                # 记录安全威胁
                security_manager.log_security_event(SecurityAuditLog(
                    user_id=None,
                    action="security_threat_detected",
                    resource=str(request.url),
                    ip_address=client_ip,
                    timestamp=datetime.utcnow(),
                    success=False,
                    details={"issues": security_issues}
                ))
                
                # 严重威胁时临时封禁IP
                if any(issue["severity"] == "high" for issue in security_issues):
                    self.blocked_ips.add(client_ip)
                    logger.error(f"High security threat detected from {client_ip}, IP blocked")
                
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "检测到潜在安全威胁"}
                )
            
            # 5. 处理请求
            response = await call_next(request)
            
            # 6. 添加安全响应头
            response = self.add_security_headers(response)
            
            # 7. 记录请求日志
            process_time = time.time() - start_time
            await self.log_request(request, response, client_ip, process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # 记录中间件错误
            security_manager.log_security_event(SecurityAuditLog(
                user_id=None,
                action="middleware_error",
                resource=str(request.url),
                ip_address=client_ip,
                timestamp=datetime.utcnow(),
                success=False,
                details={"error": str(e)}
            ))
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "服务器错误"}
            )
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    def check_ip_whitelist(self, ip: str) -> bool:
        """检查IP是否在白名单中"""
        if not self.ip_whitelist:
            return True
        
        try:
            client_ip = ipaddress.ip_address(ip)
            for allowed_ip in self.ip_whitelist:
                if "/" in allowed_ip:
                    # CIDR网段
                    if client_ip in ipaddress.ip_network(allowed_ip, strict=False):
                        return True
                else:
                    # 单个IP
                    if client_ip == ipaddress.ip_address(allowed_ip):
                        return True
            return False
        except ValueError:
            logger.warning(f"Invalid IP address: {ip}")
            return False
    
    def check_rate_limit(self, ip: str) -> bool:
        """检查速率限制"""
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # 清理过期记录
        if ip in self.request_counts:
            self.request_counts[ip] = [
                req_time for req_time in self.request_counts[ip]
                if req_time > window_start
            ]
        else:
            self.request_counts[ip] = []
        
        # 检查是否超过限制
        if len(self.request_counts[ip]) >= self.rate_limit_requests:
            return False
        
        # 记录本次请求
        self.request_counts[ip].append(now)
        return True
    
    async def check_security_issues(self, request: Request) -> List[Dict]:
        """检查安全问题"""
        issues = []
        
        # 获取请求数据
        url = str(request.url)
        method = request.method
        headers = dict(request.headers)
        
        # 获取请求体
        body = ""
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                body = body_bytes.decode("utf-8") if body_bytes else ""
            except Exception:
                body = ""
        
        # 检查查询参数
        query_params = str(request.query_params)
        
        # 所有需要检查的文本
        check_texts = [url, query_params, body]
        
        # SQL注入检查
        if self.enable_sql_injection_protection:
            for text in check_texts:
                if text:
                    for pattern in self.compiled_sql_patterns:
                        if pattern.search(text):
                            issues.append({
                                "type": "sql_injection",
                                "severity": "high",
                                "location": "request_data",
                                "pattern": pattern.pattern
                            })
                            break
        
        # XSS检查
        if self.enable_xss_protection:
            for text in check_texts:
                if text:
                    for pattern in self.compiled_xss_patterns:
                        if pattern.search(text):
                            issues.append({
                                "type": "xss",
                                "severity": "medium",
                                "location": "request_data",
                                "pattern": pattern.pattern
                            })
                            break
        
        # 检查可疑的User-Agent
        user_agent = headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nmap", "nikto", "dirb", "gobuster", "burp"]
        if any(agent in user_agent for agent in suspicious_agents):
            issues.append({
                "type": "suspicious_user_agent",
                "severity": "medium",
                "location": "headers",
                "value": user_agent
            })
        
        # 检查路径遍历攻击
        if "../" in url or "..%2f" in url.lower() or "..%5c" in url.lower():
            issues.append({
                "type": "path_traversal",
                "severity": "high",
                "location": "url",
                "value": url
            })
        
        return issues
    
    def add_security_headers(self, response: Response) -> Response:
        """添加安全响应头"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' ws: wss:; "
                "frame-ancestors 'none';"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "accelerometer=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "payment=()"
            )
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    async def log_request(self, request: Request, response: Response, client_ip: str, process_time: float):
        """记录请求日志"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", "")
        }
        
        # 记录到日志
        if response.status_code >= 400:
            logger.warning(f"HTTP {response.status_code} - {log_data}")
        else:
            logger.info(f"HTTP {response.status_code} - {request.method} {request.url.path} - {process_time:.4f}s")


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """CORS安全中间件"""
    
    def __init__(self, app, allowed_origins: List[str] = None, **kwargs):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins or ["*"])
        self.allow_credentials = kwargs.get("allow_credentials", True)
        self.allowed_methods = kwargs.get("allowed_methods", ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        self.allowed_headers = kwargs.get("allowed_headers", ["*"])
        self.max_age = kwargs.get("max_age", 86400)
    
    async def dispatch(self, request: Request, call_next):
        """处理CORS"""
        origin = request.headers.get("origin")
        
        # 预检请求处理
        if request.method == "OPTIONS":
            response = Response()
            if origin and self.is_origin_allowed(origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
                response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
                response.headers["Access-Control-Max-Age"] = str(self.max_age)
                if self.allow_credentials:
                    response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # 处理实际请求
        response = await call_next(request)
        
        # 添加CORS头
        if origin and self.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    
    def is_origin_allowed(self, origin: str) -> bool:
        """检查origin是否被允许"""
        if "*" in self.allowed_origins:
            return True
        return origin in self.allowed_origins 