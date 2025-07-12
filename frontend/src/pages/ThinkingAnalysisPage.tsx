import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Chip,
  Avatar,
  LinearProgress,
  Divider,
  Alert,
  Breadcrumbs,
  Link,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Psychology,
  AccountTree,
  Lightbulb,
  NavigateNext,
  Send,
  Clear,
  Download,
  Share,
  History,
  Settings,
  TrendingUp,
  Assessment,
  AutoFixHigh,
  Insights
} from '@mui/icons-material';
import { useNotification, NotificationTemplates } from '../components/common/NotificationProvider';
import LoadingOverlay, { ThinkingLoader } from '../components/common/LoadingOverlay';
import { useLocalStorage, STORAGE_KEYS } from '../hooks/useLocalStorage';
import { useLazyAsync } from '../hooks/useAsync';

interface ThinkingResult {
  type: 'visual' | 'logical' | 'creative';
  score: number;
  analysis: string;
  suggestions: string[];
  keywords: string[];
  confidence: number;
}

interface AnalysisHistory {
  id: string;
  input: string;
  results: ThinkingResult[];
  timestamp: Date;
  duration: number;
}

const ThinkingAnalysisPage: React.FC = () => {
  const [input, setInput] = useState('');
  const [analysisType, setAnalysisType] = useState<'auto' | 'visual' | 'logical' | 'creative'>('auto');
  const [currentTab, setCurrentTab] = useState(0);
  const [results, setResults] = useState<ThinkingResult[]>([]);
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [analysisDepth, setAnalysisDepth] = useState(50);
  
  // 本地存储
  const [analysisHistory, setAnalysisHistory] = useLocalStorage<AnalysisHistory[]>(
    STORAGE_KEYS.THINKING_HISTORY, 
    []
  );

  // 通知系统
  const { success, error, info } = useNotification();

  // 异步分析执行
  const { loading, execute: performAnalysis } = useLazyAsync(async () => {
    if (!input.trim()) {
      error('请输入要分析的内容');
      return;
    }

    info('开始AI思维分析...');
    
    // 模拟AI分析过程
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));
    
    // 模拟分析结果
    const mockResults: ThinkingResult[] = [
      {
        type: 'visual',
        score: 75 + Math.random() * 20,
        analysis: '您的表达中展现出较强的形象思维能力。能够运用具体的场景和画面来阐述抽象概念，这种能力有助于创新设计和艺术创作。',
        suggestions: ['尝试更多的视觉化表达', '结合图像和文字进行思考', '培养空间想象能力'],
        keywords: ['视觉化', '具象思维', '空间感知'],
        confidence: 0.85
      },
      {
        type: 'logical',
        score: 68 + Math.random() * 25,
        analysis: '逻辑思维结构清晰，能够按照合理的逻辑顺序组织思路。建议在分析问题时加强因果关系的梳理。',
        suggestions: ['加强逻辑推理训练', '多进行结构化思考', '培养批判性思维'],
        keywords: ['逻辑推理', '结构化', '因果分析'],
        confidence: 0.78
      },
      {
        type: 'creative',
        score: 82 + Math.random() * 15,
        analysis: '创造思维活跃，善于发散思考和联想。您的想法具有创新性，能够从多个角度思考问题。',
        suggestions: ['保持开放的思维态度', '多进行头脑风暴', '尝试跨领域思考'],
        keywords: ['发散思维', '创新思路', '跨域联想'],
        confidence: 0.92
      }
    ].filter(result => analysisType === 'auto' || result.type === analysisType);

    setResults(mockResults);

    // 保存到历史记录
    const newHistory: AnalysisHistory = {
      id: `analysis_${Date.now()}`,
      input,
      results: mockResults,
      timestamp: new Date(),
      duration: 2000 + Math.random() * 3000
    };

    setAnalysisHistory(prev => [newHistory, ...prev.slice(0, 9)]); // 保持最新10条记录

    // 显示成功通知
    const avgScore = mockResults.reduce((sum, r) => sum + r.score, 0) / mockResults.length;
    success(`分析完成！综合得分: ${avgScore.toFixed(1)}分`, '思维分析');
  });

  const handleAnalysis = useCallback(() => {
    performAnalysis();
  }, [performAnalysis]);

  const handleClear = () => {
    setInput('');
    setResults([]);
  };

  const handleExport = () => {
    if (results.length === 0) {
      error('没有可导出的分析结果');
      return;
    }

    const exportData = {
      input,
      results,
      analysisType,
      timestamp: new Date(),
      analysisDepth
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `思维分析_${new Date().toLocaleDateString()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    success('分析结果已导出');
  };

  const getThinkingTypeColor = (type: string) => {
    switch (type) {
      case 'visual': return '#2196F3';
      case 'logical': return '#FF5722';
      case 'creative': return '#4CAF50';
      default: return '#757575';
    }
  };

  const getThinkingTypeIcon = (type: string) => {
    switch (type) {
      case 'visual': return <Psychology />;
      case 'logical': return <AccountTree />;
      case 'creative': return <Lightbulb />;
      default: return <Assessment />;
    }
  };

  const getThinkingTypeName = (type: string) => {
    switch (type) {
      case 'visual': return '形象思维';
      case 'logical': return '逻辑思维';
      case 'creative': return '创造思维';
      default: return '未知类型';
    }
  };

  return (
    <LoadingOverlay loading={loading} type="thinking" message="AI正在进行深度思维分析...">
      <Box>
        {/* 面包屑导航 */}
        <Breadcrumbs separator={<NavigateNext fontSize="small" />} sx={{ mb: 1 }}>
          <Link underline="hover" color="inherit" href="/">
            首页
          </Link>
          <Typography color="text.primary">思维分析</Typography>
        </Breadcrumbs>

        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology /> AI思维分析
          <Chip label="GPT-4驱动" size="small" color="primary" />
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          运用先进的AI技术分析您的思维模式，识别形象思维、逻辑思维和创造思维的特点
        </Typography>

        <Grid container spacing={3}>
          {/* 输入区域 */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                💭 输入您的想法
              </Typography>

              <TextField
                fullWidth
                multiline
                rows={6}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="请输入您想要分析的内容，可以是：&#10;• 对某个问题的思考过程&#10;• 创意想法或解决方案&#10;• 学习心得或感悟&#10;• 工作中遇到的挑战"
                variant="outlined"
                sx={{ mb: 3 }}
              />

              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>分析类型</InputLabel>
                  <Select
                    value={analysisType}
                    label="分析类型"
                    onChange={(e) => setAnalysisType(e.target.value as any)}
                  >
                    <MenuItem value="auto">智能分析</MenuItem>
                    <MenuItem value="visual">形象思维</MenuItem>
                    <MenuItem value="logical">逻辑思维</MenuItem>
                    <MenuItem value="creative">创造思维</MenuItem>
                  </Select>
                </FormControl>

                <FormControlLabel
                  control={
                    <Switch
                      checked={realTimeMode}
                      onChange={(e) => setRealTimeMode(e.target.checked)}
                    />
                  }
                  label="实时分析"
                />

                <Button
                  variant="contained"
                  startIcon={<Send />}
                  onClick={handleAnalysis}
                  disabled={!input.trim() || loading}
                  sx={{ ml: 'auto' }}
                >
                  开始分析
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Clear />}
                  onClick={handleClear}
                >
                  清空
                </Button>
              </Box>
            </Paper>

            {/* 分析结果 */}
            {results.length > 0 && (
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6">
                    🎯 分析结果
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      startIcon={<Download />}
                      onClick={handleExport}
                    >
                      导出结果
                    </Button>
                    <Button
                      size="small"
                      startIcon={<Share />}
                      onClick={() => info('分享功能开发中...')}
                    >
                      分享
                    </Button>
                  </Box>
                </Box>

                <Grid container spacing={3}>
                  {results.map((result, index) => (
                    <Grid item xs={12} md={4} key={index}>
                      <Card 
                        sx={{ 
                          height: '100%',
                          borderTop: `4px solid ${getThinkingTypeColor(result.type)}`
                        }}
                      >
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <Avatar
                              sx={{
                                bgcolor: getThinkingTypeColor(result.type),
                                mr: 2,
                                width: 48,
                                height: 48
                              }}
                            >
                              {getThinkingTypeIcon(result.type)}
                            </Avatar>
                            <Box>
                              <Typography variant="h6">
                                {getThinkingTypeName(result.type)}
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="h4" color={getThinkingTypeColor(result.type)}>
                                  {result.score.toFixed(0)}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  分
                                </Typography>
                              </Box>
                            </Box>
                          </Box>

                          <LinearProgress
                            variant="determinate"
                            value={result.score}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              mb: 2,
                              backgroundColor: 'grey.200',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: getThinkingTypeColor(result.type)
                              }
                            }}
                          />

                          <Typography variant="body2" paragraph>
                            {result.analysis}
                          </Typography>

                          <Typography variant="subtitle2" gutterBottom>
                            关键词
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            {result.keywords.map((keyword, kidx) => (
                              <Chip
                                key={kidx}
                                label={keyword}
                                size="small"
                                sx={{ mr: 0.5, mb: 0.5 }}
                                variant="outlined"
                              />
                            ))}
                          </Box>

                          <Typography variant="subtitle2" gutterBottom>
                            建议
                          </Typography>
                          <Box component="ul" sx={{ pl: 2, m: 0 }}>
                            {result.suggestions.map((suggestion, sidx) => (
                              <Typography component="li" variant="body2" key={sidx} sx={{ mb: 0.5 }}>
                                {suggestion}
                              </Typography>
                            ))}
                          </Box>
                        </CardContent>

                        <CardActions>
                          <Chip
                            label={`置信度: ${(result.confidence * 100).toFixed(0)}%`}
                            size="small"
                            color={result.confidence > 0.8 ? 'success' : 'default'}
                          />
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            )}
          </Grid>

          {/* 侧边栏 */}
          <Grid item xs={12} md={4}>
            {/* 高级设置 */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Settings /> 分析设置
              </Typography>

              <Typography variant="body2" gutterBottom>
                分析深度
              </Typography>
              <Slider
                value={analysisDepth}
                onChange={(_, value) => setAnalysisDepth(value as number)}
                min={10}
                max={100}
                marks={[
                  { value: 25, label: '快速' },
                  { value: 50, label: '标准' },
                  { value: 75, label: '深度' },
                  { value: 100, label: '专业' }
                ]}
                sx={{ mb: 3 }}
              />

              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="caption">
                  💡 分析深度越高，结果越详细，但耗时会增加
                </Typography>
              </Alert>
            </Paper>

            {/* 分析历史 */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <History /> 分析历史
              </Typography>

              {analysisHistory.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  暂无分析历史
                </Typography>
              ) : (
                <Box>
                  {analysisHistory.slice(0, 5).map((history, index) => (
                    <Box key={history.id} sx={{ mb: 2, pb: 2, borderBottom: index < 4 ? 1 : 0, borderColor: 'divider' }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
                        {history.input.substring(0, 50)}...
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" color="text.secondary">
                          {history.timestamp.toLocaleDateString()}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {history.results.map((result, ridx) => (
                            <Chip
                              key={ridx}
                              label={result.score.toFixed(0)}
                              size="small"
                              sx={{
                                backgroundColor: getThinkingTypeColor(result.type),
                                color: 'white',
                                fontSize: '10px',
                                height: 20
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    </Box>
                  ))}
                  
                  {analysisHistory.length > 5 && (
                    <Button
                      size="small"
                      fullWidth
                      variant="outlined"
                      onClick={() => info('查看完整历史功能开发中...')}
                    >
                      查看全部 ({analysisHistory.length})
                    </Button>
                  )}
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </LoadingOverlay>
  );
};

export default ThinkingAnalysisPage; 