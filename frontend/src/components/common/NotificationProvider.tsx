/**
 * 全局通知系统
 * 提供统一的消息提示功能
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Slide,
  SlideProps,
  IconButton,
  Box
} from '@mui/material';
import { Close } from '@mui/icons-material';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title?: string;
  message: string;
  duration?: number;
  action?: React.ReactNode;
  persist?: boolean;
}

interface NotificationContextType {
  showNotification: (notification: Omit<Notification, 'id'>) => void;
  hideNotification: (id: string) => void;
  clearAll: () => void;
  // 便捷方法
  success: (message: string, title?: string) => void;
  error: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// 滑动过渡组件
function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

interface NotificationProviderProps {
  children: React.ReactNode;
  maxNotifications?: number;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({
  children,
  maxNotifications = 5
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const generateId = () => `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const showNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = generateId();
    const newNotification: Notification = {
      id,
      duration: 5000,
      ...notification
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev];
      // 限制最大通知数量
      return updated.slice(0, maxNotifications);
    });

    // 自动隐藏（如果不是持久通知）
    if (!newNotification.persist && newNotification.duration! > 0) {
      setTimeout(() => {
        hideNotification(id);
      }, newNotification.duration);
    }
  }, [maxNotifications]);

  const hideNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  // 便捷方法
  const success = useCallback((message: string, title?: string) => {
    showNotification({ type: 'success', message, title });
  }, [showNotification]);

  const error = useCallback((message: string, title?: string) => {
    showNotification({ type: 'error', message, title, duration: 0, persist: true });
  }, [showNotification]);

  const warning = useCallback((message: string, title?: string) => {
    showNotification({ type: 'warning', message, title, duration: 8000 });
  }, [showNotification]);

  const info = useCallback((message: string, title?: string) => {
    showNotification({ type: 'info', message, title });
  }, [showNotification]);

  const contextValue: NotificationContextType = {
    showNotification,
    hideNotification,
    clearAll,
    success,
    error,
    warning,
    info
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      
      {/* 通知容器 */}
      <Box sx={{ position: 'fixed', top: 88, right: 24, zIndex: 9999 }}>
        {notifications.map((notification, index) => (
          <Snackbar
            key={notification.id}
            open={true}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            TransitionComponent={SlideTransition}
            sx={{
              position: 'static',
              mb: index > 0 ? 1 : 0,
              transform: 'none !important'
            }}
          >
            <Alert
              severity={notification.type}
              variant="filled"
              sx={{ 
                minWidth: 300,
                maxWidth: 400,
                boxShadow: 3
              }}
              action={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {notification.action}
                  <IconButton
                    size="small"
                    color="inherit"
                    onClick={() => hideNotification(notification.id)}
                  >
                    <Close fontSize="small" />
                  </IconButton>
                </Box>
              }
            >
              {notification.title && (
                <AlertTitle>{notification.title}</AlertTitle>
              )}
              {notification.message}
            </Alert>
          </Snackbar>
        ))}
      </Box>
    </NotificationContext.Provider>
  );
};

// Hook for using notifications
export const useNotification = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    const error = new Error('useNotification must be used within a NotificationProvider');
    throw error;
  }
  return context;
};

// 预设通知模板
export const NotificationTemplates = {
  // AI分析完成
  analysisComplete: (type: string) => ({
    type: 'success' as NotificationType,
    title: '分析完成',
    message: `${type}思维分析已完成，查看结果获取详细洞察。`,
    duration: 6000
  }),

  // 保存成功
  saveSuccess: () => ({
    type: 'success' as NotificationType,
    message: '数据已成功保存到云端',
    duration: 3000
  }),

  // 连接错误
  connectionError: () => ({
    type: 'error' as NotificationType,
    title: '连接失败',
    message: '无法连接到服务器，请检查网络连接并重试。',
    persist: true
  }),

  // 功能开发中
  featureInDevelopment: (feature: string) => ({
    type: 'info' as NotificationType,
    title: '功能开发中',
    message: `${feature}功能正在开发中，敬请期待！`,
    duration: 4000
  }),

  // 协作邀请
  collaborationInvite: (userName: string) => ({
    type: 'info' as NotificationType,
    title: '协作邀请',
    message: `${userName} 邀请您加入思维协作会话`,
    duration: 10000
  })
}; 