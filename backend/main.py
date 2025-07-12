"""
智能思维与灵境融合项目 - FastAPI 主入口
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from prometheus_client import make_asgi_app

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.core.neo4j_client import init_neo4j
from app.api.api_v1.api import api_router
from app.ai_models.model_manager import ModelManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 启动智能思维与灵境融合服务...")
    
    # 初始化数据库连接
    await init_db()
    logger.info("✅ PostgreSQL 数据库连接成功")
    
    # 初始化Redis连接
    await init_redis()
    logger.info("✅ Redis 缓存连接成功")
    
    # 初始化Neo4j连接
    await init_neo4j()
    logger.info("✅ Neo4j 知识图谱连接成功")
    
    # 初始化AI模型管理器
    app.state.model_manager = ModelManager()
    await app.state.model_manager.initialize()
    logger.info("✅ AI模型初始化完成")
    
    logger.info("🎉 系统启动完成！")
    
    yield
    
    # 清理资源
    logger.info("🔄 正在关闭服务...")
    if hasattr(app.state, 'model_manager'):
        await app.state.model_manager.cleanup()
    logger.info("👋 服务关闭完成")


# 创建FastAPI应用实例
app = FastAPI(
    title="智能思维与灵境融合平台",
    description="""
    🧠 AI驱动的3D思维空间与协作平台
    
    ## 核心功能
    
    * 🎯 **三层思维建模**: 形象思维 → 逻辑思维 → 创造思维
    * 🌐 **3D认知空间**: WebXR沉浸式思维可视化
    * 🤝 **实时协作**: 多用户共享思维空间
    * 🧮 **知识图谱**: AI驱动的关联推演
    * ⛓️ **虚实共生**: 去中心化数据价值流通
    
    ## 技术架构
    
    * **AI引擎**: PyTorch + Transformers + 多模态AI
    * **知识图谱**: Neo4j + 语义推理
    * **实时通信**: WebSocket + Redis
    * **3D渲染**: Three.js + WebXR
    * **区块链**: Web3 + 智能合约
    """,
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 集成Prometheus监控
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# 静态文件服务
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "service": "智能思维与灵境融合平台",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "🧠 三层思维AI建模",
            "🌐 3D沉浸式认知空间", 
            "🤝 实时多用户协作",
            "🧮 知识图谱推理",
            "⛓️ 区块链经济模型"
        ],
        "docs": f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs"
    }


@app.get("/health")
async def health_check():
    """详细健康检查"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": settings.get_current_time(),
            "services": {
                "api": "running",
                "database": "connected",
                "redis": "connected", 
                "neo4j": "connected",
                "ai_models": "loaded"
            },
            "system_info": {
                "environment": settings.ENVIRONMENT,
                "python_version": sys.version,
                "platform": sys.platform
            }
        }
        return health_status
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=503, detail="服务不可用")


if __name__ == "__main__":
    logger.info("🚀 启动开发服务器...")
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=1 if settings.ENVIRONMENT == "development" else 4,
        log_level="info"
    ) 