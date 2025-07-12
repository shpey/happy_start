# Mobile App Dockerfile (for web preview and backend services)
FROM node:18-alpine

WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    openssh-client

# 全局安装Expo CLI和React Native CLI
RUN npm install -g @expo/cli @react-native-community/cli

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm install --no-audit --no-fund

# 复制源代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/assets /app/logs

# 设置权限
RUN chown -R node:node /app

# 切换到非root用户
USER node

# 暴露端口 (Expo Metro Bundler)
EXPOSE 19000 19001 19002

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:19000 || exit 1

# 启动应用 (Web预览模式)
CMD ["npm", "start", "--", "--web"] 