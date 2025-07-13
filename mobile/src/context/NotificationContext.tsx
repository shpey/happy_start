import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import Toast from 'react-native-toast-message';

// 通知类型
type NotificationType = 'success' | 'error' | 'warning' | 'info';

// 通知接口
interface Notification {
  id: string;
  type: NotificationType;
  title?: string;
  message: string;
  duration?: number;
  persist?: boolean;
  action?: React.ReactNode;
}

// 通知上下文接口
interface NotificationContextType {
  showNotification: (notification: Omit<Notification, 'id'>) => void;
  hideNotification: (id: string) => void;
  clearAll: () => void;
  success: (message: string, title?: string) => void;
  error: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
}

// 创建上下文
const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// Provider 属性接口
interface NotificationProviderProps {
  children: ReactNode;
  maxNotifications?: number;
}

// NotificationProvider 组件
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

    // 使用 Toast 显示通知
    Toast.show({
      type: newNotification.type,
      text1: newNotification.title || getDefaultTitle(newNotification.type),
      text2: newNotification.message,
      visibilityTime: newNotification.duration || 5000,
      autoHide: !newNotification.persist,
      position: 'top',
      topOffset: 50,
    });

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
    Toast.hide();
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
    Toast.hide();
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
      <Toast />
    </NotificationContext.Provider>
  );
};

// 获取默认标题
const getDefaultTitle = (type: NotificationType): string => {
  switch (type) {
    case 'success':
      return '成功';
    case 'error':
      return '错误';
    case 'warning':
      return '警告';
    case 'info':
      return '信息';
    default:
      return '通知';
  }
};

// Hook for using notification context
export const useNotification = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
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