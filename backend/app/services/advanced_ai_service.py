"""
高级AI服务模块
集成多种最新AI模型，提供企业级AI能力
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import openai
import anthropic
import google.generativeai as genai
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np
from PIL import Image
import io
import base64
import json
import aiohttp
from pydantic import BaseModel, Field

from ..core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class AIModelConfig(BaseModel):
    """AI模型配置"""
    name: str
    api_key: str
    model_id: str
    max_tokens: int = 4000
    temperature: float = 0.7
    enabled: bool = True

class MultiModalInput(BaseModel):
    """多模态输入"""
    text: Optional[str] = None
    image: Optional[str] = None  # base64编码
    audio: Optional[str] = None
    video: Optional[str] = None

class AIResponse(BaseModel):
    """AI响应"""
    model_name: str
    response_text: str
    confidence: float
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    token_usage: Optional[Dict[str, int]] = None

class ThinkingAnalysisResult(BaseModel):
    """思维分析结果"""
    thinking_style: str
    confidence: float
    analysis: Dict[str, Any]
    suggestions: List[str]
    cognitive_patterns: Dict[str, float]
    creativity_score: float
    logic_score: float
    intuition_score: float

class AdvancedAIService:
    """高级AI服务"""
    
    def __init__(self):
        self.models = {}
        self.local_models = {}
        self._initialize_models()
        
    def _initialize_models(self):
        """初始化AI模型"""
        try:
            # OpenAI GPT-4
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.models['gpt-4'] = AIModelConfig(
                    name="GPT-4",
                    api_key=settings.OPENAI_API_KEY,
                    model_id="gpt-4-turbo-preview",
                    max_tokens=4000,
                    temperature=0.7
                )
                logger.info("GPT-4 模型已初始化")
            
            # Anthropic Claude
            if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
                self.models['claude'] = AIModelConfig(
                    name="Claude",
                    api_key=settings.ANTHROPIC_API_KEY,
                    model_id="claude-3-opus-20240229",
                    max_tokens=4000,
                    temperature=0.7
                )
                logger.info("Claude 模型已初始化")
            
            # Google Gemini
            if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.models['gemini'] = AIModelConfig(
                    name="Gemini",
                    api_key=settings.GOOGLE_API_KEY,
                    model_id="gemini-pro",
                    max_tokens=4000,
                    temperature=0.7
                )
                logger.info("Gemini 模型已初始化")
            
            # 本地模型初始化
            self._initialize_local_models()
            
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
    
    def _initialize_local_models(self):
        """初始化本地模型"""
        try:
            # 情感分析模型
            self.local_models['sentiment'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # 文本分类模型
            self.local_models['classification'] = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"
            )
            
            # 嵌入模型
            self.local_models['embeddings'] = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            logger.info("本地模型已初始化")
            
        except Exception as e:
            logger.warning(f"本地模型初始化失败: {e}")
    
    async def analyze_thinking_advanced(
        self, 
        text: str, 
        model_name: str = "gpt-4",
        context: Optional[Dict[str, Any]] = None
    ) -> ThinkingAnalysisResult:
        """高级思维分析"""
        try:
            # 构建分析提示
            analysis_prompt = self._build_thinking_analysis_prompt(text, context)
            
            # 获取AI分析
            ai_response = await self._get_ai_response(analysis_prompt, model_name)
            
            # 解析分析结果
            analysis_result = self._parse_thinking_analysis(ai_response, text)
            
            # 结合本地模型增强分析
            enhanced_result = await self._enhance_with_local_models(analysis_result, text)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"高级思维分析失败: {e}")
            # 返回基础分析
            return await self._fallback_analysis(text)
    
    def _build_thinking_analysis_prompt(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建思维分析提示"""
        base_prompt = f"""
作为一位认知科学专家和AI思维分析师，请深度分析以下文本的思维模式：

文本内容：
{text}

请从以下维度进行分析：

1. 思维风格识别：
   - 视觉思维 (Visual Thinking)
   - 听觉思维 (Auditory Thinking) 
   - 动觉思维 (Kinesthetic Thinking)
   - 阅读写作思维 (Reading/Writing Thinking)

2. 认知模式分析：
   - 逻辑推理能力 (Logic)
   - 创意创新能力 (Creativity)
   - 直觉洞察能力 (Intuition)
   - 分析综合能力 (Analysis)

3. 思维特征：
   - 结构化程度
   - 抽象思维水平
   - 批判性思维
   - 发散性思维

4. 认知偏向：
   - 确认偏误
   - 锚定效应
   - 可得性启发
   - 框架效应

请以JSON格式返回分析结果，包含：
- thinking_style: 主导思维风格
- confidence: 分析置信度 (0-1)
- cognitive_patterns: 各项认知能力评分 (0-1)
- creativity_score: 创造力评分 (0-1)
- logic_score: 逻辑性评分 (0-1)
- intuition_score: 直觉性评分 (0-1)
- analysis: 详细分析结果
- suggestions: 思维训练建议
- reasoning: 分析推理过程
"""
        
        if context:
            base_prompt += f"\n\n额外上下文：\n{json.dumps(context, ensure_ascii=False, indent=2)}"
        
        return base_prompt
    
    async def _get_ai_response(
        self, 
        prompt: str, 
        model_name: str
    ) -> AIResponse:
        """获取AI响应"""
        try:
            if model_name == "gpt-4" and "gpt-4" in self.models:
                return await self._call_openai(prompt, model_name)
            elif model_name == "claude" and "claude" in self.models:
                return await self._call_anthropic(prompt, model_name)
            elif model_name == "gemini" and "gemini" in self.models:
                return await self._call_gemini(prompt, model_name)
            else:
                # 降级到本地模型
                return await self._call_local_model(prompt)
                
        except Exception as e:
            logger.error(f"AI响应获取失败: {e}")
            return await self._call_local_model(prompt)
    
    async def _call_openai(self, prompt: str, model_name: str) -> AIResponse:
        """调用OpenAI API"""
        try:
            model_config = self.models[model_name]
            
            response = await openai.ChatCompletion.acreate(
                model=model_config.model_id,
                messages=[
                    {"role": "system", "content": "你是一位专业的认知科学家和AI分析师。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature
            )
            
            return AIResponse(
                model_name=model_config.name,
                response_text=response.choices[0].message.content,
                confidence=0.9,
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    async def _call_anthropic(self, prompt: str, model_name: str) -> AIResponse:
        """调用Anthropic Claude API"""
        try:
            model_config = self.models[model_name]
            client = anthropic.Anthropic(api_key=model_config.api_key)
            
            response = await client.messages.create(
                model=model_config.model_id,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return AIResponse(
                model_name=model_config.name,
                response_text=response.content[0].text,
                confidence=0.85,
                token_usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {e}")
            raise
    
    async def _call_gemini(self, prompt: str, model_name: str) -> AIResponse:
        """调用Google Gemini API"""
        try:
            model_config = self.models[model_name]
            model = genai.GenerativeModel(model_config.model_id)
            
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=model_config.max_tokens,
                    temperature=model_config.temperature
                )
            )
            
            return AIResponse(
                model_name=model_config.name,
                response_text=response.text,
                confidence=0.8,
                metadata={
                    "safety_ratings": [
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name
                        }
                        for rating in response.prompt_feedback.safety_ratings
                    ] if response.prompt_feedback else []
                }
            )
            
        except Exception as e:
            logger.error(f"Gemini API调用失败: {e}")
            raise
    
    async def _call_local_model(self, prompt: str) -> AIResponse:
        """调用本地模型"""
        try:
            # 使用本地模型进行基础分析
            if 'sentiment' in self.local_models:
                sentiment_result = self.local_models['sentiment'](prompt)
                
                # 构建基础响应
                response_text = json.dumps({
                    "thinking_style": "analytical",
                    "confidence": 0.6,
                    "cognitive_patterns": {
                        "logic": 0.7,
                        "creativity": 0.5,
                        "intuition": 0.4,
                        "analysis": 0.8
                    },
                    "creativity_score": 0.5,
                    "logic_score": 0.7,
                    "intuition_score": 0.4,
                    "analysis": {
                        "sentiment": sentiment_result,
                        "text_length": len(prompt),
                        "complexity": "medium"
                    },
                    "suggestions": [
                        "尝试更多结构化思考",
                        "增强创意思维训练",
                        "提升直觉认知能力"
                    ],
                    "reasoning": "基于本地模型的基础分析"
                }, ensure_ascii=False)
                
                return AIResponse(
                    model_name="Local Model",
                    response_text=response_text,
                    confidence=0.6
                )
            
        except Exception as e:
            logger.error(f"本地模型调用失败: {e}")
            
        # 最终降级方案
        return AIResponse(
            model_name="Fallback",
            response_text=json.dumps({
                "thinking_style": "analytical",
                "confidence": 0.3,
                "cognitive_patterns": {"logic": 0.5, "creativity": 0.5, "intuition": 0.5, "analysis": 0.5},
                "creativity_score": 0.5,
                "logic_score": 0.5,
                "intuition_score": 0.5,
                "analysis": {"status": "basic_analysis"},
                "suggestions": ["建议使用更高级的AI模型获得更准确的分析"],
                "reasoning": "降级分析"
            }, ensure_ascii=False),
            confidence=0.3
        )
    
    def _parse_thinking_analysis(
        self, 
        ai_response: AIResponse, 
        original_text: str
    ) -> ThinkingAnalysisResult:
        """解析思维分析结果"""
        try:
            # 尝试解析JSON响应
            response_data = json.loads(ai_response.response_text)
            
            return ThinkingAnalysisResult(
                thinking_style=response_data.get("thinking_style", "analytical"),
                confidence=response_data.get("confidence", 0.5),
                analysis=response_data.get("analysis", {}),
                suggestions=response_data.get("suggestions", []),
                cognitive_patterns=response_data.get("cognitive_patterns", {}),
                creativity_score=response_data.get("creativity_score", 0.5),
                logic_score=response_data.get("logic_score", 0.5),
                intuition_score=response_data.get("intuition_score", 0.5)
            )
            
        except json.JSONDecodeError:
            # 如果不是JSON格式，进行文本解析
            return self._parse_text_response(ai_response, original_text)
    
    def _parse_text_response(
        self, 
        ai_response: AIResponse, 
        original_text: str
    ) -> ThinkingAnalysisResult:
        """解析文本响应"""
        # 基于文本内容的启发式分析
        text_lower = original_text.lower()
        
        # 简单的关键词分析
        creativity_keywords = ['创新', '想象', '创意', '新颖', '独特', '原创']
        logic_keywords = ['因为', '所以', '逻辑', '推理', '分析', '因此']
        intuition_keywords = ['感觉', '直觉', '预感', '本能', '感受']
        
        creativity_score = sum(1 for word in creativity_keywords if word in text_lower) / len(creativity_keywords)
        logic_score = sum(1 for word in logic_keywords if word in text_lower) / len(logic_keywords)
        intuition_score = sum(1 for word in intuition_keywords if word in text_lower) / len(intuition_keywords)
        
        # 确定主导思维风格
        scores = {
            'creative': creativity_score,
            'logical': logic_score,
            'intuitive': intuition_score
        }
        thinking_style = max(scores, key=scores.get)
        
        return ThinkingAnalysisResult(
            thinking_style=thinking_style,
            confidence=0.4,  # 文本分析置信度较低
            analysis={
                "method": "text_analysis",
                "keywords_found": {
                    "creativity": creativity_score,
                    "logic": logic_score,
                    "intuition": intuition_score
                },
                "text_length": len(original_text)
            },
            suggestions=[
                "尝试表达更多具体的想法",
                "增加逻辑推理过程的描述",
                "结合感性和理性思考"
            ],
            cognitive_patterns={
                "logic": logic_score,
                "creativity": creativity_score,
                "intuition": intuition_score,
                "analysis": 0.5
            },
            creativity_score=creativity_score,
            logic_score=logic_score,
            intuition_score=intuition_score
        )
    
    async def _enhance_with_local_models(
        self, 
        analysis_result: ThinkingAnalysisResult, 
        text: str
    ) -> ThinkingAnalysisResult:
        """使用本地模型增强分析"""
        try:
            # 情感分析增强
            if 'sentiment' in self.local_models:
                sentiment_scores = self.local_models['sentiment'](text)
                analysis_result.analysis['sentiment_analysis'] = sentiment_scores
            
            # 嵌入分析
            if 'embeddings' in self.local_models:
                embeddings = self.local_models['embeddings'](text)
                # 计算文本复杂度
                complexity = np.mean(np.std(embeddings, axis=1))
                analysis_result.analysis['text_complexity'] = float(complexity)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"本地模型增强失败: {e}")
            return analysis_result
    
    async def _fallback_analysis(self, text: str) -> ThinkingAnalysisResult:
        """降级分析"""
        return ThinkingAnalysisResult(
            thinking_style="analytical",
            confidence=0.3,
            analysis={"status": "fallback_analysis", "text_length": len(text)},
            suggestions=["建议配置AI模型API密钥以获得更准确的分析"],
            cognitive_patterns={"logic": 0.5, "creativity": 0.5, "intuition": 0.5, "analysis": 0.5},
            creativity_score=0.5,
            logic_score=0.5,
            intuition_score=0.5
        )
    
    async def generate_creative_content(
        self, 
        prompt: str, 
        content_type: str = "text",
        model_name: str = "gpt-4"
    ) -> AIResponse:
        """生成创意内容"""
        creative_prompt = f"""
作为一位创意专家，请根据以下提示生成{content_type}内容：

{prompt}

要求：
1. 具有创新性和独特性
2. 富有想象力和表现力
3. 符合主题要求
4. 质量优秀，引人入胜

请直接生成内容，无需额外说明。
"""
        
        return await self._get_ai_response(creative_prompt, model_name)
    
    async def multi_modal_analysis(
        self, 
        inputs: MultiModalInput,
        analysis_type: str = "comprehensive"
    ) -> AIResponse:
        """多模态分析"""
        # 这里可以扩展支持图像、音频等多模态输入
        if inputs.text:
            return await self.analyze_thinking_advanced(inputs.text)
        
        # 其他模态的处理逻辑...
        return AIResponse(
            model_name="MultiModal",
            response_text="多模态分析功能开发中...",
            confidence=0.1
        )
    
    async def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态"""
        status = {
            "available_models": list(self.models.keys()),
            "local_models": list(self.local_models.keys()),
            "model_details": {}
        }
        
        for name, config in self.models.items():
            status["model_details"][name] = {
                "name": config.name,
                "model_id": config.model_id,
                "enabled": config.enabled,
                "max_tokens": config.max_tokens
            }
        
        return status

# 全局实例
advanced_ai_service = AdvancedAIService() 