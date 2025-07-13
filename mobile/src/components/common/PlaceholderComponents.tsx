import React, { ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

// 错误边界组件
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Something went wrong.</Text>
        </View>
      );
    }

    return this.props.children;
  }
}

// 加载屏幕
export const LoadingScreen: React.FC = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#6200ea" />
    <Text style={styles.loadingText}>Loading...</Text>
  </View>
);

// 更新弹窗
interface UpdateModalProps {
  visible: boolean;
  onClose: () => void;
}

export const UpdateModal: React.FC<UpdateModalProps> = ({ visible, onClose }) => {
  if (!visible) return null;
  
  return (
    <View style={styles.modalContainer}>
      <View style={styles.modalContent}>
        <Text style={styles.modalTitle}>Update Available</Text>
        <Text style={styles.modalText}>A new version is available.</Text>
        <TouchableOpacity style={styles.modalButton} onPress={onClose}>
          <Text style={styles.modalButtonText}>Close</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

// 引导屏幕
interface OnboardingScreenProps {
  onComplete: () => void;
}

export const OnboardingScreen: React.FC<OnboardingScreenProps> = ({ onComplete }) => (
  <View style={styles.onboardingContainer}>
    <Text style={styles.onboardingTitle}>Welcome to Intelligent Thinking</Text>
    <Text style={styles.onboardingText}>AI-powered 3D thinking space</Text>
    <TouchableOpacity style={styles.onboardingButton} onPress={onComplete}>
      <Text style={styles.onboardingButtonText}>Get Started</Text>
    </TouchableOpacity>
  </View>
);

// 权限屏幕
interface PermissionScreenProps {
  onPermissionGranted: () => void;
}

export const PermissionScreen: React.FC<PermissionScreenProps> = ({ onPermissionGranted }) => (
  <View style={styles.permissionContainer}>
    <Text style={styles.permissionTitle}>Permissions Required</Text>
    <Text style={styles.permissionText}>This app needs certain permissions to function properly.</Text>
    <TouchableOpacity style={styles.permissionButton} onPress={onPermissionGranted}>
      <Text style={styles.permissionButtonText}>Grant Permissions</Text>
    </TouchableOpacity>
  </View>
);

// 网络错误屏幕
export const NetworkErrorScreen: React.FC = () => (
  <View style={styles.networkErrorContainer}>
    <Text style={styles.networkErrorTitle}>No Internet Connection</Text>
    <Text style={styles.networkErrorText}>Please check your internet connection and try again.</Text>
  </View>
);

const styles = StyleSheet.create({
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  errorText: {
    fontSize: 18,
    color: '#333',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  loadingText: {
    marginTop: 20,
    fontSize: 16,
    color: '#333',
  },
  modalContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    margin: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  modalText: {
    fontSize: 14,
    marginBottom: 20,
  },
  modalButton: {
    backgroundColor: '#6200ea',
    padding: 10,
    borderRadius: 5,
    alignItems: 'center',
  },
  modalButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  onboardingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  onboardingTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  onboardingText: {
    fontSize: 16,
    marginBottom: 30,
    textAlign: 'center',
    color: '#666',
  },
  onboardingButton: {
    backgroundColor: '#6200ea',
    padding: 15,
    borderRadius: 25,
    paddingHorizontal: 30,
  },
  onboardingButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  permissionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  permissionText: {
    fontSize: 16,
    marginBottom: 30,
    textAlign: 'center',
    color: '#666',
  },
  permissionButton: {
    backgroundColor: '#6200ea',
    padding: 15,
    borderRadius: 25,
    paddingHorizontal: 30,
  },
  permissionButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  networkErrorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  networkErrorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
    color: '#ff5722',
  },
  networkErrorText: {
    fontSize: 16,
    textAlign: 'center',
    color: '#666',
  },
}); 