"""
思维分析服务
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from PIL import Image
from loguru import logger


class ThinkingAnalysisService:
    """思维分析服务类"""
    
    def __init__(self):
        self.visual_keywords = [
            "视觉化", "形象", "画面", "空间", "色彩", "图像", "具象", "感知",
            "直观", "形态", "美感", "艺术", "设计", "外观", "场景", "景象"
        ]
        
        self.logical_keywords = [
            "逻辑", "推理", "分析", "因果", "结构", "系统", "步骤", "规律",
            "原理", "方法", "策略", "计划", "条理", "理性", "严密", "科学"
        ]
        
        self.creative_keywords = [
            "创新", "创意", "想象", "灵感", "突破", "发明", "原创", "独特",
            "新颖", "创造", "发散", "联想", "跨界", "变革", "颠覆", "未来"
        ]

    async def analyze_thinking(
        self, 
        text: str, 
        analysis_type: str = "comprehensive",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析思维模式
        """
        start_time = time.time()
        
        try:
            # 基础文本分析
            text_analysis = self._analyze_text(text)
            
            # 根据分析类型进行不同的处理
            if analysis_type == "comprehensive":
                results = {
                    "visual_thinking": await self._analyze_visual_thinking(text, text_analysis),
                    "logical_thinking": await self._analyze_logical_thinking(text, text_analysis),
                    "creative_thinking": await self._analyze_creative_thinking(text, text_analysis)
                }
            elif analysis_type == "visual":
                results = {
                    "visual_thinking": await self._analyze_visual_thinking(text, text_analysis)
                }
            elif analysis_type == "logical":
                results = {
                    "logical_thinking": await self._analyze_logical_thinking(text, text_analysis)
                }
            elif analysis_type == "creative":
                results = {
                    "creative_thinking": await self._analyze_creative_thinking(text, text_analysis)
                }
            else:
                raise ValueError(f"不支持的分析类型: {analysis_type}")
            
            # 生成思维总结
            thinking_summary = self._generate_thinking_summary(results)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "individual_analyses": results,
                "thinking_summary": thinking_summary,
                "processing_time": processing_time,
                "confidence_score": self._calculate_confidence_score(results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"思维分析失败: {e}")
            raise

    async def analyze_image_thinking(
        self, 
        image: Image.Image, 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析图像思维
        """
        try:
            # 模拟图像分析 - 在实际应用中这里会调用真实的视觉AI模型
            image_features = self._extract_image_features(image)
            
            analysis = {
                "score": 0.75 + random.random() * 0.2,
                "concepts": self._generate_visual_concepts(image_features),
                "associations": self._generate_visual_associations(image_features),
                "insights": [
                    "您展现出良好的视觉感知能力",
                    "能够从图像中提取关键信息",
                    "建议加强视觉与语言的结合表达"
                ],
                "processing_time": 800 + random.randint(-200, 400),
                "confidence": 0.8 + random.random() * 0.15
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"图像思维分析失败: {e}")
            raise

    async def generate_creative_ideas(
        self,
        prompt: str,
        num_ideas: int = 3,
        creativity_level: float = 0.8,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成创意想法
        """
        try:
            # 模拟创意生成 - 在实际应用中这里会调用真实的生成AI模型
            ideas = []
            
            for i in range(num_ideas):
                idea = {
                    "title": f"创意想法 {i+1}",
                    "description": self._generate_creative_description(prompt, i),
                    "novelty": 0.6 + random.random() * 0.4,
                    "feasibility": 0.5 + random.random() * 0.4,
                    "impact": 0.4 + random.random() * 0.5
                }
                ideas.append(idea)
            
            # 计算创意指标
            novelty_scores = [idea["novelty"] for idea in ideas]
            creativity_metrics = {
                "average_creativity_score": creativity_level,
                "idea_diversity": len(set([idea["title"][:10] for idea in ideas])) / len(ideas),
                "novelty_index": sum(novelty_scores) / len(novelty_scores)
            }
            
            return {
                "generated_ideas": ideas,
                "creativity_metrics": creativity_metrics
            }
            
        except Exception as e:
            logger.error(f"创意生成失败: {e}")
            raise

    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """基础文本分析"""
        words = text.split()
        sentences = text.split('。')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "text_length": len(text),
            "complexity_score": self._calculate_text_complexity(text)
        }

    async def _analyze_visual_thinking(self, text: str, text_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析形象思维"""
        visual_score = self._calculate_keyword_score(text, self.visual_keywords)
        
        # 识别视觉相关概念
        concepts = []
        for keyword in self.visual_keywords:
            if keyword in text:
                concepts.append(keyword)
        
        # 如果没有明显的视觉关键词，基于文本特征推断
        if not concepts:
            concepts = ["抽象概念", "思维图像", "认知框架"]
        
        # 生成联想词汇
        associations = self._generate_associations(text, "visual")
        
        return {
            "score": min(0.9, visual_score + 0.1 + random.random() * 0.2),
            "concepts": concepts[:5],  # 最多5个概念
            "associations": associations[:6],  # 最多6个关联词
            "description": "形象思维分析显示您善于运用具体形象来理解和表达抽象概念"
        }

    async def _analyze_logical_thinking(self, text: str, text_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析逻辑思维"""
        logical_score = self._calculate_keyword_score(text, self.logical_keywords)
        
        # 分析推理步骤
        reasoning_steps = self._extract_reasoning_steps(text)
        
        # 分析结论
        conclusions = self._extract_conclusions(text)
        
        return {
            "score": min(0.95, logical_score + 0.15 + random.random() * 0.15),
            "reasoning_steps": reasoning_steps,
            "conclusions": conclusions,
            "description": "逻辑思维分析显示您具备清晰的推理能力和结构化思考方式"
        }

    async def _analyze_creative_thinking(self, text: str, text_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析创造思维"""
        creative_score = self._calculate_keyword_score(text, self.creative_keywords)
        
        # 识别创新点
        innovations = self._identify_innovations(text)
        
        # 识别可能性
        possibilities = self._identify_possibilities(text)
        
        return {
            "score": min(0.92, creative_score + 0.2 + random.random() * 0.25),
            "innovations": innovations,
            "possibilities": possibilities,
            "description": "创造思维分析显示您具有活跃的想象力和创新思维能力"
        }

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """计算关键词匹配分数"""
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        return min(0.8, matches / len(keywords) * 2)

    def _calculate_text_complexity(self, text: str) -> float:
        """计算文本复杂度"""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        return min(1.0, avg_word_length / 10)

    def _generate_thinking_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成思维总结"""
        thinking_scores = {}
        
        # 提取各种思维类型的分数
        if "visual_thinking" in results:
            thinking_scores["形象思维"] = results["visual_thinking"]["score"]
        if "logical_thinking" in results:
            thinking_scores["逻辑思维"] = results["logical_thinking"]["score"]
        if "creative_thinking" in results:
            thinking_scores["创造思维"] = results["creative_thinking"]["score"]
        
        # 确定主导思维风格
        dominant_style = max(thinking_scores, key=thinking_scores.get) if thinking_scores else "综合思维"
        
        # 计算平衡指数
        if len(thinking_scores) > 1:
            scores_list = list(thinking_scores.values())
            balance_index = 1 - (max(scores_list) - min(scores_list))
        else:
            balance_index = 0.8
        
        # 生成洞察建议
        insights = self._generate_insights(thinking_scores, dominant_style, balance_index)
        
        return {
            "dominant_thinking_style": dominant_style,
            "thinking_scores": thinking_scores,
            "balance_index": max(0.0, min(1.0, balance_index)),
            "insights": insights
        }

    def _generate_insights(self, scores: Dict[str, float], dominant_style: str, balance_index: float) -> List[str]:
        """生成洞察建议"""
        insights = []
        
        if dominant_style == "形象思维":
            insights.append("您具有出色的形象思维能力，善于用具体画面理解抽象概念")
            if scores.get("逻辑思维", 0) < 0.7:
                insights.append("建议加强逻辑推理训练，提升结构化思考能力")
        elif dominant_style == "逻辑思维":
            insights.append("您的逻辑思维能力突出，善于理性分析和系统思考")
            if scores.get("创造思维", 0) < 0.7:
                insights.append("建议多进行发散性思维练习，激发创新潜能")
        elif dominant_style == "创造思维":
            insights.append("您具有活跃的创造思维，善于产生新颖独特的想法")
            if scores.get("逻辑思维", 0) < 0.7:
                insights.append("建议加强逻辑验证，将创意与实际可行性结合")
        
        if balance_index > 0.8:
            insights.append("您的思维发展较为均衡，能够灵活运用不同思维方式")
        elif balance_index < 0.5:
            insights.append("建议加强相对薄弱的思维类型，实现更均衡的思维发展")
        
        return insights

    def _calculate_confidence_score(self, results: Dict[str, Any]) -> int:
        """计算置信度分数"""
        scores = []
        for analysis in results.values():
            if isinstance(analysis, dict) and "score" in analysis:
                scores.append(analysis["score"])
        
        if not scores:
            return 75
        
        avg_score = sum(scores) / len(scores)
        confidence = int(75 + avg_score * 20)  # 75-95分范围
        return min(95, max(60, confidence))

    def _extract_image_features(self, image: Image.Image) -> Dict[str, Any]:
        """提取图像特征（模拟）"""
        return {
            "dominant_colors": ["蓝色", "白色", "灰色"],
            "objects": ["建筑", "天空", "道路"],
            "composition": "对称构图",
            "style": "现代简约"
        }

    def _generate_visual_concepts(self, features: Dict[str, Any]) -> List[str]:
        """生成视觉概念"""
        concepts = ["空间感", "色彩搭配", "构图平衡"]
        if features.get("objects"):
            concepts.extend(features["objects"][:3])
        return concepts[:5]

    def _generate_visual_associations(self, features: Dict[str, Any]) -> List[str]:
        """生成视觉联想"""
        associations = ["视觉冲击", "美学感受", "情感共鸣"]
        if "modern" in str(features).lower():
            associations.extend(["现代设计", "科技感", "简洁美"])
        return associations[:6]

    def _generate_creative_description(self, prompt: str, index: int) -> str:
        """生成创意描述"""
        templates = [
            f"基于'{prompt}'的创新方案，结合现代技术和用户需求",
            f"从'{prompt}'出发，探索跨领域融合的新可能性",
            f"以'{prompt}'为核心，构建可持续发展的创意模式"
        ]
        return templates[index % len(templates)]

    def _generate_associations(self, text: str, thinking_type: str) -> List[str]:
        """生成关联词汇"""
        if thinking_type == "visual":
            base_words = ["画面", "色彩", "形状", "空间", "美感", "视觉"]
        elif thinking_type == "logical":
            base_words = ["逻辑", "推理", "分析", "结构", "系统", "方法"]
        else:  # creative
            base_words = ["创新", "想象", "灵感", "突破", "原创", "未来"]
        
        # 基于文本内容调整关联词
        associations = []
        for word in base_words:
            if len(associations) < 6:
                associations.append(word)
        
        return associations

    def _extract_reasoning_steps(self, text: str) -> List[str]:
        """提取推理步骤"""
        # 简化的推理步骤提取
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        
        if len(sentences) >= 3:
            return [
                "分析现状和问题",
                "探讨可能的解决方案",
                "评估方案的可行性",
                "得出结论和建议"
            ]
        else:
            return [
                "理解问题核心",
                "寻找解决思路",
                "形成初步判断"
            ]

    def _extract_conclusions(self, text: str) -> List[str]:
        """提取结论"""
        # 简化的结论提取
        return ["需要综合考虑多方面因素", "建议采用渐进式方法", "重视实际执行效果"]

    def _identify_innovations(self, text: str) -> List[str]:
        """识别创新点"""
        # 简化的创新点识别
        return ["新颖的解决思路", "跨领域的思维融合", "前瞻性的发展视角"]

    def _identify_possibilities(self, text: str) -> List[str]:
        """识别可能性"""
        # 简化的可能性识别
        return ["技术实现可能性", "市场应用前景", "社会价值潜力"] 