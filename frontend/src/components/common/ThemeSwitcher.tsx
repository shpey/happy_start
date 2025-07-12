/**
 * 主题切换组件
 * 提供主题模式切换和主题定制功能
 */

import React, { useState } from 'react';
import {
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Divider,
  Slider,
  Button,
  Grid,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Chip
} from '@mui/material';
import {
  Brightness4,
  Brightness7,
  Palette,
  Settings,
  RestartAlt,
  Check,
  Close
} from '@mui/icons-material';
import { useTheme, themePresets } from '../../contexts/ThemeContext';
import { useNotification } from './NotificationProvider';

interface ThemeSwitcherProps {
  variant?: 'icon' | 'menu' | 'inline';
  showLabel?: boolean;
}

const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ 
  variant = 'icon', 
  showLabel = false 
}) => {
  const { themeConfig, isDarkMode, toggleMode, updateTheme, resetTheme } = useTheme();
  const { success, info } = useNotification();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [customizeDialogOpen, setCustomizeDialogOpen] = useState(false);
  const [tempConfig, setTempConfig] = useState(themeConfig);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleToggleMode = () => {
    toggleMode();
    success(`已切换到${isDarkMode ? '明亮' : '暗黑'}模式`);
    if (variant === 'menu') {
      handleMenuClose();
    }
  };

  const handleOpenCustomize = () => {
    setTempConfig(themeConfig);
    setCustomizeDialogOpen(true);
    handleMenuClose();
  };

  const handleApplyCustomTheme = () => {
    updateTheme(tempConfig);
    setCustomizeDialogOpen(false);
    success('主题配置已应用');
  };

  const handleResetTheme = () => {
    resetTheme();
    setCustomizeDialogOpen(false);
    info('主题已重置为默认设置');
  };

  const handlePresetSelect = (presetKey: string) => {
    const preset = themePresets[presetKey as keyof typeof themePresets];
    setTempConfig(prev => ({
      ...prev,
      primaryColor: preset.primaryColor,
      secondaryColor: preset.secondaryColor
    }));
  };

  // 图标模式
  if (variant === 'icon') {
    return (
      <>
        <Tooltip title={`切换到${isDarkMode ? '明亮' : '暗黑'}模式`}>
          <IconButton
            onClick={handleToggleMode}
            color="inherit"
            sx={{
              transition: 'transform 0.3s ease-in-out',
              '&:hover': {
                transform: 'rotate(180deg)'
              }
            }}
          >
            {isDarkMode ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Tooltip>

        <Tooltip title="主题设置">
          <IconButton onClick={handleMenuOpen} color="inherit">
            <Palette />
          </IconButton>
        </Tooltip>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          PaperProps={{
            sx: { width: 250 }
          }}
        >
          <MenuItem onClick={handleToggleMode}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              {isDarkMode ? <Brightness7 /> : <Brightness4 />}
              <Typography>
                {isDarkMode ? '明亮模式' : '暗黑模式'}
              </Typography>
              <Switch checked={isDarkMode} size="small" sx={{ ml: 'auto' }} />
            </Box>
          </MenuItem>

          <MenuItem onClick={handleOpenCustomize}>
            <Settings sx={{ mr: 2 }} />
            自定义主题
          </MenuItem>

          <MenuItem onClick={() => {
            resetTheme();
            handleMenuClose();
            info('主题已重置');
          }}>
            <RestartAlt sx={{ mr: 2 }} />
            重置主题
          </MenuItem>
        </Menu>
      </>
    );
  }

  // 内联模式
  if (variant === 'inline') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={isDarkMode}
              onChange={handleToggleMode}
              icon={<Brightness4 />}
              checkedIcon={<Brightness7 />}
            />
          }
          label={showLabel ? (isDarkMode ? '暗黑模式' : '明亮模式') : ''}
        />
        <Tooltip title="自定义主题">
          <IconButton size="small" onClick={handleOpenCustomize}>
            <Palette />
          </IconButton>
        </Tooltip>
      </Box>
    );
  }

  // 主题定制对话框
  const CustomizeDialog = (
    <Dialog
      open={customizeDialogOpen}
      onClose={() => setCustomizeDialogOpen(false)}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Palette />
        主题定制
      </DialogTitle>

      <DialogContent dividers>
        <Grid container spacing={3}>
          {/* 模式切换 */}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={tempConfig.mode === 'dark'}
                  onChange={(e) => setTempConfig(prev => ({
                    ...prev,
                    mode: e.target.checked ? 'dark' : 'light'
                  }))}
                />
              }
              label="暗黑模式"
            />
          </Grid>

          {/* 预设主题 */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              预设主题
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {Object.entries(themePresets).map(([key, preset]) => (
                <Chip
                  key={key}
                  label={preset.name}
                  onClick={() => handlePresetSelect(key)}
                  variant={
                    tempConfig.primaryColor === preset.primaryColor ? 'filled' : 'outlined'
                  }
                  sx={{
                    bgcolor: tempConfig.primaryColor === preset.primaryColor ? 
                      preset.primaryColor : 'transparent',
                    color: tempConfig.primaryColor === preset.primaryColor ? 'white' : 'inherit',
                    '&:hover': {
                      bgcolor: preset.primaryColor,
                      color: 'white'
                    }
                  }}
                />
              ))}
            </Box>
          </Grid>

          {/* 主色调 */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              主色调
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <input
                type="color"
                value={tempConfig.primaryColor}
                onChange={(e) => setTempConfig(prev => ({
                  ...prev,
                  primaryColor: e.target.value
                }))}
                style={{
                  width: 50,
                  height: 40,
                  border: 'none',
                  borderRadius: 8,
                  cursor: 'pointer'
                }}
              />
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                {tempConfig.primaryColor}
              </Typography>
            </Box>
          </Grid>

          {/* 次要色调 */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              次要色调
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <input
                type="color"
                value={tempConfig.secondaryColor}
                onChange={(e) => setTempConfig(prev => ({
                  ...prev,
                  secondaryColor: e.target.value
                }))}
                style={{
                  width: 50,
                  height: 40,
                  border: 'none',
                  borderRadius: 8,
                  cursor: 'pointer'
                }}
              />
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                {tempConfig.secondaryColor}
              </Typography>
            </Box>
          </Grid>

          {/* 圆角大小 */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              圆角大小: {tempConfig.borderRadius}px
            </Typography>
            <Slider
              value={tempConfig.borderRadius}
              onChange={(_, value) => setTempConfig(prev => ({
                ...prev,
                borderRadius: value as number
              }))}
              min={0}
              max={24}
              step={2}
              marks={[
                { value: 0, label: '直角' },
                { value: 8, label: '默认' },
                { value: 16, label: '圆润' },
                { value: 24, label: '超圆' }
              ]}
            />
          </Grid>

          {/* 字体系列 */}
          <Grid item xs={12}>
            <FormControl fullWidth size="small">
              <InputLabel>字体系列</InputLabel>
              <Select
                value={tempConfig.fontFamily}
                label="字体系列"
                onChange={(e) => setTempConfig(prev => ({
                  ...prev,
                  fontFamily: e.target.value
                }))}
              >
                <MenuItem value='"Roboto", "Helvetica", "Arial", sans-serif'>
                  Roboto (默认)
                </MenuItem>
                <MenuItem value='"Inter", "Roboto", sans-serif'>
                  Inter (现代)
                </MenuItem>
                <MenuItem value='"Poppins", "Roboto", sans-serif'>
                  Poppins (圆润)
                </MenuItem>
                <MenuItem value='"Source Sans Pro", "Roboto", sans-serif'>
                  Source Sans Pro (专业)
                </MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* 预览区域 */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              预览
            </Typography>
            <Paper 
              sx={{ 
                p: 2, 
                bgcolor: tempConfig.mode === 'dark' ? '#1e1e1e' : '#ffffff',
                color: tempConfig.mode === 'dark' ? '#ffffff' : '#000000',
                borderRadius: `${tempConfig.borderRadius}px`
              }}
            >
              <Typography variant="h6" sx={{ 
                color: tempConfig.primaryColor, 
                fontFamily: tempConfig.fontFamily 
              }}>
                智能思维平台
              </Typography>
              <Typography variant="body2" paragraph>
                这是一个预览示例，展示您的主题配置效果。
              </Typography>
              <Button 
                variant="contained" 
                size="small"
                sx={{ 
                  bgcolor: tempConfig.primaryColor,
                  borderRadius: `${tempConfig.borderRadius}px`,
                  fontFamily: tempConfig.fontFamily
                }}
              >
                主要按钮
              </Button>
              <Button 
                variant="outlined" 
                size="small" 
                sx={{ 
                  ml: 1,
                  color: tempConfig.secondaryColor,
                  borderColor: tempConfig.secondaryColor,
                  borderRadius: `${tempConfig.borderRadius}px`,
                  fontFamily: tempConfig.fontFamily
                }}
              >
                次要按钮
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleResetTheme} startIcon={<RestartAlt />}>
          重置
        </Button>
        <Button onClick={() => setCustomizeDialogOpen(false)} startIcon={<Close />}>
          取消
        </Button>
        <Button 
          onClick={handleApplyCustomTheme} 
          variant="contained" 
          startIcon={<Check />}
        >
          应用
        </Button>
      </DialogActions>
    </Dialog>
  );

  return CustomizeDialog;
};

export default ThemeSwitcher; 