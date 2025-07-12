"""
用户服务层
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from ..core.config import settings
from ..core.database import get_db
from ..models.user import User
from ..core.redis_client import cache_manager, session_manager

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户服务类"""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            result = await db.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    async def create_user(
        self, 
        db: AsyncSession, 
        username: str, 
        email: str, 
        password: str,
        full_name: Optional[str] = None
    ) -> Optional[User]:
        """创建新用户"""
        try:
            # 检查用户名是否已存在
            existing_user = await self.get_user_by_username(db, username)
            if existing_user:
                raise ValueError("用户名已存在")
            
            # 检查邮箱是否已存在
            existing_email = await self.get_user_by_email(db, email)
            if existing_email:
                raise ValueError("邮箱已存在")
            
            # 创建新用户
            hashed_password = self.get_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name or username,
                is_active=True
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"创建用户成功: {username}")
            return new_user
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建用户失败: {e}")
            raise
    
    async def authenticate_user(
        self, 
        db: AsyncSession, 
        username: str, 
        password: str
    ) -> Optional[User]:
        """验证用户身份"""
        try:
            user = await self.get_user_by_username(db, username)
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            # 更新最后登录时间
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(last_login_at=datetime.utcnow())
            )
            await db.commit()
            
            return user
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    async def update_user_profile(
        self,
        db: AsyncSession,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[User]:
        """更新用户资料"""
        try:
            user = await self.get_user_by_id(db, user_id)
            if not user:
                return None
            
            # 更新允许的字段
            allowed_fields = ['full_name', 'bio', 'avatar_url', 'preferences']
            for field, value in update_data.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"更新用户资料成功: {user_id}")
            return user
            
        except Exception as e:
            await db.rollback()
            logger.error(f"更新用户资料失败: {e}")
            return None
    
    async def update_user_thinking_stats(
        self,
        db: AsyncSession,
        user_id: int,
        analysis_result: Dict[str, Any]
    ) -> bool:
        """更新用户思维统计"""
        try:
            user = await self.get_user_by_id(db, user_id)
            if not user:
                return False
            
            user.update_thinking_stats(analysis_result)
            await db.commit()
            
            logger.info(f"更新思维统计成功: {user_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"更新思维统计失败: {e}")
            return False
    
    async def create_user_session(
        self,
        user_id: int,
        session_data: Dict[str, Any] = None
    ) -> str:
        """创建用户会话"""
        try:
            session_id = secrets.token_urlsafe(32)
            
            # 会话数据
            session_info = {
                "user_id": user_id,
                "created_at": settings.get_current_time(),
                **(session_data or {})
            }
            
            # 在Redis中创建会话
            success = await session_manager.create_session(session_id, str(user_id), session_info)
            
            if success:
                logger.info(f"创建用户会话成功: {user_id}")
                return session_id
            else:
                raise Exception("会话创建失败")
                
        except Exception as e:
            logger.error(f"创建用户会话失败: {e}")
            raise
    
    async def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取用户会话"""
        try:
            return await session_manager.get_session(session_id)
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            return None
    
    async def delete_user_session(self, session_id: str) -> bool:
        """删除用户会话"""
        try:
            return await session_manager.delete_session(session_id)
        except Exception as e:
            logger.error(f"删除用户会话失败: {e}")
            return False
    
    async def get_user_statistics(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取用户统计信息"""
        try:
            user = await self.get_user_by_id(db, user_id)
            if not user:
                return None
            
            # 基础统计
            stats = {
                "user_info": user.to_dict(),
                "thinking_stats": user.thinking_stats or {},
                "account_stats": {
                    "days_since_registration": (datetime.utcnow() - user.created_at).days if user.created_at else 0,
                    "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
                    "is_premium": user.is_premium,
                    "is_verified": user.is_verified
                }
            }
            
            # 缓存结果
            cache_key = f"user_stats:{user_id}"
            await cache_manager.set(cache_key, stats, ttl=1800)  # 30分钟缓存
            
            return stats
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return None
    
    async def search_users(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """搜索用户"""
        try:
            # 简单的用户名搜索
            result = await db.execute(
                select(User)
                .where(User.username.ilike(f"%{query}%"))
                .where(User.is_active == True)
                .limit(limit)
            )
            users = result.scalars().all()
            
            # 返回公开信息
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "bio": user.bio
                }
                for user in users
            ]
            
        except Exception as e:
            logger.error(f"搜索用户失败: {e}")
            return []


# 全局用户服务实例
user_service = UserService() 