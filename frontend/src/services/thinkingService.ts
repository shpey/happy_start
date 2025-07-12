/**
 * 思维分析服务
 */

import apiService from './api';

export interface ThinkingAnalysisRequest {
  text: string;
  analysis_type?: 'comprehensive' | 'visual' | 'logical' | 'creative';
  save_result?: boolean;
  user_id?: string;
}

export interface ThinkingAnalysisResponse {
  success: boolean;
  analysis_id?: string;
  results: {
    visual_thinking?: {
      score: number;
      concepts: string[];
      associations: string[];
    };
    logical_thinking?: {
      score: number;
      reasoning_steps: string[];
      conclusions: string[];
    };
    creative_thinking?: {
      score: number;
      innovations: string[];
      possibilities: string[];
    };
  };
  thinking_summary: {
    dominant_thinking_style: string;
    thinking_scores: Record<string, number>;
    balance_index: number;
    insights: string[];
  };
  timestamp: string;
  error?: string;
}

export interface ThinkingAnalysisHistory {
  id: number;
  input_text: string;
  analysis_type: string;
  thinking_summary: {
    dominant_thinking_style: string;
    thinking_scores: Record<string, number>;
    balance_index: number;
  };
  created_at: string;
  is_favorited: boolean;
}

export interface ThinkingStatistics {
  total_analyses: number;
  dominant_style: string;
  average_scores: Record<string, number>;
  improvement_trend: string;
  recent_analyses: number;
  favorite_count: number;
}

export interface CreativeIdeasRequest {
  prompt: string;
  num_ideas?: number;
  creativity_level?: number;
  user_id?: string;
}

export interface CreativeIdeasResponse {
  success: boolean;
  prompt: string;
  generated_ideas: Array<{
    title: string;
    description: string;
    novelty: number;
    feasibility: number;
    impact: number;
  }>;
  creativity_metrics: {
    average_creativity_score: number;
    idea_diversity: number;
    novelty_index: number;
  };
}

class ThinkingService {
  
  /**
   * 分析思维模式
   */
  async analyzeThinking(request: ThinkingAnalysisRequest): Promise<ThinkingAnalysisResponse> {
    try {
      const response = await apiService.post('/thinking/analyze', {
        text: request.text,
        analysis_type: request.analysis_type || 'comprehensive',
        save_result: request.save_result !== false,
        user_id: request.user_id
      });

      return response;
    } catch (error) {
      console.error('思维分析失败:', error);
      throw error;
    }
  }

  /**
   * 分析图像思维
   */
  async analyzeImageThinking(file: File, userId?: string): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (userId) {
        formData.append('user_id', userId);
      }
      formData.append('save_result', 'true');

      const response = await apiService.post('/thinking/analyze-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      return response;
    } catch (error) {
      console.error('图像思维分析失败:', error);
      throw error;
    }
  }

  /**
   * 生成创意想法
   */
  async generateCreativeIdeas(request: CreativeIdeasRequest): Promise<CreativeIdeasResponse> {
    try {
      const formData = new FormData();
      formData.append('prompt', request.prompt);
      formData.append('num_ideas', String(request.num_ideas || 3));
      formData.append('creativity_level', String(request.creativity_level || 0.8));
      if (request.user_id) {
        formData.append('user_id', request.user_id);
      }

      const response = await apiService.post('/thinking/generate-ideas', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      return response;
    } catch (error) {
      console.error('创意生成失败:', error);
      throw error;
    }
  }

  /**
   * 获取思维分析历史
   */
  async getAnalysisHistory(userId: string, options?: {
    limit?: number;
    offset?: number;
    analysis_type?: string;
  }): Promise<ThinkingAnalysisHistory[]> {
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.append('limit', String(options.limit));
      if (options?.offset) params.append('offset', String(options.offset));
      if (options?.analysis_type) params.append('analysis_type', options.analysis_type);

      const response = await apiService.get(`/thinking/history/${userId}?${params.toString()}`);
      return response.history || [];
    } catch (error) {
      console.error('获取分析历史失败:', error);
      throw error;
    }
  }

  /**
   * 获取思维统计信息
   */
  async getThinkingStatistics(userId: string): Promise<ThinkingStatistics> {
    try {
      const response = await apiService.get(`/thinking/statistics/${userId}`);
      return response.statistics;
    } catch (error) {
      console.error('获取思维统计失败:', error);
      throw error;
    }
  }

  /**
   * 收藏/取消收藏分析结果
   */
  async toggleFavorite(analysisId: string, isFavorited: boolean): Promise<void> {
    try {
      await apiService.put(`/thinking/analysis/${analysisId}/favorite`, {
        is_favorited: isFavorited
      });
    } catch (error) {
      console.error('收藏操作失败:', error);
      throw error;
    }
  }

  /**
   * 删除分析结果
   */
  async deleteAnalysis(analysisId: string): Promise<void> {
    try {
      await apiService.delete(`/thinking/analysis/${analysisId}`);
    } catch (error) {
      console.error('删除分析失败:', error);
      throw error;
    }
  }

  /**
   * 获取分析详情
   */
  async getAnalysisDetail(analysisId: string): Promise<any> {
    try {
      const response = await apiService.get(`/thinking/analysis/${analysisId}`);
      return response.analysis;
    } catch (error) {
      console.error('获取分析详情失败:', error);
      throw error;
    }
  }

  /**
   * 更新分析结果
   */
  async updateAnalysis(analysisId: string, updates: {
    is_public?: boolean;
    is_favorited?: boolean;
    tags?: string[];
  }): Promise<void> {
    try {
      await apiService.put(`/thinking/analysis/${analysisId}`, updates);
    } catch (error) {
      console.error('更新分析失败:', error);
      throw error;
    }
  }

  /**
   * 搜索分析结果
   */
  async searchAnalyses(query: string, options?: {
    user_id?: string;
    analysis_type?: string;
    date_from?: string;
    date_to?: string;
    limit?: number;
  }): Promise<ThinkingAnalysisHistory[]> {
    try {
      const params = new URLSearchParams();
      params.append('q', query);
      if (options?.user_id) params.append('user_id', options.user_id);
      if (options?.analysis_type) params.append('analysis_type', options.analysis_type);
      if (options?.date_from) params.append('date_from', options.date_from);
      if (options?.date_to) params.append('date_to', options.date_to);
      if (options?.limit) params.append('limit', String(options.limit));

      const response = await apiService.get(`/thinking/search?${params.toString()}`);
      return response.results || [];
    } catch (error) {
      console.error('搜索分析失败:', error);
      throw error;
    }
  }

  /**
   * 获取推荐的思维练习
   */
  async getRecommendedExercises(userId: string): Promise<any[]> {
    try {
      const response = await apiService.get(`/thinking/exercises/recommended/${userId}`);
      return response.exercises || [];
    } catch (error) {
      console.error('获取推荐练习失败:', error);
      throw error;
    }
  }

  /**
   * 比较两个分析结果
   */
  async compareAnalyses(analysisId1: string, analysisId2: string): Promise<any> {
    try {
      const response = await apiService.post('/thinking/compare', {
        analysis_id_1: analysisId1,
        analysis_id_2: analysisId2
      });
      return response.comparison;
    } catch (error) {
      console.error('比较分析失败:', error);
      throw error;
    }
  }

  /**
   * 获取思维趋势
   */
  async getThinkingTrends(userId: string, timeRange: 'week' | 'month' | 'year' = 'month'): Promise<any> {
    try {
      const response = await apiService.get(`/thinking/trends/${userId}?time_range=${timeRange}`);
      return response.trends;
    } catch (error) {
      console.error('获取思维趋势失败:', error);
      throw error;
    }
  }
}

// 导出单例
export const thinkingService = new ThinkingService();
export default thinkingService; 