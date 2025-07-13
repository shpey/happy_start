/**
 * 增强的通知显示组件
 * 支持多种通知类型、优先级和交互功能
 */

import React, { useState } from 'react';
import {
  Box,
  Snackbar,
  Alert,
  AlertTitle,
  Slide,
  SlideProps,
  IconButton,
  Badge,
  Fab,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Typography,
  Chip,
  Button,
  Divider,
  Switch,
  FormControlLabel,
  Tooltip,
  Avatar
} from '@mui/material';
import {
  Close,
  Notifications,
  NotificationsActive,
  NotificationsOff,
  Settings,
  Clear,
  CheckCircle,
  Error,
  Warning,
  Info,
  Group,
  Computer,
  VolumeUp,
  VolumeOff,
  Wifi,
  WifiOff
} from '@mui/icons-material';
import { useNotification, Notification, NotificationType } from '../../contexts/NotificationContext';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// 滑动过渡组件
function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

// 通知类型图标映射
const notificationIcons: Record<NotificationType, React.ReactElement> = {
  success: <CheckCircle />,
  error: <Error />,
  warning: <Warning />,
  info: <Info />,
  collaboration: <Group />,
  system: <Computer />
};

// 通知优先级颜色映射
const priorityColors = {
  low: 'default',
  normal: 'primary',
  high: 'warning',
  urgent: 'error'
} as const;

interface NotificationDisplayProps {
  maxDisplayCount?: number;
}

export const NotificationDisplay: React.FC<NotificationDisplayProps> = ({
  maxDisplayCount = 5
}) => {
  const {
    notifications,
    unreadCount,
    settings,
    hideNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    clearByType,
    updateSettings,
    requestBrowserPermission,
    browserPermissionGranted,
    isWebSocketConnected,
    connectWebSocket,
    disconnectWebSocket
  } = useNotification();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // 获取显示的通知（最新的几个）
  const displayNotifications = notifications
    .filter(n => !n.read)
    .slice(0, maxDisplayCount);

  // 处理通知点击
  const handleNotificationClick = (notification: Notification) => {
    markAsRead(notification.id);
    
    // 如果有特殊数据处理
    if (notification.type === 'collaboration' && notification.data?.sessionId) {
      // 跳转到协作页面
      window.location.href = `/collaboration?session=${notification.data.sessionId}`;
    }
  };

  // 获取时间显示
  const getTimeDisplay = (timestamp: Date) => {
    return formatDistanceToNow(timestamp, { 
      addSuffix: true, 
      locale: zhCN 
    });
  };

  // 通知设置项
  const settingsItems = [
    {
      key: 'enableWebSocketNotifications',
      label: 'WebSocket实时通知',
      icon: isWebSocketConnected ? <Wifi /> : <WifiOff />
    },
    {
      key: 'enableBrowserNotifications',
      label: '浏览器通知',
      icon: <NotificationsActive />
    },
    {
      key: 'enableSoundNotifications',
      label: '声音通知',
      icon: settings.enableSoundNotifications ? <VolumeUp /> : <VolumeOff />
    },
    {
      key: 'enableCollaborationNotifications',
      label: '协作通知',
      icon: <Group />
    },
    {
      key: 'enableSystemNotifications',
      label: '系统通知',
      icon: <Computer />
    }
  ];

  return (
    <>
      {/* 浮动通知显示 */}
      <Box sx={{ position: 'fixed', top: 88, right: 24, zIndex: 9999 }}>
        {displayNotifications.map((notification, index) => (
          <Snackbar
            key={notification.id}
            open={true}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            TransitionComponent={SlideTransition}
            sx={{
              position: 'static',
              mb: index > 0 ? 1 : 0,
              transform: 'none !important'
            }}
          >
            <Alert
              severity={notification.type === 'collaboration' ? 'info' : 
                       notification.type === 'system' ? 'info' : notification.type}
              variant="filled"
              sx={{ 
                minWidth: 320,
                maxWidth: 400,
                boxShadow: 3,
                cursor: notification.data ? 'pointer' : 'default'
              }}
              onClick={() => handleNotificationClick(notification)}
              action={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    size="small"
                    label={notification.priority}
                    color={priorityColors[notification.priority]}
                    variant="outlined"
                    sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
                  />
                  <IconButton
                    size="small"
                    color="inherit"
                    onClick={(e) => {
                      e.stopPropagation();
                      hideNotification(notification.id);
                    }}
                  >
                    <Close fontSize="small" />
                  </IconButton>
                </Box>
              }
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                {notificationIcons[notification.type]}
                <Box sx={{ flexGrow: 1 }}>
                  {notification.title && (
                    <AlertTitle>{notification.title}</AlertTitle>
                  )}
                  {notification.message}
                  <Typography variant="caption" sx={{ display: 'block', mt: 0.5, opacity: 0.8 }}>
                    {getTimeDisplay(notification.timestamp)}
                    {notification.source === 'websocket' && ' • 实时'}
                  </Typography>
                </Box>
              </Box>
            </Alert>
          </Snackbar>
        ))}
      </Box>

      {/* 通知中心按钮 */}
      <Fab
        size="medium"
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1200
        }}
        onClick={() => setDrawerOpen(true)}
      >
        <Badge badgeContent={unreadCount} color="error" max={99}>
          {unreadCount > 0 ? <NotificationsActive /> : <Notifications />}
        </Badge>
      </Fab>

      {/* 通知中心抽屉 */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: { width: 400 }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              通知中心 ({unreadCount})
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="设置">
                <IconButton onClick={() => setSettingsOpen(!settingsOpen)}>
                  <Settings />
                </IconButton>
              </Tooltip>
              <Tooltip title="全部已读">
                <IconButton onClick={markAllAsRead} disabled={unreadCount === 0}>
                  <CheckCircle />
                </IconButton>
              </Tooltip>
              <Tooltip title="清空所有">
                <IconButton onClick={clearAll} disabled={notifications.length === 0}>
                  <Clear />
                </IconButton>
              </Tooltip>
              <IconButton onClick={() => setDrawerOpen(false)}>
                <Close />
              </IconButton>
            </Box>
          </Box>

          {/* WebSocket连接状态 */}
          <Box sx={{ mb: 2 }}>
            <Chip
              icon={isWebSocketConnected ? <Wifi /> : <WifiOff />}
              label={isWebSocketConnected ? '实时连接已建立' : '实时连接断开'}
              color={isWebSocketConnected ? 'success' : 'error'}
              variant="outlined"
              size="small"
              onClick={isWebSocketConnected ? disconnectWebSocket : connectWebSocket}
            />
          </Box>

          {/* 设置面板 */}
          {settingsOpen && (
            <>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  通知设置
                </Typography>
                {settingsItems.map((item) => (
                  <FormControlLabel
                    key={item.key}
                    control={
                      <Switch
                        checked={settings[item.key as keyof typeof settings] as boolean}
                        onChange={(e) => updateSettings({ [item.key]: e.target.checked })}
                        size="small"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {item.icon}
                        <Typography variant="body2">{item.label}</Typography>
                      </Box>
                    }
                  />
                ))}
                
                {!browserPermissionGranted && settings.enableBrowserNotifications && (
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={requestBrowserPermission}
                    sx={{ mt: 1 }}
                  >
                    请求浏览器通知权限
                  </Button>
                )}
              </Box>
              <Divider />
            </>
          )}

          {/* 通知列表 */}
          <List dense>
            {notifications.length === 0 ? (
              <ListItem>
                <ListItemText
                  primary="暂无通知"
                  secondary="您的所有通知都会在这里显示"
                />
              </ListItem>
            ) : (
              notifications.map((notification) => (
                <ListItem
                  key={notification.id}
                  button
                  onClick={() => handleNotificationClick(notification)}
                  sx={{
                    bgcolor: notification.read ? 'transparent' : 'action.hover',
                    borderRadius: 1,
                    mb: 0.5
                  }}
                >
                  <ListItemIcon>
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        bgcolor: `${notification.type}.main`
                      }}
                    >
                      {notificationIcons[notification.type]}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography
                          variant="body2"
                          fontWeight={notification.read ? 'normal' : 'bold'}
                        >
                          {notification.title || notification.message}
                        </Typography>
                        <Chip
                          size="small"
                          label={notification.type}
                          color={priorityColors[notification.priority]}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        {notification.title && (
                          <Typography variant="body2" sx={{ mb: 0.5 }}>
                            {notification.message}
                          </Typography>
                        )}
                        <Typography variant="caption" color="text.secondary">
                          {getTimeDisplay(notification.timestamp)}
                          {notification.source === 'websocket' && ' • 实时'}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        hideNotification(notification.id);
                      }}
                    >
                      <Close fontSize="small" />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))
            )}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default NotificationDisplay; 