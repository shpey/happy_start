import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import apiService from '../services/api';

interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  is_active: boolean;
  is_verified: boolean;
  is_premium: boolean;
  created_at: string;
  thinking_stats: {
    total_analyses: number;
    dominant_style?: string;
    average_scores: Record<string, number>;
    improvement_trend: string;
  };
}

interface AuthContextType {
  user: User | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => Promise<void>;
  refreshToken: () => Promise<void>;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isLoggedIn = !!user;

  // 初始化时检查本地存储的用户信息
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const userInfo = localStorage.getItem('user_info');

        if (token && userInfo) {
          const userData = JSON.parse(userInfo);
          setUser(userData);
          
          // 验证token是否仍然有效
          try {
            const response = await apiService.get('/users/me');
            if (response.success !== false) {
              setUser(response);
              localStorage.setItem('user_info', JSON.stringify(response));
            }
          } catch (error) {
            // Token无效，清除本地存储
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_info');
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const response = await apiService.post('/users/login', { username, password });
      
      if (response.success !== false) {
        const { access_token, refresh_token, user: userData } = response;
        
        // 存储令牌和用户信息
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('user_info', JSON.stringify(userData));
        
        setUser(userData);
      } else {
        throw new Error(response.message || '登录失败');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // 注册
  const register = async (userData: RegisterData) => {
    try {
      const response = await apiService.post('/users/register', userData);
      
      if (response.success !== false) {
        const { access_token, refresh_token, user: newUser } = response;
        
        // 存储令牌和用户信息
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('user_info', JSON.stringify(newUser));
        
        setUser(newUser);
      } else {
        throw new Error(response.message || '注册失败');
      }
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  };

  // 登出
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
    setUser(null);
  };

  // 更新用户信息
  const updateUser = async (userData: Partial<User>) => {
    try {
      const response = await apiService.post('/users/me', userData);
      
      if (response.success !== false) {
        setUser(response);
        localStorage.setItem('user_info', JSON.stringify(response));
      } else {
        throw new Error(response.message || '更新用户信息失败');
      }
    } catch (error) {
      console.error('Update user error:', error);
      throw error;
    }
  };

  // 刷新令牌
  const refreshToken = async () => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) {
        throw new Error('No refresh token available');
      }

      const response = await apiService.post('/users/refresh', { refresh_token: refreshTokenValue });
      
      if (response.success !== false) {
        const { access_token } = response;
        localStorage.setItem('access_token', access_token);
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      logout(); // 刷新失败则登出
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isLoggedIn,
    isLoading,
    login,
    register,
    logout,
    updateUser,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 