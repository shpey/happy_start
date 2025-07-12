"""
用户管理 API 端点
"""

from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session
from loguru import logger

from ....core.database import get_db
from ....core.security import (
    security_manager,
    get_current_user,
    get_current_active_user,
    PasswordValidator,
    EmailValidator,
    UsernameValidator
)
from ....models.user import User
from ....services.user_service import UserService

router = APIRouter()
bearer_scheme = HTTPBearer()


class UserRegisterRequest(BaseModel):
    """用户注册请求模型"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        result = UsernameValidator.validate_username(v)
        if not result["is_valid"]:
            raise ValueError("; ".join(result["errors"]))
        return v
    
    @validator('password')
    def validate_password(cls, v):
        result = PasswordValidator.validate_password(v)
        if not result["is_valid"]:
            raise ValueError("; ".join(result["errors"]))
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    is_premium: bool
    created_at: datetime
    thinking_stats: Dict[str, Any]


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class UserUpdateRequest(BaseModel):
    """用户更新请求模型"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """密码修改请求模型"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        result = PasswordValidator.validate_password(v)
        if not result["is_valid"]:
            raise ValueError("; ".join(result["errors"]))
        return v


@router.post("/register", response_model=LoginResponse)
async def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """用户注册"""
    try:
        user_service = UserService(db)
        
        # 检查用户名是否已存在
        if await user_service.get_user_by_username(request.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if await user_service.get_user_by_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建新用户
        user_data = {
            "username": request.username,
            "email": request.email,
            "password": request.password,
            "full_name": request.full_name
        }
        
        user = await user_service.create_user(user_data)
        
        # 生成令牌
        access_token = security_manager.create_access_token(user.to_dict())
        refresh_token = security_manager.create_refresh_token(user.to_dict())
        
        logger.info(f"用户注册成功: {user.username}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(**user.to_dict())
        )
        
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """用户登录"""
    try:
        user_service = UserService(db)
        
        # 根据用户名或邮箱查找用户
        user = await user_service.get_user_by_username(request.username)
        if not user:
            user = await user_service.get_user_by_email(request.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码
        if not security_manager.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账户已被禁用"
            )
        
        # 更新最后登录时间
        await user_service.update_last_login(user.id)
        
        # 生成令牌
        access_token = security_manager.create_access_token(user.to_dict())
        refresh_token = security_manager.create_refresh_token(user.to_dict())
        
        logger.info(f"用户登录成功: {user.username}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(**user.to_dict())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """获取当前用户信息"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserResponse(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    request: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """更新用户资料"""
    try:
        user_service = UserService(db)
        
        # 构建更新数据
        update_data = {}
        if request.full_name is not None:
            update_data["full_name"] = request.full_name
        if request.bio is not None:
            update_data["bio"] = request.bio
        if request.avatar_url is not None:
            update_data["avatar_url"] = request.avatar_url
        
        # 更新用户信息
        user = await user_service.update_user(current_user["user_id"], update_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        logger.info(f"用户资料更新成功: {user.username}")
        
        return UserResponse(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户资料失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户资料失败"
        )


@router.put("/me/password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """修改密码"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证当前密码
        if not security_manager.verify_password(request.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="当前密码错误"
            )
        
        # 更新密码
        new_password_hash = security_manager.hash_password(request.new_password)
        await user_service.update_user(user.id, {"hashed_password": new_password_hash})
        
        logger.info(f"用户密码修改成功: {user.username}")
        
        return {"success": True, "message": "密码修改成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )


@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """刷新访问令牌"""
    try:
        payload = security_manager.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        user_service = UserService(db)
        user = await user_service.get_user_by_id(payload["user_id"])
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # 生成新的访问令牌
        new_access_token = security_manager.create_access_token(user.to_dict())
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新令牌失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌失败"
        )


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """获取用户公开资料"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 返回公开信息（隐藏敏感信息）
        user_data = user.to_dict()
        user_data.pop("email", None)  # 隐藏邮箱
        
        return UserResponse(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户资料失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料失败"
        ) 