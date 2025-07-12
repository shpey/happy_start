/**
 * 错误边界组件
 * 捕获React组件错误，提供优雅的错误处理和恢复机制
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Container,
  Divider,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ErrorOutline,
  Refresh,
  Home,
  BugReport,
  ExpandMore,
  ContentCopy,
  Warning
} from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // 更新state，下次渲染将显示错误UI
    return {
      hasError: true,
      error,
      errorId: `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 记录错误信息
    this.setState({
      error,
      errorInfo
    });

    // 调用外部错误处理函数
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // 发送错误到监控服务（模拟）
    this.logErrorToService(error, errorInfo);
  }

  logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      errorId: this.state.errorId
    };

    // 这里可以发送到实际的错误监控服务
    console.error('🚨 Error Boundary Caught Error:', errorData);
    
    // 存储到localStorage作为备份
    try {
      const existingErrors = JSON.parse(localStorage.getItem('app_errors') || '[]');
      existingErrors.unshift(errorData);
      localStorage.setItem('app_errors', JSON.stringify(existingErrors.slice(0, 10))); // 保持最新10个错误
    } catch (e) {
      console.warn('Failed to store error to localStorage:', e);
    }
  };

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleReportBug = () => {
    const errorData = {
      errorId: this.state.errorId,
      message: this.state.error?.message || '',
      stack: this.state.error?.stack || '',
      timestamp: new Date().toISOString(),
      url: window.location.href
    };

    // 创建GitHub issue链接或发送到bug报告系统
    const githubIssueUrl = `https://github.com/your-repo/issues/new?title=Bug Report: ${encodeURIComponent(this.state.error?.message || 'Unknown Error')}&body=${encodeURIComponent(`Error ID: ${this.state.errorId}\n\nError Details:\n${JSON.stringify(errorData, null, 2)}`)}`;
    
    window.open(githubIssueUrl, '_blank');
  };

  copyErrorInfo = () => {
    const errorText = `Error ID: ${this.state.errorId}
Message: ${this.state.error?.message || 'Unknown'}
Stack: ${this.state.error?.stack || 'No stack trace'}
Component Stack: ${this.state.errorInfo?.componentStack || 'No component stack'}
Timestamp: ${new Date().toISOString()}
URL: ${window.location.href}`;

    navigator.clipboard.writeText(errorText).then(() => {
      // 这里可以显示一个小提示
      console.log('Error info copied to clipboard');
    });
  };

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认错误UI
      return (
        <Container maxWidth="md" sx={{ py: 8 }}>
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            {/* 错误图标和标题 */}
            <Box sx={{ mb: 3 }}>
              <ErrorOutline sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
              <Typography variant="h4" gutterBottom color="error">
                糟糕，出现了一些问题！
              </Typography>
              <Typography variant="h6" color="text.secondary" paragraph>
                应用程序遇到了意外错误，但我们正在努力修复它。
              </Typography>
            </Box>

            {/* 错误ID */}
            <Alert severity="warning" sx={{ mb: 3, textAlign: 'left' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="subtitle2">错误ID</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {this.state.errorId}
                  </Typography>
                </Box>
                <Tooltip title="复制错误信息">
                  <IconButton size="small" onClick={this.copyErrorInfo}>
                    <ContentCopy fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Alert>

            {/* 操作按钮 */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 3 }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={this.handleRetry}
                size="large"
              >
                重试
              </Button>
              <Button
                variant="outlined"
                startIcon={<Home />}
                onClick={this.handleGoHome}
                size="large"
              >
                返回首页
              </Button>
              <Button
                variant="text"
                startIcon={<BugReport />}
                onClick={this.handleReportBug}
                size="large"
                color="warning"
              >
                报告问题
              </Button>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {/* 技术详情（可折叠） */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning fontSize="small" />
                  技术详情
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ textAlign: 'left' }}>
                <Typography variant="subtitle2" gutterBottom>
                  错误消息
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'error.main' }}>
                    {this.state.error?.message || '未知错误'}
                  </Typography>
                </Paper>

                {this.state.error?.stack && (
                  <>
                    <Typography variant="subtitle2" gutterBottom>
                      堆栈跟踪
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                        {this.state.error.stack}
                      </Typography>
                    </Paper>
                  </>
                )}

                {this.state.errorInfo?.componentStack && (
                  <>
                    <Typography variant="subtitle2" gutterBottom>
                      组件堆栈
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                        {this.state.errorInfo.componentStack}
                      </Typography>
                    </Paper>
                  </>
                )}
              </AccordionDetails>
            </Accordion>

            {/* 用户建议 */}
            <Box sx={{ mt: 3, textAlign: 'left' }}>
              <Typography variant="h6" gutterBottom>
                🔧 你可以尝试：
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                <Typography component="li" variant="body2" paragraph>
                  刷新页面或点击"重试"按钮
                </Typography>
                <Typography component="li" variant="body2" paragraph>
                  清除浏览器缓存和Cookie
                </Typography>
                <Typography component="li" variant="body2" paragraph>
                  检查网络连接是否正常
                </Typography>
                <Typography component="li" variant="body2" paragraph>
                  如果问题持续存在，请报告给我们的技术团队
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Container>
      );
    }

    return this.props.children;
  }
}

// 简化版错误边界，用于小组件
export const SimpleErrorBoundary: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({ 
  children, 
  fallback 
}) => {
  return (
    <ErrorBoundary 
      fallback={fallback || (
        <Alert severity="error" sx={{ m: 2 }}>
          <Typography variant="body2">
            组件加载失败，请刷新页面重试
          </Typography>
          <Button size="small" onClick={() => window.location.reload()} sx={{ mt: 1 }}>
            刷新页面
          </Button>
        </Alert>
      )}
    >
      {children}
    </ErrorBoundary>
  );
};

export default ErrorBoundary; 