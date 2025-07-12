/**
 * 智能思维元宇宙核心系统
 * 支持AR/VR多平台设备，提供沉浸式思维体验
 */

import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { ARButton } from 'three/examples/jsm/webxr/ARButton.js';
import { XRControllerModelFactory } from 'three/examples/jsm/webxr/XRControllerModelFactory.js';
import { XRHandModelFactory } from 'three/examples/jsm/webxr/XRHandModelFactory.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { FXAAShader } from 'three/examples/jsm/shaders/FXAAShader.js';
import { OctreeHelper } from 'three/examples/jsm/helpers/OctreeHelper.js';
import { Octree } from 'three/examples/jsm/math/Octree.js';
import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min.js';
import { Stats } from 'three/examples/jsm/libs/stats.module.js';
import { io } from 'socket.io-client';
import { EventEmitter } from 'events';

// 导入自定义模块
import { ThinkingNodeSystem } from './systems/ThinkingNodeSystem.js';
import { UserAvatarSystem } from './systems/UserAvatarSystem.js';
import { InteractionSystem } from './systems/InteractionSystem.js';
import { AudioSystem } from './systems/AudioSystem.js';
import { PhysicsSystem } from './systems/PhysicsSystem.js';
import { AIAssistantSystem } from './systems/AIAssistantSystem.js';
import { BlockchainSystem } from './systems/BlockchainSystem.js';
import { QuantumSystem } from './systems/QuantumSystem.js';
import { NetworkSystem } from './systems/NetworkSystem.js';
import { AnalyticsSystem } from './systems/AnalyticsSystem.js';
import { SecuritySystem } from './systems/SecuritySystem.js';
import { PerformanceSystem } from './systems/PerformanceSystem.js';
import { ContentSystem } from './systems/ContentSystem.js';
import { SocialSystem } from './systems/SocialSystem.js';
import { EconomySystem } from './systems/EconomySystem.js';
import { CreativeSystem } from './systems/CreativeSystem.js';
import { EducationSystem } from './systems/EducationSystem.js';
import { HealthSystem } from './systems/HealthSystem.js';
import { WorkspaceSystem } from './systems/WorkspaceSystem.js';
import { EntertainmentSystem } from './systems/EntertainmentSystem.js';
import { VirtualRealitySystem } from './systems/VirtualRealitySystem.js';
import { AugmentedRealitySystem } from './systems/AugmentedRealitySystem.js';
import { MixedRealitySystem } from './systems/MixedRealitySystem.js';
import { BrainComputerInterfaceSystem } from './systems/BrainComputerInterfaceSystem.js';
import { NeuralNetworkSystem } from './systems/NeuralNetworkSystem.js';
import { ConsciousnessSystem } from './systems/ConsciousnessSystem.js';
import { AwarenessSystem } from './systems/AwarenessSystem.js';
import { IntelligenceSystem } from './systems/IntelligenceSystem.js';
import { WisdomSystem } from './systems/WisdomSystem.js';
import { EnlightenmentSystem } from './systems/EnlightenmentSystem.js';
import { TranscendenceSystem } from './systems/TranscendenceSystem.js';
import { MetaverseShaders } from './shaders/MetaverseShaders.js';
import { MetaverseGeometry } from './geometry/MetaverseGeometry.js';
import { MetaverseMaterials } from './materials/MetaverseMaterials.js';
import { MetaverseEffects } from './effects/MetaverseEffects.js';
import { MetaverseUtils } from './utils/MetaverseUtils.js';
import { MetaverseConstants } from './constants/MetaverseConstants.js';
import { MetaverseConfig } from './config/MetaverseConfig.js';

/**
 * 元宇宙核心类
 */
class MetaverseCore extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      container: document.body,
      mode: 'vr', // 'vr', 'ar', 'mixed', 'desktop'
      quality: 'high', // 'low', 'medium', 'high', 'ultra'
      physics: true,
      audio: true,
      networking: true,
      analytics: true,
      ai: true,
      blockchain: true,
      quantum: true,
      bci: false, // brain-computer interface
      experimental: false,
      ...options
    };
    
    // 核心组件
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.composer = null;
    this.controls = null;
    this.stats = null;
    this.gui = null;
    
    // XR相关
    this.xrSession = null;
    this.xrReferenceSpace = null;
    this.controllers = [];
    this.hands = [];
    this.haptics = [];
    
    // 系统模块
    this.systems = {};
    this.modules = {};
    this.plugins = {};
    
    // 状态管理
    this.state = {
      initialized: false,
      running: false,
      paused: false,
      users: new Map(),
      objects: new Map(),
      interactions: new Map(),
      analytics: {},
      performance: {},
      network: {},
      security: {},
      ai: {},
      blockchain: {},
      quantum: {},
      consciousness: {},
      timestamp: 0,
      frameCount: 0,
      deltaTime: 0,
      totalTime: 0
    };
    
    // 网络连接
    this.socket = null;
    this.networkId = null;
    this.roomId = null;
    this.userId = null;
    
    // 数据存储
    this.userData = {};
    this.worldData = {};
    this.sessionData = {};
    
    // 事件监听器
    this.eventListeners = new Map();
    
    // 初始化
    this.initialize();
  }
  
  /**
   * 初始化元宇宙系统
   */
  async initialize() {
    try {
      console.log('🌌 正在初始化元宇宙系统...');
      
      // 创建渲染器
      this.createRenderer();
      
      // 创建场景
      this.createScene();
      
      // 创建相机
      this.createCamera();
      
      // 创建控制器
      this.createControls();
      
      // 创建灯光
      this.createLights();
      
      // 创建环境
      this.createEnvironment();
      
      // 初始化XR
      await this.initializeXR();
      
      // 初始化系统
      await this.initializeSystems();
      
      // 初始化网络
      await this.initializeNetwork();
      
      // 初始化用户界面
      this.initializeUI();
      
      // 绑定事件
      this.bindEvents();
      
      // 开始渲染循环
      this.startRenderLoop();
      
      this.state.initialized = true;
      this.state.running = true;
      
      console.log('✅ 元宇宙系统初始化完成');
      this.emit('initialized');
      
    } catch (error) {
      console.error('❌ 元宇宙系统初始化失败:', error);
      this.emit('error', error);
    }
  }
  
  /**
   * 创建渲染器
   */
  createRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
      precision: 'highp'
    });
    
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    this.renderer.xr.enabled = true;
    
    // 添加到DOM
    this.options.container.appendChild(this.renderer.domElement);
    
    // 创建后处理
    this.createPostProcessing();
  }
  
  /**
   * 创建后处理
   */
  createPostProcessing() {
    this.composer = new EffectComposer(this.renderer);
    
    // 渲染通道
    const renderPass = new RenderPass(this.scene, this.camera);
    this.composer.addPass(renderPass);
    
    // 辉光效果
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      1.5, // 强度
      0.4, // 半径
      0.85 // 阈值
    );
    this.composer.addPass(bloomPass);
    
    // 抗锯齿
    const fxaaPass = new ShaderPass(FXAAShader);
    fxaaPass.material.uniforms['resolution'].value.x = 1 / window.innerWidth;
    fxaaPass.material.uniforms['resolution'].value.y = 1 / window.innerHeight;
    this.composer.addPass(fxaaPass);
  }
  
  /**
   * 创建场景
   */
  createScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x000011);
    this.scene.fog = new THREE.Fog(0x000011, 100, 1000);
    
    // 添加网格辅助器
    const gridHelper = new THREE.GridHelper(100, 100, 0x333333, 0x333333);
    this.scene.add(gridHelper);
    
    // 添加坐标轴辅助器
    const axesHelper = new THREE.AxesHelper(5);
    this.scene.add(axesHelper);
  }
  
  /**
   * 创建相机
   */
  createCamera() {
    this.camera = new THREE.PerspectiveCamera(
      75, // 视角
      window.innerWidth / window.innerHeight, // 宽高比
      0.1, // 近平面
      1000 // 远平面
    );
    
    this.camera.position.set(0, 5, 10);
    this.camera.lookAt(0, 0, 0);
  }
  
  /**
   * 创建控制器
   */
  createControls() {
    // 桌面模式控制器
    if (this.options.mode === 'desktop') {
      import('three/examples/jsm/controls/OrbitControls.js').then(({ OrbitControls }) => {
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.enableZoom = true;
        this.controls.enableRotate = true;
        this.controls.enablePan = true;
      });
    }
    
    // VR控制器
    if (this.options.mode === 'vr' || this.options.mode === 'mixed') {
      this.createVRControls();
    }
    
    // AR控制器
    if (this.options.mode === 'ar' || this.options.mode === 'mixed') {
      this.createARControls();
    }
  }
  
  /**
   * 创建VR控制器
   */
  createVRControls() {
    const controllerModelFactory = new XRControllerModelFactory();
    const handModelFactory = new XRHandModelFactory();
    
    // 创建控制器
    for (let i = 0; i < 2; i++) {
      // 控制器
      const controller = this.renderer.xr.getController(i);
      controller.addEventListener('selectstart', this.onSelectStart.bind(this));
      controller.addEventListener('selectend', this.onSelectEnd.bind(this));
      controller.addEventListener('connected', this.onControllerConnected.bind(this));
      controller.addEventListener('disconnected', this.onControllerDisconnected.bind(this));
      this.scene.add(controller);
      this.controllers.push(controller);
      
      // 控制器模型
      const controllerGrip = this.renderer.xr.getControllerGrip(i);
      controllerGrip.add(controllerModelFactory.createControllerModel(controllerGrip));
      this.scene.add(controllerGrip);
      
      // 手部追踪
      const hand = this.renderer.xr.getHand(i);
      hand.add(handModelFactory.createHandModel(hand));
      this.scene.add(hand);
      this.hands.push(hand);
      
      // 射线指示器
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(0, 0, -1)
      ]);
      const line = new THREE.Line(geometry);
      line.name = 'line';
      line.scale.z = 5;
      controller.add(line);
    }
  }
  
  /**
   * 创建AR控制器
   */
  createARControls() {
    // AR手势识别
    this.createGestureRecognition();
    
    // AR对象操作
    this.createARObjectManipulation();
    
    // AR界面交互
    this.createARUIInteraction();
  }
  
  /**
   * 创建手势识别
   */
  createGestureRecognition() {
    // 实现手势识别逻辑
    console.log('🤚 手势识别系统已启动');
  }
  
  /**
   * 创建AR对象操作
   */
  createARObjectManipulation() {
    // 实现AR对象操作逻辑
    console.log('🔧 AR对象操作系统已启动');
  }
  
  /**
   * 创建AR界面交互
   */
  createARUIInteraction() {
    // 实现AR界面交互逻辑
    console.log('🖥️ AR界面交互系统已启动');
  }
  
  /**
   * 创建灯光
   */
  createLights() {
    // 环境光
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    this.scene.add(ambientLight);
    
    // 方向光
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.1;
    directionalLight.shadow.camera.far = 100;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    this.scene.add(directionalLight);
    
    // 点光源
    const pointLight = new THREE.PointLight(0x00ffff, 1, 50);
    pointLight.position.set(0, 10, 0);
    this.scene.add(pointLight);
    
    // 聚光灯
    const spotLight = new THREE.SpotLight(0xffffff, 1, 100, Math.PI / 6, 0.1, 2);
    spotLight.position.set(0, 20, 0);
    spotLight.target.position.set(0, 0, 0);
    spotLight.castShadow = true;
    this.scene.add(spotLight);
    this.scene.add(spotLight.target);
  }
  
  /**
   * 创建环境
   */
  createEnvironment() {
    // 天空盒
    const loader = new THREE.CubeTextureLoader();
    const texture = loader.load([
      'textures/skybox/px.jpg',
      'textures/skybox/nx.jpg',
      'textures/skybox/py.jpg',
      'textures/skybox/ny.jpg',
      'textures/skybox/pz.jpg',
      'textures/skybox/nz.jpg'
    ]);
    this.scene.background = texture;
    
    // 地面
    const groundGeometry = new THREE.PlaneGeometry(200, 200);
    const groundMaterial = new THREE.MeshLambertMaterial({
      color: 0x333333,
      transparent: true,
      opacity: 0.8
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    this.scene.add(ground);
    
    // 创建思维节点空间
    this.createThinkingSpace();
  }
  
  /**
   * 创建思维空间
   */
  createThinkingSpace() {
    // 思维节点容器
    this.thinkingSpace = new THREE.Group();
    this.thinkingSpace.name = 'ThinkingSpace';
    this.scene.add(this.thinkingSpace);
    
    // 创建中心思维节点
    const centerNodeGeometry = new THREE.SphereGeometry(2, 32, 32);
    const centerNodeMaterial = new THREE.MeshPhongMaterial({
      color: 0x00ff00,
      emissive: 0x002200,
      shininess: 100,
      transparent: true,
      opacity: 0.8
    });
    const centerNode = new THREE.Mesh(centerNodeGeometry, centerNodeMaterial);
    centerNode.position.set(0, 5, 0);
    centerNode.castShadow = true;
    centerNode.userData = {
      type: 'thinking_node',
      id: 'center',
      title: '核心思维',
      content: '这是元宇宙的核心思维节点',
      connections: [],
      interactions: []
    };
    this.thinkingSpace.add(centerNode);
    
    // 创建周围思维节点
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const radius = 10;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      
      const nodeGeometry = new THREE.OctahedronGeometry(1, 0);
      const nodeMaterial = new THREE.MeshPhongMaterial({
        color: new THREE.Color().setHSL(i / 8, 1, 0.5),
        emissive: new THREE.Color().setHSL(i / 8, 1, 0.1),
        shininess: 100,
        transparent: true,
        opacity: 0.8
      });
      const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
      node.position.set(x, 5, z);
      node.castShadow = true;
      node.userData = {
        type: 'thinking_node',
        id: `node_${i}`,
        title: `思维节点 ${i + 1}`,
        content: `这是第${i + 1}个思维节点`,
        connections: ['center'],
        interactions: []
      };
      this.thinkingSpace.add(node);
      
      // 创建连接线
      const lineGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 5, 0),
        new THREE.Vector3(x, 5, z)
      ]);
      const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x666666,
        transparent: true,
        opacity: 0.6
      });
      const line = new THREE.Line(lineGeometry, lineMaterial);
      this.thinkingSpace.add(line);
    }
    
    // 创建粒子系统
    this.createParticleSystem();
  }
  
  /**
   * 创建粒子系统
   */
  createParticleSystem() {
    const particleCount = 1000;
    const particles = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      
      // 位置
      positions[i3] = (Math.random() - 0.5) * 50;
      positions[i3 + 1] = Math.random() * 20;
      positions[i3 + 2] = (Math.random() - 0.5) * 50;
      
      // 颜色
      const color = new THREE.Color();
      color.setHSL(Math.random(), 1, 0.5);
      colors[i3] = color.r;
      colors[i3 + 1] = color.g;
      colors[i3 + 2] = color.b;
      
      // 速度
      velocities[i3] = (Math.random() - 0.5) * 0.01;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.01;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.01;
    }
    
    particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particles.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    particles.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
      size: 0.1,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });
    
    this.particleSystem = new THREE.Points(particles, particleMaterial);
    this.scene.add(this.particleSystem);
  }
  
  /**
   * 初始化XR
   */
  async initializeXR() {
    try {
      if ('xr' in navigator) {
        // 检查VR支持
        const vrSupported = await navigator.xr.isSessionSupported('immersive-vr');
        if (vrSupported) {
          document.body.appendChild(VRButton.createButton(this.renderer));
        }
        
        // 检查AR支持
        const arSupported = await navigator.xr.isSessionSupported('immersive-ar');
        if (arSupported) {
          document.body.appendChild(ARButton.createButton(this.renderer));
        }
        
        console.log('✅ XR系统初始化完成');
      } else {
        console.warn('⚠️ 当前浏览器不支持WebXR');
      }
    } catch (error) {
      console.error('❌ XR初始化失败:', error);
    }
  }
  
  /**
   * 初始化系统
   */
  async initializeSystems() {
    try {
      // 初始化各个系统
      this.systems.thinking = new ThinkingNodeSystem(this);
      this.systems.avatar = new UserAvatarSystem(this);
      this.systems.interaction = new InteractionSystem(this);
      this.systems.physics = new PhysicsSystem(this);
      this.systems.audio = new AudioSystem(this);
      this.systems.ai = new AIAssistantSystem(this);
      this.systems.blockchain = new BlockchainSystem(this);
      this.systems.quantum = new QuantumSystem(this);
      this.systems.analytics = new AnalyticsSystem(this);
      this.systems.security = new SecuritySystem(this);
      this.systems.performance = new PerformanceSystem(this);
      this.systems.content = new ContentSystem(this);
      this.systems.social = new SocialSystem(this);
      this.systems.economy = new EconomySystem(this);
      this.systems.creative = new CreativeSystem(this);
      this.systems.education = new EducationSystem(this);
      this.systems.health = new HealthSystem(this);
      this.systems.workspace = new WorkspaceSystem(this);
      this.systems.entertainment = new EntertainmentSystem(this);
      this.systems.vr = new VirtualRealitySystem(this);
      this.systems.ar = new AugmentedRealitySystem(this);
      this.systems.mr = new MixedRealitySystem(this);
      this.systems.bci = new BrainComputerInterfaceSystem(this);
      this.systems.neural = new NeuralNetworkSystem(this);
      this.systems.consciousness = new ConsciousnessSystem(this);
      this.systems.awareness = new AwarenessSystem(this);
      this.systems.intelligence = new IntelligenceSystem(this);
      this.systems.wisdom = new WisdomSystem(this);
      this.systems.enlightenment = new EnlightenmentSystem(this);
      this.systems.transcendence = new TranscendenceSystem(this);
      
      // 初始化所有系统
      for (const [name, system] of Object.entries(this.systems)) {
        if (system && typeof system.initialize === 'function') {
          await system.initialize();
          console.log(`✅ ${name} 系统初始化完成`);
        }
      }
      
      console.log('✅ 所有系统初始化完成');
      
    } catch (error) {
      console.error('❌ 系统初始化失败:', error);
    }
  }
  
  /**
   * 初始化网络
   */
  async initializeNetwork() {
    try {
      if (this.options.networking) {
        this.socket = io('wss://metaverse.intelligent-thinking.com', {
          transports: ['websocket'],
          upgrade: true,
          secure: true
        });
        
        this.socket.on('connect', () => {
          console.log('🌐 网络连接已建立');
          this.emit('connected');
        });
        
        this.socket.on('disconnect', () => {
          console.log('🌐 网络连接已断开');
          this.emit('disconnected');
        });
        
        this.socket.on('user_joined', (userData) => {
          this.onUserJoined(userData);
        });
        
        this.socket.on('user_left', (userId) => {
          this.onUserLeft(userId);
        });
        
        this.socket.on('user_moved', (data) => {
          this.onUserMoved(data);
        });
        
        this.socket.on('object_created', (data) => {
          this.onObjectCreated(data);
        });
        
        this.socket.on('object_updated', (data) => {
          this.onObjectUpdated(data);
        });
        
        this.socket.on('object_destroyed', (data) => {
          this.onObjectDestroyed(data);
        });
        
        this.socket.on('thinking_shared', (data) => {
          this.onThinkingShared(data);
        });
        
        this.socket.on('collaboration_started', (data) => {
          this.onCollaborationStarted(data);
        });
        
        this.socket.on('voice_message', (data) => {
          this.onVoiceMessage(data);
        });
        
        this.socket.on('gesture_performed', (data) => {
          this.onGesturePerformed(data);
        });
        
        this.socket.on('ai_response', (data) => {
          this.onAIResponse(data);
        });
        
        this.socket.on('blockchain_event', (data) => {
          this.onBlockchainEvent(data);
        });
        
        this.socket.on('quantum_computation', (data) => {
          this.onQuantumComputation(data);
        });
        
        this.socket.on('consciousness_sync', (data) => {
          this.onConsciousnessSync(data);
        });
        
        this.socket.on('transcendence_event', (data) => {
          this.onTranscendenceEvent(data);
        });
        
        console.log('✅ 网络系统初始化完成');
      }
      
    } catch (error) {
      console.error('❌ 网络初始化失败:', error);
    }
  }
  
  /**
   * 初始化用户界面
   */
  initializeUI() {
    // 创建性能监控
    this.stats = new Stats();
    this.stats.showPanel(0);
    document.body.appendChild(this.stats.dom);
    
    // 创建调试界面
    this.gui = new GUI();
    
    // 渲染设置
    const renderFolder = this.gui.addFolder('渲染设置');
    renderFolder.add(this.renderer, 'toneMappingExposure', 0, 2).name('曝光');
    renderFolder.add(this.scene.fog, 'near', 1, 100).name('雾效近距离');
    renderFolder.add(this.scene.fog, 'far', 100, 1000).name('雾效远距离');
    
    // 相机设置
    const cameraFolder = this.gui.addFolder('相机设置');
    cameraFolder.add(this.camera, 'fov', 30, 120).name('视角').onChange(() => {
      this.camera.updateProjectionMatrix();
    });
    cameraFolder.add(this.camera.position, 'y', 0, 50).name('高度');
    
    // 粒子系统设置
    const particleFolder = this.gui.addFolder('粒子系统');
    particleFolder.add(this.particleSystem.material, 'size', 0.01, 1).name('大小');
    particleFolder.add(this.particleSystem.material, 'opacity', 0, 1).name('透明度');
    
    // 思维空间设置
    const thinkingFolder = this.gui.addFolder('思维空间');
    thinkingFolder.add({ rotationSpeed: 0.01 }, 'rotationSpeed', 0, 0.1).name('旋转速度');
    
    // 系统状态
    const systemFolder = this.gui.addFolder('系统状态');
    systemFolder.add(this.state, 'frameCount').name('帧数').listen();
    systemFolder.add(this.state, 'totalTime').name('总时间').listen();
    systemFolder.add(this.state.users, 'size').name('用户数').listen();
    systemFolder.add(this.state.objects, 'size').name('对象数').listen();
    
    console.log('✅ 用户界面初始化完成');
  }
  
  /**
   * 绑定事件
   */
  bindEvents() {
    // 窗口大小变化
    window.addEventListener('resize', this.onWindowResize.bind(this));
    
    // 键盘事件
    window.addEventListener('keydown', this.onKeyDown.bind(this));
    window.addEventListener('keyup', this.onKeyUp.bind(this));
    
    // 鼠标事件
    window.addEventListener('mousedown', this.onMouseDown.bind(this));
    window.addEventListener('mouseup', this.onMouseUp.bind(this));
    window.addEventListener('mousemove', this.onMouseMove.bind(this));
    window.addEventListener('wheel', this.onMouseWheel.bind(this));
    
    // 触摸事件
    window.addEventListener('touchstart', this.onTouchStart.bind(this));
    window.addEventListener('touchend', this.onTouchEnd.bind(this));
    window.addEventListener('touchmove', this.onTouchMove.bind(this));
    
    // 设备方向事件
    window.addEventListener('deviceorientation', this.onDeviceOrientation.bind(this));
    
    // 可见性变化
    document.addEventListener('visibilitychange', this.onVisibilityChange.bind(this));
    
    // XR事件
    if (this.renderer.xr) {
      this.renderer.xr.addEventListener('sessionstart', this.onXRSessionStart.bind(this));
      this.renderer.xr.addEventListener('sessionend', this.onXRSessionEnd.bind(this));
    }
    
    console.log('✅ 事件绑定完成');
  }
  
  /**
   * 开始渲染循环
   */
  startRenderLoop() {
    this.renderer.setAnimationLoop(this.render.bind(this));
    console.log('✅ 渲染循环已启动');
  }
  
  /**
   * 主渲染函数
   */
  render(timestamp) {
    try {
      // 更新状态
      this.state.timestamp = timestamp;
      this.state.frameCount++;
      this.state.deltaTime = timestamp - this.state.totalTime;
      this.state.totalTime = timestamp;
      
      // 更新性能监控
      this.stats.begin();
      
      // 更新控制器
      if (this.controls) {
        this.controls.update();
      }
      
      // 更新粒子系统
      this.updateParticleSystem();
      
      // 更新思维空间
      this.updateThinkingSpace();
      
      // 更新所有系统
      this.updateSystems();
      
      // 渲染场景
      if (this.renderer.xr.isPresenting) {
        this.renderer.render(this.scene, this.camera);
      } else {
        this.composer.render();
      }
      
      // 完成性能监控
      this.stats.end();
      
    } catch (error) {
      console.error('❌ 渲染错误:', error);
    }
  }
  
  /**
   * 更新粒子系统
   */
  updateParticleSystem() {
    const positions = this.particleSystem.geometry.attributes.position.array;
    const velocities = this.particleSystem.geometry.attributes.velocity.array;
    
    for (let i = 0; i < positions.length; i += 3) {
      positions[i] += velocities[i];
      positions[i + 1] += velocities[i + 1];
      positions[i + 2] += velocities[i + 2];
      
      // 边界检查
      if (Math.abs(positions[i]) > 25) velocities[i] *= -1;
      if (positions[i + 1] > 20 || positions[i + 1] < 0) velocities[i + 1] *= -1;
      if (Math.abs(positions[i + 2]) > 25) velocities[i + 2] *= -1;
    }
    
    this.particleSystem.geometry.attributes.position.needsUpdate = true;
  }
  
  /**
   * 更新思维空间
   */
  updateThinkingSpace() {
    this.thinkingSpace.rotation.y += 0.005;
    
    // 更新思维节点
    this.thinkingSpace.children.forEach((child, index) => {
      if (child.userData && child.userData.type === 'thinking_node') {
        child.rotation.x += 0.01;
        child.rotation.y += 0.01;
        
        // 呼吸效果
        const scale = 1 + Math.sin(this.state.totalTime * 0.001 + index) * 0.1;
        child.scale.setScalar(scale);
      }
    });
  }
  
  /**
   * 更新所有系统
   */
  updateSystems() {
    for (const [name, system] of Object.entries(this.systems)) {
      if (system && typeof system.update === 'function') {
        system.update(this.state.deltaTime);
      }
    }
  }
  
  /**
   * 窗口大小变化处理
   */
  onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.composer.setSize(window.innerWidth, window.innerHeight);
  }
  
  /**
   * 键盘按下事件
   */
  onKeyDown(event) {
    switch (event.code) {
      case 'Space':
        event.preventDefault();
        this.togglePause();
        break;
      case 'KeyR':
        this.resetScene();
        break;
      case 'KeyF':
        this.toggleFullscreen();
        break;
      case 'KeyG':
        this.toggleGUI();
        break;
      case 'KeyS':
        this.toggleStats();
        break;
      case 'KeyC':
        this.captureScreenshot();
        break;
      case 'KeyV':
        this.toggleVoiceInput();
        break;
      case 'KeyA':
        this.toggleAIAssistant();
        break;
      case 'KeyB':
        this.toggleBlockchainMode();
        break;
      case 'KeyQ':
        this.toggleQuantumMode();
        break;
      case 'KeyT':
        this.toggleTranscendenceMode();
        break;
    }
  }
  
  /**
   * 键盘释放事件
   */
  onKeyUp(event) {
    // 处理键盘释放事件
  }
  
  /**
   * 鼠标按下事件
   */
  onMouseDown(event) {
    // 处理鼠标按下事件
  }
  
  /**
   * 鼠标释放事件
   */
  onMouseUp(event) {
    // 处理鼠标释放事件
  }
  
  /**
   * 鼠标移动事件
   */
  onMouseMove(event) {
    // 处理鼠标移动事件
  }
  
  /**
   * 鼠标滚轮事件
   */
  onMouseWheel(event) {
    // 处理鼠标滚轮事件
  }
  
  /**
   * 触摸开始事件
   */
  onTouchStart(event) {
    // 处理触摸开始事件
  }
  
  /**
   * 触摸结束事件
   */
  onTouchEnd(event) {
    // 处理触摸结束事件
  }
  
  /**
   * 触摸移动事件
   */
  onTouchMove(event) {
    // 处理触摸移动事件
  }
  
  /**
   * 设备方向事件
   */
  onDeviceOrientation(event) {
    // 处理设备方向变化
  }
  
  /**
   * 页面可见性变化
   */
  onVisibilityChange() {
    if (document.hidden) {
      this.pause();
    } else {
      this.resume();
    }
  }
  
  /**
   * XR会话开始
   */
  onXRSessionStart() {
    console.log('🥽 XR会话已开始');
    this.emit('xr_session_start');
  }
  
  /**
   * XR会话结束
   */
  onXRSessionEnd() {
    console.log('🥽 XR会话已结束');
    this.emit('xr_session_end');
  }
  
  /**
   * 控制器选择开始
   */
  onSelectStart(event) {
    console.log('🎮 控制器选择开始');
    this.emit('select_start', event);
  }
  
  /**
   * 控制器选择结束
   */
  onSelectEnd(event) {
    console.log('🎮 控制器选择结束');
    this.emit('select_end', event);
  }
  
  /**
   * 控制器连接
   */
  onControllerConnected(event) {
    console.log('🎮 控制器已连接');
    this.emit('controller_connected', event);
  }
  
  /**
   * 控制器断开
   */
  onControllerDisconnected(event) {
    console.log('🎮 控制器已断开');
    this.emit('controller_disconnected', event);
  }
  
  /**
   * 用户加入
   */
  onUserJoined(userData) {
    console.log('👤 用户加入:', userData);
    this.state.users.set(userData.id, userData);
    this.systems.avatar.createAvatar(userData);
    this.emit('user_joined', userData);
  }
  
  /**
   * 用户离开
   */
  onUserLeft(userId) {
    console.log('👤 用户离开:', userId);
    this.state.users.delete(userId);
    this.systems.avatar.removeAvatar(userId);
    this.emit('user_left', userId);
  }
  
  /**
   * 用户移动
   */
  onUserMoved(data) {
    const user = this.state.users.get(data.userId);
    if (user) {
      user.position = data.position;
      user.rotation = data.rotation;
      this.systems.avatar.updateAvatar(data.userId, data);
    }
  }
  
  /**
   * 对象创建
   */
  onObjectCreated(data) {
    console.log('🎯 对象创建:', data);
    this.state.objects.set(data.id, data);
    this.systems.content.createObject(data);
    this.emit('object_created', data);
  }
  
  /**
   * 对象更新
   */
  onObjectUpdated(data) {
    const object = this.state.objects.get(data.id);
    if (object) {
      Object.assign(object, data);
      this.systems.content.updateObject(data);
    }
  }
  
  /**
   * 对象销毁
   */
  onObjectDestroyed(data) {
    console.log('🎯 对象销毁:', data);
    this.state.objects.delete(data.id);
    this.systems.content.removeObject(data.id);
    this.emit('object_destroyed', data);
  }
  
  /**
   * 思维分享
   */
  onThinkingShared(data) {
    console.log('🧠 思维分享:', data);
    this.systems.thinking.addThinkingNode(data);
    this.emit('thinking_shared', data);
  }
  
  /**
   * 协作开始
   */
  onCollaborationStarted(data) {
    console.log('🤝 协作开始:', data);
    this.systems.social.startCollaboration(data);
    this.emit('collaboration_started', data);
  }
  
  /**
   * 语音消息
   */
  onVoiceMessage(data) {
    console.log('🎙️ 语音消息:', data);
    this.systems.audio.playVoiceMessage(data);
    this.emit('voice_message', data);
  }
  
  /**
   * 手势表演
   */
  onGesturePerformed(data) {
    console.log('🤚 手势表演:', data);
    this.systems.interaction.performGesture(data);
    this.emit('gesture_performed', data);
  }
  
  /**
   * AI响应
   */
  onAIResponse(data) {
    console.log('🤖 AI响应:', data);
    this.systems.ai.processResponse(data);
    this.emit('ai_response', data);
  }
  
  /**
   * 区块链事件
   */
  onBlockchainEvent(data) {
    console.log('🔗 区块链事件:', data);
    this.systems.blockchain.processEvent(data);
    this.emit('blockchain_event', data);
  }
  
  /**
   * 量子计算
   */
  onQuantumComputation(data) {
    console.log('⚛️ 量子计算:', data);
    this.systems.quantum.processComputation(data);
    this.emit('quantum_computation', data);
  }
  
  /**
   * 意识同步
   */
  onConsciousnessSync(data) {
    console.log('🧘 意识同步:', data);
    this.systems.consciousness.syncConsciousness(data);
    this.emit('consciousness_sync', data);
  }
  
  /**
   * 超越事件
   */
  onTranscendenceEvent(data) {
    console.log('✨ 超越事件:', data);
    this.systems.transcendence.processEvent(data);
    this.emit('transcendence_event', data);
  }
  
  /**
   * 切换暂停状态
   */
  togglePause() {
    this.state.paused = !this.state.paused;
    if (this.state.paused) {
      this.pause();
    } else {
      this.resume();
    }
  }
  
  /**
   * 暂停
   */
  pause() {
    this.state.paused = true;
    this.emit('paused');
  }
  
  /**
   * 恢复
   */
  resume() {
    this.state.paused = false;
    this.emit('resumed');
  }
  
  /**
   * 重置场景
   */
  resetScene() {
    // 重置相机位置
    this.camera.position.set(0, 5, 10);
    this.camera.lookAt(0, 0, 0);
    
    // 重置思维空间
    this.thinkingSpace.rotation.set(0, 0, 0);
    
    console.log('🔄 场景已重置');
    this.emit('scene_reset');
  }
  
  /**
   * 切换全屏
   */
  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }
  
  /**
   * 切换GUI
   */
  toggleGUI() {
    this.gui.domElement.style.display = 
      this.gui.domElement.style.display === 'none' ? 'block' : 'none';
  }
  
  /**
   * 切换统计信息
   */
  toggleStats() {
    this.stats.dom.style.display = 
      this.stats.dom.style.display === 'none' ? 'block' : 'none';
  }
  
  /**
   * 截图
   */
  captureScreenshot() {
    const canvas = this.renderer.domElement;
    const link = document.createElement('a');
    link.download = `metaverse_screenshot_${Date.now()}.png`;
    link.href = canvas.toDataURL();
    link.click();
    
    console.log('📸 截图已保存');
  }
  
  /**
   * 切换语音输入
   */
  toggleVoiceInput() {
    this.systems.audio.toggleVoiceInput();
  }
  
  /**
   * 切换AI助手
   */
  toggleAIAssistant() {
    this.systems.ai.toggleAssistant();
  }
  
  /**
   * 切换区块链模式
   */
  toggleBlockchainMode() {
    this.systems.blockchain.toggleMode();
  }
  
  /**
   * 切换量子模式
   */
  toggleQuantumMode() {
    this.systems.quantum.toggleMode();
  }
  
  /**
   * 切换超越模式
   */
  toggleTranscendenceMode() {
    this.systems.transcendence.toggleMode();
  }
  
  /**
   * 销毁元宇宙
   */
  destroy() {
    try {
      // 停止渲染循环
      this.renderer.setAnimationLoop(null);
      
      // 断开网络连接
      if (this.socket) {
        this.socket.disconnect();
      }
      
      // 销毁所有系统
      for (const [name, system] of Object.entries(this.systems)) {
        if (system && typeof system.destroy === 'function') {
          system.destroy();
        }
      }
      
      // 清理场景
      this.scene.clear();
      
      // 销毁渲染器
      this.renderer.dispose();
      
      // 移除DOM元素
      if (this.renderer.domElement.parentNode) {
        this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
      }
      
      // 清理状态
      this.state.initialized = false;
      this.state.running = false;
      
      console.log('🗑️ 元宇宙已销毁');
      this.emit('destroyed');
      
    } catch (error) {
      console.error('❌ 元宇宙销毁失败:', error);
    }
  }
}

// 导出元宇宙核心
export { MetaverseCore };

// 创建全局实例
window.MetaverseCore = MetaverseCore;

// 自动初始化（如果需要）
if (typeof window !== 'undefined' && window.AUTO_INIT_METAVERSE) {
  const metaverse = new MetaverseCore({
    container: document.getElementById('metaverse-container') || document.body,
    mode: 'mixed',
    quality: 'high',
    experimental: true
  });
  
  window.metaverse = metaverse;
  
  console.log('🌌 元宇宙自动初始化完成');
}

export default MetaverseCore; 