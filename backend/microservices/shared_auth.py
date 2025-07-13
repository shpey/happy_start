"""
微服务共享认证模块
用于统一各个微服务的认证和权限验证
"""

import jwt
import redis
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    MODERATOR = "moderator"


class Permission(str, Enum):
    """权限枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    MODERATE = "moderate"
    CREATE_ROOM = "create_room"
    JOIN_ROOM = "join_room"
    SHARE_THINKING = "share_thinking"
    AI_QUERY = "ai_query"
    BLOCKCHAIN_ACCESS = "blockchain_access"
    QUANTUM_COMPUTE = "quantum_compute"
    SEARCH_ADVANCED = "search_advanced"
    FEDERATED_LEARNING = "federated_learning"


class MicroserviceAuth:
    """微服务认证类"""
    
    def __init__(self, 
                 secret_key: str = "your-secret-key-change-this-in-production",
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 redis_password: str = "",
                 service_name: str = "unknown"):
        
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.service_name = service_name
        self.redis_client = None
        
        # 初始化Redis连接
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info(f"{service_name} Redis connection established")
        except Exception as e:
            logger.warning(f"{service_name} Redis connection failed: {e}")
            self.redis_client = None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查token是否在黑名单中
            if self.redis_client and payload.get("type") == "access":
                try:
                    key = f"token:{payload['user_id']}:{token}"
                    if not self.redis_client.exists(key):
                        logger.warning(f"{self.service_name}: Token已失效或被撤销")
                        return None
                except Exception as e:
                    logger.warning(f"{self.service_name}: Token黑名单检查失败: {e}")
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(f"{self.service_name}: 令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"{self.service_name}: 无效令牌: {e}")
            return None
    
    def has_permission(self, user_permissions: List[str], required_permission: Permission) -> bool:
        """检查用户是否有指定权限"""
        return (required_permission.value in user_permissions or 
                Permission.ADMIN.value in user_permissions)
    
    def log_auth_event(self, user_id: Optional[int], action: str, success: bool, details: str = ""):
        """记录认证事件"""
        log_message = f"{self.service_name} Auth: {action} by user {user_id} - {'Success' if success else 'Failed'}"
        if details:
            log_message += f" ({details})"
        
        if success:
            logger.info(log_message)
        else:
            logger.warning(log_message)
        
        # 记录到Redis
        if self.redis_client:
            try:
                event_key = f"auth_event:{self.service_name}:{datetime.now().isoformat()}:{user_id}"
                event_data = {
                    "service": self.service_name,
                    "user_id": user_id,
                    "action": action,
                    "success": success,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                }
                self.redis_client.setex(event_key, 86400, str(event_data))  # 保存24小时
            except Exception as e:
                logger.warning(f"{self.service_name}: 认证事件记录失败: {e}")


# 全局认证实例
auth_instances = {}

def get_microservice_auth(service_name: str) -> MicroserviceAuth:
    """获取微服务认证实例"""
    if service_name not in auth_instances:
        auth_instances[service_name] = MicroserviceAuth(service_name=service_name)
    return auth_instances[service_name]


# HTTP Bearer认证
security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service_name: str = "unknown"
) -> Dict[str, Any]:
    """获取当前用户信息（微服务版本）"""
    auth = get_microservice_auth(service_name)
    token = credentials.credentials
    payload = auth.verify_token(token)
    
    if not payload:
        auth.log_auth_event(
            user_id=None,
            action="authentication_failed",
            success=False,
            details="invalid_token"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth.log_auth_event(
        user_id=payload.get("user_id"),
        action="authentication_success",
        success=True
    )
    
    return payload


def require_permission_microservice(permission: Permission, service_name: str = "unknown"):
    """微服务权限装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            auth = get_microservice_auth(service_name)
            
            # 从参数中获取current_user
            current_user = None
            for arg in args:
                if isinstance(arg, dict) and "user_id" in arg:
                    current_user = arg
                    break
            
            if not current_user:
                current_user = kwargs.get("current_user")
            
            if not current_user:
                auth.log_auth_event(
                    user_id=None,
                    action="permission_check_failed",
                    success=False,
                    details="no_user_context"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要用户认证"
                )
            
            user_permissions = current_user.get("permissions", [])
            
            if not auth.has_permission(user_permissions, permission):
                auth.log_auth_event(
                    user_id=current_user.get("user_id"),
                    action="permission_denied",
                    success=False,
                    details=f"required_permission:{permission.value}"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有{permission.value}权限"
                )
            
            auth.log_auth_event(
                user_id=current_user.get("user_id"),
                action="permission_granted",
                success=True,
                details=f"permission:{permission.value}"
            )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role_microservice(role: UserRole, service_name: str = "unknown"):
    """微服务角色装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            auth = get_microservice_auth(service_name)
            
            # 从参数中获取current_user
            current_user = None
            for arg in args:
                if isinstance(arg, dict) and "user_id" in arg:
                    current_user = arg
                    break
            
            if not current_user:
                current_user = kwargs.get("current_user")
            
            if not current_user:
                auth.log_auth_event(
                    user_id=None,
                    action="role_check_failed",
                    success=False,
                    details="no_user_context"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要用户认证"
                )
            
            user_role = current_user.get("role")
            if user_role != role.value and user_role != UserRole.ADMIN.value:
                auth.log_auth_event(
                    user_id=current_user.get("user_id"),
                    action="role_check_failed",
                    success=False,
                    details=f"required_role:{role.value}, user_role:{user_role}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要{role.value}角色权限"
                )
            
            auth.log_auth_event(
                user_id=current_user.get("user_id"),
                action="role_check_success",
                success=True,
                details=f"role:{role.value}"
            )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 为不同微服务创建专用的认证函数
async def get_ai_service_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """AI服务用户认证"""
    return await get_current_user(request, credentials, "ai-service")


async def get_blockchain_service_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """区块链服务用户认证"""
    return await get_current_user(request, credentials, "blockchain-service")


async def get_quantum_service_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """量子计算服务用户认证"""
    return await get_current_user(request, credentials, "quantum-service")


async def get_search_service_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """搜索服务用户认证"""
    return await get_current_user(request, credentials, "search-service")


async def get_federated_learning_service_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """联邦学习服务用户认证"""
    return await get_current_user(request, credentials, "federated-learning-service")


async def get_graphql_service_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """GraphQL服务用户认证"""
    return await get_current_user(request, credentials, "graphql-service")


async def get_gateway_service_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """网关服务用户认证"""
    return await get_current_user(request, credentials, "gateway-service")


# 微服务权限装饰器快捷方式
def require_ai_permission(permission: Permission):
    return require_permission_microservice(permission, "ai-service")

def require_blockchain_permission(permission: Permission):
    return require_permission_microservice(permission, "blockchain-service")

def require_quantum_permission(permission: Permission):
    return require_permission_microservice(permission, "quantum-service")

def require_search_permission(permission: Permission):
    return require_permission_microservice(permission, "search-service")

def require_federated_learning_permission(permission: Permission):
    return require_permission_microservice(permission, "federated-learning-service")

def require_graphql_permission(permission: Permission):
    return require_permission_microservice(permission, "graphql-service")

def require_gateway_permission(permission: Permission):
    return require_permission_microservice(permission, "gateway-service") 