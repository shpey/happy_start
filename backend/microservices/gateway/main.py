"""
API Gateway Service
统一的微服务入口点，处理路由、负载均衡、认证等
"""

import asyncio
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import consul
import json
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel
import time
import hashlib
import jwt
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceRegistry:
    """服务注册与发现"""
    
    def __init__(self):
        self.consul = consul.Consul()
        self.services = {}
    
    async def register_service(self, service_name: str, host: str, port: int, health_check_url: str):
        """注册服务"""
        try:
            self.consul.agent.service.register(
                name=service_name,
                service_id=f"{service_name}-{port}",
                address=host,
                port=port,
                check=consul.Check.http(health_check_url, interval="10s")
            )
            logger.info(f"Service {service_name} registered successfully")
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")
    
    async def discover_services(self, service_name: str) -> List[Dict]:
        """发现服务"""
        try:
            services = self.consul.health.service(service_name, passing=True)[1]
            return [
                {
                    "host": service["Service"]["Address"],
                    "port": service["Service"]["Port"]
                }
                for service in services
            ]
        except Exception as e:
            logger.error(f"Failed to discover service {service_name}: {e}")
            return []

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self.service_counters = {}
    
    def round_robin(self, services: List[Dict]) -> Optional[Dict]:
        """轮询负载均衡"""
        if not services:
            return None
        
        service_key = f"{services[0]['host']}:{services[0]['port']}"
        if service_key not in self.service_counters:
            self.service_counters[service_key] = 0
        
        selected = services[self.service_counters[service_key] % len(services)]
        self.service_counters[service_key] += 1
        return selected
    
    def weighted_round_robin(self, services: List[Dict], weights: List[int]) -> Optional[Dict]:
        """加权轮询负载均衡"""
        if not services or not weights:
            return None
        
        total_weight = sum(weights)
        if total_weight == 0:
            return self.round_robin(services)
        
        # 简化的加权轮询实现
        import random
        weight_sum = 0
        rand_num = random.randint(1, total_weight)
        
        for i, weight in enumerate(weights):
            weight_sum += weight
            if rand_num <= weight_sum:
                return services[i]
        
        return services[0]

class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self.clients = {}
    
    def is_allowed(self, client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """检查是否允许请求"""
        now = time.time()
        window_start = now - window_seconds
        
        if client_id not in self.clients:
            self.clients[client_id] = []
        
        # 清理过期的请求记录
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id] 
            if req_time > window_start
        ]
        
        if len(self.clients[client_id]) >= max_requests:
            return False
        
        self.clients[client_id].append(now)
        return True

class APIGateway:
    """API网关主类"""
    
    def __init__(self):
        self.app = FastAPI(
            title="智能思维平台 - API Gateway",
            description="微服务架构的统一API入口",
            version="2.0.0"
        )
        
        self.service_registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.rate_limiter = RateLimiter()
        
        # 服务路由配置
        self.service_routes = {
            "/api/v1/auth": "auth-service",
            "/api/v1/thinking": "thinking-service",
            "/api/v1/collaboration": "collaboration-service",
            "/api/v1/ai": "ai-service",
            "/api/v1/blockchain": "blockchain-service",
            "/api/v1/analytics": "analytics-service"
        }
        
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        """设置中间件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/services")
        async def list_services():
            """列出所有已注册的服务"""
            services = {}
            for route, service_name in self.service_routes.items():
                available_services = await self.service_registry.discover_services(service_name)
                services[service_name] = {
                    "route": route,
                    "instances": len(available_services),
                    "endpoints": available_services
                }
            return services
        
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def route_request(request: Request, path: str):
            """路由请求到相应的微服务"""
            
            # 获取客户端IP
            client_ip = request.client.host
            
            # 速率限制检查
            if not self.rate_limiter.is_allowed(client_ip):
                raise HTTPException(status_code=429, detail="Too Many Requests")
            
            # 确定目标服务
            target_service = None
            for route_prefix, service_name in self.service_routes.items():
                if f"/{path}".startswith(route_prefix):
                    target_service = service_name
                    break
            
            if not target_service:
                raise HTTPException(status_code=404, detail="Service not found")
            
            # 发现服务实例
            service_instances = await self.service_registry.discover_services(target_service)
            if not service_instances:
                raise HTTPException(status_code=503, detail="Service unavailable")
            
            # 负载均衡选择实例
            selected_instance = self.load_balancer.round_robin(service_instances)
            if not selected_instance:
                raise HTTPException(status_code=503, detail="No available service instance")
            
            # 转发请求
            target_url = f"http://{selected_instance['host']}:{selected_instance['port']}/{path}"
            
            async with httpx.AsyncClient() as client:
                try:
                    # 准备请求参数
                    request_params = {
                        "method": request.method,
                        "url": target_url,
                        "headers": dict(request.headers),
                        "params": dict(request.query_params)
                    }
                    
                    # 如果有请求体，添加到参数中
                    if request.method in ["POST", "PUT", "PATCH"]:
                        request_params["content"] = await request.body()
                    
                    # 发送请求
                    response = await client.request(**request_params)
                    
                    # 返回响应
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                    
                except httpx.RequestError as e:
                    logger.error(f"Request failed: {e}")
                    raise HTTPException(status_code=502, detail="Bad Gateway")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    raise HTTPException(status_code=500, detail="Internal Server Error")

    async def startup(self):
        """启动时初始化"""
        logger.info("API Gateway starting up...")
        
        # 注册默认服务（如果需要）
        await self.service_registry.register_service(
            "api-gateway",
            "localhost",
            8080,
            "http://localhost:8080/health"
        )
        
        logger.info("API Gateway started successfully")
    
    async def shutdown(self):
        """关闭时清理"""
        logger.info("API Gateway shutting down...")

# 创建全局实例
gateway = APIGateway()
app = gateway.app

# 生命周期事件
@app.on_event("startup")
async def startup_event():
    await gateway.startup()

@app.on_event("shutdown")
async def shutdown_event():
    await gateway.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 