"""
GraphQL API Service
提供更灵活的数据查询、变更和订阅功能
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

import strawberry
from strawberry.asgi import GraphQL
from strawberry.types import Info
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import asyncpg
import aioredis

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = "postgresql://user:password@localhost/intelligent_thinking"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis配置
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# GraphQL类型定义
@strawberry.type
class User:
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool
    thinking_count: int
    collaboration_count: int

@strawberry.type
class ThinkingAnalysis:
    id: int
    user_id: int
    title: str
    content: str
    analysis_type: str
    result: str
    confidence_score: float
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    is_public: bool

@strawberry.type
class CollaborationSession:
    id: int
    title: str
    description: Optional[str] = None
    host_user_id: int
    participants: List[int]
    status: str
    created_at: datetime
    updated_at: datetime
    room_id: str
    max_participants: int

@strawberry.type
class ThoughtNFT:
    id: int
    token_id: int
    owner_address: str
    thought_data: str
    ipfs_hash: str
    metadata_uri: str
    created_at: datetime
    is_listed: bool
    price: Optional[str] = None

@strawberry.type
class SystemStats:
    total_users: int
    total_analyses: int
    total_collaborations: int
    total_nfts: int
    active_users_today: int
    average_confidence_score: float

@strawberry.type
class RealtimeUpdate:
    type: str
    data: str
    timestamp: datetime
    user_id: Optional[int] = None

# 输入类型
@strawberry.input
class UserInput:
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

@strawberry.input
class ThinkingAnalysisInput:
    title: str
    content: str
    analysis_type: str
    tags: List[str]
    is_public: bool = False

@strawberry.input
class CollaborationSessionInput:
    title: str
    description: Optional[str] = None
    max_participants: int = 10

@strawberry.input
class UserFilter:
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    search_term: Optional[str] = None

@strawberry.input
class ThinkingAnalysisFilter:
    analysis_type: Optional[str] = None
    is_public: Optional[bool] = None
    min_confidence: Optional[float] = None
    tags: Optional[List[str]] = None

# 数据加载器
class DataLoader:
    """数据加载器，用于批量加载和缓存数据"""
    
    def __init__(self):
        self.cache = {}
    
    async def load_user(self, user_id: int) -> Optional[User]:
        """加载用户数据"""
        if user_id in self.cache:
            return self.cache[user_id]
        
        # 模拟数据库查询
        user_data = {
            "id": user_id,
            "email": f"user{user_id}@example.com",
            "username": f"user{user_id}",
            "full_name": f"User {user_id}",
            "created_at": datetime.now(),
            "is_active": True,
            "thinking_count": 5,
            "collaboration_count": 3
        }
        
        user = User(**user_data)
        self.cache[user_id] = user
        return user
    
    async def load_thinking_analyses(self, user_id: int) -> List[ThinkingAnalysis]:
        """加载用户的思维分析"""
        # 模拟数据库查询
        analyses = [
            ThinkingAnalysis(
                id=i,
                user_id=user_id,
                title=f"思维分析 {i}",
                content=f"分析内容 {i}",
                analysis_type="综合分析",
                result=f"分析结果 {i}",
                confidence_score=0.85,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["逻辑思维", "创造性"],
                is_public=True
            )
            for i in range(1, 6)
        ]
        return analyses
    
    async def load_collaboration_sessions(self, user_id: int) -> List[CollaborationSession]:
        """加载用户的协作会话"""
        # 模拟数据库查询
        sessions = [
            CollaborationSession(
                id=i,
                title=f"协作会话 {i}",
                description=f"会话描述 {i}",
                host_user_id=user_id,
                participants=[user_id, user_id + 1],
                status="active",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                room_id=f"room_{i}",
                max_participants=10
            )
            for i in range(1, 4)
        ]
        return sessions

# 创建全局数据加载器
data_loader = DataLoader()

# GraphQL 查询定义
@strawberry.type
class Query:
    """GraphQL查询类"""
    
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        """获取单个用户"""
        return await data_loader.load_user(id)
    
    @strawberry.field
    async def users(self, filter: Optional[UserFilter] = None, limit: int = 10) -> List[User]:
        """获取用户列表"""
        # 模拟过滤和分页
        users = []
        for i in range(1, limit + 1):
            user = await data_loader.load_user(i)
            if user:
                users.append(user)
        return users
    
    @strawberry.field
    async def thinking_analysis(self, id: int) -> Optional[ThinkingAnalysis]:
        """获取单个思维分析"""
        return ThinkingAnalysis(
            id=id,
            user_id=1,
            title="深度思维分析",
            content="这是一个深度思维分析的内容",
            analysis_type="深度分析",
            result="分析结果显示用户具有强烈的逻辑思维能力",
            confidence_score=0.92,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["逻辑思维", "深度分析"],
            is_public=True
        )
    
    @strawberry.field
    async def thinking_analyses(
        self, 
        filter: Optional[ThinkingAnalysisFilter] = None,
        limit: int = 10
    ) -> List[ThinkingAnalysis]:
        """获取思维分析列表"""
        # 模拟过滤逻辑
        analyses = []
        for i in range(1, limit + 1):
            analysis = ThinkingAnalysis(
                id=i,
                user_id=1,
                title=f"思维分析 {i}",
                content=f"分析内容 {i}",
                analysis_type="综合分析",
                result=f"分析结果 {i}",
                confidence_score=0.85,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["逻辑思维", "创造性"],
                is_public=True
            )
            analyses.append(analysis)
        return analyses
    
    @strawberry.field
    async def collaboration_session(self, id: int) -> Optional[CollaborationSession]:
        """获取单个协作会话"""
        return CollaborationSession(
            id=id,
            title="团队思维风暴",
            description="项目创新思维协作会话",
            host_user_id=1,
            participants=[1, 2, 3],
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            room_id=f"room_{id}",
            max_participants=10
        )
    
    @strawberry.field
    async def collaboration_sessions(
        self,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[CollaborationSession]:
        """获取协作会话列表"""
        sessions = []
        for i in range(1, limit + 1):
            session = CollaborationSession(
                id=i,
                title=f"协作会话 {i}",
                description=f"会话描述 {i}",
                host_user_id=1,
                participants=[1, 2],
                status=status or "active",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                room_id=f"room_{i}",
                max_participants=10
            )
            sessions.append(session)
        return sessions
    
    @strawberry.field
    async def thought_nfts(self, owner_address: str) -> List[ThoughtNFT]:
        """获取思维NFT列表"""
        nfts = []
        for i in range(1, 6):
            nft = ThoughtNFT(
                id=i,
                token_id=i,
                owner_address=owner_address,
                thought_data=f"思维数据 {i}",
                ipfs_hash=f"QmHash{i}",
                metadata_uri=f"https://ipfs.io/ipfs/QmHash{i}",
                created_at=datetime.now(),
                is_listed=True,
                price="0.1"
            )
            nfts.append(nft)
        return nfts
    
    @strawberry.field
    async def system_stats(self) -> SystemStats:
        """获取系统统计信息"""
        return SystemStats(
            total_users=1000,
            total_analyses=5000,
            total_collaborations=1500,
            total_nfts=500,
            active_users_today=150,
            average_confidence_score=0.82
        )
    
    @strawberry.field
    async def search(self, query: str, limit: int = 10) -> List[str]:
        """全文搜索"""
        # 模拟搜索结果
        results = [
            f"搜索结果 {i}: {query}",
            f"相关分析 {i}: {query}",
            f"协作会话 {i}: {query}"
        ]
        return results[:limit]

# GraphQL 变更定义
@strawberry.type
class Mutation:
    """GraphQL变更类"""
    
    @strawberry.field
    async def create_user(self, input: UserInput) -> User:
        """创建用户"""
        # 模拟用户创建
        user = User(
            id=999,
            email=input.email,
            username=input.username,
            full_name=input.full_name,
            created_at=datetime.now(),
            is_active=True,
            thinking_count=0,
            collaboration_count=0
        )
        return user
    
    @strawberry.field
    async def create_thinking_analysis(self, input: ThinkingAnalysisInput) -> ThinkingAnalysis:
        """创建思维分析"""
        # 模拟AI分析过程
        analysis = ThinkingAnalysis(
            id=999,
            user_id=1,
            title=input.title,
            content=input.content,
            analysis_type=input.analysis_type,
            result="AI分析结果: 用户展现出优秀的逻辑思维能力",
            confidence_score=0.88,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=input.tags,
            is_public=input.is_public
        )
        
        # 发送实时更新
        await publish_realtime_update("thinking_analysis_created", analysis)
        
        return analysis
    
    @strawberry.field
    async def create_collaboration_session(self, input: CollaborationSessionInput) -> CollaborationSession:
        """创建协作会话"""
        session = CollaborationSession(
            id=999,
            title=input.title,
            description=input.description,
            host_user_id=1,
            participants=[1],
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            room_id=f"room_{999}",
            max_participants=input.max_participants
        )
        
        # 发送实时更新
        await publish_realtime_update("collaboration_session_created", session)
        
        return session
    
    @strawberry.field
    async def join_collaboration_session(self, session_id: int, user_id: int) -> bool:
        """加入协作会话"""
        # 模拟加入逻辑
        await publish_realtime_update("user_joined_session", {"session_id": session_id, "user_id": user_id})
        return True
    
    @strawberry.field
    async def leave_collaboration_session(self, session_id: int, user_id: int) -> bool:
        """离开协作会话"""
        # 模拟离开逻辑
        await publish_realtime_update("user_left_session", {"session_id": session_id, "user_id": user_id})
        return True

# GraphQL 订阅定义
@strawberry.type
class Subscription:
    """GraphQL订阅类"""
    
    @strawberry.subscription
    async def realtime_updates(self) -> RealtimeUpdate:
        """实时更新订阅"""
        # 模拟实时更新流
        counter = 0
        while True:
            await asyncio.sleep(5)  # 每5秒发送一次更新
            counter += 1
            yield RealtimeUpdate(
                type="system_update",
                data=f"系统更新 {counter}",
                timestamp=datetime.now()
            )
    
    @strawberry.subscription
    async def collaboration_updates(self, session_id: int) -> RealtimeUpdate:
        """协作会话更新订阅"""
        # 模拟协作更新
        counter = 0
        while True:
            await asyncio.sleep(3)  # 每3秒发送一次更新
            counter += 1
            yield RealtimeUpdate(
                type="collaboration_update",
                data=f"协作会话 {session_id} 更新 {counter}",
                timestamp=datetime.now(),
                user_id=1
            )
    
    @strawberry.subscription
    async def thinking_analysis_updates(self, user_id: int) -> RealtimeUpdate:
        """思维分析更新订阅"""
        # 模拟分析更新
        counter = 0
        while True:
            await asyncio.sleep(10)  # 每10秒发送一次更新
            counter += 1
            yield RealtimeUpdate(
                type="thinking_analysis_update",
                data=f"用户 {user_id} 的思维分析更新 {counter}",
                timestamp=datetime.now(),
                user_id=user_id
            )

# 实时更新发布函数
async def publish_realtime_update(event_type: str, data: Any):
    """发布实时更新"""
    try:
        update = {
            "type": event_type,
            "data": json.dumps(data, default=str),
            "timestamp": datetime.now().isoformat()
        }
        
        # 发布到Redis
        redis_client.publish("realtime_updates", json.dumps(update))
        
    except Exception as e:
        logger.error(f"Failed to publish realtime update: {e}")

# 创建GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

# 创建GraphQL应用
graphql_app = GraphQL(
    schema,
    debug=True,
    subscription_protocols=[
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
        GRAPHQL_WS_PROTOCOL,
    ]
)

# 创建FastAPI应用
app = FastAPI(
    title="智能思维平台 - GraphQL API",
    description="提供灵活的数据查询、变更和订阅功能",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "GraphQL API",
        "timestamp": datetime.now().isoformat()
    }

# 添加GraphQL端点
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)

# GraphQL Playground（开发环境）
@app.get("/")
async def graphql_playground():
    return {
        "message": "GraphQL API is running",
        "playground": "/graphql",
        "schema": "Available via introspection"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005) 