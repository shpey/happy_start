#!/bin/bash

# 测试所有Docker镜像构建脚本
set -e

echo "🚀 开始测试所有Docker镜像构建..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 构建计数器
BUILD_SUCCESS=0
BUILD_FAILED=0
FAILED_SERVICES=()

# 测试构建函数
test_build() {
    local service_name=$1
    local context_path=$2
    local dockerfile_path=$3
    
    echo -e "${YELLOW}📦 构建 $service_name...${NC}"
    
    if docker build -t "test-$service_name:latest" -f "$dockerfile_path" "$context_path"; then
        echo -e "${GREEN}✅ $service_name 构建成功${NC}"
        BUILD_SUCCESS=$((BUILD_SUCCESS + 1))
        # 清理测试镜像
        docker rmi "test-$service_name:latest" > /dev/null 2>&1 || true
    else
        echo -e "${RED}❌ $service_name 构建失败${NC}"
        BUILD_FAILED=$((BUILD_FAILED + 1))
        FAILED_SERVICES+=("$service_name")
    fi
    echo ""
}

# 检查必要文件
echo "🔍 检查必要文件..."
check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}❌ 缺失文件: $1${NC}"
        return 1
    else
        echo -e "${GREEN}✅ 找到文件: $1${NC}"
        return 0
    fi
}

# 检查所有必要文件
echo "检查 frontend 文件..."
check_file "frontend/Dockerfile"
check_file "frontend/package.json"
check_file "frontend/nginx.conf"

echo -e "\n检查 backend 文件..."
check_file "backend/Dockerfile"
check_file "backend/requirements.txt"

echo -e "\n检查 mobile 文件..."
check_file "mobile/Dockerfile"
check_file "mobile/package.json"

echo -e "\n检查 metaverse 文件..."
check_file "metaverse/Dockerfile"
check_file "metaverse/package.json"

echo -e "\n检查微服务文件..."
MICROSERVICES=("gateway" "blockchain" "graphql" "ai_advanced" "search" "federated_learning" "quantum")
for service in "${MICROSERVICES[@]}"; do
    check_file "backend/microservices/$service/Dockerfile"
    check_file "backend/microservices/$service/requirements.txt"
done

echo -e "\n${YELLOW}开始构建测试...${NC}\n"

# 测试 Frontend
test_build "frontend" "./frontend" "./frontend/Dockerfile"

# 测试 Backend
test_build "backend" "./backend" "./backend/Dockerfile"

# 测试 Mobile
test_build "mobile" "./mobile" "./mobile/Dockerfile"

# 测试 Metaverse
test_build "metaverse" "./metaverse" "./metaverse/Dockerfile"

# 测试微服务
for service in "${MICROSERVICES[@]}"; do
    test_build "microservice-$service" "./backend/microservices/$service" "./backend/microservices/$service/Dockerfile"
done

# 构建结果汇总
echo -e "${YELLOW}📊 构建结果汇总:${NC}"
echo -e "${GREEN}✅ 成功构建: $BUILD_SUCCESS${NC}"
echo -e "${RED}❌ 构建失败: $BUILD_FAILED${NC}"

if [ $BUILD_FAILED -gt 0 ]; then
    echo -e "\n${RED}失败的服务:${NC}"
    for service in "${FAILED_SERVICES[@]}"; do
        echo -e "${RED}  - $service${NC}"
    done
    echo -e "\n${RED}请修复以上服务的构建问题。${NC}"
    exit 1
else
    echo -e "\n${GREEN}🎉 所有服务构建成功！${NC}"
    exit 0
fi 