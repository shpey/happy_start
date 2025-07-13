/**
 * 增强的通知上下文
 * 支持WebSocket实时通知、本地通知和多种通知类型
 */

import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useLocalStorage, STORAGE_KEYS } from '../hooks/useLocalStorage';

export type NotificationType = 'success' | 'error' | 'warning' | 'info' | 'collaboration' | 'system';
export type NotificationPriority = 'low' | 'normal' | 'high' | 'urgent';

export interface Notification {
  id: string;
  type: NotificationType;
  priority: NotificationPriority;
  title?: string;
  message: string;
  duration?: number;
  action?: React.ReactNode;
  persist?: boolean;
  timestamp: Date;
  read: boolean;
  source: 'local' | 'websocket' | 'api';
  data?: any; // 额外数据
}

export interface NotificationSettings {
  enableWebSocketNotifications: boolean;
  enableBrowserNotifications: boolean;
  enableSoundNotifications: boolean;
  enableCollaborationNotifications: boolean;
  enableSystemNotifications: boolean;
  maxNotificationsDisplay: number;
  defaultDuration: number;
  sounds: {
    [key in NotificationType]: string;
  };
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  settings: NotificationSettings;
  
  // 通知管理
  showNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read' | 'source'>) => string;
  hideNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
  clearByType: (type: NotificationType) => void;
  
  // 便捷方法
  success: (message: string, title?: string, options?: Partial<Notification>) => string;
  error: (message: string, title?: string, options?: Partial<Notification>) => string;
  warning: (message: string, title?: string, options?: Partial<Notification>) => string;
  info: (message: string, title?: string, options?: Partial<Notification>) => string;
  collaboration: (message: string, title?: string, data?: any) => string;
  system: (message: string, title?: string, data?: any) => string;
  
  // 设置管理
  updateSettings: (newSettings: Partial<NotificationSettings>) => void;
  
  // 权限管理
  requestBrowserPermission: () => Promise<boolean>;
  browserPermissionGranted: boolean;
  
  // WebSocket状态
  isWebSocketConnected: boolean;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const defaultSettings: NotificationSettings = {
  enableWebSocketNotifications: true,
  enableBrowserNotifications: true,
  enableSoundNotifications: false,
  enableCollaborationNotifications: true,
  enableSystemNotifications: true,
  maxNotificationsDisplay: 10,
  defaultDuration: 5000,
  sounds: {
    success: '/sounds/success.mp3',
    error: '/sounds/error.mp3',
    warning: '/sounds/warning.mp3',
    info: '/sounds/info.mp3',
    collaboration: '/sounds/collaboration.mp3',
    system: '/sounds/system.mp3'
  }
};

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: React.ReactNode;
  wsUrl?: string;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({
  children,
  wsUrl = 'ws://localhost:8000/ws/notifications'
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [settings, setSettings] = useLocalStorage<NotificationSettings>(
    STORAGE_KEYS.NOTIFICATION_SETTINGS,
    defaultSettings
  );
  const [browserPermissionGranted, setBrowserPermissionGranted] = useState(false);
  
  const audioRef = useRef<{ [key: string]: HTMLAudioElement }>({});
  
  // WebSocket连接
  const {
    isConnected: isWebSocketConnected,
    sendMessage,
    connect: connectWebSocket,
    disconnect: disconnectWebSocket
  } = useWebSocket(wsUrl, {
    onMessage: handleWebSocketMessage,
    onConnect: () => {
      console.log('Notification WebSocket connected');
      showNotification({
        type: 'system',
        priority: 'low',
        message: '实时通知连接已建立',
        duration: 3000
      });
    },
    onDisconnect: () => {
      console.log('Notification WebSocket disconnected');
    }
  });

  // 初始化音频
  useEffect(() => {
    Object.entries(settings.sounds).forEach(([type, src]) => {
      if (src && !audioRef.current[type]) {
        const audio = new Audio(src);
        audio.preload = 'auto';
        audioRef.current[type] = audio;
      }
    });
  }, [settings.sounds]);

  // 检查浏览器通知权限
  useEffect(() => {
    checkBrowserPermission();
  }, []);

  const checkBrowserPermission = () => {
    if ('Notification' in window) {
      setBrowserPermissionGranted(Notification.permission === 'granted');
    }
  };

  const requestBrowserPermission = async (): Promise<boolean> => {
    if (!('Notification' in window)) {
      return false;
    }

    const permission = await Notification.requestPermission();
    const granted = permission === 'granted';
    setBrowserPermissionGranted(granted);
    return granted;
  };

  const generateId = () => `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const handleWebSocketMessage = (data: any) => {
    if (!settings.enableWebSocketNotifications) return;

    try {
      const { type, payload } = data;
      
      switch (type) {
        case 'notification':
          showNotification({
            ...payload,
            source: 'websocket'
          });
          break;
          
        case 'collaboration_update':
          if (settings.enableCollaborationNotifications) {
            showNotification({
              type: 'collaboration',
              priority: 'normal',
              title: '协作更新',
              message: payload.message,
              data: payload.data,
              source: 'websocket'
            });
          }
          break;
          
        case 'system_announcement':
          if (settings.enableSystemNotifications) {
            showNotification({
              type: 'system',
              priority: 'high',
              title: '系统公告',
              message: payload.message,
              persist: true,
              source: 'websocket'
            });
          }
          break;
          
        default:
          console.log('Unknown notification type:', type);
      }
    } catch (error) {
      console.error('Failed to handle WebSocket notification:', error);
    }
  };

  const showNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read' | 'source'>): string => {
    const id = generateId();
    const newNotification: Notification = {
      id,
      timestamp: new Date(),
      read: false,
      source: 'local',
      duration: settings.defaultDuration,
      priority: 'normal',
      ...notification
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev];
      // 限制最大通知数量
      return updated.slice(0, settings.maxNotificationsDisplay * 2); // 保存更多但只显示一部分
    });

    // 播放声音
    if (settings.enableSoundNotifications && audioRef.current[notification.type]) {
      try {
        audioRef.current[notification.type].play().catch(e => {
          console.warn('Failed to play notification sound:', e);
        });
      } catch (error) {
        console.warn('Sound playback error:', error);
      }
    }

    // 显示浏览器通知
    if (settings.enableBrowserNotifications && browserPermissionGranted && 
        (notification.priority === 'high' || notification.priority === 'urgent')) {
      try {
        new Notification(notification.title || '通知', {
          body: notification.message,
          icon: '/favicon.ico',
          tag: id
        });
      } catch (error) {
        console.warn('Browser notification error:', error);
      }
    }

    // 自动隐藏（如果不是持久通知）
    if (!newNotification.persist && newNotification.duration! > 0) {
      setTimeout(() => {
        hideNotification(id);
      }, newNotification.duration);
    }

    return id;
  }, [settings, browserPermissionGranted]);

  const hideNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => prev.map(notification =>
      notification.id === id ? { ...notification, read: true } : notification
    ));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(notification => ({ ...notification, read: true })));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const clearByType = useCallback((type: NotificationType) => {
    setNotifications(prev => prev.filter(notification => notification.type !== type));
  }, []);

  // 便捷方法
  const success = useCallback((message: string, title?: string, options?: Partial<Notification>): string => {
    return showNotification({ type: 'success', message, title, ...options });
  }, [showNotification]);

  const error = useCallback((message: string, title?: string, options?: Partial<Notification>): string => {
    return showNotification({ 
      type: 'error', 
      message, 
      title, 
      persist: true, 
      priority: 'high',
      ...options 
    });
  }, [showNotification]);

  const warning = useCallback((message: string, title?: string, options?: Partial<Notification>): string => {
    return showNotification({ 
      type: 'warning', 
      message, 
      title, 
      duration: 8000,
      priority: 'normal',
      ...options 
    });
  }, [showNotification]);

  const info = useCallback((message: string, title?: string, options?: Partial<Notification>): string => {
    return showNotification({ type: 'info', message, title, ...options });
  }, [showNotification]);

  const collaboration = useCallback((message: string, title?: string, data?: any): string => {
    return showNotification({ 
      type: 'collaboration', 
      message, 
      title, 
      data,
      priority: 'normal',
      duration: 10000 
    });
  }, [showNotification]);

  const system = useCallback((message: string, title?: string, data?: any): string => {
    return showNotification({ 
      type: 'system', 
      message, 
      title, 
      data,
      priority: 'high',
      persist: true 
    });
  }, [showNotification]);

  const updateSettings = useCallback((newSettings: Partial<NotificationSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, [setSettings]);

  // 计算未读数量
  const unreadCount = notifications.filter(n => !n.read).length;

  const contextValue: NotificationContextType = {
    notifications,
    unreadCount,
    settings,
    showNotification,
    hideNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    clearByType,
    success,
    error,
    warning,
    info,
    collaboration,
    system,
    updateSettings,
    requestBrowserPermission,
    browserPermissionGranted,
    isWebSocketConnected,
    connectWebSocket,
    disconnectWebSocket
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
};

// Hook for using notifications
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
  analysisComplete: (type: string, duration: number) => ({
    type: 'success' as NotificationType,
    priority: 'normal' as NotificationPriority,
    title: '分析完成',
    message: `${type}思维分析已完成，用时 ${duration.toFixed(1)} 秒`,
    duration: 6000
  }),

  // 保存成功
  saveSuccess: () => ({
    type: 'success' as NotificationType,
    priority: 'low' as NotificationPriority,
    message: '数据已成功保存到云端',
    duration: 3000
  }),

  // 连接错误
  connectionError: (service?: string) => ({
    type: 'error' as NotificationType,
    priority: 'high' as NotificationPriority,
    title: '连接失败',
    message: `无法连接到${service || ''}服务器，请检查网络连接并重试`,
    persist: true
  }),

  // 功能开发中
  featureInDevelopment: (feature: string) => ({
    type: 'info' as NotificationType,
    priority: 'low' as NotificationPriority,
    title: '功能开发中',
    message: `${feature}功能正在开发中，敬请期待！`,
    duration: 4000
  }),

  // 协作邀请
  collaborationInvite: (userName: string, sessionId: string) => ({
    type: 'collaboration' as NotificationType,
    priority: 'normal' as NotificationPriority,
    title: '协作邀请',
    message: `${userName} 邀请您加入思维协作会话`,
    duration: 15000,
    data: { sessionId, userName }
  }),

  // 权限错误
  permissionDenied: (action: string) => ({
    type: 'warning' as NotificationType,
    priority: 'normal' as NotificationPriority,
    title: '权限不足',
    message: `您没有权限进行${action}操作`,
    duration: 5000
  }),

  // 安全警告
  securityWarning: (message: string) => ({
    type: 'warning' as NotificationType,
    priority: 'urgent' as NotificationPriority,
    title: '安全警告',
    message,
    persist: true
  })
}; 