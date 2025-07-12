# 🧠 智能思维与灵境融合项目

一个现代化的全栈AI应用，融合Python后端、React前端、AI模型、3D可视化于一体的智能思维分析与协作平台。

## 🎯 项目概述

本项目旨在构建AI时代的"思维科学"基础，通过灵境（元宇宙）平台实现人机智慧深度融合，支持**三层思维建模架构**：

- **🎨 形象思维**: 视觉-语言理解，多模态感知
- **🔍 逻辑思维**: 推理分析，符号处理
- **💡 创造思维**: 生成创新，突破边界

## 🏗️ 技术架构

### 后端技术栈
- **🐍 Python 3.11** - 现代Python特性
- **⚡ FastAPI** - 高性能异步Web框架
- **🤖 PyTorch + Transformers** - AI模型推理
- **🐘 PostgreSQL** - 主数据库
- **🔴 Redis** - 缓存与会话管理
- **🌐 Neo4j** - 知识图谱存储
- **🔌 WebSocket** - 实时通信

### 前端技术栈
- **⚛️ React 18** - 现代前端框架
- **📘 TypeScript** - 类型安全
- **🎨 Material-UI** - 优雅组件库
- **🎪 Three.js** - 3D图形渲染
- **🔄 Redux Toolkit** - 状态管理
- **📡 React Query** - 数据获取

### AI模型集成
- **🖼️ CLIP** - 视觉-语言理解
- **🔤 RoBERTa** - 文本分析
- **📝 GPT-2** - 创意生成
- **🧮 Scikit-learn** - 机器学习

### 基础设施
- **🐳 Docker** - 容器化部署
- **🔧 Docker Compose** - 多服务编排
- **🌐 Nginx** - 反向代理
- **📊 Prometheus** - 监控指标

## 🚀 快速开始

### 环境要求

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Git**

### 1. 克隆项目

```bash
git clone <repository-url>
cd intelligent-thinking-metaverse
```

### 2. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量 (根据需要修改数据库密码等)
nano .env
```

### 3. Docker 一键启动

```bash
# 构建并启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 本地开发启动

#### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python main.py
```

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

### 5. 访问应用

- **前端应用**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **Neo4j浏览器**: http://localhost:7474
- **系统健康检查**: http://localhost:8000/health

## 📂 项目结构

```
intelligent-thinking-metaverse/
├── 📁 backend/                 # Python后端
│   ├── 📁 app/
│   │   ├── 📁 core/           # 核心配置
│   │   ├── 📁 api/            # API路由
│   │   ├── 📁 models/         # 数据模型
│   │   ├── 📁 services/       # 业务逻辑
│   │   └── 📁 ai_models/      # AI模型管理
│   ├── 📄 main.py             # 应用入口
│   ├── 📄 requirements.txt    # Python依赖
│   └── 📄 Dockerfile          # 容器构建
├── 📁 frontend/               # React前端
│   ├── 📁 src/
│   │   ├── 📁 components/     # React组件
│   │   ├── 📁 pages/          # 页面组件
│   │   ├── 📁 store/          # Redux状态
│   │   ├── 📁 services/       # API服务
│   │   └── 📁 types/          # TypeScript类型
│   ├── 📄 package.json        # 依赖配置
│   └── 📄 Dockerfile          # 容器构建
├── 📄 docker-compose.yml      # 服务编排
├── 📄 nginx.conf              # 反向代理配置
└── 📄 README.md               # 项目文档
```

## 🔧 核心功能

### 🧠 AI思维分析

```python
# 三层思维模型分析示例
POST /api/v1/thinking/analyze
{
    "text": "用户输入的思考内容",
    "analysis_type": "comprehensive"
}

# 响应示例
{
    "thinking_summary": {
        "dominant_thinking_style": "逻辑思维",
        "thinking_scores": {
            "逻辑思维": 0.85,
            "创造思维": 0.72,
            "形象思维": 0.68
        },
        "balance_index": 0.78
    }
}
```

### 🌐 知识图谱操作

```python
# 创建知识节点
POST /api/v1/knowledge/nodes
{
    "label": "Concept",
    "properties": {
        "name": "人工智能",
        "description": "模拟人类智能的技术"
    }
}

# 建立知识关系
POST /api/v1/knowledge/relationships
{
    "from_node_id": "node_1",
    "to_node_id": "node_2", 
    "relationship_type": "RELATES_TO"
}
```

### 🤝 实时协作

```typescript
// WebSocket连接示例
const socket = io('ws://localhost:8000');

socket.on('thinking_update', (data) => {
    // 处理思维空间更新
    console.log('协作更新:', data);
});
```

## 🎨 核心特性

### ✨ 主要亮点

- **🎯 三层思维建模**: 形象→逻辑→创造思维全链条分析
- **🌐 沉浸式3D空间**: WebXR支持的认知可视化
- **🤖 多模态AI**: 文本+图像+语音的综合理解
- **🔗 智能知识图谱**: Neo4j驱动的关联推理
- **⚡ 实时协作**: WebSocket多用户同步
- **📊 可视化分析**: 丰富的图表与指标
- **🔐 企业级安全**: JWT认证+数据加密
- **📱 响应式设计**: 支持桌面+移动端

### 🛠️ 开发特性

- **🔄 热重载**: 前后端开发实时更新
- **📝 类型安全**: 全栈TypeScript支持
- **🧪 单元测试**: Jest+Pytest完整覆盖
- **📊 监控告警**: Prometheus+Grafana
- **🐳 容器化**: Docker一键部署
- **📚 API文档**: 自动生成的Swagger文档

## 📊 性能指标

- **⚡ API响应**: < 100ms (平均)
- **🎮 3D渲染**: 60 FPS (目标)
- **👥 并发用户**: 1000+ (设计目标)
- **💾 数据处理**: 1M+ 节点支持
- **🔄 实时延迟**: < 50ms

## 🧪 测试

```bash
# 后端测试
cd backend
python -m pytest tests/ -v

# 前端测试  
cd frontend
npm test

# 集成测试
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 部署

### 生产环境部署

```bash
# 1. 设置生产环境变量
export ENVIRONMENT=production
export DEBUG=false

# 2. 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 3. 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 配置域名和SSL (可选)
# 使用Let's Encrypt等工具配置HTTPS
```

### 扩展部署

```bash
# 水平扩展后端服务
docker-compose up --scale backend=3

# 使用Kubernetes (高级)
kubectl apply -f k8s/
```

## 🔧 API文档

启动服务后访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/thinking/analyze` | POST | 思维分析 |
| `/api/v1/thinking/generate-ideas` | POST | 创意生成 |
| `/api/v1/knowledge/nodes` | GET/POST | 知识节点 |
| `/api/v1/collaboration/rooms` | GET/POST | 协作房间 |
| `/api/v1/system/health` | GET | 健康检查 |

## 🤝 贡献指南

1. **Fork** 本仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 **Pull Request**

### 代码规范

```bash
# Python代码格式化
black backend/
isort backend/

# TypeScript代码格式化  
cd frontend && npm run format

# 代码检查
cd frontend && npm run lint
cd backend && flake8 app/
```

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [React](https://reactjs.org/) - 用户界面库
- [Material-UI](https://mui.com/) - React组件库
- [Three.js](https://threejs.org/) - 3D图形库
- [Neo4j](https://neo4j.com/) - 图数据库
- [PyTorch](https://pytorch.org/) - 机器学习框架

## 📞 联系方式

- **项目主页**: [GitHub Repository]
- **问题报告**: [GitHub Issues]
- **功能请求**: [GitHub Discussions]

---

🌟 **如果这个项目对您有帮助，请考虑给它一个Star！** 🌟 