# 智能思维与灵境融合项目 - 部署指南

## 📋 目录

- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker容器化部署](#docker容器化部署)
- [云平台部署](#云平台部署)
- [性能优化](#性能优化)
- [监控与日志](#监控与日志)
- [故障排除](#故障排除)

## 🚀 快速开始

### 一键开发环境启动

```bash
# 克隆项目
git clone <repository-url>
cd intelligent_thinking

# 运行一键启动脚本
python start_dev.py
```

### 手动启动

```bash
# 1. 启动基础设施
docker-compose up -d postgres redis neo4j

# 2. 初始化数据库
python backend/scripts/init_db.py

# 3. 启动后端
cd backend && python main.py

# 4. 启动前端
cd frontend && npm start
```

## 🖥️ 系统要求

### 最低配置

- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB可用空间
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+ / Windows 10+

### 推荐配置

- **CPU**: 4核心或以上
- **内存**: 8GB RAM或以上
- **存储**: 50GB SSD
- **网络**: 稳定的互联网连接

### 软件依赖

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Node.js**: 16.0+
- **Python**: 3.9+
- **Git**: 2.30+

## 🛠️ 开发环境部署

### 1. 环境准备

```bash
# 安装 Node.js (使用 nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 16
nvm use 16

# 安装 Python 依赖
pip install -r backend/requirements.txt

# 安装前端依赖
cd frontend && npm install
```

### 2. 环境配置

```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量
nano .env
```

### 3. 数据库配置

```bash
# 启动数据库服务
docker-compose up -d postgres redis neo4j

# 初始化数据库
python backend/scripts/init_db.py

# 验证数据库连接
python backend/scripts/init_db.py verify
```

### 4. 启动服务

```bash
# 方式1: 使用一键启动脚本
python start_dev.py

# 方式2: 分别启动
# 终端1: 启动后端
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 终端2: 启动前端
cd frontend && npm start
```

## 🏭 生产环境部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建项目目录
sudo mkdir -p /opt/intelligent_thinking
sudo chown $USER:$USER /opt/intelligent_thinking
```

### 2. 生产环境配置

```bash
# 创建生产环境配置
cat > .env.production << EOF
NODE_ENV=production
PYTHON_ENV=production

# 数据库配置 (使用强密码)
POSTGRES_PASSWORD=your_secure_production_password
NEO4J_PASSWORD=your_secure_neo4j_password

# 安全配置
SECRET_KEY=your_very_secure_production_secret_key
JWT_ALGORITHM=HS256

# 域名配置
REACT_APP_API_URL=https://api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# SSL配置
SSL_CERTIFICATE_PATH=/etc/ssl/certs/yourdomain.crt
SSL_PRIVATE_KEY_PATH=/etc/ssl/private/yourdomain.key
EOF
```

### 3. 生产Docker配置

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: intelligent_thinking
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network

  neo4j:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_dbms_memory_heap_initial__size: 512m
      NEO4J_dbms_memory_heap_max__size: 2G
    volumes:
      - neo4j_data:/data
    restart: unless-stopped
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/intelligent_thinking
      - REDIS_URL=redis://redis:6379
      - NEO4J_URI=bolt://neo4j:7687
    depends_on:
      - postgres
      - redis
      - neo4j
    restart: unless-stopped
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  neo4j_data:

networks:
  app-network:
    driver: bridge
```

### 4. 生产环境Dockerfile

`backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

`frontend/Dockerfile.prod`:

```dockerfile
# 构建阶段
FROM node:16-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 🐳 Docker容器化部署

### 完整容器化部署

```bash
# 1. 构建镜像
docker-compose -f docker-compose.prod.yml build

# 2. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 3. 初始化数据库
docker-compose -f docker-compose.prod.yml exec backend python scripts/init_db.py

# 4. 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 镜像管理

```bash
# 构建特定服务
docker-compose build backend
docker-compose build frontend

# 推送到镜像仓库
docker tag intelligent_thinking_backend:latest your-registry/intelligent_thinking_backend:latest
docker push your-registry/intelligent_thinking_backend:latest

# 从镜像仓库拉取
docker pull your-registry/intelligent_thinking_backend:latest
```

## ☁️ 云平台部署

### AWS部署

#### 使用ECS + RDS

```bash
# 1. 创建ECS集群
aws ecs create-cluster --cluster-name intelligent-thinking

# 2. 创建RDS实例
aws rds create-db-instance \
  --db-instance-identifier intelligent-thinking-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YourSecurePassword \
  --allocated-storage 20

# 3. 部署ECS服务
aws ecs create-service \
  --cluster intelligent-thinking \
  --service-name backend-service \
  --task-definition backend-task:1 \
  --desired-count 2
```

#### 使用Kubernetes (EKS)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/intelligent_thinking_backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

### Azure部署

```bash
# 使用Azure Container Instances
az container create \
  --resource-group intelligent-thinking-rg \
  --name backend-container \
  --image your-registry/intelligent_thinking_backend:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000
```

### Google Cloud Platform

```bash
# 使用Cloud Run
gcloud run deploy backend \
  --image gcr.io/your-project/intelligent_thinking_backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## ⚡ 性能优化

### 后端优化

```python
# backend/main.py 生产环境配置
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 启用Gzip压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 配置连接池
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db?pool_size=20&max_overflow=30"
```

### 前端优化

```json
// package.json - 构建优化
{
  "scripts": {
    "build": "GENERATE_SOURCEMAP=false npm run build:optimized",
    "build:optimized": "react-scripts build && npm run compress",
    "compress": "gzip -k build/static/js/*.js && gzip -k build/static/css/*.css"
  }
}
```

### Nginx优化

```nginx
# nginx/nginx.prod.conf
http {
    # 启用gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;

    # 缓存配置
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache api_cache;
        proxy_cache_valid 200 5m;
    }
}
```

### 数据库优化

```sql
-- PostgreSQL性能优化
-- 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_thinking_analyses_user_id ON thinking_analyses(user_id);
CREATE INDEX idx_thinking_analyses_created_at ON thinking_analyses(created_at);

-- 分区表（适用于大数据量）
CREATE TABLE thinking_analyses_2024 PARTITION OF thinking_analyses
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## 📊 监控与日志

### 应用监控

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana

  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki.yml:/etc/loki/local-config.yaml

volumes:
  grafana_data:
```

### 日志配置

```python
# backend/app/core/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
```

### 健康检查

```python
# backend/app/api/api_v1/endpoints/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": await check_database(),
            "redis": await check_redis(),
            "neo4j": await check_neo4j()
        }
    }
```

## 🔒 安全配置

### SSL/TLS配置

```bash
# 使用Let's Encrypt免费证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 防火墙配置

```bash
# Ubuntu UFW配置
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # 只允许内部访问
```

### 环境变量安全

```bash
# 使用Docker secrets
echo "your_secret_password" | docker secret create db_password -

# 在docker-compose中使用
services:
  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    external: true
```

## 🚨 故障排除

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查数据库状态
docker-compose logs postgres

# 检查网络连接
docker network ls
docker network inspect intelligent_thinking_default

# 重置数据库
docker-compose down
docker volume rm intelligent_thinking_postgres_data
docker-compose up -d postgres
```

#### 2. 前端无法连接后端

```bash
# 检查后端状态
curl http://localhost:8000/api/v1/health

# 检查CORS配置
# 确认 .env 中的 CORS_ORIGINS 设置正确

# 检查nginx配置
docker-compose logs nginx
```

#### 3. 内存不足

```bash
# 检查系统资源
docker stats

# 优化内存使用
# 在 docker-compose.yml 中添加内存限制
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### 日志分析

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时日志监控
docker-compose logs -f

# 导出日志
docker-compose logs > app.log
```

### 性能调试

```bash
# 检查容器资源使用
docker stats --no-stream

# 检查磁盘空间
df -h
docker system df

# 清理未使用的资源
docker system prune -a
```

## 📚 相关文档

- [开发指南](./开发指导.md)
- [API文档](http://localhost:8000/docs)
- [用户手册](./README.md)
- [环境配置](./环境配置指南.md)

## 🆘 获取帮助

- **问题反馈**: 请在GitHub Issues中提交
- **技术支持**: 联系开发团队
- **文档更新**: 欢迎提交PR改进文档

---

**注意**: 在生产环境中，请确保：
1. 使用强密码和安全的密钥
2. 定期备份数据库
3. 监控系统性能和安全状态
4. 及时更新依赖包和安全补丁 