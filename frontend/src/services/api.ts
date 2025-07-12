/**
 * API服务配置
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API基础配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30秒超时

// 创建axios实例
export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 添加认证token
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加请求时间戳
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error);
    
    // 处理认证错误
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    
    // 处理网络错误
    if (!error.response) {
      console.error('Network Error: 无法连接到服务器');
    }
    
    return Promise.reject(error);
  }
);

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// API错误类
export class ApiError extends Error {
  public status: number;
  public data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// 通用API调用函数
export const apiCall = async <T = any>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response = await apiClient(config);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new ApiError(
        error.response.data?.message || error.message,
        error.response.status,
        error.response.data
      );
    } else {
      throw new ApiError(error.message, 0, null);
    }
  }
};

// GET请求
export const get = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  return apiCall<T>({ method: 'GET', url, ...config });
};

// POST请求
export const post = <T = any>(
  url: string, 
  data?: any, 
  config?: AxiosRequestConfig
): Promise<T> => {
  return apiCall<T>({ method: 'POST', url, data, ...config });
};

// PUT请求
export const put = <T = any>(
  url: string, 
  data?: any, 
  config?: AxiosRequestConfig
): Promise<T> => {
  return apiCall<T>({ method: 'PUT', url, data, ...config });
};

// DELETE请求
export const del = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  return apiCall<T>({ method: 'DELETE', url, ...config });
};

// 文件上传
export const uploadFile = async (
  url: string,
  file: File,
  onUploadProgress?: (progress: number) => void
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  return apiCall({
    method: 'POST',
    url,
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onUploadProgress(progress);
      }
    },
  });
};

export default apiClient; 