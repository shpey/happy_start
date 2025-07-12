import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Paper, 
  Box, 
  Grid,
  Alert,
  CircularProgress,
  Breadcrumbs,
  Link
} from '@mui/material';
import { NavigateNext, Groups, Psychology, Share } from '@mui/icons-material';
import RealtimeCollaboration, { CollaborationUser } from '../components/Collaboration/RealtimeCollaboration';

const CollaborationPage: React.FC = () => {
  const [currentUser] = useState<CollaborationUser>({
    id: 'user_' + Math.random().toString(36).substr(2, 9),
    name: '当前用户',
    status: 'online',
    role: 'host',
    avatar: undefined
  });

  const [sessionId] = useState(() => 
    new URLSearchParams(window.location.search).get('session') || 
    'session_' + Math.random().toString(36).substr(2, 9)
  );

  const [activeUsers, setActiveUsers] = useState<CollaborationUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 模拟加载过程
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  // 处理用户列表更新
  const handleUserUpdate = (users: CollaborationUser[]) => {
    setActiveUsers(users);
  };

  // 处理思维分享
  const handleThinkingShare = (data: any) => {
    console.log('Thinking shared:', data);
    // TODO: 在3D空间中显示分享的思维内容
  };

  // 处理标注添加
  const handleAnnotationAdd = (annotation: any) => {
    console.log('Annotation added:', annotation);
    // TODO: 在协作空间中显示新的标注
  };

  if (isLoading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '60vh' 
      }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          正在连接协作空间...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          会话ID: {sessionId}
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      {/* 页面头部 */}
      <Box sx={{ mb: 2 }}>
        <Breadcrumbs separator={<NavigateNext fontSize="small" />} sx={{ mb: 1 }}>
          <Link underline="hover" color="inherit" href="/">
            首页
          </Link>
          <Typography color="text.primary">实时协作</Typography>
        </Breadcrumbs>

        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Groups /> 实时协作空间
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          与团队成员实时协作，分享思维过程，共同探索创新解决方案
        </Typography>

        {/* 会话信息 */}
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            当前会话: <strong>{sessionId}</strong> | 
            在线用户: <strong>{activeUsers.length}</strong> | 
            您的角色: <strong>{currentUser.role === 'host' ? '主持人' : currentUser.role === 'participant' ? '参与者' : '观察者'}</strong>
          </Typography>
        </Alert>
      </Box>

      {/* 协作功能区域 */}
      <Grid container spacing={3} sx={{ flexGrow: 1 }}>
        {/* 主要协作区域 */}
        <Grid item xs={12}>
          <RealtimeCollaboration
            sessionId={sessionId}
            currentUser={currentUser}
            onUserUpdate={handleUserUpdate}
            onThinkingShare={handleThinkingShare}
            onAnnotationAdd={handleAnnotationAdd}
          />
        </Grid>
      </Grid>

      {/* 底部功能提示 */}
      <Paper sx={{ mt: 2, p: 2, bgcolor: 'background.default' }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Psychology color="primary" />
              <Box>
                <Typography variant="subtitle2">实时思维分享</Typography>
                <Typography variant="caption" color="text.secondary">
                  即时分享您的思考过程和创意想法
                </Typography>
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Groups color="primary" />
              <Box>
                <Typography variant="subtitle2">多人协作</Typography>
                <Typography variant="caption" color="text.secondary">
                  支持多用户同时在线，实时同步协作状态
                </Typography>
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Share color="primary" />
              <Box>
                <Typography variant="subtitle2">智能共享</Typography>
                <Typography variant="caption" color="text.secondary">
                  智能分享思维地图、标注和讨论内容
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default CollaborationPage; 