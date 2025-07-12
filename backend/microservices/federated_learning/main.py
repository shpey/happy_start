from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import asyncio
import json
import logging
from datetime import datetime, timedelta
import uuid
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import redis.asyncio as redis
import asyncpg
from contextlib import asynccontextmanager
import pickle
import gzip
import threading
import time
from collections import defaultdict, deque
import random
import signal
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据模型
class ClientInfo(BaseModel):
    client_id: str
    name: str
    data_size: int
    model_type: str
    capabilities: Dict[str, Any]
    last_active: datetime
    status: str = "active"

class ModelConfig(BaseModel):
    model_id: str
    model_type: str  # "pytorch", "tensorflow", "sklearn"
    architecture: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    privacy_budget: float = 1.0
    min_clients: int = 3
    max_clients: int = 100
    rounds: int = 10
    client_fraction: float = 0.3

class TrainingTask(BaseModel):
    task_id: str
    model_config: ModelConfig
    training_data_schema: Dict[str, Any]
    validation_metrics: List[str]
    privacy_settings: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)

class ClientUpdate(BaseModel):
    client_id: str
    task_id: str
    round_number: int
    model_weights: str  # Base64编码的模型权重
    data_size: int
    training_loss: float
    validation_metrics: Dict[str, float]
    privacy_noise: Optional[str] = None
    checksum: str

class FederatedRound(BaseModel):
    round_id: str
    task_id: str
    round_number: int
    selected_clients: List[str]
    global_model_weights: str
    aggregated_metrics: Dict[str, float]
    convergence_score: float
    privacy_spent: float
    status: str = "running"
    start_time: datetime = Field(default_factory=datetime.now)

class PrivacyMetrics(BaseModel):
    epsilon: float
    delta: float
    privacy_budget_used: float
    noise_multiplier: float
    clipping_threshold: float

# 联邦学习核心类
class FederatedLearningSystem:
    def __init__(self):
        self.clients = {}
        self.tasks = {}
        self.rounds = {}
        self.global_models = {}
        self.redis_client = None
        self.db_pool = None
        self.websocket_connections = {}
        self.privacy_engine = None
        self.model_aggregator = None
        self.differential_privacy = None
        
    async def initialize(self):
        """初始化联邦学习系统"""
        try:
            # 初始化Redis
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # 初始化数据库连接池
            self.db_pool = await asyncpg.create_pool(
                host="localhost",
                port=5432,
                user="postgres",
                password="password",
                database="intelligent_thinking"
            )
            
            # 初始化隐私引擎
            self.privacy_engine = PrivacyEngine()
            
            # 初始化模型聚合器
            self.model_aggregator = ModelAggregator()
            
            # 初始化差分隐私
            self.differential_privacy = DifferentialPrivacy()
            
            # 创建数据库表
            await self._create_tables()
            
            # 启动后台任务
            asyncio.create_task(self._background_tasks())
            
            logger.info("联邦学习系统初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    async def _create_tables(self):
        """创建数据库表"""
        try:
            async with self.db_pool.acquire() as conn:
                # 客户端表
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS federated_clients (
                        client_id VARCHAR PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        data_size INTEGER,
                        model_type VARCHAR,
                        capabilities JSONB,
                        last_active TIMESTAMP,
                        status VARCHAR DEFAULT 'active'
                    )
                """)
                
                # 训练任务表
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS federated_tasks (
                        task_id VARCHAR PRIMARY KEY,
                        model_config JSONB,
                        training_data_schema JSONB,
                        validation_metrics JSONB,
                        privacy_settings JSONB,
                        status VARCHAR DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # 训练轮次表
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS federated_rounds (
                        round_id VARCHAR PRIMARY KEY,
                        task_id VARCHAR REFERENCES federated_tasks(task_id),
                        round_number INTEGER,
                        selected_clients JSONB,
                        global_model_weights TEXT,
                        aggregated_metrics JSONB,
                        convergence_score FLOAT,
                        privacy_spent FLOAT,
                        status VARCHAR DEFAULT 'running',
                        start_time TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # 客户端更新表
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS client_updates (
                        update_id VARCHAR PRIMARY KEY,
                        client_id VARCHAR,
                        task_id VARCHAR,
                        round_number INTEGER,
                        model_weights TEXT,
                        data_size INTEGER,
                        training_loss FLOAT,
                        validation_metrics JSONB,
                        privacy_noise TEXT,
                        checksum VARCHAR,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                logger.info("数据库表创建完成")
                
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    async def _background_tasks(self):
        """后台任务"""
        while True:
            try:
                # 检查客户端状态
                await self._check_client_status()
                
                # 检查训练任务
                await self._check_training_tasks()
                
                # 清理过期数据
                await self._cleanup_expired_data()
                
                # 等待30秒
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"后台任务出错: {e}")
                await asyncio.sleep(30)
    
    async def _check_client_status(self):
        """检查客户端状态"""
        try:
            current_time = datetime.now()
            timeout_threshold = current_time - timedelta(minutes=5)
            
            # 从数据库获取所有客户端
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT client_id, last_active, status 
                    FROM federated_clients 
                    WHERE status = 'active'
                """)
                
                for row in rows:
                    client_id = row['client_id']
                    last_active = row['last_active']
                    
                    # 检查是否超时
                    if last_active and last_active < timeout_threshold:
                        await conn.execute("""
                            UPDATE federated_clients 
                            SET status = 'inactive' 
                            WHERE client_id = $1
                        """, client_id)
                        
                        # 从内存中移除
                        self.clients.pop(client_id, None)
                        
                        logger.info(f"客户端 {client_id} 已设置为非活跃状态")
                        
        except Exception as e:
            logger.error(f"检查客户端状态失败: {e}")
    
    async def _check_training_tasks(self):
        """检查训练任务"""
        try:
            async with self.db_pool.acquire() as conn:
                # 获取待处理的任务
                rows = await conn.fetch("""
                    SELECT task_id, model_config, status 
                    FROM federated_tasks 
                    WHERE status = 'pending'
                """)
                
                for row in rows:
                    task_id = row['task_id']
                    model_config = json.loads(row['model_config'])
                    
                    # 检查是否有足够的客户端
                    active_clients = len([c for c in self.clients.values() if c['status'] == 'active'])
                    min_clients = model_config.get('min_clients', 3)
                    
                    if active_clients >= min_clients:
                        # 开始训练
                        await self._start_training_task(task_id, model_config)
                        
                        # 更新任务状态
                        await conn.execute("""
                            UPDATE federated_tasks 
                            SET status = 'running' 
                            WHERE task_id = $1
                        """, task_id)
                        
                        logger.info(f"开始训练任务 {task_id}")
                        
        except Exception as e:
            logger.error(f"检查训练任务失败: {e}")
    
    async def _start_training_task(self, task_id: str, model_config: Dict):
        """开始训练任务"""
        try:
            # 选择参与的客户端
            selected_clients = await self._select_clients(task_id, model_config)
            
            # 初始化全局模型
            global_model = await self._initialize_global_model(model_config)
            
            # 创建第一轮训练
            round_id = str(uuid.uuid4())
            round_data = {
                'round_id': round_id,
                'task_id': task_id,
                'round_number': 1,
                'selected_clients': selected_clients,
                'global_model_weights': self._serialize_model(global_model),
                'aggregated_metrics': {},
                'convergence_score': 0.0,
                'privacy_spent': 0.0,
                'status': 'running',
                'start_time': datetime.now()
            }
            
            # 保存到数据库
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO federated_rounds (
                        round_id, task_id, round_number, selected_clients,
                        global_model_weights, aggregated_metrics, convergence_score,
                        privacy_spent, status, start_time
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, round_id, task_id, 1, json.dumps(selected_clients),
                round_data['global_model_weights'], json.dumps({}),
                0.0, 0.0, 'running', datetime.now())
            
            # 保存到内存
            self.rounds[round_id] = round_data
            self.global_models[task_id] = global_model
            
            # 通知客户端开始训练
            await self._notify_clients_start_training(selected_clients, round_data)
            
        except Exception as e:
            logger.error(f"开始训练任务失败: {e}")
            raise
    
    async def _select_clients(self, task_id: str, model_config: Dict) -> List[str]:
        """选择参与训练的客户端"""
        try:
            # 获取活跃客户端
            active_clients = [client_id for client_id, client in self.clients.items() 
                            if client['status'] == 'active']
            
            # 计算参与客户端数量
            client_fraction = model_config.get('client_fraction', 0.3)
            max_clients = model_config.get('max_clients', 100)
            num_clients = min(
                max_clients,
                max(1, int(len(active_clients) * client_fraction))
            )
            
            # 随机选择客户端
            selected_clients = random.sample(active_clients, min(num_clients, len(active_clients)))
            
            logger.info(f"为任务 {task_id} 选择了 {len(selected_clients)} 个客户端")
            
            return selected_clients
            
        except Exception as e:
            logger.error(f"选择客户端失败: {e}")
            return []
    
    async def _initialize_global_model(self, model_config: Dict):
        """初始化全局模型"""
        try:
            model_type = model_config.get('model_type', 'pytorch')
            architecture = model_config.get('architecture', {})
            
            if model_type == 'pytorch':
                return self._create_pytorch_model(architecture)
            elif model_type == 'tensorflow':
                return self._create_tensorflow_model(architecture)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
                
        except Exception as e:
            logger.error(f"初始化全局模型失败: {e}")
            raise
    
    def _create_pytorch_model(self, architecture: Dict):
        """创建PyTorch模型"""
        try:
            # 简单的神经网络模型
            class SimpleNN(nn.Module):
                def __init__(self, input_size, hidden_size, output_size):
                    super(SimpleNN, self).__init__()
                    self.fc1 = nn.Linear(input_size, hidden_size)
                    self.relu = nn.ReLU()
                    self.fc2 = nn.Linear(hidden_size, output_size)
                    self.softmax = nn.Softmax(dim=1)
                
                def forward(self, x):
                    x = self.fc1(x)
                    x = self.relu(x)
                    x = self.fc2(x)
                    return self.softmax(x)
            
            input_size = architecture.get('input_size', 784)
            hidden_size = architecture.get('hidden_size', 128)
            output_size = architecture.get('output_size', 10)
            
            model = SimpleNN(input_size, hidden_size, output_size)
            
            return model
            
        except Exception as e:
            logger.error(f"创建PyTorch模型失败: {e}")
            raise
    
    def _create_tensorflow_model(self, architecture: Dict):
        """创建TensorFlow模型"""
        try:
            input_size = architecture.get('input_size', 784)
            hidden_size = architecture.get('hidden_size', 128)
            output_size = architecture.get('output_size', 10)
            
            model = keras.Sequential([
                keras.layers.Dense(hidden_size, activation='relu', input_shape=(input_size,)),
                keras.layers.Dense(output_size, activation='softmax')
            ])
            
            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            return model
            
        except Exception as e:
            logger.error(f"创建TensorFlow模型失败: {e}")
            raise
    
    def _serialize_model(self, model) -> str:
        """序列化模型"""
        try:
            if isinstance(model, nn.Module):
                # PyTorch模型
                model_state = model.state_dict()
                model_bytes = pickle.dumps(model_state)
            elif isinstance(model, keras.Model):
                # TensorFlow模型
                model_bytes = pickle.dumps(model.get_weights())
            else:
                raise ValueError("不支持的模型类型")
            
            # 压缩和编码
            compressed = gzip.compress(model_bytes)
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            return encoded
            
        except Exception as e:
            logger.error(f"序列化模型失败: {e}")
            raise
    
    def _deserialize_model(self, model_data: str, model_type: str, architecture: Dict):
        """反序列化模型"""
        try:
            # 解码和解压缩
            compressed = base64.b64decode(model_data.encode('utf-8'))
            model_bytes = gzip.decompress(compressed)
            
            if model_type == 'pytorch':
                # 创建模型实例
                model = self._create_pytorch_model(architecture)
                # 加载权重
                model_state = pickle.loads(model_bytes)
                model.load_state_dict(model_state)
                return model
            elif model_type == 'tensorflow':
                # 创建模型实例
                model = self._create_tensorflow_model(architecture)
                # 加载权重
                weights = pickle.loads(model_bytes)
                model.set_weights(weights)
                return model
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
                
        except Exception as e:
            logger.error(f"反序列化模型失败: {e}")
            raise
    
    async def _notify_clients_start_training(self, selected_clients: List[str], round_data: Dict):
        """通知客户端开始训练"""
        try:
            notification = {
                'type': 'start_training',
                'round_id': round_data['round_id'],
                'task_id': round_data['task_id'],
                'round_number': round_data['round_number'],
                'global_model_weights': round_data['global_model_weights'],
                'timestamp': datetime.now().isoformat()
            }
            
            # 发送给选中的客户端
            for client_id in selected_clients:
                if client_id in self.websocket_connections:
                    websocket = self.websocket_connections[client_id]
                    try:
                        await websocket.send_text(json.dumps(notification))
                    except Exception as e:
                        logger.error(f"通知客户端 {client_id} 失败: {e}")
                
                # 也保存到Redis队列
                await self.redis_client.lpush(
                    f"client_notifications:{client_id}",
                    json.dumps(notification)
                )
                
        except Exception as e:
            logger.error(f"通知客户端失败: {e}")
    
    async def register_client(self, client_info: ClientInfo):
        """注册客户端"""
        try:
            # 保存到数据库
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO federated_clients (
                        client_id, name, data_size, model_type, capabilities, last_active, status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (client_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        data_size = EXCLUDED.data_size,
                        model_type = EXCLUDED.model_type,
                        capabilities = EXCLUDED.capabilities,
                        last_active = EXCLUDED.last_active,
                        status = EXCLUDED.status
                """, client_info.client_id, client_info.name, client_info.data_size,
                client_info.model_type, json.dumps(client_info.capabilities),
                client_info.last_active, client_info.status)
            
            # 保存到内存
            self.clients[client_info.client_id] = client_info.dict()
            
            logger.info(f"客户端 {client_info.client_id} 注册成功")
            
        except Exception as e:
            logger.error(f"注册客户端失败: {e}")
            raise
    
    async def create_training_task(self, task: TrainingTask):
        """创建训练任务"""
        try:
            # 保存到数据库
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO federated_tasks (
                        task_id, model_config, training_data_schema, validation_metrics,
                        privacy_settings, status, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, task.task_id, json.dumps(task.model_config.dict()),
                json.dumps(task.training_data_schema), json.dumps(task.validation_metrics),
                json.dumps(task.privacy_settings), task.status, task.created_at)
            
            # 保存到内存
            self.tasks[task.task_id] = task.dict()
            
            logger.info(f"训练任务 {task.task_id} 创建成功")
            
        except Exception as e:
            logger.error(f"创建训练任务失败: {e}")
            raise
    
    async def submit_client_update(self, update: ClientUpdate):
        """提交客户端更新"""
        try:
            # 验证更新
            if not await self._validate_client_update(update):
                raise ValueError("客户端更新验证失败")
            
            # 应用差分隐私
            if update.privacy_noise:
                update = await self._apply_differential_privacy(update)
            
            # 保存到数据库
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO client_updates (
                        update_id, client_id, task_id, round_number, model_weights,
                        data_size, training_loss, validation_metrics, privacy_noise,
                        checksum, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, str(uuid.uuid4()), update.client_id, update.task_id,
                update.round_number, update.model_weights, update.data_size,
                update.training_loss, json.dumps(update.validation_metrics),
                update.privacy_noise, update.checksum, datetime.now())
            
            # 检查是否所有客户端都提交了更新
            await self._check_round_completion(update.task_id, update.round_number)
            
            logger.info(f"客户端 {update.client_id} 更新提交成功")
            
        except Exception as e:
            logger.error(f"提交客户端更新失败: {e}")
            raise
    
    async def _validate_client_update(self, update: ClientUpdate) -> bool:
        """验证客户端更新"""
        try:
            # 验证校验和
            expected_checksum = self._calculate_checksum(update.model_weights)
            if update.checksum != expected_checksum:
                logger.error(f"客户端 {update.client_id} 校验和不匹配")
                return False
            
            # 验证客户端是否被选中
            round_info = await self._get_round_info(update.task_id, update.round_number)
            if not round_info or update.client_id not in round_info['selected_clients']:
                logger.error(f"客户端 {update.client_id} 未被选中参与此轮训练")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证客户端更新失败: {e}")
            return False
    
    def _calculate_checksum(self, data: str) -> str:
        """计算校验和"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def _get_round_info(self, task_id: str, round_number: int) -> Optional[Dict]:
        """获取轮次信息"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM federated_rounds 
                    WHERE task_id = $1 AND round_number = $2
                """, task_id, round_number)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"获取轮次信息失败: {e}")
            return None
    
    async def _apply_differential_privacy(self, update: ClientUpdate) -> ClientUpdate:
        """应用差分隐私"""
        try:
            # 这里应该实现差分隐私算法
            # 目前返回原始更新
            return update
            
        except Exception as e:
            logger.error(f"应用差分隐私失败: {e}")
            return update
    
    async def _check_round_completion(self, task_id: str, round_number: int):
        """检查轮次完成情况"""
        try:
            # 获取轮次信息
            round_info = await self._get_round_info(task_id, round_number)
            if not round_info:
                return
            
            selected_clients = json.loads(round_info['selected_clients'])
            
            # 检查收到的更新数量
            async with self.db_pool.acquire() as conn:
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM client_updates 
                    WHERE task_id = $1 AND round_number = $2
                """, task_id, round_number)
            
            # 如果所有客户端都提交了更新
            if count >= len(selected_clients):
                await self._aggregate_and_start_next_round(task_id, round_number)
                
        except Exception as e:
            logger.error(f"检查轮次完成失败: {e}")
    
    async def _aggregate_and_start_next_round(self, task_id: str, round_number: int):
        """聚合模型并开始下一轮"""
        try:
            # 获取所有客户端更新
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM client_updates 
                    WHERE task_id = $1 AND round_number = $2
                """, task_id, round_number)
            
            # 聚合模型
            aggregated_model = await self._aggregate_models(rows, task_id)
            
            # 计算聚合指标
            aggregated_metrics = await self._calculate_aggregated_metrics(rows)
            
            # 计算收敛分数
            convergence_score = await self._calculate_convergence(task_id, aggregated_metrics)
            
            # 更新当前轮次状态
            await self._update_round_status(task_id, round_number, aggregated_model, aggregated_metrics, convergence_score)
            
            # 检查是否需要开始下一轮
            task_info = self.tasks.get(task_id)
            if task_info and round_number < task_info['model_config']['rounds']:
                if convergence_score < 0.95:  # 未收敛
                    await self._start_next_round(task_id, round_number + 1, aggregated_model)
                else:
                    await self._complete_training(task_id, aggregated_model)
            else:
                await self._complete_training(task_id, aggregated_model)
                
        except Exception as e:
            logger.error(f"聚合模型失败: {e}")
    
    async def _aggregate_models(self, client_updates: List, task_id: str):
        """聚合模型"""
        try:
            if not client_updates:
                return None
            
            # 获取任务配置
            task_info = self.tasks.get(task_id)
            if not task_info:
                return None
            
            model_config = task_info['model_config']
            
            # 使用联邦平均算法
            aggregated_model = await self.model_aggregator.federated_averaging(
                client_updates, model_config
            )
            
            return aggregated_model
            
        except Exception as e:
            logger.error(f"聚合模型失败: {e}")
            return None
    
    async def _calculate_aggregated_metrics(self, client_updates: List) -> Dict[str, float]:
        """计算聚合指标"""
        try:
            if not client_updates:
                return {}
            
            # 加权平均
            total_data_size = sum(update['data_size'] for update in client_updates)
            
            aggregated_metrics = {}
            
            # 计算加权平均损失
            weighted_loss = sum(
                update['training_loss'] * update['data_size'] 
                for update in client_updates
            ) / total_data_size
            
            aggregated_metrics['training_loss'] = weighted_loss
            
            # 计算其他指标
            for update in client_updates:
                metrics = json.loads(update['validation_metrics'])
                for metric_name, metric_value in metrics.items():
                    if metric_name not in aggregated_metrics:
                        aggregated_metrics[metric_name] = 0.0
                    aggregated_metrics[metric_name] += metric_value * update['data_size']
            
            # 归一化
            for metric_name in aggregated_metrics:
                if metric_name != 'training_loss':
                    aggregated_metrics[metric_name] /= total_data_size
            
            return aggregated_metrics
            
        except Exception as e:
            logger.error(f"计算聚合指标失败: {e}")
            return {}
    
    async def _calculate_convergence(self, task_id: str, current_metrics: Dict) -> float:
        """计算收敛分数"""
        try:
            # 获取历史指标
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT aggregated_metrics FROM federated_rounds 
                    WHERE task_id = $1 
                    ORDER BY round_number DESC 
                    LIMIT 2
                """, task_id)
            
            if len(rows) < 2:
                return 0.0
            
            # 计算指标变化
            prev_metrics = json.loads(rows[1]['aggregated_metrics'])
            
            if 'accuracy' in current_metrics and 'accuracy' in prev_metrics:
                accuracy_diff = abs(current_metrics['accuracy'] - prev_metrics['accuracy'])
                convergence = 1.0 - min(accuracy_diff, 1.0)
                return convergence
            
            return 0.0
            
        except Exception as e:
            logger.error(f"计算收敛分数失败: {e}")
            return 0.0
    
    async def _update_round_status(self, task_id: str, round_number: int, 
                                 aggregated_model, aggregated_metrics: Dict, convergence_score: float):
        """更新轮次状态"""
        try:
            model_weights = self._serialize_model(aggregated_model) if aggregated_model else ""
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE federated_rounds 
                    SET global_model_weights = $1, aggregated_metrics = $2, 
                        convergence_score = $3, status = 'completed'
                    WHERE task_id = $4 AND round_number = $5
                """, model_weights, json.dumps(aggregated_metrics), 
                convergence_score, task_id, round_number)
                
        except Exception as e:
            logger.error(f"更新轮次状态失败: {e}")
    
    async def _start_next_round(self, task_id: str, round_number: int, global_model):
        """开始下一轮训练"""
        try:
            # 获取任务配置
            task_info = self.tasks.get(task_id)
            if not task_info:
                return
            
            model_config = task_info['model_config']
            
            # 选择新的客户端
            selected_clients = await self._select_clients(task_id, model_config)
            
            # 创建新轮次
            round_id = str(uuid.uuid4())
            round_data = {
                'round_id': round_id,
                'task_id': task_id,
                'round_number': round_number,
                'selected_clients': selected_clients,
                'global_model_weights': self._serialize_model(global_model),
                'aggregated_metrics': {},
                'convergence_score': 0.0,
                'privacy_spent': 0.0,
                'status': 'running',
                'start_time': datetime.now()
            }
            
            # 保存到数据库
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO federated_rounds (
                        round_id, task_id, round_number, selected_clients,
                        global_model_weights, aggregated_metrics, convergence_score,
                        privacy_spent, status, start_time
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, round_id, task_id, round_number, json.dumps(selected_clients),
                round_data['global_model_weights'], json.dumps({}),
                0.0, 0.0, 'running', datetime.now())
            
            # 保存到内存
            self.rounds[round_id] = round_data
            
            # 通知客户端开始新轮次
            await self._notify_clients_start_training(selected_clients, round_data)
            
            logger.info(f"开始第 {round_number} 轮训练")
            
        except Exception as e:
            logger.error(f"开始下一轮训练失败: {e}")
    
    async def _complete_training(self, task_id: str, final_model):
        """完成训练"""
        try:
            # 保存最终模型
            final_model_weights = self._serialize_model(final_model)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE federated_tasks 
                    SET status = 'completed' 
                    WHERE task_id = $1
                """, task_id)
                
                # 保存最终模型
                await conn.execute("""
                    INSERT INTO federated_models (task_id, model_weights, created_at)
                    VALUES ($1, $2, $3)
                """, task_id, final_model_weights, datetime.now())
            
            # 通知所有客户端训练完成
            await self._notify_training_completion(task_id, final_model_weights)
            
            logger.info(f"训练任务 {task_id} 完成")
            
        except Exception as e:
            logger.error(f"完成训练失败: {e}")
    
    async def _notify_training_completion(self, task_id: str, final_model_weights: str):
        """通知训练完成"""
        try:
            notification = {
                'type': 'training_completed',
                'task_id': task_id,
                'final_model_weights': final_model_weights,
                'timestamp': datetime.now().isoformat()
            }
            
            # 通知所有客户端
            for client_id in self.clients:
                if client_id in self.websocket_connections:
                    websocket = self.websocket_connections[client_id]
                    try:
                        await websocket.send_text(json.dumps(notification))
                    except:
                        pass
                
                # 保存到Redis队列
                await self.redis_client.lpush(
                    f"client_notifications:{client_id}",
                    json.dumps(notification)
                )
                
        except Exception as e:
            logger.error(f"通知训练完成失败: {e}")
    
    async def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            # 清理过期的轮次数据
            expiry_time = datetime.now() - timedelta(days=7)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM federated_rounds 
                    WHERE start_time < $1 AND status = 'completed'
                """, expiry_time)
                
                await conn.execute("""
                    DELETE FROM client_updates 
                    WHERE created_at < $1
                """, expiry_time)
                
        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")
    
    async def get_training_status(self, task_id: str) -> Dict:
        """获取训练状态"""
        try:
            async with self.db_pool.acquire() as conn:
                # 获取任务信息
                task_row = await conn.fetchrow("""
                    SELECT * FROM federated_tasks WHERE task_id = $1
                """, task_id)
                
                if not task_row:
                    return {"error": "任务不存在"}
                
                # 获取轮次信息
                round_rows = await conn.fetch("""
                    SELECT * FROM federated_rounds 
                    WHERE task_id = $1 
                    ORDER BY round_number
                """, task_id)
                
                # 获取客户端更新数量
                update_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM client_updates 
                    WHERE task_id = $1
                """, task_id)
                
                return {
                    "task_id": task_id,
                    "status": task_row['status'],
                    "total_rounds": len(round_rows),
                    "total_updates": update_count,
                    "rounds": [dict(row) for row in round_rows]
                }
                
        except Exception as e:
            logger.error(f"获取训练状态失败: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("联邦学习系统资源清理完成")
            
        except Exception as e:
            logger.error(f"清理资源失败: {e}")

# 辅助类
class PrivacyEngine:
    """隐私保护引擎"""
    
    def __init__(self):
        self.noise_multiplier = 1.0
        self.clipping_threshold = 1.0
        self.privacy_budget = 1.0
    
    def add_noise(self, data: np.ndarray) -> np.ndarray:
        """添加噪声"""
        noise = np.random.normal(0, self.noise_multiplier, data.shape)
        return data + noise
    
    def clip_gradients(self, gradients: np.ndarray) -> np.ndarray:
        """梯度裁剪"""
        norm = np.linalg.norm(gradients)
        if norm > self.clipping_threshold:
            gradients = gradients * (self.clipping_threshold / norm)
        return gradients

class ModelAggregator:
    """模型聚合器"""
    
    async def federated_averaging(self, client_updates: List, model_config: Dict):
        """联邦平均算法"""
        try:
            if not client_updates:
                return None
            
            # 计算权重
            total_data_size = sum(update['data_size'] for update in client_updates)
            weights = [update['data_size'] / total_data_size for update in client_updates]
            
            # 聚合模型权重
            aggregated_weights = None
            
            for i, update in enumerate(client_updates):
                # 反序列化模型权重
                model_weights = pickle.loads(
                    gzip.decompress(base64.b64decode(update['model_weights']))
                )
                
                if aggregated_weights is None:
                    aggregated_weights = {k: v * weights[i] for k, v in model_weights.items()}
                else:
                    for k, v in model_weights.items():
                        aggregated_weights[k] += v * weights[i]
            
            # 创建聚合后的模型
            model_type = model_config['model_type']
            architecture = model_config['architecture']
            
            if model_type == 'pytorch':
                # 创建PyTorch模型并加载权重
                model = self._create_pytorch_model(architecture)
                model.load_state_dict(aggregated_weights)
                return model
            elif model_type == 'tensorflow':
                # 创建TensorFlow模型并加载权重
                model = self._create_tensorflow_model(architecture)
                model.set_weights(list(aggregated_weights.values()))
                return model
            
            return None
            
        except Exception as e:
            logger.error(f"联邦平均失败: {e}")
            return None
    
    def _create_pytorch_model(self, architecture: Dict):
        """创建PyTorch模型"""
        # 这里应该与FederatedLearningSystem中的方法相同
        pass
    
    def _create_tensorflow_model(self, architecture: Dict):
        """创建TensorFlow模型"""
        # 这里应该与FederatedLearningSystem中的方法相同
        pass

class DifferentialPrivacy:
    """差分隐私"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
    
    def add_laplace_noise(self, data: np.ndarray, sensitivity: float) -> np.ndarray:
        """添加拉普拉斯噪声"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise
    
    def add_gaussian_noise(self, data: np.ndarray, sensitivity: float) -> np.ndarray:
        """添加高斯噪声"""
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        noise = np.random.normal(0, sigma, data.shape)
        return data + noise

# 全局联邦学习系统实例
fl_system = FederatedLearningSystem()

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await fl_system.initialize()
    yield
    # 关闭时清理
    await fl_system.cleanup()

# 创建FastAPI应用
app = FastAPI(
    title="联邦学习系统",
    description="分布式机器学习和隐私保护",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"user_id": "test_user", "username": "test"}

# API端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/clients/register")
async def register_client(
    client_info: ClientInfo,
    current_user: dict = Depends(get_current_user)
):
    """注册客户端"""
    try:
        await fl_system.register_client(client_info)
        return {"message": "客户端注册成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/create")
async def create_training_task(
    task: TrainingTask,
    current_user: dict = Depends(get_current_user)
):
    """创建训练任务"""
    try:
        await fl_system.create_training_task(task)
        return {"message": "训练任务创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/updates/submit")
async def submit_client_update(
    update: ClientUpdate,
    current_user: dict = Depends(get_current_user)
):
    """提交客户端更新"""
    try:
        await fl_system.submit_client_update(update)
        return {"message": "客户端更新提交成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}/status")
async def get_training_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取训练状态"""
    try:
        status = await fl_system.get_training_status(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clients")
async def get_clients(current_user: dict = Depends(get_current_user)):
    """获取客户端列表"""
    try:
        return {"clients": list(fl_system.clients.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks(current_user: dict = Depends(get_current_user)):
    """获取任务列表"""
    try:
        return {"tasks": list(fl_system.tasks.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接"""
    await websocket.accept()
    fl_system.websocket_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理客户端消息
            if message.get('type') == 'heartbeat':
                # 更新客户端活跃状态
                if client_id in fl_system.clients:
                    fl_system.clients[client_id]['last_active'] = datetime.now()
                
                # 发送心跳响应
                await websocket.send_text(json.dumps({
                    'type': 'heartbeat_response',
                    'timestamp': datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        # 客户端断开连接
        fl_system.websocket_connections.pop(client_id, None)
        if client_id in fl_system.clients:
            fl_system.clients[client_id]['status'] = 'inactive'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088) 