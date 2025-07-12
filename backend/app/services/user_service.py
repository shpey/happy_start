"""
用户服务层
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from loguru import logger

from ..core.security import security_manager
from ..models.user import User


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """创建新用户"""
        try:
            # 哈希密码
            hashed_password = security_manager.hash_password(user_data["password"])
            
            # 创建用户对象
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_password,
                full_name=user_data.get("full_name"),
                bio=user_data.get("bio"),
                avatar_url=user_data.get("avatar_url"),
                is_active=True,
                is_verified=False,
                is_premium=False,
                thinking_stats={
                    "total_analyses": 0,
                    "dominant_style": None,
                    "average_scores": {},
                    "improvement_trend": "stable"
                }
            )
            
            # 保存到数据库
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"用户创建成功: {user.username}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建用户失败: {e}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            user = self.db.query(User).filter(User.username == username).first()
            return user
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            user = self.db.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            raise
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """更新用户信息"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"用户信息更新成功: {user.username}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户信息失败: {e}")
            raise
    
    async def update_last_login(self, user_id: int) -> bool:
        """更新最后登录时间"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.last_login_at = datetime.utcnow()
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新最后登录时间失败: {e}")
            raise
    
    async def deactivate_user(self, user_id: int) -> bool:
        """禁用用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"用户已禁用: {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"禁用用户失败: {e}")
            raise
    
    async def activate_user(self, user_id: int) -> bool:
        """激活用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_active = True
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"用户已激活: {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"激活用户失败: {e}")
            raise
    
    async def verify_user(self, user_id: int) -> bool:
        """验证用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_verified = True
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"用户已验证: {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"验证用户失败: {e}")
            raise
    
    async def upgrade_to_premium(self, user_id: int) -> bool:
        """升级为高级用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_premium = True
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"用户已升级为高级用户: {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"升级高级用户失败: {e}")
            raise
    
    async def update_thinking_stats(self, user_id: int, analysis_result: Dict[str, Any]) -> bool:
        """更新用户思维统计"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.update_thinking_stats(analysis_result)
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"用户思维统计更新成功: {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户思维统计失败: {e}")
            raise
    
    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """搜索用户"""
        try:
            users = self.db.query(User).filter(
                or_(
                    User.username.contains(query),
                    User.full_name.contains(query)
                )
            ).filter(User.is_active == True).limit(limit).all()
            
            return users
            
        except Exception as e:
            logger.error(f"搜索用户失败: {e}")
            raise
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # 这里可以添加更多的统计信息
            stats = {
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                    "is_premium": user.is_premium,
                    "is_verified": user.is_verified
                },
                "thinking_stats": user.thinking_stats or {},
                "account_age_days": (datetime.utcnow() - user.created_at).days if user.created_at else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # 这里应该处理级联删除相关数据
            # 比如用户的思维分析记录、协作会话等
            
            self.db.delete(user)
            self.db.commit()
            
            logger.info(f"用户已删除: {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除用户失败: {e}")
            raise 