import React, { useState, useEffect, useMemo } from 'react';
import { 
  Typography, 
  Paper, 
  Box, 
  Grid,
  Card,
  CardContent,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Breadcrumbs,
  Link
} from '@mui/material';
import { 
  Add, 
  NavigateNext,
  ViewInAr,
  Psychology,
  AccountTree,
  Lightbulb,
  Share,
  Save,
  Download
} from '@mui/icons-material';
import { Vector3 } from 'three';
import EnhancedThinkingSpace, { 
  EnhancedThinkingNode, 
  ThinkingConnection, 
  ThinkingLayer 
} from '../components/ThreeD/EnhancedThinkingSpace';

const ThreeDSpacePage: React.FC = () => {
  const [nodes, setNodes] = useState<EnhancedThinkingNode[]>([]);
  const [connections, setConnections] = useState<ThinkingConnection[]>([]);
  const [selectedNode, setSelectedNode] = useState<EnhancedThinkingNode | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newNodeData, setNewNodeData] = useState({
    content: '',
    layer: 'logical' as ThinkingLayer,
    type: 'concept' as 'concept' | 'idea' | 'insight' | 'question' | 'solution',
    tags: ''
  });
  const [layerVisibility, setLayerVisibility] = useState({
    visual: true,
    logical: true,
    creative: true
  });

  // 示例思维节点数据
  const exampleNodes: EnhancedThinkingNode[] = useMemo(() => [
    {
      id: 'node1',
      layer: 'visual',
      content: '视觉想象：彩虹桥的设计',
      position: new Vector3(-5, 2, 0),
      size: 1.2,
      intensity: 0.8,
      connections: ['node2', 'node4'],
      metadata: {
        createdAt: new Date(),
        userId: 'user1',
        tags: ['设计', '视觉', '创新'],
        type: 'concept'
      },
      visual: {
        color: '#2196F3',
        opacity: 0.8,
        glow: true,
        animated: true
      }
    },
    {
      id: 'node2',
      layer: 'logical',
      content: '逻辑分析：结构工程原理',
      position: new Vector3(0, 0, 0),
      size: 1.0,
      intensity: 0.9,
      connections: ['node1', 'node3'],
      metadata: {
        createdAt: new Date(),
        userId: 'user1',
        tags: ['工程', '逻辑', '分析'],
        type: 'insight'
      },
      visual: {
        color: '#FF5722',
        opacity: 0.8,
        glow: false,
        animated: false
      }
    },
    {
      id: 'node3',
      layer: 'creative',
      content: '创意灵感：悬浮材料应用',
      position: new Vector3(5, -2, 0),
      size: 1.5,
      intensity: 0.7,
      connections: ['node2'],
      metadata: {
        createdAt: new Date(),
        userId: 'user1',
        tags: ['创新', '材料', '未来'],
        type: 'idea'
      },
      visual: {
        color: '#4CAF50',
        opacity: 0.8,
        glow: true,
        animated: true
      }
    },
    {
      id: 'node4',
      layer: 'visual',
      content: '场景构想：城市天际线',
      position: new Vector3(-3, 2, 3),
      size: 1.1,
      intensity: 0.6,
      connections: ['node1'],
      metadata: {
        createdAt: new Date(),
        userId: 'user2',
        tags: ['城市', '规划', '美学'],
        type: 'concept'
      },
      visual: {
        color: '#2196F3',
        opacity: 0.7,
        glow: false,
        animated: false
      }
    },
    {
      id: 'node5',
      layer: 'logical',
      content: '问题思考：如何实现可持续发展？',
      position: new Vector3(2, 0, -4),
      size: 0.9,
      intensity: 0.8,
      connections: ['node6'],
      metadata: {
        createdAt: new Date(),
        userId: 'user2',
        tags: ['可持续', '问题', '思考'],
        type: 'question'
      },
      visual: {
        color: '#FF5722',
        opacity: 0.8,
        glow: true,
        animated: false
      }
    },
    {
      id: 'node6',
      layer: 'creative',
      content: '解决方案：生物仿生技术',
      position: new Vector3(4, -2, -2),
      size: 1.3,
      intensity: 0.9,
      connections: ['node5'],
      metadata: {
        createdAt: new Date(),
        userId: 'user3',
        tags: ['仿生', '技术', '解决方案'],
        type: 'solution'
      },
      visual: {
        color: '#4CAF50',
        opacity: 0.9,
        glow: true,
        animated: true
      }
    }
  ], []);

  // 示例连接数据
  const exampleConnections: ThinkingConnection[] = useMemo(() => [
    {
      id: 'conn1',
      from: 'node1',
      to: 'node2',
      strength: 0.8,
      type: 'association',
      animated: true
    },
    {
      id: 'conn2',
      from: 'node2',
      to: 'node3',
      strength: 0.9,
      type: 'causality',
      animated: false
    },
    {
      id: 'conn3',
      from: 'node1',
      to: 'node4',
      strength: 0.6,
      type: 'similarity',
      animated: true
    },
    {
      id: 'conn4',
      from: 'node5',
      to: 'node6',
      strength: 0.9,
      type: 'causality',
      animated: true
    }
  ], []);

  // 初始化示例数据
  useEffect(() => {
    setNodes(exampleNodes);
    setConnections(exampleConnections);
  }, [exampleNodes, exampleConnections]);

  // 处理节点点击
  const handleNodeClick = (node: EnhancedThinkingNode) => {
    setSelectedNode(node);
  };

  // 处理节点创建
  const handleNodeCreate = (position: Vector3, layer: ThinkingLayer) => {
    setNewNodeData(prev => ({ ...prev, layer }));
    setCreateDialogOpen(true);
  };

  // 确认创建节点
  const handleCreateConfirm = () => {
    const newNode: EnhancedThinkingNode = {
      id: `node_${Date.now()}`,
      layer: newNodeData.layer,
      content: newNodeData.content,
      position: new Vector3(Math.random() * 10 - 5, 0, Math.random() * 10 - 5),
      size: 1.0,
      intensity: 0.7,
      connections: [],
      metadata: {
        createdAt: new Date(),
        userId: 'current_user',
        tags: newNodeData.tags.split(',').map(tag => tag.trim()).filter(Boolean),
        type: newNodeData.type
      },
      visual: {
        color: newNodeData.layer === 'visual' ? '#2196F3' : 
               newNodeData.layer === 'logical' ? '#FF5722' : '#4CAF50',
        opacity: 0.8,
        glow: true,
        animated: true
      }
    };

    setNodes(prev => [...prev, newNode]);
    setCreateDialogOpen(false);
    setNewNodeData({
      content: '',
      layer: 'logical',
      type: 'concept',
      tags: ''
    });
  };

  // 处理连接创建
  const handleConnectionCreate = (fromId: string, toId: string) => {
    const newConnection: ThinkingConnection = {
      id: `conn_${Date.now()}`,
      from: fromId,
      to: toId,
      strength: 0.7,
      type: 'association',
      animated: true
    };

    setConnections(prev => [...prev, newConnection]);
  };

  // 层级统计
  const layerStats = useMemo(() => {
    const stats = {
      visual: nodes.filter(n => n.layer === 'visual').length,
      logical: nodes.filter(n => n.layer === 'logical').length,
      creative: nodes.filter(n => n.layer === 'creative').length
    };
    return stats;
  }, [nodes]);

  // 导出数据
  const handleExportData = () => {
    const data = {
      nodes,
      connections,
      metadata: {
        exportedAt: new Date(),
        version: '1.0',
        nodeCount: nodes.length,
        connectionCount: connections.length
      }
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `thinking_space_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      {/* 页面头部 */}
      <Box sx={{ mb: 2 }}>
        <Breadcrumbs separator={<NavigateNext fontSize="small" />} sx={{ mb: 1 }}>
          <Link underline="hover" color="inherit" href="/">
            首页
          </Link>
          <Typography color="text.primary">3D思维空间</Typography>
        </Breadcrumbs>

        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ViewInAr /> 3D思维空间
          <Chip label={`${nodes.length} 节点`} size="small" />
          <Chip label={`${connections.length} 连接`} size="small" />
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          在三维空间中可视化和探索您的思维过程，支持形象思维、逻辑思维和创造思维的立体化表达
        </Typography>

        {/* 功能提示 */}
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            💡 点击底部的层级按钮创建思维节点 | 🖱️ 左键点击选择节点 | 🔄 鼠标拖拽旋转视角 | ⚡ 支持实时协作和VR体验
          </Typography>
        </Alert>
      </Box>

      <Grid container spacing={2} sx={{ flexGrow: 1 }}>
        {/* 3D空间主体 */}
        <Grid item xs={12} md={9}>
          <Paper sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
            <EnhancedThinkingSpace
              width={1000}
              height={600}
              nodes={nodes}
              connections={connections}
              onNodeClick={handleNodeClick}
              onNodeCreate={handleNodeCreate}
              onConnectionCreate={handleConnectionCreate}
              isCollaborative={true}
              showLayers={layerVisibility}
              xrEnabled={true}
            />
          </Paper>
        </Grid>

        {/* 侧边信息面板 */}
        <Grid item xs={12} md={3}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
            {/* 层级统计 */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  思维层级统计
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Psychology sx={{ color: '#2196F3' }} />
                        <Typography variant="body2">形象思维</Typography>
                      </Box>
                      <Chip label={layerStats.visual} size="small" color="primary" />
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AccountTree sx={{ color: '#FF5722' }} />
                        <Typography variant="body2">逻辑思维</Typography>
                      </Box>
                      <Chip label={layerStats.logical} size="small" sx={{ bgcolor: '#FF5722', color: 'white' }} />
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Lightbulb sx={{ color: '#4CAF50' }} />
                        <Typography variant="body2">创造思维</Typography>
                      </Box>
                      <Chip label={layerStats.creative} size="small" sx={{ bgcolor: '#4CAF50', color: 'white' }} />
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* 选中节点信息 */}
            {selectedNode && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    节点详情
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>内容:</strong> {selectedNode.content}
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>类型:</strong> {selectedNode.metadata.type}
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>强度:</strong> {(selectedNode.intensity * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>标签:</strong>
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {selectedNode.metadata.tags.map(tag => (
                      <Chip key={tag} label={tag} size="small" />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            )}

            {/* 快捷操作 */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  快捷操作
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button 
                    variant="outlined" 
                    startIcon={<Add />}
                    onClick={() => setCreateDialogOpen(true)}
                  >
                    添加思维节点
                  </Button>
                  <Button 
                    variant="outlined" 
                    startIcon={<Share />}
                    onClick={() => {/* TODO: 实现分享功能 */}}
                  >
                    分享思维空间
                  </Button>
                  <Button 
                    variant="outlined" 
                    startIcon={<Save />}
                    onClick={() => {/* TODO: 实现保存功能 */}}
                  >
                    保存到云端
                  </Button>
                  <Button 
                    variant="outlined" 
                    startIcon={<Download />}
                    onClick={handleExportData}
                  >
                    导出数据
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Grid>
      </Grid>

      {/* 创建节点对话框 */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>创建思维节点</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="节点内容"
              value={newNodeData.content}
              onChange={(e) => setNewNodeData(prev => ({ ...prev, content: e.target.value }))}
              multiline
              rows={3}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>思维层级</InputLabel>
              <Select
                value={newNodeData.layer}
                onChange={(e) => setNewNodeData(prev => ({ ...prev, layer: e.target.value as ThinkingLayer }))}
              >
                <MenuItem value="visual">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Psychology sx={{ color: '#2196F3' }} />
                    形象思维
                  </Box>
                </MenuItem>
                <MenuItem value="logical">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AccountTree sx={{ color: '#FF5722' }} />
                    逻辑思维
                  </Box>
                </MenuItem>
                <MenuItem value="creative">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Lightbulb sx={{ color: '#4CAF50' }} />
                    创造思维
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>节点类型</InputLabel>
              <Select
                value={newNodeData.type}
                onChange={(e) => setNewNodeData(prev => ({ ...prev, type: e.target.value as any }))}
              >
                <MenuItem value="concept">概念</MenuItem>
                <MenuItem value="idea">想法</MenuItem>
                <MenuItem value="insight">洞察</MenuItem>
                <MenuItem value="question">问题</MenuItem>
                <MenuItem value="solution">解决方案</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="标签 (用逗号分隔)"
              value={newNodeData.tags}
              onChange={(e) => setNewNodeData(prev => ({ ...prev, tags: e.target.value }))}
              placeholder="例如：创新,设计,技术"
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>取消</Button>
          <Button 
            variant="contained" 
            onClick={handleCreateConfirm}
            disabled={!newNodeData.content.trim()}
          >
            创建
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ThreeDSpacePage; 