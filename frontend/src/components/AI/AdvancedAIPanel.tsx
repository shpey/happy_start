import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  CircularProgress,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Fade,
  Slide,
  useTheme
} from '@mui/material';
import {
  Psychology,
  AutoAwesome,
  Analytics,
  TrendingUp,
  Lightbulb,
  Memory,
  Speed,
  ExpandMore,
  Send,
  Clear,
  Save,
  Share,
  Refresh,
  Settings,
  BarChart,
  PieChart,
  Timeline,
  Stars,
  CheckCircle,
  Error as ErrorIcon,
  Warning,
  Info
} from '@mui/icons-material';
import { Line, Radar, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  RadialLinearScale,
  BarElement
} from 'chart.js';

// 注册 Chart.js 组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  RadialLinearScale,
  BarElement
);

interface AIModel {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  capabilities: string[];
  status: 'available' | 'unavailable' | 'loading';
  confidence: number;
}

interface AnalysisResult {
  model_name: string;
  thinking_style: string;
  confidence: number;
  cognitive_patterns: Record<string, number>;
  creativity_score: number;
  logic_score: number;
  intuition_score: number;
  analysis: Record<string, any>;
  suggestions: string[];
  reasoning?: string;
  timestamp: string;
}

interface AdvancedAIPanelProps {
  onAnalysisComplete?: (result: AnalysisResult) => void;
  initialText?: string;
}

const AdvancedAIPanel: React.FC<AdvancedAIPanelProps> = ({
  onAnalysisComplete,
  initialText = ''
}) => {
  const theme = useTheme();
  const [inputText, setInputText] = useState(initialText);
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResult[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [modelStatus, setModelStatus] = useState<Record<string, any>>({});

  const availableModels: AIModel[] = [
    {
      id: 'gpt-4',
      name: 'GPT-4 Turbo',
      description: '最先进的大语言模型，擅长复杂推理和创意生成',
      icon: <AutoAwesome />,
      capabilities: ['深度分析', '创意生成', '逻辑推理', '多语言支持'],
      status: 'available',
      confidence: 0.95
    },
    {
      id: 'claude',
      name: 'Claude 3 Opus',
      description: 'Anthropic的旗舰模型，注重安全性和准确性',
      icon: <Psychology />,
      capabilities: ['安全分析', '伦理推理', '长文本处理', '细致分析'],
      status: 'available',
      confidence: 0.90
    },
    {
      id: 'gemini',
      name: 'Gemini Pro',
      description: 'Google的多模态AI模型，支持文本和图像',
      icon: <Memory />,
      capabilities: ['多模态分析', '代码理解', '科学推理', '实时信息'],
      status: 'available',
      confidence: 0.85
    },
    {
      id: 'local',
      name: '本地模型',
      description: '本地部署的开源模型，快速且私密',
      icon: <Speed />,
      capabilities: ['快速分析', '隐私保护', '离线运行', '基础分析'],
      status: 'available',
      confidence: 0.70
    }
  ];

  // 获取模型状态
  useEffect(() => {
    fetchModelStatus();
  }, []);

  const fetchModelStatus = async () => {
    try {
      const response = await fetch('/api/v1/ai/status');
      const status = await response.json();
      setModelStatus(status);
    } catch (error) {
      console.error('获取模型状态失败:', error);
    }
  };

  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      setError('请输入要分析的文本');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/ai/analyze/advanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          model_name: selectedModel,
          context: {
            timestamp: new Date().toISOString(),
            user_preferences: {}
          }
        }),
      });

      if (!response.ok) {
        throw new Error('分析请求失败');
      }

      const result = await response.json();
      setAnalysisResult(result);
      setAnalysisHistory(prev => [result, ...prev.slice(0, 9)]); // 保留最近10次分析
      
      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }

    } catch (error) {
      setError(error instanceof Error ? error.message : '分析失败');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const renderModelSelector = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <Settings sx={{ mr: 1 }} />
          AI模型选择
        </Typography>
        <Grid container spacing={2}>
          {availableModels.map((model) => (
            <Grid item xs={12} sm={6} md={3} key={model.id}>
              <Card
                sx={{
                  cursor: 'pointer',
                  border: selectedModel === model.id ? 2 : 1,
                  borderColor: selectedModel === model.id 
                    ? theme.palette.primary.main 
                    : theme.palette.divider,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 3
                  }
                }}
                onClick={() => setSelectedModel(model.id)}
              >
                <CardContent sx={{ p: 2 }}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Avatar 
                      sx={{ 
                        mr: 1, 
                        bgcolor: selectedModel === model.id 
                          ? theme.palette.primary.main 
                          : theme.palette.grey[400],
                        width: 32,
                        height: 32
                      }}
                    >
                      {model.icon}
                    </Avatar>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {model.name}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" display="block" mb={1}>
                    {model.description}
                  </Typography>
                  <Box display="flex" gap={0.5} flexWrap="wrap">
                    {model.capabilities.slice(0, 2).map((cap) => (
                      <Chip 
                        key={cap} 
                        label={cap} 
                        size="small" 
                        variant="outlined"
                        sx={{ fontSize: '0.65rem' }}
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );

  const renderInputSection = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <Psychology sx={{ mr: 1 }} />
          思维文本输入
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={6}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="请输入您想要分析的思维内容..."
          variant="outlined"
          sx={{ mb: 2 }}
        />
        <Box display="flex" gap={1} alignItems="center">
          <Button
            variant="contained"
            onClick={handleAnalyze}
            disabled={isAnalyzing || !inputText.trim()}
            startIcon={isAnalyzing ? <CircularProgress size={20} /> : <Send />}
            sx={{ minWidth: 120 }}
          >
            {isAnalyzing ? '分析中...' : '开始分析'}
          </Button>
          <Button
            variant="outlined"
            onClick={() => {
              setInputText('');
              setError(null);
            }}
            startIcon={<Clear />}
          >
            清空
          </Button>
          <Tooltip title="字符统计">
            <Chip 
              label={`${inputText.length} 字符`} 
              variant="outlined" 
              size="small" 
            />
          </Tooltip>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </CardContent>
    </Card>
  );

  const renderAnalysisResults = () => {
    if (!analysisResult) return null;

    const cognitiveData = {
      labels: ['逻辑思维', '创意思维', '直觉思维', '分析思维'],
      datasets: [
        {
          label: '认知能力',
          data: [
            analysisResult.logic_score * 100,
            analysisResult.creativity_score * 100,
            analysisResult.intuition_score * 100,
            (analysisResult.cognitive_patterns.analysis || 0) * 100
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderColor: 'rgba(99, 102, 241, 1)',
          borderWidth: 2,
        },
      ],
    };

    const scoreData = {
      labels: ['创造力', '逻辑性', '直觉性'],
      datasets: [
        {
          label: '评分',
          data: [
            analysisResult.creativity_score * 100,
            analysisResult.logic_score * 100,
            analysisResult.intuition_score * 100
          ],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 205, 86, 0.6)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 205, 86, 1)'
          ],
          borderWidth: 1,
        },
      ],
    };

    return (
      <Fade in>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <BarChart sx={{ mr: 1 }} />
              分析结果
            </Typography>
            
            <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
              <Tab label="概览" />
              <Tab label="详细分析" />
              <Tab label="可视化" />
              <Tab label="建议" />
            </Tabs>

            {activeTab === 0 && (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h4" color="primary" gutterBottom>
                      {analysisResult.thinking_style}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      主导思维风格
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={analysisResult.confidence * 100}
                      sx={{ mt: 2 }}
                    />
                    <Typography variant="caption" display="block" mt={1}>
                      置信度: {(analysisResult.confidence * 100).toFixed(1)}%
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      认知得分
                    </Typography>
                    <Box mb={1}>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">创造力</Typography>
                        <Typography variant="body2">{(analysisResult.creativity_score * 100).toFixed(0)}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={analysisResult.creativity_score * 100}
                        color="secondary"
                      />
                    </Box>
                    <Box mb={1}>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">逻辑性</Typography>
                        <Typography variant="body2">{(analysisResult.logic_score * 100).toFixed(0)}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={analysisResult.logic_score * 100}
                        color="primary"
                      />
                    </Box>
                    <Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">直觉性</Typography>
                        <Typography variant="body2">{(analysisResult.intuition_score * 100).toFixed(0)}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={analysisResult.intuition_score * 100}
                        color="success"
                      />
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            )}

            {activeTab === 1 && (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  详细分析报告
                </Typography>
                <Paper sx={{ p: 2, mb: 2 }}>
                  <Typography variant="body1" paragraph>
                    {analysisResult.reasoning || '详细的分析推理过程...'}
                  </Typography>
                </Paper>
                
                <Typography variant="subtitle1" gutterBottom>
                  认知模式分析
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(analysisResult.cognitive_patterns).map(([pattern, score]) => (
                    <Grid item xs={6} sm={3} key={pattern}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h6" color="primary">
                          {(score * 100).toFixed(0)}%
                        </Typography>
                        <Typography variant="caption" textTransform="capitalize">
                          {pattern}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}

            {activeTab === 2 && (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    认知能力雷达图
                  </Typography>
                  <Box height={300}>
                    <Radar 
                      data={cognitiveData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          r: {
                            beginAtZero: true,
                            max: 100
                          }
                        }
                      }}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    思维得分分布
                  </Typography>
                  <Box height={300}>
                    <Bar 
                      data={scoreData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          y: {
                            beginAtZero: true,
                            max: 100
                          }
                        }
                      }}
                    />
                  </Box>
                </Grid>
              </Grid>
            )}

            {activeTab === 3 && (
              <Box>
                <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <Lightbulb sx={{ mr: 1 }} />
                  个性化建议
                </Typography>
                <List>
                  {analysisResult.suggestions.map((suggestion, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary={suggestion} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </CardContent>
        </Card>
      </Fade>
    );
  };

  const renderHistoryPanel = () => {
    if (analysisHistory.length === 0) return null;

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <Timeline sx={{ mr: 1 }} />
            分析历史
          </Typography>
          <List>
            {analysisHistory.map((result, index) => (
              <ListItem 
                key={index}
                sx={{ 
                  border: 1, 
                  borderColor: 'divider', 
                  borderRadius: 2, 
                  mb: 1,
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'action.hover' }
                }}
                onClick={() => setAnalysisResult(result)}
              >
                <ListItemIcon>
                  <Avatar sx={{ width: 32, height: 32 }}>
                    {result.model_name[0]}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={`${result.thinking_style} (${result.model_name})`}
                  secondary={`置信度: ${(result.confidence * 100).toFixed(1)}% - ${new Date(result.timestamp).toLocaleString()}`}
                />
                <Chip 
                  label={`${(result.confidence * 100).toFixed(0)}%`}
                  size="small"
                  color={result.confidence > 0.8 ? 'success' : result.confidence > 0.6 ? 'warning' : 'default'}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      {renderModelSelector()}
      {renderInputSection()}
      {renderAnalysisResults()}
      {renderHistoryPanel()}
    </Box>
  );
};

export default AdvancedAIPanel; 