"""
应用配置管理
"""

import os
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "智能思维与灵境融合平台"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # 服务器配置
    SERVER_NAME: str = "localhost"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React开发服务器
        "http://localhost:8000",  # FastAPI本地
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres123"
    POSTGRES_DB: str = "intelligent_thinking"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Neo4j配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j123"
    
    # JWT配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    JWT_ALGORITHM: str = "HS256"
    
    # 邮箱配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "uploads"
    ALLOWED_FILE_TYPES: List[str] = [
        "jpg", "jpeg", "png", "gif", "bmp", "webp",  # 图片
        "mp4", "avi", "mkv", "mov", "wmv",           # 视频
        "mp3", "wav", "ogg", "m4a",                  # 音频
        "pdf", "doc", "docx", "txt", "md",           # 文档
        "json", "csv", "xlsx", "xls"                 # 数据
    ]
    
    # AI模型配置
    AI_MODELS_PATH: str = "models"
    HUGGINGFACE_CACHE_DIR: str = "models/huggingface"
    ENABLE_GPU: bool = False
    MAX_BATCH_SIZE: int = 32
    
    # 三层思维模型配置
    THINKING_MODELS: Dict[str, Dict[str, Any]] = {
        "visual_thinking": {
            "model_name": "clip-vit-base-patch32",
            "enabled": True,
            "description": "形象思维：视觉-语言理解"
        },
        "logical_thinking": {
            "model_name": "roberta-base",
            "enabled": True,
            "description": "逻辑思维：推理和分析"
        },
        "creative_thinking": {
            "model_name": "gpt2-medium",
            "enabled": True,
            "description": "创造思维：生成和创新"
        }
    }
    
    # 知识图谱配置
    KNOWLEDGE_GRAPH: Dict[str, Any] = {
        "max_nodes": 10000,
        "max_relationships": 50000,
        "similarity_threshold": 0.8,
        "reasoning_depth": 3
    }
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    WS_TIMEOUT: int = 60
    
    # 监控配置
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    LOG_LEVEL: str = "INFO"
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    CACHE_MAX_SIZE: int = 1000
    
    # 任务队列配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # 安全配置
    BCRYPT_ROUNDS: int = 12
    RATE_LIMIT_PER_MINUTE: int = 60
    ENABLE_CORS: bool = True
    
    # 测试配置
    TESTING: bool = False
    TEST_DATABASE_URL: Optional[str] = None
    
    # 区块链配置（可选）
    WEB3_PROVIDER_URL: Optional[str] = None
    ENABLE_BLOCKCHAIN: bool = False
    CONTRACT_ADDRESS: Optional[str] = None
    PRIVATE_KEY: Optional[str] = None
    
    # 生产环境检查
    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be one of: development, staging, production")
        return v
    
    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        return datetime.now().isoformat()
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT == "development"
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.AI_MODELS_PATH, exist_ok=True)
os.makedirs(settings.HUGGINGFACE_CACHE_DIR, exist_ok=True) 