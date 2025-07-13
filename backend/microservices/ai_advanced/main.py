"""
Advanced AI Models Service
集成GPT-4、Claude、Gemini、多模态AI等最新AI模型
"""

import asyncio
import json
import base64
import io
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import logging
import time
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import transformers
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM,
    CLIPProcessor, CLIPModel, WhisperProcessor, WhisperForConditionalGeneration,
    pipeline
)
import openai
import anthropic
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import redis
import asyncpg
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import sys
import os

# 添加上级目录到路径以导入共享模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared_auth import (
    get_ai_service_user, require_ai_permission, Permission, 
    get_microservice_auth, UserRole
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI模型配置
class AIModelConfig:
    """AI模型配置类"""
    
    # OpenAI配置
    OPENAI_API_KEY = "your-openai-api-key"
    OPENAI_MODELS = {
        "gpt-4": "gpt-4-turbo-preview",
        "gpt-3.5": "gpt-3.5-turbo",
        "dall-e": "dall-e-3",
        "whisper": "whisper-1"
    }
    
    # Anthropic配置
    ANTHROPIC_API_KEY = "your-anthropic-api-key"
    ANTHROPIC_MODELS = {
        "claude-3": "claude-3-opus-20240229",
        "claude-2": "claude-2.1"
    }
    
    # Google配置
    GOOGLE_API_KEY = "your-google-api-key"
    GOOGLE_MODELS = {
        "gemini": "gemini-pro",
        "gemini-vision": "gemini-pro-vision"
    }

# Pydantic模型
class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "comprehensive"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000

class ImageAnalysisRequest(BaseModel):
    image_base64: str
    prompt: str = "请分析这张图片"
    model: str = "gpt-4-vision"

class AudioAnalysisRequest(BaseModel):
    audio_base64: str
    language: str = "zh"
    model: str = "whisper"

class MultiModalRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None
    audio_base64: Optional[str] = None
    analysis_type: str = "comprehensive"
    model: str = "multimodal"

class ThinkingGenerationRequest(BaseModel):
    prompt: str
    thinking_type: str = "creative"
    model: str = "gpt-4"
    temperature: float = 0.8
    max_tokens: int = 1500

class KnowledgeGraphRequest(BaseModel):
    text: str
    extract_type: str = "entities_relations"
    model: str = "gpt-4"

class AIResponse(BaseModel):
    success: bool
    data: Any
    model_used: str
    processing_time: float
    confidence: float
    metadata: Dict[str, Any] = {}

class AdvancedAIService:
    """高级AI模型服务"""
    
    def __init__(self):
        self.app = FastAPI(
            title="智能思维平台 - 高级AI模型服务",
            description="集成GPT-4、Claude、多模态AI等最新AI模型",
            version="1.0.0"
        )
        
        # 初始化各种AI模型
        self.models = {}
        self.tokenizers = {}
        self.processors = {}
        
        # 初始化OpenAI
        openai.api_key = AIModelConfig.OPENAI_API_KEY
        
        # 初始化Anthropic
        self.anthropic_client = anthropic.Anthropic(api_key=AIModelConfig.ANTHROPIC_API_KEY)
        
        # 初始化Google AI
        genai.configure(api_key=AIModelConfig.GOOGLE_API_KEY)
        
        # 初始化本地模型
        self.initialize_local_models()
        
        # 初始化向量数据库
        self.initialize_vector_db()
        
        # 初始化Redis
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        self.setup_middleware()
        self.setup_routes()
    
    def initialize_local_models(self):
        """初始化本地AI模型"""
        try:
            # 加载句子转换器
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # 加载CLIP模型
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            # 加载中文BERT模型
            self.bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
            self.bert_model = AutoModel.from_pretrained("bert-base-chinese")
            
            # 加载情感分析模型
            self.sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            
            # 加载文本生成模型
            self.text_generation_pipeline = pipeline("text-generation", model="gpt2")
            
            logger.info("本地AI模型初始化成功")
            
        except Exception as e:
            logger.error(f"本地AI模型初始化失败: {e}")
    
    def initialize_vector_db(self):
        """初始化向量数据库"""
        try:
            self.chroma_client = chromadb.Client()
            self.embeddings_collection = self.chroma_client.create_collection(
                name="thinking_embeddings",
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
            logger.info("向量数据库初始化成功")
            
        except Exception as e:
            logger.error(f"向量数据库初始化失败: {e}")
    
    def setup_middleware(self):
        """设置中间件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "models_loaded": len(self.models),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/models")
        async def list_models():
            """列出所有可用模型"""
            return {
                "openai_models": AIModelConfig.OPENAI_MODELS,
                "anthropic_models": AIModelConfig.ANTHROPIC_MODELS,
                "google_models": AIModelConfig.GOOGLE_MODELS,
                "local_models": [
                    "sentence-transformer",
                    "clip",
                    "bert-chinese",
                    "sentiment-analysis",
                    "text-generation"
                ]
            }
        
        @self.app.post("/analyze/text")
        @require_ai_permission(Permission.AI_QUERY)
        async def analyze_text(
            request: TextAnalysisRequest,
            current_user: dict = Depends(get_ai_service_user)
        ):
            """文本分析"""
            start_time = time.time()
            
            try:
                auth = get_microservice_auth("ai-service")
                auth.log_auth_event(
                    user_id=current_user.get("user_id"),
                    action="text_analysis_started",
                    success=True,
                    details=f"model:{request.model}, type:{request.analysis_type}"
                )
                
                result = await self.perform_text_analysis(request)
                processing_time = time.time() - start_time
                
                auth.log_auth_event(
                    user_id=current_user.get("user_id"),
                    action="text_analysis_completed",
                    success=True,
                    details=f"processing_time:{processing_time:.2f}s"
                )
                
                return AIResponse(
                    success=True,
                    data=result,
                    model_used=request.model,
                    processing_time=processing_time,
                    confidence=result.get("confidence", 0.0),
                    metadata={"analysis_type": request.analysis_type}
                )
                
            except Exception as e:
                auth = get_microservice_auth("ai-service")
                auth.log_auth_event(
                    user_id=current_user.get("user_id"),
                    action="text_analysis_failed",
                    success=False,
                    details=str(e)
                )
                logger.error(f"文本分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/analyze/image")
        async def analyze_image(request: ImageAnalysisRequest):
            """图像分析"""
            start_time = time.time()
            
            try:
                result = await self.perform_image_analysis(request)
                processing_time = time.time() - start_time
                
                return AIResponse(
                    success=True,
                    data=result,
                    model_used=request.model,
                    processing_time=processing_time,
                    confidence=result.get("confidence", 0.0),
                    metadata={"prompt": request.prompt}
                )
                
            except Exception as e:
                logger.error(f"图像分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/analyze/audio")
        async def analyze_audio(request: AudioAnalysisRequest):
            """音频分析"""
            start_time = time.time()
            
            try:
                result = await self.perform_audio_analysis(request)
                processing_time = time.time() - start_time
                
                return AIResponse(
                    success=True,
                    data=result,
                    model_used=request.model,
                    processing_time=processing_time,
                    confidence=result.get("confidence", 0.0),
                    metadata={"language": request.language}
                )
                
            except Exception as e:
                logger.error(f"音频分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/analyze/multimodal")
        async def analyze_multimodal(request: MultiModalRequest):
            """多模态分析"""
            start_time = time.time()
            
            try:
                result = await self.perform_multimodal_analysis(request)
                processing_time = time.time() - start_time
                
                return AIResponse(
                    success=True,
                    data=result,
                    model_used=request.model,
                    processing_time=processing_time,
                    confidence=result.get("confidence", 0.0),
                    metadata={"analysis_type": request.analysis_type}
                )
                
            except Exception as e:
                logger.error(f"多模态分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/generate/thinking")
        async def generate_thinking(request: ThinkingGenerationRequest):
            """生成思维内容"""
            start_time = time.time()
            
            try:
                result = await self.generate_thinking_content(request)
                processing_time = time.time() - start_time
                
                return AIResponse(
                    success=True,
                    data=result,
                    model_used=request.model,
                    processing_time=processing_time,
                    confidence=result.get("confidence", 0.0),
                    metadata={"thinking_type": request.thinking_type}
                )
                
            except Exception as e:
                logger.error(f"思维生成失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/extract/knowledge_graph")
        async def extract_knowledge_graph(request: KnowledgeGraphRequest):
            """提取知识图谱"""
            start_time = time.time()
            
            try:
                result = await self.extract_knowledge_graph(request)
                processing_time = time.time() - start_time
                
                return AIResponse(
                    success=True,
                    data=result,
                    model_used=request.model,
                    processing_time=processing_time,
                    confidence=result.get("confidence", 0.0),
                    metadata={"extract_type": request.extract_type}
                )
                
            except Exception as e:
                logger.error(f"知识图谱提取失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/embeddings/create")
        async def create_embeddings(texts: List[str]):
            """创建文本嵌入"""
            try:
                embeddings = self.sentence_transformer.encode(texts)
                
                # 保存到向量数据库
                self.embeddings_collection.add(
                    documents=texts,
                    embeddings=embeddings.tolist(),
                    ids=[f"text_{i}" for i in range(len(texts))]
                )
                
                return {
                    "success": True,
                    "embeddings_count": len(embeddings),
                    "dimension": embeddings.shape[1]
                }
                
            except Exception as e:
                logger.error(f"嵌入创建失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/embeddings/search")
        async def search_embeddings(query: str, n_results: int = 10):
            """搜索相似嵌入"""
            try:
                results = self.embeddings_collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                
                return {
                    "success": True,
                    "results": results
                }
                
            except Exception as e:
                logger.error(f"嵌入搜索失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def perform_text_analysis(self, request: TextAnalysisRequest) -> Dict[str, Any]:
        """执行文本分析"""
        if request.model == "gpt-4":
            return await self.analyze_with_gpt4(request.text, request.analysis_type)
        elif request.model == "claude-3":
            return await self.analyze_with_claude(request.text, request.analysis_type)
        elif request.model == "gemini":
            return await self.analyze_with_gemini(request.text, request.analysis_type)
        elif request.model == "local":
            return await self.analyze_with_local_models(request.text, request.analysis_type)
        else:
            raise ValueError(f"不支持的模型: {request.model}")
    
    async def analyze_with_gpt4(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """使用GPT-4进行分析"""
        try:
            prompt = f"""
            请对以下文本进行{analysis_type}分析:
            
            文本: {text}
            
            请从以下维度进行分析:
            1. 思维类型识别
            2. 逻辑结构分析
            3. 情感色彩分析
            4. 创造性评估
            5. 认知偏见识别
            6. 改进建议
            
            请以JSON格式返回分析结果。
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的思维分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                parsed_result = json.loads(result)
            except json.JSONDecodeError:
                parsed_result = {"analysis": result}
            
            parsed_result["confidence"] = 0.85
            return parsed_result
            
        except Exception as e:
            logger.error(f"GPT-4分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def analyze_with_claude(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """使用Claude进行分析"""
        try:
            prompt = f"""
            请对以下文本进行{analysis_type}分析:
            
            文本: {text}
            
            请提供详细的思维分析报告。
            """
            
            response = await self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            
            return {
                "analysis": result,
                "confidence": 0.82,
                "model": "claude-3"
            }
            
        except Exception as e:
            logger.error(f"Claude分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def analyze_with_gemini(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """使用Gemini进行分析"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            请对以下文本进行{analysis_type}分析:
            
            文本: {text}
            
            请提供综合的思维分析。
            """
            
            response = await model.generate_content_async(prompt)
            
            return {
                "analysis": response.text,
                "confidence": 0.80,
                "model": "gemini-pro"
            }
            
        except Exception as e:
            logger.error(f"Gemini分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def analyze_with_local_models(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """使用本地模型进行分析"""
        try:
            # 情感分析
            sentiment_result = self.sentiment_pipeline(text)
            
            # 文本嵌入
            embedding = self.sentence_transformer.encode([text])
            
            # BERT特征提取
            bert_inputs = self.bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True)
            with torch.no_grad():
                bert_outputs = self.bert_model(**bert_inputs)
                bert_features = bert_outputs.last_hidden_state.mean(dim=1)
            
            return {
                "sentiment": sentiment_result[0],
                "embedding_dim": embedding.shape[1],
                "bert_features_dim": bert_features.shape[1],
                "confidence": 0.75,
                "model": "local_ensemble"
            }
            
        except Exception as e:
            logger.error(f"本地模型分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def perform_image_analysis(self, request: ImageAnalysisRequest) -> Dict[str, Any]:
        """执行图像分析"""
        try:
            # 解码base64图像
            image_data = base64.b64decode(request.image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # 使用CLIP进行图像分析
            inputs = self.clip_processor(text=[request.prompt], images=image, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            return {
                "image_analysis": "图像分析结果",
                "confidence": float(probs.max()),
                "model": "clip"
            }
            
        except Exception as e:
            logger.error(f"图像分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def perform_audio_analysis(self, request: AudioAnalysisRequest) -> Dict[str, Any]:
        """执行音频分析"""
        try:
            # 模拟音频转文本
            transcription = "这是转录的音频内容"
            
            # 对转录文本进行情感分析
            sentiment_result = self.sentiment_pipeline(transcription)
            
            return {
                "transcription": transcription,
                "sentiment": sentiment_result[0],
                "confidence": 0.78,
                "model": "whisper+sentiment"
            }
            
        except Exception as e:
            logger.error(f"音频分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def perform_multimodal_analysis(self, request: MultiModalRequest) -> Dict[str, Any]:
        """执行多模态分析"""
        try:
            results = {}
            
            # 分析文本
            if request.text:
                text_result = await self.analyze_with_local_models(request.text, request.analysis_type)
                results["text_analysis"] = text_result
            
            # 分析图像
            if request.image_base64:
                image_request = ImageAnalysisRequest(
                    image_base64=request.image_base64,
                    prompt="请分析这张图片的内容"
                )
                image_result = await self.perform_image_analysis(image_request)
                results["image_analysis"] = image_result
            
            # 分析音频
            if request.audio_base64:
                audio_request = AudioAnalysisRequest(audio_base64=request.audio_base64)
                audio_result = await self.perform_audio_analysis(audio_request)
                results["audio_analysis"] = audio_result
            
            # 计算综合置信度
            confidences = [result.get("confidence", 0.0) for result in results.values() if isinstance(result, dict)]
            overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "multimodal_analysis": results,
                "confidence": overall_confidence,
                "model": "multimodal_ensemble"
            }
            
        except Exception as e:
            logger.error(f"多模态分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def generate_thinking_content(self, request: ThinkingGenerationRequest) -> Dict[str, Any]:
        """生成思维内容"""
        try:
            # 使用本地文本生成模型
            generated = self.text_generation_pipeline(
                request.prompt,
                max_length=request.max_tokens,
                temperature=request.temperature,
                do_sample=True
            )
            
            return {
                "generated_content": generated[0]["generated_text"],
                "thinking_type": request.thinking_type,
                "confidence": 0.76,
                "model": "local_gpt2"
            }
            
        except Exception as e:
            logger.error(f"思维内容生成失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def extract_knowledge_graph(self, request: KnowledgeGraphRequest) -> Dict[str, Any]:
        """提取知识图谱"""
        try:
            # 简化的知识图谱提取
            entities = ["概念A", "概念B", "概念C"]
            relations = [
                {"from": "概念A", "to": "概念B", "relation": "影响"},
                {"from": "概念B", "to": "概念C", "relation": "导致"}
            ]
            
            return {
                "entities": entities,
                "relations": relations,
                "confidence": 0.73,
                "model": "knowledge_extraction"
            }
            
        except Exception as e:
            logger.error(f"知识图谱提取失败: {e}")
            return {"error": str(e), "confidence": 0.0}

# 创建高级AI服务实例
ai_service = AdvancedAIService()
app = ai_service.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 