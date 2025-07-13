import React, { useRef, useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Tooltip,
  IconButton,
  Grid,
  useTheme
} from '@mui/material';
import {
  Timeline,
  BubbleChart,
  ScatterPlot,
  NetworkCheck,
  Insights,
  TrendingUp,
  SaveAlt,
  Fullscreen
} from '@mui/icons-material';

// 高级图表配置接口
interface ChartConfig {
  type: 'heatmap' | 'sankey' | 'network' | 'treemap' | 'sunburst' | 'timeline';
  data: any;
  options?: any;
  width?: number;
  height?: number;
}

interface AdvancedChartsProps {
  config: ChartConfig;
  title?: string;
  onExport?: (format: 'png' | 'svg' | 'pdf') => void;
  interactive?: boolean;
}

// 热力图组件
const HeatmapChart: React.FC<{
  data: any;
  width: number;
  height: number;
  theme: any;
}> = ({ data, width, height, theme }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = svgRef.current;
    svg.innerHTML = '';

    // 创建热力图
    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // 模拟热力图数据
    const heatmapData = data.matrix || generateHeatmapData();
    const maxValue = Math.max(...heatmapData.flat());
    
    // 创建SVG容器
    const container = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    container.setAttribute('transform', `translate(${margin.left}, ${margin.top})`);
    svg.appendChild(container);

    // 绘制热力图网格
    const cellWidth = innerWidth / heatmapData[0].length;
    const cellHeight = innerHeight / heatmapData.length;

    heatmapData.forEach((row, i) => {
      row.forEach((value, j) => {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', (j * cellWidth).toString());
        rect.setAttribute('y', (i * cellHeight).toString());
        rect.setAttribute('width', cellWidth.toString());
        rect.setAttribute('height', cellHeight.toString());
        
        // 根据值设置颜色
        const intensity = value / maxValue;
        const color = interpolateColor(theme.palette.primary.light, theme.palette.primary.dark, intensity);
        rect.setAttribute('fill', color);
        rect.setAttribute('stroke', theme.palette.divider);
        rect.setAttribute('stroke-width', '1');
        
        // 添加交互
        rect.addEventListener('mouseenter', () => {
          rect.setAttribute('opacity', '0.8');
        });
        rect.addEventListener('mouseleave', () => {
          rect.setAttribute('opacity', '1');
        });

        container.appendChild(rect);

        // 添加文本标签
        if (cellWidth > 30 && cellHeight > 20) {
          const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          text.setAttribute('x', (j * cellWidth + cellWidth / 2).toString());
          text.setAttribute('y', (i * cellHeight + cellHeight / 2).toString());
          text.setAttribute('text-anchor', 'middle');
          text.setAttribute('dominant-baseline', 'central');
          text.setAttribute('fill', intensity > 0.5 ? 'white' : 'black');
          text.setAttribute('font-size', '12');
          text.textContent = Math.round(value).toString();
          container.appendChild(text);
        }
      });
    });

  }, [data, width, height, theme]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      style={{ border: `1px solid ${theme.palette.divider}` }}
    />
  );
};

// 网络图组件
const NetworkChart: React.FC<{
  data: any;
  width: number;
  height: number;
  theme: any;
}> = ({ data, width, height, theme }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = svgRef.current;
    svg.innerHTML = '';

    // 创建网络图数据
    const nodes = data.nodes || generateNetworkNodes();
    const links = data.links || generateNetworkLinks(nodes);

    // 简单的力导向布局模拟
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;

    nodes.forEach((node: any, i: number) => {
      const angle = (2 * Math.PI * i) / nodes.length;
      node.x = centerX + radius * Math.cos(angle);
      node.y = centerY + radius * Math.sin(angle);
    });

    // 绘制连接线
    links.forEach((link: any) => {
      const sourceNode = nodes.find((n: any) => n.id === link.source);
      const targetNode = nodes.find((n: any) => n.id === link.target);
      
      if (sourceNode && targetNode) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', sourceNode.x.toString());
        line.setAttribute('y1', sourceNode.y.toString());
        line.setAttribute('x2', targetNode.x.toString());
        line.setAttribute('y2', targetNode.y.toString());
        line.setAttribute('stroke', theme.palette.divider);
        line.setAttribute('stroke-width', Math.sqrt(link.weight || 1).toString());
        line.setAttribute('opacity', '0.6');
        svg.appendChild(line);
      }
    });

    // 绘制节点
    nodes.forEach((node: any) => {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', node.x.toString());
      circle.setAttribute('cy', node.y.toString());
      circle.setAttribute('r', (node.size || 10).toString());
      circle.setAttribute('fill', node.color || theme.palette.primary.main);
      circle.setAttribute('stroke', theme.palette.background.paper);
      circle.setAttribute('stroke-width', '2');
      
      // 添加交互
      circle.addEventListener('mouseenter', () => {
        circle.setAttribute('r', ((node.size || 10) * 1.2).toString());
      });
      circle.addEventListener('mouseleave', () => {
        circle.setAttribute('r', (node.size || 10).toString());
      });

      svg.appendChild(circle);

      // 添加标签
      if (node.label) {
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.x.toString());
        text.setAttribute('y', (node.y + (node.size || 10) + 15).toString());
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', theme.palette.text.primary);
        text.setAttribute('font-size', '10');
        text.textContent = node.label;
        svg.appendChild(text);
      }
    });

  }, [data, width, height, theme]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      style={{ border: `1px solid ${theme.palette.divider}` }}
    />
  );
};

// 时间线图组件
const TimelineChart: React.FC<{
  data: any;
  width: number;
  height: number;
  theme: any;
}> = ({ data, width, height, theme }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = svgRef.current;
    svg.innerHTML = '';

    const margin = { top: 20, right: 20, bottom: 40, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // 创建时间线数据
    const events = data.events || generateTimelineData();
    const minDate = new Date(Math.min(...events.map((e: any) => new Date(e.date).getTime())));
    const maxDate = new Date(Math.max(...events.map((e: any) => new Date(e.date).getTime())));
    const timeRange = maxDate.getTime() - minDate.getTime();

    // 创建容器
    const container = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    container.setAttribute('transform', `translate(${margin.left}, ${margin.top})`);
    svg.appendChild(container);

    // 绘制时间轴
    const timelineY = innerHeight / 2;
    const timeline = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    timeline.setAttribute('x1', '0');
    timeline.setAttribute('y1', timelineY.toString());
    timeline.setAttribute('x2', innerWidth.toString());
    timeline.setAttribute('y2', timelineY.toString());
    timeline.setAttribute('stroke', theme.palette.divider);
    timeline.setAttribute('stroke-width', '2');
    container.appendChild(timeline);

    // 绘制事件
    events.forEach((event: any, index: number) => {
      const eventDate = new Date(event.date);
      const x = ((eventDate.getTime() - minDate.getTime()) / timeRange) * innerWidth;
      const isEven = index % 2 === 0;
      const y = isEven ? timelineY - 60 : timelineY + 60;

      // 连接线
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', x.toString());
      line.setAttribute('y1', timelineY.toString());
      line.setAttribute('x2', x.toString());
      line.setAttribute('y2', y.toString());
      line.setAttribute('stroke', theme.palette.primary.main);
      line.setAttribute('stroke-width', '2');
      line.setAttribute('stroke-dasharray', '3,3');
      container.appendChild(line);

      // 事件圆点
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', x.toString());
      circle.setAttribute('cy', timelineY.toString());
      circle.setAttribute('r', '6');
      circle.setAttribute('fill', event.color || theme.palette.primary.main);
      circle.setAttribute('stroke', theme.palette.background.paper);
      circle.setAttribute('stroke-width', '2');
      container.appendChild(circle);

      // 事件标签
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', x.toString());
      text.setAttribute('y', (y + (isEven ? -5 : 15)).toString());
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('fill', theme.palette.text.primary);
      text.setAttribute('font-size', '12');
      text.setAttribute('font-weight', 'bold');
      text.textContent = event.title;
      container.appendChild(text);

      // 日期标签
      const dateText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      dateText.setAttribute('x', x.toString());
      dateText.setAttribute('y', (timelineY + 20).toString());
      dateText.setAttribute('text-anchor', 'middle');
      dateText.setAttribute('fill', theme.palette.text.secondary);
      dateText.setAttribute('font-size', '10');
      dateText.textContent = eventDate.toLocaleDateString();
      container.appendChild(dateText);
    });

  }, [data, width, height, theme]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      style={{ border: `1px solid ${theme.palette.divider}` }}
    />
  );
};

// 主要的高级图表组件
const AdvancedCharts: React.FC<AdvancedChartsProps> = ({
  config,
  title,
  onExport,
  interactive = true
}) => {
  const theme = useTheme();
  const [fullscreen, setFullscreen] = useState(false);
  const [exportFormat, setExportFormat] = useState<'png' | 'svg' | 'pdf'>('png');

  const chartWidth = config.width || (fullscreen ? window.innerWidth - 100 : 800);
  const chartHeight = config.height || (fullscreen ? window.innerHeight - 200 : 400);

  const handleExport = () => {
    if (onExport) {
      onExport(exportFormat);
    }
  };

  const renderChart = () => {
    switch (config.type) {
      case 'heatmap':
        return (
          <HeatmapChart
            data={config.data}
            width={chartWidth}
            height={chartHeight}
            theme={theme}
          />
        );
      case 'network':
        return (
          <NetworkChart
            data={config.data}
            width={chartWidth}
            height={chartHeight}
            theme={theme}
          />
        );
      case 'timeline':
        return (
          <TimelineChart
            data={config.data}
            width={chartWidth}
            height={chartHeight}
            theme={theme}
          />
        );
      default:
        return (
          <Box
            sx={{
              width: chartWidth,
              height: chartHeight,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: 1,
              borderColor: 'divider',
              color: 'text.secondary'
            }}
          >
            暂不支持的图表类型: {config.type}
          </Box>
        );
    }
  };

  const chartContent = (
    <Card sx={{ width: fullscreen ? '100vw' : 'auto', height: fullscreen ? '100vh' : 'auto' }}>
      <CardHeader
        title={title || '高级图表'}
        action={
          interactive && (
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 80 }}>
                <Select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value as any)}
                  variant="outlined"
                >
                  <MenuItem value="png">PNG</MenuItem>
                  <MenuItem value="svg">SVG</MenuItem>
                  <MenuItem value="pdf">PDF</MenuItem>
                </Select>
              </FormControl>
              
              <Tooltip title="导出图表">
                <IconButton onClick={handleExport} size="small">
                  <SaveAlt />
                </IconButton>
              </Tooltip>
              
              <Tooltip title={fullscreen ? "退出全屏" : "全屏显示"}>
                <IconButton 
                  onClick={() => setFullscreen(!fullscreen)} 
                  size="small"
                >
                  <Fullscreen />
                </IconButton>
              </Tooltip>
            </Box>
          )
        }
      />
      <CardContent>
        <Box sx={{ 
          overflow: 'auto',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          {renderChart()}
        </Box>
      </CardContent>
    </Card>
  );

  if (fullscreen) {
    return (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          bgcolor: 'background.default',
          zIndex: 9999,
          p: 2
        }}
      >
        {chartContent}
      </Box>
    );
  }

  return chartContent;
};

// 工具函数
function generateHeatmapData(): number[][] {
  const rows = 10;
  const cols = 15;
  const data: number[][] = [];
  
  for (let i = 0; i < rows; i++) {
    const row: number[] = [];
    for (let j = 0; j < cols; j++) {
      // 生成有一定规律的随机数据
      const value = Math.random() * 100 + Math.sin(i / 2) * Math.cos(j / 3) * 20;
      row.push(Math.max(0, value));
    }
    data.push(row);
  }
  
  return data;
}

function generateNetworkNodes() {
  const nodeCount = 12;
  const nodes = [];
  
  for (let i = 0; i < nodeCount; i++) {
    nodes.push({
      id: i,
      label: `节点${i + 1}`,
      size: 8 + Math.random() * 12,
      color: `hsl(${Math.random() * 360}, 70%, 50%)`
    });
  }
  
  return nodes;
}

function generateNetworkLinks(nodes: any[]) {
  const links = [];
  const linkCount = Math.floor(nodes.length * 1.5);
  
  for (let i = 0; i < linkCount; i++) {
    const source = Math.floor(Math.random() * nodes.length);
    let target = Math.floor(Math.random() * nodes.length);
    while (target === source) {
      target = Math.floor(Math.random() * nodes.length);
    }
    
    links.push({
      source,
      target,
      weight: 1 + Math.random() * 5
    });
  }
  
  return links;
}

function generateTimelineData() {
  const events = [
    { title: '项目启动', date: '2024-01-01', color: '#4CAF50' },
    { title: '需求分析', date: '2024-02-15', color: '#2196F3' },
    { title: '设计阶段', date: '2024-03-10', color: '#FF9800' },
    { title: '开发开始', date: '2024-04-01', color: '#E91E63' },
    { title: '测试阶段', date: '2024-06-15', color: '#9C27B0' },
    { title: '上线部署', date: '2024-08-01', color: '#00BCD4' },
    { title: '优化改进', date: '2024-10-15', color: '#8BC34A' }
  ];
  
  return events;
}

function interpolateColor(color1: string, color2: string, factor: number): string {
  // 简单的颜色插值函数
  const hex1 = color1.replace('#', '');
  const hex2 = color2.replace('#', '');
  
  const r1 = parseInt(hex1.substr(0, 2), 16);
  const g1 = parseInt(hex1.substr(2, 2), 16);
  const b1 = parseInt(hex1.substr(4, 2), 16);
  
  const r2 = parseInt(hex2.substr(0, 2), 16);
  const g2 = parseInt(hex2.substr(2, 2), 16);
  const b2 = parseInt(hex2.substr(4, 2), 16);
  
  const r = Math.round(r1 + (r2 - r1) * factor);
  const g = Math.round(g1 + (g2 - g1) * factor);
  const b = Math.round(b1 + (b2 - b1) * factor);
  
  return `rgb(${r}, ${g}, ${b})`;
}

export default AdvancedCharts;
export type { ChartConfig, AdvancedChartsProps }; 