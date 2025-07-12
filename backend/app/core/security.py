"""
安全认证模块
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from loguru import logger

from .config import settings


class TokenData(BaseModel):
    """JWT令牌数据模型"""
    user_id: int
    username: str
    email: str
    exp: datetime


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
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
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "exp": expire,
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "exp": expire,
            "type": "refresh"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效令牌")
            return None
    
    def get_current_user_id(self, token: str) -> Optional[int]:
        """从令牌获取当前用户ID"""
        payload = self.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None


# 全局安全管理器实例
security_manager = SecurityManager()

# HTTP Bearer认证
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Dict[str, Any]:
    """获取当前用户信息"""
    token = credentials.credentials
    payload = security_manager.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取当前活跃用户"""
    # 这里可以添加额外的用户状态检查
    return current_user


def require_permission(permission: str):
    """权限装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以添加权限检查逻辑
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