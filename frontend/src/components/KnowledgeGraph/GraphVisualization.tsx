/**
 * 知识图谱可视化组件
 * 使用D3.js实现交互式节点图形
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { Box, Paper, IconButton, Tooltip, Typography, Chip } from '@mui/material';
import { 
  ZoomIn, 
  ZoomOut, 
  CenterFocusStrong, 
  FilterList,
  Search,
  Settings 
} from '@mui/icons-material';

// 节点类型定义
export interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  type: 'concept' | 'thinking' | 'user' | 'analysis';
  size: number;
  color?: string;
  description?: string;
  metadata?: any;
}

// 连接线定义
export interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  id: string;
  source: string | GraphNode;
  target: string | GraphNode;
  type: 'related' | 'contains' | 'influences' | 'derived';
  strength: number;
  label?: string;
}

// 图谱数据
export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface GraphVisualizationProps {
  data: GraphData;
  width?: number;
  height?: number;
  onNodeClick?: (node: GraphNode) => void;
  onLinkClick?: (link: GraphLink) => void;
  selectedNodeId?: string;
  filterType?: string[];
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  data,
  width = 800,
  height = 600,
  onNodeClick,
  onLinkClick,
  selectedNodeId,
  filterType = []
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [zoom, setZoom] = useState(1);
  const [simulation, setSimulation] = useState<d3.Simulation<GraphNode, GraphLink> | null>(null);

  // 颜色方案
  const colorScale = d3.scaleOrdinal<string>()
    .domain(['concept', 'thinking', 'user', 'analysis'])
    .range(['#2196F3', '#FF5722', '#4CAF50', '#9C27B0']);

  // 节点大小比例
  const sizeScale = d3.scaleLinear()
    .domain([1, 10])
    .range([8, 30]);

  // 初始化图形
  const initializeGraph = useCallback(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // 创建容器组
    const container = svg.append("g").attr("class", "graph-container");

    // 创建连接线组
    const linkGroup = container.append("g").attr("class", "links");
    
    // 创建节点组
    const nodeGroup = container.append("g").attr("class", "nodes");

    // 创建标签组
    const labelGroup = container.append("g").attr("class", "labels");

    // 过滤数据
    const filteredNodes = filterType.length > 0 
      ? data.nodes.filter(node => filterType.includes(node.type))
      : data.nodes;

    const filteredLinks = data.links.filter(link => {
      const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
      const targetId = typeof link.target === 'string' ? link.target : link.target.id;
      return filteredNodes.some(n => n.id === sourceId) && 
             filteredNodes.some(n => n.id === targetId);
    });

    // 创建力导向布局
    const newSimulation = d3.forceSimulation<GraphNode>(filteredNodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(filteredLinks)
        .id(d => d.id)
        .distance(d => 100 - d.strength * 20)
        .strength(d => d.strength * 0.8))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(d => sizeScale(d.size) + 5));

    setSimulation(newSimulation);

    // 创建连接线
    const links = linkGroup.selectAll<SVGLineElement, GraphLink>("line")
      .data(filteredLinks)
      .enter()
      .append("line")
      .attr("class", "link")
      .style("stroke", d => d.type === 'influences' ? '#FF5722' : '#999')
      .style("stroke-width", d => Math.sqrt(d.strength * 5))
      .style("stroke-opacity", 0.6)
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation();
        onLinkClick?.(d);
      });

    // 创建节点
    const nodes = nodeGroup.selectAll<SVGCircleElement, GraphNode>("circle")
      .data(filteredNodes)
      .enter()
      .append("circle")
      .attr("class", "node")
      .attr("r", d => sizeScale(d.size))
      .style("fill", d => d.color || colorScale(d.type))
      .style("stroke", d => selectedNodeId === d.id ? '#000' : '#fff')
      .style("stroke-width", d => selectedNodeId === d.id ? 3 : 2)
      .style("cursor", "pointer")
      .call(d3.drag<SVGCircleElement, GraphNode>()
        .on("start", (event, d) => {
          if (!event.active) newSimulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) newSimulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }))
      .on("click", (event, d) => {
        event.stopPropagation();
        onNodeClick?.(d);
      })
      .on("mouseover", function(event, d) {
        // 高亮相关节点
        const connectedNodeIds = new Set<string>();
        filteredLinks.forEach(link => {
          const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
          const targetId = typeof link.target === 'string' ? link.target : link.target.id;
          if (sourceId === d.id) connectedNodeIds.add(targetId);
          if (targetId === d.id) connectedNodeIds.add(sourceId);
        });

        nodes.style("opacity", node => 
          node.id === d.id || connectedNodeIds.has(node.id) ? 1 : 0.3);
        links.style("opacity", link => {
          const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
          const targetId = typeof link.target === 'string' ? link.target : link.target.id;
          return sourceId === d.id || targetId === d.id ? 1 : 0.1;
        });
      })
      .on("mouseout", () => {
        nodes.style("opacity", 1);
        links.style("opacity", 0.6);
      });

    // 创建标签
    const labels = labelGroup.selectAll<SVGTextElement, GraphNode>("text")
      .data(filteredNodes)
      .enter()
      .append("text")
      .attr("class", "label")
      .text(d => d.label)
      .style("font-size", "12px")
      .style("font-weight", "500")
      .style("fill", "#333")
      .style("text-anchor", "middle")
      .style("pointer-events", "none")
      .style("user-select", "none");

    // 更新位置
    newSimulation.on("tick", () => {
      links
        .attr("x1", d => (d.source as GraphNode).x || 0)
        .attr("y1", d => (d.source as GraphNode).y || 0)
        .attr("x2", d => (d.target as GraphNode).x || 0)
        .attr("y2", d => (d.target as GraphNode).y || 0);

      nodes
        .attr("cx", d => d.x || 0)
        .attr("cy", d => d.y || 0);

      labels
        .attr("x", d => d.x || 0)
        .attr("y", d => (d.y || 0) + sizeScale(d.size) + 15);
    });

    // 缩放功能
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        container.attr("transform", event.transform);
        setZoom(event.transform.k);
      });

    svg.call(zoomBehavior);

  }, [data, width, height, selectedNodeId, filterType, onNodeClick, onLinkClick]);

  useEffect(() => {
    initializeGraph();
    return () => {
      simulation?.stop();
    };
  }, [initializeGraph, simulation]);

  // 缩放控制
  const handleZoomIn = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 1.5
    );
  };

  const handleZoomOut = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 1 / 1.5
    );
  };

  const handleResetView = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().transform as any,
      d3.zoomIdentity
    );
  };

  return (
    <Paper elevation={3} sx={{ position: 'relative', overflow: 'hidden' }}>
      {/* 图形容器 */}
      <Box sx={{ width, height, position: 'relative' }}>
        <svg
          ref={svgRef}
          width={width}
          height={height}
          style={{ cursor: 'grab' }}
        />

        {/* 控制面板 */}
        <Box
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            display: 'flex',
            flexDirection: 'column',
            gap: 1
          }}
        >
          <Tooltip title="放大" placement="left">
            <IconButton 
              size="small" 
              onClick={handleZoomIn}
              sx={{ bgcolor: 'background.paper', '&:hover': { bgcolor: 'grey.100' } }}
            >
              <ZoomIn />
            </IconButton>
          </Tooltip>

          <Tooltip title="缩小" placement="left">
            <IconButton 
              size="small" 
              onClick={handleZoomOut}
              sx={{ bgcolor: 'background.paper', '&:hover': { bgcolor: 'grey.100' } }}
            >
              <ZoomOut />
            </IconButton>
          </Tooltip>

          <Tooltip title="重置视图" placement="left">
            <IconButton 
              size="small" 
              onClick={handleResetView}
              sx={{ bgcolor: 'background.paper', '&:hover': { bgcolor: 'grey.100' } }}
            >
              <CenterFocusStrong />
            </IconButton>
          </Tooltip>
        </Box>

        {/* 状态信息 */}
        <Paper
          sx={{
            position: 'absolute',
            bottom: 16,
            left: 16,
            padding: 1,
            backgroundColor: 'rgba(255, 255, 255, 0.9)'
          }}
        >
          <Typography variant="caption" display="block">
            节点: {data.nodes.length} | 连接: {data.links.length}
          </Typography>
          <Typography variant="caption" display="block">
            缩放: {(zoom * 100).toFixed(0)}%
          </Typography>
        </Paper>

        {/* 图例 */}
        <Paper
          sx={{
            position: 'absolute',
            top: 16,
            left: 16,
            padding: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.9)'
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            节点类型
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            {[
              { type: 'concept', label: '概念' },
              { type: 'thinking', label: '思维' },
              { type: 'user', label: '用户' },
              { type: 'analysis', label: '分析' }
            ].map(({ type, label }) => (
              <Chip
                key={type}
                label={label}
                size="small"
                sx={{
                  backgroundColor: colorScale(type),
                  color: 'white',
                  fontSize: '12px'
                }}
              />
            ))}
          </Box>
        </Paper>
      </Box>
    </Paper>
  );
};

export default GraphVisualization; 