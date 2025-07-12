"""
思维分析 API 端点
"""

import io
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
from loguru import logger
from sqlalchemy.orm import Session
from datetime import datetime

from ....core.database import get_db
from ....core.security import get_current_active_user
from ....models.user import User
from ....models.thinking_analysis import ThinkingAnalysis
from ....services.thinking_service import ThinkingAnalysisService
from ....services.user_service import UserService

router = APIRouter()


class ThinkingAnalysisRequest(BaseModel):
    """思维分析请求模型"""
    text: Optional[str] = None
    analysis_type: str = "comprehensive"  # comprehensive, visual, logical, creative
    save_result: bool = True
    user_id: Optional[str] = None


class ThinkingAnalysisResponse(BaseModel):
    """思维分析响应模型"""
    success: bool
    analysis_id: Optional[str] = None
    results: Dict[str, Any]
    thinking_summary: Dict[str, Any]
    timestamp: str
    error: Optional[str] = None


@router.post("/analyze", response_model=ThinkingAnalysisResponse)
async def analyze_thinking_pattern(
    request: ThinkingAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ThinkingAnalysisResponse:
    """
    分析思维模式
    
    支持三层思维分析：
    - 形象思维：视觉-语言理解
    - 逻辑思维：推理和分析 
    - 创造思维：生成和创新
    """
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="需要提供分析文本")
        
        # 获取思维分析服务
        thinking_service = ThinkingAnalysisService()
        user_service = UserService(db)
        
        # 执行思维分析
        analysis_results = await thinking_service.analyze_thinking(
            text=request.text,
            analysis_type=request.analysis_type,
            user_id=current_user["user_id"]
        )
        
        # 保存分析结果到数据库
        analysis_id = None
        if request.save_result:
            analysis_record = ThinkingAnalysis(
                user_id=current_user["user_id"],
                input_text=request.text,
                analysis_type=request.analysis_type,
                results=analysis_results["individual_analyses"],
                thinking_summary=analysis_results["thinking_summary"],
                processing_time=analysis_results.get("processing_time", 0),
                confidence_score=analysis_results.get("confidence_score", 85)
            )
            
            db.add(analysis_record)
            db.commit()
            db.refresh(analysis_record)
            analysis_id = str(analysis_record.id)
            
            # 更新用户思维统计
            await user_service.update_thinking_stats(
                current_user["user_id"], 
                analysis_results
            )
        
        return ThinkingAnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            results=analysis_results["individual_analyses"],
            thinking_summary=analysis_results["thinking_summary"],
            timestamp=analysis_results["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"思维分析失败: {e}")
        return ThinkingAnalysisResponse(
            success=False,
            results={},
            thinking_summary={},
            timestamp="",
            error=str(e)
        )


@router.post("/analyze-image")
async def analyze_image_thinking(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    save_result: bool = Form(True),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    分析图像的思维内容
    
    使用形象思维模型分析图像中的认知概念
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图像文件")
        
        # 读取图像
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # 获取思维分析服务
        thinking_service = ThinkingAnalysisService()
        
        # 执行形象思维分析
        visual_analysis = await thinking_service.analyze_image_thinking(
            image=image,
            user_id=current_user["user_id"]
        )
        
        # 保存分析结果
        if save_result:
            analysis_record = ThinkingAnalysis(
                user_id=current_user["user_id"],
                input_text=f"图像分析: {file.filename}",
                analysis_type="visual",
                results={"visual_thinking": visual_analysis},
                thinking_summary={
                    "dominant_thinking_style": "形象思维",
                    "thinking_scores": {"形象思维": visual_analysis.get("score", 0.8)},
                    "balance_index": visual_analysis.get("score", 0.8),
                    "insights": visual_analysis.get("insights", [])
                },
                processing_time=visual_analysis.get("processing_time", 1000),
                confidence_score=int(visual_analysis.get("confidence", 0.8) * 100)
            )
            
            db.add(analysis_record)
            db.commit()
        
        return {
            "success": True,
            "analysis": visual_analysis,
            "file_info": {
                "filename": file.filename,
                "size": len(image_data),
                "format": image.format,
                "dimensions": image.size
            }
        }
        
    except Exception as e:
        logger.error(f"图像思维分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"图像分析失败: {str(e)}")


@router.post("/generate-ideas")
async def generate_creative_ideas(
    prompt: str = Form(...),
    num_ideas: int = Form(3),
    creativity_level: float = Form(0.8),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    生成创意想法
    
    使用创造思维模型基于提示生成创新想法
    """
    try:
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="创意提示不能为空")
        
        # 获取思维分析服务
        thinking_service = ThinkingAnalysisService()
        
        # 执行创造思维分析
        creative_analysis = await thinking_service.generate_creative_ideas(
            prompt=prompt,
            num_ideas=num_ideas,
            creativity_level=creativity_level,
            user_id=current_user["user_id"]
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "generated_ideas": creative_analysis["generated_ideas"],
            "creativity_metrics": creative_analysis["creativity_metrics"]
        }
        
    except Exception as e:
        logger.error(f"创意生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"创意生成失败: {str(e)}")


@router.get("/history/{user_id}")
async def get_analysis_history(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    analysis_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取用户的思维分析历史"""
    try:
        # 检查权限 - 只能查看自己的历史
        if int(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问他人的分析历史")
        
        query = db.query(ThinkingAnalysis).filter(
            ThinkingAnalysis.user_id == int(user_id)
        )
        
        if analysis_type:
            query = query.filter(ThinkingAnalysis.analysis_type == analysis_type)
        
        total_count = query.count()
        
        analyses = query.order_by(
            ThinkingAnalysis.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "history": [analysis.to_dict() for analysis in analyses],
            "total_count": total_count,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取分析历史失败")


@router.get("/statistics/{user_id}")
async def get_thinking_statistics(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取用户思维统计信息"""
    try:
        # 检查权限
        if int(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问他人的统计信息")
        
        user_service = UserService(db)
        user_stats = await user_service.get_user_stats(int(user_id))
        
        # 获取分析记录统计
        analyses = db.query(ThinkingAnalysis).filter(
            ThinkingAnalysis.user_id == int(user_id)
        ).all()
        
        # 计算统计信息
        total_analyses = len(analyses)
        favorite_count = sum(1 for a in analyses if a.is_favorited)
        
        # 分析类型分布
        type_distribution = {}
        style_scores = {}
        
        for analysis in analyses:
            # 分析类型统计
            analysis_type = analysis.analysis_type
            type_distribution[analysis_type] = type_distribution.get(analysis_type, 0) + 1
            
            # 思维风格分数统计
            if analysis.thinking_summary and "thinking_scores" in analysis.thinking_summary:
                scores = analysis.thinking_summary["thinking_scores"]
                for style, score in scores.items():
                    if style not in style_scores:
                        style_scores[style] = []
                    style_scores[style].append(score)
        
        # 计算平均分数
        average_scores = {}
        for style, scores in style_scores.items():
            average_scores[style] = sum(scores) / len(scores) if scores else 0
        
        # 确定主导思维风格
        dominant_style = max(average_scores, key=average_scores.get) if average_scores else None
        
        statistics = {
            "total_analyses": total_analyses,
            "recent_analyses": len([a for a in analyses if (datetime.now() - a.created_at).days <= 30]),
            "favorite_count": favorite_count,
            "dominant_style": dominant_style,
            "average_scores": average_scores,
            "type_distribution": type_distribution,
            "improvement_trend": "stable"  # 这里可以添加更复杂的趋势分析
        }
        
        return {
            "success": True,
            "statistics": statistics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取思维统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取思维统计失败")


@router.get("/analysis/{analysis_id}")
async def get_analysis_detail(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取分析结果详情"""
    try:
        analysis = db.query(ThinkingAnalysis).filter(
            ThinkingAnalysis.id == int(analysis_id)
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="分析记录不存在")
        
        # 检查权限
        if analysis.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问此分析记录")
        
        return {
            "success": True,
            "analysis": analysis.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取分析详情失败")


@router.put("/analysis/{analysis_id}/favorite")
async def toggle_analysis_favorite(
    analysis_id: str,
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """收藏/取消收藏分析结果"""
    try:
        analysis = db.query(ThinkingAnalysis).filter(
            ThinkingAnalysis.id == int(analysis_id)
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="分析记录不存在")
        
        # 检查权限
        if analysis.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权修改此分析记录")
        
        analysis.is_favorited = request.get("is_favorited", False)
        db.commit()
        
        return {"success": True, "message": "收藏状态更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新收藏状态失败: {e}")
        raise HTTPException(status_code=500, detail="更新收藏状态失败")


@router.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """删除分析记录"""
    try:
        analysis = db.query(ThinkingAnalysis).filter(
            ThinkingAnalysis.id == int(analysis_id)
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="分析记录不存在")
        
        # 检查权限
        if analysis.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权删除此分析记录")
        
        db.delete(analysis)
        db.commit()
        
        return {"success": True, "message": "分析记录删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除分析记录失败: {e}")
        raise HTTPException(status_code=500, detail="删除分析记录失败") 