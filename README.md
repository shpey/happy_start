# 智能思维分析平台

一个基于AI驱动的三维思维分析与协作平台，运用前沿人工智能技术深度分析用户思维模式，提供个性化认知提升建议。

## 🌟 核心特性

### 🧠 AI思维分析
- **三层思维模型**：形象思维、逻辑思维、创造思维全面分析
- **智能文本分析**：深度理解用户输入的思维内容
- **图像思维识别**：支持图片上传进行视觉思维分析
- **个性化建议**：基于分析结果提供专业的思维训练建议

### 🔗 知识图谱
- **可视化展示**：动态展示概念间的关联关系
- **智能推荐**：基于用户思维特点推荐相关知识节点
- **路径发现**：自动发现概念间的逻辑路径
- **协作编辑**：支持多用户协同构建知识图谱

### 👥 实时协作
- **多用户协作**：支持实时多人思维空间共享
- **WebSocket连接**：低延迟的实时数据同步
- **角色管理**：主持人、协调者、参与者等多种角色
- **会话管理**：创建、加入、管理协作会话

### 🌐 3D思维空间
- **三维可视化**：在立体空间中展示思维结构
- **沉浸式体验**：支持VR/AR设备交互
- **空间导航**：直观的3D空间导航和交互
- **动态交互**：实时响应用户操作和思维变化

### 🔐 用户认证系统
- **JWT认证**：安全的用户身份验证
- **自动刷新**：Token自动续期机制
- **权限控制**：基于角色的访问控制
- **密码安全**：bcrypt加密存储

## 🏗️ 技术架构

### 前端技术栈
- **React 18** - 现代化UI框架
- **TypeScript** - 类型安全的JavaScript
- **Material-UI 5** - Google Material Design组件库
- **Three.js** - 3D图形渲染引擎
- **React Router** - 单页应用路由管理
- **Axios** - HTTP客户端库
- **WebSocket** - 实时通信

### 后端技术栈
- **FastAPI** - 高性能Python Web框架
- **Python 3.9+** - 现代Python版本
- **SQLAlchemy** - ORM数据库操作
- **PostgreSQL/SQLite** - 关系型数据库
- **Redis** - 缓存和会话存储
- **Neo4j** - 图数据库（知识图谱）
- **JWT** - 用户认证
- **WebSocket** - 实时通信

### AI/ML技术
- **自然语言处理**：基于Transformer的文本理解
- **计算机视觉**：图像内容分析和理解
- **机器学习**：思维模式识别和分类
- **深度学习**：神经网络模型训练和推理

## 🚀 快速开始

### 环境要求
- Node.js 16.0+
- Python 3.9+
- PostgreSQL 13+ (可选，默认使用SQLite)
- Redis 6.0+ (可选)

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/your-username/intelligent_thinking.git
cd intelligent_thinking
```

2. **安装前端依赖**
```bash
cd frontend
npm install
```

3. **安装后端依赖**
```bash
cd ../backend
pip install -r requirements.txt
```

4. **环境配置**
```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量文件
vim .env
```

5. **数据库初始化**
```bash
cd backend
python scripts/init_db.py
```

6. **启动服务**

前端开发服务器：
```bash
cd frontend
npm run dev
```

后端API服务器：
```bash
cd backend
python main.py
```

访问 `http://localhost:3000` 体验平台功能。

## 📁 项目结构

```
intelligent_thinking/
├── frontend/                 # React前端应用
│   ├── src/
│   │   ├── components/       # 可复用组件
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API服务
│   │   ├── contexts/        # React上下文
│   │   ├── hooks/           # 自定义Hooks
│   │   ├── types/           # TypeScript类型定义
│   │   └── utils/           # 工具函数
│   ├── public/              # 静态资源
│   └── package.json         # 依赖配置
├── backend/                 # FastAPI后端应用
│   ├── app/
│   │   ├── api/             # API路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   └── ai_models/       # AI模型管理
│   ├── scripts/             # 辅助脚本
│   ├── tests/               # 测试文件
│   └── requirements.txt     # Python依赖
├── docs/                    # 项目文档
├── docker-compose.yml       # Docker容器编排
└── README.md               # 项目说明
```

## 🔧 配置说明

### 环境变量配置

```bash
# 应用配置
PROJECT_NAME=智能思维分析平台
VERSION=1.0.0
ENVIRONMENT=development

# 数据库配置
DATABASE_URL=sqlite:///./intelligent_thinking.db
# DATABASE_URL=postgresql://user:password@localhost:5432/intelligent_thinking

# Redis配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 安全配置
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI模型配置
OPENAI_API_KEY=your-openai-api-key
MODEL_CACHE_TTL=3600
```

## 🎯 功能使用指南

### 思维分析
1. 登录或注册账户
2. 选择"思维分析"功能
3. 输入您想要分析的文本内容
4. 选择分析类型（综合分析、形象思维、逻辑思维、创造思维）
5. 点击"开始分析"查看结果
6. 查看详细的思维分析报告和建议

### 知识图谱
1. 进入"知识图谱"页面
2. 添加概念节点
3. 建立概念间的关联关系
4. 使用可视化界面探索知识网络
5. 导出或分享知识图谱

### 实时协作
1. 创建或加入协作会话
2. 邀请团队成员参与
3. 在共享空间中进行思维碰撞
4. 使用协作工具进行讨论和标注
5. 保存协作成果

### 3D思维空间
1. 进入"3D思维空间"
2. 在三维环境中组织思维结构
3. 使用手势或VR设备进行交互
4. 与他人在3D空间中协作
5. 导出3D思维模型

## 🧪 测试

### 运行前端测试
```bash
cd frontend
npm test
```

### 运行后端测试
```bash
cd backend
python -m pytest tests/
```

## 📦 部署

### Docker部署
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 生产环境部署
1. 设置环境变量为生产模式
2. 配置反向代理(Nginx)
3. 设置SSL证书
4. 配置数据库和Redis
5. 启动后端和前端服务

## 🤝 贡献指南

我们欢迎任何形式的贡献！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范
- 遵循代码格式化规范
- 编写单元测试
- 更新相关文档
- 提供清晰的提交信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [React](https://reactjs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Material-UI](https://mui.com/) - UI组件库
- [Three.js](https://threejs.org/) - 3D图形库
- 所有开源贡献者

## 📞 联系我们

- 项目主页：https://github.com/your-username/intelligent_thinking
- 问题反馈：https://github.com/your-username/intelligent_thinking/issues
- 邮箱：your-email@example.com

## 🗺️ 发展路线

- [ ] 移动端适配
- [ ] 更多AI模型集成
- [ ] 实时语音分析
- [ ] 团队管理功能
- [ ] 数据分析报告
- [ ] API开放平台
- [ ] 第三方应用集成

---

⭐ 如果这个项目对您有帮助，请不要忘记给它一个星标！ 