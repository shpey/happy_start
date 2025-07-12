"""
API v1 主路由
"""

from fastapi import APIRouter

from .endpoints import (
    thinking_analysis,
    knowledge_graph,
    collaboration,
    user_management,
    file_upload,
    system_status
)

api_router = APIRouter()

# 思维分析相关路由
api_router.include_router(
    thinking_analysis.router,
    prefix="/thinking",
    tags=["思维分析"]
)

# 知识图谱相关路由
api_router.include_router(
    knowledge_graph.router,
    prefix="/knowledge",
    tags=["知识图谱"]
)

# 实时协作相关路由
api_router.include_router(
    collaboration.router,
    prefix="/collaboration",
    tags=["实时协作"]
)

# 用户管理相关路由
api_router.include_router(
    user_management.router,
    prefix="/users",
    tags=["用户管理"]
)

# 文件上传相关路由
api_router.include_router(
    file_upload.router,
    prefix="/files",
    tags=["文件管理"]
)

# 系统状态相关路由
api_router.include_router(
    system_status.router,
    prefix="/system",
    tags=["系统状态"]
) 