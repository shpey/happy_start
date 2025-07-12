import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  Stack,
  Tooltip,
  Fade,
  Slide
} from '@mui/material';
import {
  Psychology,
  Send,
  History,
  Favorite,
  FavoriteBorder,
  Share,
  Download,
  Delete,
  MoreVert,
  TrendingUp,
  Lightbulb,
  Analytics,
  Visibility,
  School,
  EmojiObjects,
  Assessment,
  Timeline,
  Memory,
  AutoAwesome
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { thinkingService, ThinkingAnalysisRequest, ThinkingAnalysisResponse } from '../services/thinkingService';

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
      id={`thinking-tabpanel-${index}`}
      aria-labelledby={`thinking-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ThinkingAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLoggedIn } = useAuth();
  
  const [currentTab, setCurrentTab] = useState(0);
  const [inputText, setInputText] = useState('');
  const [analysisType, setAnalysisType] = useState<'comprehensive' | 'visual' | 'logical' | 'creative'>('comprehensive');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<ThinkingAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showHistoryDialog, setShowHistoryDialog] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState<any | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);

  // 检查用户登录状态
  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login');
      return;
    }
  }, [isLoggedIn, navigate]);

  // 加载分析历史
  useEffect(() => {
    if (isLoggedIn && user && currentTab === 1) {
      loadAnalysisHistory();
    }
  }, [isLoggedIn, user, currentTab]);

  const loadAnalysisHistory = async () => {
    if (!user) return;
    
    setHistoryLoading(true);
    try {
      const history = await thinkingService.getAnalysisHistory(user.id.toString(), {
        limit: 20,
        offset: 0
      });
      setAnalysisHistory(history);
    } catch (error) {
      console.error('加载分析历史失败:', error);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      setError('请输入要分析的思维内容');
      return;
    }

    if (!user) {
      setError('请先登录');
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const request: ThinkingAnalysisRequest = {
        text: inputText,
        analysis_type: analysisType,
        save_result: true,
        user_id: user.id.toString()
      };

      const result = await thinkingService.analyzeThinking(request);
      
      if (result.success) {
        setAnalysisResult(result);
        // 如果当前在历史页面，刷新历史记录
        if (currentTab === 1) {
          loadAnalysisHistory();
        }
      } else {
        setError(result.error || '分析失败');
      }
    } catch (error: any) {
      setError(error.message || '分析过程中发生错误');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleHistoryItemClick = (historyItem: any) => {
    setSelectedHistory(historyItem);
    setShowHistoryDialog(true);
  };

  const handleToggleFavorite = async (analysisId: string, isFavorited: boolean) => {
    try {
      await thinkingService.toggleFavorite(analysisId, !isFavorited);
      loadAnalysisHistory();
    } catch (error) {
      console.error('收藏操作失败:', error);
    }
  };

  const handleDeleteAnalysis = async (analysisId: string) => {
    if (!window.confirm('确定要删除这个分析记录吗？')) {
      return;
    }

    try {
      await thinkingService.deleteAnalysis(analysisId);
      loadAnalysisHistory();
    } catch (error) {
      console.error('删除分析失败:', error);
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, historyItem: any) => {
    event.stopPropagation();
    setMenuAnchorEl(event.currentTarget);
    setSelectedHistory(historyItem);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setSelectedHistory(null);
  };

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    const { results, thinking_summary } = analysisResult;
    const scores = thinking_summary.thinking_scores || {};

    return (
      <Fade in>
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            🧠 思维分析结果
          </Typography>
          
          {/* 主导思维风格 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                主导思维风格: {thinking_summary.dominant_thinking_style}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                平衡指数: {(thinking_summary.balance_index * 100).toFixed(1)}%
              </Typography>
              
              {/* 思维分数 */}
              <Box sx={{ mt: 2 }}>
                {Object.entries(scores).map(([style, score]) => (
                  <Box key={style} sx={{ mb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2">{style}</Typography>
                      <Typography variant="body2">{(score * 100).toFixed(1)}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={score * 100}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: style === thinking_summary.dominant_thinking_style ? 'primary.main' : 'secondary.main'
                        }
                      }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>

          {/* 详细分析结果 */}
          <Grid container spacing={3}>
            {results.visual_thinking && (
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      <Visibility sx={{ mr: 1 }} />
                      形象思维
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      分数: {(results.visual_thinking.score * 100).toFixed(1)}%
                    </Typography>
                    
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>关键概念:</Typography>
                    <Box sx={{ mt: 1 }}>
                      {results.visual_thinking.concepts.map((concept, index) => (
                        <Chip key={index} label={concept} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                      ))}
                    </Box>
                    
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>联想词汇:</Typography>
                    <Box sx={{ mt: 1 }}>
                      {results.visual_thinking.associations.map((association, index) => (
                        <Chip key={index} label={association} size="small" variant="outlined" sx={{ mr: 0.5, mb: 0.5 }} />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {results.logical_thinking && (
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      <Assessment sx={{ mr: 1 }} />
                      逻辑思维
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      分数: {(results.logical_thinking.score * 100).toFixed(1)}%
                    </Typography>
                    
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>推理步骤:</Typography>
                    <List dense>
                      {results.logical_thinking.reasoning_steps.map((step, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon>
                            <Typography variant="body2" color="primary">{index + 1}.</Typography>
                          </ListItemIcon>
                          <ListItemText primary={step} primaryTypographyProps={{ variant: 'body2' }} />
                        </ListItem>
                      ))}
                    </List>
                    
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>结论:</Typography>
                    <Box sx={{ mt: 1 }}>
                      {results.logical_thinking.conclusions.map((conclusion, index) => (
                        <Chip key={index} label={conclusion} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {results.creative_thinking && (
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      <EmojiObjects sx={{ mr: 1 }} />
                      创造思维
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      分数: {(results.creative_thinking.score * 100).toFixed(1)}%
                    </Typography>
                    
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>创新点:</Typography>
                    <List dense>
                      {results.creative_thinking.innovations.map((innovation, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon>
                            <AutoAwesome color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={innovation} primaryTypographyProps={{ variant: 'body2' }} />
                        </ListItem>
                      ))}
                    </List>
                    
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>可能性:</Typography>
                    <Box sx={{ mt: 1 }}>
                      {results.creative_thinking.possibilities.map((possibility, index) => (
                        <Chip key={index} label={possibility} size="small" variant="outlined" sx={{ mr: 0.5, mb: 0.5 }} />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>

          {/* 洞察建议 */}
          {thinking_summary.insights && thinking_summary.insights.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  <Lightbulb sx={{ mr: 1 }} />
                  洞察建议
                </Typography>
                <List>
                  {thinking_summary.insights.map((insight, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Typography variant="body2" color="primary">💡</Typography>
                      </ListItemIcon>
                      <ListItemText primary={insight} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
        </Paper>
      </Fade>
    );
  };

  const renderHistoryItem = (item: any) => (
    <Card 
      key={item.id} 
      sx={{ 
        mb: 2, 
        cursor: 'pointer',
        '&:hover': { 
          boxShadow: 3,
          transform: 'translateY(-2px)',
          transition: 'all 0.2s'
        }
      }}
      onClick={() => handleHistoryItemClick(item)}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body1" noWrap sx={{ mb: 1 }}>
              {item.input_text}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Chip 
                label={item.thinking_summary.dominant_thinking_style} 
                size="small" 
                color="primary"
              />
              <Chip 
                label={`${(item.thinking_summary.balance_index * 100).toFixed(1)}%`} 
                size="small" 
                variant="outlined"
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              {new Date(item.created_at).toLocaleDateString('zh-CN')}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleToggleFavorite(item.id, item.is_favorited);
              }}
            >
              {item.is_favorited ? <Favorite color="error" /> : <FavoriteBorder />}
            </IconButton>
            <IconButton
              size="small"
              onClick={(e) => handleMenuClick(e, item)}
            >
              <MoreVert />
            </IconButton>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (!isLoggedIn) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="warning">
          请先登录以使用思维分析功能。
          <Button onClick={() => navigate('/login')} sx={{ ml: 2 }}>
            去登录
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
        <Psychology sx={{ mr: 2, color: 'primary.main' }} />
        思维分析
      </Typography>

      {/* 标签页 */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange} aria-label="思维分析标签">
          <Tab label="开始分析" />
          <Tab label="历史记录" />
          <Tab label="统计趋势" />
        </Tabs>
      </Paper>

      {/* 分析页面 */}
      <TabPanel value={currentTab} index={0}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            请输入您想要分析的思维内容
          </Typography>
          
          <TextField
            fullWidth
            multiline
            rows={4}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="请描述您的想法、问题或思考过程..."
            sx={{ mb: 3 }}
          />

          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button
              variant={analysisType === 'comprehensive' ? 'contained' : 'outlined'}
              onClick={() => setAnalysisType('comprehensive')}
            >
              综合分析
            </Button>
            <Button
              variant={analysisType === 'visual' ? 'contained' : 'outlined'}
              onClick={() => setAnalysisType('visual')}
            >
              形象思维
            </Button>
            <Button
              variant={analysisType === 'logical' ? 'contained' : 'outlined'}
              onClick={() => setAnalysisType('logical')}
            >
              逻辑思维
            </Button>
            <Button
              variant={analysisType === 'creative' ? 'contained' : 'outlined'}
              onClick={() => setAnalysisType('creative')}
            >
              创造思维
            </Button>
          </Box>

          <Button
            variant="contained"
            size="large"
            onClick={handleAnalyze}
            disabled={isLoading || !inputText.trim()}
            startIcon={isLoading ? <CircularProgress size={20} /> : <Send />}
          >
            {isLoading ? '分析中...' : '开始分析'}
          </Button>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {renderAnalysisResult()}
        </Paper>
      </TabPanel>

      {/* 历史记录页面 */}
      <TabPanel value={currentTab} index={1}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            分析历史记录
          </Typography>
          
          {historyLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : analysisHistory.length === 0 ? (
            <Alert severity="info">
              还没有分析记录。开始您的第一次思维分析吧！
            </Alert>
          ) : (
            <Box>
              {analysisHistory.map(renderHistoryItem)}
            </Box>
          )}
        </Paper>
      </TabPanel>

      {/* 统计趋势页面 */}
      <TabPanel value={currentTab} index={2}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            思维发展趋势
          </Typography>
          <Alert severity="info">
            统计功能正在开发中，敬请期待...
          </Alert>
        </Paper>
      </TabPanel>

      {/* 历史详情对话框 */}
      <Dialog
        open={showHistoryDialog}
        onClose={() => setShowHistoryDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>分析详情</DialogTitle>
        <DialogContent>
          {selectedHistory && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                分析内容:
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {selectedHistory.input_text}
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom>
                分析结果:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip 
                  label={`主导风格: ${selectedHistory.thinking_summary.dominant_thinking_style}`} 
                  color="primary"
                />
                <Chip 
                  label={`平衡指数: ${(selectedHistory.thinking_summary.balance_index * 100).toFixed(1)}%`} 
                  variant="outlined"
                />
              </Box>
              
              {selectedHistory.thinking_summary.thinking_scores && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    思维分数:
                  </Typography>
                  {Object.entries(selectedHistory.thinking_summary.thinking_scores).map(([style, score]) => (
                    <Box key={style} sx={{ mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2">{style}</Typography>
                        <Typography variant="body2">{((score as number) * 100).toFixed(1)}%</Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={(score as number) * 100}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistoryDialog(false)}>关闭</Button>
        </DialogActions>
      </Dialog>

      {/* 菜单 */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          handleMenuClose();
          if (selectedHistory) {
            handleToggleFavorite(selectedHistory.id, selectedHistory.is_favorited);
          }
        }}>
          <ListItemIcon>
            {selectedHistory?.is_favorited ? <Favorite /> : <FavoriteBorder />}
          </ListItemIcon>
          <ListItemText>
            {selectedHistory?.is_favorited ? '取消收藏' : '收藏'}
          </ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          handleMenuClose();
          // TODO: 实现分享功能
        }}>
          <ListItemIcon>
            <Share />
          </ListItemIcon>
          <ListItemText>分享</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          handleMenuClose();
          // TODO: 实现导出功能
        }}>
          <ListItemIcon>
            <Download />
          </ListItemIcon>
          <ListItemText>导出</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          handleMenuClose();
          if (selectedHistory) {
            handleDeleteAnalysis(selectedHistory.id);
          }
        }}>
          <ListItemIcon>
            <Delete />
          </ListItemIcon>
          <ListItemText>删除</ListItemText>
        </MenuItem>
      </Menu>
    </Container>
  );
};

export default ThinkingAnalysisPage; 