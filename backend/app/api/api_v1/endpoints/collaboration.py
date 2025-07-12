"""
实时协作 API 端点
"""

from typing import Dict, Any
from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

router = APIRouter()


class RoomCreate(BaseModel):
    name: str
    description: str = ""
    max_users: int = 10


@router.post("/rooms")
async def create_room(room: RoomCreate) -> Dict[str, Any]:
    """创建协作房间"""
    return {"success": True, "room_id": "mock_room_id"}


@router.get("/rooms")
async def get_rooms() -> Dict[str, Any]:
    """获取协作房间列表"""
    return {"success": True, "rooms": []}


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket连接端点"""
    await websocket.accept()
    await websocket.send_text("连接成功") 