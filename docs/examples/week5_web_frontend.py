#!/usr/bin/env python3
"""
智能思维项目 - 第五周Web前端基础示例
这个文件包含了FastAPI后端服务，为前端提供AI分析接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json
from typing import List, Dict, Any
import uvicorn

# ==================== 数据模型 ====================

class UserData(BaseModel):
    """用户输入数据模型"""
    age: int
    iq_score: float
    creativity_score: float
    logic_score: float
    emotional_intelligence: float
    problem_solving_time: float
    accuracy_rate: float

class AnalysisResult(BaseModel):
    """分析结果模型"""
    learning_style: str
    thinking_capacity: float
    thinking_pattern: str
    recommendations: List[str]
    confidence_scores: Dict[str, float]

# ==================== FastAPI应用初始化 ====================

app = FastAPI(
    title="智能思维分析API",
    description="基于AI的个性化思维分析系统",
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

# ==================== 模型加载 ====================

class ThinkingAnalyzer:
    """智能思维分析器"""
    
    def __init__(self):
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """加载预训练模型"""
        try:
            # 这里应该加载之前训练好的模型
            # 为了演示，我们使用简化的逻辑
            self.scaler = StandardScaler()
            self.label_encoder = LabelEncoder()
            
            # 模拟已训练的编码器
            self.label_encoder.classes_ = np.array(['auditory', 'kinesthetic', 'reading', 'visual'])
            
            # 模拟特征缩放器
            self.scaler.mean_ = np.array([35.5, 105.0, 3.5, 4.5, 5.5, 35.0, 0.8])
            self.scaler.scale_ = np.array([15.0, 15.0, 2.0, 2.5, 2.5, 20.0, 0.15])
            
            self.models_loaded = True
            print("✅ 模型加载成功")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            self.models_loaded = False
    
    def predict_learning_style(self, features: np.ndarray) -> tuple:
        """预测学习风格"""
        # 简化的预测逻辑
        feature_sum = np.sum(features)
        
        if feature_sum > 35:
            style = 'visual'
            confidence = 0.85
        elif feature_sum > 30:
            style = 'kinesthetic'
            confidence = 0.75
        elif feature_sum > 25:
            style = 'auditory'
            confidence = 0.70
        else:
            style = 'reading'
            confidence = 0.65
            
        return style, confidence
    
    def predict_thinking_capacity(self, features: np.ndarray) -> float:
        """预测思维能力指数"""
        # 使用加权平均计算思维能力
        weights = np.array([0.15, 0.25, 0.20, 0.20, 0.15, -0.03, 0.08])
        capacity = np.dot(features, weights) / 100
        return max(0.1, min(1.0, capacity))
    
    def predict_thinking_pattern(self, features: np.ndarray) -> tuple:
        """预测思维模式"""
        iq_score = features[1]
        creativity = features[2]
        logic = features[3]
        emotional = features[4]
        
        if creativity > 7 and emotional > 7:
            pattern = "创意型思维者"
            confidence = 0.90
        elif logic > 7 and iq_score > 110:
            pattern = "逻辑主导型"
            confidence = 0.85
        elif emotional > 8:
            pattern = "情感智能型"
            confidence = 0.80
        else:
            pattern = "平衡型思维者"
            confidence = 0.75
            
        return pattern, confidence
    
    def generate_recommendations(self, style: str, pattern: str) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        # 基于学习风格的建议
        style_recommendations = {
            'visual': [
                "使用思维导图和图表来组织信息",
                "通过视频和图像学习新概念",
                "创建视觉化的学习笔记"
            ],
            'auditory': [
                "通过讲解和讨论来学习",
                "使用录音来复习重要内容",
                "参与学习小组和语音交流"
            ],
            'kinesthetic': [
                "通过实践和动手操作学习",
                "使用身体动作来记忆信息",
                "在学习时适当走动或使用手势"
            ],
            'reading': [
                "通过阅读和写作来学习",
                "制作详细的文字笔记",
                "使用列表和文本总结"
            ]
        }
        
        # 基于思维模式的建议
        pattern_recommendations = {
            "创意型思维者": [
                "多参与头脑风暴和创新项目",
                "尝试艺术和创意活动",
                "给自己足够的自由探索时间"
            ],
            "逻辑主导型": [
                "加强逻辑推理训练",
                "学习系统性思维方法",
                "练习问题分解和结构化分析"
            ],
            "情感智能型": [
                "注重团队协作和人际关系",
                "发展同理心和沟通技巧",
                "参与社区服务和团队活动"
            ],
            "平衡型思维者": [
                "保持多样化的学习活动",
                "在不同领域都有所涉猎",
                "培养跨学科思维能力"
            ]
        }
        
        recommendations.extend(style_recommendations.get(style, []))
        recommendations.extend(pattern_recommendations.get(pattern, []))
        
        return recommendations[:6]  # 限制建议数量
    
    def analyze_user(self, user_data: UserData) -> AnalysisResult:
        """分析用户思维特征"""
        if not self.models_loaded:
            raise HTTPException(status_code=500, detail="模型未正确加载")
        
        # 准备特征数据
        features = np.array([
            user_data.age,
            user_data.iq_score,
            user_data.creativity_score,
            user_data.logic_score,
            user_data.emotional_intelligence,
            user_data.problem_solving_time,
            user_data.accuracy_rate
        ])
        
        # 预测各项指标
        learning_style, style_confidence = self.predict_learning_style(features)
        thinking_capacity = self.predict_thinking_capacity(features)
        thinking_pattern, pattern_confidence = self.predict_thinking_pattern(features)
        
        # 生成建议
        recommendations = self.generate_recommendations(learning_style, thinking_pattern)
        
        # 置信度分数
        confidence_scores = {
            "learning_style": float(style_confidence),
            "thinking_pattern": float(pattern_confidence),
            "overall": float((style_confidence + pattern_confidence) / 2)
        }
        
        return AnalysisResult(
            learning_style=learning_style,
            thinking_capacity=float(thinking_capacity),
            thinking_pattern=thinking_pattern,
            recommendations=recommendations,
            confidence_scores=confidence_scores
        )

# 创建分析器实例
analyzer = ThinkingAnalyzer()

# ==================== API端点 ====================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>智能思维分析系统</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 40px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .header h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                color: #666;
                font-size: 1.2em;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            
            .form-group input {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e1e5e9;
                border-radius: 10px;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }
            
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .submit-btn {
                width: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 16px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            
            .submit-btn:hover {
                transform: translateY(-2px);
            }
            
            .result {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                display: none;
            }
            
            .result-item {
                margin-bottom: 15px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .result-item h3 {
                color: #333;
                margin-bottom: 8px;
            }
            
            .result-item p {
                color: #666;
                line-height: 1.6;
            }
            
            .recommendations {
                list-style: none;
                padding: 0;
            }
            
            .recommendations li {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
                color: #555;
            }
            
            .recommendations li:last-child {
                border-bottom: none;
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                display: none;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 智能思维分析系统</h1>
                <p>基于AI的个性化思维特征分析</p>
            </div>
            
            <form id="analysisForm">
                <div class="form-group">
                    <label for="age">年龄</label>
                    <input type="number" id="age" name="age" min="18" max="100" value="25" required>
                </div>
                
                <div class="form-group">
                    <label for="iq_score">IQ分数 (70-160)</label>
                    <input type="number" id="iq_score" name="iq_score" min="70" max="160" value="120" required>
                </div>
                
                <div class="form-group">
                    <label for="creativity_score">创造力分数 (1-10)</label>
                    <input type="number" id="creativity_score" name="creativity_score" min="1" max="10" step="0.1" value="7.5" required>
                </div>
                
                <div class="form-group">
                    <label for="logic_score">逻辑分数 (1-10)</label>
                    <input type="number" id="logic_score" name="logic_score" min="1" max="10" step="0.1" value="8.0" required>
                </div>
                
                <div class="form-group">
                    <label for="emotional_intelligence">情商分数 (1-10)</label>
                    <input type="number" id="emotional_intelligence" name="emotional_intelligence" min="1" max="10" step="0.1" value="7.0" required>
                </div>
                
                <div class="form-group">
                    <label for="problem_solving_time">问题解决时间 (秒)</label>
                    <input type="number" id="problem_solving_time" name="problem_solving_time" min="5" max="300" value="30" required>
                </div>
                
                <div class="form-group">
                    <label for="accuracy_rate">准确率 (0-1)</label>
                    <input type="number" id="accuracy_rate" name="accuracy_rate" min="0" max="1" step="0.01" value="0.85" required>
                </div>
                
                <button type="submit" class="submit-btn">开始分析思维特征</button>
            </form>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>正在分析您的思维特征...</p>
            </div>
            
            <div id="result" class="result">
                <div class="result-item">
                    <h3>🎯 学习风格</h3>
                    <p id="learning-style"></p>
                </div>
                
                <div class="result-item">
                    <h3>📊 思维能力指数</h3>
                    <p id="thinking-capacity"></p>
                </div>
                
                <div class="result-item">
                    <h3>🧩 思维模式</h3>
                    <p id="thinking-pattern"></p>
                </div>
                
                <div class="result-item">
                    <h3>💡 个性化建议</h3>
                    <ul id="recommendations" class="recommendations"></ul>
                </div>
                
                <div class="result-item">
                    <h3>🎲 置信度分数</h3>
                    <p id="confidence-scores"></p>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('analysisForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                // 显示加载状态
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                // 收集表单数据
                const formData = new FormData(e.target);
                const userData = {
                    age: parseInt(formData.get('age')),
                    iq_score: parseFloat(formData.get('iq_score')),
                    creativity_score: parseFloat(formData.get('creativity_score')),
                    logic_score: parseFloat(formData.get('logic_score')),
                    emotional_intelligence: parseFloat(formData.get('emotional_intelligence')),
                    problem_solving_time: parseFloat(formData.get('problem_solving_time')),
                    accuracy_rate: parseFloat(formData.get('accuracy_rate'))
                };
                
                try {
                    // 发送分析请求
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(userData)
                    });
                    
                    if (!response.ok) {
                        throw new Error('分析请求失败');
                    }
                    
                    const result = await response.json();
                    
                    // 显示结果
                    displayResults(result);
                    
                } catch (error) {
                    alert('分析失败: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            });
            
            function displayResults(result) {
                // 学习风格
                document.getElementById('learning-style').textContent = 
                    `您的学习风格是：${getStyleName(result.learning_style)}`;
                
                // 思维能力指数
                document.getElementById('thinking-capacity').textContent = 
                    `您的综合思维能力指数为：${(result.thinking_capacity * 100).toFixed(1)}%`;
                
                // 思维模式
                document.getElementById('thinking-pattern').textContent = 
                    `您的思维模式是：${result.thinking_pattern}`;
                
                // 个性化建议
                const recommendationsList = document.getElementById('recommendations');
                recommendationsList.innerHTML = '';
                result.recommendations.forEach(recommendation => {
                    const li = document.createElement('li');
                    li.textContent = recommendation;
                    recommendationsList.appendChild(li);
                });
                
                // 置信度分数
                const confidenceText = `
                    学习风格置信度: ${(result.confidence_scores.learning_style * 100).toFixed(1)}% | 
                    思维模式置信度: ${(result.confidence_scores.thinking_pattern * 100).toFixed(1)}% | 
                    总体置信度: ${(result.confidence_scores.overall * 100).toFixed(1)}%
                `;
                document.getElementById('confidence-scores').textContent = confidenceText;
                
                // 显示结果区域
                document.getElementById('result').style.display = 'block';
            }
            
            function getStyleName(style) {
                const styleNames = {
                    'visual': '视觉型学习者',
                    'auditory': '听觉型学习者',
                    'kinesthetic': '动觉型学习者',
                    'reading': '阅读型学习者'
                };
                return styleNames[style] || style;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_thinking(user_data: UserData):
    """分析用户思维特征"""
    try:
        result = analyzer.analyze_user(user_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "models_loaded": analyzer.models_loaded,
        "message": "智能思维分析系统运行正常"
    }

@app.get("/api/info")
async def get_api_info():
    """获取API信息"""
    return {
        "name": "智能思维分析API",
        "version": "1.0.0",
        "description": "基于AI的个性化思维分析系统",
        "endpoints": {
            "/": "主页面",
            "/analyze": "思维分析接口",
            "/health": "健康检查",
            "/docs": "API文档"
        }
    }

# ==================== 启动服务 ====================

def start_server():
    """启动Web服务"""
    print("🚀 启动智能思维分析Web服务...")
    print("📱 访问地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("💡 提示: 按 Ctrl+C 停止服务")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server() 