"""
WebSocket服务层
处理实时协作功能
"""

import json
import asyncio
import uuid
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from ..core.database import get_db
from ..models.collaboration import CollaborationSession, UserSession, SessionEvent, UserRole
from ..models.user import User
from ..core.redis_client import cache_manager
from ..services.user_service import user_service


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接字典 {socket_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # 用户连接映射 {user_id: set(socket_ids)}
        self.user_connections: Dict[int, Set[str]] = {}
        
        # 房间连接映射 {room_id: set(socket_ids)}
        self.room_connections: Dict[str, Set[str]] = {}
        
        # 连接元数据 {socket_id: connection_info}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        user_id: int, 
        room_id: Optional[str] = None
    ) -> str:
        """建立WebSocket连接"""
        await websocket.accept()
        
        # 生成连接ID
        socket_id = str(uuid.uuid4())
        
        # 保存连接
        self.active_connections[socket_id] = websocket
        
        # 更新用户连接映射
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(socket_id)
        
        # 更新房间连接映射
        if room_id:
            if room_id not in self.room_connections:
                self.room_connections[room_id] = set()
            self.room_connections[room_id].add(socket_id)
        
        # 保存连接元数据
        self.connection_metadata[socket_id] = {
            "user_id": user_id,
            "room_id": room_id,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        logger.info(f"WebSocket连接建立: socket_id={socket_id}, user_id={user_id}, room_id={room_id}")
        return socket_id
    
    def disconnect(self, socket_id: str):
        """断开WebSocket连接"""
        if socket_id not in self.active_connections:
            return
        
        metadata = self.connection_metadata.get(socket_id, {})
        user_id = metadata.get("user_id")
        room_id = metadata.get("room_id")
        
        # 移除连接
        del self.active_connections[socket_id]
        
        # 更新用户连接映射
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(socket_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # 更新房间连接映射
        if room_id and room_id in self.room_connections:
            self.room_connections[room_id].discard(socket_id)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
        
        # 移除元数据
        if socket_id in self.connection_metadata:
            del self.connection_metadata[socket_id]
        
        logger.info(f"WebSocket连接断开: socket_id={socket_id}, user_id={user_id}, room_id={room_id}")
    
    async def send_personal_message(self, socket_id: str, message: Dict[str, Any]):
        """发送个人消息"""
        if socket_id in self.active_connections:
            try:
                websocket = self.active_connections[socket_id]
                await websocket.send_text(json.dumps(message))
                
                # 更新活跃时间
                if socket_id in self.connection_metadata:
                    self.connection_metadata[socket_id]["last_activity"] = datetime.utcnow().isoformat()
                    
            except Exception as e:
                logger.error(f"发送个人消息失败: {e}")
                self.disconnect(socket_id)
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """发送消息给指定用户的所有连接"""
        if user_id in self.user_connections:
            for socket_id in self.user_connections[user_id].copy():
                await self.send_personal_message(socket_id, message)
    
    async def send_to_room(self, room_id: str, message: Dict[str, Any], exclude_socket: Optional[str] = None):
        """发送消息给房间内所有用户"""
        if room_id in self.room_connections:
            for socket_id in self.room_connections[room_id].copy():
                if exclude_socket and socket_id == exclude_socket:
                    continue
                await self.send_personal_message(socket_id, message)
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息给所有连接"""
        for socket_id in list(self.active_connections.keys()):
            await self.send_personal_message(socket_id, message)
    
    def get_room_users(self, room_id: str) -> List[int]:
        """获取房间内的用户ID列表"""
        if room_id not in self.room_connections:
            return []
        
        user_ids = []
        for socket_id in self.room_connections[room_id]:
            metadata = self.connection_metadata.get(socket_id, {})
            user_id = metadata.get("user_id")
            if user_id and user_id not in user_ids:
                user_ids.append(user_id)
        
        return user_ids
    
    def get_connection_info(self, socket_id: str) -> Optional[Dict[str, Any]]:
        """获取连接信息"""
        return self.connection_metadata.get(socket_id)


class WebSocketService:
    """WebSocket服务类"""
    
    def __init__(self):
        self.manager = ConnectionManager()
    
    async def handle_connection(
        self, 
        websocket: WebSocket, 
        user_id: int, 
        room_id: Optional[str] = None
    ):
        """处理WebSocket连接"""
        socket_id = await self.manager.connect(websocket, user_id, room_id)
        
        try:
            # 如果连接到房间，处理房间相关逻辑
            if room_id:
                await self._handle_room_join(socket_id, user_id, room_id)
            
            # 发送欢迎消息
            await self.manager.send_personal_message(socket_id, {
                "type": "connection_established",
                "socket_id": socket_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # 处理消息循环
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await self._handle_message(socket_id, message)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket客户端断开连接: {socket_id}")
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            # 清理连接
            if room_id:
                await self._handle_room_leave(socket_id, user_id, room_id)
            self.manager.disconnect(socket_id)
    
    async def _handle_message(self, socket_id: str, message: Dict[str, Any]):
        """处理WebSocket消息"""
        try:
            message_type = message.get("type")
            
            if message_type == "chat_message":
                await self._handle_chat_message(socket_id, message)
            elif message_type == "position_update":
                await self._handle_position_update(socket_id, message)
            elif message_type == "object_create":
                await self._handle_object_create(socket_id, message)
            elif message_type == "object_update":
                await self._handle_object_update(socket_id, message)
            elif message_type == "object_delete":
                await self._handle_object_delete(socket_id, message)
            elif message_type == "voice_status":
                await self._handle_voice_status(socket_id, message)
            elif message_type == "screen_share":
                await self._handle_screen_share(socket_id, message)
            elif message_type == "thinking_share":
                await self._handle_thinking_share(socket_id, message)
            elif message_type == "ping":
                await self._handle_ping(socket_id, message)
            else:
                logger.warning(f"未知消息类型: {message_type}")
                
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")
            await self.manager.send_personal_message(socket_id, {
                "type": "error",
                "message": "消息处理失败",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_room_join(self, socket_id: str, user_id: int, room_id: str):
        """处理用户加入房间"""
        try:
            # 获取连接信息
            connection_info = self.manager.get_connection_info(socket_id)
            if not connection_info:
                return
            
            # 通知房间内其他用户
            await self.manager.send_to_room(room_id, {
                "type": "user_joined",
                "user_id": user_id,
                "socket_id": socket_id,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_socket=socket_id)
            
            # 发送房间状态给新用户
            room_users = self.manager.get_room_users(room_id)
            await self.manager.send_personal_message(socket_id, {
                "type": "room_status",
                "room_id": room_id,
                "users": room_users,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # 记录事件到数据库
            await self._record_session_event(room_id, user_id, "user_joined", {
                "socket_id": socket_id
            })
            
        except Exception as e:
            logger.error(f"处理房间加入失败: {e}")
    
    async def _handle_room_leave(self, socket_id: str, user_id: int, room_id: str):
        """处理用户离开房间"""
        try:
            # 通知房间内其他用户
            await self.manager.send_to_room(room_id, {
                "type": "user_left",
                "user_id": user_id,
                "socket_id": socket_id,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_socket=socket_id)
            
            # 记录事件到数据库
            await self._record_session_event(room_id, user_id, "user_left", {
                "socket_id": socket_id
            })
            
        except Exception as e:
            logger.error(f"处理房间离开失败: {e}")
    
    async def _handle_chat_message(self, socket_id: str, message: Dict[str, Any]):
        """处理聊天消息"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            # 广播消息到房间
            broadcast_message = {
                "type": "chat_message",
                "user_id": user_id,
                "content": message.get("content"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message)
            
            # 记录聊天事件
            await self._record_session_event(room_id, user_id, "chat_message", {
                "content": message.get("content")
            })
    
    async def _handle_position_update(self, socket_id: str, message: Dict[str, Any]):
        """处理位置更新"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            # 广播位置更新
            broadcast_message = {
                "type": "position_update",
                "user_id": user_id,
                "position": message.get("position"),
                "rotation": message.get("rotation"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message, exclude_socket=socket_id)
    
    async def _handle_object_create(self, socket_id: str, message: Dict[str, Any]):
        """处理对象创建"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            # 广播对象创建
            broadcast_message = {
                "type": "object_created",
                "user_id": user_id,
                "object_id": message.get("object_id"),
                "object_type": message.get("object_type"),
                "object_data": message.get("object_data"),
                "position": message.get("position"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message)
            
            # TODO: 保存对象到数据库
    
    async def _handle_thinking_share(self, socket_id: str, message: Dict[str, Any]):
        """处理思维分享"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            # 广播思维分析结果
            broadcast_message = {
                "type": "thinking_shared",
                "user_id": user_id,
                "thinking_analysis": message.get("thinking_analysis"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message)
    
    async def _handle_voice_status(self, socket_id: str, message: Dict[str, Any]):
        """处理语音状态"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            # 广播语音状态
            broadcast_message = {
                "type": "voice_status",
                "user_id": user_id,
                "is_speaking": message.get("is_speaking"),
                "audio_enabled": message.get("audio_enabled"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message, exclude_socket=socket_id)
    
    async def _handle_screen_share(self, socket_id: str, message: Dict[str, Any]):
        """处理屏幕共享"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            # 广播屏幕共享状态
            broadcast_message = {
                "type": "screen_share",
                "user_id": user_id,
                "is_sharing": message.get("is_sharing"),
                "stream_id": message.get("stream_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message, exclude_socket=socket_id)
    
    async def _handle_ping(self, socket_id: str, message: Dict[str, Any]):
        """处理心跳"""
        await self.manager.send_personal_message(socket_id, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_object_update(self, socket_id: str, message: Dict[str, Any]):
        """处理对象更新"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            broadcast_message = {
                "type": "object_updated",
                "user_id": user_id,
                "object_id": message.get("object_id"),
                "updates": message.get("updates"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message, exclude_socket=socket_id)
    
    async def _handle_object_delete(self, socket_id: str, message: Dict[str, Any]):
        """处理对象删除"""
        connection_info = self.manager.get_connection_info(socket_id)
        if not connection_info:
            return
        
        room_id = connection_info.get("room_id")
        user_id = connection_info.get("user_id")
        
        if room_id:
            broadcast_message = {
                "type": "object_deleted",
                "user_id": user_id,
                "object_id": message.get("object_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.manager.send_to_room(room_id, broadcast_message, exclude_socket=socket_id)
    
    async def _record_session_event(
        self, 
        room_id: str, 
        user_id: int, 
        event_type: str, 
        event_data: Dict[str, Any]
    ):
        """记录会话事件到数据库"""
        try:
            # 这里应该连接数据库记录事件
            # 暂时只记录到缓存
            event = {
                "room_id": room_id,
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            cache_key = f"session_events:{room_id}"
            await cache_manager.lpush(cache_key, json.dumps(event))
            await cache_manager.expire(cache_key, 86400)  # 24小时过期
            
        except Exception as e:
            logger.error(f"记录会话事件失败: {e}")
    
    def get_room_stats(self, room_id: str) -> Dict[str, Any]:
        """获取房间统计信息"""
        users = self.manager.get_room_users(room_id)
        connections = len(self.manager.room_connections.get(room_id, set()))
        
        return {
            "room_id": room_id,
            "active_users": len(users),
            "total_connections": connections,
            "users": users,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """获取全局统计信息"""
        return {
            "total_connections": len(self.manager.active_connections),
            "active_users": len(self.manager.user_connections),
            "active_rooms": len(self.manager.room_connections),
            "timestamp": datetime.utcnow().isoformat()
        }


# 全局WebSocket服务实例
websocket_service = WebSocketService() 