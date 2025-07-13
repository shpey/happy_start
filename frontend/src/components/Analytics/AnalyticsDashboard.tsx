import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  LinearProgress,
  CircularProgress,
  Alert,
  Tooltip,
  IconButton,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Analytics,
  Psychology,
  Group,
  Schedule,
  Assessment,
  Refresh,
  FileDownload,
  Info,
  Star,
  Warning,
  CheckCircle
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  RadialLinearScale
} from 'chart.js';
import {
  Line,
  Bar,
  Doughnut,
  Radar
} from 'react-chartjs-2';
import { apiService } from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  RadialLinearScale
);

interface AnalyticsDashboardProps {
  userId?: number;
  isAdmin?: boolean;
}

interface DashboardData {
  personalStats: any;
  recentActivity: any;
  recommendations: any[];
  quickInsights: any;
}

interface BehaviorAnalytics {
  activityMetrics: any;
  usagePatterns: any;
  timeDistribution: any;
  featureUsage: any;
  trends: any;
}

interface ThinkingInsights {
  thinkingDistribution: any;
  cognitiveAssessment: any;
  patternEvolution: any;
  recommendations: any[];
  comparativeAnalysis: any;
}

interface SystemStats {
  userStatistics: any;
  analysisStatistics: any;
  collaborationStatistics: any;
  performanceStatistics: any;
  growthTrends: any;
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  userId,
  isAdmin = false
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { success, error } = useNotification();

  // 状态管理
  const [currentTab, setCurrentTab] = useState(0);
  const [timeRange, setTimeRange] = useState(30);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // 数据状态
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [behaviorAnalytics, setBehaviorAnalytics] = useState<BehaviorAnalytics | null>(null);
  const [thinkingInsights, setThinkingInsights] = useState<ThinkingInsights | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);

  // 获取仪表板摘要数据
  const fetchDashboardSummary = useCallback(async () => {
    try {
      const response = await apiService.get('/analytics/dashboard-summary');
      setDashboardData(response.data);
    } catch (err) {
      console.error('获取仪表板摘要失败:', err);
      error('获取仪表板摘要失败');
    }
  }, [error]);

  // 获取用户行为分析
  const fetchBehaviorAnalytics = useCallback(async () => {
    try {
      const params = { days: timeRange };
      if (userId && isAdmin) {
        params.user_id = userId;
      }
      
      const response = await apiService.get('/analytics/user-behavior', { params });
      setBehaviorAnalytics(response.data);
    } catch (err) {
      console.error('获取行为分析失败:', err);
      error('获取行为分析失败');
    }
  }, [timeRange, userId, isAdmin, error]);

  // 获取思维模式洞察
  const fetchThinkingInsights = useCallback(async () => {
    try {
      const params = { days: timeRange };
      if (userId && isAdmin) {
        params.user_id = userId;
      }
      
      const response = await apiService.get('/analytics/thinking-patterns', { params });
      setThinkingInsights(response.data);
    } catch (err) {
      console.error('获取思维洞察失败:', err);
      error('获取思维洞察失败');
    }
  }, [timeRange, userId, isAdmin, error]);

  // 获取系统统计（仅管理员）
  const fetchSystemStats = useCallback(async () => {
    if (!isAdmin) return;
    
    try {
      const response = await apiService.get('/analytics/system-usage', {
        params: { days: timeRange }
      });
      setSystemStats(response.data);
    } catch (err) {
      console.error('获取系统统计失败:', err);
      error('获取系统统计失败');
    }
  }, [timeRange, isAdmin, error]);

  // 初始化数据加载
  const loadAllData = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchDashboardSummary(),
        fetchBehaviorAnalytics(),
        fetchThinkingInsights(),
        fetchSystemStats()
      ]);
    } catch (err) {
      console.error('数据加载失败:', err);
    } finally {
      setLoading(false);
    }
  }, [fetchDashboardSummary, fetchBehaviorAnalytics, fetchThinkingInsights, fetchSystemStats]);

  // 刷新数据
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await loadAllData();
      success('数据刷新成功');
    } catch (err) {
      error('数据刷新失败');
    } finally {
      setRefreshing(false);
    }
  };

  // 导出报告
  const handleExportReport = async () => {
    try {
      const response = await apiService.get('/analytics/export-report', {
        params: {
          format: 'json',
          include_charts: true,
          days: timeRange
        }
      });
      
      // 创建下载链接
      const dataStr = JSON.stringify(response.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `analytics-report-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
      success('报告导出成功');
    } catch (err) {
      console.error('报告导出失败:', err);
      error('报告导出失败');
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  // 时间范围变化时重新加载数据
  useEffect(() => {
    if (!loading) {
      loadAllData();
    }
  }, [timeRange]);

  // Tab切换处理
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  // 图表配置
  const getChartOptions = (title: string) => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20
        }
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
          weight: 'bold'
        },
        padding: {
          bottom: 20
        }
      },
      tooltip: {
        backgroundColor: theme.palette.background.paper,
        titleColor: theme.palette.text.primary,
        bodyColor: theme.palette.text.secondary,
        borderColor: theme.palette.divider,
        borderWidth: 1,
        cornerRadius: 8
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: theme.palette.divider
        },
        ticks: {
          color: theme.palette.text.secondary
        }
      },
      x: {
        grid: {
          color: theme.palette.divider
        },
        ticks: {
          color: theme.palette.text.secondary
        }
      }
    }
  });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', p: isMobile ? 2 : 3 }}>
      {/* 页面头部 */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h4" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Analytics color="primary" />
          数据分析仪表板
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
            <InputLabel>时间范围</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as number)}
              label="时间范围"
            >
              <MenuItem value={7}>最近7天</MenuItem>
              <MenuItem value={30}>最近30天</MenuItem>
              <MenuItem value={90}>最近90天</MenuItem>
              <MenuItem value={365}>最近1年</MenuItem>
            </Select>
          </FormControl>
          
          <Tooltip title="刷新数据">
            <IconButton
              onClick={handleRefresh}
              disabled={refreshing}
              color="primary"
            >
              <Refresh className={refreshing ? 'rotating' : ''} />
            </IconButton>
          </Tooltip>
          
          <Button
            startIcon={<FileDownload />}
            onClick={handleExportReport}
            variant="outlined"
            size="small"
          >
            导出报告
          </Button>
        </Box>
      </Box>

      {/* 主要内容 */}
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={currentTab} onChange={handleTabChange}>
            <Tab label="概览仪表板" />
            <Tab label="用户行为分析" />
            <Tab label="思维模式洞察" />
            {isAdmin && <Tab label="系统统计" />}
          </Tabs>
        </Box>

        {/* 概览仪表板 */}
        {currentTab === 0 && (
          <DashboardOverview 
            data={dashboardData}
            theme={theme}
            isMobile={isMobile}
            getChartOptions={getChartOptions}
          />
        )}

        {/* 用户行为分析 */}
        {currentTab === 1 && (
          <BehaviorAnalysisPanel 
            data={behaviorAnalytics}
            theme={theme}
            isMobile={isMobile}
            getChartOptions={getChartOptions}
          />
        )}

        {/* 思维模式洞察 */}
        {currentTab === 2 && (
          <ThinkingInsightsPanel 
            data={thinkingInsights}
            theme={theme}
            isMobile={isMobile}
            getChartOptions={getChartOptions}
          />
        )}

        {/* 系统统计（管理员） */}
        {currentTab === 3 && isAdmin && (
          <SystemStatsPanel 
            data={systemStats}
            theme={theme}
            isMobile={isMobile}
            getChartOptions={getChartOptions}
          />
        )}
      </Box>
    </Box>
  );
};

// 概览仪表板组件
const DashboardOverview: React.FC<{
  data: DashboardData | null;
  theme: any;
  isMobile: boolean;
  getChartOptions: (title: string) => any;
}> = ({ data, theme, isMobile, getChartOptions }) => {
  if (!data) {
    return <Alert severity="info">暂无数据</Alert>;
  }

  const { personalStats, recentActivity, recommendations, quickInsights } = data;

  return (
    <Grid container spacing={3}>
      {/* 个人统计卡片 */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Assessment color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">总分析次数</Typography>
            </Box>
            <Typography variant="h3" color="primary">
              {personalStats?.totalAnalyses || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              日均 {personalStats?.dailyAverage || 0} 次
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Schedule color="secondary" sx={{ mr: 1 }} />
              <Typography variant="h6">活跃天数</Typography>
            </Box>
            <Typography variant="h3" color="secondary">
              {personalStats?.activeDays || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              最近 {Math.min(30, personalStats?.activeDays || 0)} 天
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Psychology color="success.main" sx={{ mr: 1 }} />
              <Typography variant="h6">整体评分</Typography>
            </Box>
            <Typography variant="h3" color="success.main">
              {Math.round(personalStats?.overallScore || 0)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              认知能力评估
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Star color="warning.main" sx={{ mr: 1 }} />
              <Typography variant="h6">主导风格</Typography>
            </Box>
            <Typography variant="h5" color="warning.main">
              {personalStats?.dominantThinkingStyle || '未知'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              思维类型偏好
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* 快速洞察 */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardHeader title="快速洞察" />
          <CardContent>
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                优势领域
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                {quickInsights?.strengths?.map((strength: string, index: number) => (
                  <Chip
                    key={index}
                    label={strength}
                    color="success"
                    size="small"
                    icon={<CheckCircle />}
                  />
                ))}
              </Box>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                待提升领域
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                {quickInsights?.weaknesses?.map((weakness: string, index: number) => (
                  <Chip
                    key={index}
                    label={weakness}
                    color="warning"
                    size="small"
                    icon={<Warning />}
                  />
                ))}
              </Box>
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                发展趋势
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body1">
                  {quickInsights?.evolutionTrend || '稳定'}
                </Typography>
                {quickInsights?.improvementRate > 0 ? (
                  <TrendingUp color="success" />
                ) : (
                  <TrendingDown color="error" />
                )}
                <Typography variant="body2" color="text.secondary">
                  ({quickInsights?.improvementRate || 0}%)
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 个性化建议 */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardHeader title="个性化建议" />
          <CardContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {recommendations?.slice(0, 3).map((rec: any, index: number) => (
                <Paper
                  key={index}
                  sx={{
                    p: 2,
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 2
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                    <Info color={
                      rec.priority === 'high' ? 'error' :
                      rec.priority === 'medium' ? 'warning' : 'info'
                    } />
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        {rec.type}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {rec.content}
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// 用户行为分析面板
const BehaviorAnalysisPanel: React.FC<{
  data: BehaviorAnalytics | null;
  theme: any;
  isMobile: boolean;
  getChartOptions: (title: string) => any;
}> = ({ data, theme, isMobile, getChartOptions }) => {
  if (!data) {
    return <Alert severity="info">暂无行为分析数据</Alert>;
  }

  // 时间分布图表数据
  const hourlyData = {
    labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
    datasets: [{
      label: '使用频次',
      data: Array.from({ length: 24 }, (_, i) => data.timeDistribution?.hourly?.[i] || 0),
      borderColor: theme.palette.primary.main,
      backgroundColor: theme.palette.primary.light,
      fill: true,
      tension: 0.4
    }]
  };

  // 功能使用分布
  const featureUsageData = {
    labels: Object.keys(data.featureUsage?.analysisTypes || {}),
    datasets: [{
      data: Object.values(data.featureUsage?.analysisTypes || {}),
      backgroundColor: [
        theme.palette.primary.main,
        theme.palette.secondary.main,
        theme.palette.success.main,
        theme.palette.warning.main,
        theme.palette.error.main
      ]
    }]
  };

  return (
    <Grid container spacing={3}>
      {/* 活跃度指标 */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardHeader title="活跃度指标" />
          <CardContent>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  日均使用
                </Typography>
                <Typography variant="h5" color="primary">
                  {data.activityMetrics?.dailyAverage || 0}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  高峰时段
                </Typography>
                <Typography variant="h5" color="secondary">
                  {data.activityMetrics?.peakHour || 0}:00
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  活跃天数
                </Typography>
                <Typography variant="h5" color="success.main">
                  {data.activityMetrics?.activeDays || 0}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  留存率
                </Typography>
                <Typography variant="h5" color="warning.main">
                  {data.activityMetrics?.retentionRate || 0}%
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* 趋势分析 */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardHeader title="发展趋势" />
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography variant="h4" color={
                data.trends?.growthRate > 0 ? 'success.main' : 'error.main'
              }>
                {data.trends?.growthRate || 0}%
              </Typography>
              {data.trends?.growthRate > 0 ? (
                <TrendingUp color="success" sx={{ ml: 1 }} />
              ) : (
                <TrendingDown color="error" sx={{ ml: 1 }} />
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              增长率 - {data.trends?.trendDirection || '稳定'}
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                未来预测
              </Typography>
              {data.trends?.predictions?.slice(0, 3).map((pred: any, index: number) => (
                <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    {new Date(pred.date).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {pred.predictedValue} 次
                  </Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 时间分布图 */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardHeader title="使用时间分布" />
          <CardContent>
            <Box sx={{ height: 300 }}>
              <Line
                data={hourlyData}
                options={getChartOptions('24小时使用分布')}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 功能使用分布 */}
      <Grid item xs={12} lg={4}>
        <Card>
          <CardHeader title="功能使用分布" />
          <CardContent>
            <Box sx={{ height: 300 }}>
              <Doughnut
                data={featureUsageData}
                options={{
                  ...getChartOptions('分析类型分布'),
                  plugins: {
                    ...getChartOptions('分析类型分布').plugins,
                    legend: {
                      position: 'bottom' as const
                    }
                  }
                }}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// 思维模式洞察面板
const ThinkingInsightsPanel: React.FC<{
  data: ThinkingInsights | null;
  theme: any;
  isMobile: boolean;
  getChartOptions: (title: string) => any;
}> = ({ data, theme, isMobile, getChartOptions }) => {
  if (!data) {
    return <Alert severity="info">暂无思维洞察数据</Alert>;
  }

  // 认知能力雷达图数据
  const radarData = {
    labels: Object.keys(data.cognitiveAssessment?.abilities || {}),
    datasets: [{
      label: '能力评分',
      data: Object.values(data.cognitiveAssessment?.abilities || {}),
      borderColor: theme.palette.primary.main,
      backgroundColor: theme.palette.primary.light + '40',
      pointBackgroundColor: theme.palette.primary.main,
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: theme.palette.primary.main
    }]
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        angleLines: {
          color: theme.palette.divider
        },
        grid: {
          color: theme.palette.divider
        },
        pointLabels: {
          color: theme.palette.text.primary
        },
        ticks: {
          color: theme.palette.text.secondary,
          backdrop: {
            color: 'transparent'
          }
        },
        suggestedMin: 0,
        suggestedMax: 100
      }
    },
    plugins: {
      legend: {
        labels: {
          color: theme.palette.text.primary
        }
      }
    }
  };

  return (
    <Grid container spacing={3}>
      {/* 认知能力评估 */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardHeader title="认知能力评估" />
          <CardContent>
            <Box sx={{ height: 400 }}>
              <Radar data={radarData} options={radarOptions} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 整体评分和详情 */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardHeader title="综合评估" />
          <CardContent>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Typography variant="h2" color="primary" gutterBottom>
                {Math.round(data.cognitiveAssessment?.overallScore || 0)}
              </Typography>
              <Typography variant="h6" color="text.secondary">
                整体认知能力评分
              </Typography>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                能力详情
              </Typography>
              {Object.entries(data.cognitiveAssessment?.abilities || {}).map(([ability, score]) => (
                <Box key={ability} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{ability}</Typography>
                    <Typography variant="body2" color="primary">
                      {Math.round(score as number)}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={score as number}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              ))}
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                平均指标
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    平均置信度
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {data.cognitiveAssessment?.avgConfidence || 0}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    平均处理时间
                  </Typography>
                  <Typography variant="h6" color="info.main">
                    {Math.round(data.cognitiveAssessment?.avgProcessingTime || 0)}s
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 思维模式演进 */}
      <Grid item xs={12}>
        <Card>
          <CardHeader title="思维模式演进" />
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color={
                    data.patternEvolution?.improvementRate > 0 ? 'success.main' : 'error.main'
                  }>
                    {data.patternEvolution?.improvementRate || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    改进率
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" color="primary">
                    {data.patternEvolution?.evolutionTrend || '稳定'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    发展趋势
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="secondary">
                    {data.patternEvolution?.milestones?.length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    重要里程碑
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            {/* 里程碑展示 */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                重要里程碑
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {data.patternEvolution?.milestones?.slice(0, 3).map((milestone: any, index: number) => (
                  <Paper
                    key={index}
                    sx={{ p: 2, border: 1, borderColor: 'divider' }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="subtitle2" color="primary">
                          {milestone.type}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {milestone.description}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(milestone.date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Paper>
                ))}
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// 系统统计面板（管理员）
const SystemStatsPanel: React.FC<{
  data: SystemStats | null;
  theme: any;
  isMobile: boolean;
  getChartOptions: (title: string) => any;
}> = ({ data, theme, isMobile, getChartOptions }) => {
  if (!data) {
    return <Alert severity="info">暂无系统统计数据</Alert>;
  }

  // 增长趋势图表数据
  const growthData = {
    labels: data.growthTrends?.dailyTrends?.slice(-7).map(
      (trend: any) => new Date(trend.date).toLocaleDateString()
    ) || [],
    datasets: [
      {
        label: '新用户',
        data: data.growthTrends?.dailyTrends?.slice(-7).map(
          (trend: any) => trend.newUsers
        ) || [],
        borderColor: theme.palette.primary.main,
        backgroundColor: theme.palette.primary.light,
        tension: 0.4
      },
      {
        label: '新分析',
        data: data.growthTrends?.dailyTrends?.slice(-7).map(
          (trend: any) => trend.newAnalyses
        ) || [],
        borderColor: theme.palette.secondary.main,
        backgroundColor: theme.palette.secondary.light,
        tension: 0.4
      }
    ]
  };

  return (
    <Grid container spacing={3}>
      {/* 用户统计 */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Group color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">用户统计</Typography>
            </Box>
            <Typography variant="h3" color="primary">
              {data.userStatistics?.totalUsers || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              总用户数
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="success.main">
                新增: {data.userStatistics?.newUsers || 0}
              </Typography>
              <Typography variant="body2" color="info.main">
                活跃: {data.userStatistics?.activeUsers || 0}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 分析统计 */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Psychology color="secondary" sx={{ mr: 1 }} />
              <Typography variant="h6">分析统计</Typography>
            </Box>
            <Typography variant="h3" color="secondary">
              {data.analysisStatistics?.totalAnalyses || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              总分析次数
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="success.main">
                置信度: {data.analysisStatistics?.avgConfidence || 0}%
              </Typography>
              <Typography variant="body2" color="info.main">
                耗时: {Math.round(data.analysisStatistics?.avgProcessingTime || 0)}s
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 协作统计 */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Group color="success.main" sx={{ mr: 1 }} />
              <Typography variant="h6">协作统计</Typography>
            </Box>
            <Typography variant="h3" color="success.main">
              {data.collaborationStatistics?.totalSessions || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              协作会话
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="primary">
                事件: {data.collaborationStatistics?.totalEvents || 0}
              </Typography>
              <Typography variant="body2" color="secondary">
                协作者: {data.collaborationStatistics?.activeCollaborators || 0}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 性能统计 */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Assessment color="warning.main" sx={{ mr: 1 }} />
              <Typography variant="h6">性能统计</Typography>
            </Box>
            <Typography variant="h3" color="warning.main">
              {data.performanceStatistics?.avgResponseTime || 0}ms
            </Typography>
            <Typography variant="body2" color="text.secondary">
              平均响应时间
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="success.main">
                正常运行: {data.performanceStatistics?.uptime || 0}%
              </Typography>
              <Typography variant="body2" color="error.main">
                错误率: {data.performanceStatistics?.errorRate || 0}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 增长趋势图 */}
      <Grid item xs={12}>
        <Card>
          <CardHeader title="系统增长趋势" />
          <CardContent>
            <Box sx={{ height: 400 }}>
              <Line
                data={growthData}
                options={getChartOptions('最近7天增长趋势')}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default AnalyticsDashboard; 