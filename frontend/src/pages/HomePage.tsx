import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  IconButton,
  Fab,
  Container,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,

  Tooltip
} from '@mui/material';
import {
  Psychology,
  AccountTree,
  Groups,
  ViewInAr,
  TrendingUp,
  Speed,
  People,
  CloudDone,
  Notifications,
  PlayArrow,
  Explore,
  Science,
  School,
  EmojiObjects,
  Assessment,
  Timeline as TimelineIcon,
  Memory,
  Rocket,
  Star,
  Add,
  ArrowForward
} from '@mui/icons-material';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [activeStep, setActiveStep] = useState(0);

  // 更新时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // 核心功能模块
  const coreFeatures = [
    {
      id: 'thinking',
      title: '思维分析',
      description: 'AI驱动的三层思维模型分析，深度理解您的思维模式',
      icon: <Psychology />,
      color: '#E91E63',
      bgColor: 'rgba(233, 30, 99, 0.1)',
      path: '/thinking',
      stats: { users: 1247, analyses: 5683 },
      features: ['形象思维识别', '逻辑推理分析', '创造力评估', '个性化建议']
    },
    {
      id: 'knowledge',
      title: '知识图谱',
      description: '可视化知识关联网络，探索概念间的深层连接',
      icon: <AccountTree />,
      color: '#2196F3',
      bgColor: 'rgba(33, 150, 243, 0.1)',
      path: '/knowledge',
      stats: { nodes: 3247, connections: 8951 },
      features: ['智能节点生成', '关系自动发现', '路径推理', '知识推荐']
    },
    {
      id: 'collaboration',
      title: '实时协作',
      description: '多用户协作思维空间，实现思维的碰撞与融合',
      icon: <Groups />,
      color: '#FF5722',
      bgColor: 'rgba(255, 87, 34, 0.1)',
      path: '/collaboration',
      stats: { sessions: 156, participants: 423 },
      features: ['实时思维同步', '协作白板', '语音/视频', '智能匹配']
    },
    {
      id: '3d-space',
      title: '3D思维空间',
      description: '沉浸式三维思维体验，支持VR/AR交互',
      icon: <ViewInAr />,
      color: '#4CAF50',
      bgColor: 'rgba(76, 175, 80, 0.1)',
      path: '/3d-space',
      stats: { spaces: 89, interactions: 2341 },
      features: ['三层空间可视化', 'XR支持', '动态交互', '空间导航']
    }
  ];

  // 系统统计数据
  const systemStats = [
    { label: '总用户数', value: '2,847', change: '+12%', color: 'primary' },
    { label: '思维分析次数', value: '15,693', change: '+25%', color: 'secondary' },
    { label: '知识节点', value: '8,742', change: '+18%', color: 'success' },
    { label: '协作会话', value: '1,234', change: '+31%', color: 'warning' }
  ];

  // 最新活动
  const recentActivities = [
    {
      user: '张三',
      action: '完成了创造思维分析',
      time: '2分钟前',
      avatar: '👨‍💼',
      type: 'analysis'
    },
    {
      user: '李四',
      action: '创建了新的知识图谱',
      time: '5分钟前',
      avatar: '👩‍🔬',
      type: 'knowledge'
    },
    {
      user: '王五',
      action: '加入了协作会话',
      time: '8分钟前',
      avatar: '👨‍🎓',
      type: 'collaboration'
    },
    {
      user: 'AI助手',
      action: '生成了新的思维洞察',
      time: '10分钟前',
      avatar: '🤖',
      type: 'ai'
    }
  ];

  // 快速开始步骤
  const quickStartSteps = [
    {
      label: '选择思维模式',
      description: '根据您的需求选择形象思维、逻辑思维或创造思维'
    },
    {
      label: '开始分析',
      description: '输入您的想法或问题，让AI为您进行深度分析'
    },
    {
      label: '探索关联',
      description: '在知识图谱中发现概念间的有趣连接'
    },
    {
      label: '协作创新',
      description: '邀请团队成员，在3D空间中共同探索创新解决方案'
    }
  ];

  const handleFeatureClick = (path: string) => {
    navigate(path);
  };

  return (
    <Container maxWidth={false} sx={{ py: 0 }}>
      {/* 欢迎横幅 */}
      <Paper
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          p: 4,
          mb: 4,
          borderRadius: 3,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 2 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
                🧠 智能思维与灵境融合平台
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
                探索认知的边界，构建思维的未来 | 当前时间：{currentTime.toLocaleString()}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<Rocket />}
                  onClick={() => navigate('/thinking')}
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    backdropFilter: 'blur(10px)',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                  }}
                >
                  开始思维分析
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<Explore />}
                  onClick={() => navigate('/knowledge')}
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)',
                    color: 'white',
                    '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' }
                  }}
                >
                  探索知识图谱
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Box
                  sx={{
                    width: 120,
                    height: 120,
                    bgcolor: 'rgba(255,255,255,0.2)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '48px',
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  ✨
                </Box>
                <Typography variant="h6">AI 已就绪</Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  3个思维模型 | 24/7 在线服务
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>
        
        {/* 装饰性背景 */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 200,
            height: 200,
            bgcolor: 'rgba(255,255,255,0.1)',
            borderRadius: '50%',
            zIndex: 1
          }}
        />
      </Paper>

      <Grid container spacing={3}>
        {/* 核心功能卡片 */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
            🚀 核心功能模块
          </Typography>
          <Grid container spacing={3}>
            {coreFeatures.map((feature) => (
              <Grid item xs={12} sm={6} lg={3} key={feature.id}>
                <Card
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4
                    }
                  }}
                  onClick={() => handleFeatureClick(feature.path)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar
                        sx={{
                          bgcolor: feature.bgColor,
                          color: feature.color,
                          mr: 2,
                          width: 48,
                          height: 48
                        }}
                      >
                        {feature.icon}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {Object.values(feature.stats).join(' / ')}
                        </Typography>
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" paragraph sx={{ minHeight: 48 }}>
                      {feature.description}
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      {feature.features.map((feat, index) => (
                        <Chip
                          key={index}
                          label={feat}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5, fontSize: '11px' }}
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      endIcon={<ArrowForward />}
                      sx={{ color: feature.color }}
                    >
                      立即体验
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* 系统统计 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Assessment /> 系统统计概览
            </Typography>
            <Grid container spacing={3}>
              {systemStats.map((stat, index) => (
                <Grid item xs={6} md={3} key={index}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: `${stat.color}.main` }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.label}
                    </Typography>
                    <Chip
                      label={stat.change}
                      size="small"
                      color="success"
                      sx={{ mt: 1, fontSize: '11px' }}
                    />
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>

          {/* 快速开始指南 */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <School /> 快速开始指南
            </Typography>
            <Stepper activeStep={activeStep} orientation="vertical">
              {quickStartSteps.map((step, index) => (
                <Step key={index}>
                  <StepLabel
                    onClick={() => setActiveStep(index)}
                    sx={{ cursor: 'pointer' }}
                  >
                    {step.label}
                  </StepLabel>
                  <StepContent>
                    <Typography variant="body2" paragraph>
                      {step.description}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Button
                        variant="contained"
                        onClick={() => setActiveStep(index + 1)}
                        sx={{ mt: 1, mr: 1 }}
                        size="small"
                      >
                        {index === quickStartSteps.length - 1 ? '完成' : '下一步'}
                      </Button>
                      {index > 0 && (
                        <Button
                          onClick={() => setActiveStep(index - 1)}
                          sx={{ mt: 1, mr: 1 }}
                          size="small"
                        >
                          上一步
                        </Button>
                      )}
                    </Box>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Paper>
        </Grid>

        {/* 侧边栏 */}
        <Grid item xs={12} md={4}>
          {/* 系统状态 */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Speed /> 系统状态
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">AI模型负载</Typography>
                <Typography variant="body2">75%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={75} sx={{ height: 8, borderRadius: 1 }} />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">内存使用</Typography>
                <Typography variant="body2">62%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={62} color="success" sx={{ height: 8, borderRadius: 1 }} />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">网络延迟</Typography>
                <Typography variant="body2">18ms</Typography>
              </Box>
              <LinearProgress variant="determinate" value={95} color="info" sx={{ height: 8, borderRadius: 1 }} />
            </Box>

            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="caption">
                🟢 所有服务运行正常
              </Typography>
            </Alert>
          </Paper>

          {/* 最新活动 */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TimelineIcon /> 最新活动
            </Typography>
            
            <List dense>
              {recentActivities.map((activity, index) => (
                <React.Fragment key={index}>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ width: 32, height: 32, fontSize: '16px' }}>
                        {activity.avatar}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          <strong>{activity.user}</strong> {activity.action}
                        </Typography>
                      }
                      secondary={activity.time}
                    />
                  </ListItem>
                  {index < recentActivities.length - 1 && <Divider variant="inset" />}
                </React.Fragment>
              ))}
            </List>

            <Button
              variant="outlined"
              size="small"
              fullWidth
              sx={{ mt: 2 }}
              onClick={() => navigate('/dashboard')}
            >
              查看全部活动
            </Button>
          </Paper>
        </Grid>
      </Grid>

      {/* 浮动操作按钮 */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 32,
          right: 32,
          zIndex: 1000
        }}
        onClick={() => navigate('/thinking')}
      >
        <Add />
      </Fab>
    </Container>
  );
};

export default HomePage; 