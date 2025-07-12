#!/usr/bin/env python3
"""
智能思维项目 - 第六周3D思维空间集成
这个文件集成了AI分析和3D可视化功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
import json
import math
import uvicorn

# ==================== 数据模型 ====================

class ThinkingNode(BaseModel):
    """思维节点模型"""
    id: int
    concept: str
    position: Dict[str, float]  # x, y, z
    strength: float
    node_type: str
    connections: List[int]

class ThinkingSpace(BaseModel):
    """思维空间模型"""
    nodes: List[ThinkingNode]
    connections: List[Dict[str, Any]]
    mode: str
    metadata: Dict[str, Any]

class UserThinkingData(BaseModel):
    """用户思维数据"""
    creativity_score: float
    logic_score: float
    emotional_intelligence: float
    focus_level: float
    thinking_style: str
    preferences: Optional[Dict[str, Any]] = {}

class Space3DRequest(BaseModel):
    """3D空间生成请求"""
    user_data: UserThinkingData
    node_count: int = 50
    connection_strength: float = 0.5
    thinking_mode: str = "creative"

# ==================== FastAPI应用初始化 ====================

app = FastAPI(
    title="智能思维3D空间API",
    description="基于AI的3D思维空间可视化系统",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 3D思维空间生成器 ====================

class ThinkingSpaceGenerator:
    """3D思维空间生成器"""
    
    def __init__(self):
        # 不同思维模式的概念库
        self.concept_libraries = {
            'creative': [
                '创意', '想象', '艺术', '创新', '灵感', '直觉', '美感', '表达',
                '原创', '构思', '设计', '色彩', '音乐', '诗歌', '故事', '梦想',
                '幻想', '联想', '比喻', '象征', '风格', '形式', '内容', '主题'
            ],
            'logical': [
                '逻辑', '推理', '分析', '证明', '归纳', '演绎', '因果', '结构',
                '系统', '方法', '步骤', '规律', '原理', '定律', '公式', '算法',
                '模式', '框架', '体系', '层次', '分类', '比较', '判断', '决策'
            ],
            'analytical': [
                '数据', '统计', '模式', '趋势', '比较', '评估', '量化', '测量',
                '指标', '变量', '相关', '回归', '预测', '建模', '优化', '效率',
                '性能', '质量', '准确', '精确', '误差', '范围', '分布', '概率'
            ],
            'intuitive': [
                '直觉', '感受', '预感', '洞察', '理解', '共鸣', '感知', '领悟',
                '意识', '潜意识', '第六感', '心理', '情感', '感情', '体验', '感觉',
                '氛围', '气质', '个性', '风格', '印象', '感染', '共振', '和谐'
            ]
        }
        
        self.color_schemes = {
            'creative': {'primary': '#ff6b9d', 'secondary': '#c44569', 'accent': '#f8b500'},
            'logical': {'primary': '#4ecdc4', 'secondary': '#26a0da', 'accent': '#0abde3'},
            'analytical': {'primary': '#45b7d1', 'secondary': '#96ceb4', 'accent': '#feca57'},
            'intuitive': {'primary': '#f9ca24', 'secondary': '#f0932b', 'accent': '#eb4d4b'}
        }
    
    def generate_thinking_space(self, request: Space3DRequest) -> ThinkingSpace:
        """生成个性化的3D思维空间"""
        user_data = request.user_data
        
        # 根据用户数据调整空间参数
        adjusted_params = self._adjust_space_parameters(user_data, request)
        
        # 生成思维节点
        nodes = self._generate_nodes(adjusted_params)
        
        # 生成连接
        connections = self._generate_connections(nodes, adjusted_params)
        
        # 创建元数据
        metadata = self._create_metadata(user_data, adjusted_params)
        
        return ThinkingSpace(
            nodes=nodes,
            connections=connections,
            mode=request.thinking_mode,
            metadata=metadata
        )
    
    def _adjust_space_parameters(self, user_data: UserThinkingData, request: Space3DRequest) -> Dict[str, Any]:
        """根据用户数据调整空间参数"""
        params = {
            'node_count': request.node_count,
            'connection_strength': request.connection_strength,
            'thinking_mode': request.thinking_mode,
            'space_radius': 50,
            'node_size_range': (0.8, 2.0),
            'connection_opacity_range': (0.2, 0.8)
        }
        
        # 根据创造力调整节点分布
        if user_data.creativity_score > 7:
            params['space_radius'] = 60  # 更大的空间
            params['node_size_range'] = (1.0, 2.5)  # 更大的节点
        
        # 根据逻辑性调整连接密度
        if user_data.logic_score > 7:
            params['connection_strength'] *= 1.3  # 更多连接
        
        # 根据情商调整颜色强度
        if user_data.emotional_intelligence > 7:
            params['color_intensity'] = 1.2
        else:
            params['color_intensity'] = 0.8
        
        # 根据专注度调整动画速度
        params['animation_speed'] = user_data.focus_level / 10.0
        
        return params
    
    def _generate_nodes(self, params: Dict[str, Any]) -> List[ThinkingNode]:
        """生成思维节点"""
        nodes = []
        concepts = self.concept_libraries[params['thinking_mode']]
        node_count = params['node_count']
        
        for i in range(node_count):
            # 选择概念
            concept = concepts[i % len(concepts)]
            
            # 生成3D位置（球形分布）
            position = self._generate_spherical_position(params['space_radius'])
            
            # 根据概念重要性调整强度
            strength = self._calculate_node_strength(concept, params)
            
            node = ThinkingNode(
                id=i,
                concept=concept,
                position=position,
                strength=strength,
                node_type=params['thinking_mode'],
                connections=[]
            )
            
            nodes.append(node)
        
        return nodes
    
    def _generate_spherical_position(self, radius: float) -> Dict[str, float]:
        """生成球形分布的3D位置"""
        # 使用球坐标系生成均匀分布
        theta = np.random.uniform(0, 2 * np.pi)  # 方位角
        phi = np.random.uniform(0, np.pi)        # 极角
        r = np.random.uniform(0.3, 1.0) * radius  # 半径
        
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        return {'x': float(x), 'y': float(y), 'z': float(z)}
    
    def _calculate_node_strength(self, concept: str, params: Dict[str, Any]) -> float:
        """计算节点强度"""
        base_strength = np.random.uniform(0.3, 1.0)
        
        # 根据思维模式调整强度
        mode = params['thinking_mode']
        if mode == 'creative' and concept in ['创意', '想象', '灵感']:
            base_strength *= 1.5
        elif mode == 'logical' and concept in ['逻辑', '推理', '分析']:
            base_strength *= 1.5
        elif mode == 'analytical' and concept in ['数据', '统计', '分析']:
            base_strength *= 1.5
        elif mode == 'intuitive' and concept in ['直觉', '感受', '洞察']:
            base_strength *= 1.5
        
        return min(1.0, base_strength)
    
    def _generate_connections(self, nodes: List[ThinkingNode], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成节点连接"""
        connections = []
        connection_strength = params['connection_strength']
        
        for i, node_a in enumerate(nodes):
            for j, node_b in enumerate(nodes[i+1:], i+1):
                # 计算节点距离
                distance = self._calculate_distance(node_a.position, node_b.position)
                
                # 根据距离和概念相关性决定是否连接
                connection_probability = self._calculate_connection_probability(
                    node_a, node_b, distance, connection_strength
                )
                
                if np.random.random() < connection_probability:
                    connection = {
                        'id': len(connections),
                        'source': node_a.id,
                        'target': node_b.id,
                        'strength': np.random.uniform(0.3, 1.0),
                        'type': self._determine_connection_type(node_a, node_b)
                    }
                    connections.append(connection)
                    
                    # 更新节点连接信息
                    node_a.connections.append(node_b.id)
                    node_b.connections.append(node_a.id)
        
        return connections
    
    def _calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """计算两点间的3D距离"""
        dx = pos1['x'] - pos2['x']
        dy = pos1['y'] - pos2['y']
        dz = pos1['z'] - pos2['z']
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _calculate_connection_probability(self, node_a: ThinkingNode, node_b: ThinkingNode, 
                                       distance: float, strength: float) -> float:
        """计算连接概率"""
        # 距离因子：距离越近，连接概率越高
        distance_factor = max(0, 1 - distance / 80)
        
        # 概念相关性因子
        concept_similarity = self._calculate_concept_similarity(node_a.concept, node_b.concept)
        
        # 强度因子
        strength_factor = (node_a.strength + node_b.strength) / 2
        
        # 综合概率
        probability = distance_factor * concept_similarity * strength_factor * strength
        
        return min(1.0, probability)
    
    def _calculate_concept_similarity(self, concept1: str, concept2: str) -> float:
        """计算概念相似度（简化版）"""
        # 简单的语义相似度计算
        similarity_map = {
            ('创意', '想象'): 0.9, ('逻辑', '推理'): 0.9, ('数据', '统计'): 0.9,
            ('直觉', '感受'): 0.9, ('分析', '评估'): 0.8, ('艺术', '美感'): 0.8,
            ('系统', '结构'): 0.8, ('感知', '意识'): 0.8
        }
        
        # 检查预定义的相似度
        for (c1, c2), sim in similarity_map.items():
            if (concept1 == c1 and concept2 == c2) or (concept1 == c2 and concept2 == c1):
                return sim
        
        # 默认相似度
        return np.random.uniform(0.1, 0.4)
    
    def _determine_connection_type(self, node_a: ThinkingNode, node_b: ThinkingNode) -> str:
        """确定连接类型"""
        connection_types = [
            'association',  # 关联
            'causation',    # 因果
            'similarity',   # 相似
            'contrast',     # 对比
            'hierarchy'     # 层次
        ]
        
        return np.random.choice(connection_types)
    
    def _create_metadata(self, user_data: UserThinkingData, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建空间元数据"""
        return {
            'generated_at': pd.Timestamp.now().isoformat(),
            'user_profile': {
                'creativity': user_data.creativity_score,
                'logic': user_data.logic_score,
                'emotional_intelligence': user_data.emotional_intelligence,
                'focus': user_data.focus_level,
                'style': user_data.thinking_style
            },
            'space_config': params,
            'color_scheme': self.color_schemes[params['thinking_mode']],
            'statistics': {
                'total_nodes': params['node_count'],
                'connection_density': params['connection_strength'],
                'space_complexity': params['node_count'] * params['connection_strength']
            }
        }

# 创建生成器实例
space_generator = ThinkingSpaceGenerator()

# ==================== API端点 ====================

@app.get("/3d", response_class=HTMLResponse)
async def get_3d_space():
    """返回3D思维空间页面"""
    try:
        with open('examples/week6_3d_thinking_space.html', 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="3D页面文件未找到")

@app.post("/api/generate-space", response_model=ThinkingSpace)
async def generate_thinking_space(request: Space3DRequest):
    """生成个性化3D思维空间"""
    try:
        thinking_space = space_generator.generate_thinking_space(request)
        return thinking_space
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成3D空间失败: {str(e)}")

@app.get("/api/space-templates")
async def get_space_templates():
    """获取空间模板"""
    templates = {
        'creative': {
            'name': '创意思维空间',
            'description': '激发创造力和想象力的3D环境',
            'color': '#ff6b9d',
            'features': ['发散思维', '艺术创作', '灵感涌现']
        },
        'logical': {
            'name': '逻辑思维空间',
            'description': '结构化思考和推理的3D环境',
            'color': '#4ecdc4',
            'features': ['系统分析', '逻辑推理', '问题解决']
        },
        'analytical': {
            'name': '分析思维空间',
            'description': '数据分析和模式识别的3D环境',
            'color': '#45b7d1',
            'features': ['数据挖掘', '趋势分析', '决策支持']
        },
        'intuitive': {
            'name': '直觉思维空间',
            'description': '感性认知和直觉洞察的3D环境',
            'color': '#f9ca24',
            'features': ['直觉感知', '情感理解', '洞察发现']
        }
    }
    return templates

@app.get("/api/thinking-analysis/{space_id}")
async def analyze_thinking_patterns(space_id: str):
    """分析思维模式"""
    # 模拟思维分析结果
    analysis = {
        'space_id': space_id,
        'analysis_time': pd.Timestamp.now().isoformat(),
        'patterns': {
            'dominant_clusters': np.random.randint(2, 6),
            'connection_strength': np.random.uniform(0.3, 0.9),
            'thinking_diversity': np.random.uniform(0.4, 1.0),
            'cognitive_load': np.random.uniform(0.2, 0.8)
        },
        'insights': [
            '您的思维网络显示出强烈的创造性倾向',
            '逻辑思维和直觉思维之间存在良好的平衡',
            '建议增强概念间的深层连接',
            '您的思维模式适合复杂问题解决'
        ],
        'recommendations': [
            '尝试增加更多跨领域的概念连接',
            '定期进行思维空间的重构练习',
            '关注弱连接节点的强化训练'
        ]
    }
    return analysis

@app.get("/")
async def read_root():
    """主页重定向到3D空间"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能思维3D空间</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; margin: 10px; text-decoration: none; display: inline-block; }
            .btn:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 智能思维3D空间系统</h1>
            <p>探索您的思维世界，在3D空间中可视化思考过程</p>
            
            <a href="/3d" class="btn">🌐 进入3D思维空间</a>
            <a href="/docs" class="btn">📚 API文档</a>
            
            <h3>功能特色</h3>
            <ul style="text-align: left;">
                <li>🎯 个性化3D思维空间生成</li>
                <li>🧠 AI驱动的思维模式分析</li>
                <li>🔗 智能概念连接可视化</li>
                <li>🎮 沉浸式VR/AR体验支持</li>
                <li>📊 实时思维性能监控</li>
            </ul>
        </div>
    </body>
    </html>
    """)

# ==================== 启动服务 ====================

def start_3d_server():
    """启动3D思维空间服务"""
    print("🚀 启动智能思维3D空间服务...")
    print("🌐 主页: http://localhost:8001")
    print("🧠 3D空间: http://localhost:8001/3d")
    print("📚 API文档: http://localhost:8001/docs")
    print("💡 提示: 按 Ctrl+C 停止服务")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_3d_server() 