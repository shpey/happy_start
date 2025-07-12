/**
 * 用户引导组件
 * 为新用户提供交互式的功能介绍和指导
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fab,
  Zoom,
  Tooltip,
  Avatar,
  IconButton,
  Divider,
  Alert
} from '@mui/material';
import {
  Help,
  Psychology,
  AccountTree,
  Groups,
  ViewInAr,
  Dashboard,
  NavigateNext,
  NavigateBefore,
  Close,
  CheckCircle,
  Lightbulb,
  School,
  Explore,
  Settings,
  PlayArrow,
  Bookmark
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useLocalStorage, STORAGE_KEYS } from '../../hooks/useLocalStorage';
import { useNotification } from './NotificationProvider';

interface GuideStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactElement;
  content: React.ReactNode;
  action?: {
    label: string;
    path?: string;
    callback?: () => void;
  };
}

const UserGuide: React.FC = () => {
  const navigate = useNavigate();
  const { success, info } = useNotification();
  const [guideOpen, setGuideOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [hasSeenGuide, setHasSeenGuide] = useLocalStorage('user_guide_completed', false);
  const [showHelpFab, setShowHelpFab] = useState(true);

  // 引导步骤
  const guideSteps: GuideStep[] = [
    {
      id: 'welcome',
      title: '欢迎使用智能思维平台',
      description: '让我们快速了解这个强大的AI思维分析工具',
      icon: <School />,
      content: (
        <Box>
          <Typography variant="body1" paragraph>
            🎉 欢迎来到智能思维平台！这是一个基于AI技术的思维分析和协作平台，能够帮助您：
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon><Psychology color="primary" /></ListItemIcon>
              <ListItemText primary="分析思维模式" secondary="识别您的形象思维、逻辑思维和创造思维特点" />
            </ListItem>
            <ListItem>
              <ListItemIcon><AccountTree color="success" /></ListItemIcon>
              <ListItemText primary="构建知识图谱" secondary="可视化您的知识结构和关联关系" />
            </ListItem>
            <ListItem>
              <ListItemIcon><Groups color="error" /></ListItemIcon>
              <ListItemText primary="实时协作" secondary="与他人共同探讨和分析复杂问题" />
            </ListItem>
            <ListItem>
              <ListItemIcon><ViewInAr color="warning" /></ListItemIcon>
              <ListItemText primary="3D思维空间" secondary="在沉浸式环境中进行思维可视化" />
            </ListItem>
          </List>
        </Box>
      )
    },
    {
      id: 'thinking_analysis',
      title: '思维分析功能',
      description: '了解AI驱动的思维模式分析',
      icon: <Psychology />,
      content: (
        <Box>
          <Typography variant="body1" paragraph>
            🧠 思维分析是我们的核心功能，它使用先进的AI技术来分析您的思维方式：
          </Typography>
          <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: 'primary.50' }}>
            <Typography variant="subtitle2" gutterBottom>
              三层思维模型
            </Typography>
            <Typography variant="body2" paragraph>
              • <strong>形象思维</strong>：分析您的视觉化和具象化思维能力<br/>
              • <strong>逻辑思维</strong>：评估逻辑推理和结构化思考能力<br/>
              • <strong>创造思维</strong>：识别创新思路和发散性思维特点
            </Typography>
          </Paper>
          <Alert severity="info">
            💡 输入您的想法或问题，AI会分析您的思维模式并提供个性化建议
          </Alert>
        </Box>
      ),
      action: {
        label: '立即体验',
        path: '/thinking'
      }
    },
    {
      id: 'knowledge_graph',
      title: '知识图谱',
      description: '可视化知识关联网络',
      icon: <AccountTree />,
      content: (
        <Box>
          <Typography variant="body1" paragraph>
            🌐 知识图谱功能帮助您建立和可视化知识之间的关联：
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><CheckCircle color="success" fontSize="small" /></ListItemIcon>
              <ListItemText primary="交互式节点图" secondary="直观展示概念间的关系" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircle color="success" fontSize="small" /></ListItemIcon>
              <ListItemText primary="智能搜索" secondary="快速定位相关知识点" />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircle color="success" fontSize="small" /></ListItemIcon>
              <ListItemText primary="个性化布局" secondary="自定义图谱的展示方式" />
            </ListItem>
          </List>
          <Paper elevation={1} sx={{ p: 2, bgcolor: 'success.50' }}>
            <Typography variant="body2">
              🔍 使用方法：点击节点查看详情，拖拽调整位置，双击展开关联内容
            </Typography>
          </Paper>
        </Box>
      ),
      action: {
        label: '探索图谱',
        path: '/knowledge'
      }
    },
    {
      id: 'collaboration',
      title: '实时协作',
      description: '多人协作思维空间',
      icon: <Groups />,
      content: (
        <Box>
          <Typography variant="body1" paragraph>
            👥 实时协作功能让您与团队成员共同思考和分析：
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2, mb: 2 }}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6" color="primary">
                实时聊天
              </Typography>
              <Typography variant="body2">
                与协作者即时交流想法
              </Typography>
            </Paper>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6" color="primary">
                思维分享
              </Typography>
              <Typography variant="body2">
                分享分析结果和洞察
              </Typography>
            </Paper>
          </Box>
          <Alert severity="warning">
            👆 提示：创建或加入协作会话，邀请他人参与思维讨论
          </Alert>
        </Box>
      ),
      action: {
        label: '开始协作',
        path: '/collaboration'
      }
    },
    {
      id: 'quick_access',
      title: '快速访问面板',
      description: '便捷的功能入口',
      icon: <Explore />,
      content: (
        <Box>
          <Typography variant="body1" paragraph>
            🚀 快速访问面板提供了便捷的功能入口：
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <PlayArrow />
            </Avatar>
            <Box>
              <Typography variant="subtitle2">右下角速拨菜单</Typography>
              <Typography variant="body2" color="text.secondary">
                点击浮动按钮快速访问所有功能
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Avatar sx={{ bgcolor: 'success.main' }}>
              <Dashboard />
            </Avatar>
            <Box>
              <Typography variant="subtitle2">系统状态面板</Typography>
              <Typography variant="body2" color="text.secondary">
                查看系统运行状态和最近活动
              </Typography>
            </Box>
          </Box>
          <Paper elevation={1} sx={{ p: 2, bgcolor: 'info.50' }}>
            <Typography variant="body2">
              💡 贴士：右下角的通知按钮可查看系统消息和提醒
            </Typography>
          </Paper>
        </Box>
      )
    },
    {
      id: 'tips',
      title: '使用技巧',
      description: '让您更高效地使用平台',
      icon: <Lightbulb />,
      content: (
        <Box>
          <Typography variant="body1" paragraph>
            💡 一些有用的使用技巧：
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon><Bookmark color="primary" /></ListItemIcon>
              <ListItemText 
                primary="保存重要分析" 
                secondary="分析结果会自动保存到历史记录中"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><Settings color="primary" /></ListItemIcon>
              <ListItemText 
                primary="个性化设置" 
                secondary="调整主题、分析深度等偏好设置"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><Help color="primary" /></ListItemIcon>
              <ListItemText 
                primary="获取帮助" 
                secondary="随时点击帮助按钮重新查看引导"
              />
            </ListItem>
          </List>
          <Alert severity="success">
            🎯 完成引导后，建议先从思维分析功能开始体验！
          </Alert>
        </Box>
      ),
      action: {
        label: '开始探索',
        path: '/thinking'
      }
    }
  ];

  useEffect(() => {
    // 首次访问时显示引导
    if (!hasSeenGuide) {
      setTimeout(() => {
        setGuideOpen(true);
      }, 1000);
    }
  }, [hasSeenGuide]);

  const handleNext = () => {
    if (currentStep < guideSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    setHasSeenGuide(true);
    setGuideOpen(false);
    setCurrentStep(0);
    success('欢迎使用智能思维平台！开始您的思维探索之旅吧！');
  };

  const handleSkip = () => {
    setHasSeenGuide(true);
    setGuideOpen(false);
    setCurrentStep(0);
    info('您可以随时点击帮助按钮重新查看引导');
  };

  const handleStepAction = () => {
    const step = guideSteps[currentStep];
    if (step.action) {
      if (step.action.path) {
        navigate(step.action.path);
        handleComplete();
      } else if (step.action.callback) {
        step.action.callback();
      }
    }
  };

  const openGuide = () => {
    setGuideOpen(true);
    setCurrentStep(0);
  };

  return (
    <>
      {/* 帮助按钮 */}
      <Zoom in={showHelpFab}>
        <Fab
          color="secondary"
          size="small"
          sx={{
            position: 'fixed',
            bottom: 160,
            right: 24,
            zIndex: 1200
          }}
          onClick={openGuide}
        >
          <Help />
        </Fab>
      </Zoom>

      {/* 引导对话框 */}
      <Dialog
        open={guideOpen}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { minHeight: 500 }
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {guideSteps[currentStep]?.icon}
            {guideSteps[currentStep]?.title}
          </Box>
          <IconButton onClick={handleSkip} size="small">
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent>
          <Stepper activeStep={currentStep} orientation="vertical">
            {guideSteps.map((step, index) => (
              <Step key={step.id}>
                <StepLabel>
                  <Typography variant="subtitle1">
                    {step.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {step.description}
                  </Typography>
                </StepLabel>
                <StepContent>
                  {step.content}
                  {step.action && (
                    <Box sx={{ mt: 2 }}>
                      <Button
                        variant="contained"
                        onClick={handleStepAction}
                        startIcon={step.action.path ? <NavigateNext /> : undefined}
                      >
                        {step.action.label}
                      </Button>
                    </Box>
                  )}
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </DialogContent>

        <DialogActions sx={{ justifyContent: 'space-between', px: 3, pb: 2 }}>
          <Button onClick={handleSkip} color="inherit">
            跳过引导
          </Button>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              onClick={handleBack}
              disabled={currentStep === 0}
              startIcon={<NavigateBefore />}
            >
              上一步
            </Button>
            
            {currentStep === guideSteps.length - 1 ? (
              <Button
                onClick={handleComplete}
                variant="contained"
                startIcon={<CheckCircle />}
              >
                完成引导
              </Button>
            ) : (
              <Button
                onClick={handleNext}
                variant="contained"
                endIcon={<NavigateNext />}
              >
                下一步
              </Button>
            )}
          </Box>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default UserGuide; 