import React, { useState, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  LinearProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  FileDownload,
  PictureAsPdf,
  TableChart,
  Image,
  Settings,
  Preview,
  Share,
  Email,
  Schedule,
  Close,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';

interface ExportOptions {
  format: 'pdf' | 'excel' | 'csv' | 'png' | 'svg' | 'json';
  includeCharts: boolean;
  includeData: boolean;
  includeMetadata: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
  selectedMetrics?: string[];
  customFileName?: string;
  pageFormat?: 'A4' | 'A3' | 'Letter';
  orientation?: 'portrait' | 'landscape';
  quality?: 'low' | 'medium' | 'high';
}

interface ExportTask {
  id: string;
  name: string;
  format: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  downloadUrl?: string;
  error?: string;
  createdAt: Date;
}

interface DataExportEnhancedProps {
  open: boolean;
  onClose: () => void;
  data?: any;
  chartRefs?: React.RefObject<any>[];
  title?: string;
  onExportComplete?: (task: ExportTask) => void;
}

const DataExportEnhanced: React.FC<DataExportEnhancedProps> = ({
  open,
  onClose,
  data,
  chartRefs = [],
  title = '数据导出',
  onExportComplete
}) => {
  const theme = useTheme();
  
  // 状态管理
  const [currentStep, setCurrentStep] = useState(0);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'pdf',
    includeCharts: true,
    includeData: true,
    includeMetadata: true,
    pageFormat: 'A4',
    orientation: 'portrait',
    quality: 'high'
  });
  const [exportTasks, setExportTasks] = useState<ExportTask[]>([]);
  const [isExporting, setIsExporting] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);

  // 可用的导出格式
  const exportFormats = [
    { value: 'pdf', label: 'PDF报告', icon: <PictureAsPdf />, description: '完整的可视化报告' },
    { value: 'excel', label: 'Excel表格', icon: <TableChart />, description: '可编辑的数据表格' },
    { value: 'csv', label: 'CSV文件', icon: <TableChart />, description: '纯数据文件' },
    { value: 'png', label: 'PNG图片', icon: <Image />, description: '高质量图片' },
    { value: 'svg', label: 'SVG矢量图', icon: <Image />, description: '可缩放矢量图形' },
    { value: 'json', label: 'JSON数据', icon: <Settings />, description: '结构化数据文件' }
  ];

  // 可用的指标列表
  const availableMetrics = [
    '用户活跃度',
    '思维分析统计',
    '系统性能指标',
    '协作数据',
    '增长趋势',
    '认知能力评估'
  ];

  // 导出步骤
  const steps = ['选择格式', '配置选项', '预览确认', '开始导出'];

  // 更新导出选项
  const updateOptions = (updates: Partial<ExportOptions>) => {
    setExportOptions(prev => ({ ...prev, ...updates }));
  };

  // 生成预览
  const generatePreview = async () => {
    try {
      // 模拟预览数据生成
      const preview = {
        pageCount: exportOptions.format === 'pdf' ? 5 : 1,
        dataPoints: data ? Object.keys(data).length : 0,
        chartCount: chartRefs.length,
        estimatedSize: calculateEstimatedSize(),
        format: exportOptions.format
      };
      
      setPreviewData(preview);
    } catch (error) {
      console.error('预览生成失败:', error);
    }
  };

  // 计算预估文件大小
  const calculateEstimatedSize = (): string => {
    let sizeKB = 100; // 基础大小
    
    if (exportOptions.includeCharts) sizeKB += chartRefs.length * 200;
    if (exportOptions.includeData && data) sizeKB += Object.keys(data).length * 2;
    if (exportOptions.quality === 'high') sizeKB *= 1.5;
    
    if (sizeKB > 1024) {
      return `${(sizeKB / 1024).toFixed(1)}MB`;
    }
    return `${Math.round(sizeKB)}KB`;
  };

  // 开始导出
  const startExport = async () => {
    setIsExporting(true);
    
    const newTask: ExportTask = {
      id: `export-${Date.now()}`,
      name: exportOptions.customFileName || `${title}-${new Date().toISOString().split('T')[0]}`,
      format: exportOptions.format,
      status: 'processing',
      progress: 0,
      createdAt: new Date()
    };

    setExportTasks(prev => [newTask, ...prev]);

    try {
      // 模拟导出过程
      await processExport(newTask);
    } catch (error) {
      updateTaskStatus(newTask.id, 'failed', 100, undefined, error.message);
    } finally {
      setIsExporting(false);
    }
  };

  // 处理导出
  const processExport = async (task: ExportTask) => {
    // 模拟导出进度
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 200));
      updateTaskStatus(task.id, 'processing', progress);
    }

    // 根据格式执行不同的导出逻辑
    let downloadUrl = '';
    
    switch (exportOptions.format) {
      case 'pdf':
        downloadUrl = await exportToPDF();
        break;
      case 'excel':
        downloadUrl = await exportToExcel();
        break;
      case 'csv':
        downloadUrl = await exportToCSV();
        break;
      case 'png':
        downloadUrl = await exportToPNG();
        break;
      case 'svg':
        downloadUrl = await exportToSVG();
        break;
      case 'json':
        downloadUrl = await exportToJSON();
        break;
    }

    updateTaskStatus(task.id, 'completed', 100, downloadUrl);
    
    if (onExportComplete) {
      onExportComplete({ ...task, status: 'completed', downloadUrl });
    }
  };

  // 更新任务状态
  const updateTaskStatus = (
    taskId: string, 
    status: ExportTask['status'], 
    progress: number, 
    downloadUrl?: string, 
    error?: string
  ) => {
    setExportTasks(prev => prev.map(task => 
      task.id === taskId 
        ? { ...task, status, progress, downloadUrl, error }
        : task
    ));
  };

  // 导出到PDF
  const exportToPDF = async (): Promise<string> => {
    // 这里应该集成 jspdf 或类似库
    console.log('导出PDF:', exportOptions);
    return 'blob:pdf-url';
  };

  // 导出到Excel
  const exportToExcel = async (): Promise<string> => {
    // 这里应该集成 xlsx 库
    console.log('导出Excel:', exportOptions);
    return 'blob:excel-url';
  };

  // 导出到CSV
  const exportToCSV = async (): Promise<string> => {
    if (!data) return '';
    
    const csvContent = convertToCSV(data);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    return URL.createObjectURL(blob);
  };

  // 导出到PNG
  const exportToPNG = async (): Promise<string> => {
    // 这里应该使用 html2canvas
    console.log('导出PNG:', exportOptions);
    return 'blob:png-url';
  };

  // 导出到SVG
  const exportToSVG = async (): Promise<string> => {
    console.log('导出SVG:', exportOptions);
    return 'blob:svg-url';
  };

  // 导出到JSON
  const exportToJSON = async (): Promise<string> => {
    const jsonData = {
      metadata: {
        title,
        exportDate: new Date().toISOString(),
        options: exportOptions
      },
      data: data || {},
      charts: chartRefs.length > 0 ? 'Chart data would be here' : null
    };
    
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { 
      type: 'application/json' 
    });
    return URL.createObjectURL(blob);
  };

  // 转换为CSV格式
  const convertToCSV = (data: any): string => {
    if (!data || typeof data !== 'object') return '';
    
    const rows: string[][] = [];
    
    // 如果是数组
    if (Array.isArray(data)) {
      if (data.length > 0 && typeof data[0] === 'object') {
        // 对象数组
        const headers = Object.keys(data[0]);
        rows.push(headers);
        
        data.forEach(item => {
          const row = headers.map(header => 
            item[header] !== undefined ? String(item[header]) : ''
          );
          rows.push(row);
        });
      }
    } else {
      // 对象转换
      rows.push(['键', '值']);
      Object.entries(data).forEach(([key, value]) => {
        rows.push([key, String(value)]);
      });
    }
    
    return rows.map(row => 
      row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ).join('\n');
  };

  // 下载文件
  const downloadFile = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 渲染步骤内容
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return renderFormatSelection();
      case 1:
        return renderOptionsConfiguration();
      case 2:
        return renderPreview();
      case 3:
        return renderExportProgress();
      default:
        return null;
    }
  };

  // 格式选择
  const renderFormatSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        选择导出格式
      </Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
        {exportFormats.map(format => (
          <Paper
            key={format.value}
            sx={{
              p: 2,
              cursor: 'pointer',
              border: 2,
              borderColor: exportOptions.format === format.value ? 'primary.main' : 'transparent',
              '&:hover': { borderColor: 'primary.light' }
            }}
            onClick={() => updateOptions({ format: format.value as any })}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              {format.icon}
              <Typography variant="subtitle1" sx={{ ml: 1 }}>
                {format.label}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {format.description}
            </Typography>
          </Paper>
        ))}
      </Box>
    </Box>
  );

  // 选项配置
  const renderOptionsConfiguration = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        配置导出选项
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* 文件名 */}
        <TextField
          label="文件名"
          value={exportOptions.customFileName || ''}
          onChange={(e) => updateOptions({ customFileName: e.target.value })}
          placeholder={`${title}-${new Date().toISOString().split('T')[0]}`}
          fullWidth
        />

        {/* 包含内容 */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            包含内容
          </Typography>
          <FormGroup>
            <FormControlLabel
              control={
                <Checkbox
                  checked={exportOptions.includeCharts}
                  onChange={(e) => updateOptions({ includeCharts: e.target.checked })}
                />
              }
              label="图表和可视化"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={exportOptions.includeData}
                  onChange={(e) => updateOptions({ includeData: e.target.checked })}
                />
              }
              label="原始数据"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={exportOptions.includeMetadata}
                  onChange={(e) => updateOptions({ includeMetadata: e.target.checked })}
                />
              }
              label="元数据信息"
            />
          </FormGroup>
        </Box>

        {/* PDF特定选项 */}
        {exportOptions.format === 'pdf' && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              PDF设置
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>页面格式</InputLabel>
                <Select
                  value={exportOptions.pageFormat}
                  onChange={(e) => updateOptions({ pageFormat: e.target.value as any })}
                  label="页面格式"
                >
                  <MenuItem value="A4">A4</MenuItem>
                  <MenuItem value="A3">A3</MenuItem>
                  <MenuItem value="Letter">Letter</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>方向</InputLabel>
                <Select
                  value={exportOptions.orientation}
                  onChange={(e) => updateOptions({ orientation: e.target.value as any })}
                  label="方向"
                >
                  <MenuItem value="portrait">纵向</MenuItem>
                  <MenuItem value="landscape">横向</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Box>
        )}

        {/* 图片质量选项 */}
        {['png', 'svg'].includes(exportOptions.format) && (
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>图片质量</InputLabel>
            <Select
              value={exportOptions.quality}
              onChange={(e) => updateOptions({ quality: e.target.value as any })}
              label="图片质量"
            >
              <MenuItem value="low">低 (较小文件)</MenuItem>
              <MenuItem value="medium">中等</MenuItem>
              <MenuItem value="high">高 (较大文件)</MenuItem>
            </Select>
          </FormControl>
        )}

        {/* 指标选择 */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            选择指标
          </Typography>
          <FormGroup>
            {availableMetrics.map(metric => (
              <FormControlLabel
                key={metric}
                control={
                  <Checkbox
                    checked={exportOptions.selectedMetrics?.includes(metric) ?? true}
                    onChange={(e) => {
                      const current = exportOptions.selectedMetrics || availableMetrics;
                      const updated = e.target.checked
                        ? [...current, metric]
                        : current.filter(m => m !== metric);
                      updateOptions({ selectedMetrics: updated });
                    }}
                  />
                }
                label={metric}
              />
            ))}
          </FormGroup>
        </Box>
      </Box>
    </Box>
  );

  // 预览
  const renderPreview = () => {
    if (!previewData) {
      generatePreview();
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <LinearProgress sx={{ width: '100%' }} />
        </Box>
      );
    }

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          导出预览
        </Typography>
        
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            导出摘要
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            <Chip label={`格式: ${exportOptions.format.toUpperCase()}`} />
            <Chip label={`预估大小: ${previewData.estimatedSize}`} />
            {previewData.pageCount > 1 && (
              <Chip label={`页数: ${previewData.pageCount}`} />
            )}
            <Chip label={`图表: ${previewData.chartCount}`} />
            <Chip label={`数据点: ${previewData.dataPoints}`} />
          </Box>
          
          <Alert severity="info">
            点击"开始导出"将生成文件并自动下载
          </Alert>
        </Paper>
      </Box>
    );
  };

  // 导出进度
  const renderExportProgress = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        导出进度
      </Typography>
      
      <List>
        {exportTasks.map(task => (
          <React.Fragment key={task.id}>
            <ListItem>
              <ListItemIcon>
                {task.status === 'completed' ? (
                  <CheckCircle color="success" />
                ) : task.status === 'failed' ? (
                  <ErrorIcon color="error" />
                ) : (
                  <Schedule color="primary" />
                )}
              </ListItemIcon>
              <ListItemText
                primary={task.name}
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {task.format.toUpperCase()} - {task.status === 'completed' ? '已完成' : 
                       task.status === 'failed' ? '失败' : '处理中...'}
                    </Typography>
                    {task.status === 'processing' && (
                      <LinearProgress 
                        variant="determinate" 
                        value={task.progress} 
                        sx={{ mt: 1 }}
                      />
                    )}
                    {task.error && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        {task.error}
                      </Alert>
                    )}
                  </Box>
                }
              />
              {task.downloadUrl && (
                <Button
                  startIcon={<FileDownload />}
                  onClick={() => downloadFile(task.downloadUrl!, task.name)}
                  size="small"
                >
                  下载
                </Button>
              )}
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>
      
      {exportTasks.length === 0 && (
        <Alert severity="info">
          没有导出任务
        </Alert>
      )}
    </Box>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {title}
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {/* 步骤指示器 */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            {steps.map((step, index) => (
              <Typography
                key={step}
                variant="body2"
                color={index <= currentStep ? 'primary' : 'text.secondary'}
                sx={{ fontWeight: index === currentStep ? 'bold' : 'normal' }}
              >
                {index + 1}. {step}
              </Typography>
            ))}
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={(currentStep / (steps.length - 1)) * 100} 
          />
        </Box>

        {/* 步骤内容 */}
        {renderStepContent()}
      </DialogContent>
      
      <DialogActions>
        <Button
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
        >
          上一步
        </Button>
        
        {currentStep < steps.length - 1 ? (
          <Button
            onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
            variant="contained"
          >
            下一步
          </Button>
        ) : (
          <Button
            onClick={startExport}
            variant="contained"
            disabled={isExporting}
            startIcon={<FileDownload />}
          >
            {isExporting ? '导出中...' : '开始导出'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default DataExportEnhanced;
export type { ExportOptions, ExportTask, DataExportEnhancedProps }; 