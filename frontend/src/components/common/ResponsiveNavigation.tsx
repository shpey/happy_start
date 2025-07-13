import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Avatar,
  Chip,
  Badge,
  useTheme,
  useMediaQuery,
  Tooltip,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Collapse,
  Slide,
  Zoom
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Home,
  Psychology,
  AccountTree,
  Groups,
  ViewInAr,
  Dashboard,
  ShowChart,
  Settings,
  Notifications,
  Help,
  KeyboardArrowDown,
  KeyboardArrowUp,
  Add,
  Search,
  Favorite,
  Share,
  MoreVert
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

interface NavigationItem {
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
  color?: string;
  description?: string;
  subItems?: NavigationItem[];
}

interface ResponsiveNavigationProps {
  open: boolean;
  onToggle: () => void;
  variant?: 'permanent' | 'temporary' | 'persistent';
}

const ResponsiveNavigation: React.FC<ResponsiveNavigationProps> = ({
  open,
  onToggle,
  variant = 'temporary'
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [speedDialOpen, setSpeedDialOpen] = useState(false);

  const navigationItems: NavigationItem[] = [
    {
      label: '首页',
      icon: <Home />,
      path: '/',
      color: theme.palette.primary.main,
      description: '返回主页'
    },
    {
      label: '思维分析',
      icon: <Psychology />,
      path: '/thinking',
      color: theme.palette.secondary.main,
      description: 'AI驱动的思维模式分析',
      subItems: [
        { label: '新建分析', icon: <Add />, path: '/thinking/new' },
        { label: '历史记录', icon: <Search />, path: '/thinking/history' },
        { label: '收藏分析', icon: <Favorite />, path: '/thinking/favorites' }
      ]
    },
    {
      label: '知识图谱',
      icon: <AccountTree />,
      path: '/knowledge',
      color: theme.palette.success.main,
      description: '可视化知识关联网络'
    },
    {
      label: '实时协作',
      icon: <Groups />,
      path: '/collaboration',
      badge: 3,
      color: theme.palette.warning.main,
      description: '多人协作思维空间'
    },
    {
      label: '3D思维空间',
      icon: <ViewInAr />,
      path: '/3d-space',
      color: theme.palette.error.main,
      description: '沉浸式三维思维体验'
    },
    {
      label: '仪表板',
      icon: <Dashboard />,
      path: '/dashboard',
      color: theme.palette.info.main,
      description: '数据分析与洞察'
    },
    {
      label: '高级可视化',
      icon: <ShowChart />,
      path: '/visualization',
      color: '#9C27B0',
      description: '高级图表和实时监控'
    }
  ];

  const quickActions = [
    {
      icon: <Psychology />,
      name: '快速分析',
      action: () => navigate('/thinking')
    },
    {
      icon: <Groups />,
      name: '创建协作',
      action: () => navigate('/collaboration')
    },
    {
      icon: <ViewInAr />,
      name: '3D空间',
      action: () => navigate('/3d-space')
    },
    {
      icon: <Share />,
      name: '分享',
      action: () => {/* 分享功能 */}
    }
  ];

  const handleItemClick = (item: NavigationItem) => {
    if (item.subItems) {
      toggleExpanded(item.path);
    } else {
      navigate(item.path);
      if (isMobile) {
        onToggle();
      }
    }
  };

  const toggleExpanded = (path: string) => {
    setExpandedItems(prev =>
      prev.includes(path)
        ? prev.filter(item => item !== path)
        : [...prev, path]
    );
  };

  const isActive = (path: string) => {
    return location.pathname === path || 
           (path !== '/' && location.pathname.startsWith(path));
  };

  const renderNavigationItem = (item: NavigationItem, level = 0) => {
    const active = isActive(item.path);
    const expanded = expandedItems.includes(item.path);
    const hasSubItems = item.subItems && item.subItems.length > 0;

    return (
      <React.Fragment key={item.path}>
        <ListItemButton
          onClick={() => handleItemClick(item)}
          sx={{
            pl: 2 + level * 2,
            borderRadius: 2,
            mx: 1,
            mb: 0.5,
            ...(active && {
              backgroundColor: `${item.color}15`,
              borderLeft: `4px solid ${item.color}`,
              '& .MuiListItemIcon-root': {
                color: item.color
              },
              '& .MuiListItemText-primary': {
                color: item.color,
                fontWeight: 600
              }
            }),
            '&:hover': {
              backgroundColor: `${item.color}10`,
              transform: 'translateX(4px)',
              transition: 'all 0.2s ease'
            }
          }}
        >
          <ListItemIcon
            sx={{
              minWidth: 40,
              color: active ? item.color : 'text.secondary'
            }}
          >
            <Badge
              badgeContent={item.badge}
              color="error"
              variant="dot"
              invisible={!item.badge}
            >
              {item.icon}
            </Badge>
          </ListItemIcon>
          
          <ListItemText
            primary={item.label}
            secondary={level === 0 ? item.description : undefined}
            primaryTypographyProps={{
              fontSize: level === 0 ? '0.9rem' : '0.85rem',
              fontWeight: active ? 600 : 400
            }}
            secondaryTypographyProps={{
              fontSize: '0.75rem',
              color: 'text.disabled'
            }}
          />
          
          {hasSubItems && (
            <IconButton size="small" sx={{ ml: 1 }}>
              {expanded ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
            </IconButton>
          )}
        </ListItemButton>

        {hasSubItems && (
          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <List disablePadding>
              {item.subItems?.map(subItem => renderNavigationItem(subItem, level + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const renderUserSection = () => (
    <Box sx={{ p: 2 }}>
      {user ? (
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            background: `linear-gradient(135deg, ${theme.palette.primary.main}10, ${theme.palette.secondary.main}10)`,
            border: `1px solid ${theme.palette.primary.main}20`
          }}
        >
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
              }}
            >
              {user.username?.[0]?.toUpperCase()}
            </Avatar>
            <Box flex={1}>
              <Typography variant="subtitle1" fontWeight={600}>
                {user.username}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user.email}
              </Typography>
            </Box>
          </Box>
          
          <Box display="flex" gap={1} mt={2}>
            <Chip
              label="活跃用户"
              size="small"
              color="primary"
              variant="outlined"
            />
            <Chip
              label="Lv.5"
              size="small"
              color="secondary"
              variant="outlined"
            />
          </Box>
        </Box>
      ) : (
        <Box textAlign="center" p={2}>
          <Typography variant="body2" color="text.secondary" mb={2}>
            登录以获取完整体验
          </Typography>
          <Box display="flex" gap={1}>
            <Chip
              label="登录"
              variant="outlined"
              onClick={() => navigate('/login')}
              clickable
            />
            <Chip
              label="注册"
              variant="filled"
              color="primary"
              onClick={() => navigate('/register')}
              clickable
            />
          </Box>
        </Box>
      )}
    </Box>
  );

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 头部 */}
      <Box
        sx={{
          p: 2,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          color: 'white'
        }}
      >
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
              <Psychology />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              智能思维
            </Typography>
          </Box>
          
          {isMobile && (
            <IconButton onClick={onToggle} sx={{ color: 'white' }}>
              <CloseIcon />
            </IconButton>
          )}
        </Box>
      </Box>

      {/* 用户信息 */}
      {renderUserSection()}

      <Divider />

      {/* 导航菜单 */}
      <Box sx={{ flex: 1, overflow: 'auto', py: 1 }}>
        <List>
          {navigationItems.map(item => renderNavigationItem(item))}
        </List>
      </Box>

      <Divider />

      {/* 底部工具 */}
      <Box sx={{ p: 2 }}>
        <List>
          <ListItemButton
            onClick={() => navigate('/settings')}
            sx={{ borderRadius: 2 }}
          >
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText primary="设置" />
          </ListItemButton>
          
          <ListItemButton
            onClick={() => navigate('/help')}
            sx={{ borderRadius: 2 }}
          >
            <ListItemIcon>
              <Help />
            </ListItemIcon>
            <ListItemText primary="帮助" />
          </ListItemButton>
        </List>
      </Box>
    </Box>
  );

  return (
    <>
      {/* 侧边栏抽屉 */}
      <Drawer
        variant={isMobile ? 'temporary' : variant}
        open={open}
        onClose={onToggle}
        sx={{
          width: 280,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 280,
            boxSizing: 'border-box',
            border: 'none',
            boxShadow: isMobile ? '0 8px 32px rgba(0,0,0,0.12)' : 1
          }
        }}
        ModalProps={{
          keepMounted: true // 移动端性能优化
        }}
      >
        {drawerContent}
      </Drawer>

      {/* 移动端快速操作按钮 */}
      {isMobile && (
        <SpeedDial
          ariaLabel="快速操作"
          sx={{
            position: 'fixed',
            bottom: 80,
            right: 16,
            '& .MuiSpeedDial-fab': {
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
            }
          }}
          icon={<SpeedDialIcon />}
          onClose={() => setSpeedDialOpen(false)}
          onOpen={() => setSpeedDialOpen(true)}
          open={speedDialOpen}
        >
          {quickActions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipTitle={action.name}
              onClick={() => {
                action.action();
                setSpeedDialOpen(false);
              }}
              FabProps={{
                sx: {
                  '&:hover': {
                    transform: 'scale(1.1)',
                    transition: 'transform 0.2s ease'
                  }
                }
              }}
            />
          ))}
        </SpeedDial>
      )}

      {/* 移动端底部导航栏 */}
      {isMobile && (
        <Slide direction="up" in mountOnEnter unmountOnExit>
          <Box
            sx={{
              position: 'fixed',
              bottom: 0,
              left: 0,
              right: 0,
              backgroundColor: 'background.paper',
              borderTop: `1px solid ${theme.palette.divider}`,
              zIndex: 1100,
              backdropFilter: 'blur(10px)',
              background: 'rgba(255, 255, 255, 0.95)'
            }}
          >
            <Box display="flex" justifyContent="space-around" p={1}>
              {navigationItems.slice(0, 4).map((item) => (
                <Tooltip key={item.path} title={item.label}>
                  <IconButton
                    onClick={() => navigate(item.path)}
                    sx={{
                      flexDirection: 'column',
                      borderRadius: 2,
                      p: 1,
                      minWidth: 64,
                      ...(isActive(item.path) && {
                        backgroundColor: `${item.color}15`,
                        color: item.color
                      })
                    }}
                  >
                    <Badge
                      badgeContent={item.badge}
                      color="error"
                      variant="dot"
                      invisible={!item.badge}
                    >
                      {item.icon}
                    </Badge>
                    <Typography variant="caption" fontSize="0.7rem">
                      {item.label}
                    </Typography>
                  </IconButton>
                </Tooltip>
              ))}
              
              <Tooltip title="更多">
                <IconButton
                  onClick={onToggle}
                  sx={{
                    flexDirection: 'column',
                    borderRadius: 2,
                    p: 1,
                    minWidth: 64
                  }}
                >
                  <MoreVert />
                  <Typography variant="caption" fontSize="0.7rem">
                    更多
                  </Typography>
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Slide>
      )}
    </>
  );
};

export default ResponsiveNavigation; 