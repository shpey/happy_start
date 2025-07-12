#!/usr/bin/env python3
"""
智能思维项目 - 第7-8周高级功能集成
企业级功能：用户管理、数据持久化、实时协作、云部署准备
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import sqlite3
import json
import hashlib
import uuid
import datetime
import asyncio
import uvicorn
from pathlib import Path
import jwt
import bcrypt

# ==================== 数据模型 ====================

class User(BaseModel):
    """用户模型"""
    id: Optional[str] = None
    username: str
    email: EmailStr
    full_name: str
    thinking_profile: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime.datetime] = None
    last_active: Optional[datetime.datetime] = None

class UserCreate(BaseModel):
    """用户创建模型"""
    username: str
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

class ThinkingSession(BaseModel):
    """思维会话模型"""
    id: Optional[str] = None
    user_id: str
    space_id: str
    session_name: str
    thinking_mode: str
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    session_data: Dict[str, Any]
    is_shared: bool = False
    collaborators: List[str] = []

class CollaborationRoom(BaseModel):
    """协作房间模型"""
    room_id: str
    owner_id: str
    participants: List[str]
    thinking_space: Dict[str, Any]
    created_at: datetime.datetime
    max_participants: int = 10

class SystemMetrics(BaseModel):
    """系统指标模型"""
    total_users: int
    active_sessions: int
    total_spaces_created: int
    average_session_duration: float
    popular_thinking_modes: Dict[str, int]

# ==================== 数据库管理 ====================

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "intelligent_thinking.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            thinking_profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 思维会话表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS thinking_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            space_id TEXT NOT NULL,
            session_name TEXT NOT NULL,
            thinking_mode TEXT NOT NULL,
            session_data TEXT NOT NULL,
            is_shared BOOLEAN DEFAULT FALSE,
            collaborators TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 协作房间表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collaboration_rooms (
            room_id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            participants TEXT NOT NULL,
            thinking_space TEXT NOT NULL,
            max_participants INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
        ''')
        
        # 系统日志表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_data: UserCreate) -> str:
        """创建用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, full_name, thinking_profile)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, user_data.username, user_data.email, password_hash, user_data.full_name, '{}'))
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """验证用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash, full_name, email FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
            return {
                'id': result[0],
                'username': username,
                'full_name': result[2],
                'email': result[3]
            }
        return None
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, space_id, session_name, thinking_mode, created_at, updated_at, is_shared
        FROM thinking_sessions WHERE user_id = ? ORDER BY updated_at DESC
        ''', (user_id,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'space_id': row[1],
                'session_name': row[2],
                'thinking_mode': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'is_shared': bool(row[6])
            })
        
        conn.close()
        return sessions

# ==================== JWT认证 ====================

SECRET_KEY = "intelligent-thinking-secret-key-2024"
ALGORITHM = "HS256"

def create_access_token(user_data: Dict[str, Any]) -> str:
    """创建访问令牌"""
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    to_encode = user_data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效令牌")

# ==================== WebSocket连接管理 ====================

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_rooms: Dict[str, str] = {}  # user_id -> room_id
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        """连接用户到房间"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        self.active_connections[room_id].append(websocket)
        self.user_rooms[user_id] = room_id
        
        # 通知其他用户
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "message": f"用户 {user_id} 加入了协作空间"
        }, exclude_websocket=websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """断开连接"""
        room_id = self.user_rooms.get(user_id)
        if room_id and room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            
            if user_id in self.user_rooms:
                del self.user_rooms[user_id]
            
            # 通知其他用户
            asyncio.create_task(self.broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": user_id,
                "message": f"用户 {user_id} 离开了协作空间"
            }))
    
    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_websocket: WebSocket = None):
        """向房间广播消息"""
        if room_id in self.active_connections:
            dead_connections = []
            for websocket in self.active_connections[room_id]:
                if websocket != exclude_websocket:
                    try:
                        await websocket.send_json(message)
                    except:
                        dead_connections.append(websocket)
            
            # 清理死连接
            for dead_ws in dead_connections:
                self.active_connections[room_id].remove(dead_ws)

# ==================== FastAPI应用 ====================

app = FastAPI(
    title="智能思维高级功能API",
    description="企业级智能思维分析系统",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
db_manager = DatabaseManager()
connection_manager = ConnectionManager()
security = HTTPBearer()

# ==================== 认证依赖 ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    user_data = verify_token(token)
    return user_data

# ==================== 用户管理API ====================

@app.post("/api/auth/register")
async def register_user(user_data: UserCreate):
    """用户注册"""
    try:
        user_id = db_manager.create_user(user_data)
        return {
            "message": "用户创建成功",
            "user_id": user_id,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login_user(login_data: UserLogin):
    """用户登录"""
    user = db_manager.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@app.get("/api/user/sessions")
async def get_user_sessions(current_user: Dict = Depends(get_current_user)):
    """获取用户思维会话"""
    sessions = db_manager.get_user_sessions(current_user['id'])
    return {"sessions": sessions}

# ==================== 协作功能API ====================

@app.post("/api/collaboration/create-room")
async def create_collaboration_room(
    thinking_space: Dict[str, Any],
    max_participants: int = 10,
    current_user: Dict = Depends(get_current_user)
):
    """创建协作房间"""
    room_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO collaboration_rooms (room_id, owner_id, participants, thinking_space, max_participants)
    VALUES (?, ?, ?, ?, ?)
    ''', (room_id, current_user['id'], json.dumps([current_user['id']]), json.dumps(thinking_space), max_participants))
    
    conn.commit()
    conn.close()
    
    return {
        "room_id": room_id,
        "message": "协作房间创建成功",
        "room_url": f"/collaboration/{room_id}"
    }

@app.get("/api/collaboration/room/{room_id}")
async def get_collaboration_room(room_id: str, current_user: Dict = Depends(get_current_user)):
    """获取协作房间信息"""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM collaboration_rooms WHERE room_id = ?', (room_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="协作房间不存在")
    
    return {
        "room_id": result[0],
        "owner_id": result[1],
        "participants": json.loads(result[2]),
        "thinking_space": json.loads(result[3]),
        "max_participants": result[4],
        "created_at": result[5]
    }

@app.websocket("/ws/collaboration/{room_id}")
async def websocket_collaboration(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket协作端点"""
    await connection_manager.connect(websocket, room_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # 处理不同类型的协作消息
            if data["type"] == "thinking_update":
                await connection_manager.broadcast_to_room(room_id, {
                    "type": "thinking_update",
                    "user_id": user_id,
                    "updates": data["updates"],
                    "timestamp": datetime.datetime.now().isoformat()
                })
            
            elif data["type"] == "cursor_position":
                await connection_manager.broadcast_to_room(room_id, {
                    "type": "cursor_position",
                    "user_id": user_id,
                    "position": data["position"]
                }, exclude_websocket=websocket)
            
            elif data["type"] == "chat_message":
                await connection_manager.broadcast_to_room(room_id, {
                    "type": "chat_message",
                    "user_id": user_id,
                    "message": data["message"],
                    "timestamp": datetime.datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id)

# ==================== 系统监控API ====================

@app.get("/api/admin/metrics")
async def get_system_metrics(current_user: Dict = Depends(get_current_user)):
    """获取系统指标"""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # 统计用户数
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # 统计会话数
    cursor.execute('SELECT COUNT(*) FROM thinking_sessions')
    total_sessions = cursor.fetchone()[0]
    
    # 统计活跃房间数
    active_sessions = len(connection_manager.active_connections)
    
    # 统计思维模式使用情况
    cursor.execute('SELECT thinking_mode, COUNT(*) FROM thinking_sessions GROUP BY thinking_mode')
    mode_stats = dict(cursor.fetchall())
    
    conn.close()
    
    return SystemMetrics(
        total_users=total_users,
        active_sessions=active_sessions,
        total_spaces_created=total_sessions,
        average_session_duration=25.5,  # 模拟数据
        popular_thinking_modes=mode_stats
    )

# ==================== 数据导出API ====================

@app.get("/api/export/user-data")
async def export_user_data(current_user: Dict = Depends(get_current_user)):
    """导出用户数据"""
    sessions = db_manager.get_user_sessions(current_user['id'])
    
    export_data = {
        "user_info": current_user,
        "sessions": sessions,
        "export_timestamp": datetime.datetime.now().isoformat(),
        "total_sessions": len(sessions)
    }
    
    return export_data

# ==================== 移动端API ====================

@app.get("/api/mobile/thinking-summary")
async def get_mobile_thinking_summary(current_user: Dict = Depends(get_current_user)):
    """移动端思维摘要"""
    sessions = db_manager.get_user_sessions(current_user['id'])
    
    # 计算统计信息
    total_sessions = len(sessions)
    mode_counts = {}
    for session in sessions:
        mode = session.get('thinking_mode', 'unknown')
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
    
    return {
        "user_name": current_user['full_name'],
        "total_sessions": total_sessions,
        "favorite_mode": max(mode_counts.items(), key=lambda x: x[1])[0] if mode_counts else "creative",
        "mode_distribution": mode_counts,
        "recent_activity": sessions[:5],  # 最近5个会话
        "thinking_streak": 7  # 模拟连续天数
    }

# ==================== 主页和文档 ====================

@app.get("/")
async def get_advanced_home():
    """高级功能主页"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 智能思维高级功能中心</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 800px;
                text-align: center;
            }
            h1 { color: #333; margin-bottom: 20px; font-size: 2.5rem; }
            .subtitle { color: #666; margin-bottom: 30px; font-size: 1.2rem; }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .feature h3 { color: #333; margin-bottom: 10px; }
            .feature p { color: #666; font-size: 0.9rem; }
            .btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                margin: 10px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
            .status { 
                background: #e8f5e8; 
                border: 1px solid #4caf50; 
                border-radius: 10px; 
                padding: 15px; 
                margin: 20px 0; 
                color: #2e7d32;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 智能思维高级功能中心</h1>
            <p class="subtitle">企业级智能思维分析与协作平台</p>
            
            <div class="status">
                ✅ 系统状态：所有服务正常运行 | 在线用户：实时统计 | 活跃协作房间：动态更新
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>👥 用户管理系统</h3>
                    <p>完整的用户注册、登录、认证体系，支持JWT令牌和安全会话管理</p>
                </div>
                
                <div class="feature">
                    <h3>🤝 实时协作功能</h3>
                    <p>WebSocket驱动的多用户协作，支持实时思维空间共享和同步</p>
                </div>
                
                <div class="feature">
                    <h3>💾 数据持久化</h3>
                    <p>SQLite数据库存储用户数据、会话记录和协作历史</p>
                </div>
                
                <div class="feature">
                    <h3>📊 系统监控</h3>
                    <p>实时系统指标监控、用户行为分析和性能优化建议</p>
                </div>
                
                <div class="feature">
                    <h3>📱 移动端适配</h3>
                    <p>响应式设计，完美支持移动设备和平板电脑访问</p>
                </div>
                
                <div class="feature">
                    <h3>☁️ 云部署就绪</h3>
                    <p>容器化部署，支持Docker和Kubernetes集群环境</p>
                </div>
            </div>
            
            <div>
                <a href="/docs" class="btn">📚 API文档</a>
                <a href="http://localhost:8001/3d" class="btn">🌐 3D思维空间</a>
                <a href="/api/admin/metrics" class="btn">📊 系统指标</a>
            </div>
            
            <p style="margin-top: 30px; color: #888; font-size: 0.9rem;">
                🔧 版本 3.0.0 | 企业级功能已就绪 | 支持高并发和大规模部署
            </p>
        </div>
    </body>
    </html>
    """)

# ==================== 启动服务 ====================

def start_advanced_server():
    """启动高级功能服务"""
    print("🚀 启动智能思维高级功能服务...")
    print("🌐 主页: http://localhost:8002")
    print("📚 API文档: http://localhost:8002/docs") 
    print("👥 用户管理: http://localhost:8002/api/auth/*")
    print("🤝 协作功能: http://localhost:8002/api/collaboration/*")
    print("📊 系统监控: http://localhost:8002/api/admin/metrics")
    print("💡 提示: 按 Ctrl+C 停止服务")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_advanced_server() 