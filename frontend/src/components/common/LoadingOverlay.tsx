/**
 * 智能加载覆盖组件
 * 提供多种加载状态和动画效果
 */

import React from 'react';
import {
  Box,
  CircularProgress,
  LinearProgress,
  Typography,
  Backdrop,
  Paper,
  Skeleton,
  Grid
} from '@mui/material';
import { keyframes } from '@mui/system';

// 脉冲动画
const pulse = keyframes`
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
`;

// 思维波动画
const thinkingWave = keyframes`
  0%, 60%, 100% {
    transform: initial;
  }
  30% {
    transform: translateY(-15px);
  }
`;

interface LoadingOverlayProps {
  loading: boolean;
  type?: 'circular' | 'linear' | 'thinking' | 'skeleton';
  message?: string;
  progress?: number;
  backdrop?: boolean;
  children?: React.ReactNode;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  loading,
  type = 'circular',
  message,
  progress,
  backdrop = true,
  children
}) => {
  if (!loading && type !== 'skeleton') {
    return <>{children}</>;
  }

  const renderLoadingContent = () => {
    switch (type) {
      case 'linear':
        return (
          <Box sx={{ width: '100%', maxWidth: 400 }}>
            <LinearProgress 
              variant={progress !== undefined ? 'determinate' : 'indeterminate'}
              value={progress}
              sx={{ height: 8, borderRadius: 4 }}
            />
            {message && (
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ mt: 2, textAlign: 'center' }}
              >
                {message}
                {progress !== undefined && ` (${Math.round(progress)}%)`}
              </Typography>
            )}
          </Box>
        );

      case 'thinking':
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {[0, 1, 2].map((index) => (
                <Box
                  key={index}
                  sx={{
                    width: 12,
                    height: 12,
                    backgroundColor: 'primary.main',
                    borderRadius: '50%',
                    animation: `${thinkingWave} 1.4s ease-in-out infinite both`,
                    animationDelay: `${index * 0.16}s`
                  }}
                />
              ))}
            </Box>
            {message && (
              <Typography variant="body2" color="text.secondary">
                {message}
              </Typography>
            )}
          </Box>
        );

      case 'skeleton':
        if (!loading) return children;
        return (
          <Box>
            <Skeleton variant="text" width="60%" height={32} />
            <Skeleton variant="rectangular" width="100%" height={200} sx={{ mt: 2 }} />
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
              <Skeleton variant="circular" width={40} height={40} />
              <Box sx={{ flex: 1 }}>
                <Skeleton variant="text" width="80%" />
                <Skeleton variant="text" width="60%" />
              </Box>
            </Box>
          </Box>
        );

      default: // circular
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CircularProgress 
              size={48}
              variant={progress !== undefined ? 'determinate' : 'indeterminate'}
              value={progress}
              sx={{
                animation: progress === undefined ? `${pulse} 2s ease-in-out infinite` : 'none'
              }}
            />
            {message && (
              <Typography variant="body2" color="text.secondary" textAlign="center">
                {message}
              </Typography>
            )}
            {progress !== undefined && (
              <Typography variant="caption" color="text.secondary">
                {Math.round(progress)}%
              </Typography>
            )}
          </Box>
        );
    }
  };

  if (type === 'skeleton') {
    return renderLoadingContent();
  }

  if (backdrop) {
    return (
      <>
        {children}
        <Backdrop
          sx={{ 
            color: '#fff', 
            zIndex: 9998,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(4px)'
          }}
          open={loading}
        >
          <Paper
            elevation={8}
            sx={{
              p: 4,
              borderRadius: 3,
              backgroundColor: 'background.paper',
              color: 'text.primary',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              minWidth: 200
            }}
          >
            {renderLoadingContent()}
          </Paper>
        </Backdrop>
      </>
    );
  }

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: 200,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      {renderLoadingContent()}
    </Box>
  );
};

// 预设加载组件
export const ThinkingLoader: React.FC<{ message?: string }> = ({ message = "AI正在思考..." }) => (
  <LoadingOverlay loading={true} type="thinking" message={message} backdrop={false} />
);

export const ProgressLoader: React.FC<{ progress: number; message?: string }> = ({ progress, message }) => (
  <LoadingOverlay loading={true} type="linear" progress={progress} message={message} backdrop={false} />
);

export const SkeletonLoader: React.FC<{ loading: boolean; children: React.ReactNode }> = ({ loading, children }) => (
  <LoadingOverlay loading={loading} type="skeleton" backdrop={false}>
    {children}
  </LoadingOverlay>
);

export default LoadingOverlay; 