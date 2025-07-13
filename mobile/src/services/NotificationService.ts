import AsyncStorage from '@react-native-async-storage/async-storage';
import Toast from 'react-native-toast-message';
import { Platform, PermissionsAndroid } from 'react-native';

// 通知类型
export interface NotificationData {
  id: string;
  title: string;
  message: string;
  data?: any;
  type?: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  soundName?: string;
}

class NotificationServiceClass {
  private isInitialized = false;

  // 初始化通知服务
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // 请求权限
      await this.requestPermissions();
      
      this.isInitialized = true;
      console.log('✅ 通知服务初始化完成');
      
    } catch (error) {
      console.error('❌ 通知服务初始化失败:', error);
      throw error;
    }
  }

  // 请求通知权限
  private async requestPermissions(): Promise<boolean> {
    try {
      if (Platform.OS === 'android') {
        if (Platform.Version >= 33) {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS
          );
          return granted === PermissionsAndroid.RESULTS.GRANTED;
        }
        return true;
      }
      return true;
    } catch (error) {
      console.error('请求通知权限失败:', error);
      return false;
    }
  }

  // 显示Toast通知
  showNotification(notification: NotificationData): void {
    Toast.show({
      type: notification.type || 'info',
      text1: notification.title,
      text2: notification.message,
      visibilityTime: notification.duration || 4000,
      position: 'top',
      topOffset: 50,
    });
  }

  // 显示成功通知
  showSuccess(title: string, message: string): void {
    this.showNotification({
      id: `success_${Date.now()}`,
      title,
      message,
      type: 'success',
    });
  }

  // 显示错误通知
  showError(title: string, message: string): void {
    this.showNotification({
      id: `error_${Date.now()}`,
      title,
      message,
      type: 'error',
      duration: 6000,
    });
  }

  // 显示警告通知
  showWarning(title: string, message: string): void {
    this.showNotification({
      id: `warning_${Date.now()}`,
      title,
      message,
      type: 'warning',
      duration: 5000,
    });
  }

  // 显示信息通知
  showInfo(title: string, message: string): void {
    this.showNotification({
      id: `info_${Date.now()}`,
      title,
      message,
      type: 'info',
    });
  }

  // 隐藏通知
  hideNotification(): void {
    Toast.hide();
  }

  // 保存设备令牌
  async saveDeviceToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('device_token', token);
      console.log('设备令牌已保存:', token);
    } catch (error) {
      console.error('保存设备令牌失败:', error);
    }
  }

  // 获取设备令牌
  async getDeviceToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('device_token');
    } catch (error) {
      console.error('获取设备令牌失败:', error);
      return null;
    }
  }

  // 发送思维分析完成通知
  notifyAnalysisComplete(analysisType: string): void {
    this.showSuccess(
      '分析完成',
      `${analysisType}思维分析已完成，点击查看结果`
    );
  }

  // 发送协作邀请通知
  notifyCollaborationInvite(userName: string, sessionId: string): void {
    this.showInfo(
      '协作邀请',
      `${userName} 邀请您加入思维协作会话`
    );
  }

  // 发送数据同步完成通知
  notifyDataSyncComplete(): void {
    this.showSuccess(
      '数据同步完成',
      '您的思维数据已成功同步到云端'
    );
  }

  // 发送网络错误通知
  notifyNetworkError(): void {
    this.showError(
      '网络连接失败',
      '请检查您的网络连接并重试'
    );
  }

  // 发送权限请求通知
  notifyPermissionRequired(permission: string): void {
    this.showWarning(
      '需要权限',
      `应用需要${permission}权限才能正常工作`
    );
  }

  // 发送功能开发中通知
  notifyFeatureInDevelopment(feature: string): void {
    this.showInfo(
      '功能开发中',
      `${feature}功能正在开发中，敬请期待！`
    );
  }
}

// 导出单例实例
export const NotificationService = new NotificationServiceClass(); 