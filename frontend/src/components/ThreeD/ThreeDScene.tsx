/**
 * 3D场景组件
 * 基于Three.js实现思维空间可视化
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  Scene,
  PerspectiveCamera,
  WebGLRenderer,
  AmbientLight,
  DirectionalLight,
  PlaneGeometry,
  MeshLambertMaterial,
  Mesh,
  BoxGeometry,
  SphereGeometry,
  Vector3,
  Color,
  TextureLoader,
  GridHelper,
  AxesHelper,
  Clock,
  Raycaster,
  Vector2
} from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { Box, Typography, Paper, Fab, Tooltip } from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  CenterFocusStrong as CenterIcon,
  Settings as SettingsIcon,
  Fullscreen as FullscreenIcon
} from '@mui/icons-material';

// 3D对象类型
export interface ThreeDObject {
  id: string;
  type: 'cube' | 'sphere' | 'text' | 'thinking_bubble' | 'connection';
  position: { x: number; y: number; z: number };
  rotation?: { x: number; y: number; z: number };
  scale?: { x: number; y: number; z: number };
  color?: string;
  data?: any;
  userData?: any;
}

// 思维节点类型
export interface ThinkingNode {
  id: string;
  type: 'visual' | 'logical' | 'creative';
  content: string;
  position: { x: number; y: number; z: number };
  connections: string[];
  strength: number;
  color?: string;
}

interface ThreeDSceneProps {
  width?: number;
  height?: number;
  objects?: ThreeDObject[];
  thinkingNodes?: ThinkingNode[];
  onObjectClick?: (object: ThreeDObject) => void;
  onNodeClick?: (node: ThinkingNode) => void;
  interactive?: boolean;
  showGrid?: boolean;
  showAxes?: boolean;
  backgroundColor?: string;
  cameraPosition?: { x: number; y: number; z: number };
  autoRotate?: boolean;
}

export const ThreeDScene: React.FC<ThreeDSceneProps> = ({
  width = 800,
  height = 600,
  objects = [],
  thinkingNodes = [],
  onObjectClick,
  onNodeClick,
  interactive = true,
  showGrid = true,
  showAxes = false,
  backgroundColor = '#f0f0f0',
  cameraPosition = { x: 5, y: 5, z: 5 },
  autoRotate = false
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
  const [zoom, setZoom] = useState(1);
  const [selectedObject, setSelectedObject] = useState<ThreeDObject | null>(null);

  // 初始化3D场景
  useEffect(() => {
    if (!mountRef.current) return;

    // 创建场景
    const scene = new Scene();
    scene.background = new Color(backgroundColor);
    sceneRef.current = scene;

    // 创建相机
    const camera = new PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(cameraPosition.x, cameraPosition.y, cameraPosition.z);
    cameraRef.current = camera;

    // 创建渲染器
    const renderer = new WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    rendererRef.current = renderer;

    // 添加到DOM
    mountRef.current.appendChild(renderer.domElement);

    // 添加控制器
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 0.5;
    controlsRef.current = controls;

    // 添加光源
    const ambientLight = new AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);

    const directionalLight = new DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // 添加网格
    if (showGrid) {
      const gridHelper = new GridHelper(20, 20);
      gridHelper.position.y = -2;
      scene.add(gridHelper);
    }

    // 添加坐标轴
    if (showAxes) {
      const axesHelper = new AxesHelper(5);
      scene.add(axesHelper);
    }

    // 添加地面
    const groundGeometry = new PlaneGeometry(20, 20);
    const groundMaterial = new MeshLambertMaterial({ color: 0xffffff });
    const ground = new Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -2;
    ground.receiveShadow = true;
    scene.add(ground);

    // 鼠标交互
    const handleMouseClick = (event: MouseEvent) => {
      if (!interactive) return;

      const rect = renderer.domElement.getBoundingClientRect();
      mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycasterRef.current.setFromCamera(mouseRef.current, camera);
      const intersects = raycasterRef.current.intersectObjects(scene.children, true);

      if (intersects.length > 0) {
        const clickedObject = intersects[0].object;
        const userData = clickedObject.userData;
        
        if (userData?.type === 'object' && onObjectClick) {
          onObjectClick(userData.data);
          setSelectedObject(userData.data);
        } else if (userData?.type === 'node' && onNodeClick) {
          onNodeClick(userData.data);
        }
      }
    };

    renderer.domElement.addEventListener('click', handleMouseClick);

    // 动画循环
    const animate = () => {
      requestAnimationFrame(animate);
      
      controls.update();
      
      // 自动旋转思维节点
      scene.children.forEach(child => {
        if (child.userData?.autoRotate) {
          child.rotation.y += 0.01;
        }
      });
      
      renderer.render(scene, camera);
    };
    animate();

    // 清理函数
    return () => {
      renderer.domElement.removeEventListener('click', handleMouseClick);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [width, height, backgroundColor, interactive, showGrid, showAxes, autoRotate]);

  // 更新3D对象
  useEffect(() => {
    if (!sceneRef.current) return;

    // 清除现有对象
    const objectsToRemove = sceneRef.current.children.filter(
      child => child.userData?.type === 'object'
    );
    objectsToRemove.forEach(obj => sceneRef.current!.remove(obj));

    // 添加新对象
    objects.forEach(obj => {
      let geometry;
      let material;

      switch (obj.type) {
        case 'cube':
          geometry = new BoxGeometry(1, 1, 1);
          material = new MeshLambertMaterial({ color: obj.color || '#4CAF50' });
          break;
        case 'sphere':
          geometry = new SphereGeometry(0.5, 32, 32);
          material = new MeshLambertMaterial({ color: obj.color || '#2196F3' });
          break;
        default:
          geometry = new BoxGeometry(1, 1, 1);
          material = new MeshLambertMaterial({ color: obj.color || '#9E9E9E' });
      }

      const mesh = new Mesh(geometry, material);
      mesh.position.set(obj.position.x, obj.position.y, obj.position.z);
      
      if (obj.rotation) {
        mesh.rotation.set(obj.rotation.x, obj.rotation.y, obj.rotation.z);
      }
      
      if (obj.scale) {
        mesh.scale.set(obj.scale.x, obj.scale.y, obj.scale.z);
      }

      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.userData = { type: 'object', data: obj };

      sceneRef.current!.add(mesh);
    });
  }, [objects]);

  // 更新思维节点
  useEffect(() => {
    if (!sceneRef.current) return;

    // 清除现有节点
    const nodesToRemove = sceneRef.current.children.filter(
      child => child.userData?.type === 'node'
    );
    nodesToRemove.forEach(node => sceneRef.current!.remove(node));

    // 添加思维节点
    thinkingNodes.forEach(node => {
      const geometry = new SphereGeometry(0.3 + node.strength * 0.3, 32, 32);
      
      let color;
      switch (node.type) {
        case 'visual':
          color = '#FF5722'; // 橙红色 - 形象思维
          break;
        case 'logical':
          color = '#2196F3'; // 蓝色 - 逻辑思维
          break;
        case 'creative':
          color = '#9C27B0'; // 紫色 - 创造思维
          break;
        default:
          color = '#4CAF50';
      }

      const material = new MeshLambertMaterial({ 
        color: node.color || color,
        transparent: true,
        opacity: 0.8
      });
      
      const mesh = new Mesh(geometry, material);
      mesh.position.set(node.position.x, node.position.y, node.position.z);
      mesh.castShadow = true;
      mesh.userData = { 
        type: 'node', 
        data: node,
        autoRotate: true
      };

      sceneRef.current!.add(mesh);

      // 添加连接线
      // TODO: 实现节点之间的连接线可视化
    });
  }, [thinkingNodes]);

  // 缩放控制
  const handleZoomIn = () => {
    if (cameraRef.current) {
      cameraRef.current.position.multiplyScalar(0.9);
      setZoom(zoom * 1.1);
    }
  };

  const handleZoomOut = () => {
    if (cameraRef.current) {
      cameraRef.current.position.multiplyScalar(1.1);
      setZoom(zoom * 0.9);
    }
  };

  // 重置视角
  const handleResetView = () => {
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(cameraPosition.x, cameraPosition.y, cameraPosition.z);
      controlsRef.current.reset();
      setZoom(1);
    }
  };

  // 全屏切换
  const handleFullscreen = () => {
    if (!document.fullscreenElement) {
      mountRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ position: 'relative', overflow: 'hidden' }}>
      {/* 3D渲染容器 */}
      <Box
        ref={mountRef}
        sx={{
          width,
          height,
          position: 'relative',
          cursor: interactive ? 'pointer' : 'default'
        }}
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
          <Fab size="small" color="primary" onClick={handleZoomIn}>
            <AddIcon />
          </Fab>
        </Tooltip>
        
        <Tooltip title="缩小" placement="left">
          <Fab size="small" color="primary" onClick={handleZoomOut}>
            <RemoveIcon />
          </Fab>
        </Tooltip>
        
        <Tooltip title="重置视角" placement="left">
          <Fab size="small" color="secondary" onClick={handleResetView}>
            <CenterIcon />
          </Fab>
        </Tooltip>
        
        <Tooltip title="全屏" placement="left">
          <Fab size="small" onClick={handleFullscreen}>
            <FullscreenIcon />
          </Fab>
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
          对象: {objects.length} | 节点: {thinkingNodes.length}
        </Typography>
        <Typography variant="caption" display="block">
          缩放: {zoom.toFixed(1)}x
        </Typography>
        {selectedObject && (
          <Typography variant="caption" display="block" color="primary">
            选中: {selectedObject.type} ({selectedObject.id})
          </Typography>
        )}
      </Paper>
    </Paper>
  );
};

export default ThreeDScene; 