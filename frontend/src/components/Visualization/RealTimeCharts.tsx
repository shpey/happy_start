import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Switch,
  FormControlLabel,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  useTheme
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Refresh,
  Speed,
  Timeline,
  ShowChart,
  Stop,
  Wifi,
  WifiOff
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
);

interface RealTimeData {
  timestamp: number;
  value: number;
  label?: string;
  category?: string;
}

interface RealTimeChartsProps {
  title?: string;
  dataSource: 'websocket' | 'api' | 'mock';
  updateInterval?: number;
  maxDataPoints?: number;
  chartType?: 'line' | 'area' | 'bar';
  metrics?: string[];
  onDataUpdate?: (data: RealTimeData[]) => void;
}

interface ConnectionStatus {
  connected: boolean;
  lastUpdate: Date | null;
  errorCount: number;
  latency: number;
}

const RealTimeCharts: React.FC<RealTimeChartsProps> = ({
  title = '实时数据监控',
  dataSource = 'mock',
  updateInterval = 2000,
  maxDataPoints = 50,
  chartType = 'line',
  metrics = ['CPU使用率', '内存使用率', '网络流量'],
  onDataUpdate
}) => {
  const theme = useTheme();
  
  // 状态管理
  const [isRunning, setIsRunning] = useState(false);
  const [data, setData] = useState<Map<string, RealTimeData[]>>(new Map());
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    connected: false,
    lastUpdate: null,
    errorCount: 0,
    latency: 0
  });
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(metrics.slice(0, 3));
  const [currentInterval, setCurrentInterval] = useState(updateInterval);
  const [autoScale, setAutoScale] = useState(true);

  // 引用
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const lastUpdateRef = useRef<number>(Date.now());

  // 启动实时数据流
  const startRealTimeUpdates = useCallback(() => {
    if (isRunning) return;

    setIsRunning(true);
    setConnectionStatus(prev => ({ ...prev, connected: true, errorCount: 0 }));

    if (dataSource === 'websocket') {
      // WebSocket连接
      try {
        const wsUrl = `ws://localhost:8000/ws/realtime-data`;
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          setConnectionStatus(prev => ({ ...prev, connected: true }));
        };

        wsRef.current.onmessage = (event) => {
          try {
            const newData = JSON.parse(event.data);
            handleDataUpdate(newData);
          } catch (error) {
            console.error('WebSocket数据解析错误:', error);
          }
        };

        wsRef.current.onerror = () => {
          setConnectionStatus(prev => ({ 
            ...prev, 
            connected: false, 
            errorCount: prev.errorCount + 1 
          }));
        };

        wsRef.current.onclose = () => {
          setConnectionStatus(prev => ({ ...prev, connected: false }));
          if (isRunning) {
            // 尝试重连
            setTimeout(() => startRealTimeUpdates(), 5000);
          }
        };
      } catch (error) {
        console.error('WebSocket连接失败:', error);
        setConnectionStatus(prev => ({ 
          ...prev, 
          connected: false, 
          errorCount: prev.errorCount + 1 
        }));
      }
    } else {
      // 定时器更新
      intervalRef.current = setInterval(() => {
        if (dataSource === 'api') {
          fetchAPIData();
        } else {
          generateMockData();
        }
      }, currentInterval);
    }
  }, [isRunning, dataSource, currentInterval]);

  // 停止实时数据流
  const stopRealTimeUpdates = useCallback(() => {
    setIsRunning(false);
    setConnectionStatus(prev => ({ ...prev, connected: false }));

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // 处理数据更新
  const handleDataUpdate = useCallback((newData: any) => {
    const timestamp = Date.now();
    const latency = timestamp - lastUpdateRef.current;
    lastUpdateRef.current = timestamp;

    setConnectionStatus(prev => ({
      ...prev,
      lastUpdate: new Date(),
      latency
    }));

    setData(prevData => {
      const updatedData = new Map(prevData);

      selectedMetrics.forEach(metric => {
        const currentData = updatedData.get(metric) || [];
        const value = newData[metric] || generateRandomValue(metric);
        
        const dataPoint: RealTimeData = {
          timestamp,
          value,
          label: new Date(timestamp).toLocaleTimeString(),
          category: metric
        };

        const newMetricData = [...currentData, dataPoint];
        
        // 限制数据点数量
        if (newMetricData.length > maxDataPoints) {
          newMetricData.shift();
        }

        updatedData.set(metric, newMetricData);
      });

      // 触发回调
      if (onDataUpdate) {
        const allData = Array.from(updatedData.values()).flat();
        onDataUpdate(allData);
      }

      return updatedData;
    });
  }, [selectedMetrics, maxDataPoints, onDataUpdate]);

  // 获取API数据
  const fetchAPIData = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/monitoring/metrics?realtime=true');
      const apiData = await response.json();
      handleDataUpdate(apiData);
    } catch (error) {
      console.error('API数据获取失败:', error);
      setConnectionStatus(prev => ({ 
        ...prev, 
        errorCount: prev.errorCount + 1 
      }));
    }
  }, [handleDataUpdate]);

  // 生成模拟数据
  const generateMockData = useCallback(() => {
    const mockData: any = {};
    selectedMetrics.forEach(metric => {
      mockData[metric] = generateRandomValue(metric);
    });
    handleDataUpdate(mockData);
  }, [selectedMetrics, handleDataUpdate]);

  // 清空数据
  const clearData = useCallback(() => {
    setData(new Map());
  }, []);

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      stopRealTimeUpdates();
    };
  }, [stopRealTimeUpdates]);

  // 准备图表数据
  const chartData = {
    labels: Array.from(data.values())[0]?.map(d => d.label) || [],
    datasets: selectedMetrics.map((metric, index) => {
      const metricData = data.get(metric) || [];
      const colors = [
        theme.palette.primary.main,
        theme.palette.secondary.main,
        theme.palette.success.main,
        theme.palette.warning.main,
        theme.palette.error.main
      ];
      
      return {
        label: metric,
        data: metricData.map(d => d.value),
        borderColor: colors[index % colors.length],
        backgroundColor: chartType === 'area' ? 
          colors[index % colors.length] + '20' : 
          colors[index % colors.length],
        fill: chartType === 'area',
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 4
      };
    })
  };

  // 图表配置
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: isRunning ? 300 : 0
    },
    interaction: {
      intersect: false,
      mode: 'index' as const
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20
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
      x: {
        display: true,
        grid: {
          color: theme.palette.divider
        },
        ticks: {
          color: theme.palette.text.secondary,
          maxTicksLimit: 10
        }
      },
      y: {
        display: true,
        beginAtZero: true,
        suggestedMax: autoScale ? undefined : 100,
        grid: {
          color: theme.palette.divider
        },
        ticks: {
          color: theme.palette.text.secondary
        }
      }
    }
  };

  return (
    <Card>
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ShowChart color="primary" />
            {title}
            <Chip
              icon={connectionStatus.connected ? <Wifi /> : <WifiOff />}
              label={connectionStatus.connected ? '已连接' : '未连接'}
              color={connectionStatus.connected ? 'success' : 'error'}
              size="small"
            />
          </Box>
        }
        action={
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>更新间隔</InputLabel>
              <Select
                value={currentInterval}
                onChange={(e) => setCurrentInterval(e.target.value as number)}
                label="更新间隔"
                disabled={isRunning}
              >
                <MenuItem value={1000}>1秒</MenuItem>
                <MenuItem value={2000}>2秒</MenuItem>
                <MenuItem value={5000}>5秒</MenuItem>
                <MenuItem value={10000}>10秒</MenuItem>
              </Select>
            </FormControl>

            <Tooltip title={isRunning ? "暂停" : "开始"}>
              <IconButton
                onClick={isRunning ? stopRealTimeUpdates : startRealTimeUpdates}
                color={isRunning ? "error" : "success"}
              >
                {isRunning ? <Pause /> : <PlayArrow />}
              </IconButton>
            </Tooltip>

            <Tooltip title="清空数据">
              <IconButton onClick={clearData} disabled={isRunning}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        }
      />
      
      <CardContent>
        {/* 控制面板 */}
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>监控指标</InputLabel>
            <Select
              multiple
              value={selectedMetrics}
              onChange={(e) => setSelectedMetrics(e.target.value as string[])}
              label="监控指标"
              disabled={isRunning}
            >
              {metrics.map(metric => (
                <MenuItem key={metric} value={metric}>{metric}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControlLabel
            control={
              <Switch
                checked={autoScale}
                onChange={(e) => setAutoScale(e.target.checked)}
              />
            }
            label="自动缩放"
          />

          {connectionStatus.connected && (
            <Chip
              icon={<Speed />}
              label={`延迟: ${connectionStatus.latency}ms`}
              size="small"
              color="info"
            />
          )}

          {connectionStatus.errorCount > 0 && (
            <Chip
              label={`错误: ${connectionStatus.errorCount}`}
              size="small"
              color="error"
            />
          )}
        </Box>

        {/* 连接状态警告 */}
        {!connectionStatus.connected && isRunning && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            连接已断开，正在尝试重连...
          </Alert>
        )}

        {/* 图表区域 */}
        <Box sx={{ height: 400, position: 'relative' }}>
          {selectedMetrics.length > 0 ? (
            <Line data={chartData} options={chartOptions} />
          ) : (
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'text.secondary'
              }}
            >
              请选择至少一个监控指标
            </Box>
          )}
        </Box>

        {/* 状态信息 */}
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <Typography variant="caption" color="text.secondary">
            数据源: {dataSource === 'websocket' ? 'WebSocket' : dataSource === 'api' ? 'REST API' : '模拟数据'}
          </Typography>
          
          <Typography variant="caption" color="text.secondary">
            最后更新: {connectionStatus.lastUpdate?.toLocaleTimeString() || '无'}
          </Typography>
          
          <Typography variant="caption" color="text.secondary">
            数据点: {Math.max(...Array.from(data.values()).map(arr => arr.length), 0)}/{maxDataPoints}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

// 工具函数：生成随机值
function generateRandomValue(metric: string): number {
  const baseValues: { [key: string]: number } = {
    'CPU使用率': 30,
    '内存使用率': 60,
    '网络流量': 20,
    '磁盘IO': 15,
    '响应时间': 200,
    '请求数': 100,
    '错误率': 2
  };

  const base = baseValues[metric] || 50;
  const variation = base * 0.3; // 30%的变化范围
  
  return Math.max(0, Math.min(100, base + (Math.random() - 0.5) * variation * 2));
}

export default RealTimeCharts;
export type { RealTimeData, RealTimeChartsProps }; 