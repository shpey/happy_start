import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Keychain from 'react-native-keychain';

// 安全配置接口
interface SecurityConfig {
  enableBiometrics: boolean;
  requirePinOnStartup: boolean;
  autoLockTimeout: number; // 分钟
  encryptLocalData: boolean;
  allowScreenshots: boolean;
}

// 安全状态接口
interface SecurityState {
  isSecured: boolean;
  biometricsAvailable: boolean;
  biometricsEnabled: boolean;
  appLocked: boolean;
  lastActiveTime: number;
}

// 安全上下文接口
interface SecurityContextType {
  config: SecurityConfig;
  state: SecurityState;
  updateConfig: (newConfig: Partial<SecurityConfig>) => Promise<void>;
  enableBiometrics: () => Promise<boolean>;
  disableBiometrics: () => Promise<void>;
  lockApp: () => void;
  unlockApp: () => void;
  authenticateWithBiometrics: () => Promise<boolean>;
  checkAutoLock: () => void;
  encryptData: (data: string) => Promise<string>;
  decryptData: (encryptedData: string) => Promise<string>;
}

// 创建上下文
const SecurityContext = createContext<SecurityContextType | undefined>(undefined);

// Provider 属性接口
interface SecurityProviderProps {
  children: ReactNode;
}

// SecurityProvider 组件
export const SecurityProvider: React.FC<SecurityProviderProps> = ({ children }) => {
  const [config, setConfig] = useState<SecurityConfig>({
    enableBiometrics: false,
    requirePinOnStartup: false,
    autoLockTimeout: 5,
    encryptLocalData: true,
    allowScreenshots: false,
  });

  const [state, setState] = useState<SecurityState>({
    isSecured: false,
    biometricsAvailable: false,
    biometricsEnabled: false,
    appLocked: false,
    lastActiveTime: Date.now(),
  });

  // 初始化安全设置
  useEffect(() => {
    initializeSecurity();
  }, []);

  // 初始化安全配置
  const initializeSecurity = async () => {
    try {
      // 加载保存的配置
      const savedConfig = await AsyncStorage.getItem('security_config');
      if (savedConfig) {
        setConfig(JSON.parse(savedConfig));
      }

      // 检查生物识别可用性
      const biometricsAvailable = await checkBiometricsAvailability();
      
      setState(prev => ({
        ...prev,
        biometricsAvailable,
        isSecured: true,
      }));

      console.log('✅ 安全服务初始化完成');
    } catch (error) {
      console.error('❌ 安全服务初始化失败:', error);
    }
  };

  // 检查生物识别可用性
  const checkBiometricsAvailability = async (): Promise<boolean> => {
    try {
      const biometryType = await Keychain.getSupportedBiometryType();
      return biometryType !== null;
    } catch (error) {
      console.error('检查生物识别失败:', error);
      return false;
    }
  };

  // 更新安全配置
  const updateConfig = async (newConfig: Partial<SecurityConfig>) => {
    try {
      const updatedConfig = { ...config, ...newConfig };
      setConfig(updatedConfig);
      await AsyncStorage.setItem('security_config', JSON.stringify(updatedConfig));
    } catch (error) {
      console.error('更新安全配置失败:', error);
    }
  };

  // 启用生物识别
  const enableBiometrics = async (): Promise<boolean> => {
    try {
      if (!state.biometricsAvailable) {
        return false;
      }

      // 验证生物识别
      const credentials = await Keychain.setInternetCredentials(
        'biometrics_test',
        'test',
        'test',
        { accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY }
      );

      if (credentials) {
        await updateConfig({ enableBiometrics: true });
        setState(prev => ({ ...prev, biometricsEnabled: true }));
        return true;
      }

      return false;
    } catch (error) {
      console.error('启用生物识别失败:', error);
      return false;
    }
  };

  // 禁用生物识别
  const disableBiometrics = async () => {
    try {
      await Keychain.resetInternetCredentials('biometrics_test');
      await updateConfig({ enableBiometrics: false });
      setState(prev => ({ ...prev, biometricsEnabled: false }));
    } catch (error) {
      console.error('禁用生物识别失败:', error);
    }
  };

  // 锁定应用
  const lockApp = () => {
    setState(prev => ({ ...prev, appLocked: true }));
  };

  // 解锁应用
  const unlockApp = () => {
    setState(prev => ({ 
      ...prev, 
      appLocked: false, 
      lastActiveTime: Date.now() 
    }));
  };

  // 使用生物识别验证
  const authenticateWithBiometrics = async (): Promise<boolean> => {
    try {
      if (!config.enableBiometrics || !state.biometricsAvailable) {
        return false;
      }

      const credentials = await Keychain.getInternetCredentials('biometrics_test');
      return !!credentials;
    } catch (error) {
      console.error('生物识别验证失败:', error);
      return false;
    }
  };

  // 检查自动锁定
  const checkAutoLock = () => {
    if (config.autoLockTimeout > 0) {
      const timeSinceLastActive = Date.now() - state.lastActiveTime;
      const lockTimeoutMs = config.autoLockTimeout * 60 * 1000;
      
      if (timeSinceLastActive > lockTimeoutMs && !state.appLocked) {
        lockApp();
      }
    }
  };

  // 加密数据 (简化实现)
  const encryptData = async (data: string): Promise<string> => {
    try {
      if (!config.encryptLocalData) {
        return data;
      }
      
      // 简化的加密实现，实际应用中应使用更强的加密
      const encoded = Buffer.from(data, 'utf8').toString('base64');
      return `encrypted_${encoded}`;
    } catch (error) {
      console.error('数据加密失败:', error);
      return data;
    }
  };

  // 解密数据 (简化实现)
  const decryptData = async (encryptedData: string): Promise<string> => {
    try {
      if (!config.encryptLocalData || !encryptedData.startsWith('encrypted_')) {
        return encryptedData;
      }
      
      const encoded = encryptedData.replace('encrypted_', '');
      return Buffer.from(encoded, 'base64').toString('utf8');
    } catch (error) {
      console.error('数据解密失败:', error);
      return encryptedData;
    }
  };

  // 定期检查自动锁定
  useEffect(() => {
    const interval = setInterval(checkAutoLock, 30000); // 每30秒检查一次
    return () => clearInterval(interval);
  }, [config.autoLockTimeout, state.lastActiveTime, state.appLocked]);

  const value: SecurityContextType = {
    config,
    state,
    updateConfig,
    enableBiometrics,
    disableBiometrics,
    lockApp,
    unlockApp,
    authenticateWithBiometrics,
    checkAutoLock,
    encryptData,
    decryptData,
  };

  return (
    <SecurityContext.Provider value={value}>
      {children}
    </SecurityContext.Provider>
  );
};

// Hook for using security context
export const useSecurity = (): SecurityContextType => {
  const context = useContext(SecurityContext);
  if (context === undefined) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
}; 