import React, { useState, useEffect } from 'react';
import {
  Box,
  CircularProgress,
  LinearProgress,
  Typography,
  Skeleton,
  Card,
  CardContent,
  Grid,
  Fade,
  useTheme,
  keyframes
} from '@mui/material';
import { Psychology, TrendingUp, Timeline } from '@mui/icons-material';

// 动画定义
const pulseAnimation = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const waveAnimation = keyframes`
  0%, 60%, 100% { transform: initial; }
  30% { transform: translateY(-15px); }
`;

const spinAnimation = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

interface EnhancedLoadingProps {
  type?: 'circular' | 'linear' | 'skeleton' | 'custom' | 'dots';
  size?: 'small' | 'medium' | 'large';
  message?: string;
  progress?: number;
  showProgress?: boolean;
  variant?: 'primary' | 'secondary' | 'success' | 'info';
  fullScreen?: boolean;
  minHeight?: string | number;
}

const EnhancedLoading: React.FC<EnhancedLoadingProps> = ({
  type = 'circular',
  size = 'medium',
  message = '正在加载...',
  progress,
  showProgress = false,
  variant = 'primary',
  fullScreen = false,
  minHeight = 200
}) => {
  const theme = useTheme();
  const [dots, setDots] = useState('');
  const [currentTip, setCurrentTip] = useState(0);

  const loadingTips = [
    '正在分析您的思维模式...',
    '构建知识图谱连接...',
    '优化AI推理结果...',
    '渲染3D思维空间...',
    '同步协作数据...'
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTip(prev => (prev + 1) % loadingTips.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const getSizeConfig = () => {
    switch (size) {
      case 'small':
        return { circularSize: 24, iconSize: 'small', fontSize: '0.875rem' };
      case 'large':
        return { circularSize: 64, iconSize: 'large', fontSize: '1.25rem' };
      default:
        return { circularSize: 40, iconSize: 'medium', fontSize: '1rem' };
    }
  };

  const sizeConfig = getSizeConfig();

  const renderCircularLoading = () => (
    <Box 
      display="flex" 
      flexDirection="column" 
      alignItems="center" 
      gap={2}
      p={3}
    >
      <Box position="relative">
        <CircularProgress
          size={sizeConfig.circularSize}
          variant={progress !== undefined ? 'determinate' : 'indeterminate'}
          value={progress}
          sx={{
            color: theme.palette[variant].main,
            animation: progress === undefined ? `${spinAnimation} 1.4s linear infinite` : 'none'
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
          }}
        >
          <Psychology 
            sx={{ 
              fontSize: sizeConfig.circularSize * 0.4,
              color: theme.palette[variant].main,
              animation: `${pulseAnimation} 2s ease-in-out infinite`
            }} 
          />
        </Box>
      </Box>
      
      <Typography 
        variant="body2" 
        color="text.secondary"
        fontSize={sizeConfig.fontSize}
        textAlign="center"
      >
        {message}{dots}
      </Typography>
      
      {showProgress && progress !== undefined && (
        <Typography variant="caption" color="text.secondary">
          {Math.round(progress)}%
        </Typography>
      )}
    </Box>
  );

  const renderLinearLoading = () => (
    <Box width="100%" p={3}>
      <Typography 
        variant="body2" 
        color="text.secondary"
        mb={2}
        textAlign="center"
      >
        {loadingTips[currentTip]}
      </Typography>
      <LinearProgress
        variant={progress !== undefined ? 'determinate' : 'indeterminate'}
        value={progress}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: theme.palette.grey[200],
          '& .MuiLinearProgress-bar': {
            borderRadius: 4,
            background: `linear-gradient(45deg, ${theme.palette[variant].main}, ${theme.palette[variant].light})`
          }
        }}
      />
      {showProgress && progress !== undefined && (
        <Typography variant="caption" color="text.secondary" mt={1} display="block" textAlign="center">
          {Math.round(progress)}% 完成
        </Typography>
      )}
    </Box>
  );

  const renderSkeletonLoading = () => (
    <Box p={3}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Skeleton variant="text" height={40} />
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card>
            <CardContent>
              <Skeleton variant="rectangular" height={120} />
              <Skeleton variant="text" height={30} sx={{ mt: 1 }} />
              <Skeleton variant="text" height={20} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card>
            <CardContent>
              <Skeleton variant="circular" width={60} height={60} />
              <Skeleton variant="text" height={30} sx={{ mt: 1 }} />
              <Skeleton variant="text" height={20} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Skeleton variant="rectangular" height={200} />
        </Grid>
      </Grid>
    </Box>
  );

  const renderDotsLoading = () => (
    <Box display="flex" flexDirection="column" alignItems="center" gap={3} p={3}>
      <Box display="flex" gap={1}>
        {[0, 1, 2].map((index) => (
          <Box
            key={index}
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: theme.palette[variant].main,
              animation: `${waveAnimation} 1.4s ease-in-out infinite`,
              animationDelay: `${index * 0.16}s`
            }}
          />
        ))}
      </Box>
      <Typography 
        variant="body2" 
        color="text.secondary"
        textAlign="center"
      >
        {loadingTips[currentTip]}
      </Typography>
    </Box>
  );

  const renderCustomLoading = () => (
    <Box 
      display="flex" 
      flexDirection="column" 
      alignItems="center" 
      gap={3}
      p={4}
    >
      {/* 自定义AI思维图标动画 */}
      <Box
        sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          background: `linear-gradient(135deg, ${theme.palette[variant].main}, ${theme.palette[variant].light})`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          animation: `${pulseAnimation} 2s ease-in-out infinite`,
          boxShadow: `0 4px 20px ${theme.palette[variant].main}40`
        }}
      >
        <Psychology sx={{ fontSize: 40, color: 'white' }} />
      </Box>

      {/* 进度环 */}
      <Box position="relative" display="inline-flex">
        <CircularProgress
          variant="determinate"
          value={100}
          size={120}
          thickness={2}
          sx={{ color: theme.palette.grey[200] }}
        />
        <CircularProgress
          variant={progress !== undefined ? 'determinate' : 'indeterminate'}
          value={progress || 25}
          size={120}
          thickness={2}
          sx={{
            color: theme.palette[variant].main,
            position: 'absolute',
            left: 0,
            '& .MuiCircularProgress-circle': {
              strokeLinecap: 'round',
            },
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="h6" component="div" color="text.secondary">
            {showProgress && progress !== undefined ? `${Math.round(progress)}%` : ''}
          </Typography>
        </Box>
      </Box>

      <Box textAlign="center">
        <Typography variant="h6" color="text.primary" gutterBottom>
          智能分析中
        </Typography>
        <Fade in key={currentTip}>
          <Typography variant="body2" color="text.secondary">
            {loadingTips[currentTip]}
          </Typography>
        </Fade>
      </Box>
    </Box>
  );

  const renderContent = () => {
    switch (type) {
      case 'linear':
        return renderLinearLoading();
      case 'skeleton':
        return renderSkeletonLoading();
      case 'dots':
        return renderDotsLoading();
      case 'custom':
        return renderCustomLoading();
      default:
        return renderCircularLoading();
    }
  };

  const containerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: fullScreen ? '100vh' : minHeight,
    width: '100%',
    ...(fullScreen && {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      backdropFilter: 'blur(10px)',
      zIndex: 9999
    })
  };

  return (
    <Box sx={containerStyle}>
      <Card
        sx={{
          maxWidth: type === 'skeleton' ? 800 : 400,
          width: '100%',
          mx: 2,
          background: fullScreen ? 'rgba(255, 255, 255, 0.95)' : 'background.paper',
          backdropFilter: fullScreen ? 'blur(10px)' : 'none',
          border: fullScreen ? '1px solid rgba(255, 255, 255, 0.2)' : 'none',
          borderRadius: 3,
          boxShadow: fullScreen ? '0 8px 32px rgba(0, 0, 0, 0.1)' : 1
        }}
      >
        {renderContent()}
      </Card>
    </Box>
  );
};

// 高阶组件：为任意组件添加加载状态
export const withLoading = <P extends object>(
  Component: React.ComponentType<P>,
  LoadingComponent?: React.ComponentType<EnhancedLoadingProps>
) => {
  return React.forwardRef<any, P & { loading?: boolean; loadingProps?: EnhancedLoadingProps }>(
    (props, ref) => {
      const { loading, loadingProps, ...componentProps } = props;
      const LoadingComp = LoadingComponent || EnhancedLoading;

      if (loading) {
        return <LoadingComp {...loadingProps} />;
      }

      return <Component {...(componentProps as P)} ref={ref} />;
    }
  );
};

export default EnhancedLoading; 