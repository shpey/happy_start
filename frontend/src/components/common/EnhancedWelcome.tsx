import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  IconButton,
  Fade,
  Slide,
  Grow,
  useTheme,
  useMediaQuery,
  Avatar,
  Chip,
  CircularProgress,
  LinearProgress
} from '@mui/material';
import {
  Psychology,
  RocketLaunch,
  AutoAwesome,
  Insights,
  TrendingUp,
  PlayArrow,
  ArrowForward,
  Star,
  EmojiObjects,
  Groups,
  ViewInAr,
  AccountTree
} from '@mui/icons-material';
import { keyframes } from '@mui/system';

// 动画定义
const floatAnimation = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
`;

const pulseAnimation = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`;

const gradientAnimation = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

interface EnhancedWelcomeProps {
  user?: any;
  onNavigate: (path: string) => void;
  stats?: any;
}

const EnhancedWelcome: React.FC<EnhancedWelcomeProps> = ({ 
  user, 
  onNavigate,
  stats 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [animationStep, setAnimationStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setAnimationStep(prev => (prev + 1) % 3);
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  const features = [
    {
      icon: <Psychology />,
      title: "AI思维分析",
      description: "深度分析您的思维模式",
      color: "#6366f1",
      path: "/thinking"
    },
    {
      icon: <AccountTree />,
      title: "知识图谱",
      description: "可视化思维连接",
      color: "#10b981",
      path: "/knowledge"
    },
    {
      icon: <Groups />,
      title: "实时协作",
      description: "团队思维共享",
      color: "#f59e0b",
      path: "/collaboration"
    },
    {
      icon: <ViewInAr />,
      title: "3D思维空间",
      description: "沉浸式思维体验",
      color: "#ef4444",
      path: "/3d-space"
    }
  ];

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
        background: `linear-gradient(-45deg, 
          ${theme.palette.primary.main}15, 
          ${theme.palette.secondary.main}15, 
          ${theme.palette.success.main}15, 
          ${theme.palette.info.main}15)`,
        backgroundSize: '400% 400%',
        animation: `${gradientAnimation} 15s ease infinite`,
        overflow: 'hidden'
      }}
    >
      {/* 背景装饰元素 */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.1) 0%, transparent 50%)',
          zIndex: 0
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1, pt: 8 }}>
        {/* 主标题区域 */}
        <Fade in timeout={1000}>
          <Box textAlign="center" mb={8}>
            <Slide direction="down" in timeout={1200}>
              <Box>
                <Avatar
                  sx={{
                    width: 80,
                    height: 80,
                    mx: 'auto',
                    mb: 3,
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    animation: `${floatAnimation} 3s ease-in-out infinite`,
                    boxShadow: `0 8px 32px ${theme.palette.primary.main}40`
                  }}
                >
                  <Psychology fontSize="large" />
                </Avatar>
                
                <Typography
                  variant="h2"
                  component="h1"
                  sx={{
                    fontWeight: 800,
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    color: 'transparent',
                    mb: 2,
                    fontSize: { xs: '2.5rem', md: '3.5rem' }
                  }}
                >
                  智能思维分析平台
                </Typography>
                
                <Typography
                  variant="h5"
                  color="text.secondary"
                  sx={{ 
                    mb: 4,
                    fontWeight: 300,
                    maxWidth: 600,
                    mx: 'auto'
                  }}
                >
                  运用前沿AI技术，深度分析思维模式，开启认知提升之旅
                </Typography>
              </Box>
            </Slide>

            {/* 用户欢迎信息 */}
            {user && (
              <Grow in timeout={1500}>
                <Card
                  sx={{
                    maxWidth: 400,
                    mx: 'auto',
                    mb: 4,
                    background: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: 3,
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      欢迎回来，{user.username}！
                    </Typography>
                    {stats && (
                      <Box display="flex" justifyContent="space-around" mt={2}>
                        <Box textAlign="center">
                          <Typography variant="h4" color="primary" fontWeight="bold">
                            {stats.total_analyses || 0}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            总分析次数
                          </Typography>
                        </Box>
                        <Box textAlign="center">
                          <Typography variant="h4" color="secondary" fontWeight="bold">
                            {stats.favorite_count || 0}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            收藏分析
                          </Typography>
                        </Box>
                        <Box textAlign="center">
                          <Chip
                            label={stats.dominant_style || "待分析"}
                            color="primary"
                            variant="outlined"
                            size="small"
                          />
                          <Typography variant="caption" display="block" color="text.secondary">
                            主导思维
                          </Typography>
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grow>
            )}

            {/* 快速开始按钮 */}
            <Fade in timeout={2000}>
              <Box>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<RocketLaunch />}
                  onClick={() => onNavigate(user ? '/thinking' : '/login')}
                  sx={{
                    px: 4,
                    py: 2,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    borderRadius: 3,
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    boxShadow: `0 4px 20px ${theme.palette.primary.main}40`,
                    animation: `${pulseAnimation} 2s ease-in-out infinite`,
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 8px 25px ${theme.palette.primary.main}50`,
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  {user ? '开始思维分析' : '立即体验'}
                </Button>
              </Box>
            </Fade>
          </Box>
        </Fade>

        {/* 功能特性卡片 */}
        <Grid container spacing={3} mb={8}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={feature.title}>
              <Grow in timeout={1000 + index * 200}>
                <Card
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    background: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: 3,
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
                      background: 'rgba(255, 255, 255, 0.95)',
                    }
                  }}
                  onClick={() => onNavigate(feature.path)}
                >
                  <CardContent sx={{ p: 3, textAlign: 'center' }}>
                    <Avatar
                      sx={{
                        width: 60,
                        height: 60,
                        mx: 'auto',
                        mb: 2,
                        background: feature.color,
                        boxShadow: `0 4px 20px ${feature.color}40`
                      }}
                    >
                      {feature.icon}
                    </Avatar>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {feature.title}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                      sx={{ lineHeight: 1.6 }}
                    >
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grow>
            </Grid>
          ))}
        </Grid>

        {/* 动态统计数字 */}
        <Fade in timeout={2500}>
          <Card
            sx={{
              background: 'rgba(255, 255, 255, 0.9)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: 3,
              p: 4,
              textAlign: 'center',
              mb: 8
            }}
          >
            <Typography variant="h5" fontWeight="bold" mb={3}>
              平台实时数据
            </Typography>
            <Grid container spacing={4}>
              <Grid item xs={12} sm={4}>
                <Box>
                  <Typography variant="h3" color="primary" fontWeight="bold">
                    10,000+
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    分析完成
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box>
                  <Typography variant="h3" color="secondary" fontWeight="bold">
                    5,000+
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    活跃用户
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box>
                  <Typography variant="h3" color="success.main" fontWeight="bold">
                    98%
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    满意度
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Card>
        </Fade>

        {/* 底部行动区域 */}
        <Slide direction="up" in timeout={3000}>
          <Box textAlign="center" pb={8}>
            <Typography variant="h5" fontWeight="bold" mb={3}>
              准备开启您的思维提升之旅吗？
            </Typography>
            <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
              <Button
                variant="outlined"
                size="large"
                startIcon={<EmojiObjects />}
                onClick={() => onNavigate('/thinking')}
                sx={{ 
                  borderRadius: 3,
                  px: 3,
                  py: 1.5
                }}
              >
                开始分析
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<Groups />}
                onClick={() => onNavigate('/collaboration')}
                sx={{ 
                  borderRadius: 3,
                  px: 3,
                  py: 1.5
                }}
              >
                加入协作
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<ViewInAr />}
                onClick={() => onNavigate('/3d-space')}
                sx={{ 
                  borderRadius: 3,
                  px: 3,
                  py: 1.5
                }}
              >
                探索3D空间
              </Button>
            </Box>
          </Box>
        </Slide>
      </Container>
    </Box>
  );
};

export default EnhancedWelcome; 