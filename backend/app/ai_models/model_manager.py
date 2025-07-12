"""
AI模型管理器 - 三层思维建模架构
"""

import os
import asyncio
import torch
import numpy as np
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM,
    CLIPProcessor, CLIPModel,
    AutoModelForSequenceClassification,
    pipeline
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import cv2
from PIL import Image
from loguru import logger

from ..core.config import settings


class VisualThinkingModel:
    """形象思维模型 - 视觉-语言理解"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu"
        
    async def initialize(self):
        """初始化模型"""
        try:
            logger.info("🔄 正在加载形象思维模型...")
            
            # 加载CLIP模型用于视觉-语言理解
            model_name = "openai/clip-vit-base-patch32"
            self.processor = CLIPProcessor.from_pretrained(
                model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            )
            self.model = CLIPModel.from_pretrained(
                model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            ).to(self.device)
            
            logger.info("✅ 形象思维模型加载完成")
            
        except Exception as e:
            logger.error(f"❌ 形象思维模型加载失败: {e}")
            raise
    
    async def analyze_image(self, image_data: Union[str, bytes, Image.Image]) -> Dict[str, Any]:
        """分析图像内容"""
        try:
            # 处理输入图像
            if isinstance(image_data, str):
                image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # 预定义的思维概念
            concepts = [
                "创新思维", "逻辑推理", "抽象概念", "具体实物",
                "情感表达", "空间关系", "时间概念", "因果关系",
                "科学原理", "艺术美感", "社会互动", "问题解决"
            ]
            
            # 使用CLIP进行图像-文本匹配
            inputs = self.processor(
                text=concepts,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # 分析结果
            concept_scores = {}
            for i, concept in enumerate(concepts):
                concept_scores[concept] = float(probs[0][i])
            
            # 找出主要概念
            dominant_concept = max(concept_scores, key=concept_scores.get)
            confidence = concept_scores[dominant_concept]
            
            return {
                "analysis_type": "visual_thinking",
                "dominant_concept": dominant_concept,
                "confidence": confidence,
                "concept_scores": concept_scores,
                "thinking_style": "形象思维" if confidence > 0.3 else "混合思维"
            }
            
        except Exception as e:
            logger.error(f"图像分析失败: {e}")
            return {"error": str(e)}
    
    async def extract_visual_features(self, image_data: Union[str, bytes, Image.Image]) -> np.ndarray:
        """提取视觉特征向量"""
        try:
            if isinstance(image_data, str):
                image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
                
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                return image_features.cpu().numpy().flatten()
                
        except Exception as e:
            logger.error(f"视觉特征提取失败: {e}")
            return np.array([])


class LogicalThinkingModel:
    """逻辑思维模型 - 推理和分析"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.classifier = None
        self.device = "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu"
        
    async def initialize(self):
        """初始化模型"""
        try:
            logger.info("🔄 正在加载逻辑思维模型...")
            
            # 加载RoBERTa模型用于文本理解
            model_name = "roberta-base"
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            )
            self.model = AutoModel.from_pretrained(
                model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            ).to(self.device)
            
            # 初始化分类器用于逻辑推理
            self.classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("✅ 逻辑思维模型加载完成")
            
        except Exception as e:
            logger.error(f"❌ 逻辑思维模型加载失败: {e}")
            raise
    
    async def analyze_reasoning(self, text: str) -> Dict[str, Any]:
        """分析文本的逻辑推理结构"""
        try:
            # 编码文本
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            # 分析逻辑模式
            logical_patterns = self._detect_logical_patterns(text)
            reasoning_strength = self._calculate_reasoning_strength(text)
            
            return {
                "analysis_type": "logical_thinking",
                "logical_patterns": logical_patterns,
                "reasoning_strength": reasoning_strength,
                "coherence_score": self._calculate_coherence(text),
                "argument_structure": self._analyze_argument_structure(text),
                "thinking_style": "逻辑思维"
            }
            
        except Exception as e:
            logger.error(f"逻辑推理分析失败: {e}")
            return {"error": str(e)}
    
    def _detect_logical_patterns(self, text: str) -> List[str]:
        """检测逻辑模式"""
        patterns = []
        
        # 因果关系
        if any(word in text for word in ["因为", "所以", "导致", "因此", "由于"]):
            patterns.append("因果推理")
        
        # 归纳推理
        if any(word in text for word in ["例如", "比如", "一般来说", "通常"]):
            patterns.append("归纳推理")
        
        # 演绎推理
        if any(word in text for word in ["如果", "那么", "假设", "前提"]):
            patterns.append("演绎推理")
        
        # 对比分析
        if any(word in text for word in ["相比", "对比", "然而", "但是", "相反"]):
            patterns.append("对比分析")
        
        return patterns
    
    def _calculate_reasoning_strength(self, text: str) -> float:
        """计算推理强度"""
        reasoning_words = [
            "分析", "推理", "证明", "论证", "结论", "假设",
            "验证", "逻辑", "原理", "规律", "因果", "关联"
        ]
        
        word_count = len(text.split())
        reasoning_count = sum(1 for word in reasoning_words if word in text)
        
        return min(reasoning_count / max(word_count * 0.1, 1), 1.0)
    
    def _calculate_coherence(self, text: str) -> float:
        """计算文本连贯性"""
        sentences = text.split('。')
        if len(sentences) < 2:
            return 1.0
        
        # 简单的连贯性评分（基于连接词）
        connection_words = ["因此", "所以", "然而", "但是", "而且", "另外", "此外"]
        connections = sum(1 for word in connection_words if word in text)
        
        return min(connections / len(sentences), 1.0)
    
    def _analyze_argument_structure(self, text: str) -> Dict[str, Any]:
        """分析论证结构"""
        return {
            "has_premise": any(word in text for word in ["前提", "假设", "基于"]),
            "has_evidence": any(word in text for word in ["证据", "数据", "事实", "研究"]),
            "has_conclusion": any(word in text for word in ["结论", "总结", "因此", "所以"]),
            "argument_type": "演绎论证" if "如果" in text and "那么" in text else "归纳论证"
        }


class CreativeThinkingModel:
    """创造思维模型 - 生成和创新"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu"
        
    async def initialize(self):
        """初始化模型"""
        try:
            logger.info("🔄 正在加载创造思维模型...")
            
            # 加载GPT-2模型用于创意生成
            model_name = "gpt2-medium"
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            ).to(self.device)
            
            # 设置pad_token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("✅ 创造思维模型加载完成")
            
        except Exception as e:
            logger.error(f"❌ 创造思维模型加载失败: {e}")
            raise
    
    async def generate_creative_ideas(
        self, 
        prompt: str, 
        num_ideas: int = 3,
        max_length: int = 100
    ) -> Dict[str, Any]:
        """生成创意想法"""
        try:
            inputs = self.tokenizer.encode(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(self.device)
            
            ideas = []
            for i in range(num_ideas):
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=max_length,
                        num_return_sequences=1,
                        temperature=0.8 + i * 0.1,  # 不同的温度产生不同的创意
                        do_sample=True,
                        top_k=50,
                        top_p=0.95,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                generated_text = self.tokenizer.decode(
                    outputs[0], 
                    skip_special_tokens=True
                )
                
                # 移除原始提示
                new_idea = generated_text[len(prompt):].strip()
                if new_idea:
                    ideas.append({
                        "idea": new_idea,
                        "creativity_score": self._calculate_creativity_score(new_idea),
                        "novelty": self._assess_novelty(new_idea, prompt)
                    })
            
            return {
                "analysis_type": "creative_thinking",
                "generated_ideas": ideas,
                "creativity_level": np.mean([idea["creativity_score"] for idea in ideas]),
                "thinking_style": "创造思维"
            }
            
        except Exception as e:
            logger.error(f"创意生成失败: {e}")
            return {"error": str(e)}
    
    def _calculate_creativity_score(self, text: str) -> float:
        """计算创意分数"""
        creative_words = [
            "创新", "独特", "新颖", "原创", "突破", "想象",
            "灵感", "创意", "发明", "设计", "艺术", "美感"
        ]
        
        word_count = len(text.split())
        creative_count = sum(1 for word in creative_words if word in text)
        
        # 基于创意词汇密度和文本长度
        density_score = creative_count / max(word_count * 0.1, 1)
        length_bonus = min(word_count / 50, 1.0)  # 更长的文本可能更有创意
        
        return min(density_score + length_bonus, 1.0)
    
    def _assess_novelty(self, idea: str, prompt: str) -> float:
        """评估新颖性"""
        # 简单的新颖性评估：与提示的相似度越低，新颖性越高
        try:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([prompt, idea])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return 1.0 - similarity
        except:
            return 0.5


class ModelManager:
    """AI模型统一管理器"""
    
    def __init__(self):
        self.visual_model = VisualThinkingModel()
        self.logical_model = LogicalThinkingModel()
        self.creative_model = CreativeThinkingModel()
        self.initialized = False
        
    async def initialize(self):
        """初始化所有AI模型"""
        try:
            logger.info("🚀 开始初始化AI模型管理器...")
            
            # 并行初始化模型
            await asyncio.gather(
                self.visual_model.initialize(),
                self.logical_model.initialize(),
                self.creative_model.initialize()
            )
            
            self.initialized = True
            logger.info("🎉 AI模型管理器初始化完成！")
            
        except Exception as e:
            logger.error(f"❌ AI模型管理器初始化失败: {e}")
            raise
    
    async def analyze_thinking_pattern(
        self, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """综合分析思维模式"""
        try:
            if not self.initialized:
                raise Exception("模型管理器未初始化")
            
            results = {}
            
            # 根据输入类型选择分析方法
            if "text" in input_data:
                # 逻辑思维分析
                logical_result = await self.logical_model.analyze_reasoning(
                    input_data["text"]
                )
                results["logical_thinking"] = logical_result
                
                # 创造思维分析
                creative_result = await self.creative_model.generate_creative_ideas(
                    input_data["text"]
                )
                results["creative_thinking"] = creative_result
            
            if "image" in input_data:
                # 形象思维分析
                visual_result = await self.visual_model.analyze_image(
                    input_data["image"]
                )
                results["visual_thinking"] = visual_result
            
            # 综合分析
            thinking_summary = self._synthesize_thinking_analysis(results)
            
            return {
                "individual_analyses": results,
                "thinking_summary": thinking_summary,
                "timestamp": settings.get_current_time()
            }
            
        except Exception as e:
            logger.error(f"思维模式分析失败: {e}")
            return {"error": str(e)}
    
    def _synthesize_thinking_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """综合思维分析结果"""
        thinking_scores = {}
        dominant_style = "平衡思维"
        
        # 收集各种思维的得分
        if "visual_thinking" in results and "confidence" in results["visual_thinking"]:
            thinking_scores["形象思维"] = results["visual_thinking"]["confidence"]
        
        if "logical_thinking" in results and "reasoning_strength" in results["logical_thinking"]:
            thinking_scores["逻辑思维"] = results["logical_thinking"]["reasoning_strength"]
        
        if "creative_thinking" in results and "creativity_level" in results["creative_thinking"]:
            thinking_scores["创造思维"] = results["creative_thinking"]["creativity_level"]
        
        # 确定主导思维风格
        if thinking_scores:
            dominant_style = max(thinking_scores, key=thinking_scores.get)
            max_score = thinking_scores[dominant_style]
            
            # 如果最高分不够高，则认为是平衡思维
            if max_score < 0.6:
                dominant_style = "平衡思维"
        
        return {
            "dominant_thinking_style": dominant_style,
            "thinking_scores": thinking_scores,
            "balance_index": self._calculate_balance_index(thinking_scores),
            "thinking_complexity": len(thinking_scores)
        }
    
    def _calculate_balance_index(self, scores: Dict[str, float]) -> float:
        """计算思维平衡指数"""
        if not scores:
            return 0.0
        
        values = list(scores.values())
        if len(values) == 1:
            return 0.0
        
        # 计算标准差，越小说明越平衡
        mean_score = np.mean(values)
        std_score = np.std(values)
        
        # 转换为平衡指数（0-1，1表示完全平衡）
        return max(0, 1 - std_score / max(mean_score, 0.1))
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✅ AI模型资源清理完成")
            
        except Exception as e:
            logger.error(f"AI模型资源清理失败: {e}")
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态"""
        return {
            "initialized": self.initialized,
            "device": "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu",
            "models": {
                "visual_thinking": self.visual_model.model is not None,
                "logical_thinking": self.logical_model.model is not None,
                "creative_thinking": self.creative_model.model is not None
            },
            "gpu_available": torch.cuda.is_available(),
            "gpu_enabled": settings.ENABLE_GPU
        } 