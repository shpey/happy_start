import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Button,
  Fab,
  Tooltip,
  Breadcrumbs,
  Link,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  NavigateNext,
  Insights,
  ShowChart,
  Timeline,
  Dashboard,
  FileDownload,
  Settings,
  Add
} from '@mui/icons-material';
import AdvancedCharts from '../components/Visualization/AdvancedCharts';
import RealTimeCharts from '../components/Visualization/RealTimeCharts';
import CustomDashboard from '../components/Visualization/CustomDashboard';
import DataExportEnhanced from '../components/Visualization/DataExportEnhanced';
import { useAuth } from '../contexts/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`visualization-tabpanel-${index}`}
      aria-labelledby={`visualization-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AdvancedVisualizationPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user } = useAuth();

  // 状态管理
  const [currentTab, setCurrentTab] = useState(0);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [selectedChartData, setSelectedChartData] = useState<any>(null);

  // 引用
  const chartRefs = useRef<React.RefObject<any>[]>([]);

  // Tab变化处理
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  // 生成示例数据
  const generateSampleData = () => {
    return {
      heatmapData: {
        matrix: Array.from({ length: 8 }, () => 
          Array.from({ length: 12 }, () => Math.random() * 100)
        )
      },
      networkData: {
        nodes: [
          { id: 0, label: '用户分析', size: 15, color: '#E91E63' },
          { id: 1, label: '思维模式', size: 12, color: '#2196F3' },
          { id: 2, label: '系统性能', size: 10, color: '#4CAF50' },
          { id: 3, label: '协作数据', size: 8, color: '#FF9800' },
          { id: 4, label: '知识图谱', size: 14, color: '#9C27B0' },
          { id: 5, label: '实时监控', size: 11, color: '#00BCD4' }
        ],
        links: [
          { source: 0, target: 1, weight: 3 },
          { source: 1, target: 2, weight: 2 },
          { source: 2, target: 3, weight: 4 },
          { source: 3, target: 4, weight: 2 },
          { source: 4, target: 5, weight: 3 },
          { source: 0, target: 4, weight: 1 }
        ]
      },
      timelineData: {
        events: [
          { title: '系统上线', date: '2024-01-15', color: '#4CAF50' },
          { title: 'AI功能集成', date: '2024-03-20', color: '#2196F3' },
          { title: '数据分析优化', date: '2024-06-10', color: '#FF9800' },
          { title: '可视化升级', date: '2024-09-15', color: '#E91E63' },
          { title: '性能提升', date: '2024-11-01', color: '#9C27B0' }
        ]
      }
    };
  };

  const sampleData = generateSampleData();

  return (
    <Box sx={{ width: '100%' }}>
      {/* 面包屑导航 */}
      <Breadcrumbs separator={<NavigateNext fontSize="small" />} sx={{ mb: 2 }}>
        <Link underline="hover" color="inherit" href="/">
          首页
        </Link>
        <Link underline="hover" color="inherit" href="/dashboard">
          数据仪表板
        </Link>
        <Typography color="text.primary">高级可视化</Typography>
      </Breadcrumbs>

      {/* 页面标题 */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h4" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Insights color="primary" />
          高级数据可视化
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            startIcon={<FileDownload />}
            onClick={() => setShowExportDialog(true)}
            variant="outlined"
          >
            导出数据
          </Button>
          <Button
            startIcon={<Settings />}
            variant="outlined"
          >
            可视化设置
          </Button>
        </Box>
      </Box>

      {/* 主要内容 */}
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={currentTab} 
            onChange={handleTabChange}
            variant={isMobile ? 'scrollable' : 'standard'}
            scrollButtons="auto"
          >
            <Tab 
              label="高级图表" 
              icon={<ShowChart />}
              iconPosition="start"
            />
            <Tab 
              label="实时监控" 
              icon={<Timeline />}
              iconPosition="start"
            />
            <Tab 
              label="自定义仪表板" 
              icon={<Dashboard />}
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {/* 高级图表标签页 */}
        <TabPanel value={currentTab} index={0}>
          <Grid container spacing={3}>
            {/* 热力图 */}
            <Grid item xs={12} lg={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    用户活跃度热力图
                  </Typography>
                  <AdvancedCharts
                    config={{
                      type: 'heatmap',
                      data: sampleData.heatmapData,
                      width: isMobile ? 300 : 500,
                      height: 300
                    }}
                    title="24小时活跃度分布"
                    onExport={(format) => {
                      console.log('导出热力图:', format);
                      setSelectedChartData(sampleData.heatmapData);
                      setShowExportDialog(true);
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* 网络图 */}
            <Grid item xs={12} lg={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    功能关联网络图
                  </Typography>
                  <AdvancedCharts
                    config={{
                      type: 'network',
                      data: sampleData.networkData,
                      width: isMobile ? 300 : 500,
                      height: 300
                    }}
                    title="系统功能关联分析"
                    onExport={(format) => {
                      console.log('导出网络图:', format);
                      setSelectedChartData(sampleData.networkData);
                      setShowExportDialog(true);
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* 时间线图 */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    项目发展时间线
                  </Typography>
                  <AdvancedCharts
                    config={{
                      type: 'timeline',
                      data: sampleData.timelineData,
                      width: isMobile ? 300 : 800,
                      height: 200
                    }}
                    title="系统发展历程"
                    onExport={(format) => {
                      console.log('导出时间线:', format);
                      setSelectedChartData(sampleData.timelineData);
                      setShowExportDialog(true);
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* 图表说明 */}
            <Grid item xs={12}>
              <Card sx={{ bgcolor: 'background.default' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    图表功能说明
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="primary" gutterBottom>
                          热力图
                        </Typography>
                        <Typography variant="body2">
                          展示数据密度和分布模式，适用于时间序列分析、相关性分析等场景。
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="secondary" gutterBottom>
                          网络图
                        </Typography>
                        <Typography variant="body2">
                          显示节点间的关系和连接强度，适用于社交网络分析、系统架构展示等。
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="success.main" gutterBottom>
                          时间线
                        </Typography>
                        <Typography variant="body2">
                          按时间顺序展示事件和里程碑，适用于项目进展、历史回顾等场景。
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 实时监控标签页 */}
        <TabPanel value={currentTab} index={1}>
          <Grid container spacing={3}>
            {/* 系统性能监控 */}
            <Grid item xs={12} lg={6}>
              <RealTimeCharts
                title="系统性能实时监控"
                dataSource="mock"
                updateInterval={2000}
                maxDataPoints={30}
                chartType="area"
                metrics={['CPU使用率', '内存使用率', '磁盘IO']}
                onDataUpdate={(data) => {
                  console.log('系统性能数据更新:', data.length);
                }}
              />
            </Grid>

            {/* 用户活动监控 */}
            <Grid item xs={12} lg={6}>
              <RealTimeCharts
                title="用户活动实时监控"
                dataSource="mock"
                updateInterval={3000}
                maxDataPoints={50}
                chartType="line"
                metrics={['在线用户数', '新增用户', '活跃会话']}
                onDataUpdate={(data) => {
                  console.log('用户活动数据更新:', data.length);
                }}
              />
            </Grid>

            {/* 业务指标监控 */}
            <Grid item xs={12}>
              <RealTimeCharts
                title="核心业务指标监控"
                dataSource="mock"
                updateInterval={5000}
                maxDataPoints={40}
                chartType="line"
                metrics={['思维分析次数', '协作会话数', '知识图谱查询', '响应时间']}
                onDataUpdate={(data) => {
                  console.log('业务指标数据更新:', data.length);
                }}
              />
            </Grid>

            {/* 监控说明 */}
            <Grid item xs={12}>
              <Card sx={{ bgcolor: 'info.main', color: 'info.contrastText' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    实时监控特性
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    <Box>
                      <Typography variant="subtitle2">🔄 自动刷新</Typography>
                      <Typography variant="body2">支持1-10秒间隔的自动数据更新</Typography>
                    </Box>
                    <Box>
                      <Typography variant="subtitle2">📊 多种数据源</Typography>
                      <Typography variant="body2">支持WebSocket、REST API和模拟数据</Typography>
                    </Box>
                    <Box>
                      <Typography variant="subtitle2">⚡ 高性能</Typography>
                      <Typography variant="body2">优化的数据处理和渲染性能</Typography>
                    </Box>
                    <Box>
                      <Typography variant="subtitle2">🎛️ 可定制</Typography>
                      <Typography variant="body2">灵活的指标选择和显示配置</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 自定义仪表板标签页 */}
        <TabPanel value={currentTab} index={2}>
          <CustomDashboard
            userId={user?.id?.toString()}
            readOnly={false}
            onLayoutChange={(layout) => {
              console.log('仪表板布局更新:', layout);
            }}
          />
        </TabPanel>
      </Box>

      {/* 导出对话框 */}
      <DataExportEnhanced
        open={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        data={selectedChartData}
        chartRefs={chartRefs.current}
        title="高级可视化数据导出"
        onExportComplete={(task) => {
          console.log('导出完成:', task);
        }}
      />

      {/* 浮动操作按钮 */}
      <Tooltip title="添加新图表">
        <Fab
          color="primary"
          sx={{ position: 'fixed', bottom: 24, right: 24 }}
          onClick={() => {
            // 根据当前标签页执行不同操作
            if (currentTab === 2) {
              // 自定义仪表板页面，这个功能已在CustomDashboard中实现
              return;
            }
            // 其他页面可以添加新图表的逻辑
            console.log('添加新图表');
          }}
        >
          <Add />
        </Fab>
      </Tooltip>
    </Box>
  );
};

export default AdvancedVisualizationPage; 