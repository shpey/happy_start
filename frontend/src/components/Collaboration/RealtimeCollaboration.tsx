/**
 * 实时协作组件
 * 支持多用户实时协作、聊天、共享思维空间
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Badge,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import {
  Send,
  Videocam,
  VoiceChat,
  Share,
  PersonAdd,
  Settings,
  MoreVert,
  Circle,
  Visibility,
  Edit,
  Comment,
  Group,
  VideoCall,
  Call,
  Psychology
} from '@mui/icons-material';
import { useWebSocket } from '../../hooks/useWebSocket';

// 用户状态定义
export interface CollaborationUser {
  id: string;
  name: string;
  avatar?: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  role: 'host' | 'participant' | 'observer';
  cursor?: { x: number; y: number };
  thinking_focus?: string; // 当前关注的思维节点
}

// 消息类型定义
export interface ChatMessage {
  id: string;
  user_id: string;
  user_name: string;
  content: string;
  type: 'text' | 'system' | 'thinking_share' | 'annotation';
  timestamp: Date;
  metadata?: any;
}

// 协作事件定义
export interface CollaborationEvent {
  id: string;
  type: 'user_join' | 'user_leave' | 'cursor_move' | 'thinking_update' | 'annotation_add';
  user_id: string;
  data: any;
  timestamp: Date;
}

interface RealtimeCollaborationProps {
  sessionId: string;
  currentUser: CollaborationUser;
  onUserUpdate?: (users: CollaborationUser[]) => void;
  onThinkingShare?: (data: any) => void;
  onAnnotationAdd?: (annotation: any) => void;
}

const RealtimeCollaboration: React.FC<RealtimeCollaborationProps> = ({
  sessionId,
  currentUser,
  onUserUpdate,
  onThinkingShare,
  onAnnotationAdd
}) => {
  const [activeUsers, setActiveUsers] = useState<CollaborationUser[]>([currentUser]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [currentTab, setCurrentTab] = useState(0);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // WebSocket连接
  const { socket, isConnected, sendMessage } = useWebSocket(
    `ws://localhost:8000/ws/collaboration/${sessionId}`,
    {
      onMessage: handleWebSocketMessage,
      onConnect: handleConnect,
      onDisconnect: handleDisconnect
    }
  );

  // 处理WebSocket消息
  function handleWebSocketMessage(data: any) {
    const { type, payload } = data;
    
    switch (type) {
      case 'user_list_update':
        setActiveUsers(payload.users);
        onUserUpdate?.(payload.users);
        break;
        
      case 'new_message':
        setMessages(prev => [...prev, payload.message]);
        break;
        
      case 'user_joined':
        setActiveUsers(prev => [...prev, payload.user]);
        addSystemMessage(`${payload.user.name} 加入了协作`);
        break;
        
      case 'user_left':
        setActiveUsers(prev => prev.filter(u => u.id !== payload.user_id));
        addSystemMessage(`用户离开了协作`);
        break;
        
      case 'cursor_update':
        setActiveUsers(prev => prev.map(user => 
          user.id === payload.user_id 
            ? { ...user, cursor: payload.cursor }
            : user
        ));
        break;
        
      case 'thinking_shared':
        onThinkingShare?.(payload.thinking_data);
        addSystemMessage(`${payload.user_name} 分享了思维内容`, 'thinking_share');
        break;
        
      case 'annotation_added':
        onAnnotationAdd?.(payload.annotation);
        addSystemMessage(`${payload.user_name} 添加了标注`, 'annotation');
        break;
        
      default:
        console.log('Unknown message type:', type);
    }
  }

  // 连接成功处理
  function handleConnect() {
    console.log('WebSocket connected');
    // 发送用户加入事件
    sendMessage({
      type: 'user_join',
      payload: { user: currentUser }
    });
  }

  // 断开连接处理
  function handleDisconnect() {
    console.log('WebSocket disconnected');
  }

  // 添加系统消息
  const addSystemMessage = (content: string, type: ChatMessage['type'] = 'system') => {
    const systemMessage: ChatMessage = {
      id: `system_${Date.now()}`,
      user_id: 'system',
      user_name: 'System',
      content,
      type,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, systemMessage]);
  };

  // 发送聊天消息
  const handleSendMessage = useCallback(() => {
    if (newMessage.trim() && isConnected) {
      const message: ChatMessage = {
        id: `msg_${Date.now()}`,
        user_id: currentUser.id,
        user_name: currentUser.name,
        content: newMessage.trim(),
        type: 'text',
        timestamp: new Date()
      };

      sendMessage({
        type: 'new_message',
        payload: { message }
      });

      setNewMessage('');
    }
  }, [newMessage, currentUser, isConnected, sendMessage]);

  // 分享思维内容
  const handleShareThinking = (thinkingData: any) => {
    if (isConnected) {
      sendMessage({
        type: 'share_thinking',
        payload: {
          thinking_data: thinkingData,
          user_name: currentUser.name
        }
      });
    }
  };

  // 更新用户状态
  const updateUserStatus = (status: CollaborationUser['status']) => {
    if (isConnected) {
      sendMessage({
        type: 'update_status',
        payload: {
          user_id: currentUser.id,
          status
        }
      });
    }
  };

  // 滚动到消息底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 状态颜色
  const getStatusColor = (status: CollaborationUser['status']) => {
    switch (status) {
      case 'online': return 'success';
      case 'away': return 'warning';
      case 'busy': return 'error';
      default: return 'default';
    }
  };

  // 状态图标
  const getStatusIcon = (status: CollaborationUser['status']) => {
    return <Circle sx={{ fontSize: 12, color: getStatusColor(status) === 'success' ? 'green' : 
                           getStatusColor(status) === 'warning' ? 'orange' : 
                           getStatusColor(status) === 'error' ? 'red' : 'gray' }} />;
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 协作状态头部 */}
      <Paper sx={{ p: 2, mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6">实时协作</Typography>
          <Badge color={isConnected ? 'success' : 'error'} variant="dot">
            <Chip 
              label={isConnected ? '已连接' : '连接中...'} 
              size="small" 
              color={isConnected ? 'success' : 'default'}
            />
          </Badge>
          <Chip label={`${activeUsers.length} 人在线`} size="small" icon={<Group />} />
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="语音通话">
            <IconButton size="small">
              <Call />
            </IconButton>
          </Tooltip>
          <Tooltip title="视频通话">
            <IconButton size="small">
              <VideoCall />
            </IconButton>
          </Tooltip>
          <Tooltip title="邀请用户">
            <IconButton size="small" onClick={() => setInviteDialogOpen(true)}>
              <PersonAdd />
            </IconButton>
          </Tooltip>
          <Tooltip title="分享">
            <IconButton size="small" onClick={() => setShareDialogOpen(true)}>
              <Share />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      <Grid container spacing={2} sx={{ flexGrow: 1, overflow: 'hidden' }}>
        {/* 用户列表 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Tabs 
              value={currentTab} 
              onChange={(_, newValue) => setCurrentTab(newValue)}
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab label="用户" icon={<Group />} />
              <Tab label="聊天" icon={<Comment />} />
            </Tabs>

            {/* 用户列表标签页 */}
            {currentTab === 0 && (
              <Box sx={{ p: 2, flexGrow: 1, overflow: 'auto' }}>
                <Typography variant="subtitle2" gutterBottom>
                  在线用户 ({activeUsers.length})
                </Typography>
                <List>
                  {activeUsers.map(user => (
                    <ListItem key={user.id} sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <Badge
                          overlap="circular"
                          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                          badgeContent={getStatusIcon(user.status)}
                        >
                          <Avatar src={user.avatar} sx={{ width: 40, height: 40 }}>
                            {user.name[0]}
                          </Avatar>
                        </Badge>
                      </ListItemAvatar>
                      <ListItemText
                        primary={user.name}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip label={user.role} size="small" variant="outlined" />
                            {user.thinking_focus && (
                              <Chip label={`关注: ${user.thinking_focus}`} size="small" />
                            )}
                          </Box>
                        }
                      />
                      <IconButton size="small">
                        <MoreVert />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* 聊天标签页 */}
            {currentTab === 1 && (
              <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                {/* 消息列表 */}
                <Box sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
                  <List>
                    {messages.map(message => (
                      <ListItem key={message.id} sx={{ px: 1, alignItems: 'flex-start' }}>
                        {message.type !== 'system' && (
                          <ListItemAvatar>
                            <Avatar sx={{ width: 32, height: 32 }}>
                              {message.user_name[0]}
                            </Avatar>
                          </ListItemAvatar>
                        )}
                        <ListItemText
                          primary={
                            message.type === 'system' ? (
                              <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                {message.content}
                              </Typography>
                            ) : (
                              <Box>
                                <Typography variant="body2" component="span" fontWeight="bold">
                                  {message.user_name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                  {message.timestamp.toLocaleTimeString()}
                                </Typography>
                              </Box>
                            )
                          }
                          secondary={
                            message.type !== 'system' && (
                              <Typography variant="body2" sx={{ mt: 0.5 }}>
                                {message.content}
                              </Typography>
                            )
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                  <div ref={messagesEndRef} />
                </Box>

                {/* 消息输入 */}
                <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider' }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder="输入消息..."
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      multiline
                      maxRows={3}
                    />
                    <IconButton 
                      color="primary" 
                      onClick={handleSendMessage}
                      disabled={!newMessage.trim() || !isConnected}
                    >
                      <Send />
                    </IconButton>
                  </Box>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* 协作活动区域 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ height: '100%', p: 2 }}>
            <Typography variant="h6" gutterBottom>
              🎯 协作活动
            </Typography>
            
            <Grid container spacing={2}>
              {/* 实时思维分享 */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      思维共享
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      分享您的思维过程，让团队成员了解您的思考方向
                    </Typography>
                    <Button 
                      variant="outlined" 
                      startIcon={<Psychology />}
                      onClick={() => handleShareThinking({ type: 'current_thinking' })}
                    >
                      分享当前思维
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              {/* 注释和标记 */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      协作标注
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      在共享空间中添加注释和标记
                    </Typography>
                    <Button 
                      variant="outlined" 
                      startIcon={<Edit />}
                      onClick={() => onAnnotationAdd?.({ type: 'new_annotation' })}
                    >
                      添加标注
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              {/* 协作统计 */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      协作统计
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h4" color="primary">
                            {activeUsers.length}
                          </Typography>
                          <Typography variant="caption">在线用户</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h4" color="secondary">
                            {messages.filter(m => m.type === 'text').length}
                          </Typography>
                          <Typography variant="caption">聊天消息</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h4" color="success.main">
                            {messages.filter(m => m.type === 'thinking_share').length}
                          </Typography>
                          <Typography variant="caption">思维分享</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h4" color="warning.main">
                            {messages.filter(m => m.type === 'annotation').length}
                          </Typography>
                          <Typography variant="caption">协作标注</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* 邀请用户对话框 */}
      <Dialog open={inviteDialogOpen} onClose={() => setInviteDialogOpen(false)}>
        <DialogTitle>邀请用户</DialogTitle>
        <DialogContent>
          <Typography paragraph>
            分享以下链接邀请其他用户加入协作：
          </Typography>
          <TextField
            fullWidth
            value={`${window.location.origin}/collaboration/${sessionId}`}
            InputProps={{ readOnly: true }}
            sx={{ mb: 2 }}
          />
          <Button variant="outlined" fullWidth>
            复制链接
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInviteDialogOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>

      {/* 分享对话框 */}
      <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)}>
        <DialogTitle>分享协作</DialogTitle>
        <DialogContent>
          <Typography paragraph>
            选择要分享的内容类型：
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Button variant="outlined" startIcon={<Visibility />}>
              分享屏幕
            </Button>
            <Button variant="outlined" startIcon={<Psychology />}>
              分享思维地图
            </Button>
            <Button variant="outlined" startIcon={<Comment />}>
              分享聊天记录
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareDialogOpen(false)}>取消</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RealtimeCollaboration; 