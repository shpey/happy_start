"""
Redis 客户端连接管理
"""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta

import redis.asyncio as redis
from loguru import logger

from .config import settings


class RedisClient:
    """Redis客户端管理器"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.pool: Optional[redis.ConnectionPool] = None
    
    async def connect(self) -> None:
        """建立Redis连接"""
        try:
            # 创建连接池
            self.pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                retry_on_timeout=True,
                decode_responses=False  # 支持二进制数据
            )
            
            # 创建Redis客户端
            self.redis = redis.Redis(connection_pool=self.pool)
            
            # 测试连接
            await self.redis.ping()
            logger.info(f"✅ Redis连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except Exception as e:
            logger.error(f"❌ Redis连接失败: {e}")
            raise
    
    async def disconnect(self) -> None:
        """关闭Redis连接"""
        try:
            if self.redis:
                await self.redis.close()
            if self.pool:
                await self.pool.disconnect()
            logger.info("✅ Redis连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭Redis连接失败: {e}")
    
    async def health_check(self) -> bool:
        """Redis健康检查"""
        try:
            if self.redis:
                await self.redis.ping()
                return True
            return False
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False
    
    async def get_info(self) -> dict:
        """获取Redis服务器信息"""
        try:
            if self.redis:
                info = await self.redis.info()
                return {
                    "version": info.get("redis_version"),
                    "mode": info.get("redis_mode"),
                    "connected_clients": info.get("connected_clients"),
                    "used_memory": info.get("used_memory_human"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "status": "connected"
                }
            return {"status": "disconnected"}
        except Exception as e:
            logger.error(f"获取Redis信息失败: {e}")
            return {"status": "error", "message": str(e)}


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.default_ttl = settings.CACHE_TTL
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: str = "json"
    ) -> bool:
        """设置缓存值"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return False
            
            # 序列化数据
            if serialize == "json":
                serialized_value = json.dumps(value, ensure_ascii=False)
            elif serialize == "pickle":
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = str(value)
            
            # 设置TTL
            expire_time = ttl or self.default_ttl
            
            await redis_conn.setex(key, expire_time, serialized_value)
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    async def get(
        self, 
        key: str, 
        default: Any = None,
        deserialize: str = "json"
    ) -> Any:
        """获取缓存值"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return default
            
            value = await redis_conn.get(key)
            if value is None:
                return default
            
            # 反序列化数据
            if deserialize == "json":
                return json.loads(value.decode('utf-8'))
            elif deserialize == "pickle":
                return pickle.loads(value)
            else:
                return value.decode('utf-8')
                
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return default
    
    async def delete(self, *keys: str) -> int:
        """删除缓存键"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return 0
            
            return await redis_conn.delete(*keys)
            
        except Exception as e:
            logger.error(f"删除缓存失败 {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return False
            
            return bool(await redis_conn.exists(key))
            
        except Exception as e:
            logger.error(f"检查缓存键失败 {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return False
            
            return bool(await redis_conn.expire(key, ttl))
            
        except Exception as e:
            logger.error(f"设置过期时间失败 {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return -1
            
            return await redis_conn.ttl(key)
            
        except Exception as e:
            logger.error(f"获取TTL失败 {key}: {e}")
            return -1
    
    async def keys(self, pattern: str = "*") -> list:
        """获取匹配模式的所有键"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return []
            
            keys = await redis_conn.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
            
        except Exception as e:
            logger.error(f"获取键列表失败 {pattern}: {e}")
            return []
    
    async def flush_all(self) -> bool:
        """清空所有缓存"""
        try:
            redis_conn = self.redis_client.redis
            if not redis_conn:
                return False
            
            await redis_conn.flushall()
            logger.info("✅ 所有缓存已清空")
            return True
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False


class SessionManager:
    """会话管理器"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
    
    async def create_session(self, session_id: str, user_id: str, data: dict) -> bool:
        """创建用户会话"""
        try:
            # 设置会话数据
            session_key = f"{self.session_prefix}{session_id}"
            session_data = {
                "user_id": user_id,
                "created_at": settings.get_current_time(),
                **data
            }
            
            # 设置会话（8小时过期）
            await self.cache.set(session_key, session_data, ttl=28800)
            
            # 添加到用户会话列表
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            existing_sessions = await self.cache.get(user_sessions_key, [])
            existing_sessions.append(session_id)
            await self.cache.set(user_sessions_key, existing_sessions, ttl=86400)
            
            return True
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话数据"""
        session_key = f"{self.session_prefix}{session_id}"
        return await self.cache.get(session_key)
    
    async def update_session(self, session_id: str, data: dict) -> bool:
        """更新会话数据"""
        try:
            session_key = f"{self.session_prefix}{session_id}"
            existing_data = await self.cache.get(session_key, {})
            existing_data.update(data)
            existing_data["updated_at"] = settings.get_current_time()
            
            return await self.cache.set(session_key, existing_data, ttl=28800)
            
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        try:
            session_key = f"{self.session_prefix}{session_id}"
            session_data = await self.cache.get(session_key)
            
            if session_data and "user_id" in session_data:
                # 从用户会话列表中移除
                user_id = session_data["user_id"]
                user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
                sessions = await self.cache.get(user_sessions_key, [])
                if session_id in sessions:
                    sessions.remove(session_id)
                    await self.cache.set(user_sessions_key, sessions, ttl=86400)
            
            # 删除会话数据
            await self.cache.delete(session_key)
            return True
            
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False


# 全局Redis客户端实例
redis_client = RedisClient()
cache_manager = CacheManager(redis_client)
session_manager = SessionManager(cache_manager)


async def init_redis() -> None:
    """初始化Redis连接"""
    await redis_client.connect()


async def close_redis() -> None:
    """关闭Redis连接"""
    await redis_client.disconnect() 