/**
 * 增强版3D思维空间组件
 * 支持三层思维模型可视化、实时协作、XR体验
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import {
  Scene,
  PerspectiveCamera,
  WebGLRenderer,
  AmbientLight,
  DirectionalLight,
  PointLight,
  PlaneGeometry,
  MeshPhongMaterial,
  MeshLambertMaterial,
  Mesh,
  BoxGeometry,
  SphereGeometry,
  ConeGeometry,
  CylinderGeometry,
  Vector3,
  Color,
  GridHelper,
  Clock,
  Raycaster,
  Vector2,
  Group,
  LineBasicMaterial,
  BufferGeometry,
  Line,
  DoubleSide,
  Fog,
  TextureLoader,
  CanvasTexture,
  SpriteMaterial,
  Sprite
} from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { 
  Box, 
  Typography, 
  Paper, 
  Fab, 
  Tooltip, 
  Card, 
  CardContent,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Slider,
  FormControlLabel,
  Switch,
  Grid
} from '@mui/material';
import {
  Add,
  Remove,
  CenterFocusStrong,
  Settings,
  Fullscreen,
  Psychology,
  AccountTree,
  Lightbulb,
  ViewInAr,
  Visibility,
  VisibilityOff,
  Speed,
  Tune,
  Link,
  ColorLens
} from '@mui/icons-material';

// 思维层级类型
export type ThinkingLayer = 'visual' | 'logical' | 'creative';

// 思维节点类型
export interface EnhancedThinkingNode {
  id: string;
  layer: ThinkingLayer;
  content: string;
  position: Vector3;
  size: number;
  intensity: number; // 思维强度 0-1
  connections: string[];
  metadata: {
    createdAt: Date;
    userId?: string;
    tags: string[];
    type: 'concept' | 'idea' | 'insight' | 'question' | 'solution';
  };
  visual: {
    color: string;
    opacity: number;
    glow: boolean;
    animated: boolean;
  };
}

// 连接线类型
export interface ThinkingConnection {
  id: string;
  from: string;
  to: string;
  strength: number;
  type: 'association' | 'causality' | 'similarity' | 'contradiction';
  animated: boolean;
}

// 用户光标类型
export interface UserCursor {
  userId: string;
  userName: string;
  position: Vector3;
  color: string;
  visible: boolean;
}

interface EnhancedThinkingSpaceProps {
  width?: number;
  height?: number;
  nodes?: EnhancedThinkingNode[];
  connections?: ThinkingConnection[];
  userCursors?: UserCursor[];
  onNodeClick?: (node: EnhancedThinkingNode) => void;
  onNodeCreate?: (position: Vector3, layer: ThinkingLayer) => void;
  onConnectionCreate?: (fromId: string, toId: string) => void;
  onCameraMove?: (position: Vector3, target: Vector3) => void;
  isCollaborative?: boolean;
  showLayers?: { visual: boolean; logical: boolean; creative: boolean };
  immersiveMode?: boolean;
  xrEnabled?: boolean;
}

const EnhancedThinkingSpace: React.FC<EnhancedThinkingSpaceProps> = ({
  width = 1000,
  height = 700,
  nodes = [],
  connections = [],
  userCursors = [],
  onNodeClick,
  onNodeCreate,
  onConnectionCreate,
  onCameraMove,
  isCollaborative = false,
  showLayers = { visual: true, logical: true, creative: true },
  immersiveMode = false,
  xrEnabled = false
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<Scene | null>(null);
  const rendererRef = useRef<WebGLRenderer | null>(null);
  const cameraRef = useRef<PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const clockRef = useRef<Clock>(new Clock());
  const raycasterRef = useRef<Raycaster>(new Raycaster());
  const mouseRef = useRef<Vector2>(new Vector2());
  
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<EnhancedThinkingNode | null>(null);
  const [creationMode, setCreationMode] = useState<ThinkingLayer | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [layerVisibility, setLayerVisibility] = useState(showLayers);
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [fogEnabled, setFogEnabled] = useState(true);

  // 层级配置
  const layerConfig = useMemo(() => ({
    visual: {
      color: '#2196F3',
      height: 2,
      icon: '👁️',
      name: '形象思维层'
    },
    logical: {
      color: '#FF5722',
      height: 0,
      icon: '🧠',
      name: '逻辑思维层'
    },
    creative: {
      color: '#4CAF50',
      height: -2,
      icon: '💡',
      name: '创造思维层'
    }
  }), []);

  // 初始化场景
  const initializeScene = useCallback(() => {
    if (!mountRef.current) return;

    // 创建场景
    const scene = new Scene();
    scene.background = new Color(immersiveMode ? '#000011' : '#f5f5f5');
    
    // 添加雾效
    if (fogEnabled) {
      scene.fog = new Fog(scene.background.getHex(), 50, 200);
    }
    
    sceneRef.current = scene;

    // 创建相机
    const camera = new PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(15, 10, 15);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // 创建渲染器
    const renderer = new WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = 2; // PCFSoftShadowMap
    renderer.outputEncoding = 3001; // sRGBEncoding
    renderer.toneMapping = 1; // ReinhardToneMapping
    rendererRef.current = renderer;

    // XR设置
    if (xrEnabled && 'xr' in navigator) {
      renderer.xr.enabled = true;
    }

    // 添加到DOM
    if (mountRef.current) {
      mountRef.current.appendChild(renderer.domElement);
    }

    // 创建控制器
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controls.enablePan = true;
    controls.maxDistance = 100;
    controls.minDistance = 5;
    controlsRef.current = controls;

    // 添加光源系统
    setupLighting(scene);
    
    // 创建思维层级平面
    createThinkingLayers(scene);
    
    // 添加环境元素
    createEnvironment(scene);

    // 事件监听
    setupEventListeners(renderer, camera, scene);

    // 开始渲染循环
    startRenderLoop();

  }, [width, height, immersiveMode, fogEnabled, xrEnabled]);

  // 设置光照系统
  const setupLighting = (scene: Scene) => {
    // 环境光
    const ambientLight = new AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    // 主光源
    const mainLight = new DirectionalLight(0xffffff, 1);
    mainLight.position.set(20, 20, 20);
    mainLight.castShadow = true;
    mainLight.shadow.mapSize.width = 2048;
    mainLight.shadow.mapSize.height = 2048;
    scene.add(mainLight);

    // 填充光
    const fillLight = new DirectionalLight(0x8888ff, 0.3);
    fillLight.position.set(-10, 10, -10);
    scene.add(fillLight);

    // 点光源（营造氛围）
    const pointLight = new PointLight(0x66aaff, 0.5, 50);
    pointLight.position.set(0, 5, 0);
    scene.add(pointLight);
  };

  // 创建思维层级
  const createThinkingLayers = (scene: Scene) => {
    Object.entries(layerConfig).forEach(([layer, config]) => {
      if (!layerVisibility[layer as ThinkingLayer]) return;

      // 创建层级平面
      const geometry = new PlaneGeometry(30, 30);
      const material = new MeshPhongMaterial({
        color: config.color,
        transparent: true,
        opacity: 0.1,
        side: DoubleSide
      });
      
      const plane = new Mesh(geometry, material);
      plane.rotation.x = -Math.PI / 2;
      plane.position.y = config.height;
      plane.userData = { type: 'layer', layer: layer };
      scene.add(plane);

      // 添加层级标签
      const labelTexture = createTextTexture(`${config.icon} ${config.name}`, config.color);
      const labelMaterial = new SpriteMaterial({ map: labelTexture });
      const label = new Sprite(labelMaterial);
      label.position.set(-12, config.height + 1, -12);
      label.scale.set(4, 2, 1);
      scene.add(label);
    });
  };

  // 创建环境元素
  const createEnvironment = (scene: Scene) => {
    // 网格辅助线
    const gridHelper = new GridHelper(30, 30, 0x888888, 0xcccccc);
    gridHelper.position.y = -5;
    scene.add(gridHelper);

    // 边界指示器
    const boundaryGeometry = new BoxGeometry(0.2, 10, 0.2);
    const boundaryMaterial = new MeshPhongMaterial({ color: 0x666666 });
    
    for (let i = 0; i < 4; i++) {
      const boundary = new Mesh(boundaryGeometry, boundaryMaterial);
      const angle = (i / 4) * Math.PI * 2;
      boundary.position.set(
        Math.cos(angle) * 15,
        0,
        Math.sin(angle) * 15
      );
      scene.add(boundary);
    }
  };

  // 创建文本纹理
  const createTextTexture = (text: string, color: string) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    canvas.width = 512;
    canvas.height = 256;
    
    context.fillStyle = 'rgba(255, 255, 255, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.fillStyle = color;
    context.font = 'bold 48px Arial';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    return new CanvasTexture(canvas);
  };

  // 事件监听设置
  const setupEventListeners = (renderer: WebGLRenderer, camera: PerspectiveCamera, scene: Scene) => {
    const handleMouseClick = (event: MouseEvent) => {
      if (creationMode) {
        handleNodeCreation(event, camera, scene);
      } else {
        handleNodeSelection(event, camera, scene);
      }
    };

    const handleMouseMove = (event: MouseEvent) => {
      if (isCollaborative) {
        // 广播鼠标位置用于协作
        const rect = renderer.domElement.getBoundingClientRect();
        const position = new Vector3(
          ((event.clientX - rect.left) / rect.width) * 2 - 1,
          -((event.clientY - rect.top) / rect.height) * 2 + 1,
          0
        );
        // TODO: 发送位置到协作服务
      }
    };

    renderer.domElement.addEventListener('click', handleMouseClick);
    renderer.domElement.addEventListener('mousemove', handleMouseMove);
  };

  // 处理节点创建
  const handleNodeCreation = (event: MouseEvent, camera: PerspectiveCamera, scene: Scene) => {
    if (!creationMode) return;

    const rect = rendererRef.current!.domElement.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycasterRef.current.setFromCamera(mouseRef.current, camera);
    
    // 在对应层级创建节点
    const layerHeight = layerConfig[creationMode].height;
    const position = new Vector3(
      mouseRef.current.x * 10,
      layerHeight,
      mouseRef.current.y * 10
    );

    onNodeCreate?.(position, creationMode);
    setCreationMode(null);
  };

  // 处理节点选择
  const handleNodeSelection = (event: MouseEvent, camera: PerspectiveCamera, scene: Scene) => {
    const rect = rendererRef.current!.domElement.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycasterRef.current.setFromCamera(mouseRef.current, camera);
    const intersects = raycasterRef.current.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
      const clickedObject = intersects[0].object;
      const userData = clickedObject.userData;
      
      if (userData?.type === 'thinking_node') {
        setSelectedNode(userData.node);
        onNodeClick?.(userData.node);
      }
    }
  };

  // 渲染循环
  const startRenderLoop = () => {
    const animate = () => {
      requestAnimationFrame(animate);
      
      if (controlsRef.current) {
        controlsRef.current.update();
      }

      const deltaTime = clockRef.current.getDelta() * animationSpeed;
      
      // 更新节点动画
      updateNodeAnimations(deltaTime);
      
      // 更新连接线动画
      updateConnectionAnimations(deltaTime);
      
      // 更新用户光标
      updateUserCursors();

      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    
    animate();
  };

  // 更新节点动画
  const updateNodeAnimations = (deltaTime: number) => {
    if (!sceneRef.current) return;

    sceneRef.current.children.forEach(child => {
      if (child.userData?.type === 'thinking_node' && child.userData?.animated) {
        child.rotation.y += deltaTime * 2;
        
        // 呼吸动画
        const scale = 1 + Math.sin(clockRef.current.elapsedTime * 3) * 0.1;
        child.scale.setScalar(scale);
      }
    });
  };

  // 更新连接线动画
  const updateConnectionAnimations = (deltaTime: number) => {
    // TODO: 实现连接线动画效果
  };

  // 更新用户光标
  const updateUserCursors = () => {
    // TODO: 渲染其他用户的3D光标
  };

  // 渲染思维节点
  useEffect(() => {
    if (!sceneRef.current) return;

    // 清除现有节点
    const existingNodes = sceneRef.current.children.filter(child => 
      child.userData?.type === 'thinking_node'
    );
    existingNodes.forEach(node => sceneRef.current!.remove(node));

    // 添加新节点
    nodes.forEach(node => {
      if (!layerVisibility[node.layer]) return;

      const geometry = new SphereGeometry(node.size, 16, 12);
      const material = new MeshPhongMaterial({
        color: node.visual.color,
        transparent: true,
        opacity: node.visual.opacity,
        emissive: node.visual.glow ? new Color(node.visual.color).multiplyScalar(0.2) : new Color(0)
      });

      const mesh = new Mesh(geometry, material);
      mesh.position.copy(node.position);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.userData = {
        type: 'thinking_node',
        node: node,
        animated: node.visual.animated
      };

      sceneRef.current!.add(mesh);

      // 添加节点标签
      if (node.content) {
        const labelTexture = createTextTexture(node.content.substring(0, 20), node.visual.color);
        const labelMaterial = new SpriteMaterial({ map: labelTexture });
        const label = new Sprite(labelMaterial);
        label.position.copy(node.position);
        label.position.y += node.size + 1;
        label.scale.set(3, 1.5, 1);
        sceneRef.current!.add(label);
      }
    });

  }, [nodes, layerVisibility]);

  // 渲染连接线
  useEffect(() => {
    if (!sceneRef.current) return;

    // 清除现有连接线
    const existingConnections = sceneRef.current.children.filter(child => 
      child.userData?.type === 'connection'
    );
    existingConnections.forEach(connection => sceneRef.current!.remove(connection));

    // 添加新连接线
    connections.forEach(connection => {
      const fromNode = nodes.find(n => n.id === connection.from);
      const toNode = nodes.find(n => n.id === connection.to);
      
      if (fromNode && toNode) {
        const geometry = new BufferGeometry().setFromPoints([
          fromNode.position,
          toNode.position
        ]);
        
        const material = new LineBasicMaterial({
          color: connection.type === 'causality' ? 0xff0000 : 
                 connection.type === 'similarity' ? 0x00ff00 : 0x0000ff,
          opacity: connection.strength,
          transparent: true
        });

        const line = new Line(geometry, material);
        line.userData = {
          type: 'connection',
          connection: connection
        };

        sceneRef.current!.add(line);
      }
    });

  }, [connections, nodes]);

  // 初始化场景
  useEffect(() => {
    initializeScene();

    return () => {
      if (rendererRef.current && mountRef.current) {
        mountRef.current.removeChild(rendererRef.current.domElement);
      }
    };
  }, [initializeScene]);

  // 控制函数
  const handleZoomIn = () => {
    if (cameraRef.current) {
      cameraRef.current.position.multiplyScalar(0.8);
    }
  };

  const handleZoomOut = () => {
    if (cameraRef.current) {
      cameraRef.current.position.multiplyScalar(1.2);
    }
  };

  const handleResetView = () => {
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(15, 10, 15);
      controlsRef.current.target.set(0, 0, 0);
      controlsRef.current.update();
    }
  };

  const toggleLayer = (layer: ThinkingLayer) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  return (
    <Box sx={{ position: 'relative', width, height }}>
      {/* 3D画布容器 */}
      <div ref={mountRef} style={{ width: '100%', height: '100%', borderRadius: '8px', overflow: 'hidden' }} />

      {/* 控制面板 */}
      <Paper 
        sx={{ 
          position: 'absolute', 
          top: 16, 
          right: 16, 
          p: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          backgroundColor: 'rgba(255, 255, 255, 0.9)'
        }}
      >
        <Tooltip title="放大">
          <IconButton size="small" onClick={handleZoomIn}>
            <Add />
          </IconButton>
        </Tooltip>

        <Tooltip title="缩小">
          <IconButton size="small" onClick={handleZoomOut}>
            <Remove />
          </IconButton>
        </Tooltip>

        <Tooltip title="重置视图">
          <IconButton size="small" onClick={handleResetView}>
            <CenterFocusStrong />
          </IconButton>
        </Tooltip>

        <Tooltip title="设置">
          <IconButton size="small" onClick={() => setSettingsOpen(true)}>
            <Settings />
          </IconButton>
        </Tooltip>

        {xrEnabled && (
          <Tooltip title="VR模式">
            <IconButton size="small">
              <ViewInAr />
            </IconButton>
          </Tooltip>
        )}
      </Paper>

      {/* 层级控制 */}
      <Paper 
        sx={{ 
          position: 'absolute', 
          top: 16, 
          left: 16, 
          p: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.9)'
        }}
      >
        <Typography variant="subtitle2" gutterBottom>
          思维层级
        </Typography>
        {Object.entries(layerConfig).map(([layer, config]) => (
          <Box key={layer} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <IconButton 
              size="small" 
              onClick={() => toggleLayer(layer as ThinkingLayer)}
              sx={{ mr: 1 }}
            >
              {layerVisibility[layer as ThinkingLayer] ? <Visibility /> : <VisibilityOff />}
            </IconButton>
            <Chip 
              label={`${config.icon} ${config.name}`}
              size="small"
              sx={{ backgroundColor: config.color, color: 'white' }}
            />
          </Box>
        ))}
      </Paper>

      {/* 创建模式选择器 */}
      <Paper 
        sx={{ 
          position: 'absolute', 
          bottom: 16, 
          left: 16, 
          p: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.9)'
        }}
      >
        <Typography variant="subtitle2" gutterBottom>
          创建节点
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {Object.entries(layerConfig).map(([layer, config]) => (
            <Tooltip key={layer} title={`创建${config.name}节点`}>
              <Fab
                size="small"
                color={creationMode === layer ? 'primary' : 'default'}
                onClick={() => setCreationMode(creationMode === layer ? null : layer as ThinkingLayer)}
                sx={{ 
                  backgroundColor: creationMode === layer ? config.color : undefined,
                  '&:hover': { backgroundColor: config.color }
                }}
              >
                <span style={{ fontSize: '18px' }}>{config.icon}</span>
              </Fab>
            </Tooltip>
          ))}
        </Box>
      </Paper>

      {/* 节点信息面板 */}
      {selectedNode && (
        <Card 
          sx={{ 
            position: 'absolute', 
            bottom: 16, 
            right: 16, 
            maxWidth: 300,
            backgroundColor: 'rgba(255, 255, 255, 0.95)'
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {layerConfig[selectedNode.layer].icon} 思维节点
            </Typography>
            <Typography variant="body2" paragraph>
              {selectedNode.content}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {selectedNode.metadata.tags.map(tag => (
                <Chip key={tag} label={tag} size="small" />
              ))}
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              强度: {(selectedNode.intensity * 100).toFixed(0)}% | 
              连接: {selectedNode.connections.length}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* 设置对话框 */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>3D空间设置</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography gutterBottom>动画速度</Typography>
              <Slider
                value={animationSpeed}
                onChange={(_, value) => setAnimationSpeed(value as number)}
                min={0.1}
                max={3}
                step={0.1}
                marks={[
                  { value: 0.5, label: '慢' },
                  { value: 1, label: '正常' },
                  { value: 2, label: '快' }
                ]}
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={fogEnabled}
                    onChange={(e) => setFogEnabled(e.target.checked)}
                  />
                }
                label="启用雾效"
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={immersiveMode}
                    onChange={(e) => window.location.reload()} // 需要重新初始化
                  />
                }
                label="沉浸模式"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedThinkingSpace; 