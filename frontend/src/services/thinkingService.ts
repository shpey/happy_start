/**
 * 思维分析API服务
 */

import { get, post, uploadFile } from './api';

// 思维分析请求参数
export interface ThinkingAnalysisRequest {
  text: string;
  analysis_type?: 'comprehensive' | 'visual' | 'logical' | 'creative';
  save_result?: boolean;
  user_id?: string;
}

// 思维分析响应
export interface ThinkingAnalysisResponse {
  success: boolean;
  analysis_id?: string;
  thinking_summary: {
    dominant_thinking_style: string;
    thinking_scores: Record<string, number>;
    balance_index: number;
    thinking_complexity: number;
  };
  individual_analyses: {
    logical_thinking?: any;
    creative_thinking?: any;
    visual_thinking?: any;
  };
  processing_time: number;
  confidence_score: number;
  timestamp: string;
  error?: string;
}

// 创意生成请求参数
export interface CreativeIdeaRequest {
  prompt: string;
  num_ideas?: number;
  creativity_level?: number;
  user_id?: string;
}

// 创意生成响应
export interface CreativeIdeaResponse {
  success: boolean;
  prompt: string;
  generated_ideas: Array<{
    idea: string;
    creativity_score: number;
    novelty: number;
    feasibility?: number;
  }>;
  creativity_metrics: {
    average_creativity_score: number;
    idea_diversity: number;
    novelty_index?: number;
    processing_time?: number;
  };
}

// 分析历史响应
export interface AnalysisHistoryResponse {
  success: boolean;
  analyses: Array<{
    id: string;
    analysis_type: string;
    dominant_thinking_style: string;
    balance_index: number;
    confidence_score: number;
    created_at: string;
    tags: string[];
    summary?: string;
  }>;
  total_count: number;
  pagination: {
    limit: number;
    offset: number;
    has_more: boolean;
  };
}

// 思维统计响应
export interface ThinkingStatisticsResponse {
  success: boolean;
  user_id: string;
  statistics: {
    total_analyses: number;
    avg_confidence: number;
    avg_balance_index: number;
    avg_processing_time: number;
    style_distribution: Record<string, number>;
    improvement_trend: 'improving' | 'stable' | 'declining';
    user_thinking_stats: Record<string, any>;
  };
  insights: string[];
}

/**
 * 思维分析API服务类
 */
class ThinkingService {
  
  /**
   * 分析思维模式
   */
  async analyzeThinking(request: ThinkingAnalysisRequest): Promise<ThinkingAnalysisResponse> {
    return post<ThinkingAnalysisResponse>('/thinking/analyze', request);
  }

  /**
   * 分析图像思维
   */
  async analyzeImageThinking(
    file: File, 
    userId?: string, 
    saveResult: boolean = true
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (userId) formData.append('user_id', userId);
    formData.append('save_result', saveResult.toString());

    return uploadFile('/thinking/analyze-image', file);
  }

  /**
   * 生成创意想法
   */
  async generateCreativeIdeas(request: CreativeIdeaRequest): Promise<CreativeIdeaResponse> {
    const formData = new FormData();
    formData.append('prompt', request.prompt);
    formData.append('num_ideas', (request.num_ideas || 3).toString());
    formData.append('creativity_level', (request.creativity_level || 0.8).toString());
    if (request.user_id) formData.append('user_id', request.user_id);

    return post<CreativeIdeaResponse>('/thinking/generate-ideas', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * 获取分析历史
   */
  async getAnalysisHistory(
    userId: string,
    limit: number = 20,
    offset: number = 0,
    analysisType?: string
  ): Promise<AnalysisHistoryResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    
    if (analysisType) {
      params.append('analysis_type', analysisType);
    }

    return get<AnalysisHistoryResponse>(`/thinking/history/${userId}?${params}`);
  }

  /**
   * 获取分析详情
   */
  async getAnalysisDetail(analysisId: string): Promise<any> {
    return get(`/thinking/analysis/${analysisId}`);
  }

  /**
   * 获取思维统计
   */
  async getThinkingStatistics(userId: string): Promise<ThinkingStatisticsResponse> {
    return get<ThinkingStatisticsResponse>(`/thinking/statistics/${userId}`);
  }

  /**
   * 提交分析反馈
   */
  async submitFeedback(
    analysisId: string,
    feedback: {
      rating: number;
      feedback_text?: string;
      is_accurate?: number;
      suggestions?: string;
    }
  ): Promise<{ success: boolean; message?: string }> {
    return post(`/thinking/feedback/${analysisId}`, feedback);
  }

  /**
   * 获取思维风格建议
   */
  async getThinkingStyleSuggestions(userId: string): Promise<{
    success: boolean;
    suggestions: Array<{
      style: string;
      description: string;
      improvement_tips: string[];
      exercises: string[];
    }>;
  }> {
    return get(`/thinking/suggestions/${userId}`);
  }

  /**
   * 比较思维分析结果
   */
  async compareAnalyses(
    analysisIds: string[]
  ): Promise<{
    success: boolean;
    comparison: {
      common_patterns: string[];
      differences: Record<string, any>;
      evolution_trend?: string;
      recommendations: string[];
    };
  }> {
    return post('/thinking/compare', { analysis_ids: analysisIds });
  }

  /**
   * 导出分析报告
   */
  async exportAnalysisReport(
    userId: string,
    format: 'pdf' | 'csv' | 'json' = 'pdf',
    dateRange?: {
      start_date: string;
      end_date: string;
    }
  ): Promise<Blob> {
    const params = new URLSearchParams({
      format,
    });
    
    if (dateRange) {
      params.append('start_date', dateRange.start_date);
      params.append('end_date', dateRange.end_date);
    }

    const response = await get(`/thinking/export/${userId}?${params}`, {
      responseType: 'blob',
    });
    
    return response;
  }

  /**
   * 获取实时思维分析流
   * （用于实时文本分析）
   */
  async getRealtimeAnalysis(text: string): Promise<{
    partial_analysis: any;
    confidence: number;
    suggestions: string[];
  }> {
    return post('/thinking/realtime', { text });
  }

  /**
   * 搜索相似分析
   */
  async searchSimilarAnalyses(
    query: string,
    userId?: string,
    limit: number = 10
  ): Promise<{
    success: boolean;
    similar_analyses: Array<{
      id: string;
      similarity_score: number;
      summary: string;
      created_at: string;
    }>;
  }> {
    return post('/thinking/search', {
      query,
      user_id: userId,
      limit,
    });
  }
}

// 创建并导出服务实例
export const thinkingService = new ThinkingService();
export default thinkingService; 