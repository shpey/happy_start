import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Keychain from 'react-native-keychain';

// 用户接口
interface User {
  id: string;
  username: string;
  email: string;
  fullName?: string;
  avatar?: string;
}

// 认证上下文接口
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: { username: string; password: string }) => Promise<boolean>;
  logout: () => Promise<void>;
  register: (userData: any) => Promise<boolean>;
  checkAuthStatus: () => Promise<void>;
}

// 创建上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider 属性接口
interface AuthProviderProps {
  children: ReactNode;
}

// AuthProvider 组件
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // 检查认证状态
  const checkAuthStatus = async () => {
    try {
      setIsLoading(true);
      const credentials = await Keychain.getInternetCredentials('user_credentials');
      
      if (credentials) {
        const userData = JSON.parse(credentials.password);
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('检查认证状态失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 登录
  const login = async (credentials: { username: string; password: string }): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // 模拟API调用
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        const userData: User = data.user;
        
        // 保存凭据到Keychain
        await Keychain.setInternetCredentials(
          'user_credentials',
          credentials.username,
          JSON.stringify(userData)
        );
        
        setUser(userData);
        setIsAuthenticated(true);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('登录失败:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 注册
  const register = async (userData: any): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // 模拟API调用
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        const newUser: User = data.user;
        
        // 保存凭据到Keychain
        await Keychain.setInternetCredentials(
          'user_credentials',
          userData.username,
          JSON.stringify(newUser)
        );
        
        setUser(newUser);
        setIsAuthenticated(true);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('注册失败:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 登出
  const logout = async () => {
    try {
      // 清除Keychain
      await Keychain.resetInternetCredentials('user_credentials');
      
      // 清除AsyncStorage
      await AsyncStorage.removeItem('user_data');
      
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('登出失败:', error);
    }
  };

  // 初始化时检查认证状态
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook for using auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 