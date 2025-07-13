import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  Tooltip,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  useTheme,
  useMediaQuery,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Psychology,
  Menu as MenuIcon,
  AccountCircle,
  Settings,
  Logout,
  Login,
  PersonAdd,
  Home,
  AccountTree,
  Groups,
  ViewInAr,
  Dashboard,
  Notifications,
  Help,
  DarkMode,
  LightMode
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import ResponsiveNavigation from './common/ResponsiveNavigation';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, isLoggedIn, logout } = useAuth();
  
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const navigationItems = [
    { path: '/', label: '首页', icon: <Home /> },
    { path: '/thinking', label: '思维分析', icon: <Psychology /> },
    { path: '/knowledge', label: '知识图谱', icon: <AccountTree /> },
    { path: '/collaboration', label: '协作空间', icon: <Groups /> },
    { path: '/3d-space', label: '3D空间', icon: <ViewInAr /> },
    ...(isLoggedIn ? [{ path: '/dashboard', label: '控制面板', icon: <Dashboard /> }] : [])
  ];

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = async () => {
    try {
      logout();
      setNotification({
        open: true,
        message: '已成功退出登录',
        severity: 'success'
      });
      navigate('/');
    } catch (error) {
      setNotification({
        open: true,
        message: '退出登录失败',
        severity: 'error'
      });
    }
    handleUserMenuClose();
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  const toggleTheme = () => {
    setDarkMode(!darkMode);
    // 这里可以添加主题切换逻辑
  };

  const renderUserSection = () => {
    if (isLoggedIn && user) {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="通知">
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>
          
          <Tooltip title="用户菜单">
            <IconButton onClick={handleUserMenuOpen} color="inherit">
              <Avatar
                src={user.avatar_url}
                alt={user.username}
                sx={{ width: 32, height: 32 }}
              >
                {user.username.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
          </Tooltip>
          
          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={handleUserMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={() => { handleUserMenuClose(); navigate('/profile'); }}>
              <ListItemIcon>
                <AccountCircle />
              </ListItemIcon>
              <ListItemText>
                <Typography variant="body2">{user.full_name || user.username}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {user.email}
                </Typography>
              </ListItemText>
            </MenuItem>
            
            <Divider />
            
            <MenuItem onClick={() => { handleUserMenuClose(); navigate('/settings'); }}>
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText>设置</ListItemText>
            </MenuItem>
            
            <MenuItem onClick={toggleTheme}>
              <ListItemIcon>
                {darkMode ? <LightMode /> : <DarkMode />}
              </ListItemIcon>
              <ListItemText>
                {darkMode ? '浅色模式' : '深色模式'}
              </ListItemText>
            </MenuItem>
            
            <MenuItem onClick={() => { handleUserMenuClose(); navigate('/help'); }}>
              <ListItemIcon>
                <Help />
              </ListItemIcon>
              <ListItemText>帮助</ListItemText>
            </MenuItem>
            
            <Divider />
            
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout />
              </ListItemIcon>
              <ListItemText>退出登录</ListItemText>
            </MenuItem>
          </Menu>
        </Box>
      );
    }

    return (
      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          color="inherit"
          startIcon={<Login />}
          onClick={() => navigate('/login')}
          sx={{ textTransform: 'none' }}
        >
          登录
        </Button>
        <Button
          variant="outlined"
          startIcon={<PersonAdd />}
          onClick={() => navigate('/register')}
          sx={{
            textTransform: 'none',
            borderColor: 'rgba(255, 255, 255, 0.5)',
            color: 'white',
            '&:hover': {
              borderColor: 'white',
              backgroundColor: 'rgba(255, 255, 255, 0.1)'
            }
          }}
        >
          注册
        </Button>
      </Box>
    );
  };

  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      <Typography variant="h6" sx={{ my: 2 }}>
        智能思维分析
      </Typography>
      <Divider />
      <List>
        {navigationItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* 响应式导航组件 */}
      <ResponsiveNavigation
        open={drawerOpen}
        onToggle={handleDrawerToggle}
        variant={isMobile ? 'temporary' : 'persistent'}
      />

      {/* 主要内容区域 */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.default',
          minHeight: '100vh',
          marginLeft: !isMobile && drawerOpen ? 0 : 0,
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        {/* 顶部应用栏 */}
        <AppBar
          position="sticky"
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            zIndex: theme.zIndex.drawer - 1,
          }}
        >
          <Toolbar>
            {/* 移动端菜单按钮 */}
            <IconButton
              color="inherit"
              aria-label="toggle drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ 
                mr: 2,
                ...(isMobile ? {} : { display: 'none' })
              }}
            >
              <MenuIcon />
            </IconButton>

            {/* Logo 和标题 */}
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
              <Psychology sx={{ mr: 1 }} />
              <Typography
                variant="h6"
                component="div"
                sx={{ 
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
                onClick={() => navigate('/')}
              >
                智能思维分析
              </Typography>
            </Box>

            {/* 搜索框 - 桌面端 */}
            {!isMobile && (
              <Box sx={{ flexGrow: 1, mx: 3, maxWidth: 400 }}>
                {/* 这里可以添加搜索功能 */}
              </Box>
            )}

            {/* 右侧工具栏 */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {/* 通知按钮 */}
              <Tooltip title="通知">
                <IconButton color="inherit">
                  <Badge badgeContent={3} color="error">
                    <Notifications />
                  </Badge>
                </IconButton>
              </Tooltip>

              {/* 主题切换 */}
              <Tooltip title="切换主题">
                <IconButton color="inherit" onClick={toggleTheme}>
                  <LightMode />
                </IconButton>
              </Tooltip>

              {/* 用户区域 */}
              {renderUserSection()}
            </Box>
          </Toolbar>
        </AppBar>

        {/* 页面内容 */}
        <Box
          sx={{
            flexGrow: 1,
            p: { xs: 1, sm: 2, md: 3 },
            overflow: 'auto',
            mb: isMobile ? 8 : 0, // 为移动端底部导航栏留空间
          }}
        >
          {children}
        </Box>
      </Box>

      {/* 通知系统 */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setNotification({ ...notification, open: false })}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Layout; 