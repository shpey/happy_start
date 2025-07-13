import React, { ReactNode } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';

// 基础组件属性接口
interface ComponentProps {
  children?: ReactNode;
  onComplete?: () => void;
  onClose?: () => void;
  visible?: boolean;
  onPermissionGranted?: () => void;
}

// 错误边界组件
export class ErrorBoundary extends React.Component<
  { children: ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>出现错误</Text>
          <Text style={styles.errorMessage}>
            {this.state.error?.message || '应用发生了未知错误'}
          </Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => this.setState({ hasError: false, error: undefined })}
          >
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}

// 加载屏幕组件
export const LoadingScreen: React.FC = () => {
  return (
    <View style={styles.loadingContainer}>
      <ActivityIndicator size="large" color="#6200ea" />
      <Text style={styles.loadingText}>正在加载智能思维应用...</Text>
    </View>
  );
};

// 更新模态框组件
export const UpdateModal: React.FC<ComponentProps> = ({ visible, onClose }) => {
  if (!visible) return null;

  return (
    <View style={styles.modalContainer}>
      <View style={styles.modalContent}>
        <Text style={styles.modalTitle}>发现新版本</Text>
        <Text style={styles.modalMessage}>
          新版本包含性能优化和bug修复，建议立即更新。
        </Text>
        <View style={styles.modalButtons}>
          <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
            <Text style={styles.cancelButtonText}>稍后</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.updateButton} onPress={onClose}>
            <Text style={styles.updateButtonText}>立即更新</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

// 引导屏幕组件
export const OnboardingScreen: React.FC<ComponentProps> = ({ onComplete }) => {
  return (
    <View style={styles.onboardingContainer}>
      <Text style={styles.onboardingTitle}>欢迎使用智能思维</Text>
      <Text style={styles.onboardingSubtitle}>
        AI驱动的3D思维空间与协作平台
      </Text>
      <TouchableOpacity style={styles.continueButton} onPress={onComplete}>
        <Text style={styles.continueButtonText}>开始体验</Text>
      </TouchableOpacity>
    </View>
  );
};

// 权限屏幕组件
export const PermissionScreen: React.FC<ComponentProps> = ({ onPermissionGranted }) => {
  return (
    <View style={styles.permissionContainer}>
      <Text style={styles.permissionTitle}>需要授权</Text>
      <Text style={styles.permissionMessage}>
        为了提供更好的体验，我们需要以下权限：
      </Text>
      <Text style={styles.permissionList}>
        • 相机权限 - 用于AR功能{'\n'}
        • 麦克风权限 - 用于语音交互{'\n'}
        • 位置权限 - 用于协作功能{'\n'}
        • 存储权限 - 用于数据缓存
      </Text>
      <TouchableOpacity style={styles.grantButton} onPress={onPermissionGranted}>
        <Text style={styles.grantButtonText}>授予权限</Text>
      </TouchableOpacity>
    </View>
  );
};

// 网络错误屏幕组件
export const NetworkErrorScreen: React.FC<ComponentProps> = () => {
  return (
    <View style={styles.networkErrorContainer}>
      <Text style={styles.networkErrorTitle}>网络连接失败</Text>
      <Text style={styles.networkErrorMessage}>
        请检查您的网络连接并重试
      </Text>
      <TouchableOpacity style={styles.retryButton}>
        <Text style={styles.retryButtonText}>重试</Text>
      </TouchableOpacity>
    </View>
  );
};

// 样式定义
const styles = StyleSheet.create({
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#d32f2f',
    marginBottom: 10,
  },
  errorMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingText: {
    marginTop: 20,
    fontSize: 16,
    color: '#666',
  },
  modalContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 10,
    margin: 20,
    minWidth: 300,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  modalMessage: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  cancelButton: {
    padding: 10,
    flex: 1,
    marginRight: 10,
  },
  cancelButtonText: {
    textAlign: 'center',
    color: '#666',
  },
  updateButton: {
    backgroundColor: '#6200ea',
    padding: 10,
    borderRadius: 5,
    flex: 1,
  },
  updateButtonText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  onboardingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#6200ea',
  },
  onboardingTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 10,
    textAlign: 'center',
  },
  onboardingSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 40,
    textAlign: 'center',
  },
  continueButton: {
    backgroundColor: 'white',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 25,
  },
  continueButtonText: {
    color: '#6200ea',
    fontSize: 16,
    fontWeight: 'bold',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  permissionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  permissionMessage: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
  },
  permissionList: {
    fontSize: 14,
    color: '#333',
    marginBottom: 30,
    lineHeight: 20,
  },
  grantButton: {
    backgroundColor: '#6200ea',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 25,
  },
  grantButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  networkErrorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  networkErrorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#d32f2f',
    marginBottom: 10,
  },
  networkErrorMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#6200ea',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 6,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 