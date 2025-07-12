import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Divider,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  useTheme,
  useMediaQuery,
  Collapse
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home,
  Psychology,
  AccountTree,
  Groups,
  ViewInAr,
  Settings,
  Notifications,
  AccountCircle,
  Dashboard,
  Analytics,
  Science,
  Lightbulb,
  Share,
  CloudUpload,
  ExpandLess,
  ExpandMore,
  ChevronLeft,
  ChevronRight,
  Brightness4,
  Brightness7,
  Search
} from '@mui/icons-material';
import { useLocalStorage, STORAGE_KEYS } from '../hooks/useLocalStorage';
import { useNotification } from '../components/common/NotificationProvider';
import ThemeSwitcher from '../components/common/ThemeSwitcher';
import GlobalSearch from '../components/common/GlobalSearch';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { info } = useNotification();
  
  // 持久化侧边栏状态
  const [drawerOpen, setDrawerOpen] = useLocalStorage(
    STORAGE_KEYS.SIDEBAR_COLLAPSED, 
    !isMobile
  );
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedMenus, setExpandedMenus] = useState<string[]>([]);
  const [minimized, setMinimized] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const drawerWidth = minimized ? 64 : 280;

  // 导航菜单项
  const menuItems = [
    {
      path: '/',
      label: '首页',
      icon: <Home />,
      description: '项目概览和快速入口'
    },
    {
      path: '/thinking',
      label: '思维分析',
      icon: <Psychology />,
      description: 'AI驱动的思维模式分析',
      badge: 'AI',
      badgeColor: 'primary'
    },
    {
      path: '/knowledge',
      label: '知识图谱',
      icon: <AccountTree />,
      description: '可视化知识关联网络',
      badge: 'NEW',
      badgeColor: 'success'
    },
    {
      path: '/collaboration',
      label: '实时协作',
      icon: <Groups />,
      description: '多用户协作思维空间',
      badge: 'LIVE',
      badgeColor: 'error'
    },
    {
      path: '/3d-space',
      label: '3D思维空间',
      icon: <ViewInAr />,
      description: '沉浸式三维思维体验',
      badge: 'XR',
      badgeColor: 'warning'
    }
  ];

  const quickMenuItems = [
    { icon: <Dashboard />, label: '数据仪表板', path: '/dashboard' },
    { icon: <Science />, label: 'AI模型配置', path: '/models' },
    { icon: <CloudUpload />, label: '云端同步', path: '/sync' },
    { icon: <Settings />, label: '系统设置', path: '/settings' }
  ];

  useEffect(() => {
    if (isMobile) {
      setDrawerOpen(false);
    }
  }, [isMobile, setDrawerOpen]);

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K 打开搜索
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleMenuClick = (path: string) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const toggleMinimize = () => {
    setMinimized(!minimized);
  };

  const toggleSubmenu = (menuId: string) => {
    setExpandedMenus(prev => 
      prev.includes(menuId) 
        ? prev.filter(id => id !== menuId)
        : [...prev, menuId]
    );
  };

  // 侧边栏内容
  const drawerContent = (
    <Box sx={{ width: drawerWidth, height: '100%', bgcolor: 'background.paper', transition: 'width 0.3s' }}>
      {/* Logo区域 */}
      <Box sx={{ p: minimized ? 1 : 2, display: 'flex', alignItems: 'center', gap: 2, justifyContent: minimized ? 'center' : 'flex-start' }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            bgcolor: 'primary.main',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '18px'
          }}
        >
          🧠
        </Box>
        {!minimized && (
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 'bold', lineHeight: 1.2 }}>
              智能思维
            </Typography>
            <Typography variant="caption" color="text.secondary">
              v2.0 Beta
            </Typography>
          </Box>
        )}
        
        {/* 最小化按钮 */}
        {!isMobile && (
          <IconButton 
            size="small" 
            onClick={toggleMinimize}
            sx={{ ml: 'auto' }}
          >
            {minimized ? <ChevronRight /> : <ChevronLeft />}
          </IconButton>
        )}
      </Box>

      <Divider />

      {/* 导航菜单 */}
      <List sx={{ px: minimized ? 0.5 : 1, py: 1 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <Tooltip title={minimized ? item.label : ''} placement="right">
                <ListItemButton
                  onClick={() => handleMenuClick(item.path)}
                  sx={{
                    borderRadius: 2,
                    minHeight: 48,
                    bgcolor: isActive ? 'primary.main' : 'transparent',
                    color: isActive ? 'primary.contrastText' : 'text.primary',
                    justifyContent: minimized ? 'center' : 'flex-start',
                    px: minimized ? 1 : 2,
                    '&:hover': {
                      bgcolor: isActive ? 'primary.dark' : 'action.hover'
                    }
                  }}
                >
                  <ListItemIcon sx={{ 
                    color: isActive ? 'primary.contrastText' : 'action.active',
                    minWidth: minimized ? 'auto' : 40,
                    justifyContent: 'center'
                  }}>
                    {item.icon}
                  </ListItemIcon>
                  {!minimized && (
                    <>
                      <ListItemText 
                        primary={item.label}
                        secondary={!isActive ? item.description : undefined}
                        primaryTypographyProps={{
                          fontSize: '14px',
                          fontWeight: isActive ? 600 : 500
                        }}
                        secondaryTypographyProps={{
                          fontSize: '12px',
                          color: 'text.secondary'
                        }}
                      />
                      {item.badge && (
                        <Chip
                          label={item.badge}
                          size="small"
                          sx={{
                            height: 20,
                            fontSize: '10px',
                            bgcolor: isActive ? 'rgba(255,255,255,0.2)' : `${item.badgeColor}.main`,
                            color: isActive ? 'white' : 'white'
                          }}
                        />
                      )}
                    </>
                  )}
                </ListItemButton>
              </Tooltip>
            </ListItem>
          );
        })}
      </List>

      {!minimized && (
        <>
          <Divider sx={{ mx: 2, my: 1 }} />

          {/* 快捷功能 */}
          <List sx={{ px: 1 }}>
            <ListItem>
              <Typography variant="overline" color="text.secondary" sx={{ fontSize: '11px' }}>
                快捷功能
              </Typography>
            </ListItem>
            
            {quickMenuItems.map((item, index) => (
              <ListItem key={index} disablePadding sx={{ mb: 0.5 }}>
                <Tooltip title={item.label} placement="right">
                  <ListItemButton
                    sx={{ borderRadius: 1, minHeight: 36 }}
                    onClick={() => {
                      if (item.path.includes('/models') || item.path.includes('/sync') || item.path.includes('/settings')) {
                        info(`${item.label}功能开发中...`);
                      } else {
                        handleMenuClick(item.path);
                      }
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 32, color: 'action.active' }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.label}
                      primaryTypographyProps={{ fontSize: '13px' }}
                    />
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            ))}
          </List>

          {/* 底部状态 */}
          <Box sx={{ position: 'absolute', bottom: 16, left: 16, right: 16 }}>
            <Box
              sx={{
                p: 2,
                bgcolor: 'success.main',
                color: 'success.contrastText',
                borderRadius: 2,
                textAlign: 'center'
              }}
            >
              <Typography variant="caption" sx={{ display: 'block', fontWeight: 600 }}>
                🚀 系统运行正常
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                AI模型：已连接 | 协作：3人在线
              </Typography>
            </Box>
          </Box>
        </>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* 顶部应用栏 */}
      <AppBar 
        position="fixed" 
        sx={{ 
          width: { md: `calc(100% - ${drawerOpen ? drawerWidth : 0}px)` },
          ml: { md: drawerOpen ? `${drawerWidth}px` : 0 },
          bgcolor: 'background.paper',
          color: 'text.primary',
          boxShadow: 1,
          borderBottom: 1,
          borderColor: 'divider',
          transition: 'width 0.3s, margin 0.3s'
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 500 }}>
            {menuItems.find(item => item.path === location.pathname)?.label || '智能思维平台'}
          </Typography>

          {/* 顶部右侧功能区 */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* 全局搜索 */}
            <Tooltip title="全局搜索 (Ctrl+K)">
              <IconButton color="inherit" onClick={() => setSearchOpen(true)}>
                <Search />
              </IconButton>
            </Tooltip>

            <Tooltip title="通知">
              <IconButton color="inherit">
                <Badge badgeContent={3} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>

            <Tooltip title="AI助手">
              <IconButton color="inherit" onClick={() => info('AI助手功能开发中...')}>
                <Lightbulb sx={{ color: 'warning.main' }} />
              </IconButton>
            </Tooltip>

            <Tooltip title="分享">
              <IconButton color="inherit" onClick={() => info('分享功能开发中...')}>
                <Share />
              </IconButton>
            </Tooltip>

            {/* 主题切换器 */}
            <ThemeSwitcher variant="icon" />

            <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />

            {/* 用户菜单 */}
            <IconButton
              color="inherit"
              onClick={handleProfileMenuOpen}
              sx={{ p: 0 }}
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                U
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* 侧边栏 */}
      <Box
        component="nav"
        sx={{ width: { md: drawerOpen ? drawerWidth : 0 }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? "temporary" : "persistent"}
          open={drawerOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: 1,
              borderColor: 'divider',
              bgcolor: 'background.default',
              transition: 'width 0.3s'
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* 主内容区域 */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerOpen ? drawerWidth : 0}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default',
          transition: 'width 0.3s'
        }}
      >
        <Toolbar />
        <Container maxWidth={false} sx={{ py: 3, px: 3 }}>
          {children}
        </Container>
      </Box>

      {/* 用户菜单 */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        PaperProps={{
          sx: { width: 200, mt: 1 }
        }}
      >
        <MenuItem onClick={handleProfileMenuClose}>
          <AccountCircle sx={{ mr: 2 }} />
          个人资料
        </MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>
          <Settings sx={{ mr: 2 }} />
          账户设置
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          handleProfileMenuClose();
          info('退出登录功能开发中...');
        }}>
          退出登录
        </MenuItem>
      </Menu>

      {/* 全局搜索对话框 */}
      <GlobalSearch 
        open={searchOpen} 
        onClose={() => setSearchOpen(false)} 
      />
    </Box>
  );
};

export default Layout; 