"""
应用配置
"""

import os
from datetime import datetime
from typing import List, Union
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    PROJECT_NAME: str = "智能思维与灵境融合平台"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI驱动的3D思维空间与协作平台"
    
    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # 环境配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./intelligent_thinking.db"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Neo4j配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".pdf", ".doc", ".docx", ".txt", ".csv",
        ".mp3", ".wav", ".mp4", ".avi", ".mov"
    ]
    
    # AI模型配置
    AI_MODEL_DIR: str = "models"
    ENABLE_AI_MODELS: bool = True
    
    # 高级AI模型API配置
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    # AI模型参数
    AI_MODEL_TIMEOUT: int = 30  # 请求超时时间（秒）
    AI_DEFAULT_MODEL: str = "gpt-4"
    AI_MAX_TOKENS: int = 4000
    AI_TEMPERATURE: float = 0.7
    AI_TOP_P: float = 1.0
    AI_FREQUENCY_PENALTY: float = 0.0
    AI_PRESENCE_PENALTY: float = 0.0
    
    # AI功能开关
    ENABLE_GPT4: bool = False
    ENABLE_CLAUDE: bool = False
    ENABLE_GEMINI: bool = False
    ENABLE_LOCAL_MODELS: bool = True
    
    # 多模态AI配置
    ENABLE_IMAGE_ANALYSIS: bool = True
    ENABLE_AUDIO_ANALYSIS: bool = True
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    MAX_AUDIO_SIZE: int = 25 * 1024 * 1024  # 25MB
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    # 监控配置
    ENABLE_METRICS: bool = True
    MONITORING_INTERVAL: int = 60  # 监控数据收集间隔（秒）
    METRICS_RETENTION_HOURS: int = 24  # 指标保留时间（小时）
    ALERT_WEBHOOK_URL: str = ""  # 告警Webhook URL
    
    # 邮件配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    
    # 验证CORS来源
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 获取当前时间
    @staticmethod
    def get_current_time() -> str:
        return datetime.now().isoformat()
    
    # 获取Redis连接URL
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # 获取Neo4j连接URL
    @property
    def neo4j_url(self) -> str:
        return f"{self.NEO4J_URI}"
    
    # 检查是否为生产环境
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    # 检查是否为开发环境
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 如果是生产环境，进行额外的配置检查
if settings.is_production:
    # 检查必要的环境变量
    required_env_vars = [
        "SECRET_KEY",
        "DATABASE_URL",
        "REDIS_HOST",
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not getattr(settings, var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"生产环境缺少必要的环境变量: {', '.join(missing_vars)}")
    
    # 生产环境安全检查
    if settings.SECRET_KEY == "your-secret-key-change-this-in-production":
        raise ValueError("生产环境必须设置自定义的SECRET_KEY") 