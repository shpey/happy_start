@echo off
setlocal EnableDelayedExpansion

echo 🚀 开始测试所有Docker镜像构建...
echo.

set BUILD_SUCCESS=0
set BUILD_FAILED=0

:: 测试 Frontend
echo 📦 测试构建 frontend...
docker build -t test-frontend:latest ./frontend
if !errorlevel! equ 0 (
    echo ✅ frontend 构建成功
    set /a BUILD_SUCCESS+=1
    docker rmi test-frontend:latest >nul 2>&1
) else (
    echo ❌ frontend 构建失败
    set /a BUILD_FAILED+=1
)
echo.

:: 测试 Backend
echo 📦 测试构建 backend...
docker build -t test-backend:latest ./backend
if !errorlevel! equ 0 (
    echo ✅ backend 构建成功
    set /a BUILD_SUCCESS+=1
    docker rmi test-backend:latest >nul 2>&1
) else (
    echo ❌ backend 构建失败
    set /a BUILD_FAILED+=1
)
echo.

:: 测试 Mobile
echo 📦 测试构建 mobile...
docker build -t test-mobile:latest ./mobile
if !errorlevel! equ 0 (
    echo ✅ mobile 构建成功
    set /a BUILD_SUCCESS+=1
    docker rmi test-mobile:latest >nul 2>&1
) else (
    echo ❌ mobile 构建失败
    set /a BUILD_FAILED+=1
)
echo.

:: 测试 Metaverse
echo 📦 测试构建 metaverse...
docker build -t test-metaverse:latest ./metaverse
if !errorlevel! equ 0 (
    echo ✅ metaverse 构建成功
    set /a BUILD_SUCCESS+=1
    docker rmi test-metaverse:latest >nul 2>&1
) else (
    echo ❌ metaverse 构建失败
    set /a BUILD_FAILED+=1
)
echo.

:: 测试微服务
set MICROSERVICES=gateway blockchain graphql ai_advanced search federated_learning quantum
for %%s in (%MICROSERVICES%) do (
    echo 📦 测试构建 microservice-%%s...
    docker build -t test-microservice-%%s:latest ./backend/microservices/%%s
    if !errorlevel! equ 0 (
        echo ✅ microservice-%%s 构建成功
        set /a BUILD_SUCCESS+=1
        docker rmi test-microservice-%%s:latest >nul 2>&1
    ) else (
        echo ❌ microservice-%%s 构建失败
        set /a BUILD_FAILED+=1
    )
    echo.
)

:: 显示结果
echo 📊 构建结果汇总:
echo ✅ 成功构建: !BUILD_SUCCESS!
echo ❌ 构建失败: !BUILD_FAILED!

if !BUILD_FAILED! gtr 0 (
    echo.
    echo ❌ 有服务构建失败，请检查相关配置
    exit /b 1
) else (
    echo.
    echo 🎉 所有服务构建成功！
    exit /b 0
) 