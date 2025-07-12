/**
 * 全局搜索组件
 * 支持跨页面内容搜索、智能过滤和快速导航
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Typography,
  Chip,
  InputAdornment,
  Divider,
  Paper,
  Avatar,
  IconButton
} from '@mui/material';
import {
  Search,
  Psychology,
  AccountTree,
  Groups,
  ViewInAr,
  Dashboard,
  History,
  TrendingUp,
  Close,
  NavigateNext,
  Star,
  Schedule,
  Label,
  FilterList
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useNotification } from './NotificationProvider';
import { useLocalStorage, STORAGE_KEYS } from '../../hooks/useLocalStorage';

interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'page' | 'analysis' | 'knowledge' | 'collaboration' | 'feature';
  path?: string;
  icon: React.ReactElement;
  category: string;
  relevance: number;
  lastAccessed?: Date;
}

interface GlobalSearchProps {
  open: boolean;
  onClose: () => void;
}

const GlobalSearch: React.FC<GlobalSearchProps> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const { success } = useNotification();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [searchHistory, setSearchHistory] = useLocalStorage<string[]>('search_history', []);
  const [recentAnalyses] = useLocalStorage(STORAGE_KEYS.THINKING_HISTORY, []);

  // 搜索数据源
  const searchData: SearchResult[] = [
    // 页面
    {
      id: 'home',
      title: '首页',
      description: '项目概览、快速入口和系统状态',
      type: 'page',
      path: '/',
      icon: <Dashboard />,
      category: '页面',
      relevance: 100
    },
    {
      id: 'thinking',
      title: '思维分析',
      description: 'AI驱动的思维模式分析，支持形象、逻辑、创造思维',
      type: 'page',
      path: '/thinking',
      icon: <Psychology />,
      category: '页面',
      relevance: 95
    },
    {
      id: 'knowledge',
      title: '知识图谱',
      description: '可视化知识关联网络，交互式节点图',
      type: 'page',
      path: '/knowledge',
      icon: <AccountTree />,
      category: '页面',
      relevance: 90
    },
    {
      id: 'collaboration',
      title: '实时协作',
      description: '多用户协作思维空间，实时聊天和分享',
      type: 'page',
      path: '/collaboration',
      icon: <Groups />,
      category: '页面',
      relevance: 85
    },
    {
      id: '3d-space',
      title: '3D思维空间',
      description: '沉浸式三维思维体验，WebXR支持',
      type: 'page',
      path: '/3d-space',
      icon: <ViewInAr />,
      category: '页面',
      relevance: 80
    },
    {
      id: 'dashboard',
      title: '数据仪表板',
      description: '系统统计、性能监控和数据可视化',
      type: 'page',
      path: '/dashboard',
      icon: <TrendingUp />,
      category: '页面',
      relevance: 75
    },

    // 功能
    {
      id: 'thinking-analysis',
      title: '思维分析功能',
      description: '分析深度设置、实时分析模式、结果导出',
      type: 'feature',
      path: '/thinking',
      icon: <Psychology />,
      category: '功能',
      relevance: 90
    },
    {
      id: 'theme-switch',
      title: '主题切换',
      description: '暗黑模式、自定义主题、预设配色方案',
      type: 'feature',
      icon: <Star />,
      category: '功能',
      relevance: 70
    },
    {
      id: 'quick-access',
      title: '快速访问面板',
      description: '速拨菜单、系统状态、历史记录',
      type: 'feature',
      icon: <NavigateNext />,
      category: '功能',
      relevance: 65
    },
    {
      id: 'user-guide',
      title: '用户引导',
      description: '新手指导、功能介绍、使用技巧',
      type: 'feature',
      icon: <Star />,
      category: '功能',
      relevance: 60
    },

    // 分析记录
    ...recentAnalyses.slice(0, 5).map((analysis: any, index: number) => ({
      id: `analysis-${index}`,
      title: `思维分析记录`,
      description: analysis.input?.substring(0, 50) + '...' || '无描述',
      type: 'analysis' as const,
      path: '/thinking',
      icon: <History />,
      category: '历史记录',
      relevance: 50 - index * 5,
      lastAccessed: new Date(analysis.timestamp)
    }))
  ];

  // 搜索过滤逻辑
  const filteredResults = useMemo(() => {
    if (!query) {
      // 没有查询时显示最近访问和推荐
      return searchData
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, 8);
    }

    const normalizedQuery = query.toLowerCase();
    
    return searchData
      .filter(item => {
        const titleMatch = item.title.toLowerCase().includes(normalizedQuery);
        const descMatch = item.description.toLowerCase().includes(normalizedQuery);
        const categoryMatch = item.category.toLowerCase().includes(normalizedQuery);
        
        return titleMatch || descMatch || categoryMatch;
      })
      .map(item => {
        // 计算相关性得分
        let score = 0;
        const titleMatch = item.title.toLowerCase().includes(normalizedQuery);
        const descMatch = item.description.toLowerCase().includes(normalizedQuery);
        
        if (titleMatch) score += 100;
        if (descMatch) score += 50;
        if (item.title.toLowerCase().startsWith(normalizedQuery)) score += 200;
        
        return { ...item, relevance: score };
      })
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 10);
  }, [query, searchData]);

  // 键盘导航
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!open) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => 
            prev < filteredResults.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => 
            prev > 0 ? prev - 1 : filteredResults.length - 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredResults[selectedIndex]) {
            handleResultClick(filteredResults[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, selectedIndex, filteredResults, onClose]);

  // 重置状态
  useEffect(() => {
    if (open) {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [open]);

  const handleResultClick = (result: SearchResult) => {
    // 保存搜索历史
    if (query && !searchHistory.includes(query)) {
      setSearchHistory(prev => [query, ...prev.slice(0, 9)]);
    }

    // 导航
    if (result.path) {
      navigate(result.path);
      success(`已跳转到${result.title}`);
    }

    onClose();
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'page': return 'primary';
      case 'feature': return 'success';
      case 'analysis': return 'warning';
      case 'knowledge': return 'info';
      default: return 'default';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          position: 'fixed',
          top: 100,
          m: 0,
          borderRadius: 3,
          maxHeight: 500
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        pb: 1
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Search />
          <Typography variant="h6">全局搜索</Typography>
        </Box>
        <IconButton onClick={onClose} size="small">
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ pt: 0 }}>
        {/* 搜索输入框 */}
        <TextField
          fullWidth
          placeholder="搜索页面、功能、历史记录..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
            endAdornment: query && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={() => setQuery('')}>
                  <Close />
                </IconButton>
              </InputAdornment>
            )
          }}
          sx={{ mb: 2 }}
        />

        {/* 快捷提示 */}
        {!query && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              快捷键提示
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip 
                size="small" 
                label="↑↓ 导航" 
                variant="outlined"
              />
              <Chip 
                size="small" 
                label="Enter 确认" 
                variant="outlined"
              />
              <Chip 
                size="small" 
                label="Esc 关闭" 
                variant="outlined"
              />
            </Box>
          </Box>
        )}

        {/* 搜索结果 */}
        <List sx={{ maxHeight: 300, overflow: 'auto' }}>
          {filteredResults.length === 0 && query ? (
            <ListItem>
              <ListItemText
                primary="未找到相关结果"
                secondary="尝试使用不同的关键词搜索"
              />
            </ListItem>
          ) : (
            filteredResults.map((result, index) => (
              <ListItemButton
                key={result.id}
                selected={index === selectedIndex}
                onClick={() => handleResultClick(result)}
                sx={{
                  borderRadius: 2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    bgcolor: 'primary.50'
                  }
                }}
              >
                <ListItemIcon>
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: `${getTypeColor(result.type)}.main`
                    }}
                  >
                    {result.icon}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle2">
                        {result.title}
                      </Typography>
                      <Chip
                        label={result.category}
                        size="small"
                        variant="outlined"
                        sx={{ height: 20, fontSize: '10px' }}
                      />
                    </Box>
                  }
                  secondary={result.description}
                />
                {result.lastAccessed && (
                  <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                    <Schedule fontSize="small" />
                    <Typography variant="caption" sx={{ ml: 0.5 }}>
                      {result.lastAccessed.toLocaleDateString()}
                    </Typography>
                  </Box>
                )}
              </ListItemButton>
            ))
          )}
        </List>

        {/* 搜索历史 */}
        {!query && searchHistory.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              最近搜索
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {searchHistory.slice(0, 5).map((term, index) => (
                <Chip
                  key={index}
                  label={term}
                  size="small"
                  onClick={() => setQuery(term)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default GlobalSearch; 