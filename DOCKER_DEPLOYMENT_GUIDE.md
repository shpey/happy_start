# Docker 部署指南

## 概述

这个文档详细说明了如何使用 GitHub Actions 自动化构建和部署智能思维平台的 Docker 镜像。

## 文件结构

```
.github/workflows/
├── docker-image.yml          # 主要的 Docker 镜像构建和部署流程
├── deploy.yml               # 详细的部署策略流程
└── k8s-deployment.yml       # Kubernetes 部署配置（已删除）

k8s/
└── intelligent-thinking-k8s.yaml  # Kubernetes 部署配置

```

## 主要 Workflow 文件

### 1. docker-image.yml - 主要构建流程

这是核心的 GitHub Actions workflow，负责：

- **变更检测**: 只构建有变化的组件
- **并行构建**: 同时构建多个服务
- **多平台支持**: 支持 linux/amd64 和 linux/arm64
- **缓存优化**: 使用 GitHub Actions 缓存
- **安全扫描**: 使用 Trivy 扫描漏洞
- **自动部署**: 根据分支自动部署到不同环境

#### 构建的镜像

1. **Frontend**: React 18 + TypeScript 前端应用
2. **Backend**: FastAPI 后端应用
3. **11个微服务**:
   - api-gateway (端口 8080)
   - auth-service (端口 8081)
   - thinking-analysis (端口 8082)
   - collaboration (端口 8083)
   - blockchain (端口 8084)
   - graphql (端口 8085)
   - advanced-ai (端口 8086)
   - search (端口 8087)
   - federated-learning (端口 8088)
   - quantum-computing (端口 8089)
   - networking (端口 8090)
4. **Mobile**: React Native 移动应用
5. **Metaverse**: WebXR 元宇宙服务

### 2. deploy.yml - 部署策略流程

这是可重用的部署流程，支持：

- **Kubernetes 部署**: 使用 kubectl 部署到 K8s 集群
- **Docker Compose 部署**: 用于开发和测试环境
- **健康检查**: 部署后的服务健康检查
- **自动回滚**: 失败时自动回滚
- **通知机制**: Slack 通知部署状态

## 部署环境

### 开发环境 (Development)
- **触发**: 推送到 `develop` 分支
- **部署方式**: Docker Compose
- **镜像标签**: `develop`

### 预发布环境 (Staging)
- **触发**: 推送到 `develop` 分支
- **部署方式**: Kubernetes
- **镜像标签**: `develop`

### 生产环境 (Production)
- **触发**: 推送到 `main` 分支
- **部署方式**: Kubernetes
- **镜像标签**: `main`

### 版本发布
- **触发**: 推送 `v*` 标签
- **部署方式**: Kubernetes
- **镜像标签**: 版本号

## 配置要求

### GitHub Secrets

在 GitHub 仓库设置中添加以下 secrets：

```bash
# Container Registry
GITHUB_TOKEN  # 自动提供

# Kubernetes
KUBECONFIG    # Base64 编码的 kubeconfig 文件

# Slack 通知 (可选)
SLACK_WEBHOOK # Slack webhook URL

# API Keys (用于应用)
OPENAI_API_KEY
ANTHROPIC_API_KEY
GOOGLE_AI_API_KEY
JWT_SECRET
ENCRYPTION_KEY
```

### 环境变量

在 Kubernetes 中配置以下环境变量：

```yaml
# 数据库连接
DATABASE_URL: "postgresql://postgres:password@postgres:5432/intelligent_thinking"
REDIS_URL: "redis://redis:6379"
NEO4J_URL: "bolt://neo4j:7687"
ELASTICSEARCH_URL: "http://elasticsearch:9200"

# 消息队列和服务发现
KAFKA_URL: "kafka:9092"
CONSUL_URL: "consul:8500"

# 监控和追踪
PROMETHEUS_URL: "prometheus:9090"
GRAFANA_URL: "grafana:3000"
JAEGER_URL: "jaeger:14268"
```

## 使用方法

### 1. 自动构建触发

```bash
# 开发环境部署
git checkout develop
git add .
git commit -m "feat: 添加新功能"
git push origin develop

# 生产环境部署
git checkout main
git merge develop
git push origin main

# 版本发布
git tag v1.0.0
git push origin v1.0.0
```

### 2. 手动触发

在 GitHub Actions 页面可以手动触发 workflow：

1. 进入 **Actions** 页面
2. 选择 **Build and Deploy Docker Images**
3. 点击 **Run workflow**
4. 选择分支和参数

### 3. 本地测试

```bash
# 构建单个服务
docker build -t intelligent-thinking/frontend:latest ./frontend

# 构建所有服务
docker-compose build

# 运行所有服务
docker-compose up -d
```

## 监控和日志

### 1. 部署状态监控

- **GitHub Actions**: 查看构建和部署状态
- **Kubernetes Dashboard**: 查看 Pod 状态
- **Grafana**: 查看服务监控指标

### 2. 日志查看

```bash
# 查看 Pod 日志
kubectl logs -f deployment/frontend-deployment -n intelligent-thinking

# 查看服务状态
kubectl get pods -n intelligent-thinking
kubectl get services -n intelligent-thinking
```

### 3. 健康检查

```bash
# 检查服务健康状态
curl -f http://your-domain.com/health

# 检查 API Gateway
curl -f http://your-domain.com/api/health
```

## 故障排除

### 1. 构建失败

```bash
# 检查构建日志
# 在 GitHub Actions 页面查看详细日志

# 常见问题：
# - Docker 镜像构建失败
# - 依赖安装失败
# - 测试失败
```

### 2. 部署失败

```bash
# 查看 Kubernetes 事件
kubectl get events -n intelligent-thinking

# 查看 Pod 状态
kubectl describe pod <pod-name> -n intelligent-thinking

# 查看部署状态
kubectl rollout status deployment/frontend-deployment -n intelligent-thinking
```

### 3. 服务不可用

```bash
# 检查服务端点
kubectl get endpoints -n intelligent-thinking

# 检查网络策略
kubectl get networkpolicies -n intelligent-thinking

# 检查 Ingress 配置
kubectl describe ingress intelligent-thinking-ingress -n intelligent-thinking
```

## 性能优化

### 1. 镜像优化

- **多阶段构建**: 减少镜像大小
- **缓存层**: 利用 Docker 层缓存
- **基础镜像**: 使用优化的基础镜像

### 2. 构建优化

- **并行构建**: 同时构建多个服务
- **增量构建**: 只构建有变化的组件
- **缓存策略**: 使用 GitHub Actions 缓存

### 3. 部署优化

- **滚动更新**: 零停机部署
- **健康检查**: 确保服务可用性
- **自动扩缩**: 根据负载自动扩展

## 安全考虑

### 1. 镜像安全

- **漏洞扫描**: 使用 Trivy 扫描
- **最小权限**: 使用非 root 用户
- **安全更新**: 定期更新基础镜像

### 2. 密钥管理

- **GitHub Secrets**: 存储敏感信息
- **Kubernetes Secrets**: 运行时密钥
- **加密传输**: 使用 TLS/SSL

### 3. 网络安全

- **网络策略**: 限制 Pod 间通信
- **入口控制**: 使用 Ingress 控制器
- **防火墙**: 配置适当的防火墙规则

## 最佳实践

### 1. 版本管理

- **语义化版本**: 使用 semantic versioning
- **标签策略**: 合理的镜像标签
- **变更日志**: 维护详细的变更记录

### 2. 环境管理

- **环境分离**: 开发、测试、生产环境隔离
- **配置管理**: 使用 ConfigMap 和 Secrets
- **资源限制**: 设置适当的资源限制

### 3. 监控和日志

- **全链路监控**: 使用 Prometheus + Grafana
- **日志聚合**: 使用 ELK Stack
- **告警机制**: 配置关键指标告警

## 扩展和定制

### 1. 添加新服务

```yaml
# 在 docker-image.yml 中添加新的构建 job
build-new-service:
  needs: changes
  if: needs.changes.outputs.new-service == 'true'
  runs-on: ubuntu-latest
  # ... 构建步骤
```

### 2. 自定义部署策略

```yaml
# 在 deploy.yml 中添加自定义部署步骤
custom-deployment:
  runs-on: ubuntu-latest
  steps:
    - name: Custom Deploy
      run: |
        # 自定义部署逻辑
```

### 3. 集成第三方服务

```yaml
# 添加第三方服务集成
third-party-integration:
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to Cloud Provider
      uses: cloud-provider/deploy-action@v1
      with:
        api-key: ${{ secrets.CLOUD_API_KEY }}
```

## 总结

这个部署系统提供了完整的 CI/CD 流程，支持：

- ✅ 自动化构建和部署
- ✅ 多环境支持
- ✅ 安全扫描和监控
- ✅ 自动回滚和通知
- ✅ 高可用性和扩展性

通过这个系统，您可以实现：
- **快速迭代**: 自动化部署缩短上线时间
- **可靠性**: 自动化测试和健康检查
- **可扩展性**: 支持大规模微服务架构
- **可维护性**: 清晰的配置和文档

如有问题，请参考故障排除部分或联系运维团队。 