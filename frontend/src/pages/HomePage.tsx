import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Avatar,
  Chip,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Divider,
  Alert,
  Skeleton,
  Fade,
  Slide,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Lightbulb,
  AccountTree,
  Groups,
  ViewInAr,
  Timeline,
  Star,
  ArrowForward,
  PlayArrow,
  Analytics,
  EmojiObjects,
  Assessment,
  Favorite,
  School,
  Insights,
  AutoAwesome,
  RocketLaunch
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { thinkingService } from '../services/thinkingService';

interface RecentAnalysis {
  id: number;
  input_text: string;
  thinking_summary: {
    dominant_thinking_style: string;
    thinking_scores: Record<string, number>;
    balance_index: number;
  };
  created_at: string;
  is_favorited: boolean;
}

interface UserStats {
  total_analyses: number;
  recent_analyses: number;
  favorite_count: number;
  dominant_style: string;
  average_scores: Record<string, number>;
  improvement_trend: string;
}

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, isLoggedIn } = useAuth();
  
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isLoggedIn && user) {
      loadUserData();
    }
  }, [isLoggedIn, user]);

  const loadUserData = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const [analyses, stats] = await Promise.all([
        thinkingService.getAnalysisHistory(user.id.toString(), { limit: 5 }),
        thinkingService.getThinkingStatistics(user.id.toString())
      ]);
      
      setRecentAnalyses(analyses);
      setUserStats(stats);
    } catch (error) {
      console.error('加载用户数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: <Psychology color="primary" />,
      title: "AI思维分析",
      description: "运用前沿AI技术，深度分析您的思维模式，识别逻辑思维、形象思维和创造思维特征",
      color: theme.palette.primary.main,
      path: "/thinking"
    },
    {
      icon: <AccountTree color="secondary" />,
      title: "知识图谱",
      description: "可视化展示知识关联网络，帮助您建立系统性的认知框架和思维导图",
      color: theme.palette.secondary.main,
      path: "/knowledge"
    },
    {
      icon: <Groups color="success" />,
      title: "实时协作",
      description: "与他人共同探索思维空间，进行头脑风暴和创意交流，激发集体智慧",
      color: theme.palette.success.main,
      path: "/collaboration"
    },
    {
      icon: <ViewInAr color="warning" />,
      title: "3D思维空间",
      description: "沉浸式三维思维体验，在立体空间中组织和展示您的想法和概念",
      color: theme.palette.warning.main,
      path: "/3d-space"
    }
  ];

  const renderWelcomeSection = () => (
    <Paper
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        p: 4,
        borderRadius: 3,
        mb: 4,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
              {isLoggedIn ? `欢迎回来，${user?.full_name || user?.username}！` : '欢迎来到智能思维分析平台'}
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
              {isLoggedIn 
                ? '探索您的思维世界，发现认知潜能，与AI一起成长'
                : '运用前沿AI技术，深度分析思维模式，开启智慧之旅'
              }
            </Typography>
            {!isLoggedIn ? (
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<RocketLaunch />}
                  onClick={() => navigate('/register')}
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    backdropFilter: 'blur(10px)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.3)'
                    }
                  }}
                >
                  开始体验
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<Psychology />}
                  onClick={() => navigate('/thinking')}
                  sx={{
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    color: 'white',
                    '&:hover': {
                      borderColor: 'white',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)'
                    }
                  }}
                >
                  快速体验
                </Button>
              </Box>
            ) : (
              <Button
                variant="contained"
                size="large"
                startIcon={<PlayArrow />}
                onClick={() => navigate('/thinking')}
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  backdropFilter: 'blur(10px)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.3)'
                  }
                }}
              >
                开始新的分析
              </Button>
            )}
          </Grid>
          {isLoggedIn && user && (
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
                <CardContent sx={{ textAlign: 'center', color: 'white' }}>
                  <Avatar 
                    src={user.avatar_url}
                    sx={{ 
                      width: 80, 
                      height: 80, 
                      mx: 'auto', 
                      mb: 2,
                      bgcolor: 'rgba(255, 255, 255, 0.2)'
                    }}
                  >
                    {user.username.charAt(0).toUpperCase()}
                  </Avatar>
                  <Typography variant="h6" gutterBottom>
                    {user.full_name || user.username}
                  </Typography>
                  {user.thinking_stats && (
                    <>
                      <Typography variant="body2" sx={{ opacity: 0.8, mb: 1 }}>
                        已完成 {user.thinking_stats.total_analyses} 次分析
                      </Typography>
                      {user.thinking_stats.dominant_style && (
                        <Chip 
                          label={`主导风格: ${user.thinking_stats.dominant_style}`}
                          size="small"
                          sx={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.2)',
                            color: 'white'
                          }}
                        />
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Box>
    </Paper>
  );

  const renderFeatureCards = () => (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {features.map((feature, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Fade in timeout={600 + index * 200}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: 6
                }
              }}
              onClick={() => navigate(feature.path)}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box 
                    sx={{ 
                      p: 1.5, 
                      borderRadius: 2, 
                      backgroundColor: `${feature.color}20`,
                      mr: 2
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" component="h3">
                    {feature.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  endIcon={<ArrowForward />}
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(feature.path);
                  }}
                >
                  立即体验
                </Button>
              </CardActions>
            </Card>
          </Fade>
        </Grid>
      ))}
    </Grid>
  );

  const renderUserDashboard = () => {
    if (!isLoggedIn || !user) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* 用户统计 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Analytics sx={{ mr: 1, color: 'primary.main' }} />
                思维统计
              </Typography>
              
              {loading ? (
                <Box>
                  <Skeleton height={40} />
                  <Skeleton height={40} />
                  <Skeleton height={40} />
                </Box>
              ) : userStats ? (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">总分析次数</Typography>
                    <Typography variant="h6" color="primary">{userStats.total_analyses}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">最近分析</Typography>
                    <Typography variant="h6" color="secondary">{userStats.recent_analyses}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">收藏数量</Typography>
                    <Typography variant="h6" color="error">{userStats.favorite_count}</Typography>
                  </Box>
                  
                  {userStats.dominant_style && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" gutterBottom>主导思维风格</Typography>
                      <Chip 
                        label={userStats.dominant_style} 
                        color="primary" 
                        icon={<Psychology />}
                      />
                    </Box>
                  )}
                  
                  {Object.keys(userStats.average_scores).length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" gutterBottom>平均分数</Typography>
                      {Object.entries(userStats.average_scores).map(([style, score]) => (
                        <Box key={style} sx={{ mb: 1 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption">{style}</Typography>
                            <Typography variant="caption">{(score * 100).toFixed(1)}%</Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={score * 100}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                      ))}
                    </Box>
                  )}
                </Box>
              ) : (
                <Alert severity="info">暂无统计数据</Alert>
              )}
            </CardContent>
            <CardActions>
              <Button size="small" startIcon={<Timeline />} onClick={() => navigate('/dashboard')}>
                查看详细统计
              </Button>
            </CardActions>
          </Card>
        </Grid>

        {/* 最近分析 */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Assessment sx={{ mr: 1, color: 'primary.main' }} />
                最近分析
              </Typography>
              
              {loading ? (
                <Box>
                  {[1, 2, 3].map((item) => (
                    <Box key={item} sx={{ mb: 2 }}>
                      <Skeleton height={20} width="80%" />
                      <Skeleton height={16} width="60%" />
                      <Skeleton height={16} width="40%" />
                    </Box>
                  ))}
                </Box>
              ) : recentAnalyses.length > 0 ? (
                <List>
                  {recentAnalyses.map((analysis, index) => (
                    <React.Fragment key={analysis.id}>
                      <ListItem
                        sx={{
                          cursor: 'pointer',
                          borderRadius: 1,
                          '&:hover': { backgroundColor: 'action.hover' }
                        }}
                        onClick={() => navigate(`/thinking/analysis/${analysis.id}`)}
                      >
                        <ListItemIcon>
                          <Box
                            sx={{
                              width: 40,
                              height: 40,
                              borderRadius: '50%',
                              backgroundColor: 'primary.main',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: 'white'
                            }}
                          >
                            <Psychology />
                          </Box>
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body1" noWrap sx={{ flex: 1 }}>
                                {analysis.input_text.length > 50 
                                  ? `${analysis.input_text.substring(0, 50)}...` 
                                  : analysis.input_text
                                }
                              </Typography>
                              {analysis.is_favorited && (
                                <Favorite color="error" fontSize="small" />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                              <Chip 
                                label={analysis.thinking_summary.dominant_thinking_style} 
                                size="small" 
                                color="primary"
                              />
                              <Chip 
                                label={`${(analysis.thinking_summary.balance_index * 100).toFixed(1)}%`} 
                                size="small" 
                                variant="outlined"
                              />
                              <Typography variant="caption" color="text.secondary">
                                {new Date(analysis.created_at).toLocaleDateString()}
                              </Typography>
                            </Box>
                          }
                        />
                        <IconButton size="small">
                          <ArrowForward />
                        </IconButton>
                      </ListItem>
                      {index < recentAnalyses.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Alert severity="info">
                  还没有分析记录。
                  <Button onClick={() => navigate('/thinking')} sx={{ ml: 1 }}>
                    开始第一次分析
                  </Button>
                </Alert>
              )}
            </CardContent>
            {recentAnalyses.length > 0 && (
              <CardActions>
                <Button size="small" startIcon={<Timeline />} onClick={() => navigate('/thinking')}>
                  查看所有分析
                </Button>
              </CardActions>
            )}
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderQuickActions = () => (
    <Paper sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        快速开始
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<Psychology />}
            onClick={() => navigate('/thinking')}
            sx={{ py: 1.5 }}
          >
            思维分析
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<EmojiObjects />}
            onClick={() => navigate('/thinking')}
            sx={{ py: 1.5 }}
          >
            创意生成
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<Groups />}
            onClick={() => navigate('/collaboration')}
            sx={{ py: 1.5 }}
          >
            加入协作
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<ViewInAr />}
            onClick={() => navigate('/3d-space')}
            sx={{ py: 1.5 }}
          >
            3D空间
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {renderWelcomeSection()}
      
      {isLoggedIn && renderUserDashboard()}
      
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        核心功能
      </Typography>
      {renderFeatureCards()}
      
      {renderQuickActions()}
      
      {/* 平台介绍 */}
      <Paper sx={{ p: 4, background: 'linear-gradient(45deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="h4" gutterBottom>
              AI驱动的思维分析平台
            </Typography>
            <Typography variant="body1" paragraph>
              我们运用最先进的人工智能技术，深度分析您的思维模式，帮助您了解自己的认知特点，
              发现思维优势，并提供个性化的思维训练建议。
            </Typography>
            <Typography variant="body1" paragraph>
              通过三层思维模型（形象思维、逻辑思维、创造思维），我们能够全面评估您的思维能力，
              并在3D可视化环境中展示分析结果，让思维分析变得更加直观和有趣。
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip icon={<AutoAwesome />} label="AI驱动" color="primary" />
              <Chip icon={<Insights />} label="深度分析" color="secondary" />
              <Chip icon={<School />} label="个性化建议" color="success" />
              <Chip icon={<ViewInAr />} label="3D可视化" color="warning" />
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Box
                sx={{
                  width: 200,
                  height: 200,
                  mx: 'auto',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '4rem'
                }}
              >
                🧠
              </Box>
              <Typography variant="h6" sx={{ mt: 2 }}>
                智能思维分析
              </Typography>
              <Typography variant="body2" color="text.secondary">
                探索您的认知潜能
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default HomePage; 