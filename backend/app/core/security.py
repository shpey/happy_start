"""
安全认证模块
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from loguru import logger
from functools import wraps
import time
import redis
from enum import Enum

from .config import settings


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


class TokenData(BaseModel):
    """JWT令牌数据模型"""
    user_id: int
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    exp: datetime


class SecurityAuditLog(BaseModel):
    """安全审计日志"""
    user_id: Optional[int]
    action: str
    resource: str
    ip_address: str
    timestamp: datetime
    success: bool
    details: Optional[Dict[str, Any]] = None


# 角色权限映射
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN, 
                    Permission.MODERATE, Permission.CREATE_ROOM, Permission.JOIN_ROOM, 
                    Permission.SHARE_THINKING],
    UserRole.MODERATOR: [Permission.READ, Permission.WRITE, Permission.MODERATE, 
                        Permission.CREATE_ROOM, Permission.JOIN_ROOM, Permission.SHARE_THINKING],
    UserRole.USER: [Permission.READ, Permission.WRITE, Permission.JOIN_ROOM, Permission.SHARE_THINKING],
    UserRole.GUEST: [Permission.READ, Permission.JOIN_ROOM]
}


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.redis_client = None
        self.rate_limit_max_requests = 100
        self.rate_limit_window = 3600  # 1小时
        
        # 初始化Redis连接
        try:
            import redis
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis连接失败，安全功能可能受限: {e}")
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    def get_user_permissions(self, role: UserRole) -> List[Permission]:
        """获取用户角色对应的权限"""
        return ROLE_PERMISSIONS.get(role, [])
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        user_role = UserRole(user_data.get("role", UserRole.USER))
        permissions = self.get_user_permissions(user_role)
        
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_role.value,
            "permissions": [p.value for p in permissions],
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow().timestamp()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # 将token存储到Redis（可选，用于黑名单功能）
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"token:{user_data['id']}:{token}",
                    self.access_token_expire_minutes * 60,
                    "valid"
                )
            except Exception as e:
                logger.warning(f"Token缓存失败: {e}")
        
        return token
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow().timestamp()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查token是否在黑名单中
            if self.redis_client and payload.get("type") == "access":
                try:
                    key = f"token:{payload['user_id']}:{token}"
                    if not self.redis_client.exists(key):
                        logger.warning("Token已失效或被撤销")
                        return None
                except Exception as e:
                    logger.warning(f"Token黑名单检查失败: {e}")
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效令牌")
            return None
    
    def revoke_token(self, token: str, user_id: int) -> bool:
        """撤销令牌"""
        if not self.redis_client:
            return False
        
        try:
            key = f"token:{user_id}:{token}"
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Token撤销失败: {e}")
            return False
    
    def check_rate_limit(self, user_id: int, action: str) -> bool:
        """检查速率限制"""
        if not self.redis_client:
            return True
        
        try:
            key = f"rate_limit:{user_id}:{action}"
            current_count = self.redis_client.get(key)
            
            if current_count is None:
                self.redis_client.setex(key, self.rate_limit_window, 1)
                return True
            
            if int(current_count) >= self.rate_limit_max_requests:
                return False
            
            self.redis_client.incr(key)
            return True
        except Exception as e:
            logger.warning(f"速率限制检查失败: {e}")
            return True
    
    def log_security_event(self, log: SecurityAuditLog):
        """记录安全事件"""
        logger.info(f"Security Event: {log.action} by user {log.user_id} from {log.ip_address} - {'Success' if log.success else 'Failed'}")
        
        # 将安全日志存储到Redis或数据库
        if self.redis_client:
            try:
                log_key = f"security_log:{datetime.now().isoformat()}:{log.user_id}"
                self.redis_client.setex(log_key, 86400 * 7, log.json())  # 保存7天
            except Exception as e:
                logger.warning(f"安全日志存储失败: {e}")
    
    def get_current_user_id(self, token: str) -> Optional[int]:
        """从令牌获取当前用户ID"""
        payload = self.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    def has_permission(self, user_permissions: List[str], required_permission: Permission) -> bool:
        """检查用户是否有指定权限"""
        return required_permission.value in user_permissions or Permission.ADMIN.value in user_permissions


# 全局安全管理器实例
security_manager = SecurityManager()

# HTTP Bearer认证
bearer_scheme = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Dict[str, Any]:
    """获取当前用户信息"""
    token = credentials.credentials
    payload = security_manager.verify_token(token)
    
    if not payload:
        # 记录失败的认证尝试
        security_manager.log_security_event(SecurityAuditLog(
            user_id=None,
            action="authentication_failed",
            resource="api_access",
            ip_address=request.client.host,
            timestamp=datetime.utcnow(),
            success=False,
            details={"reason": "invalid_token"}
        ))
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查速率限制
    if not security_manager.check_rate_limit(payload["user_id"], "api_access"):
        security_manager.log_security_event(SecurityAuditLog(
            user_id=payload["user_id"],
            action="rate_limit_exceeded",
            resource="api_access",
            ip_address=request.client.host,
            timestamp=datetime.utcnow(),
            success=False
        ))
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后重试"
        )
    
    return payload


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取当前活跃用户"""
    # 这里可以添加额外的用户状态检查
    return current_user


def require_permission(permission: Permission):
    """权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中获取request和current_user
            request = None
            current_user = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, dict) and "user_id" in arg:
                    current_user = arg
            
            # 从kwargs中获取
            if not request:
                request = kwargs.get("request")
            if not current_user:
                current_user = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要用户认证"
                )
            
            user_permissions = current_user.get("permissions", [])
            
            if not security_manager.has_permission(user_permissions, permission):
                # 记录权限检查失败
                if request:
                    security_manager.log_security_event(SecurityAuditLog(
                        user_id=current_user.get("user_id"),
                        action="permission_denied",
                        resource=f"{func.__name__}:{permission.value}",
                        ip_address=request.client.host,
                        timestamp=datetime.utcnow(),
                        success=False
                    ))
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有{permission.value}权限"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: UserRole):
    """角色装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中获取current_user
            current_user = None
            for arg in args:
                if isinstance(arg, dict) and "user_id" in arg:
                    current_user = arg
                    break
            
            if not current_user:
                current_user = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要用户认证"
                )
            
            user_role = current_user.get("role")
            if user_role != role.value and user_role != UserRole.ADMIN.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要{role.value}角色权限"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class PasswordValidator:
    """密码验证器"""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """验证密码强度"""
        errors = []
        
        if len(password) < 8:
            errors.append("密码长度至少8个字符")
        
        if not any(c.isupper() for c in password):
            errors.append("密码必须包含至少一个大写字母")
        
        if not any(c.islower() for c in password):
            errors.append("密码必须包含至少一个小写字母")
        
        if not any(c.isdigit() for c in password):
            errors.append("密码必须包含至少一个数字")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("密码必须包含至少一个特殊字符")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": "strong" if len(errors) == 0 else "weak"
        }


class EmailValidator:
    """邮箱验证器"""
    
    @staticmethod
    def validate_email(email: str) -> Dict[str, Any]:
        """验证邮箱格式"""
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        
        return {
            "is_valid": is_valid,
            "error": "邮箱格式不正确" if not is_valid else None
        }


class UsernameValidator:
    """用户名验证器"""
    
    @staticmethod
    def validate_username(username: str) -> Dict[str, Any]:
        """验证用户名格式"""
        import re
        
        errors = []
        
        if len(username) < 3:
            errors.append("用户名长度至少3个字符")
        
        if len(username) > 50:
            errors.append("用户名长度不能超过50个字符")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append("用户名只能包含字母、数字和下划线")
        
        if username[0].isdigit():
            errors.append("用户名不能以数字开头")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }


# 导出常用函数
__all__ = [
    "security_manager",
    "get_current_user",
    "get_current_active_user",
    "require_permission",
    "PasswordValidator",
    "EmailValidator",
    "UsernameValidator"
] 