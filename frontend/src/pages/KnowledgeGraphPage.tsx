import React, { useState, useMemo } from 'react';
import { 
  Typography, 
  Paper, 
  Box, 
  Grid, 
  Card, 
  CardContent,
  Chip,
  TextField,
  InputAdornment,
  FormControlLabel,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Fab
} from '@mui/material';
import { 
  Search, 
  Add, 
  FilterList,
  AccountTree,
  Psychology,
  Person,
  Analytics
} from '@mui/icons-material';
import GraphVisualization, { GraphNode, GraphLink, GraphData } from '../components/KnowledgeGraph/GraphVisualization';

const KnowledgeGraphPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>();
  const [filterTypes, setFilterTypes] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // 示例知识图谱数据
  const graphData: GraphData = useMemo(() => ({
    nodes: [
      // 概念节点
      { id: 'concept1', label: '形象思维', type: 'concept', size: 8, description: '基于图像、空间和视觉的思维方式' },
      { id: 'concept2', label: '逻辑思维', type: 'concept', size: 8, description: '基于逻辑推理和分析的思维方式' },
      { id: 'concept3', label: '创造思维', type: 'concept', size: 8, description: '产生新想法和创新解决方案的思维方式' },
      { id: 'concept4', label: '批判思维', type: 'concept', size: 6, description: '分析和评估信息的思维技能' },
      { id: 'concept5', label: '系统思维', type: 'concept', size: 7, description: '从整体视角看待问题的思维方式' },
      
      // 思维分析节点
      { id: 'thinking1', label: '创意写作', type: 'thinking', size: 5, description: '基于创造思维的文本生成' },
      { id: 'thinking2', label: '数学推理', type: 'thinking', size: 6, description: '基于逻辑思维的数学问题解决' },
      { id: 'thinking3', label: '空间设计', type: 'thinking', size: 5, description: '基于形象思维的空间布局' },
      { id: 'thinking4', label: '策略规划', type: 'thinking', size: 7, description: '综合多种思维模式的策略制定' },
      
      // 用户节点
      { id: 'user1', label: '张三', type: 'user', size: 4, description: '擅长逻辑思维的用户' },
      { id: 'user2', label: '李四', type: 'user', size: 4, description: '擅长创造思维的用户' },
      { id: 'user3', label: '王五', type: 'user', size: 4, description: '擅长形象思维的用户' },
      
      // 分析节点
      { id: 'analysis1', label: '思维模式分析', type: 'analysis', size: 6, description: '对用户思维模式的综合分析' },
      { id: 'analysis2', label: '学习路径推荐', type: 'analysis', size: 5, description: '基于思维特点的学习建议' },
      { id: 'analysis3', label: '协作匹配', type: 'analysis', size: 5, description: '基于思维互补的团队匹配' }
    ],
    links: [
      // 概念之间的关系
      { id: 'link1', source: 'concept1', target: 'concept2', type: 'related', strength: 0.6, label: '互补关系' },
      { id: 'link2', source: 'concept2', target: 'concept3', type: 'related', strength: 0.7, label: '协同关系' },
      { id: 'link3', source: 'concept1', target: 'concept3', type: 'related', strength: 0.5, label: '支持关系' },
      { id: 'link4', source: 'concept4', target: 'concept2', type: 'contains', strength: 0.8, label: '包含关系' },
      { id: 'link5', source: 'concept5', target: 'concept1', type: 'influences', strength: 0.6, label: '影响关系' },
      
      // 思维活动与概念的关系
      { id: 'link6', source: 'thinking1', target: 'concept3', type: 'derived', strength: 0.9, label: '基于' },
      { id: 'link7', source: 'thinking2', target: 'concept2', type: 'derived', strength: 0.9, label: '基于' },
      { id: 'link8', source: 'thinking3', target: 'concept1', type: 'derived', strength: 0.8, label: '基于' },
      { id: 'link9', source: 'thinking4', target: 'concept5', type: 'derived', strength: 0.7, label: '基于' },
      
      // 用户与思维模式的关系
      { id: 'link10', source: 'user1', target: 'concept2', type: 'related', strength: 0.8, label: '擅长' },
      { id: 'link11', source: 'user2', target: 'concept3', type: 'related', strength: 0.9, label: '擅长' },
      { id: 'link12', source: 'user3', target: 'concept1', type: 'related', strength: 0.8, label: '擅长' },
      
      // 分析与其他节点的关系
      { id: 'link13', source: 'analysis1', target: 'user1', type: 'influences', strength: 0.7, label: '分析' },
      { id: 'link14', source: 'analysis1', target: 'user2', type: 'influences', strength: 0.7, label: '分析' },
      { id: 'link15', source: 'analysis1', target: 'user3', type: 'influences', strength: 0.7, label: '分析' },
      { id: 'link16', source: 'analysis2', target: 'concept1', type: 'related', strength: 0.6, label: '推荐' },
      { id: 'link17', source: 'analysis3', target: 'user1', type: 'influences', strength: 0.5, label: '匹配' },
      { id: 'link18', source: 'analysis3', target: 'user2', type: 'influences', strength: 0.5, label: '匹配' }
    ]
  }), []);

  // 过滤数据
  const filteredData = useMemo(() => {
    let filteredNodes = graphData.nodes;
    let filteredLinks = graphData.links;

    // 按类型过滤
    if (filterTypes.length > 0) {
      filteredNodes = graphData.nodes.filter(node => filterTypes.includes(node.type));
      filteredLinks = graphData.links.filter(link => {
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
        return filteredNodes.some(n => n.id === sourceId) && 
               filteredNodes.some(n => n.id === targetId);
      });
    }

    // 按搜索查询过滤
    if (searchQuery) {
      const queryLower = searchQuery.toLowerCase();
      filteredNodes = filteredNodes.filter(node => 
        node.label.toLowerCase().includes(queryLower) ||
        (node.description && node.description.toLowerCase().includes(queryLower))
      );
      filteredLinks = filteredLinks.filter(link => {
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
        return filteredNodes.some(n => n.id === sourceId) && 
               filteredNodes.some(n => n.id === targetId);
      });
    }

    return { nodes: filteredNodes, links: filteredLinks };
  }, [graphData, filterTypes, searchQuery]);

  // 处理节点点击
  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
    setSelectedNodeId(node.id);
    setDialogOpen(true);
  };

  // 处理连接线点击
  const handleLinkClick = (link: GraphLink) => {
    console.log('Link clicked:', link);
  };

  // 处理类型过滤
  const handleFilterChange = (type: string) => {
    setFilterTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const nodeTypeIcons = {
    concept: <AccountTree />,
    thinking: <Psychology />,
    user: <Person />,
    analysis: <Analytics />
  };

  const nodeTypeLabels = {
    concept: '概念',
    thinking: '思维',
    user: '用户',
    analysis: '分析'
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        🌐 知识图谱
        <Chip label={`${filteredData.nodes.length} 节点`} size="small" />
        <Chip label={`${filteredData.links.length} 连接`} size="small" />
      </Typography>

      <Grid container spacing={3}>
        {/* 控制面板 */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              搜索与过滤
            </Typography>
            
            {/* 搜索框 */}
            <TextField
              fullWidth
              placeholder="搜索节点..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />

            {/* 类型过滤 */}
            <Typography variant="subtitle2" gutterBottom>
              节点类型
            </Typography>
            {Object.entries(nodeTypeLabels).map(([type, label]) => (
              <FormControlLabel
                key={type}
                control={
                  <Checkbox
                    checked={filterTypes.includes(type)}
                    onChange={() => handleFilterChange(type)}
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {nodeTypeIcons[type as keyof typeof nodeTypeIcons]}
                    {label}
                  </Box>
                }
              />
            ))}
          </Paper>

          {/* 统计信息 */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              图谱统计
            </Typography>
            <Grid container spacing={1}>
              {Object.entries(nodeTypeLabels).map(([type, label]) => {
                const count = filteredData.nodes.filter(n => n.type === type).length;
                return (
                  <Grid item xs={6} key={type}>
                    <Card sx={{ textAlign: 'center', py: 1 }}>
                      <CardContent sx={{ py: '8px !important' }}>
                        {nodeTypeIcons[type as keyof typeof nodeTypeIcons]}
                        <Typography variant="h6">{count}</Typography>
                        <Typography variant="caption">{label}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </Paper>
        </Grid>

        {/* 图谱可视化 */}
        <Grid item xs={12} md={9}>
          <GraphVisualization
            data={filteredData}
            width={800}
            height={600}
            onNodeClick={handleNodeClick}
            onLinkClick={handleLinkClick}
            selectedNodeId={selectedNodeId}
            filterType={filterTypes}
          />
        </Grid>
      </Grid>

      {/* 添加新节点的浮动按钮 */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 32, right: 32 }}
        onClick={() => {
          // TODO: 实现添加节点功能
          console.log('Add new node');
        }}
      >
        <Add />
      </Fab>

      {/* 节点详情对话框 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {selectedNode && nodeTypeIcons[selectedNode.type as keyof typeof nodeTypeIcons]}
          {selectedNode?.label}
          <Chip 
            label={selectedNode ? nodeTypeLabels[selectedNode.type as keyof typeof nodeTypeLabels] : ''} 
            size="small" 
          />
        </DialogTitle>
        <DialogContent>
          {selectedNode && (
            <Box>
              <Typography variant="body1" paragraph>
                {selectedNode.description}
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom>
                节点信息
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ID: {selectedNode.id}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                类型: {nodeTypeLabels[selectedNode.type as keyof typeof nodeTypeLabels]}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                大小: {selectedNode.size}
              </Typography>

              {selectedNode.metadata && (
                <>
                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                    元数据
                  </Typography>
                  <pre style={{ fontSize: '12px', color: '#666' }}>
                    {JSON.stringify(selectedNode.metadata, null, 2)}
                  </pre>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>关闭</Button>
          <Button variant="contained" onClick={() => {
            // TODO: 实现编辑功能
            console.log('Edit node:', selectedNode);
          }}>
            编辑
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default KnowledgeGraphPage; 