// 应用常量
export const constants = {
  APP_NAME: '智能思维',
  VERSION: '1.0.0',
  API_TIMEOUT: 10000,
  
  // 颜色常量
  COLORS: {
    PRIMARY: '#6200ea',
    SECONDARY: '#03dac6',
    SUCCESS: '#4caf50',
    WARNING: '#ff9800',
    ERROR: '#f44336',
    INFO: '#2196f3',
  },
  
  // 尺寸常量
  SIZES: {
    HEADER_HEIGHT: 60,
    TAB_BAR_HEIGHT: 50,
    BORDER_RADIUS: 8,
    SPACING: 16,
  },
  
  // 动画时长
  ANIMATION: {
    FAST: 200,
    NORMAL: 300,
    SLOW: 500,
  },
};

// API端点
export const API_ENDPOINTS = {
  BASE_URL: 'http://localhost:8000',
  AUTH: '/api/v1/auth',
  THINKING: '/api/v1/thinking',
  COLLABORATION: '/api/v1/collaboration',
};

// 存储键
export const STORAGE_KEYS = {
  USER_TOKEN: 'user_token',
  USER_DATA: 'user_data',
  SETTINGS: 'app_settings',
  THEME: 'app_theme',
}; 