/**
 * 快速访问面板
 * 提供常用功能的快捷入口和实时信息
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Badge,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import {
  Speed,
  Psychology,
  AccountTree,
  Groups,
  ViewInAr,
  Add,
  Notifications,
  History,
  Download,
  Share,
  Settings,
  Help,
  Lightbulb,
  TrendingUp,
  CloudUpload,
  Assessment,
  Close,
  ExpandLess,
  ExpandMore
} from '@mui/icons-material';
import { useNotification } from './NotificationProvider';
import { useLocalStorage, STORAGE_KEYS } from '../../hooks/useLocalStorage';

interface QuickAction {
  icon: React.ReactElement;
  name: string;
  description: string;
  action: () => void;
  badge?: number;
  color?: string;
}

const QuickAccessPanel: React.FC = () => {
  const navigate = useNavigate();
  const { info, success } = useNotification();
  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  const [panelOpen, setPanelOpen] = useState(false);
  const [recentActivities] = useLocalStorage(STORAGE_KEYS.RECENT_ACTIVITIES, []);

  // 快速操作列表
  const quickActions: QuickAction[] = [
    {
      icon: <Psychology />,
      name: '新思维分析',
      description: '快速开始AI思维分析',
      action: () => {
        navigate('/thinking');
        success('已跳转到思维分析页面');
      },
      color: '#E91E63'
    },
    {
      icon: <AccountTree />,
      name: '知识图谱',
      description: '查看知识关联网络',
      action: () => {
        navigate('/knowledge');
        success('已跳转到知识图谱页面');
      },
      color: '#2196F3'
    },
    {
      icon: <Groups />,
      name: '实时协作',
      description: '加入协作会话',
      action: () => {
        navigate('/collaboration');
        success('已跳转到实时协作页面');
      },
      badge: 3,
      color: '#FF5722'
    },
    {
      icon: <ViewInAr />,
      name: '3D空间',
      description: '进入3D思维空间',
      action: () => {
        navigate('/3d-space');
        success('已跳转到3D思维空间');
      },
      color: '#4CAF50'
    },
    {
      icon: <Assessment />,
      name: '数据仪表板',
      description: '查看系统统计',
      action: () => {
        navigate('/dashboard');
        success('已跳转到数据仪表板');
      },
      color: '#FF9800'
    },
    {
      icon: <History />,
      name: '历史记录',
      description: '查看最近活动',
      action: () => {
        setPanelOpen(!panelOpen);
      },
      color: '#9C27B0'
    }
  ];

  // 系统快捷操作
  const systemActions: QuickAction[] = [
    {
      icon: <Download />,
      name: '数据导出',
      description: '导出个人数据',
      action: () => {
        info('正在准备数据导出...');
        // 模拟导出过程
        setTimeout(() => {
          success('数据导出完成！');
        }, 2000);
      }
    },
    {
      icon: <Share />,
      name: '分享平台',
      description: '分享给朋友',
      action: () => {
        if (navigator.share) {
          navigator.share({
            title: '智能思维平台',
            text: '发现这个很棒的AI思维分析平台！',
            url: window.location.origin
          });
        } else {
          navigator.clipboard.writeText(window.location.origin);
          success('平台链接已复制到剪贴板');
        }
      }
    },
    {
      icon: <Help />,
      name: '使用帮助',
      description: '查看使用指南',
      action: () => {
        info('帮助文档功能开发中...');
      }
    },
    {
      icon: <Settings />,
      name: '系统设置',
      description: '配置个人偏好',
      action: () => {
        info('系统设置功能开发中...');
      }
    }
  ];

  return (
    <>
      {/* 速拨菜单 */}
      <SpeedDial
        ariaLabel="快速访问"
        sx={{ 
          position: 'fixed', 
          bottom: 24, 
          right: 24,
          '& .MuiFab-primary': {
            bgcolor: 'primary.main',
            '&:hover': {
              bgcolor: 'primary.dark'
            }
          }
        }}
        icon={<SpeedDialIcon icon={<Speed />} openIcon={<Close />} />}
        onClose={() => setSpeedDialOpen(false)}
        onOpen={() => setSpeedDialOpen(true)}
        open={speedDialOpen}
        direction="up"
      >
        {quickActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={
              action.badge ? (
                <Badge badgeContent={action.badge} color="error">
                  {action.icon}
                </Badge>
              ) : (
                action.icon
              )
            }
            tooltipTitle={action.description}
            tooltipOpen
            onClick={() => {
              action.action();
              setSpeedDialOpen(false);
            }}
            sx={{
              '& .MuiSpeedDialAction-fab': {
                bgcolor: action.color || 'action.active',
                color: 'white',
                '&:hover': {
                  bgcolor: action.color || 'action.active',
                  opacity: 0.8
                }
              }
            }}
          />
        ))}
      </SpeedDial>

      {/* 快速信息面板 */}
      <Paper
        sx={{
          position: 'fixed',
          bottom: 100,
          right: 24,
          width: 320,
          maxHeight: 400,
          overflow: 'hidden',
          transform: panelOpen ? 'translateX(0)' : 'translateX(350px)',
          transition: 'transform 0.3s ease-in-out',
          zIndex: 1300,
          boxShadow: 3
        }}
      >
        {/* 面板头部 */}
        <Box sx={{ 
          p: 2, 
          bgcolor: 'primary.main', 
          color: 'primary.contrastText',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Lightbulb />
            快速访问
          </Typography>
          <IconButton 
            size="small" 
            onClick={() => setPanelOpen(false)}
            sx={{ color: 'inherit' }}
          >
            <Close />
          </IconButton>
        </Box>

        {/* 系统状态 */}
        <Box sx={{ p: 2, bgcolor: 'background.default' }}>
          <Typography variant="subtitle2" gutterBottom>
            系统状态
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip label="AI在线" size="small" color="success" />
            <Chip label="协作: 3人" size="small" color="info" />
            <Chip label="负载: 正常" size="small" color="default" />
          </Box>
        </Box>

        <Divider />

        {/* 快捷操作 */}
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            快捷操作
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 1 }}>
            {systemActions.map((action, index) => (
              <Tooltip key={index} title={action.description} placement="top">
                <IconButton
                  onClick={action.action}
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 2,
                    p: 2,
                    '&:hover': {
                      bgcolor: 'action.hover'
                    }
                  }}
                >
                  {action.icon}
                </IconButton>
              </Tooltip>
            ))}
          </Box>
        </Box>

        <Divider />

        {/* 最近活动 */}
        <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
          <Box sx={{ p: 2, pb: 1 }}>
            <Typography variant="subtitle2">
              最近活动
            </Typography>
          </Box>
          
          {recentActivities.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                暂无最近活动
              </Typography>
            </Box>
          ) : (
            <List dense>
              {recentActivities.slice(0, 5).map((activity: any, index: number) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <TrendingUp fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={activity.title || '未知活动'}
                    secondary={activity.time || '刚刚'}
                    primaryTypographyProps={{ fontSize: '14px' }}
                    secondaryTypographyProps={{ fontSize: '12px' }}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* 面板底部 */}
        <Box sx={{ p: 2, bgcolor: 'background.default', textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            💡 更多功能请查看侧边栏
          </Typography>
        </Box>
      </Paper>

      {/* 通知按钮 */}
      <Fab
        size="small"
        color="secondary"
        sx={{
          position: 'fixed',
          bottom: 90,
          right: 90,
          zIndex: 1200
        }}
        onClick={() => {
          info('通知中心功能开发中...');
        }}
      >
        <Badge badgeContent={5} color="error">
          <Notifications />
        </Badge>
      </Fab>
    </>
  );
};

export default QuickAccessPanel; 