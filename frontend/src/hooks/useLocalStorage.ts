/**
 * 本地存储Hook
 * 用于持久化用户偏好设置和状态
 */

import { useState, useEffect } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void] {
  // 获取存储的值或使用初始值
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // 返回包装后的setState函数，会同时更新localStorage
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // 允许value是函数，这样我们可以有与useState相同的API
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      
      // 保存状态
      setStoredValue(valueToStore);
      
      // 保存到localStorage
      if (valueToStore === undefined) {
        window.localStorage.removeItem(key);
      } else {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}

// 预定义的存储键
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'intelligent_thinking_user_preferences',
  THEME_MODE: 'intelligent_thinking_theme_mode',
  SIDEBAR_COLLAPSED: 'intelligent_thinking_sidebar_collapsed',
  RECENT_ACTIVITIES: 'intelligent_thinking_recent_activities',
  THINKING_HISTORY: 'intelligent_thinking_history',
  KNOWLEDGE_GRAPH_LAYOUT: 'intelligent_thinking_graph_layout',
  COLLABORATION_SETTINGS: 'intelligent_thinking_collab_settings',
  THREED_CAMERA_POSITION: 'intelligent_thinking_3d_camera'
} as const; 