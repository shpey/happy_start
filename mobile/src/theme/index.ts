import { DefaultTheme, MD3DarkTheme } from 'react-native-paper';

// 自定义颜色配置
const colors = {
  primary: '#6200ea',
  primaryVariant: '#3700b3',
  secondary: '#03dac6',
  secondaryVariant: '#018786',
  background: '#ffffff',
  surface: '#ffffff',
  error: '#b00020',
  onPrimary: '#ffffff',
  onSecondary: '#000000',
  onBackground: '#000000',
  onSurface: '#000000',
  onError: '#ffffff',
};

const darkColors = {
  primary: '#bb86fc',
  primaryVariant: '#3700b3',
  secondary: '#03dac6',
  secondaryVariant: '#03dac6',
  background: '#121212',
  surface: '#121212',
  error: '#cf6679',
  onPrimary: '#000000',
  onSecondary: '#000000',
  onBackground: '#ffffff',
  onSurface: '#ffffff',
  onError: '#000000',
};

// 亮色主题
export const lightTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    ...colors,
  },
};

// 暗色主题
export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    ...darkColors,
  },
};

// 默认导出亮色主题
export const theme = lightTheme;

// 主题类型
export type Theme = typeof lightTheme; 