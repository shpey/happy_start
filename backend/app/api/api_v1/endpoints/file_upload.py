"""
文件上传 API 端点
"""

from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """上传文件"""
    return {"success": True, "file_id": "mock_file_id", "filename": file.filename}


@router.get("/list/{user_id}")
async def list_user_files(user_id: str) -> Dict[str, Any]:
    """获取用户文件列表"""
    return {"success": True, "files": []}


@router.delete("/{file_id}")
async def delete_file(file_id: str) -> Dict[str, Any]:
    """删除文件"""
    return {"success": True, "message": "文件已删除"} 