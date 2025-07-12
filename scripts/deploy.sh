#!/bin/bash

# 智能思维平台部署脚本
# Author: AI Assistant
# Version: 1.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示横幅
show_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "     智能思维平台 - Docker 部署脚本"
    echo "=================================================="
    echo -e "${NC}"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查 kubectl（如果使用 Kubernetes）
    if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl 未安装，请先安装 kubectl"
            exit 1
        fi
    fi
    
    log_success "依赖检查通过"
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."
    
    # 创建 .env 文件
    if [ ! -f .env ]; then
        cp env.example .env
        log_warning "请编辑 .env 文件，配置您的环境变量"
        echo "按回车键继续..."
        read
    fi
    
    # 加载环境变量
    source .env
    
    log_success "环境变量设置完成"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    # 构建前端镜像
    log_info "构建前端镜像..."
    docker build -t intelligent-thinking/frontend:latest ./frontend
    
    # 构建后端镜像
    log_info "构建后端镜像..."
    docker build -t intelligent-thinking/backend:latest ./backend
    
    # 构建微服务镜像
    log_info "构建微服务镜像..."
    services=("gateway" "blockchain" "graphql" "ai_advanced" "search" "federated_learning" "quantum")
    
    for service in "${services[@]}"; do
        log_info "构建 $service 镜像..."
        docker build -t intelligent-thinking/$service:latest ./backend/microservices/$service
    done
    
    # 构建移动端镜像
    if [ -d "./mobile" ]; then
        log_info "构建移动端镜像..."
        docker build -t intelligent-thinking/mobile:latest ./mobile
    fi
    
    # 构建元宇宙镜像
    if [ -d "./metaverse" ]; then
        log_info "构建元宇宙镜像..."
        docker build -t intelligent-thinking/metaverse:latest ./metaverse
    fi
    
    log_success "所有镜像构建完成"
}

# Docker Compose 部署
deploy_docker_compose() {
    log_info "使用 Docker Compose 部署..."
    
    # 停止现有容器
    docker-compose down
    
    # 启动所有服务
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    docker-compose ps
    
    log_success "Docker Compose 部署完成"
}

# Kubernetes 部署
deploy_kubernetes() {
    log_info "使用 Kubernetes 部署..."
    
    # 创建命名空间
    kubectl create namespace intelligent-thinking --dry-run=client -o yaml | kubectl apply -f -
    
    # 创建 ConfigMap
    kubectl create configmap app-config \
        --from-env-file=.env \
        --namespace=intelligent-thinking \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # 应用 Kubernetes 配置
    kubectl apply -f k8s/intelligent-thinking-k8s.yaml
    
    # 等待部署完成
    log_info "等待 Kubernetes 部署完成..."
    kubectl rollout status deployment/frontend-deployment -n intelligent-thinking
    kubectl rollout status deployment/gateway-deployment -n intelligent-thinking
    
    # 显示服务状态
    kubectl get pods -n intelligent-thinking
    kubectl get services -n intelligent-thinking
    
    log_success "Kubernetes 部署完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    if [ "$DEPLOY_TYPE" = "docker-compose" ]; then
        # Docker Compose 健康检查
        frontend_url="http://localhost:3000"
        api_url="http://localhost:8080/health"
    else
        # Kubernetes 健康检查
        frontend_url="http://$(kubectl get service frontend-service -n intelligent-thinking -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):80"
        api_url="http://$(kubectl get service gateway-service -n intelligent-thinking -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8080/health"
    fi
    
    # 检查前端
    if curl -f "$frontend_url" > /dev/null 2>&1; then
        log_success "前端服务健康检查通过"
    else
        log_warning "前端服务健康检查失败"
    fi
    
    # 检查 API Gateway
    if curl -f "$api_url" > /dev/null 2>&1; then
        log_success "API Gateway 健康检查通过"
    else
        log_warning "API Gateway 健康检查失败"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_info "部署信息："
    echo "=================================================="
    echo "🚀 智能思维平台部署完成！"
    echo "=================================================="
    echo ""
    echo "📱 前端地址: http://localhost:3000"
    echo "🔗 API Gateway: http://localhost:8080"
    echo "📊 监控面板: http://localhost:9090 (Prometheus)"
    echo "📈 图表面板: http://localhost:3001 (Grafana)"
    echo ""
    echo "🛠️ 管理命令："
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
    echo ""
    echo "🔧 微服务端口："
    echo "  API Gateway: 8080"
    echo "  Blockchain: 8084"
    echo "  GraphQL: 8085"
    echo "  AI Advanced: 8086"
    echo "  Search: 8087"
    echo "  Federated Learning: 8088"
    echo "  Quantum Computing: 8089"
    echo ""
    echo "=================================================="
}

# 主函数
main() {
    show_banner
    
    # 解析命令行参数
    DEPLOY_TYPE="docker-compose"
    SKIP_BUILD=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                DEPLOY_TYPE="$2"
                shift 2
                ;;
            -s|--skip-build)
                SKIP_BUILD=true
                shift
                ;;
            -h|--help)
                echo "使用方法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  -t, --type TYPE      部署类型 (docker-compose|kubernetes)"
                echo "  -s, --skip-build     跳过镜像构建"
                echo "  -h, --help           显示帮助信息"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 检查部署类型
    if [ "$DEPLOY_TYPE" != "docker-compose" ] && [ "$DEPLOY_TYPE" != "kubernetes" ]; then
        log_error "无效的部署类型: $DEPLOY_TYPE"
        exit 1
    fi
    
    log_info "部署类型: $DEPLOY_TYPE"
    
    # 执行部署步骤
    check_dependencies
    setup_environment
    
    if [ "$SKIP_BUILD" = false ]; then
        build_images
    fi
    
    if [ "$DEPLOY_TYPE" = "docker-compose" ]; then
        deploy_docker_compose
    else
        deploy_kubernetes
    fi
    
    health_check
    show_deployment_info
    
    log_success "部署完成！"
}

# 运行主函数
main "$@" 