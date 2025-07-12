// 基本类型定义
export interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ThinkingNode {
  id: string;
  title: string;
  content: string;
  type: 'thought' | 'idea' | 'question' | 'answer';
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  userId: string;
  parentId?: string;
  children?: ThinkingNode[];
}

export interface KnowledgeGraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
  x?: number;
  y?: number;
  z?: number;
}

export interface KnowledgeGraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}

export interface ThreeDPosition {
  x: number;
  y: number;
  z: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  userId?: string;
}

// 主题类型
export type ThemeMode = 'light' | 'dark';

export interface ThemeSettings {
  mode: ThemeMode;
  primaryColor: string;
  secondaryColor: string;
  fontSize: number;
}

// 错误类型
export interface AppError {
  code: string;
  message: string;
  details?: any;
}

// 加载状态
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

// 分页
export interface PaginationParams {
  page: number;
  limit: number;
  total?: number;
}

// 搜索
export interface SearchParams {
  query: string;
  filters?: Record<string, any>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// 导出所有类型
export type * from './index'; 