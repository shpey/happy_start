# 智能思维平台 - 快速部署指南

## 🚀 快速开始

### 1. 准备工作

确保您的系统已安装：
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (可选，用于本地开发)

### 2. 克隆项目

```bash
git clone https://github.com/your-username/intelligent-thinking.git
cd intelligent-thinking
```

### 3. 配置环境变量

复制环境变量模板：
```bash
cp env.example .env
```

编辑 `.env` 文件，填入您的配置：
```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_AI_API_KEY=your_google_ai_api_key

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/intelligent_thinking

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your_jwt_secret_key
```

### 4. 部署方式

#### 方式一：使用部署脚本（推荐）

**Linux/macOS:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**Windows:**
```bash
bash scripts/deploy.sh
```

#### 方式二：使用 Docker Compose

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看运行状态
docker-compose ps
```

#### 方式三：使用 Kubernetes

```bash
# 创建命名空间
kubectl create namespace intelligent-thinking

# 创建配置
kubectl create configmap app-config --from-env-file=.env -n intelligent-thinking

# 部署应用
kubectl apply -f k8s/intelligent-thinking-k8s.yaml

# 查看状态
kubectl get pods -n intelligent-thinking
```

### 5. 访问应用

部署完成后，您可以访问：

- **前端应用**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **GraphQL**: http://localhost:8085/graphql
- **API 文档**: http://localhost:8080/docs

### 6. 微服务端口

| 服务 | 端口 | 描述 |
|------|------|------|
| Frontend | 3000 | React 前端应用 |
| Gateway | 8080 | API 网关服务 |
| Blockchain | 8084 | 区块链服务 |
| GraphQL | 8085 | GraphQL 服务 |
| AI Advanced | 8086 | 高级 AI 服务 |
| Search | 8087 | 搜索服务 |
| Federated Learning | 8088 | 联邦学习服务 |
| Quantum Computing | 8089 | 量子计算服务 |

## 🔧 管理命令

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f frontend
docker-compose logs -f gateway
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart frontend
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 更新服务
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

## 📊 监控和日志

### 监控面板
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Jaeger**: http://localhost:16686

### 健康检查
```bash
# 检查前端
curl http://localhost:3000

# 检查 API Gateway
curl http://localhost:8080/health

# 检查所有微服务
curl http://localhost:8084/health  # Blockchain
curl http://localhost:8085/health  # GraphQL
curl http://localhost:8086/health  # AI Advanced
curl http://localhost:8087/health  # Search
curl http://localhost:8088/health  # Federated Learning
curl http://localhost:8089/health  # Quantum Computing
```

## 🛠️ 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -an | grep :8080
   
   # 停止冲突的服务
   docker-compose down
   ```

2. **内存不足**
   ```bash
   # 增加 Docker 内存限制
   # 在 Docker Desktop 设置中调整内存分配
   ```

3. **网络问题**
   ```bash
   # 重新创建网络
   docker network prune
   docker-compose up -d
   ```

### 日志分析

```bash
# 查看错误日志
docker-compose logs | grep ERROR

# 查看特定时间的日志
docker-compose logs --since "2023-01-01T00:00:00" --until "2023-01-02T00:00:00"

# 跟踪实时日志
docker-compose logs -f --tail=100
```

## 🔒 安全配置

### 生产环境配置

1. **更新密钥**
   ```bash
   # 生成新的 JWT 密钥
   openssl rand -base64 32
   
   # 更新 .env 文件
   JWT_SECRET=your_new_secret_key
   ```

2. **启用 HTTPS**
   ```bash
   # 在 nginx.conf 中配置 SSL
   # 或使用 Let's Encrypt 证书
   ```

3. **限制访问**
   ```bash
   # 配置防火墙规则
   # 限制数据库访问
   ```

## 📝 开发指南

### 本地开发

```bash
# 启动开发环境
npm run dev

# 启动后端服务
cd backend && python -m uvicorn main:app --reload

# 启动前端服务
cd frontend && npm start
```

### 测试

```bash
# 运行单元测试
npm test

# 运行集成测试
npm run test:integration

# 运行端到端测试
npm run test:e2e
```

## 📚 更多文档

- [API 文档](./docs/API配置指南.md)
- [架构设计](./docs/README.md)
- [开发指导](./docs/开发指导.md)
- [环境配置](./docs/环境配置指南.md)

## 🆘 获取帮助

如果您遇到问题，请：

1. 查看 [常见问题](#常见问题)
2. 检查 [GitHub Issues](https://github.com/your-username/intelligent-thinking/issues)
3. 查看项目文档
4. 联系开发团队

---

**祝您使用愉快！** 🎉 