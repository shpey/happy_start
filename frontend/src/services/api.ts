/**
 * API 服务配置
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API 基础配置
const API_BASE_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private api: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器 - 添加认证token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器 - 处理token过期
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // 如果正在刷新token，将请求加入队列
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(this.api(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }

            const response = await this.api.post('/users/refresh', {
              refresh_token: refreshToken
            });

            const { access_token } = response.data;
            localStorage.setItem('access_token', access_token);

            // 通知所有等待的请求使用新token
            this.refreshSubscribers.forEach((callback) => callback(access_token));
            this.refreshSubscribers = [];

            // 重新发送原始请求
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            // 刷新失败，清除所有认证信息
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_info');
            
            // 重定向到登录页面
            window.location.href = '/login';
            
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // GET 请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.get(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // POST 请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.post(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // PUT 请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.put(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // PATCH 请求
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.patch(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // DELETE 请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.delete(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // 文件上传
  async uploadFile<T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response: AxiosResponse<T> = await this.api.post(url, formData, {
        ...config,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...config?.headers
        }
      });
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // 下载文件
  async downloadFile(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void> {
    try {
      const response = await this.api.get(url, {
        ...config,
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // 批量请求
  async batchRequest<T = any>(requests: Array<{ url: string; method: string; data?: any }>): Promise<T[]> {
    try {
      const promises = requests.map(req => {
        switch (req.method.toLowerCase()) {
          case 'get':
            return this.get(req.url);
          case 'post':
            return this.post(req.url, req.data);
          case 'put':
            return this.put(req.url, req.data);
          case 'patch':
            return this.patch(req.url, req.data);
          case 'delete':
            return this.delete(req.url);
          default:
            throw new Error(`Unsupported method: ${req.method}`);
        }
      });

      return await Promise.all(promises);
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  // 错误处理
  private handleError(error: any) {
    if (error.response) {
      // 服务器返回错误状态码
      console.error('API Error:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url
      });
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('Network Error:', error.message);
    } else {
      // 其他错误
      console.error('Error:', error.message);
    }
  }

  // 设置默认请求头
  setDefaultHeader(key: string, value: string) {
    this.api.defaults.headers.common[key] = value;
  }

  // 移除默认请求头
  removeDefaultHeader(key: string) {
    delete this.api.defaults.headers.common[key];
  }

  // 创建取消令牌
  createCancelToken() {
    return axios.CancelToken.source();
  }

  // 检查是否是取消请求的错误
  isCancel(error: any) {
    return axios.isCancel(error);
  }

  // 获取axios实例
  getInstance() {
    return this.api;
  }
}

// 导出单例实例
export const apiService = new ApiService();
export default apiService;

// 导出类型
export type {
  AxiosRequestConfig,
  AxiosResponse
}; 