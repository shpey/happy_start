#!/bin/bash

# 本地 Docker 构建测试脚本
# 用于验证所有服务的 Docker 构建是否正常工作

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
    echo "     智能思维平台 - 本地构建测试"
    echo "=================================================="
    echo -e "${NC}"
}

# 检查 Docker
check_docker() {
    log_info "检查 Docker 环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker 服务未运行，请启动 Docker"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 构建前端
build_frontend() {
    log_info "构建前端服务..."
    
    if [ -d "./frontend" ]; then
        if [ -f "./frontend/Dockerfile" ]; then
            docker build -t intelligent-thinking/frontend:test ./frontend
            log_success "前端构建成功"
        else
            log_warning "前端 Dockerfile 不存在，跳过构建"
        fi
    else
        log_warning "前端目录不存在，跳过构建"
    fi
}

# 构建后端
build_backend() {
    log_info "构建后端服务..."
    
    if [ -d "./backend" ]; then
        if [ -f "./backend/Dockerfile" ]; then
            docker build -t intelligent-thinking/backend:test ./backend
            log_success "后端构建成功"
        else
            log_warning "后端 Dockerfile 不存在，跳过构建"
        fi
    else
        log_warning "后端目录不存在，跳过构建"
    fi
}

# 构建微服务
build_microservices() {
    log_info "构建微服务..."
    
    # 微服务列表
    services=("gateway" "blockchain" "graphql" "ai_advanced" "search" "federated_learning" "quantum")
    
    local success_count=0
    local total_count=${#services[@]}
    
    for service in "${services[@]}"; do
        service_dir="./backend/microservices/$service"
        
        if [ -d "$service_dir" ]; then
            if [ -f "$service_dir/Dockerfile" ]; then
                log_info "构建微服务: $service"
                if docker build -t "intelligent-thinking/$service:test" "$service_dir"; then
                    log_success "微服务 $service 构建成功"
                    ((success_count++))
                else
                    log_error "微服务 $service 构建失败"
                fi
            else
                log_warning "微服务 $service 的 Dockerfile 不存在，跳过构建"
            fi
        else
            log_warning "微服务 $service 目录不存在，跳过构建"
        fi
    done
    
    log_info "微服务构建完成：$success_count/$total_count 成功"
}

# 构建移动端
build_mobile() {
    log_info "构建移动端服务..."
    
    if [ -d "./mobile" ]; then
        if [ -f "./mobile/Dockerfile" ]; then
            docker build -t intelligent-thinking/mobile:test ./mobile
            log_success "移动端构建成功"
        else
            log_warning "移动端 Dockerfile 不存在，跳过构建"
        fi
    else
        log_warning "移动端目录不存在，跳过构建"
    fi
}

# 构建元宇宙
build_metaverse() {
    log_info "构建元宇宙服务..."
    
    if [ -d "./metaverse" ]; then
        if [ -f "./metaverse/Dockerfile" ]; then
            docker build -t intelligent-thinking/metaverse:test ./metaverse
            log_success "元宇宙构建成功"
        else
            log_warning "元宇宙 Dockerfile 不存在，跳过构建"
        fi
    else
        log_warning "元宇宙目录不存在，跳过构建"
    fi
}

# 清理测试镜像
cleanup_images() {
    log_info "清理测试镜像..."
    
    # 获取所有测试镜像
    test_images=$(docker images --filter "reference=intelligent-thinking/*:test" -q)
    
    if [ -n "$test_images" ]; then
        docker rmi $test_images
        log_success "测试镜像清理完成"
    else
        log_info "没有找到测试镜像"
    fi
}

# 显示镜像信息
show_images() {
    log_info "构建的镜像列表："
    echo "=================================================="
    docker images --filter "reference=intelligent-thinking/*:test" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo "=================================================="
}

# 测试镜像运行
test_images() {
    log_info "测试镜像运行..."
    
    # 测试前端镜像
    if docker images -q intelligent-thinking/frontend:test > /dev/null; then
        log_info "测试前端镜像..."
        if docker run --rm intelligent-thinking/frontend:test echo "Frontend test OK"; then
            log_success "前端镜像测试通过"
        else
            log_error "前端镜像测试失败"
        fi
    fi
    
    # 测试后端镜像
    if docker images -q intelligent-thinking/backend:test > /dev/null; then
        log_info "测试后端镜像..."
        if docker run --rm intelligent-thinking/backend:test echo "Backend test OK"; then
            log_success "后端镜像测试通过"
        else
            log_error "后端镜像测试失败"
        fi
    fi
    
    # 测试微服务镜像
    services=("gateway" "blockchain" "graphql" "ai_advanced" "search" "federated_learning" "quantum")
    for service in "${services[@]}"; do
        if docker images -q "intelligent-thinking/$service:test" > /dev/null; then
            log_info "测试微服务镜像: $service"
            if docker run --rm "intelligent-thinking/$service:test" echo "$service test OK"; then
                log_success "微服务 $service 镜像测试通过"
            else
                log_error "微服务 $service 镜像测试失败"
            fi
        fi
    done
}

# 主函数
main() {
    show_banner
    
    # 解析命令行参数
    CLEANUP_AFTER=false
    TEST_RUN=false
    COMPONENT=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--cleanup)
                CLEANUP_AFTER=true
                shift
                ;;
            -t|--test)
                TEST_RUN=true
                shift
                ;;
            --component)
                COMPONENT="$2"
                shift 2
                ;;
            -h|--help)
                echo "使用方法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  -c, --cleanup       构建后清理测试镜像"
                echo "  -t, --test          构建后测试镜像运行"
                echo "  --component NAME    只构建指定组件 (frontend|backend|microservices|mobile|metaverse)"
                echo "  -h, --help          显示帮助信息"
                echo ""
                echo "示例:"
                echo "  $0                  # 构建所有组件"
                echo "  $0 -c               # 构建所有组件并清理"
                echo "  $0 --component frontend  # 只构建前端"
                echo "  $0 -t               # 构建并测试所有组件"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 检查 Docker 环境
    check_docker
    
    # 构建组件
    case $COMPONENT in
        "frontend")
            build_frontend
            ;;
        "backend")
            build_backend
            ;;
        "microservices")
            build_microservices
            ;;
        "mobile")
            build_mobile
            ;;
        "metaverse")
            build_metaverse
            ;;
        "")
            # 构建所有组件
            build_frontend
            build_backend
            build_microservices
            build_mobile
            build_metaverse
            ;;
        *)
            log_error "未知组件: $COMPONENT"
            exit 1
            ;;
    esac
    
    # 显示构建结果
    show_images
    
    # 测试镜像运行
    if [ "$TEST_RUN" = true ]; then
        test_images
    fi
    
    # 清理镜像
    if [ "$CLEANUP_AFTER" = true ]; then
        cleanup_images
    fi
    
    log_success "构建测试完成！"
    
    if [ "$CLEANUP_AFTER" = false ]; then
        echo ""
        log_info "提示："
        echo "  - 查看镜像: docker images intelligent-thinking/*:test"
        echo "  - 清理镜像: $0 --cleanup 或 docker rmi \$(docker images -q intelligent-thinking/*:test)"
        echo "  - 测试运行: $0 --test"
    fi
}

# 运行主函数
main "$@" 