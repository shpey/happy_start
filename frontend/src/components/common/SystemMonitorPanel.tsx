/**
 * 系统监控面板组件
 * 显示系统健康状态、性能指标和告警信息
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Alert,
  AlertTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Collapse,
  Badge,
  Button,
  Tooltip,
  Divider,
  CircularProgress,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Computer,
  Memory,
  Storage,
  NetworkCheck,
  Speed,
  Warning,
  Error,
  CheckCircle,
  ExpandMore,
  ExpandLess,
  Refresh,
  Settings,
  Timeline,
  Notifications,
  Security,
  Dashboard
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { useNotification } from '../../contexts/NotificationContext';
import { apiService } from '../../services/api';

interface SystemStatus {
  status: string;
  timestamp: string;
  uptime_seconds: number;
  services: number;
  healthy_services: number;
  cpu_percent?: number;
  memory_percent?: number;
  response_time_avg?: number;
  requests_per_second?: number;
}

interface PerformanceMetrics {
  current: {
    timestamp: string;
    cpu_percent: number;
    memory_percent: number;
    memory_used_mb: number;
    disk_percent: number;
    network_bytes_sent: number;
    network_bytes_recv: number;
    active_connections: number;
    response_time_avg: number;
    requests_per_second: number;
    error_rate: number;
  } | null;
  history: Array<{
    timestamp: string;
    cpu_percent: number;
    memory_percent: number;
    response_time_avg: number;
    requests_per_second: number;
    error_rate: number;
  }>;
  summary: {
    total_requests: number;
    total_errors: number;
    uptime_seconds: number;
    avg_cpu_percent?: number;
    avg_memory_percent?: number;
    avg_response_time?: number;
    max_cpu_percent?: number;
    max_memory_percent?: number;
    max_response_time?: number;
  };
}

interface Alert {
  id: string;
  level: string;
  title: string;
  message: string;
  timestamp: string;
  service: string;
  metric: string;
  value: any;
  threshold: any;
}

interface AlertsData {
  active_alerts: Alert[];
  resolved_alerts: Alert[];
  alert_summary: {
    active_count: number;
    critical_count: number;
    error_count: number;
    warning_count: number;
    info_count: number;
  };
}

interface SystemMonitorPanelProps {
  autoRefresh?: boolean;
  refreshInterval?: number;
  showCharts?: boolean;
}

export const SystemMonitorPanel: React.FC<SystemMonitorPanelProps> = ({
  autoRefresh = true,
  refreshInterval = 30000, // 30秒
  showCharts = true
}) => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [alertsData, setAlertsData] = useState<AlertsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<{ [key: string]: boolean }>({
    performance: false,
    alerts: false,
    charts: false
  });
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(autoRefresh);

  const { error, success } = useNotification();

  // 获取系统状态
  const fetchSystemStatus = useCallback(async () => {
    try {
      const response = await apiService.get('/monitoring/system/status');
      setSystemStatus(response);
    } catch (err) {
      console.error('Failed to fetch system status:', err);
      error('获取系统状态失败');
    }
  }, [error]);

  // 获取性能指标
  const fetchPerformanceMetrics = useCallback(async () => {
    try {
      const response = await apiService.get('/monitoring/metrics?hours=1');
      setPerformanceMetrics(response);
    } catch (err) {
      console.error('Failed to fetch performance metrics:', err);
      error('获取性能指标失败');
    }
  }, [error]);

  // 获取告警信息
  const fetchAlerts = useCallback(async () => {
    try {
      const response = await apiService.get('/monitoring/alerts');
      setAlertsData(response);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
      error('获取告警信息失败');
    }
  }, [error]);

  // 获取所有监控数据
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchSystemStatus(),
        fetchPerformanceMetrics(),
        fetchAlerts()
      ]);
    } finally {
      setLoading(false);
    }
  }, [fetchSystemStatus, fetchPerformanceMetrics, fetchAlerts]);

  // 手动刷新
  const handleRefresh = () => {
    fetchAllData();
    success('监控数据已刷新');
  };

  // 解决告警
  const resolveAlert = async (alertId: string) => {
    try {
      await apiService.post(`/monitoring/alerts/${alertId}/resolve`);
      await fetchAlerts(); // 重新获取告警数据
      success('告警已解决');
    } catch (err) {
      error('解决告警失败');
    }
  };

  // 切换展开状态
  const toggleExpand = (section: string) => {
    setExpanded(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'unhealthy': return 'error';
      default: return 'default';
    }
  };

  // 获取告警级别颜色
  const getAlertColor = (level: string) => {
    switch (level) {
      case 'critical': return 'error';
      case 'error': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  // 格式化时间
  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}天 ${hours}时 ${minutes}分`;
    if (hours > 0) return `${hours}时 ${minutes}分`;
    return `${minutes}分`;
  };

  // 格式化字节数
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 自动刷新
  useEffect(() => {
    fetchAllData();

    let interval: NodeJS.Timeout;
    if (autoRefreshEnabled) {
      interval = setInterval(fetchAllData, refreshInterval);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [fetchAllData, autoRefreshEnabled, refreshInterval]);

  if (loading && !systemStatus) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>加载监控数据...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* 标题和控制 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Dashboard />
          系统监控面板
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefreshEnabled}
                onChange={(e) => setAutoRefreshEnabled(e.target.checked)}
                size="small"
              />
            }
            label="自动刷新"
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
          >
            刷新
          </Button>
        </Box>
      </Box>

      {/* 系统状态概览 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Computer sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h6">系统状态</Typography>
              <Chip
                label={systemStatus?.status || 'unknown'}
                color={getStatusColor(systemStatus?.status || 'unknown')}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Speed sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h6">运行时间</Typography>
              <Typography variant="body1" sx={{ mt: 1 }}>
                {systemStatus ? formatUptime(systemStatus.uptime_seconds) : '-'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <CheckCircle sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h6">服务状态</Typography>
              <Typography variant="body1" sx={{ mt: 1 }}>
                {systemStatus ? `${systemStatus.healthy_services}/${systemStatus.services}` : '-'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge 
                badgeContent={alertsData?.alert_summary.active_count || 0} 
                color="error"
              >
                <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              </Badge>
              <Typography variant="h6">活跃告警</Typography>
              <Typography variant="body1" sx={{ mt: 1 }}>
                {alertsData?.alert_summary.active_count || 0} 个
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 性能指标详情 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Timeline />
              性能指标
            </Typography>
            <IconButton onClick={() => toggleExpand('performance')}>
              {expanded.performance ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>

          {performanceMetrics?.current && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    CPU 使用率
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={performanceMetrics.current.cpu_percent} 
                    sx={{ mt: 1, mb: 1 }}
                  />
                  <Typography variant="body2">
                    {performanceMetrics.current.cpu_percent.toFixed(1)}%
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    内存使用率
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={performanceMetrics.current.memory_percent} 
                    color={performanceMetrics.current.memory_percent > 80 ? 'warning' : 'primary'}
                    sx={{ mt: 1, mb: 1 }}
                  />
                  <Typography variant="body2">
                    {performanceMetrics.current.memory_percent.toFixed(1)}% 
                    ({formatBytes(performanceMetrics.current.memory_used_mb * 1024 * 1024)})
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    磁盘使用率
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={performanceMetrics.current.disk_percent} 
                    color={performanceMetrics.current.disk_percent > 90 ? 'error' : 'primary'}
                    sx={{ mt: 1, mb: 1 }}
                  />
                  <Typography variant="body2">
                    {performanceMetrics.current.disk_percent.toFixed(1)}%
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    平均响应时间
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 1 }}>
                    {performanceMetrics.current.response_time_avg.toFixed(3)}s
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {performanceMetrics.current.requests_per_second.toFixed(1)} req/s
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          )}

          <Collapse in={expanded.performance}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              详细统计
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <Typography variant="body2" color="text.secondary">
                  总请求数
                </Typography>
                <Typography variant="h6">
                  {performanceMetrics?.summary.total_requests?.toLocaleString() || 0}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Typography variant="body2" color="text.secondary">
                  错误数
                </Typography>
                <Typography variant="h6" color="error.main">
                  {performanceMetrics?.summary.total_errors?.toLocaleString() || 0}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Typography variant="body2" color="text.secondary">
                  错误率
                </Typography>
                <Typography variant="h6">
                  {performanceMetrics?.current 
                    ? (performanceMetrics.current.error_rate * 100).toFixed(2) + '%'
                    : '0%'
                  }
                </Typography>
              </Grid>
            </Grid>
          </Collapse>
        </CardContent>
      </Card>

      {/* 性能图表 */}
      {showCharts && performanceMetrics?.history && performanceMetrics.history.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">性能趋势图</Typography>
              <IconButton onClick={() => toggleExpand('charts')}>
                {expanded.charts ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>

            <Collapse in={expanded.charts} timeout="auto" unmountOnExit>
              <Box sx={{ mt: 2, height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceMetrics.history}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                    />
                    <YAxis />
                    <RechartsTooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value: number, name: string) => [
                        `${value.toFixed(2)}${name.includes('percent') ? '%' : name.includes('time') ? 's' : ''}`,
                        name
                      ]}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="cpu_percent" 
                      stroke="#8884d8" 
                      fill="#8884d8" 
                      fillOpacity={0.3}
                      name="CPU使用率"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="memory_percent" 
                      stroke="#82ca9d" 
                      fill="#82ca9d" 
                      fillOpacity={0.3}
                      name="内存使用率"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </Collapse>
          </CardContent>
        </Card>
      )}

      {/* 告警信息 */}
      {alertsData && alertsData.active_alerts.length > 0 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Notifications />
                活跃告警 ({alertsData.active_alerts.length})
              </Typography>
              <IconButton onClick={() => toggleExpand('alerts')}>
                {expanded.alerts ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>

            <Box sx={{ mt: 2 }}>
              {alertsData.active_alerts.slice(0, expanded.alerts ? undefined : 3).map((alert) => (
                <Alert 
                  key={alert.id}
                  severity={getAlertColor(alert.level) as any}
                  sx={{ mb: 1 }}
                  action={
                    <Button 
                      size="small" 
                      onClick={() => resolveAlert(alert.id)}
                    >
                      解决
                    </Button>
                  }
                >
                  <AlertTitle>{alert.title}</AlertTitle>
                  {alert.message}
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    {new Date(alert.timestamp).toLocaleString()} - {alert.service}
                  </Typography>
                </Alert>
              ))}
            </Box>

            {!expanded.alerts && alertsData.active_alerts.length > 3 && (
              <Button 
                onClick={() => toggleExpand('alerts')}
                sx={{ mt: 1 }}
              >
                查看更多 ({alertsData.active_alerts.length - 3} 个)
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SystemMonitorPanel; 