import React, { useEffect, useState } from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Platform,
  Alert,
  Dimensions,
  BackHandler,
  AppState,
} from 'react-native';

import { NavigationContainer } from '@react-navigation/native';
import { Provider as PaperProvider } from 'react-native-paper';
import { Provider as StoreProvider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import Toast from 'react-native-toast-message';
import AsyncStorage from '@react-native-async-storage/async-storage';
import DeviceInfo from 'react-native-device-info';
import * as Keychain from 'react-native-keychain';
import { Appearance } from 'react-native';

// 导入自定义组件和服务
import { store, persistor } from './src/store';
import { theme } from './src/theme';
import { AuthProvider } from './src/context/AuthContext';
import { ThemeProvider } from './src/context/ThemeContext';
import { NotificationProvider } from './src/context/NotificationContext';
import { SecurityProvider } from './src/context/SecurityContext';
import {
  NetworkProvider,
  PermissionsProvider,
  BiometricsProvider,
  VoiceProvider,
  CameraProvider,
  LocationProvider,
  BluetoothProvider,
  SensorProvider,
  AudioProvider,
  VideoProvider,
  ARProvider,
  VRProvider,
  AIProvider,
  BlockchainProvider,
  QuantumProvider,
  FederatedLearningProvider,
  AnalyticsProvider,
  PerformanceProvider,
} from './src/context/PlaceholderContexts';

import {
  ErrorBoundary,
  LoadingScreen,
  UpdateModal,
  OnboardingScreen,
  PermissionScreen,
  NetworkErrorScreen,
} from './src/components/common/PlaceholderComponents';

import { MainNavigator } from './src/navigation/MainNavigator';
import { NotificationService } from './src/services/NotificationService';
import {
  AnalyticsService,
  BackgroundTaskService,
  CrashReporter,
} from './src/services/PlaceholderServices';

// 获取设备信息
const { width, height } = Dimensions.get('window');
const isTablet = width >= 768;
const isAndroid = Platform.OS === 'android';
const isIOS = Platform.OS === 'ios';

// 应用状态接口
interface AppStateType {
  isLoading: boolean;
  isInitialized: boolean;
  isOnboarded: boolean;
  isAuthenticated: boolean;
  hasPermissions: boolean;
  isConnected: boolean;
  hasUpdate: boolean;
  showUpdate: boolean;
  currentRoute: string;
  theme: 'light' | 'dark' | 'auto';
  language: string;
  user: any;
  error: string | null;
}

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppStateType>({
    isLoading: true,
    isInitialized: false,
    isOnboarded: false,
    isAuthenticated: false,
    hasPermissions: false,
    isConnected: true, // 默认为连接状态
    hasUpdate: false,
    showUpdate: false,
    currentRoute: 'Loading',
    theme: 'auto',
    language: 'zh-CN',
    user: null,
    error: null,
  });

  // 应用初始化
  useEffect(() => {
    initializeApp();
  }, []);

  // 应用状态监听
  useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, []);

  // 主题变化监听
  useEffect(() => {
    const subscription = Appearance.addChangeListener(({ colorScheme }) => {
      if (appState.theme === 'auto') {
        // 根据系统主题自动切换
        console.log('系统主题变化:', colorScheme);
      }
    });
    return () => subscription?.remove();
  }, [appState.theme]);

  // 初始化应用
  const initializeApp = async () => {
    try {
      console.log('🚀 正在初始化智能思维移动应用...');
      
      // 初始化核心服务
      await initializeCoreServices();
      
      // 检查认证状态
      await checkAuthStatus();
      
      // 检查是否需要引导
      await checkOnboardingStatus();
      
      // 初始化分析服务
      await initializeAnalytics();
      
      // 初始化完成
      setAppState(prev => ({
        ...prev,
        isLoading: false,
        isInitialized: true,
        hasPermissions: true, // 简化处理
      }));
      
      console.log('✅ 应用初始化完成');
      
    } catch (error) {
      console.error('❌ 应用初始化失败:', error);
      handleInitializationError(error);
    }
  };

  // 初始化核心服务
  const initializeCoreServices = async () => {
    try {
      // 初始化通知服务
      await NotificationService.initialize();
      
      console.log('✅ 核心服务初始化完成');
      
    } catch (error) {
      console.error('❌ 核心服务初始化失败:', error);
      throw error;
    }
  };

  // 检查认证状态
  const checkAuthStatus = async () => {
    try {
      const credentials = await Keychain.getInternetCredentials('user_credentials');
      const isAuthenticated = !!credentials;
      
      setAppState(prev => ({
        ...prev,
        isAuthenticated,
        user: isAuthenticated ? JSON.parse(credentials.password) : null
      }));
      
    } catch (error) {
      console.error('❌ 认证状态检查失败:', error);
    }
  };

  // 检查引导状态
  const checkOnboardingStatus = async () => {
    try {
      const hasOnboarded = await AsyncStorage.getItem('has_onboarded');
      
      setAppState(prev => ({
        ...prev,
        isOnboarded: hasOnboarded === 'true'
      }));
      
    } catch (error) {
      console.error('❌ 引导状态检查失败:', error);
    }
  };

  // 初始化分析服务
  const initializeAnalytics = async () => {
    try {
      await AnalyticsService.trackEvent('app_start', {
        platform: Platform.OS,
        version: DeviceInfo.getVersion(),
        device: DeviceInfo.getDeviceId(),
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      console.error('❌ 分析服务初始化失败:', error);
    }
  };

  // 应用状态变化处理
  const handleAppStateChange = (nextAppState: string) => {
    console.log('应用状态变化:', nextAppState);
    
    if (nextAppState === 'active') {
      // 应用进入前台
      console.log('应用进入前台');
    } else if (nextAppState === 'background') {
      // 应用进入后台
      console.log('应用进入后台');
      BackgroundTaskService.startBackgroundTask();
    }
  };

  // 初始化错误处理
  const handleInitializationError = (error: any) => {
    console.error('应用初始化错误:', error);
    
    setAppState(prev => ({
      ...prev,
      isLoading: false,
      error: error.message || '应用初始化失败'
    }));
    
    // 发送错误报告
    CrashReporter.recordError(error);
  };

  // 如果正在加载，显示加载屏幕
  if (appState.isLoading) {
    return <LoadingScreen />;
  }

  // 如果有错误，显示错误屏幕
  if (appState.error) {
    return <NetworkErrorScreen />;
  }

  // 如果没有网络连接，显示网络错误屏幕
  if (!appState.isConnected) {
    return <NetworkErrorScreen />;
  }

  // 如果需要权限，显示权限屏幕
  if (!appState.hasPermissions) {
    return <PermissionScreen onPermissionGranted={() => setAppState(prev => ({ ...prev, hasPermissions: true }))} />;
  }

  // 如果需要引导，显示引导屏幕
  if (!appState.isOnboarded) {
    return (
      <OnboardingScreen
        onComplete={() => {
          AsyncStorage.setItem('has_onboarded', 'true');
          setAppState(prev => ({ ...prev, isOnboarded: true }));
        }}
      />
    );
  }

  return (
    <ErrorBoundary>
      <GestureHandlerRootView style={styles.container}>
        <SafeAreaProvider>
          <StoreProvider store={store}>
            <PersistGate loading={<LoadingScreen />} persistor={persistor}>
              <PaperProvider theme={theme}>
                <AuthProvider>
                  <ThemeProvider>
                    <NetworkProvider>
                      <PermissionsProvider>
                        <BiometricsProvider>
                          <VoiceProvider>
                            <CameraProvider>
                              <LocationProvider>
                                <NotificationProvider>
                                  <BluetoothProvider>
                                    <SensorProvider>
                                      <AudioProvider>
                                        <VideoProvider>
                                          <ARProvider>
                                            <VRProvider>
                                              <AIProvider>
                                                <BlockchainProvider>
                                                  <QuantumProvider>
                                                    <FederatedLearningProvider>
                                                      <AnalyticsProvider>
                                                        <PerformanceProvider>
                                                          <SecurityProvider>
                                                            <NavigationContainer>
                                                              <StatusBar
                                                                barStyle={
                                                                  appState.theme === 'dark'
                                                                    ? 'light-content'
                                                                    : 'dark-content'
                                                                }
                                                                backgroundColor={
                                                                  appState.theme === 'dark'
                                                                    ? '#000000'
                                                                    : '#ffffff'
                                                                }
                                                              />
                                                              <MainNavigator />
                                                              <Toast />
                                                              {appState.showUpdate && (
                                                                <UpdateModal
                                                                  visible={appState.showUpdate}
                                                                  onClose={() =>
                                                                    setAppState(prev => ({
                                                                      ...prev,
                                                                      showUpdate: false
                                                                    }))
                                                                  }
                                                                />
                                                              )}
                                                            </NavigationContainer>
                                                          </SecurityProvider>
                                                        </PerformanceProvider>
                                                      </AnalyticsProvider>
                                                    </FederatedLearningProvider>
                                                  </QuantumProvider>
                                                </BlockchainProvider>
                                              </AIProvider>
                                            </VRProvider>
                                          </ARProvider>
                                        </VideoProvider>
                                      </AudioProvider>
                                    </SensorProvider>
                                  </BluetoothProvider>
                                </NotificationProvider>
                              </LocationProvider>
                            </CameraProvider>
                          </VoiceProvider>
                        </BiometricsProvider>
                      </PermissionsProvider>
                    </NetworkProvider>
                  </ThemeProvider>
                </AuthProvider>
              </PaperProvider>
            </PersistGate>
          </StoreProvider>
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </ErrorBoundary>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default App; 