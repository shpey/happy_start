"""
高级AI API端点
提供多模型AI分析、创意生成等功能
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import numpy as np

from ....services.advanced_ai_service import (
    advanced_ai_service,
    ThinkingAnalysisResult,
    AIResponse,
    MultiModalInput
)
from ....core.security import get_current_user
from ....models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

class AdvancedAnalysisRequest(BaseModel):
    """高级分析请求"""
    text: str = Field(..., min_length=1, max_length=10000, description="要分析的文本")
    model_name: str = Field(default="gpt-4", description="使用的AI模型")
    context: Optional[Dict[str, Any]] = Field(default=None, description="分析上下文")
    analysis_type: str = Field(default="comprehensive", description="分析类型")

class CreativeGenerationRequest(BaseModel):
    """创意生成请求"""
    prompt: str = Field(..., min_length=1, max_length=5000, description="创意生成提示")
    content_type: str = Field(default="text", description="内容类型")
    model_name: str = Field(default="gpt-4", description="使用的AI模型")
    creativity_level: float = Field(default=0.7, ge=0.0, le=1.0, description="创意水平")
    style: Optional[str] = Field(default=None, description="创作风格")

class MultiModalAnalysisRequest(BaseModel):
    """多模态分析请求"""
    text: Optional[str] = None
    image: Optional[str] = None  # base64编码
    audio: Optional[str] = None
    analysis_type: str = Field(default="comprehensive", description="分析类型")
    model_name: str = Field(default="gemini", description="使用的AI模型")

class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""
    texts: List[str] = Field(..., min_items=1, max_items=10, description="批量文本")
    model_name: str = Field(default="gpt-4", description="使用的AI模型")
    analysis_type: str = Field(default="comprehensive", description="分析类型")

@router.post("/analyze/advanced", response_model=ThinkingAnalysisResult)
async def advanced_thinking_analysis(
    request: AdvancedAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    高级思维分析
    
    - 支持多种AI模型
    - 深度认知分析
    - 个性化建议
    """
    try:
        logger.info(f"用户 {current_user.username} 请求高级思维分析，模型: {request.model_name}")
        
        # 执行高级思维分析
        result = await advanced_ai_service.analyze_thinking_advanced(
            text=request.text,
            model_name=request.model_name,
            context=request.context
        )
        
        # 后台任务：记录分析历史
        background_tasks.add_task(
            log_analysis_history,
            user_id=current_user.id,
            analysis_type="advanced_thinking",
            input_text=request.text,
            result=result.dict(),
            model_name=request.model_name
        )
        
        return result
        
    except Exception as e:
        logger.error(f"高级思维分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.post("/generate/creative", response_model=AIResponse)
async def creative_content_generation(
    request: CreativeGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    创意内容生成
    
    - 多种内容类型
    - 可调节创意水平
    - 风格定制
    """
    try:
        logger.info(f"用户 {current_user.username} 请求创意生成，类型: {request.content_type}")
        
        # 构建创意生成提示
        enhanced_prompt = build_creative_prompt(
            prompt=request.prompt,
            content_type=request.content_type,
            creativity_level=request.creativity_level,
            style=request.style
        )
        
        # 生成创意内容
        result = await advanced_ai_service.generate_creative_content(
            prompt=enhanced_prompt,
            content_type=request.content_type,
            model_name=request.model_name
        )
        
        return result
        
    except Exception as e:
        logger.error(f"创意生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@router.post("/analyze/multimodal", response_model=AIResponse)
async def multimodal_analysis(
    request: MultiModalAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    多模态分析
    
    - 文本、图像、音频分析
    - 跨模态理解
    - 综合洞察
    """
    try:
        logger.info(f"用户 {current_user.username} 请求多模态分析")
        
        # 构建多模态输入
        multimodal_input = MultiModalInput(
            text=request.text,
            image=request.image,
            audio=request.audio
        )
        
        # 执行多模态分析
        result = await advanced_ai_service.multi_modal_analysis(
            inputs=multimodal_input,
            analysis_type=request.analysis_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"多模态分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.post("/analyze/batch", response_model=List[ThinkingAnalysisResult])
async def batch_thinking_analysis(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    批量思维分析
    
    - 同时分析多个文本
    - 效率优化
    - 对比分析
    """
    try:
        logger.info(f"用户 {current_user.username} 请求批量分析，数量: {len(request.texts)}")
        
        results = []
        for i, text in enumerate(request.texts):
            try:
                result = await advanced_ai_service.analyze_thinking_advanced(
                    text=text,
                    model_name=request.model_name,
                    context={"batch_index": i, "total_count": len(request.texts)}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"批量分析第 {i+1} 项失败: {e}")
                # 继续处理其他项目
                continue
        
        # 后台任务：记录批量分析
        background_tasks.add_task(
            log_batch_analysis,
            user_id=current_user.id,
            texts=request.texts,
            results=[r.dict() for r in results],
            model_name=request.model_name
        )
        
        return results
        
    except Exception as e:
        logger.error(f"批量分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")

@router.get("/models/status")
async def get_ai_models_status(
    current_user: User = Depends(get_current_user)
):
    """
    获取AI模型状态
    
    - 可用模型列表
    - 模型能力信息
    - 实时状态
    """
    try:
        status = await advanced_ai_service.get_model_status()
        return status
        
    except Exception as e:
        logger.error(f"获取模型状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@router.get("/models/{model_name}/info")
async def get_model_info(
    model_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取特定模型详细信息
    
    - 模型参数
    - 能力描述
    - 使用建议
    """
    try:
        model_info = get_model_detailed_info(model_name)
        if not model_info:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        return model_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取信息失败: {str(e)}")

@router.post("/analyze/compare")
async def compare_model_analysis(
    request: AdvancedAnalysisRequest,
    models: List[str] = ["gpt-4", "claude", "gemini"],
    current_user: User = Depends(get_current_user)
):
    """
    模型对比分析
    
    - 多模型同时分析
    - 结果对比
    - 一致性评估
    """
    try:
        logger.info(f"用户 {current_user.username} 请求模型对比分析")
        
        results = {}
        for model_name in models:
            try:
                result = await advanced_ai_service.analyze_thinking_advanced(
                    text=request.text,
                    model_name=model_name,
                    context=request.context
                )
                results[model_name] = result.dict()
            except Exception as e:
                logger.warning(f"模型 {model_name} 分析失败: {e}")
                results[model_name] = {"error": str(e)}
        
        # 计算一致性分析
        consistency_analysis = calculate_model_consistency(results)
        
        return {
            "results": results,
            "consistency": consistency_analysis,
            "recommendation": get_model_recommendation(results)
        }
        
    except Exception as e:
        logger.error(f"模型对比分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"对比分析失败: {str(e)}")

@router.get("/analytics/user-usage")
async def get_user_ai_usage_analytics(
    current_user: User = Depends(get_current_user),
    days: int = 30
):
    """
    用户AI使用分析
    
    - 使用统计
    - 模型偏好
    - 分析趋势
    """
    try:
        analytics = await get_user_usage_statistics(current_user.id, days)
        return analytics
        
    except Exception as e:
        logger.error(f"获取用户使用分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析失败: {str(e)}")

# 辅助函数

def build_creative_prompt(
    prompt: str,
    content_type: str,
    creativity_level: float,
    style: Optional[str] = None
) -> str:
    """构建创意生成提示"""
    creativity_desc = {
        0.0: "保守和传统",
        0.3: "稳妥和实用",
        0.5: "平衡和适中",
        0.7: "创新和富有想象力",
        1.0: "极度创新和前卫"
    }
    
    level_desc = creativity_desc.get(
        min(creativity_desc.keys(), key=lambda x: abs(x - creativity_level)),
        "平衡和适中"
    )
    
    enhanced_prompt = f"""
创意生成任务：
内容类型：{content_type}
创意水平：{level_desc} (级别 {creativity_level})
{f'风格要求：{style}' if style else ''}

原始提示：{prompt}

请根据以上要求生成高质量的创意内容。
"""
    
    return enhanced_prompt

def get_model_detailed_info(model_name: str) -> Optional[Dict[str, Any]]:
    """获取模型详细信息"""
    model_info_db = {
        "gpt-4": {
            "name": "GPT-4 Turbo",
            "provider": "OpenAI",
            "capabilities": ["文本理解", "代码生成", "创意写作", "复杂推理"],
            "max_tokens": 4000,
            "languages": ["中文", "英文", "多语言"],
            "strengths": ["逻辑推理", "创意生成", "多任务处理"],
            "use_cases": ["思维分析", "内容创作", "问题解决", "教育辅助"]
        },
        "claude": {
            "name": "Claude 3 Opus",
            "provider": "Anthropic",
            "capabilities": ["安全分析", "伦理推理", "长文本处理", "准确理解"],
            "max_tokens": 4000,
            "languages": ["中文", "英文"],
            "strengths": ["安全性", "准确性", "伦理推理"],
            "use_cases": ["安全分析", "伦理评估", "长文档处理"]
        },
        "gemini": {
            "name": "Gemini Pro",
            "provider": "Google",
            "capabilities": ["多模态理解", "代码分析", "科学推理", "实时信息"],
            "max_tokens": 4000,
            "languages": ["中文", "英文", "多语言"],
            "strengths": ["多模态", "科学推理", "代码理解"],
            "use_cases": ["多模态分析", "科学研究", "代码审查"]
        }
    }
    
    return model_info_db.get(model_name)

def calculate_model_consistency(results: Dict[str, Any]) -> Dict[str, Any]:
    """计算模型一致性"""
    # 简化的一致性分析
    valid_results = {k: v for k, v in results.items() if "error" not in v}
    
    if len(valid_results) < 2:
        return {"consistency_score": 0.0, "note": "需要至少两个有效结果"}
    
    # 分析思维风格一致性
    thinking_styles = [r.get("thinking_style") for r in valid_results.values()]
    style_consistency = len(set(thinking_styles)) / len(thinking_styles)
    
    # 分析置信度一致性
    confidences = [r.get("confidence", 0) for r in valid_results.values()]
    confidence_variance = np.var(confidences) if confidences else 1.0
    
    overall_consistency = (1 - style_consistency) * 0.5 + max(0, 1 - confidence_variance) * 0.5
    
    return {
        "consistency_score": overall_consistency,
        "style_agreement": 1 - style_consistency,
        "confidence_variance": confidence_variance,
        "participating_models": list(valid_results.keys())
    }

def get_model_recommendation(results: Dict[str, Any]) -> Dict[str, Any]:
    """获取模型推荐"""
    valid_results = {k: v for k, v in results.items() if "error" not in v}
    
    if not valid_results:
        return {"recommended_model": None, "reason": "没有有效结果"}
    
    # 根据置信度推荐
    best_model = max(
        valid_results.items(),
        key=lambda x: x[1].get("confidence", 0)
    )
    
    return {
        "recommended_model": best_model[0],
        "confidence": best_model[1].get("confidence", 0),
        "reason": f"在所有模型中具有最高置信度 ({best_model[1].get('confidence', 0):.1%})"
    }

async def log_analysis_history(
    user_id: int,
    analysis_type: str,
    input_text: str,
    result: Dict[str, Any],
    model_name: str
):
    """记录分析历史"""
    try:
        # 这里可以连接数据库记录分析历史
        logger.info(f"记录用户 {user_id} 的 {analysis_type} 分析历史")
    except Exception as e:
        logger.error(f"记录分析历史失败: {e}")

async def log_batch_analysis(
    user_id: int,
    texts: List[str],
    results: List[Dict[str, Any]],
    model_name: str
):
    """记录批量分析"""
    try:
        logger.info(f"记录用户 {user_id} 的批量分析，数量: {len(texts)}")
    except Exception as e:
        logger.error(f"记录批量分析失败: {e}")

async def get_user_usage_statistics(user_id: int, days: int) -> Dict[str, Any]:
    """获取用户使用统计"""
    # 模拟数据，实际应该从数据库获取
    return {
        "total_analyses": 42,
        "models_used": ["gpt-4", "claude", "gemini"],
        "favorite_model": "gpt-4",
        "avg_confidence": 0.85,
        "analysis_types": {
            "thinking": 30,
            "creative": 8,
            "multimodal": 4
        },
        "daily_usage": [2, 3, 1, 5, 2, 4, 3]  # 最近7天
    } 