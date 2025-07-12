/**
 * 主题上下文
 * 支持明暗主题切换和主题定制
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createTheme, ThemeProvider, PaletteMode } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { useLocalStorage, STORAGE_KEYS } from '../hooks/useLocalStorage';

// 主题配置类型
interface ThemeConfig {
  mode: PaletteMode;
  primaryColor: string;
  secondaryColor: string;
  borderRadius: number;
  fontFamily: string;
}

// 主题上下文类型
interface ThemeContextType {
  themeConfig: ThemeConfig;
  toggleMode: () => void;
  updateTheme: (config: Partial<ThemeConfig>) => void;
  resetTheme: () => void;
  isDarkMode: boolean;
}

// 默认主题配置
const defaultThemeConfig: ThemeConfig = {
  mode: 'light',
  primaryColor: '#1976d2',
  secondaryColor: '#dc004e',
  borderRadius: 8,
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif'
};

// 预设主题
export const themePresets = {
  default: {
    name: '默认蓝色',
    primaryColor: '#1976d2',
    secondaryColor: '#dc004e'
  },
  purple: {
    name: '紫色科技',
    primaryColor: '#7c4dff',
    secondaryColor: '#ff4081'
  },
  green: {
    name: '自然绿色',
    primaryColor: '#4caf50',
    secondaryColor: '#ff9800'
  },
  orange: {
    name: '活力橙色',
    primaryColor: '#ff9800',
    secondaryColor: '#3f51b5'
  },
  teal: {
    name: '青色清新',
    primaryColor: '#009688',
    secondaryColor: '#e91e63'
  }
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface CustomThemeProviderProps {
  children: ReactNode;
}

export const CustomThemeProvider: React.FC<CustomThemeProviderProps> = ({ children }) => {
  const [themeConfig, setThemeConfig] = useLocalStorage<ThemeConfig>(
    STORAGE_KEYS.THEME_MODE,
    defaultThemeConfig
  );

  // 检测系统主题偏好
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      // 只有在用户没有手动设置过主题时才自动切换
      const userHasSetTheme = localStorage.getItem(STORAGE_KEYS.THEME_MODE);
      if (!userHasSetTheme) {
        setThemeConfig(prev => ({
          ...prev,
          mode: e.matches ? 'dark' : 'light'
        }));
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    
    // 初始检查
    const userHasSetTheme = localStorage.getItem(STORAGE_KEYS.THEME_MODE);
    if (!userHasSetTheme) {
      setThemeConfig(prev => ({
        ...prev,
        mode: mediaQuery.matches ? 'dark' : 'light'
      }));
    }

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [setThemeConfig]);

  // 创建Material-UI主题
  const theme = createTheme({
    palette: {
      mode: themeConfig.mode,
      primary: {
        main: themeConfig.primaryColor,
      },
      secondary: {
        main: themeConfig.secondaryColor,
      },
      background: {
        default: themeConfig.mode === 'dark' ? '#121212' : '#f5f5f5',
        paper: themeConfig.mode === 'dark' ? '#1e1e1e' : '#ffffff',
      },
      // 智能思维平台特色色彩
      ...(themeConfig.mode === 'dark' ? {
        // 暗色模式特殊配置
        info: {
          main: '#29b6f6',
        },
        success: {
          main: '#66bb6a',
        },
        warning: {
          main: '#ffa726',
        },
        error: {
          main: '#f44336',
        }
      } : {
        // 明亮模式特殊配置
        info: {
          main: '#0288d1',
        },
        success: {
          main: '#2e7d32',
        },
        warning: {
          main: '#ed6c02',
        },
        error: {
          main: '#d32f2f',
        }
      })
    },
    typography: {
      fontFamily: themeConfig.fontFamily,
      h1: {
        fontWeight: 600,
        fontSize: '2.5rem',
      },
      h2: {
        fontWeight: 600,
        fontSize: '2rem',
      },
      h3: {
        fontWeight: 600,
        fontSize: '1.75rem',
      },
      h4: {
        fontWeight: 600,
        fontSize: '1.5rem',
      },
      h5: {
        fontWeight: 600,
        fontSize: '1.25rem',
      },
      h6: {
        fontWeight: 600,
        fontSize: '1.125rem',
      },
      subtitle1: {
        fontWeight: 500,
      },
      subtitle2: {
        fontWeight: 500,
      },
      button: {
        fontWeight: 500,
        textTransform: 'none',
      },
    },
    shape: {
      borderRadius: themeConfig.borderRadius,
    },
    components: {
      // Card组件样式
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: themeConfig.mode === 'dark' 
              ? '0 4px 20px rgba(0,0,0,0.3)' 
              : '0 2px 8px rgba(0,0,0,0.1)',
            borderRadius: themeConfig.borderRadius,
            transition: 'box-shadow 0.3s ease-in-out',
            '&:hover': {
              boxShadow: themeConfig.mode === 'dark'
                ? '0 8px 30px rgba(0,0,0,0.4)'
                : '0 4px 16px rgba(0,0,0,0.15)',
            },
          },
        },
      },
      // Button组件样式
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: themeConfig.borderRadius,
            padding: '8px 24px',
            fontSize: '0.95rem',
            transition: 'all 0.2s ease-in-out',
          },
          contained: {
            boxShadow: 'none',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              transform: 'translateY(-1px)',
            },
          },
        },
      },
      // Paper组件样式
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: themeConfig.borderRadius,
            ...(themeConfig.mode === 'dark' && {
              backgroundImage: 'none',
            }),
          },
        },
      },
      // Drawer组件样式
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRadius: 0,
            ...(themeConfig.mode === 'dark' && {
              backgroundColor: '#1a1a1a',
              borderRight: '1px solid rgba(255,255,255,0.12)',
            }),
          },
        },
      },
      // AppBar组件样式
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: 'none',
            borderBottom: themeConfig.mode === 'dark' 
              ? '1px solid rgba(255,255,255,0.12)'
              : '1px solid rgba(0,0,0,0.12)',
          },
        },
      },
      // TextField组件样式
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: themeConfig.borderRadius,
            },
          },
        },
      },
      // Chip组件样式
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: themeConfig.borderRadius / 2,
          },
        },
      },
    },
  });

  // 主题操作函数
  const toggleMode = () => {
    setThemeConfig(prev => ({
      ...prev,
      mode: prev.mode === 'light' ? 'dark' : 'light'
    }));
  };

  const updateTheme = (config: Partial<ThemeConfig>) => {
    setThemeConfig(prev => ({ ...prev, ...config }));
  };

  const resetTheme = () => {
    setThemeConfig(defaultThemeConfig);
  };

  const contextValue: ThemeContextType = {
    themeConfig,
    toggleMode,
    updateTheme,
    resetTheme,
    isDarkMode: themeConfig.mode === 'dark'
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};

// Hook for using theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a CustomThemeProvider');
  }
  return context;
};

export { ThemeContext }; 