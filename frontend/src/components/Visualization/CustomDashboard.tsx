import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Fab,
  Menu,
  ListItemIcon,
  ListItemText,
  Switch,
  FormControlLabel,
  Alert,
  Tooltip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Save,
  Restore,
  Settings,
  DragIndicator,
  GridView,
  ViewModule,
  ShowChart,
  Assessment,
  Psychology,
  Speed,
  Timeline,
  BubbleChart,
  Share,
  Download
} from '@mui/icons-material';
import AdvancedCharts from './AdvancedCharts';
import RealTimeCharts from './RealTimeCharts';
import { useLocalStorage } from '../../hooks/useLocalStorage';

// 组件类型定义
interface DashboardWidget {
  id: string;
  type: 'chart' | 'realtime' | 'metric' | 'text';
  title: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  config: any;
  visible: boolean;
}

interface DashboardLayout {
  id: string;
  name: string;
  widgets: DashboardWidget[];
  createdAt: Date;
  updatedAt: Date;
}

interface CustomDashboardProps {
  userId?: string;
  defaultLayout?: DashboardLayout;
  onLayoutChange?: (layout: DashboardLayout) => void;
  readOnly?: boolean;
}

// 预定义的组件模板
const WIDGET_TEMPLATES = {
  chart: {
    type: 'chart' as const,
    title: '数据图表',
    size: { width: 400, height: 300 },
    config: {
      chartType: 'line',
      dataSource: 'analytics',
      metric: 'user_activity'
    }
  },
  realtime: {
    type: 'realtime' as const,
    title: '实时监控',
    size: { width: 500, height: 350 },
    config: {
      dataSource: 'mock',
      updateInterval: 2000,
      metrics: ['CPU使用率', '内存使用率']
    }
  },
  metric: {
    type: 'metric' as const,
    title: '关键指标',
    size: { width: 250, height: 150 },
    config: {
      metric: 'total_users',
      format: 'number',
      color: 'primary'
    }
  },
  text: {
    type: 'text' as const,
    title: '文本组件',
    size: { width: 300, height: 200 },
    config: {
      content: '这是一个文本组件',
      fontSize: 16,
      align: 'left'
    }
  }
};

const CustomDashboard: React.FC<CustomDashboardProps> = ({
  userId,
  defaultLayout,
  onLayoutChange,
  readOnly = false
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // 状态管理
  const [currentLayout, setCurrentLayout] = useLocalStorage<DashboardLayout>(
    `dashboard-layout-${userId}`,
    defaultLayout || {
      id: 'default',
      name: '默认仪表板',
      widgets: [],
      createdAt: new Date(),
      updatedAt: new Date()
    }
  );
  
  const [editMode, setEditMode] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);
  const [showWidgetDialog, setShowWidgetDialog] = useState(false);
  const [showLayoutDialog, setShowLayoutDialog] = useState(false);
  const [draggedWidget, setDraggedWidget] = useState<string | null>(null);
  const [addMenuAnchor, setAddMenuAnchor] = useState<HTMLElement | null>(null);
  
  // 表单状态
  const [layoutName, setLayoutName] = useState(currentLayout.name);
  const [editingWidget, setEditingWidget] = useState<Partial<DashboardWidget> | null>(null);

  // 网格配置
  const GRID_SIZE = 20;
  const SNAP_TO_GRID = true;

  // 添加新组件
  const addWidget = useCallback((templateType: keyof typeof WIDGET_TEMPLATES) => {
    const template = WIDGET_TEMPLATES[templateType];
    const newWidget: DashboardWidget = {
      id: `widget-${Date.now()}`,
      ...template,
      position: { x: 20, y: 20 },
      visible: true
    };

    setCurrentLayout(prev => ({
      ...prev,
      widgets: [...prev.widgets, newWidget],
      updatedAt: new Date()
    }));

    setAddMenuAnchor(null);
  }, [setCurrentLayout]);

  // 更新组件
  const updateWidget = useCallback((widgetId: string, updates: Partial<DashboardWidget>) => {
    setCurrentLayout(prev => ({
      ...prev,
      widgets: prev.widgets.map(widget =>
        widget.id === widgetId ? { ...widget, ...updates } : widget
      ),
      updatedAt: new Date()
    }));
  }, [setCurrentLayout]);

  // 删除组件
  const deleteWidget = useCallback((widgetId: string) => {
    setCurrentLayout(prev => ({
      ...prev,
      widgets: prev.widgets.filter(widget => widget.id !== widgetId),
      updatedAt: new Date()
    }));
  }, [setCurrentLayout]);

  // 处理拖拽
  const handleDragStart = useCallback((widgetId: string) => {
    if (!editMode) return;
    setDraggedWidget(widgetId);
  }, [editMode]);

  const handleDragEnd = useCallback((event: React.DragEvent) => {
    if (!draggedWidget || !editMode) return;

    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const gridX = SNAP_TO_GRID ? Math.round(x / GRID_SIZE) * GRID_SIZE : x;
    const gridY = SNAP_TO_GRID ? Math.round(y / GRID_SIZE) * GRID_SIZE : y;

    updateWidget(draggedWidget, {
      position: { x: Math.max(0, gridX), y: Math.max(0, gridY) }
    });

    setDraggedWidget(null);
  }, [draggedWidget, editMode, updateWidget]);

  // 保存布局
  const saveLayout = useCallback(() => {
    const updatedLayout = {
      ...currentLayout,
      name: layoutName,
      updatedAt: new Date()
    };
    
    setCurrentLayout(updatedLayout);
    
    if (onLayoutChange) {
      onLayoutChange(updatedLayout);
    }
    
    setShowLayoutDialog(false);
  }, [currentLayout, layoutName, setCurrentLayout, onLayoutChange]);

  // 渲染组件
  const renderWidget = useCallback((widget: DashboardWidget) => {
    if (!widget.visible) return null;

    const isSelected = selectedWidget === widget.id;
    
    return (
      <Box
        key={widget.id}
        sx={{
          position: 'absolute',
          left: widget.position.x,
          top: widget.position.y,
          width: widget.size.width,
          height: widget.size.height,
          cursor: editMode ? 'move' : 'default',
          border: isSelected && editMode ? 2 : 0,
          borderColor: 'primary.main',
          borderStyle: 'dashed',
          borderRadius: 1
        }}
        draggable={editMode}
        onDragStart={() => handleDragStart(widget.id)}
        onClick={() => editMode && setSelectedWidget(widget.id)}
      >
        <Card sx={{ height: '100%', position: 'relative' }}>
          {editMode && (
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                right: 0,
                zIndex: 10,
                display: 'flex',
                gap: 0.5,
                p: 0.5
              }}
            >
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingWidget(widget);
                  setShowWidgetDialog(true);
                }}
              >
                <Edit fontSize="small" />
              </IconButton>
              <IconButton
                size="small"
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteWidget(widget.id);
                }}
              >
                <Delete fontSize="small" />
              </IconButton>
            </Box>
          )}
          
          <CardContent sx={{ height: '100%', p: 1 }}>
            {renderWidgetContent(widget)}
          </CardContent>
        </Card>
      </Box>
    );
  }, [editMode, selectedWidget, handleDragStart, deleteWidget]);

  // 渲染组件内容
  const renderWidgetContent = (widget: DashboardWidget) => {
    switch (widget.type) {
      case 'chart':
        return (
          <AdvancedCharts
            config={{
              type: widget.config.chartType || 'line',
              data: generateChartData(widget.config.metric),
              width: widget.size.width - 20,
              height: widget.size.height - 60
            }}
            title={widget.title}
            interactive={!editMode}
          />
        );
        
      case 'realtime':
        return (
          <RealTimeCharts
            title={widget.title}
            dataSource={widget.config.dataSource}
            updateInterval={widget.config.updateInterval}
            metrics={widget.config.metrics}
          />
        );
        
      case 'metric':
        return (
          <Box sx={{ textAlign: 'center', pt: 2 }}>
            <Typography variant="h4" color={widget.config.color || 'primary'}>
              {generateMetricValue(widget.config.metric)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {widget.title}
            </Typography>
          </Box>
        );
        
      case 'text':
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              {widget.title}
            </Typography>
            <Typography
              variant="body1"
              sx={{
                fontSize: widget.config.fontSize || 16,
                textAlign: widget.config.align || 'left'
              }}
            >
              {widget.config.content || ''}
            </Typography>
          </Box>
        );
        
      default:
        return (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'text.secondary'
            }}
          >
            未知组件类型
          </Box>
        );
    }
  };

  return (
    <Box sx={{ position: 'relative', minHeight: '600px' }}>
      {/* 工具栏 */}
      <Paper
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          p: 2,
          mb: 2,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6">
            {currentLayout.name}
          </Typography>
          <Chip
            label={editMode ? '编辑模式' : '查看模式'}
            color={editMode ? 'warning' : 'success'}
            size="small"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {!readOnly && (
            <>
              <FormControlLabel
                control={
                  <Switch
                    checked={editMode}
                    onChange={(e) => setEditMode(e.target.checked)}
                  />
                }
                label="编辑模式"
              />

              <Button
                startIcon={<Settings />}
                onClick={() => setShowLayoutDialog(true)}
                variant="outlined"
                size="small"
              >
                布局设置
              </Button>

              <Button
                startIcon={<Share />}
                variant="outlined"
                size="small"
              >
                分享
              </Button>
            </>
          )}

          <Button
            startIcon={<Download />}
            variant="outlined"
            size="small"
          >
            导出
          </Button>
        </Box>
      </Paper>

      {/* 仪表板画布 */}
      <Box
        sx={{
          position: 'relative',
          minHeight: 500,
          border: editMode ? 1 : 0,
          borderColor: 'divider',
          borderStyle: 'dashed',
          borderRadius: 1,
          backgroundColor: editMode ? 'action.hover' : 'transparent'
        }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDragEnd}
      >
        {currentLayout.widgets.map(renderWidget)}

        {/* 空状态 */}
        {currentLayout.widgets.length === 0 && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: 400,
              color: 'text.secondary'
            }}
          >
            <GridView sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
            <Typography variant="h6" gutterBottom>
              空白仪表板
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              开始添加组件来自定义您的仪表板
            </Typography>
            {!readOnly && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={(e) => setAddMenuAnchor(e.currentTarget)}
              >
                添加组件
              </Button>
            )}
          </Box>
        )}
      </Box>

      {/* 添加组件按钮 */}
      {!readOnly && editMode && currentLayout.widgets.length > 0 && (
        <Fab
          color="primary"
          sx={{ position: 'fixed', bottom: 24, right: 24 }}
          onClick={(e) => setAddMenuAnchor(e.currentTarget)}
        >
          <Add />
        </Fab>
      )}

      {/* 添加组件菜单 */}
      <Menu
        anchorEl={addMenuAnchor}
        open={Boolean(addMenuAnchor)}
        onClose={() => setAddMenuAnchor(null)}
      >
        {Object.entries(WIDGET_TEMPLATES).map(([key, template]) => (
          <MenuItem
            key={key}
            onClick={() => addWidget(key as keyof typeof WIDGET_TEMPLATES)}
          >
            <ListItemIcon>
              {getWidgetIcon(template.type)}
            </ListItemIcon>
            <ListItemText>{template.title}</ListItemText>
          </MenuItem>
        ))}
      </Menu>

      {/* 组件编辑对话框 */}
      <Dialog
        open={showWidgetDialog}
        onClose={() => setShowWidgetDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>编辑组件</DialogTitle>
        <DialogContent>
          {editingWidget && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <TextField
                label="组件标题"
                value={editingWidget.title || ''}
                onChange={(e) => setEditingWidget(prev => ({ ...prev, title: e.target.value }))}
                fullWidth
              />
              
              <FormControl fullWidth>
                <InputLabel>组件类型</InputLabel>
                <Select
                  value={editingWidget.type || ''}
                  onChange={(e) => setEditingWidget(prev => ({ ...prev, type: e.target.value as any }))}
                  label="组件类型"
                >
                  <MenuItem value="chart">数据图表</MenuItem>
                  <MenuItem value="realtime">实时监控</MenuItem>
                  <MenuItem value="metric">关键指标</MenuItem>
                  <MenuItem value="text">文本组件</MenuItem>
                </Select>
              </FormControl>

              {/* 根据组件类型显示不同的配置选项 */}
              {renderWidgetConfigForm(editingWidget)}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWidgetDialog(false)}>
            取消
          </Button>
          <Button
            onClick={() => {
              if (editingWidget && editingWidget.id) {
                updateWidget(editingWidget.id, editingWidget);
              }
              setShowWidgetDialog(false);
              setEditingWidget(null);
            }}
            variant="contained"
          >
            保存
          </Button>
        </DialogActions>
      </Dialog>

      {/* 布局设置对话框 */}
      <Dialog
        open={showLayoutDialog}
        onClose={() => setShowLayoutDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>布局设置</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="布局名称"
              value={layoutName}
              onChange={(e) => setLayoutName(e.target.value)}
              fullWidth
            />

            <Alert severity="info">
              布局将自动保存到本地存储
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowLayoutDialog(false)}>
            取消
          </Button>
          <Button onClick={saveLayout} variant="contained">
            保存
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// 工具函数
function getWidgetIcon(type: string) {
  switch (type) {
    case 'chart': return <ShowChart />;
    case 'realtime': return <Timeline />;
    case 'metric': return <Assessment />;
    case 'text': return <Edit />;
    default: return <ViewModule />;
  }
}

function renderWidgetConfigForm(widget: Partial<DashboardWidget>) {
  // 这里可以根据组件类型渲染不同的配置表单
  return (
    <Alert severity="info">
      详细配置功能正在开发中...
    </Alert>
  );
}

function generateChartData(metric: string) {
  // 生成模拟图表数据
  const data = [];
  for (let i = 0; i < 10; i++) {
    data.push(Math.random() * 100);
  }
  return { values: data };
}

function generateMetricValue(metric: string): string {
  const values = {
    'total_users': '1,234',
    'active_sessions': '456',
    'revenue': '$12,345',
    'conversion_rate': '3.4%'
  };
  return values[metric as keyof typeof values] || '0';
}

export default CustomDashboard;
export type { DashboardWidget, DashboardLayout, CustomDashboardProps }; 